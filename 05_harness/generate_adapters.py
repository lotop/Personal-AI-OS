#!/usr/bin/env python3
"""从 adapter_profiles.toml 确定性生成 Codex 与 Gemini CLI Adapter。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError as exc:
        raise SystemExit("需要 Python 3.11+ 或安装 tomli") from exc


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "00_system/compatibility/adapter_profiles.toml"
OUTPUT_ROOT = ROOT / "03_adapters"
GENERATOR = "05_harness/generate_adapters.py@0.1"


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_manifest(platform: str, source: str, target: str, format_name: str) -> str:
    return (
        'schema_version = "0.1.0-working"\n'
        'artifact_class = "GENERATED"\n'
        'maturity_state = "CANDIDATE"\n'
        f"platform = {toml_string(platform)}\n"
        f"generator = {toml_string(GENERATOR)}\n"
        'source_files = ["AGENTS.md", "00_system/compatibility/adapter_profiles.toml"]\n\n'
        "[[files]]\n"
        f"source = {toml_string(source)}\n"
        f"target = {toml_string(target)}\n"
        f"format = {toml_string(format_name)}\n"
    )


def render_outputs() -> dict[Path, str]:
    profiles = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    codex = profiles["codex"]
    codex_settings = codex["settings"]
    codex_config = (
        "# GENERATED CANDIDATE. 修改源文件而不是本文件。\n"
        f"# Source: {PROFILE_PATH.relative_to(ROOT)}\n\n"
        f"project_doc_max_bytes = {codex_settings['project_doc_max_bytes']}\n"
        "project_root_markers = ["
        + ", ".join(toml_string(item) for item in codex_settings["project_root_markers"])
        + "]\n"
    )

    gemini = profiles["gemini_cli"]
    gemini_settings = {
        "context": {
            "fileName": gemini["context"]["fileName"],
            "loadFromIncludeDirectories": gemini["context"]["loadFromIncludeDirectories"],
            "fileFiltering": gemini["context"]["fileFiltering"],
        }
    }
    gemini_json = json.dumps(gemini_settings, ensure_ascii=False, indent=2) + "\n"

    return {
        OUTPUT_ROOT / "codex/config.toml": codex_config,
        OUTPUT_ROOT / "codex/manifest.toml": render_manifest(
            "codex", "config.toml", codex["target"], "toml"
        ),
        OUTPUT_ROOT / "gemini-cli/settings.json": gemini_json,
        OUTPUT_ROOT / "gemini-cli/manifest.toml": render_manifest(
            "gemini-cli", "settings.json", gemini["target"], "json"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只检查生成结果是否最新")
    args = parser.parse_args()

    mismatches: list[str] = []
    for path, expected in render_outputs().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    if mismatches:
        for path in mismatches:
            print(f"OUTDATED: {path}")
        return 1
    print("ADAPTERS_OK" if args.check else "ADAPTERS_GENERATED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
