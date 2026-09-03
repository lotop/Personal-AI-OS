#!/usr/bin/env python3
"""Personal AI OS V1.1 Minimum Release Readiness；不执行 Promotion。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from ci_gate import run_base_checks
from tree_digest import calculate_commit

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
RECOVERY_ARTIFACT_ROOT = Path("06_deployment/recovery_artifacts")
RELEASE_GATE_CONFIG = Path("05_harness/release_gates.toml")
EXPECTED_GATES = [
    ("M1", "Repository"),
    ("M2", "Validation"),
    ("M3", "Template & Factory"),
    ("M4", "Adapter & Deployment"),
    ("M5", "Recovery"),
    ("M6", "Founder Release Approval"),
]

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


GIT_ENV = {
    **os.environ,
    "HOME": "/dev/null",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "XDG_CONFIG_HOME": "/dev/null",
}


def run(root: Path, *args: str, text: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    sub_env = env if env is not None else (GIT_ENV if args and args[0] == "git" else None)
    return subprocess.run(args, cwd=root, text=text, capture_output=True, check=False, env=sub_env)


def load_gate_contract(root: Path = ROOT) -> list[tuple[str, str]]:
    path = root / RELEASE_GATE_CONFIG
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"Release Gate Config 无法解析: {exc}") from exc
    required = {
        "schema_version": "0.4.0",
        "artifact_class": "CONFIG",
        "maturity_state": "APPROVED",
        "canonical_authority": "FOUNDER_APPROVED",
        "approval_reference": "PAOS-019",
        "readiness_script": "release_audit.py",
    }
    for key, expected in required.items():
        if data.get(key) != expected:
            raise ValueError(f"Release Gate Config {key} 漂移")
    if "promotion" in data:
        raise ValueError("Release Gate Config 不得把 Promotion 声明为 Gate")
    gates = data.get("gates")
    if not isinstance(gates, list):
        raise ValueError("Release Gate Config 缺少 gates")
    actual = [(item.get("id"), item.get("name")) for item in gates if isinstance(item, dict)]
    if actual != EXPECTED_GATES:
        raise ValueError("Release Gate Config 的顺序、ID 或名称漂移")
    return actual


def repository_gate(root: Path = ROOT) -> Gate:
    head = run(root, "git", "rev-parse", "HEAD")
    status = run(root, "git", "status", "--porcelain")
    if head.returncode != 0:
        return Gate("M1", "Repository", "FAIL", "Git HEAD 不存在")
    if status.stdout.strip():
        return Gate("M1", "Repository", "BLOCKED", "Working Tree 非干净")
    return Gate("M1", "Repository", "PASS", head.stdout.strip())


def validation_gate(root: Path = ROOT) -> Gate:
    checks = run_base_checks(root)
    evidence = "; ".join(f"{item['id']}={item['status']}" for item in checks)
    return Gate(
        "M2",
        "Validation",
        "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        evidence,
    )


def template_factory_gate(root: Path = ROOT) -> Gate:
    try:
        factory_config = tomllib.loads(
            (root / "04_project_factory/factory.toml").read_text(encoding="utf-8")
        )
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return Gate("M3", "Template & Factory", "FAIL", f"Factory Config 无法解析: {exc}")
    pack_kinds = factory_config.get("template_pack_kinds", {})
    approved_project_packs = []
    for manifest in (root / "01_templates").glob("*/template.toml"):
        try:
            data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            return Gate("M3", "Template & Factory", "FAIL", f"Template Pack 无法解析: {manifest}: {exc}")
        if (
            data.get("artifact_state") == "APPROVED"
            and data.get("approval_reference")
            and pack_kinds.get(data.get("pack_id")) == "PROJECT_SCAFFOLD"
        ):
            approved_project_packs.append(manifest.parent)
    if not approved_project_packs:
        return Gate("M3", "Template & Factory", "BLOCKED", "没有 Approved PROJECT_SCAFFOLD Template Pack")
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
                "SOFTWARE_DEVELOPMENT",
                "--apply",
                "--git",
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip().splitlines()
                return Gate(
                    "M3",
                    "Template & Factory",
                    "FAIL",
                    f"Approved Project Pack 无法实例化: {pack.name}: {detail[-1] if detail else 'unknown error'}",
                )
            init_path = target / ".paos-init.json"
            try:
                init = json.loads(init_path.read_text(encoding="utf-8"))
                pack_manifest = tomllib.loads((pack / "template.toml").read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                return Gate("M3", "Template & Factory", "FAIL", f"初始化 Manifest 无效: {pack.name}: {exc}")
            except tomllib.TOMLDecodeError as exc:
                return Gate("M3", "Template & Factory", "FAIL", f"Template Manifest 无效: {pack.name}: {exc}")
            expected_digest = factory_config.get("approved_template_pack_digests", {}).get(init.get("template_pack"))
            if (
                init.get("schema_version") != "0.3.0"
                or init.get("project_status") != "PROVISIONAL"
                or init.get("template_pack") != pack_manifest.get("pack_id")
                or init.get("template_approval_reference") != pack_manifest.get("approval_reference")
                or init.get("template_pack_digest") != expected_digest
            ):
                return Gate("M3", "Template & Factory", "FAIL", f"初始化 Manifest 证据不完整: {pack.name}")
            records = init.get("files", [])
            if not isinstance(records, list):
                return Gate("M3", "Template & Factory", "FAIL", f"初始化文件证据不是数组: {pack.name}")
            expected_paths = {item.get("destination") for item in pack_manifest.get("files", [])}
            actual_paths = {item.get("path") for item in records if isinstance(item, dict)}
            if len(records) != len(actual_paths) or actual_paths != expected_paths:
                return Gate("M3", "Template & Factory", "FAIL", f"初始化文件证据覆盖不完整: {pack.name}")
            for record in records:
                materialized = target / record.get("path", "")
                if not materialized.is_file() or hashlib.sha256(materialized.read_bytes()).hexdigest() != record.get("sha256"):
                    return Gate("M3", "Template & Factory", "FAIL", f"初始化文件 Hash 不一致: {pack.name}")
            branch = run(target, "git", "branch", "--show-current")
            if branch.returncode != 0 or branch.stdout.strip() != "main":
                return Gate("M3", "Template & Factory", "FAIL", f"初始化 Git 分支不是 main: {pack.name}")
    return Gate(
        "M3",
        "Template & Factory",
        "PASS",
        f"approved_project_packs={len(approved_project_packs)}; apply_git_e2e=PASS",
    )


def adapter_deployment_gate(root: Path = ROOT) -> Gate:
    generated = run(root, PYTHON, "05_harness/generate_adapters.py", "--check")
    if generated.returncode != 0:
        return Gate("M4", "Adapter & Deployment", "FAIL", "Adapter generation drift")

    required_platforms = {"codex", "claude-code", "antigravity-cli"}
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
    antigravity = records.get("antigravity-cli", {})
    if codex.get("runtime_smoke") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Codex Runtime Smoke 尚未 PASS")
    if claude.get("config_load") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Claude Code Config Load 尚未 PASS")
    if antigravity.get("config_load") != "PASS" or antigravity.get("runtime_smoke") != "PASS":
        return Gate("M4", "Adapter & Deployment", "BLOCKED", "Antigravity Config Load / Runtime Smoke 尚未 PASS")
    return Gate(
        "M4",
        "Adapter & Deployment",
        "PASS",
        "Codex runtime PASS; Claude Code config PASS; Antigravity runtime & config PASS",
    )


def commit_tree_digest(root: Path, commit: str) -> str:
    """兼容旧测试/证据的 V0.1 Commit Digest。"""
    return calculate_commit(root, commit, algorithm="0.1")[0]


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
    bundle_path_value = evidence.get("bundle_path", "")
    expected_tree = evidence.get("tree_sha256", "")
    if not all(
        isinstance(value, str)
        for value in (tested, recovered, bundle_head, bundle_sha, bundle_path_value, expected_tree)
    ):
        return Gate("M5", "Recovery", "FAIL", "恢复证据字段类型无效")
    if evidence.get("status") != "PASS":
        return Gate("M5", "Recovery", "BLOCKED", "恢复证据状态不是 PASS")
    if not re.fullmatch(r"[0-9a-f]{40}", tested) or tested != recovered or tested != bundle_head:
        return Gate("M5", "Recovery", "FAIL", "tested/recovered/bundle commit 未精确一致")
    if not re.fullmatch(r"[0-9a-f]{64}", bundle_sha) or not re.fullmatch(r"[0-9a-f]{64}", expected_tree):
        return Gate("M5", "Recovery", "FAIL", "Bundle 或 Tree SHA-256 格式无效")
    bundle_relative = Path(bundle_path_value)
    if (
        not bundle_path_value
        or bundle_relative.is_absolute()
        or ".." in bundle_relative.parts
        or bundle_relative.parts[:2] != RECOVERY_ARTIFACT_ROOT.parts
    ):
        return Gate("M5", "Recovery", "FAIL", "Bundle Artifact 路径不在受管目录")
    # Bundle 文件名必须内嵌 Tested Commit 前缀，否则重复演练会原地覆盖上一次的恢复物证。
    if tested[:8] not in bundle_relative.name:
        return Gate("M5", "Recovery", "FAIL", "Bundle Artifact 文件名未内嵌 Tested Commit 前缀")
    bundle_artifact = root / bundle_relative
    if not bundle_artifact.is_file() or bundle_artifact.is_symlink():
        return Gate("M5", "Recovery", "BLOCKED", "Bundle Artifact 缺失或为 symlink")
    actual_bundle_sha = hashlib.sha256(bundle_artifact.read_bytes()).hexdigest()
    if actual_bundle_sha != bundle_sha:
        return Gate("M5", "Recovery", "FAIL", "Bundle Artifact SHA-256 与 Evidence 不一致")
    verify = run(root, "git", "bundle", "verify", str(bundle_artifact))
    if verify.returncode != 0:
        return Gate("M5", "Recovery", "FAIL", "git bundle verify 失败")
    heads = run(root, "git", "bundle", "list-heads", str(bundle_artifact))
    if heads.returncode != 0 or not any(
        line.split(maxsplit=1)[0] == bundle_head
        for line in heads.stdout.splitlines()
        if line.strip()
    ):
        return Gate("M5", "Recovery", "FAIL", "Bundle Artifact 不包含 Evidence Head")
    tree_algorithm = evidence.get("tree_digest_version", "0.1")
    if not isinstance(tree_algorithm, str) or tree_algorithm not in {"0.1", "0.2"}:
        return Gate("M5", "Recovery", "FAIL", "未知 Tree Digest Version")
    try:
        actual_tree = calculate_commit(root, tested, algorithm=tree_algorithm)[0]
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
    try:
        system = tomllib.loads((root / "SYSTEM.toml").read_text(encoding="utf-8"))
        decisions = (root / "DECISIONS.md").read_text(encoding="utf-8")
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return Gate("M6", "Founder Release Approval", "FAIL", f"Release Approval 输入无法解析: {exc}")
    version = system.get("target_version", "")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", version):
        return Gate("M6", "Founder Release Approval", "FAIL", "target_version 格式无效")
    tag_name = f"v{version}"
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
    tag_message = tag_body.partition("\n\n")[2]
    if tag_commit != head:
        return Gate("M6", "Founder Release Approval", "BLOCKED", f"{tag_name} 未绑定当前 HEAD")
    if approval_ref not in tag_message:
        return Gate("M6", "Founder Release Approval", "FAIL", f"{tag_name} 缺少 {approval_ref}")
    if tag_name not in tag_message and not re.search(rf"(?<![0-9.])V?{re.escape(version)}(?![0-9.])", tag_message):
        return Gate("M6", "Founder Release Approval", "FAIL", f"{tag_name} message 缺少版本 {version}")
    baseline = system.get("approved_baseline", {})
    if baseline.get("version") != version:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.version 与 target_version 不一致")
    if baseline.get("git_tag") != tag_name:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.git_tag 与发布 Tag 不一致")
    if baseline.get("approval_reference") != approval_ref:
        return Gate("M6", "Founder Release Approval", "FAIL", "approved_baseline.approval_reference 与 Decision 不一致")
    return Gate("M6", "Founder Release Approval", "PASS", f"{approval_ref} tag={tag_name} commit={head}")


def audit(root: Path = ROOT) -> list[Gate]:
    try:
        contract = load_gate_contract(root)
    except ValueError as exc:
        return [Gate(gate_id, name, "FAIL", str(exc)) for gate_id, name in EXPECTED_GATES]
    gates = [
        repository_gate(root),
        validation_gate(root),
        template_factory_gate(root),
        adapter_deployment_gate(root),
        recovery_gate(root),
        approval_gate(root),
    ]
    if [(gate.id, gate.name) for gate in gates] != contract:
        return [Gate(gate_id, name, "FAIL", "Release Audit 实现与 Gate Config 漂移") for gate_id, name in contract]
    return gates


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
