#!/usr/bin/env python3
"""为已知 Temp/Cache 生成不可变计划，并在授权后移动到可恢复 Quarantine。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
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


def sha256_path(path: Path) -> str:
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
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


def discover_candidates(root: Path) -> list[tuple[Path, str, str]]:
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
        if is_under(relative, Path("99_temp/quarantine")) or is_under(
            relative, Path("99_temp/plans")
        ):
            continue
        candidates.append((path, "CACHE", "PYTHON_BYTECODE_CACHE"))

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
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
    return [unique[key] for key in sorted(unique)]


def build_plan(root: Path, policy: dict) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(hours=int(policy["plan_ttl_hours"]))
    plan_id = "gc-" + now.strftime("%Y%m%dT%H%M%SZ")
    items = []
    for path, artifact_class, reason in discover_candidates(root):
        if path.is_symlink():
            raise ValueError(f"清理范围不得包含 symlink: {path}")
        items.append(
            {
                "path": path.relative_to(root).as_posix(),
                "real_path": str(path.resolve()),
                "artifact_class": artifact_class,
                "sha256": sha256_path(path),
                "reference_scan": "CLEAR_KNOWN_EPHEMERAL_ONLY",
                "hold": False,
                "recovery_until": expires.isoformat().replace("+00:00", "Z"),
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
    path = plan_root / f"{plan['plan_id']}.json"
    if path.exists():
        raise ValueError(f"计划已存在，不得覆盖: {path}")
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def apply_plan(root: Path, policy: dict, plan: dict) -> Path:
    if not policy.get("enabled"):
        raise ValueError("GC 尚未启用")
    if policy.get("dry_run_only"):
        raise ValueError("Policy 只允许 Dry Run")
    if policy.get("destructive_delete"):
        raise ValueError("V1.1.2 清理器拒绝 destructive_delete")
    if plan.get("policy_version") != policy.get("schema_version"):
        raise ValueError("Policy Version 已变化，计划 STALE")
    expires = datetime.fromisoformat(plan["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires:
        raise ValueError("计划已过期，状态 STALE")

    allowed_classes = {"TEMP", "CACHE"}
    validated: list[tuple[Path, Path, dict]] = []
    quarantine_root = root / policy["quarantine_root"] / plan["plan_id"]
    for item in plan.get("items", []):
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts or item["artifact_class"] not in allowed_classes:
            raise ValueError(f"非法计划项: {item}")
        source = root / relative
        if not source.exists() or source.is_symlink():
            raise ValueError(f"计划项缺失或为 symlink，状态 STALE: {relative}")
        if str(source.resolve()) != item["real_path"] or sha256_path(source) != item["sha256"]:
            raise ValueError(f"计划项已变化，状态 STALE: {relative}")
        target = quarantine_root / relative
        if target.exists():
            raise ValueError(f"Quarantine 目标已存在: {target}")
        validated.append((source, target, item))

    moved = []
    for source, target, item in validated:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        moved.append({**item, "quarantine_path": str(target), "post_move_sha256": sha256_path(target)})

    record = {
        "schema_version": plan["schema_version"],
        "plan_id": plan["plan_id"],
        "applied_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "QUARANTINE_ONLY",
        "items": moved,
    }
    record_path = root / policy["plan_root"] / f"{plan['plan_id']}.applied.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record_path


def load_policy(path: Path = POLICY_PATH) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--plan", required=True)
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
            record = apply_plan(ROOT, policy, plan)
            print(json.dumps({"status": "QUARANTINED", "record": str(record), "items": len(plan["items"])}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
