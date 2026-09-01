#!/usr/bin/env python3
"""安全部署受管 Adapter；默认只输出 Dry Run 计划。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        try:
            import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]
        except ModuleNotFoundError as exc:
            raise SystemExit("需要 Python 3.11+ 或安装 tomli") from exc


ROOT = Path(__file__).resolve().parents[1]
MANAGED_ADAPTER_ROOT = ROOT / "03_adapters"
AUTHORIZATION_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._:-]{2,127}$")


@dataclass(frozen=True)
class DeploymentItem:
    source: Path
    target: Path
    target_root: Path
    relative_target: Path
    action: str
    sha256: str
    source_mode: str
    previous_sha256: str | None
    previous_mode: str | None


def confined(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"{label} 必须是安全相对路径: {value}")
    return path


def reject_symlink_path(root: Path, relative: Path, label: str) -> None:
    current = root
    if current.is_symlink():
        raise ValueError(f"{label} Root 不得是 symlink")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label} 路径不得经过 symlink: {relative}")


def require_regular(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"{label} 必须是普通文件且不得为 symlink: {path}")


def validate_native(path: Path, format_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    if format_name == "toml":
        tomllib.loads(text)
    elif format_name == "json":
        json.loads(text)
    elif format_name != "markdown":
        raise ValueError(f"未知格式: {format_name}")


def build_plan(
    manifest_path: Path,
    target_root: Path,
    *,
    managed_adapter_root: Path,
) -> tuple[dict, list[DeploymentItem]]:
    if manifest_path.is_symlink():
        raise ValueError("Adapter Manifest 不得是 symlink")
    manifest_path = manifest_path.resolve()
    managed_root = managed_adapter_root.resolve()
    if manifest_path.parent.parent != managed_root or manifest_path.name != "manifest.toml":
        raise ValueError("只允许受管 Adapter Manifest")
    require_regular(manifest_path, "Adapter Manifest")
    adapter_root = manifest_path.parent
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    for field in ("platform", "artifact_class", "maturity_state", "generator", "source_files", "files"):
        if not manifest.get(field):
            raise ValueError(f"Adapter Manifest 缺少字段: {field}")
    if manifest.get("artifact_class") != "GENERATED" or manifest.get("maturity_state") != "WORKING":
        raise ValueError("Adapter 必须保持 GENERATED/WORKING")
    if manifest.get("generator") != "05_harness/generate_adapters.py@0.3":
        raise ValueError("Adapter Generator Version 漂移")

    resolved_target_root = target_root.resolve()
    plan: list[DeploymentItem] = []
    targets: set[Path] = set()
    declared_sources: set[Path] = set()
    for record in manifest.get("files", []):
        source_rel = confined(record["source"], "source")
        target_rel = confined(record["target"], "target")
        source_candidate = adapter_root / source_rel
        if source_candidate.is_symlink():
            raise ValueError(f"Adapter source 不得是符号链接: {source_rel}")
        source = source_candidate.resolve()
        if adapter_root not in source.parents:
            raise ValueError(f"Adapter source 越界: {source_rel}")
        require_regular(source, "Adapter Source")
        declared_sources.add(source)
        validate_native(source, record["format"])
        if target_rel in targets:
            raise ValueError(f"Adapter Manifest 包含重复目标: {target_rel}")
        targets.add(target_rel)
        reject_symlink_path(resolved_target_root, target_rel, "Adapter target")
        target = resolved_target_root / target_rel
        source_bytes = source.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()
        source_mode = oct(source.lstat().st_mode & 0o7777)
        if not target.exists():
            action, previous_digest, previous_mode = "CREATE", None, None
        else:
            require_regular(target, "Adapter Target")
            target_bytes = target.read_bytes()
            previous_digest = hashlib.sha256(target_bytes).hexdigest()
            previous_mode = oct(target.lstat().st_mode & 0o7777)
            action = "UNCHANGED" if target_bytes == source_bytes else "REPLACE"
        plan.append(DeploymentItem(source, target, resolved_target_root, target_rel, action, digest, source_mode, previous_digest, previous_mode))
    if not plan:
        raise ValueError("Adapter Manifest 没有 files")
    actual_sources = {
        item.resolve() for item in adapter_root.iterdir()
        if item.name != "manifest.toml" and item.is_file() and not item.is_symlink()
    }
    if actual_sources != declared_sources:
        raise ValueError("Adapter 目录存在未声明或缺失的 Generated 文件")
    for item in adapter_root.iterdir():
        if item.is_symlink() or (item.name != "manifest.toml" and not item.is_file()):
            raise ValueError(f"Adapter 目录包含 symlink 或特殊文件: {item.name}")
    return manifest, plan


def serialize(manifest: dict, target_root: Path, plan: list[DeploymentItem]) -> dict:
    return {
        "schema_version": "0.2.0",
        "platform": manifest["platform"],
        "maturity_state": manifest["maturity_state"],
        "target_root": str(target_root.resolve()),
        "files": [
            {
                "target": str(item.relative_target),
                "action": item.action,
                "source_sha256": item.sha256,
                "source_mode": item.source_mode,
                "previous_sha256": item.previous_sha256,
                "previous_mode": item.previous_mode,
            }
            for item in plan
        ],
    }


def plan_digest(document: dict) -> str:
    payload = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_replace(staged: Path, target: Path) -> None:
    staged.replace(target)


def remove_empty_parents(path: Path, stop: Path) -> None:
    """Remove rollback-created empty directories without crossing stop."""
    current = path
    resolved_stop = stop.resolve()
    while current != resolved_stop and resolved_stop in current.resolve().parents:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def apply_plan(
    manifest: dict,
    plan: list[DeploymentItem],
    backup_root: Path | None,
    *,
    authorization_ref: str,
    target_scope: str,
    record_root: Path,
) -> Path:
    if not AUTHORIZATION_PATTERN.fullmatch(authorization_ref or ""):
        raise ValueError("缺少有效 Deployment 单次授权引用")
    if target_scope not in {"PROJECT", "USER"}:
        raise ValueError("Deployment Target Scope 非法")
    if record_root.is_symlink():
        raise ValueError("Deployment Record Root 不得为 symlink")
    replacements = [item for item in plan if item.action == "REPLACE"]
    if replacements and backup_root is None:
        raise ValueError("覆盖现有文件前必须提供 --backup-dir")
    if backup_root is not None and backup_root.is_symlink():
        raise ValueError("Backup Root 不得为 symlink")

    document = serialize(manifest, plan[0].target_root, plan)
    digest = plan_digest(document)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    deployment_id = "deploy-" + now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12]
    record_root_created = not record_root.exists()
    record_root.mkdir(parents=True, exist_ok=True)
    record_path = record_root / f"{deployment_id}.json"
    if record_path.exists():
        raise ValueError("Deployment Record 已存在，不得覆盖")

    changed = [item for item in plan if item.action != "UNCHANGED"]
    staged: dict[Path, Path] = {}
    applied: list[DeploymentItem] = []
    created_backups: list[Path] = []
    try:
        for item in plan:
            reject_symlink_path(item.target_root, item.relative_target, "Adapter target")
            require_regular(item.source, "Adapter Source")
            if item.action == "CREATE":
                if item.target.exists() or item.target.is_symlink():
                    raise ValueError(f"部署计划已过期，CREATE 目标已经存在: {item.relative_target}")
            else:
                require_regular(item.target, "Adapter Target")
                current_digest = hashlib.sha256(item.target.read_bytes()).hexdigest()
                current_mode = oct(item.target.lstat().st_mode & 0o7777)
                if current_digest != item.previous_sha256 or current_mode != item.previous_mode:
                    raise ValueError(f"部署计划已过期，目标已变化: {item.relative_target}")
            if hashlib.sha256(item.source.read_bytes()).hexdigest() != item.sha256:
                raise ValueError(f"部署计划已过期，Adapter Source 已变化: {item.source}")
        for item in replacements:
            assert backup_root is not None
            resolved_backup_root = backup_root.resolve()
            reject_symlink_path(resolved_backup_root, item.relative_target, "Backup")
            backup = resolved_backup_root / item.relative_target
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists() or backup.is_symlink():
                raise ValueError(f"Backup 已存在，拒绝覆盖: {backup}")
            shutil.copy2(item.target, backup)
            created_backups.append(backup)
        for item in changed:
            item.target.parent.mkdir(parents=True, exist_ok=True)
            stage = item.target.parent / f".{item.target.name}.paos-stage-{uuid.uuid4().hex}"
            shutil.copy2(item.source, stage)
            staged[item.target] = stage
        for item in changed:
            reject_symlink_path(item.target_root, item.relative_target, "Adapter target")
            atomic_replace(staged[item.target], item.target)
            applied.append(item)
        record = {
            **document,
            "files": [
                {
                    **file_record,
                    "deployed_sha256": hashlib.sha256(item.target.read_bytes()).hexdigest(),
                    "deployed_mode": oct(item.target.lstat().st_mode & 0o7777),
                }
                for file_record, item in zip(document["files"], plan)
            ],
            "deployment_id": deployment_id,
            "plan_sha256": digest,
            "applied_at": now.isoformat().replace("+00:00", "Z"),
            "authorization_reference": authorization_ref,
            "target_scope": target_scope,
            "backup_root": str(backup_root.resolve()) if backup_root else None,
            "rollback_status": "READY" if replacements else "NOT_REQUIRED",
        }
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception:
        record_path.unlink(missing_ok=True)
        for item in reversed(applied):
            if item.action == "CREATE":
                item.target.unlink(missing_ok=True)
            else:
                assert backup_root is not None
                backup = backup_root.resolve() / item.relative_target
                if backup.is_file():
                    shutil.copy2(backup, item.target)
        for backup in reversed(created_backups):
            backup.unlink(missing_ok=True)
            assert backup_root is not None
            remove_empty_parents(backup.parent, backup_root)
        if record_root_created:
            try:
                record_root.rmdir()
            except OSError:
                pass
        raise
    finally:
        for stage in staged.values():
            stage.unlink(missing_ok=True)
    return record_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--record-dir", type=Path)
    parser.add_argument("--authorization-ref")
    parser.add_argument("--scope", choices=["PROJECT", "USER"])
    args = parser.parse_args()
    try:
        manifest, plan = build_plan(args.manifest, args.target, managed_adapter_root=MANAGED_ADAPTER_ROOT)
        print(json.dumps(serialize(manifest, args.target, plan), ensure_ascii=False, indent=2))
        if args.apply:
            if not args.record_dir or not args.authorization_ref or not args.scope:
                raise ValueError("Apply 必须提供 --record-dir、--authorization-ref 与 --scope")
            record = apply_plan(
                manifest,
                plan,
                args.backup_dir,
                authorization_ref=args.authorization_ref,
                target_scope=args.scope,
                record_root=args.record_dir,
            )
            print(f"DEPLOYED record={record}", file=sys.stderr)
        else:
            print("DRY_RUN: 未修改目标", file=sys.stderr)
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
