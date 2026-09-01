#!/usr/bin/env python3
"""Personal AI OS 统一 CI Gate；默认 local-offline，不触发网络。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

BASE_CHECKS = [
    ("repository", [PYTHON, "05_harness/validate_repository.py"]),
    ("factory", [PYTHON, "04_project_factory/test_factory.py"]),
    ("schema", [PYTHON, "05_harness/test_schema_validation.py"]),
    ("deployment", [PYTHON, "06_deployment/test_deployment.py"]),
    ("tree-digest", [PYTHON, "05_harness/test_tree_digest.py"]),
    ("temp-cleanup", [PYTHON, "05_harness/test_temp_cleanup.py"]),
    ("adapters", [PYTHON, "05_harness/generate_adapters.py", "--check"]),
]
LOCAL_CHECKS = BASE_CHECKS[:3] + [
    ("release-audit", [PYTHON, "05_harness/test_release_audit.py"]),
] + BASE_CHECKS[3:]


def run_check(name: str, command: list[str], root: Path = ROOT) -> dict:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    combined = (result.stdout + result.stderr).strip().splitlines()
    return {
        "id": name,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "exit_code": result.returncode,
        "summary": combined[-1] if combined else "no output",
    }


def run_base_checks(root: Path = ROOT) -> list[dict]:
    """供 M2 与外层 CI 复用；不包含 Release Audit 自身，避免递归。"""
    return [run_check(name, command, root) for name, command in BASE_CHECKS]


def run_release_state(root: Path = ROOT) -> dict:
    """真实运行 Release Audit 并暴露 overall。

    `release_audit.py` 无论 overall 为 PASS/STALE/BLOCKED 都返回 exit 0，
    因此不能用退出码判断；此处直接解析 JSON，避免默认 profile 把 BLOCKED 显示成 PASS。
    BLOCKED/STALE 是开发期的正常状态，不使本 profile 失败；只有 FAIL 才失败。
    """
    result = subprocess.run(
        [PYTHON, "05_harness/release_audit.py"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return {
            "id": "release-state",
            "status": "FAIL",
            "exit_code": result.returncode,
            "summary": "release_audit.py 无法执行",
        }
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "id": "release-state",
            "status": "FAIL",
            "exit_code": result.returncode,
            "summary": "release_audit.py 输出不是合法 JSON",
        }
    overall = report.get("overall", "UNKNOWN")
    blocking = [
        f"{gate.get('id')}={gate.get('status')}"
        for gate in report.get("gates", [])
        if gate.get("status") != "PASS"
    ]
    return {
        "id": "release-state",
        "status": "FAIL" if overall == "FAIL" else overall,
        "exit_code": result.returncode,
        "summary": f"overall={overall}" + (f"; {', '.join(blocking)}" if blocking else ""),
    }


def build_report(profile: str) -> tuple[dict, int]:
    checks = [run_check(name, command) for name, command in LOCAL_CHECKS]
    checks.append(run_release_state())
    if any(check["status"] == "FAIL" for check in checks):
        return {"profile": profile, "status": "FAIL", "checks": checks}, 10
    if profile == "release-readiness":
        release = run_check(
            "release-readiness",
            [PYTHON, "05_harness/release_audit.py", "--require-release-ready"],
        )
        checks.append(release)
        if release["status"] != "PASS":
            return {"profile": profile, "status": "BLOCKED", "checks": checks}, 14
    return {"profile": profile, "status": "PASS", "checks": checks}, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["local-offline", "release-readiness"], default="local-offline")
    args = parser.parse_args()
    report, exit_code = build_report(args.profile)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
