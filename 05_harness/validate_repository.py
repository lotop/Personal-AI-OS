#!/usr/bin/env python3
"""Personal AI OS V1.1 仓库最小验证器。"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 兼容
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError as exc:
        raise SystemExit("需要 Python 3.11+ 或安装 tomli") from exc


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    "00_system",
    "01_templates",
    "02_registry",
    "03_adapters",
    "04_project_factory",
    "05_harness",
    "06_deployment",
    "07_working/specs",
    "07_working/candidates",
    "07_working/reviews",
    "08_history",
    "09_archive",
    "99_temp",
]

REQUIRED_FILES = [
    "README.md",
    "PROJECT.md",
    "AGENTS.md",
    "DECISIONS.md",
    "CHANGELOG.md",
    "SYSTEM.toml",
    "07_working/specs/PHYSICAL_ARCHITECTURE.md",
    "07_working/reviews/CONSOLIDATION_V1.1.md",
    "08_history/V1.0_BASELINE_NOTE.md",
    "04_project_factory/FACTORY_SPEC.md",
    "06_deployment/CODEX_DEPLOYMENT.md",
    "06_deployment/GEMINI_DEPLOYMENT.md",
]

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_toml(path: Path, report: Report) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        report.error(f"TOML 解析失败: {path.relative_to(ROOT)}: {exc}")
        return {}


def validate_required(report: Report) -> None:
    for relative in REQUIRED_DIRS:
        if not (ROOT / relative).is_dir():
            report.error(f"缺少目录: {relative}")
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            report.error(f"缺少文件: {relative}")


def validate_structured_files(report: Report) -> dict[Path, dict]:
    parsed: dict[Path, dict] = {}
    for path in sorted(ROOT.rglob("*.toml")):
        parsed[path] = load_toml(path, report)
    for path in sorted(ROOT.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            report.error(f"JSON 解析失败: {path.relative_to(ROOT)}: {exc}")
    for path in sorted(ROOT.rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            report.error(f"Python 语法失败: {path.relative_to(ROOT)}: {exc}")
    return parsed


def validate_unique_ids(parsed: dict[Path, dict], report: Report) -> None:
    collections = {
        "02_registry/tasks.toml": "tasks",
        "02_registry/projects.toml": "projects",
        "02_registry/agents.toml": "agents",
        "02_registry/hooks.toml": "hooks",
        "00_system/modes/registry.toml": "modes",
        "00_system/compatibility/platforms.toml": "platforms",
    }
    for relative, key in collections.items():
        data = parsed.get(ROOT / relative, {})
        records = data.get(key, [])
        ids = [record.get("id") for record in records]
        if any(value is None for value in ids):
            report.error(f"{relative} 存在缺少 id 的记录")
        if len(ids) != len(set(ids)):
            report.error(f"{relative} 存在重复 id")


def validate_tasks(parsed: dict[Path, dict], report: Report) -> None:
    relative = "02_registry/tasks.toml"
    data = parsed.get(ROOT / relative, {})
    allowed_statuses = set(data.get("allowed_statuses", []))
    allowed_progress = set(data.get("allowed_progress", []))
    for task in data.get("tasks", []):
        task_id = task.get("id", "<unknown>")
        if task.get("status") not in allowed_statuses:
            report.error(f"{task_id} 的 status 非法")
        for field in (
            "research_status",
            "local_artifact_status",
            "review_status",
            "implementation_status",
        ):
            if task.get(field) not in allowed_progress:
                report.error(f"{task_id} 缺少或非法字段 {field}")


def validate_lifecycle(parsed: dict[Path, dict], report: Report) -> None:
    data = parsed.get(ROOT / "00_system/lifecycle/states.toml", {})
    classes = set(data.get("artifact_classes", []))
    maturity = set(data.get("maturity_states", []))
    if "SOURCE" not in classes:
        report.error("SOURCE 必须属于 artifact_classes")
    if "SOURCE" in maturity:
        report.error("SOURCE 不得属于 maturity_states")
    if not {"WORKING", "CANDIDATE", "APPROVED", "CANONICAL"}.issubset(maturity):
        report.error("maturity_states 缺少 Promotion 核心状态")


def validate_secrets(report: Report) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name == ".DS_Store":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                report.error(f"疑似 Secret: {path.relative_to(ROOT)}")


def validate_git(report: Report) -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        report.error("当前目录不是可用 Git Repository")
    elif status.stdout.strip():
        report.warn("Git Working Tree 尚未形成干净 Baseline")

    remote = subprocess.run(
        ["git", "remote"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if "origin" not in remote.stdout.split():
        report.warn("尚未配置 origin")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="将 Warning 视为失败")
    args = parser.parse_args()

    report = Report()
    validate_required(report)
    parsed = validate_structured_files(report)
    validate_unique_ids(parsed, report)
    validate_tasks(parsed, report)
    validate_lifecycle(parsed, report)
    validate_secrets(report)
    validate_git(report)

    print(f"ERRORS={len(report.errors)} WARNINGS={len(report.warnings)}")
    for message in report.errors:
        print(f"ERROR: {message}")
    for message in report.warnings:
        print(f"WARN: {message}")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
