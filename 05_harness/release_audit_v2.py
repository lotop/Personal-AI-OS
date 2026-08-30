#!/usr/bin/env python3
"""V1.1 Readiness V2：区分发布前 Gate 与批准后 Promotion。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError as exc:
        raise SystemExit("需要 Python 3.11+ 或安装 tomli") from exc

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


@dataclass(frozen=True)
class Gate:
    id: str
    name: str
    status: str
    evidence: str
    phase: str = "READINESS"
    mandatory: bool = True


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def command_gate(gate_id: str, name: str, command: list[str]) -> Gate:
    result = run(*command)
    if result.returncode == 0:
        evidence = (result.stdout.strip().splitlines() or ["PASS"])[-1]
        return Gate(gate_id, name, "PASS", evidence)
    evidence = (result.stdout + result.stderr).strip().splitlines()
    return Gate(gate_id, name, "FAIL", evidence[-1] if evidence else "command failed")


def repository_gate() -> Gate:
    head = run("git", "rev-parse", "HEAD")
    status = run("git", "status", "--porcelain")
    if head.returncode != 0:
        return Gate("R1", "Repository Identity", "FAIL", "Git HEAD 不存在")
    if status.stdout.strip():
        return Gate("R1", "Repository Identity", "BLOCKED", "Working Tree 非干净")
    return Gate("R1", "Repository Identity", "PASS", head.stdout.strip())


def inventory_gate() -> Gate:
    tracked = run("git", "ls-files")
    files = [line for line in tracked.stdout.splitlines() if line]
    missing = [path for path in files if not (ROOT / path).is_file()]
    if tracked.returncode != 0 or not files or missing:
        return Gate("R2", "Inventory & Provenance", "FAIL", f"tracked={len(files)} missing={len(missing)}")
    return Gate("R2", "Inventory & Provenance", "PASS", f"tracked_files={len(files)}; scope=git-tracked")


def template_structure_gate() -> Gate:
    packs = list((ROOT / "07_working/candidates").glob("*/template.toml"))
    status = "PASS" if packs else "BLOCKED"
    return Gate("R5a", "Template Structural Readiness", status, f"candidate_packs={len(packs)}; schema-bound")


def template_approval_gate() -> Gate:
    approved = []
    for manifest in (ROOT / "01_templates").glob("*/template.toml"):
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        if data.get("artifact_state") == "APPROVED" and data.get("approval_reference"):
            approved.append(manifest)
    if not approved:
        return Gate("R5b", "Template Founder Approval", "BLOCKED", "没有带 approval_reference 的 Approved Pack")
    return Gate("R5b", "Template Founder Approval", "PASS", f"approved_packs={len(approved)}")


def evidence_gate(gate_id: str, name: str, relative: str, marker: str, blocked: str) -> Gate:
    path = ROOT / relative
    if path.is_file() and marker in path.read_text(encoding="utf-8"):
        return Gate(gate_id, name, "PASS", relative)
    return Gate(gate_id, name, "BLOCKED", blocked)


def runtime_records() -> dict[str, dict]:
    data = tomllib.loads((ROOT / "02_registry/runtimes.toml").read_text(encoding="utf-8"))
    return {item["platform"]: item for item in data.get("runtimes", [])}


def runtime_gate(gate_id: str, name: str, platform: str, field: str, expected: str = "PASS") -> Gate:
    record = runtime_records().get(platform, {})
    value = record.get(field, "NOT_TESTED")
    if value == expected:
        return Gate(gate_id, name, "PASS", str(value))
    status = "BLOCKED_EXTERNAL_DATA_AUTHORIZATION" if value == "BLOCKED_EXTERNAL_DATA_AUTHORIZATION" else "BLOCKED"
    return Gate(gate_id, name, status, str(value))


def decision_gate(gate_id: str, name: str, decision_id: str, missing: str) -> Gate:
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    if decision_id in text and "状态：`APPROVED`" in text:
        return Gate(gate_id, name, "PASS", decision_id)
    return Gate(gate_id, name, "BLOCKED_FOUNDER_DECISION", missing)


def recovery_gate() -> Gate:
    path = ROOT / "07_working/reviews/RECOVERY_DRILL.md"
    if not path.is_file() or "结论：`PASS`" not in path.read_text(encoding="utf-8"):
        return Gate("R9", "Repository Recovery", "BLOCKED", "缺少 Recovery evidence")
    text = path.read_text(encoding="utf-8")
    marker = "> Source Commit：`"
    source = text.split(marker, 1)[1].split("`", 1)[0] if marker in text else ""
    head = run("git", "rev-parse", "HEAD").stdout.strip()
    if source != head:
        return Gate("R9", "Repository Recovery", "STALE", f"evidence_commit={source or 'missing'} current={head}")
    return Gate("R9", "Repository Recovery", "PASS", str(path.relative_to(ROOT)))


def promotion_gate() -> Gate:
    tags = run("git", "tag", "--list", "v1.1*")
    if tags.stdout.strip():
        return Gate("P1", "Tag & Canonical Promotion", "PASS", tags.stdout.strip().splitlines()[-1], "PROMOTION", False)
    return Gate("P1", "Tag & Canonical Promotion", "NOT_AUTHORIZED", "等待 R12 Founder Approval", "PROMOTION", False)


def audit() -> list[Gate]:
    test_commands = [
        [PYTHON, "04_project_factory/test_factory.py"],
        [PYTHON, "05_harness/test_schema_validation.py"],
        [PYTHON, "06_deployment/test_deployment.py"],
        [PYTHON, "05_harness/test_tree_digest.py"],
    ]
    tests_pass = all(run(*command).returncode == 0 for command in test_commands)
    return [
        evidence_gate("R0", "Release Scope & Review Pack", "07_working/reviews/FOUNDER_REVIEW_PACK.md", "Founder Review Pack", "缺少 Founder Review Pack"),
        repository_gate(),
        inventory_gate(),
        command_gate("R3", "Schema Syntax & Binding", [PYTHON, "05_harness/validate_repository.py"]),
        command_gate("R4", "Cross-file Invariants & Boundary", [PYTHON, "05_harness/validate_repository.py"]),
        template_structure_gate(),
        template_approval_gate(),
        command_gate("R6a", "Factory Engine Safety", [PYTHON, "04_project_factory/test_factory.py"]),
        evidence_gate("R6b", "Factory Provisional E2E", "07_working/reviews/PROJECT_FACTORY_PROVISIONAL_ACCEPTANCE.md", "PASS_PROVISIONAL_ONLY", "缺少 provisional E2E"),
        evidence_gate("R6c", "Factory Formal E2E", "07_working/reviews/PROJECT_FACTORY_ACCEPTANCE.md", "结论：`PASS`", "等待 Approved Template Pack"),
        command_gate("R7a", "Adapter Generation", [PYTHON, "05_harness/generate_adapters.py", "--check"]),
        runtime_gate("R7b", "Codex Live Runtime", "codex", "runtime_smoke"),
        runtime_gate("R7c", "Gemini Config Load", "gemini-cli", "config_load"),
        runtime_gate("R7d", "Gemini Live Runtime", "gemini-cli", "runtime_smoke"),
        decision_gate("R8", "V1.0 Baseline Disposition", "PAOS-BASELINE-001", "V1.0 原件不可得，尚无 disposition"),
        recovery_gate(),
        command_gate("R10", "Local Security Controls", [PYTHON, "05_harness/validate_repository.py"]),
        Gate("R11", "Test Assurance", "PASS" if tests_pass else "FAIL", "4 suites; includes factory/deployment rollback and tree determinism"),
        decision_gate("R12", "Founder Release Approval", "PAOS-REL-001", "缺少固定 commit 的 V1.1 Release Approval"),
        promotion_gate(),
        Gate("P2", "Post-promotion Verification", "NOT_STARTED", "仅在 P1 后执行", "PROMOTION", False),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-release-ready", action="store_true")
    args = parser.parse_args()
    gates = audit()
    readiness = [gate for gate in gates if gate.phase == "READINESS" and gate.mandatory]
    overall = "PASS" if all(gate.status == "PASS" for gate in readiness) else "BLOCKED"
    print(json.dumps({"overall": overall, "gates": [asdict(gate) for gate in gates]}, ensure_ascii=False, indent=2))
    if any(gate.status == "FAIL" for gate in readiness):
        return 1
    if args.require_release_ready and overall != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
