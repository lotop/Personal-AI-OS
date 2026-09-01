#!/usr/bin/env python3
"""从 Approved Adapter Profile 确定性生成平台 Adapter；默认只输出计划。"""

from __future__ import annotations

import argparse
import json
import stat
import shutil
import sys
import uuid
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
PROFILE_PATH = ROOT / "00_system/compatibility/adapter_profiles.toml"
OUTPUT_ROOT = ROOT / "03_adapters"
GENERATOR = "05_harness/generate_adapters.py@0.3"


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def require_keys(data: dict, expected: set[str], label: str) -> None:
    actual = set(data)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise ValueError(f"{label} 字段漂移: missing={missing} extra={extra}")


def load_profiles(path: Path = PROFILE_PATH) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Adapter Profile 缺失或为 symlink")
    profiles = tomllib.loads(path.read_text(encoding="utf-8"))
    require_keys(
        profiles,
        {
            "schema_version", "artifact_class", "maturity_state",
            "canonical_authority", "approval_reference", "codex", "claude_code", "gemini_cli",
        },
        "Adapter Profile",
    )
    if (
        profiles["schema_version"] != "0.2.0"
        or profiles["artifact_class"] != "CONFIG"
        or profiles["maturity_state"] != "APPROVED"
        or profiles["canonical_authority"] != "FOUNDER_APPROVED"
        or profiles["approval_reference"] != "PAOS-020"
    ):
        raise ValueError("Adapter Profile 尚未形成 PAOS-020 Approved Contract")
    codex = profiles["codex"]
    require_keys(codex, {"platform", "native_format", "target", "settings"}, "Codex Profile")
    require_keys(codex["settings"], {"project_doc_max_bytes", "project_root_markers"}, "Codex Settings")
    claude = profiles["claude_code"]
    require_keys(claude, {"platform", "native_format", "context_target", "settings_target", "context", "settings"}, "Claude Code Profile")
    require_keys(claude["context"], {"imports"}, "Claude Context")
    require_keys(claude["settings"], {"schema", "permissions"}, "Claude Settings")
    require_keys(claude["settings"]["permissions"], {"deny"}, "Claude Permissions")
    gemini = profiles["gemini_cli"]
    require_keys(gemini, {"platform", "native_format", "target", "context"}, "Gemini Profile")
    require_keys(gemini["context"], {"fileName", "loadMemoryFromIncludeDirectories", "fileFiltering"}, "Gemini Context")
    require_keys(gemini["context"]["fileFiltering"], {"respectGitIgnore"}, "Gemini Filtering")
    targets = {codex["target"], claude["context_target"], claude["settings_target"], gemini["target"]}
    if targets != {".codex/config.toml", "CLAUDE.md", ".claude/settings.json", ".gemini/settings.json"}:
        raise ValueError("Adapter Profile Target 漂移")
    if codex["platform"] != "codex" or claude["platform"] != "claude-code" or gemini["platform"] != "gemini-cli":
        raise ValueError("Adapter Profile Platform 漂移")
    return profiles


def render_manifest(platform: str, source: str, target: str, format_name: str) -> str:
    return (
        'schema_version = "0.2.0-working"\nartifact_class = "GENERATED"\n'
        'maturity_state = "WORKING"\n'
        f"platform = {toml_string(platform)}\n"
        f"generator = {toml_string(GENERATOR)}\n"
        'source_files = ["AGENTS.md", "00_system/compatibility/adapter_profiles.toml"]\n\n'
        "[[files]]\n"
        f"source = {toml_string(source)}\n"
        f"target = {toml_string(target)}\n"
        f"format = {toml_string(format_name)}\n"
    )


def render_outputs(profile_path: Path = PROFILE_PATH, output_root: Path = OUTPUT_ROOT) -> dict[Path, str]:
    profiles = load_profiles(profile_path)
    codex = profiles["codex"]
    codex_settings = codex["settings"]
    source_label = "00_system/compatibility/adapter_profiles.toml" if profile_path == PROFILE_PATH else profile_path.name
    codex_config = (
        "# GENERATED WORKING. 修改 Source 而不是本文件。\n"
        f"# Source: {source_label}\n\n"
        f"project_doc_max_bytes = {codex_settings['project_doc_max_bytes']}\n"
        "project_root_markers = ["
        + ", ".join(toml_string(item) for item in codex_settings["project_root_markers"])
        + "]\n"
    )
    claude = profiles["claude_code"]
    claude_context = (
        "<!-- GENERATED WORKING. 修改 Source 或生成器，不直接修改本文件。 -->\n"
        "<!-- Source: 00_system/compatibility/adapter_profiles.toml -->\n\n"
        + "\n".join(f"@{item}" for item in claude["context"]["imports"])
        + "\n\n## Claude Code Adapter\n\n"
        "本文件是 Generated Working Adapter。统一项目规则来自 `AGENTS.md`；不得在此复制或分叉 Canonical Rule。\n\n"
        "### 初始化与诊断\n\n"
        "- 用 `/context` 确认 Context Load，用 `/status` 确认 Settings Source；两者不得互相替代。\n"
        "- 若 `@AGENTS.md` 导入失败，在复杂写入前停止并报告。\n"
        "- 不使用 `/init` 覆盖本文件；改进回到 Adapter Source 和生成器。\n\n"
        "### Claude Code 专属边界\n\n"
        "- Auto Memory、`CLAUDE.local.md` 和 Conversation 不自动成为正式事实。\n"
        "- 不自行创建或启用 Rules、Hooks、Skills、Subagents 或 MCP。\n"
        "- 项目配置需经 Workspace Trust；Live Runtime 与外部数据授权单独验证。\n"
    )
    claude_json = json.dumps({"$schema": claude["settings"]["schema"], "permissions": {"deny": claude["settings"]["permissions"]["deny"]}}, ensure_ascii=False, indent=2) + "\n"
    gemini = profiles["gemini_cli"]
    gemini_json = json.dumps(
        {"context": {
            "fileName": gemini["context"]["fileName"],
            "loadMemoryFromIncludeDirectories": gemini["context"]["loadMemoryFromIncludeDirectories"],
            "fileFiltering": gemini["context"]["fileFiltering"],
        }},
        ensure_ascii=False,
        indent=2,
    ) + "\n"
    return {
        output_root / "codex/config.toml": codex_config,
        output_root / "codex/manifest.toml": render_manifest("codex", "config.toml", codex["target"], "toml"),
        output_root / "claude-code/CLAUDE.md": claude_context,
        output_root / "claude-code/settings.json": claude_json,
        output_root / "claude-code/manifest.toml": (
            'schema_version = "0.2.0-working"\nartifact_class = "GENERATED"\n'
            'maturity_state = "WORKING"\nplatform = "claude-code"\n'
            f'generator = {toml_string(GENERATOR)}\n'
            'source_files = ["AGENTS.md", "00_system/compatibility/adapter_profiles.toml"]\n\n'
            '[[files]]\nsource = "CLAUDE.md"\ntarget = "CLAUDE.md"\nformat = "markdown"\n\n'
            '[[files]]\nsource = "settings.json"\ntarget = ".claude/settings.json"\nformat = "json"\n'
        ),
        output_root / "gemini-cli/settings.json": gemini_json,
        output_root / "gemini-cli/manifest.toml": render_manifest("gemini-cli", "settings.json", gemini["target"], "json"),
    }


def validate_output(path: Path, content: str) -> None:
    if path.suffix == ".json":
        json.loads(content)
    elif path.suffix == ".toml":
        tomllib.loads(content)
    elif path.suffix != ".md":
        raise ValueError(f"未知 Adapter 输出类型: {path}")


def reject_output_symlinks(output_root: Path, target: Path) -> None:
    root = output_root.resolve()
    current = output_root
    for part in target.relative_to(output_root).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Adapter 输出路径不得经过 symlink: {target.relative_to(output_root)}")
    parent = target.parent.resolve()
    if parent != root and root not in parent.parents:
        raise ValueError(f"Adapter 输出越界: {target}")


def build_plan(outputs: dict[Path, str]) -> list[dict[str, str]]:
    roots = {path.parents[1] for path in outputs}
    if len(roots) != 1:
        raise ValueError("Adapter 输出必须位于同一受管 Root")
    output_root = roots.pop()
    expected = {path.resolve() for path in outputs}
    allowed = {output_root / "README.md"}
    if output_root.exists():
        for item in output_root.rglob("*"):
            if item.name.startswith(".paos-adapter-stage-"):
                raise ValueError(f"Adapter 输出目录存在残留 Staging: {item}")
            if item.is_symlink():
                raise ValueError(f"Adapter 输出目录包含 symlink: {item}")
            if item.is_file() and not stat.S_ISREG(item.lstat().st_mode):
                raise ValueError(f"Adapter 输出目录包含特殊文件: {item}")
            if item.is_file() and item.resolve() not in expected and item not in allowed:
                raise ValueError(f"Adapter 输出目录包含未声明文件: {item}")
    plan = []
    for path, content in sorted(outputs.items(), key=lambda item: str(item[0])):
        validate_output(path, content)
        if path.is_symlink():
            raise ValueError(f"Adapter 输出不得是 symlink: {path}")
        if path.exists() and not path.is_file():
            raise ValueError(f"Adapter 输出不得是特殊文件: {path}")
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        action = "UNCHANGED" if current == content else ("UPDATE" if current is not None else "CREATE")
        plan.append({"path": str(path), "action": action})
    return plan


def replace_generated(staged: Path, target: Path) -> None:
    staged.replace(target)


def write_outputs(outputs: dict[Path, str], output_root: Path = OUTPUT_ROOT) -> None:
    for target in outputs:
        reject_output_symlinks(output_root, target)
    stage_root = output_root / f".paos-adapter-stage-{uuid.uuid4().hex}"
    previous: dict[Path, tuple[bytes, int] | None] = {}
    applied: list[Path] = []
    try:
        stage_root.mkdir()
        for target, content in outputs.items():
            stage = stage_root / target.relative_to(output_root)
            stage.parent.mkdir(parents=True, exist_ok=True)
            stage.write_text(content, encoding="utf-8")
            validate_output(stage, content)
            previous[target] = (
                (target.read_bytes(), target.lstat().st_mode & 0o7777)
                if target.is_file() else None
            )
        for target in sorted(outputs, key=str):
            reject_output_symlinks(output_root, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            replace_generated(stage_root / target.relative_to(output_root), target)
            applied.append(target)
    except Exception:
        for target in reversed(applied):
            prior = previous[target]
            if prior is None:
                target.unlink(missing_ok=True)
            else:
                old, old_mode = prior
                rollback = target.parent / f".{target.name}.paos-rollback-{uuid.uuid4().hex}"
                rollback.write_bytes(old)
                rollback.chmod(old_mode)
                rollback.replace(target)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        outputs = render_outputs()
        plan = build_plan(outputs)
        mismatches = [item for item in plan if item["action"] != "UNCHANGED"]
        if args.check:
            for item in mismatches:
                print(f"OUTDATED: {Path(item['path']).relative_to(ROOT)}")
            if mismatches:
                return 1
            print("ADAPTERS_OK")
            return 0
        if args.write:
            write_outputs(outputs)
            print("ADAPTERS_GENERATED")
            return 0
        print(json.dumps({"status": "PLANNED", "write": False, "files": plan}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
