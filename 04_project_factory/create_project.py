#!/usr/bin/env python3
"""从版本化 Template Pack 安全创建独立项目。默认只执行 Dry Run。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError as exc:
        raise SystemExit("需要 Python 3.11+ 或安装 tomli") from exc


OS_ROOT = Path(__file__).resolve().parents[1]
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


@dataclass(frozen=True)
class PlannedFile:
    source: Path
    destination: Path
    content: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


def confined_relative(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"{label} 必须是仓库内相对路径: {value}")
    return path


def render(text: str, variables: dict[str, str]) -> str:
    missing = sorted(set(TOKEN_PATTERN.findall(text)) - variables.keys())
    if missing:
        raise ValueError(f"模板包含未提供变量: {', '.join(missing)}")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def load_plan(pack: Path, target: Path, variables: dict[str, str]) -> tuple[dict, list[PlannedFile]]:
    manifest_path = pack / "template.toml"
    if not manifest_path.is_file():
        raise ValueError("Template Pack 缺少 template.toml")
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    files: list[PlannedFile] = []
    destinations: set[Path] = set()
    for record in manifest.get("files", []):
        source_rel = confined_relative(record["source"], "source")
        destination_rel = confined_relative(record["destination"], "destination")
        source = (pack / source_rel).resolve()
        if pack.resolve() not in source.parents or not source.is_file():
            raise ValueError(f"模板来源不存在或越界: {source_rel}")
        destination = target / destination_rel
        if destination_rel in destinations:
            raise ValueError(f"重复目标路径: {destination_rel}")
        destinations.add(destination_rel)
        content = source.read_text(encoding="utf-8")
        if record.get("render", True):
            content = render(content, variables)
        files.append(PlannedFile(source, destination, content))
    if not files:
        raise ValueError("Template Pack 没有文件记录")
    return manifest, files


def validate_target(target: Path) -> None:
    resolved = target.resolve()
    if resolved == OS_ROOT or OS_ROOT in resolved.parents:
        raise ValueError("业务项目不得创建在 Personal AI OS 仓库内部")
    if target.exists() and any(target.iterdir()):
        raise ValueError("目标目录已经存在且非空")


def build_manifest(
    pack_manifest: dict,
    target: Path,
    variables: dict[str, str],
    files: list[PlannedFile],
    provisional: bool,
) -> dict:
    return {
        "schema_version": "0.1.0-working",
        "project_id": variables["PROJECT_ID"],
        "project_name": variables["PROJECT_NAME"],
        "owner": variables["OWNER"],
        "primary_type": variables["PRIMARY_TYPE"],
        "overlays": variables["OVERLAYS"].split(",") if variables["OVERLAYS"] else [],
        "project_status": "PROVISIONAL" if provisional else "GENERATED",
        "template_pack": pack_manifest.get("pack_id"),
        "template_version": pack_manifest.get("version"),
        "target": str(target.resolve()),
        "files": [
            {
                "path": str(item.destination.relative_to(target)),
                "sha256": item.sha256,
            }
            for item in files
        ],
    }


def write_project(target: Path, files: list[PlannedFile], manifest: dict, init_git: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for item in files:
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        if item.destination.exists():
            raise ValueError(f"拒绝覆盖: {item.destination}")
        item.destination.write_text(item.content, encoding="utf-8")
    (target / ".paos-init.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if init_git:
        result = subprocess.run(
            ["git", "init", "-b", "main"], cwd=target, text=True, capture_output=True
        )
        if result.returncode != 0:
            raise ValueError(f"Git 初始化失败: {result.stderr.strip()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-pack", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--primary-type", required=True)
    parser.add_argument("--overlay", action="append", default=[])
    parser.add_argument("--apply", action="store_true", help="实际创建；默认只输出 Dry Run")
    parser.add_argument("--provisional", action="store_true", help="允许 Candidate Pack 进行临时演练")
    parser.add_argument("--git", action="store_true", help="创建后初始化 Git main 分支")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if not SLUG_PATTERN.fullmatch(args.project_id):
            raise ValueError("project-id 必须是 2-63 位小写字母、数字或连字符")
        validate_target(args.target)
        config = tomllib.loads((Path(__file__).with_name("factory.toml")).read_text())
        if args.primary_type not in config["primary_types"]:
            raise ValueError("未知 primary-type")
        unknown_overlays = sorted(set(args.overlay) - set(config["allowed_overlays"]))
        if unknown_overlays:
            raise ValueError(f"未知 overlay: {', '.join(unknown_overlays)}")

        variables = {
            "PROJECT_ID": args.project_id,
            "PROJECT_NAME": args.name,
            "OWNER": args.owner,
            "PRIMARY_TYPE": args.primary_type,
            "OVERLAYS": ",".join(sorted(set(args.overlay))),
        }
        pack_manifest, files = load_plan(args.template_pack.resolve(), args.target, variables)
        state = pack_manifest.get("artifact_state")
        if state != "APPROVED" and not args.provisional:
            raise ValueError("正式创建只允许 APPROVED Template Pack")
        manifest = build_manifest(pack_manifest, args.target, variables, files, args.provisional)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        if args.apply:
            write_project(args.target, files, manifest, args.git)
            print(f"CREATED {args.target.resolve()}", file=sys.stderr)
        else:
            print("DRY_RUN: 未写入目标目录", file=sys.stderr)
        return 0
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
