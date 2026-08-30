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
    relative_target: Path
    action: str
    sha256: str


def confined(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"{label} 必须是安全相对路径: {value}")
    return path


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
    if manifest.get("maturity_state") not in {"WORKING", "APPROVED"}:
        raise ValueError("Adapter maturity_state 不允许部署演练")

    plan: list[DeploymentItem] = []
    for record in manifest.get("files", []):
        source_rel = confined(record["source"], "source")
        target_rel = confined(record["target"], "target")
        source = (adapter_root / source_rel).resolve()
        if (adapter_root / source_rel).is_symlink():
            raise ValueError(f"Adapter source 不得是符号链接: {source_rel}")
        if adapter_root not in source.parents or not source.is_file():
            raise ValueError(f"Adapter source 不存在或越界: {source_rel}")
        validate_native(source, record["format"])
        target = target_root.resolve() / target_rel
        source_bytes = source.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()
        if not target.exists():
            action = "CREATE"
        elif target.read_bytes() == source_bytes:
            action = "UNCHANGED"
        else:
            action = "REPLACE"
        plan.append(DeploymentItem(source, target, target_rel, action, digest))
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
        for item in replacements:
            assert backup_root is not None
            backup = backup_root.resolve() / item.relative_target
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
