#!/usr/bin/env python3
"""安全部署单个平台 Adapter。默认只输出 Dry Run 计划。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from dataclasses import dataclass
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


@dataclass(frozen=True)
class DeploymentItem:
    source: Path
    target: Path
    target_root: Path
    relative_target: Path
    action: str
    sha256: str
    previous_sha256: str | None


def confined(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"{label} 必须是安全相对路径: {value}")
    return path


def reject_symlink_path(root: Path, relative: Path, label: str) -> None:
    """拒绝受管目标路径中的现有 symlink，避免读写逃逸到目标根之外。"""
    current = root.resolve()
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label} 路径不得经过 symlink: {relative}")


def validate_native(path: Path, format_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    if format_name == "toml":
        tomllib.loads(text)
    elif format_name == "json":
        json.loads(text)
    elif format_name != "markdown":
        raise ValueError(f"未知格式: {format_name}")


def build_plan(manifest_path: Path, target_root: Path) -> tuple[dict, list[DeploymentItem]]:
    manifest_path = manifest_path.resolve()
    adapter_root = manifest_path.parent
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    for field in ("platform", "artifact_class", "maturity_state", "generator", "source_files", "files"):
        if not manifest.get(field):
            raise ValueError(f"Adapter Manifest 缺少字段: {field}")
    if manifest.get("artifact_class") != "GENERATED":
        raise ValueError("Adapter artifact_class 必须为 GENERATED")
    if manifest.get("maturity_state") not in {"WORKING", "APPROVED"}:
        raise ValueError("Adapter maturity_state 不允许部署演练")

    plan: list[DeploymentItem] = []
    targets: set[Path] = set()
    for record in manifest.get("files", []):
        source_rel = confined(record["source"], "source")
        target_rel = confined(record["target"], "target")
        source = (adapter_root / source_rel).resolve()
        if (adapter_root / source_rel).is_symlink():
            raise ValueError(f"Adapter source 不得是符号链接: {source_rel}")
        if adapter_root not in source.parents or not source.is_file():
            raise ValueError(f"Adapter source 不存在或越界: {source_rel}")
        validate_native(source, record["format"])
        if target_rel in targets:
            raise ValueError(f"Adapter Manifest 包含重复目标: {target_rel}")
        targets.add(target_rel)
        resolved_target_root = target_root.resolve()
        reject_symlink_path(resolved_target_root, target_rel, "Adapter target")
        target = resolved_target_root / target_rel
        source_bytes = source.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()
        if not target.exists():
            action = "CREATE"
            previous_digest = None
        elif target.read_bytes() == source_bytes:
            action = "UNCHANGED"
            previous_digest = digest
        else:
            action = "REPLACE"
            previous_digest = hashlib.sha256(target.read_bytes()).hexdigest()
        plan.append(
            DeploymentItem(
                source,
                target,
                resolved_target_root,
                target_rel,
                action,
                digest,
                previous_digest,
            )
        )
    if not plan:
        raise ValueError("Adapter Manifest 没有 files")
    return manifest, plan


def atomic_replace(staged: Path, target: Path) -> None:
    staged.replace(target)


def apply_plan(plan: list[DeploymentItem], backup_root: Path | None) -> None:
    replacements = [item for item in plan if item.action == "REPLACE"]
    if replacements and backup_root is None:
        raise ValueError("覆盖现有文件前必须提供 --backup-dir")
    changed = [item for item in plan if item.action != "UNCHANGED"]
    staged: dict[Path, Path] = {}
    applied: list[DeploymentItem] = []
    try:
        for item in plan:
            reject_symlink_path(item.target_root, item.relative_target, "Adapter target")
            if item.action == "CREATE":
                if item.target.exists():
                    raise ValueError(f"部署计划已过期，CREATE 目标已经存在: {item.relative_target}")
            else:
                if not item.target.is_file():
                    raise ValueError(f"部署计划已过期，目标缺失: {item.relative_target}")
                current_digest = hashlib.sha256(item.target.read_bytes()).hexdigest()
                if current_digest != item.previous_sha256:
                    raise ValueError(f"部署计划已过期，目标内容已变化: {item.relative_target}")
            if hashlib.sha256(item.source.read_bytes()).hexdigest() != item.sha256:
                raise ValueError(f"部署计划已过期，Adapter Source 已变化: {item.source}")
        for item in replacements:
            assert backup_root is not None
            resolved_backup_root = backup_root.resolve()
            reject_symlink_path(resolved_backup_root, item.relative_target, "Backup")
            backup = resolved_backup_root / item.relative_target
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                raise ValueError(f"Backup 已存在，拒绝覆盖: {backup}")
            shutil.copy2(item.target, backup)
        for item in changed:
            item.target.parent.mkdir(parents=True, exist_ok=True)
            stage = item.target.parent / f".{item.target.name}.paos-stage-{uuid.uuid4().hex}"
            shutil.copy2(item.source, stage)
            staged[item.target] = stage
        for item in changed:
            atomic_replace(staged[item.target], item.target)
            applied.append(item)
    except Exception:
        for item in reversed(applied):
            if item.action == "CREATE":
                item.target.unlink(missing_ok=True)
            else:
                assert backup_root is not None
                backup = backup_root.resolve() / item.relative_target
                if backup.is_file():
                    shutil.copy2(backup, item.target)
        raise
    finally:
        for stage in staged.values():
            stage.unlink(missing_ok=True)


def serialize(manifest: dict, target_root: Path, plan: list[DeploymentItem]) -> dict:
    return {
        "platform": manifest["platform"],
        "maturity_state": manifest["maturity_state"],
        "target_root": str(target_root.resolve()),
        "files": [
            {
                "target": str(item.relative_target),
                "action": item.action,
                "sha256": item.sha256,
            }
            for item in plan
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    args = parser.parse_args()
    try:
        manifest, plan = build_plan(args.manifest, args.target)
        print(json.dumps(serialize(manifest, args.target, plan), ensure_ascii=False, indent=2))
        if args.apply:
            apply_plan(plan, args.backup_dir)
            print("DEPLOYED", file=sys.stderr)
        else:
            print("DRY_RUN: 未修改目标", file=sys.stderr)
        return 0
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
