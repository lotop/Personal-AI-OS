#!/usr/bin/env python3
"""Personal AI OS V1.1 Minimum Release Readiness；不执行 Promotion。"""

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
    except ModuleNotFoundError:
        try:
            import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]
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
        return Gate("M1", "Repository", "FAIL", "Git HEAD 不存在")
    if status.stdout.strip():
        return Gate("M1", "Repository", "BLOCKED", "Working Tree 非干净")
    return Gate("M1", "Repository", "PASS", head.stdout.strip())


def validation_gate() -> Gate:
    result = run(PYTHON, "05_harness/validate_repository.py")
    output = (result.stdout + result.stderr).strip().splitlines()
    return Gate("M2", "Validation", "PASS" if result.returncode == 0 else "FAIL", output[-1] if output else "validator produced no output")


def template_factory_gate() -> Gate:
    approved = []
    for manifest in (ROOT / "01_templates").glob("*/template.toml"):
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        if data.get("artifact_state") == "APPROVED" and data.get("approval_reference"):
            approved.append(manifest)
    acceptance = ROOT / "07_working/reviews/PROJECT_FACTORY_ACCEPTANCE.md"
    if not approved:
        return Gate("M3", "Template & Factory", "BLOCKED", "没有 Approved Template Pack")
    if not acceptance.is_file() or "结论：`PASS`" not in acceptance.read_text(encoding="utf-8"):
        return Gate("M3", "Template & Factory", "BLOCKED", "缺少 Formal Factory E2E")
    return Gate("M3", "Template & Factory", "PASS", f"approved_packs={len(approved)}")


def adapter_deployment_gate() -> Gate:
    generated = run(PYTHON, "05_harness/generate_adapters.py", "--check")
    if generated.returncode != 0:
        return Gate("M4", "Adapter & Deployment", "FAIL", "Adapter generation drift")
    data = tomllib.loads((ROOT / "02_registry/runtimes.toml").read_text(encoding="utf-8"))
    records = {item["platform"]: item for item in data.get("runtimes", [])}
    codex = records.get("codex", {})
    gemini = records.get("gemini-cli", {})
    if codex.get("runtime_smoke") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Codex Runtime Smoke 尚未 PASS")
    if gemini.get("config_load") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Gemini Conditional Config Load 尚未 PASS")
    return Gate("M4", "Adapter & Deployment", "PASS", "Codex PASS; Gemini CONDITIONAL config PASS")


def recovery_gate() -> Gate:
    path = ROOT / "07_working/reviews/RECOVERY_DRILL.md"
    if not path.is_file() or "结论：`PASS`" not in path.read_text(encoding="utf-8"):
        return Gate("M5", "Recovery", "BLOCKED", "缺少 Recovery evidence")
    text = path.read_text(encoding="utf-8")
    marker = "> Source Commit：`"
    source = text.split(marker, 1)[1].split("`", 1)[0] if marker in text else ""
    head = run("git", "rev-parse", "HEAD").stdout.strip()
    is_ancestor = run("git", "merge-base", "--is-ancestor", source, "HEAD").returncode == 0 if source else False
    if source != head and not is_ancestor:
        return Gate("M5", "Recovery", "STALE", f"evidence_commit={source or 'missing'} current={head}")
    return Gate("M5", "Recovery", "PASS", str(path.relative_to(ROOT)))


def approval_gate() -> Gate:
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    if "PAOS-REL-001" in decisions:
        return Gate("M6", "Founder Release Approval", "PASS", "PAOS-REL-001")
    return Gate("M6", "Founder Release Approval", "BLOCKED", "缺少固定 Commit 的 Release Approval")


def audit() -> list[Gate]:
    return [repository_gate(), validation_gate(), template_factory_gate(), adapter_deployment_gate(), recovery_gate(), approval_gate()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-release-ready", action="store_true")
    args = parser.parse_args()
    gates = audit()
    overall = "PASS" if all(gate.status == "PASS" for gate in gates) else "BLOCKED"
    print(json.dumps({"overall": overall, "gates": [asdict(gate) for gate in gates]}, ensure_ascii=False, indent=2))
    if any(gate.status == "FAIL" for gate in gates):
        return 10
    if args.require_release_ready and overall != "PASS":
        return 14
    return 0


if __name__ == "__main__":
    sys.exit(main())
