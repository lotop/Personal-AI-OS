#!/usr/bin/env python3
"""为已知 Temp/Cache 生成不可变计划，并在授权后移动到可恢复 Quarantine。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "00_system/lifecycle/gc.toml"
PLAN_ID_PATTERN = re.compile(r"^gc-[0-9]{8}T[0-9]{6}Z$")
AUTHORIZATION_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._:-]{2,127}$")


def sha256_path(path: Path) -> str:
    if path.is_symlink():
        raise ValueError(f"清理范围不得包含 symlink: {path}")
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            raise ValueError(f"清理范围不得包含嵌套 symlink: {child}")
        mode = child.lstat().st_mode
        if child.is_dir():
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f"清理范围不得包含特殊文件: {child}")
        relative = child.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(child.read_bytes()).hexdigest().encode("ascii") + b"\n")
    return digest.hexdigest()


def is_under(relative: Path, prefix: Path) -> bool:
    try:
        relative.relative_to(prefix)
    except ValueError:
        return False
    return True


def discover_candidates(
    root: Path, policy: dict | None = None, now: datetime | None = None
) -> list[tuple[Path, str, str]]:
    candidates: list[tuple[Path, str, str]] = []
    temp_root = root / "99_temp"
    protected_temp = {".gitkeep", "plans", "quarantine"}

    if temp_root.is_dir():
        for child in sorted(temp_root.iterdir()):
            if child.name not in protected_temp:
                candidates.append((child, "TEMP", "TEMP_AREA_ITEM"))

    cache_dirs = sorted(path for path in root.rglob("__pycache__") if path.is_dir())
    for path in cache_dirs:
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == ".git":
            continue
        if is_under(relative, Path("99_temp/quarantine")) or is_under(
            relative, Path("99_temp/plans")
        ):
            continue
        candidates.append((path, "CACHE", "PYTHON_BYTECODE_CACHE"))

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == ".git":
            continue
        if is_under(relative, Path("99_temp/quarantine")) or is_under(
            relative, Path("99_temp/plans")
        ):
            continue
        if any(parent.name == "__pycache__" for parent in path.parents):
            continue
        if path.name == ".DS_Store":
            candidates.append((path, "TEMP", "MACOS_METADATA"))
        elif path.suffix == ".pyc":
            candidates.append((path, "CACHE", "PYTHON_BYTECODE_CACHE"))

    unique: dict[str, tuple[Path, str, str]] = {}
    for item in candidates:
        unique[item[0].relative_to(root).as_posix()] = item
    results = [unique[key] for key in sorted(unique)]
    if policy is None:
        return results
    current = now or datetime.now(timezone.utc)
    retention = policy.get("retention", {})
    filtered = []
    for path, artifact_class, reason in results:
        days = int(retention.get("temp_days" if artifact_class == "TEMP" else "cache_days", 0))
        if days <= 0:
            filtered.append((path, artifact_class, reason))
            continue
        age = current - datetime.fromtimestamp(path.lstat().st_mtime, timezone.utc)
        if age >= timedelta(days=days):
            filtered.append((path, artifact_class, reason))
    return filtered


def reference_scan(root: Path, candidate: Path) -> tuple[str, bool]:
    relative = candidate.relative_to(root).as_posix()
    if not relative.startswith("99_temp/"):
        return "CLEAR_KNOWN_EPHEMERAL_ONLY", False
    needles = {relative.encode("utf-8"), candidate.name.encode("utf-8")}
    scanned = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink() or path == candidate:
            continue
        rel = path.relative_to(root)
        if rel.parts[0] in {".git", "99_temp", "08_history", "09_archive"}:
            continue
        try:
            content = path.read_bytes()
        except OSError:
            continue
        scanned += 1
        if any(needle in content for needle in needles):
            return f"HIT:{rel.as_posix()}", True
    return f"CLEAR_SCANNED_FILES:{scanned}", False


def build_plan(root: Path, policy: dict) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(hours=int(policy["plan_ttl_hours"]))
    plan_id = "gc-" + now.strftime("%Y%m%dT%H%M%SZ")
    items = []
    recovery_until = now + timedelta(days=int(policy.get("retention", {}).get("logs_days", 30)))
    for path, artifact_class, reason in discover_candidates(root, policy, now):
        item_hash = sha256_path(path)
        scan_evidence, hold = reference_scan(root, path)
        items.append(
            {
                "path": path.relative_to(root).as_posix(),
                "real_path": str(path.resolve()),
                "artifact_class": artifact_class,
                "sha256": item_hash,
                "source_mode": oct(path.lstat().st_mode & 0o7777),
                "source_mtime_ns": path.lstat().st_mtime_ns,
                "reference_scan": scan_evidence,
                "hold": hold,
                "recovery_until": recovery_until.isoformat().replace("+00:00", "Z"),
                "reason_code": reason,
            }
        )
    return {
        "schema_version": "0.1.0-working",
        "plan_id": plan_id,
        "policy_version": policy["schema_version"],
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": expires.isoformat().replace("+00:00", "Z"),
        "mode": "QUARANTINE_ONLY",
        "items": items,
    }


def write_plan(root: Path, policy: dict, plan: dict) -> Path:
    plan_root = root / policy["plan_root"]
    plan_root.mkdir(parents=True, exist_ok=True)
    plan_id = plan.get("plan_id", "")
    if not isinstance(plan_id, str) or not PLAN_ID_PATTERN.fullmatch(plan_id):
        raise ValueError("plan_id 格式非法")
    path = plan_root / f"{plan_id}.json"
    if path.exists():
        raise ValueError(f"计划已存在，不得覆盖: {path}")
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def apply_plan(
    root: Path,
    policy: dict,
    plan: dict,
    *,
    plan_path: Path,
    authorization_ref: str,
) -> Path:
    if not policy.get("enabled"):
        raise ValueError("GC 尚未启用")
    if policy.get("dry_run_only"):
        raise ValueError("Policy 只允许 Dry Run")
    if policy.get("destructive_delete"):
        raise ValueError("V1.1.2 清理器拒绝 destructive_delete")
    if plan.get("mode") != "QUARANTINE_ONLY":
        raise ValueError("计划执行模式非法")
    plan_id = plan.get("plan_id", "")
    if not isinstance(plan_id, str) or not PLAN_ID_PATTERN.fullmatch(plan_id):
        raise ValueError("plan_id 格式非法")
    if plan_path.name != f"{plan_id}.json":
        raise ValueError("plan_id 与计划文件名不一致")
    if plan_path.resolve().parent != (root / policy["plan_root"]).resolve():
        raise ValueError("计划文件不在受管 plan_root")
    if policy.get("protection", {}).get("require_founder_approval") and not AUTHORIZATION_PATTERN.fullmatch(authorization_ref or ""):
        raise ValueError("缺少有效 Founder 单次清理授权引用")
    if plan.get("policy_version") != policy.get("schema_version"):
        raise ValueError("Policy Version 已变化，计划 STALE")
    expires = datetime.fromisoformat(plan["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires:
        raise ValueError("计划已过期，状态 STALE")

    allowed_classes = {"TEMP", "CACHE"}
    validated: list[tuple[Path, Path, dict]] = []
    managed_quarantine = (root / policy["quarantine_root"]).resolve()
    quarantine_root = managed_quarantine / plan_id
    if quarantine_root.parent != managed_quarantine:
        raise ValueError("Quarantine 目标越界")
    discovered = {
        path.relative_to(root).as_posix(): (artifact_class, reason)
        for path, artifact_class, reason in discover_candidates(root, policy)
    }
    seen: set[str] = set()
    for item in plan.get("items", []):
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts or item["artifact_class"] not in allowed_classes:
            raise ValueError(f"非法计划项: {item}")
        relative_text = relative.as_posix()
        if relative_text in seen:
            raise ValueError(f"计划包含重复项: {relative}")
        seen.add(relative_text)
        expected_classification = discovered.get(relative_text)
        actual_classification = (item.get("artifact_class"), item.get("reason_code"))
        if expected_classification is None or actual_classification != expected_classification:
            raise ValueError(f"计划项不属于实时允许清理范围，疑似被篡改: {relative}")
        current_scan, current_hold = reference_scan(root, root / relative)
        if item.get("reference_scan") != current_scan or item.get("hold") != current_hold or current_hold:
            raise ValueError(f"计划项缺少清理授权证据: {relative}")
        source = root / relative
        if not source.exists() or source.is_symlink():
            raise ValueError(f"计划项缺失或为 symlink，状态 STALE: {relative}")
        if (
            str(source.resolve()) != item["real_path"]
            or sha256_path(source) != item["sha256"]
            or oct(source.lstat().st_mode & 0o7777) != item.get("source_mode")
            or source.lstat().st_mtime_ns != item.get("source_mtime_ns")
        ):
            raise ValueError(f"计划项已变化，状态 STALE: {relative}")
        target = quarantine_root / relative
        resolved_parent = target.parent.resolve()
        if managed_quarantine != resolved_parent and managed_quarantine not in resolved_parent.parents:
            raise ValueError(f"Quarantine 目标越界: {relative}")
        if target.exists():
            raise ValueError(f"Quarantine 目标已存在: {target}")
        validated.append((source, target, item))

    moved_items = []
    moved_paths: list[tuple[Path, Path]] = []
    record_path = root / policy["plan_root"] / f"{plan_id}.applied.json"
    if record_path.exists():
        raise ValueError(f"Applied Record 已存在，不得覆盖: {record_path}")
    try:
        for source, target, item in validated:
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(source), str(target))
            except Exception:
                if source.exists() and target.exists():
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                raise
            moved_paths.append((source, target))
            moved_items.append(
                {
                    **item,
                    "original_path": item["path"],
                    "authorization_reference": authorization_ref,
                    "quarantine_path": str(target),
                    "post_move_sha256": sha256_path(target),
                    "post_move_mode": oct(target.lstat().st_mode & 0o7777),
                }
            )
        record = {
            "schema_version": plan["schema_version"],
            "plan_id": plan_id,
            "applied_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "mode": "QUARANTINE_ONLY",
            "authorization_reference": authorization_ref,
            "items": moved_items,
        }
        record_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except Exception:
        if record_path.exists():
            record_path.unlink()
        for source, target in reversed(moved_paths):
            if target.exists() and not source.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(source))
        raise
    return record_path


def load_policy(path: Path = POLICY_PATH) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--plan", required=True)
    apply_parser.add_argument("--authorization-ref", required=True)
    args = parser.parse_args()

    policy = load_policy()
    try:
        if args.command == "plan":
            plan = build_plan(ROOT, policy)
            plan_path = write_plan(ROOT, policy, plan)
            print(json.dumps({"status": "PLANNED", "plan": str(plan_path), "items": len(plan["items"])}, ensure_ascii=False))
        else:
            plan_path = Path(args.plan).resolve()
            allowed_plan_root = (ROOT / policy["plan_root"]).resolve()
            if plan_path.parent != allowed_plan_root:
                raise ValueError("只能执行受管 plan_root 中的计划")
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            record = apply_plan(
                ROOT,
                policy,
                plan,
                plan_path=plan_path,
                authorization_ref=args.authorization_ref,
            )
            print(json.dumps({"status": "QUARANTINED", "record": str(record), "items": len(plan["items"])}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
