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

LOCAL_CHECKS = [
    ("repository", [PYTHON, "05_harness/validate_repository.py"]),
    ("factory", [PYTHON, "04_project_factory/test_factory.py"]),
    ("schema", [PYTHON, "05_harness/test_schema_validation.py"]),
    ("release-audit", [PYTHON, "05_harness/test_release_audit.py"]),
    ("deployment", [PYTHON, "06_deployment/test_deployment.py"]),
    ("tree-digest", [PYTHON, "05_harness/test_tree_digest.py"]),
    ("temp-cleanup", [PYTHON, "05_harness/test_temp_cleanup.py"]),
    ("adapters", [PYTHON, "05_harness/generate_adapters.py", "--check"]),
]


def run_check(name: str, command: list[str]) -> dict:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    combined = (result.stdout + result.stderr).strip().splitlines()
    return {
        "id": name,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "exit_code": result.returncode,
        "summary": combined[-1] if combined else "no output",
    }


def build_report(profile: str) -> tuple[dict, int]:
    checks = [run_check(name, command) for name, command in LOCAL_CHECKS]
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
