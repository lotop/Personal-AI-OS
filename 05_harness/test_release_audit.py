#!/usr/bin/env python3
"""V1.1 Minimum Release Audit 结构测试。"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_audit import (
    ROOT,
    approval_gate,
    audit,
    commit_tree_digest,
    is_recovery_followup,
    load_gate_contract,
    recovery_gate,
    template_factory_gate,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 兼容
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]

_AUDIT_CACHE: list | None = None

GIT_ENV = {
    **os.environ,
    "HOME": "/dev/null",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "XDG_CONFIG_HOME": "/dev/null",
}


def git(*args: str, cwd: Path, **kwargs) -> subprocess.CompletedProcess:
    env = kwargs.pop("env", GIT_ENV)
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True, **kwargs)


def cached_audit() -> list:
    """audit() 会 fork 完整验证链；同一次测试运行内只跑一次。"""
    global _AUDIT_CACHE
    if _AUDIT_CACHE is None:
        _AUDIT_CACHE = audit()
    return _AUDIT_CACHE


class ReleaseAuditTest(unittest.TestCase):
    def test_exactly_six_minimum_gates(self) -> None:
        self.assertEqual([gate.id for gate in cached_audit()], ["M1", "M2", "M3", "M4", "M5", "M6"])

    def test_gate_config_is_real_contract(self) -> None:
        self.assertEqual(load_gate_contract(), [(gate.id, gate.name) for gate in cached_audit()])

    def test_gate_config_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            config = root / "05_harness/release_gates.toml"
            config.parent.mkdir(parents=True)
            config.write_text('schema_version = "0.4.0"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "漂移"):
                load_gate_contract(root)

    def test_ids_are_unique(self) -> None:
        ids = [gate.id for gate in cached_audit()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_promotion_gate(self) -> None:
        names = " ".join(gate.name.lower() for gate in cached_audit())
        self.assertNotIn("promotion", names)

    def test_antigravity_status(self) -> None:
        gate = {item.id: item for item in cached_audit()}["M4"]
        if gate.status == "PASS":
            self.assertIn("Antigravity", gate.evidence)

    def test_m2_evidence_lists_base_check_ids(self) -> None:
        evidence = {item.id: item.evidence for item in cached_audit()}["M2"]
        for check_id in ("repository", "factory", "schema", "deployment", "tree-digest", "temp-cleanup", "adapters"):
            self.assertIn(f"{check_id}=", evidence)

    def test_runtime_registry_does_not_overclaim(self) -> None:
        """任何 PASS 都必须带证据字段；不把具体平台状态钉死成字面量。"""
        data = tomllib.loads((ROOT / "02_registry/runtimes.toml").read_text(encoding="utf-8"))
        records = {item["platform"]: item for item in data["runtimes"]}
        for platform in ("codex", "claude-code", "antigravity-cli"):
            self.assertIn(platform, records)
        for platform, record in records.items():
            if record.get("config_load") == "PASS":
                self.assertTrue(
                    record.get("config_evidence", "").strip(),
                    f"{platform} config_load=PASS 但缺少 config_evidence",
                )
            if record.get("runtime_smoke") == "PASS":
                self.assertTrue(
                    record.get("smoke_evidence", "").strip(),
                    f"{platform} runtime_smoke=PASS 但缺少 smoke_evidence",
                )
            if record.get("runtime_smoke") == "BLOCKED":
                self.assertTrue(
                    record.get("blocked_reasons"),
                    f"{platform} runtime_smoke=BLOCKED 但缺少 blocked_reasons",
                )

    def test_recovery_followup_accepts_evidence_and_ledger_only(self) -> None:
        self.assertTrue(is_recovery_followup("07_working/reviews/RECOVERY_DRILL.md"))
        self.assertTrue(is_recovery_followup("07_working/reviews/recovery_evidence.toml"))
        self.assertTrue(is_recovery_followup("02_registry/tasks.toml"))
        self.assertTrue(is_recovery_followup("07_working/reviews/FULL_AUDIT_REMEDIATION_TASK.md"))
        self.assertTrue(is_recovery_followup("07_working/reviews/HANDOFF_V1.1.2.md"))
        self.assertFalse(is_recovery_followup("05_harness/release_audit.py"))
        self.assertFalse(is_recovery_followup("SYSTEM.toml"))
        self.assertFalse(is_recovery_followup("07_working/reviews/nested/deep.md"))
        self.assertFalse(is_recovery_followup("07_working/reviews/UNRELATED.md"))
        self.assertFalse(is_recovery_followup("07_working/reviews/payload.py"))

    def test_factory_gate_checks_apply_git(self) -> None:
        gate = template_factory_gate()
        self.assertIn(gate.status, {"PASS", "FAIL"})
        self.assertIn("apply_git_e2e=", gate.evidence)

    def test_template_gate_counts_only_instantiable_project_packs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            templates = root / "01_templates"
            factory = root / "04_project_factory"
            templates.mkdir()
            factory.mkdir()
            (templates / "project-pack").mkdir()
            (templates / "project-pack/template.toml").write_text(
                'pack_id = "project-pack"\n'
                'artifact_state = "APPROVED"\n'
                'approval_reference = "APPROVED-1"\n'
                '[[files]]\nsource = "a.txt"\ndestination = "a.txt"\n',
                encoding="utf-8",
            )
            (templates / "artifact-pack").mkdir()
            (templates / "artifact-pack/template.toml").write_text(
                'pack_id = "artifact-pack"\n'
                'artifact_state = "APPROVED"\n'
                'approval_reference = "APPROVED-2"\n'
                '[[files]]\nsource = "a.txt"\ndestination = "a.txt"\n',
                encoding="utf-8",
            )
            (factory / "create_project.py").write_text(
                "import argparse,json,subprocess,os,hashlib\n"
                "from pathlib import Path\n"
                "p=argparse.ArgumentParser()\n"
                "p.add_argument('--template-pack');p.add_argument('--target');p.add_argument('--project-id')\n"
                "p.add_argument('--name');p.add_argument('--owner');p.add_argument('--primary-type')\n"
                "p.add_argument('--apply',action='store_true');p.add_argument('--git',action='store_true')\n"
                "a=p.parse_args(); t=Path(a.target); t.mkdir(parents=True, exist_ok=True)\n"
                "(t/'a.txt').write_text('')\n"
                "m={'schema_version':'0.2.0','project_status':'PROVISIONAL','template_pack':'project-pack',"
                "'template_approval_reference':'APPROVED-1','template_pack_digest':'digest',"
                "'files':[{'path':'a.txt','sha256':hashlib.sha256(b'').hexdigest()}]}\n"
                "(t/'.paos-init.json').write_text(json.dumps(m))\n"
                "env={**os.environ,'HOME':'/dev/null','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_NOSYSTEM':'1','XDG_CONFIG_HOME':'/dev/null'}\n"
                "subprocess.run(['git','init','-b','main'],cwd=t,check=True,capture_output=True,env=env)\n"
                "print(json.dumps(m))\n",
                encoding="utf-8",
            )
            (factory / "factory.toml").write_text(
                '[template_pack_kinds]\nproject-pack = "PROJECT_SCAFFOLD"\n'
                'artifact-pack = "ARTIFACT_LIBRARY"\n'
                '[approved_template_pack_digests]\nproject-pack = "digest"\n',
                encoding="utf-8",
            )
            gate = template_factory_gate(root)
            self.assertEqual(gate.status, "PASS")
            self.assertIn("approved_project_packs=1", gate.evidence)
            self.assertIn("apply_git_e2e=PASS", gate.evidence)

    def init_repo(self, root: Path) -> str:
        git("init", "-b", "main", cwd=root, capture_output=True)
        git("config", "user.name", "PAOS Test", cwd=root)
        git("config", "user.email", "paos-test@example.invalid", cwd=root)
        (root / "payload.txt").write_text("verified\n", encoding="utf-8")
        git("add", "payload.txt", cwd=root)
        git("commit", "-m", "verified payload", cwd=root, capture_output=True)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, env=GIT_ENV, text=True).strip()

    def write_recovery_evidence(self, root: Path, commit: str) -> None:
        review = root / "07_working/reviews"
        review.mkdir(parents=True)
        artifact_root = root / "06_deployment/recovery_artifacts"
        artifact_root.mkdir(parents=True)
        bundle_name = f"test-{commit[:8]}.bundle"
        bundle = artifact_root / bundle_name
        git("bundle", "create", str(bundle), "main", cwd=root, capture_output=True)
        bundle_sha = hashlib.sha256(bundle.read_bytes()).hexdigest()
        digest = commit_tree_digest(root, commit)
        (review / "recovery_evidence.toml").write_text(
            'schema_version = "0.1.0-working"\nstatus = "PASS"\n'
            f'tested_commit = "{commit}"\nrecovered_commit = "{commit}"\n'
            f'bundle_head = "{commit}"\nbundle_sha256 = "{bundle_sha}"\n'
            f'bundle_path = "06_deployment/recovery_artifacts/{bundle_name}"\n'
            f'tree_sha256 = "{digest}"\nexecuted_at = "2026-08-31"\n',
            encoding="utf-8",
        )
        (review / "RECOVERY_DRILL.md").write_text(
            f"> Source Commit：`{commit}`\n\n结论：`PASS`\n",
            encoding="utf-8",
        )

    def test_recovery_requires_consistent_machine_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            commit = self.init_repo(root)
            self.write_recovery_evidence(root, commit)
            self.assertEqual(recovery_gate(root).status, "PASS")

    def test_recovery_rejects_implementation_changes_after_tested_commit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            commit = self.init_repo(root)
            self.write_recovery_evidence(root, commit)
            (root / "implementation.py").write_text("changed = True\n", encoding="utf-8")
            git("add", "implementation.py", cwd=root)
            git("commit", "-m", "implementation changed", cwd=root, capture_output=True)
            gate = recovery_gate(root)
            self.assertEqual(gate.status, "STALE")
            self.assertIn("implementation.py", gate.evidence)

    def test_recovery_rejects_tampered_bundle_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            commit = self.init_repo(root)
            self.write_recovery_evidence(root, commit)
            bundle = root / f"06_deployment/recovery_artifacts/test-{commit[:8]}.bundle"
            bundle.write_bytes(bundle.read_bytes() + b"tampered")
            gate = recovery_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("SHA-256", gate.evidence)

    def test_recovery_rejects_bundle_name_without_commit_prefix(self) -> None:
        """Bundle 文件名不内嵌 Tested Commit 时，重复演练会原地覆盖上一次物证。"""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            commit = self.init_repo(root)
            self.write_recovery_evidence(root, commit)
            artifact_root = root / "06_deployment/recovery_artifacts"
            (artifact_root / f"test-{commit[:8]}.bundle").rename(artifact_root / "release.bundle")
            evidence = root / "07_working/reviews/recovery_evidence.toml"
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    f"test-{commit[:8]}.bundle", "release.bundle"
                ),
                encoding="utf-8",
            )
            gate = recovery_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("Tested Commit 前缀", gate.evidence)

    def tag_release(self, root: Path) -> str:
        """提交 Release Approval 并打 annotated tag，返回 tag 指向的 Commit。"""
        (root / "DECISIONS.md").write_text(
            "### PAOS-REL-002｜Personal AI OS V1.1.1 正式发布批准\n\n- 状态：`APPROVED`\n",
            encoding="utf-8",
        )
        git("add", "DECISIONS.md", cwd=root)
        git("commit", "-m", "release approval", cwd=root, capture_output=True)
        git("tag", "-a", "v1.1.1", "-m", "PAOS-REL-002 Release Personal AI OS V1.1.1", cwd=root)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, env=GIT_ENV, text=True).strip()

    def write_system(self, root: Path, include_baseline: bool) -> None:
        baseline = ""
        if include_baseline:
            baseline = (
                "\n[approved_baseline]\n"
                'version = "1.1.1"\n'
                'git_tag = "v1.1.1"\n'
                'approval_reference = "PAOS-REL-002"\n'
            )
        (root / "SYSTEM.toml").write_text('target_version = "1.1.1"\n' + baseline, encoding="utf-8")

    def test_approval_accepts_tag_bound_release_without_commit_self_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            self.tag_release(root)
            self.write_system(root, True)
            self.assertEqual(approval_gate(root).status, "PASS")

    def test_approval_rejects_baseline_version_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            self.tag_release(root)
            self.write_system(root, True)
            (root / "SYSTEM.toml").write_text(
                (root / "SYSTEM.toml").read_text(encoding="utf-8").replace(
                    '\nversion = "1.1.1"', '\nversion = "1.1.0"'
                ),
                encoding="utf-8",
            )
            gate = approval_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("approved_baseline.version", gate.evidence)

    def test_approval_rejects_baseline_tag_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            self.tag_release(root)
            self.write_system(root, True)
            (root / "SYSTEM.toml").write_text(
                (root / "SYSTEM.toml").read_text(encoding="utf-8").replace('"v1.1.1"', '"v1.1.0"'),
                encoding="utf-8",
            )
            gate = approval_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("git_tag", gate.evidence)

    def test_approval_rejects_missing_approved_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            (root / "SYSTEM.toml").write_text('target_version = "1.1.1"\n', encoding="utf-8")
            (root / "DECISIONS.md").write_text(
                "### PAOS-REL-002｜Personal AI OS V1.1.1 正式发布批准\n\n- 状态：`APPROVED`\n",
                encoding="utf-8",
            )
            git("add", "SYSTEM.toml", "DECISIONS.md", cwd=root)
            git("commit", "-m", "release approval", cwd=root, capture_output=True)
            git("tag", "-a", "v1.1.1", "-m", "PAOS-REL-002 Release Personal AI OS V1.1.1", cwd=root)
            gate = approval_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("approved_baseline.version", gate.evidence)

    def test_approval_rejects_tag_message_without_version(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            (root / "DECISIONS.md").write_text(
                "### PAOS-REL-002｜Personal AI OS V1.1.1 正式发布批准\n\n- 状态：`APPROVED`\n",
                encoding="utf-8",
            )
            git("add", "DECISIONS.md", cwd=root)
            git("commit", "-m", "release", cwd=root, capture_output=True)
            git("tag", "-a", "v1.1.1", "-m", "PAOS-REL-002 release", cwd=root)
            self.write_system(root, True)
            gate = approval_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("缺少版本", gate.evidence)


if __name__ == "__main__":
    unittest.main()
