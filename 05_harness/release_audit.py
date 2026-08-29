#!/usr/bin/env python3
"""审计 Personal AI OS V1.1 Release Gates，不执行 Promotion。"""

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


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def repository_gate() -> Gate:
    head = run("git", "rev-parse", "HEAD")
    status = run("git", "status", "--porcelain")
    if head.returncode != 0:
        return Gate("G0", "Repository", "FAIL", "Git HEAD 不存在")
    if status.stdout.strip():
        return Gate("G0", "Repository", "BLOCKED", "Working Tree 非干净")
    return Gate("G0", "Repository", "PASS", head.stdout.strip())


def inventory_gate() -> Gate:
    tracked = run("git", "ls-files")
    files = [line for line in tracked.stdout.splitlines() if line]
    if tracked.returncode != 0 or not files:
        return Gate("G1", "Inventory", "FAIL", "无法读取 Git 文件清单")
    missing = [path for path in files if not (ROOT / path).is_file()]
    if missing:
        return Gate("G1", "Inventory", "FAIL", f"缺失 {len(missing)} 个已跟踪文件")
    return Gate("G1", "Inventory", "PASS", f"tracked_files={len(files)}")


def command_gate(gate_id: str, name: str, command: list[str]) -> Gate:
    result = run(*command)
    if result.returncode == 0:
        last = (result.stdout.strip().splitlines() or ["PASS"])[-1]
        return Gate(gate_id, name, "PASS", last)
    evidence = (result.stdout + result.stderr).strip().splitlines()
    return Gate(gate_id, name, "FAIL", evidence[-1] if evidence else "command failed")


def template_gate() -> Gate:
    approved: list[Path] = []
    for manifest in (ROOT / "01_templates").glob("*/template.toml"):
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        if data.get("artifact_state") == "APPROVED":
            approved.append(manifest)
    if not approved:
        return Gate("G4", "Templates", "BLOCKED", "没有 Approved Template Pack")
    return Gate("G4", "Templates", "PASS", f"approved_packs={len(approved)}")


def factory_gate() -> Gate:
    evidence = ROOT / "07_working/reviews/PROJECT_FACTORY_ACCEPTANCE.md"
    if not evidence.is_file() or "`PASS`" not in evidence.read_text(encoding="utf-8"):
        return Gate("G5", "Project Factory", "BLOCKED", "缺少正式 Template Pack 端到端验收")
    return Gate("G5", "Project Factory", "PASS", str(evidence.relative_to(ROOT)))


def deployment_gate() -> Gate:
    runtimes = tomllib.loads((ROOT / "02_registry/runtimes.toml").read_text(encoding="utf-8"))
    records = {item["platform"]: item for item in runtimes.get("runtimes", [])}
    codex = records.get("codex", {})
    gemini = records.get("gemini-cli", {})
    if codex.get("runtime_smoke") != "PASS":
        return Gate("G7", "Deployment", "BLOCKED", "Codex Runtime Smoke 尚未 PASS")
    if gemini.get("runtime_smoke") != "PASS":
        return Gate("G7", "Deployment", "BLOCKED", "Gemini CLI Runtime Smoke 尚未 PASS")
    return Gate("G7", "Deployment", "PASS", "Codex 与 Gemini Runtime Smoke 均通过")


def recovery_gate() -> Gate:
    evidence = ROOT / "07_working/reviews/RECOVERY_DRILL.md"
    if evidence.is_file() and "结论：`PASS`" in evidence.read_text(encoding="utf-8"):
        return Gate("G8", "Recovery", "PASS", str(evidence.relative_to(ROOT)))
    return Gate("G8", "Recovery", "BLOCKED", "缺少通过的恢复演练记录")


def approval_gate() -> Gate:
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    if "PAOS-REL-001" in decisions and "状态：`APPROVED`" in decisions:
        return Gate("G9", "Founder Approval", "PASS", "PAOS-REL-001")
    return Gate("G9", "Founder Approval", "BLOCKED", "缺少 V1.1 Release Approval")


def promotion_gate() -> Gate:
    tags = run("git", "tag", "--list", "v1.1*")
    if tags.stdout.strip():
        return Gate("G10", "Promotion", "PASS", tags.stdout.strip().splitlines()[-1])
    return Gate("G10", "Promotion", "BLOCKED", "没有 V1.1 Release Tag")


def audit() -> list[Gate]:
    return [
        repository_gate(),
        inventory_gate(),
        command_gate("G2", "Schema", [PYTHON, "05_harness/validate_repository.py"]),
        command_gate("G3", "Boundary", [PYTHON, "05_harness/validate_repository.py"]),
        template_gate(),
        factory_gate(),
        command_gate("G6", "Adapters", [PYTHON, "05_harness/generate_adapters.py", "--check"]),
        deployment_gate(),
        recovery_gate(),
        approval_gate(),
        promotion_gate(),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-release-ready", action="store_true")
    args = parser.parse_args()
    gates = audit()
    overall = "PASS" if all(gate.status == "PASS" for gate in gates) else "BLOCKED"
    print(json.dumps({"overall": overall, "gates": [asdict(gate) for gate in gates]}, ensure_ascii=False, indent=2))
    if any(gate.status == "FAIL" for gate in gates):
        return 1
    if args.require_release_ready and overall != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
