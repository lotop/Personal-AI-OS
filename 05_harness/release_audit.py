#!/usr/bin/env python3
"""Personal AI OS V1.1 Minimum Release Readiness；不执行 Promotion。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
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
RECOVERY_EVIDENCE = Path("07_working/reviews/recovery_evidence.toml")

# 恢复演练之后只允许已声明的证据与任务账本类文件继续变化；实现文件变化必须重新演练。
RECOVERY_FOLLOWUP_PATHS = {
    "02_registry/tasks.toml",
    "07_working/reviews/recovery_evidence.toml",
    "07_working/reviews/RECOVERY_DRILL.md",
    "07_working/reviews/RELEASE_READINESS.md",
}
RECOVERY_FOLLOWUP_PATTERNS = (
    re.compile(r"^07_working/reviews/[A-Z0-9][A-Z0-9_.-]*_TASK\.md$"),
    re.compile(r"^07_working/reviews/HANDOFF[A-Z0-9_.-]*\.md$"),
)


def is_recovery_followup(path: str) -> bool:
    """判断恢复演练后的变更是否属于允许的证据/账本更新。"""
    if path in RECOVERY_FOLLOWUP_PATHS:
        return True
    return any(pattern.fullmatch(path) for pattern in RECOVERY_FOLLOWUP_PATTERNS)


@dataclass(frozen=True)
class Gate:
    id: str
    name: str
    status: str
    evidence: str


def run(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=root, text=text, capture_output=True, check=False)


def repository_gate(root: Path = ROOT) -> Gate:
    head = run(root, "git", "rev-parse", "HEAD")
    status = run(root, "git", "status", "--porcelain")
    if head.returncode != 0:
        return Gate("M1", "Repository", "FAIL", "Git HEAD 不存在")
    if status.stdout.strip():
        return Gate("M1", "Repository", "BLOCKED", "Working Tree 非干净")
    return Gate("M1", "Repository", "PASS", head.stdout.strip())


def validation_gate(root: Path = ROOT) -> Gate:
    result = run(root, PYTHON, "05_harness/validate_repository.py")
    output = (result.stdout + result.stderr).strip().splitlines()
    return Gate("M2", "Validation", "PASS" if result.returncode == 0 else "FAIL", output[-1] if output else "validator produced no output")


def template_factory_gate(root: Path = ROOT) -> Gate:
    approved_project_packs = []
    for manifest in (root / "01_templates").glob("*/template.toml"):
        try:
            data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            return Gate("M3", "Template & Factory", "FAIL", f"Template Pack 无法解析: {manifest}: {exc}")
        if (
            data.get("artifact_state") == "APPROVED"
            and data.get("approval_reference")
            and data.get("pack_kind") == "PROJECT_SCAFFOLD"
        ):
            approved_project_packs.append(manifest.parent)
    acceptance = root / "07_working/reviews/PROJECT_FACTORY_ACCEPTANCE.md"
    if not approved_project_packs:
        return Gate("M3", "Template & Factory", "BLOCKED", "没有 Approved PROJECT_SCAFFOLD Template Pack")
    if not acceptance.is_file() or "结论：`PASS`" not in acceptance.read_text(encoding="utf-8"):
        return Gate("M3", "Template & Factory", "BLOCKED", "缺少 Formal Factory E2E")
    with tempfile.TemporaryDirectory(prefix="paos-m3-") as raw:
        for pack in approved_project_packs:
            target = Path(raw) / pack.name
            result = run(
                root,
                PYTHON,
                "04_project_factory/create_project.py",
                "--template-pack",
                str(pack),
                "--target",
                str(target),
                "--project-id",
                f"m3-{pack.name}",
                "--name",
                "M3 Factory Validation",
                "--owner",
                "paos-release-audit",
                "--primary-type",
                "SOFTWARE_PRODUCT",
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip().splitlines()
                return Gate(
                    "M3",
                    "Template & Factory",
                    "FAIL",
                    f"Approved Project Pack 无法实例化: {pack.name}: {detail[-1] if detail else 'unknown error'}",
                )
    return Gate(
        "M3",
        "Template & Factory",
        "PASS",
        f"approved_project_packs={len(approved_project_packs)}; dry_run=PASS",
    )


def adapter_deployment_gate(root: Path = ROOT) -> Gate:
    generated = run(root, PYTHON, "05_harness/generate_adapters.py", "--check")
    if generated.returncode != 0:
        return Gate("M4", "Adapter & Deployment", "FAIL", "Adapter generation drift")

    required_platforms = {"codex", "claude-code", "gemini-cli"}
    manifests: dict[str, dict] = {}
    for manifest_path in sorted((root / "03_adapters").glob("*/manifest.toml")):
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        manifests[manifest["platform"]] = manifest
        for record in manifest.get("files", []):
            source = manifest_path.parent / record["source"]
            target = root / record["target"]
            if not source.is_file() or not target.is_file() or source.read_bytes() != target.read_bytes():
                return Gate(
                    "M4",
                    "Adapter & Deployment",
                    "FAIL",
                    f"{manifest['platform']} Adapter 未部署或发生漂移: {record['target']}",
                )
    missing = sorted(required_platforms - manifests.keys())
    if missing:
        return Gate("M4", "Adapter & Deployment", "FAIL", "缺少 Adapter: " + ", ".join(missing))

    data = tomllib.loads((root / "02_registry/runtimes.toml").read_text(encoding="utf-8"))
    records = {item["platform"]: item for item in data.get("runtimes", [])}
    codex = records.get("codex", {})
    claude = records.get("claude-code", {})
    gemini = records.get("gemini-cli", {})
    if codex.get("runtime_smoke") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Codex Runtime Smoke 尚未 PASS")
    if claude.get("config_load") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Claude Code Config Load 尚未 PASS")
    if gemini.get("config_load") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Gemini Conditional Config Load 尚未 PASS")
    return Gate(
        "M4",
        "Adapter & Deployment",
        "PASS",
        "Codex runtime PASS; Claude Code config PASS; Gemini CONDITIONAL config PASS",
    )


def commit_tree_digest(root: Path, commit: str) -> str:
    listing = run(root, "git", "ls-tree", "-rz", "--full-tree", commit, text=False)
    if listing.returncode != 0:
        raise ValueError("无法读取 evidence commit tree")
    records: list[tuple[str, str]] = []
    for raw in listing.stdout.split(b"\0"):
        if not raw:
            continue
        metadata, path_raw = raw.split(b"\t", 1)
        _mode, kind, object_id = metadata.decode("ascii").split()
        if kind != "blob":
            raise ValueError(f"不支持的 Git tree object: {kind}")
        blob = run(root, "git", "cat-file", "blob", object_id, text=False)
        if blob.returncode != 0:
            raise ValueError("无法读取 evidence commit blob")
        records.append((path_raw.decode("utf-8"), hashlib.sha256(blob.stdout).hexdigest()))
    digest = hashlib.sha256()
    for path, file_hash in sorted(records):
        digest.update(path.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\n")
    return digest.hexdigest()


def recovery_gate(root: Path = ROOT) -> Gate:
    evidence_path = root / RECOVERY_EVIDENCE
    report_path = root / "07_working/reviews/RECOVERY_DRILL.md"
    if not evidence_path.is_file() or not report_path.is_file():
        return Gate("M5", "Recovery", "BLOCKED", "缺少机器可读恢复证据或 Recovery Drill")
    try:
        evidence = tomllib.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return Gate("M5", "Recovery", "FAIL", f"恢复证据无法解析: {exc}")
    tested = evidence.get("tested_commit", "")
    recovered = evidence.get("recovered_commit", "")
    bundle_head = evidence.get("bundle_head", "")
    bundle_sha = evidence.get("bundle_sha256", "")
    expected_tree = evidence.get("tree_sha256", "")
    if evidence.get("status") != "PASS":
        return Gate("M5", "Recovery", "BLOCKED", "恢复证据状态不是 PASS")
    if not re.fullmatch(r"[0-9a-f]{40}", tested) or tested != recovered or tested != bundle_head:
        return Gate("M5", "Recovery", "FAIL", "tested/recovered/bundle commit 未精确一致")
    if not re.fullmatch(r"[0-9a-f]{64}", bundle_sha) or not re.fullmatch(r"[0-9a-f]{64}", expected_tree):
        return Gate("M5", "Recovery", "FAIL", "Bundle 或 Tree SHA-256 格式无效")
    try:
        actual_tree = commit_tree_digest(root, tested)
    except ValueError as exc:
        return Gate("M5", "Recovery", "FAIL", str(exc))
    if actual_tree != expected_tree:
        return Gate("M5", "Recovery", "FAIL", "Evidence tree digest 与 Git commit 不一致")
    report = report_path.read_text(encoding="utf-8")
    if f"Source Commit：`{tested}`" not in report or "结论：`PASS`" not in report:
        return Gate("M5", "Recovery", "FAIL", "Recovery Drill 与机器证据不一致")
    head = run(root, "git", "rev-parse", "HEAD").stdout.strip()
    if tested != head:
        if run(root, "git", "merge-base", "--is-ancestor", tested, head).returncode != 0:
            return Gate("M5", "Recovery", "STALE", f"evidence={tested} current={head}")
        changed = set(run(root, "git", "diff", "--name-only", f"{tested}..{head}").stdout.splitlines())
        unexpected = sorted(path for path in changed if not is_recovery_followup(path))
        if unexpected:
            return Gate("M5", "Recovery", "STALE", "恢复后仍有实现变更: " + ", ".join(unexpected))
    return Gate("M5", "Recovery", "PASS", f"commit={tested} bundle_sha256={bundle_sha}")


def approval_gate(root: Path = ROOT) -> Gate:
    system = tomllib.loads((root / "SYSTEM.toml").read_text(encoding="utf-8"))
    version = system.get("target_version", "")
    tag_name = f"v{version}"
    decisions = (root / "DECISIONS.md").read_text(encoding="utf-8")
    match = re.search(
        rf"### (PAOS-REL-[0-9]+)[^\n]*{re.escape(version)}[^\n]*\n\n- 状态：`APPROVED`",
        decisions,
    )
    if not match:
        return Gate("M6", "Founder Release Approval", "BLOCKED", f"缺少 V{version} Founder Approval")
    approval_ref = match.group(1)
    object_type = run(root, "git", "cat-file", "-t", f"refs/tags/{tag_name}")
    if object_type.returncode != 0 or object_type.stdout.strip() != "tag":
        return Gate("M6", "Founder Release Approval", "BLOCKED", f"缺少 annotated tag {tag_name}")
    tag_commit = run(root, "git", "rev-parse", f"{tag_name}^{{}}").stdout.strip()
    head = run(root, "git", "rev-parse", "HEAD").stdout.strip()
    tag_body = run(root, "git", "cat-file", "-p", f"refs/tags/{tag_name}").stdout
    if tag_commit != head:
        return Gate("M6", "Founder Release Approval", "BLOCKED", f"{tag_name} 未绑定当前 HEAD")
    if approval_ref not in tag_body:
        return Gate("M6", "Founder Release Approval", "FAIL", f"{tag_name} 缺少 {approval_ref}")
    baseline = system.get("approved_baseline", {})
    if baseline.get("version") != version:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.version 与 target_version 不一致")
    if baseline.get("git_tag") != tag_name:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.git_tag 与发布 Tag 不一致")
    if baseline.get("approval_reference") != approval_ref:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.approval_reference 与 Decision 不一致")
    if baseline.get("release_commit") != tag_commit:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.release_commit 与 Tag 指向的 Commit 不一致")
    return Gate("M6", "Founder Release Approval", "PASS", f"{approval_ref} tag={tag_name} commit={head}")


def audit(root: Path = ROOT) -> list[Gate]:
    return [
        repository_gate(root),
        validation_gate(root),
        template_factory_gate(root),
        adapter_deployment_gate(root),
        recovery_gate(root),
        approval_gate(root),
    ]


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
