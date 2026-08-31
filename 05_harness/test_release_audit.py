#!/usr/bin/env python3
"""V1.1 Minimum Release Audit 结构测试。"""

from __future__ import annotations

import sys
import subprocess
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
    recovery_gate,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 兼容
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]

_AUDIT_CACHE: list | None = None


def cached_audit() -> list:
    """audit() 会 fork 完整验证链；同一次测试运行内只跑一次。"""
    global _AUDIT_CACHE
    if _AUDIT_CACHE is None:
        _AUDIT_CACHE = audit()
    return _AUDIT_CACHE


class ReleaseAuditTest(unittest.TestCase):
    def test_exactly_six_minimum_gates(self) -> None:
        self.assertEqual([gate.id for gate in cached_audit()], ["M1", "M2", "M3", "M4", "M5", "M6"])

    def test_ids_are_unique(self) -> None:
        ids = [gate.id for gate in cached_audit()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_promotion_gate(self) -> None:
        names = " ".join(gate.name.lower() for gate in cached_audit())
        self.assertNotIn("promotion", names)

    def test_gemini_is_conditional(self) -> None:
        gate = {item.id: item for item in cached_audit()}["M4"]
        if gate.status == "PASS":
            self.assertIn("CONDITIONAL", gate.evidence)

    def test_runtime_registry_does_not_overclaim(self) -> None:
        """直接断言 Registry 事实，不依赖工作区是否干净等门禁前置条件。"""
        data = tomllib.loads((ROOT / "02_registry/runtimes.toml").read_text(encoding="utf-8"))
        records = {item["platform"]: item for item in data["runtimes"]}
        self.assertEqual(records["claude-code"]["config_load"], "PASS")
        self.assertEqual(records["claude-code"]["runtime_smoke"], "NOT_RUN")
        self.assertEqual(records["gemini-cli"]["config_load"], "PASS")
        self.assertEqual(records["gemini-cli"]["runtime_smoke"], "NOT_RUN")
        self.assertEqual(records["codex"]["runtime_smoke"], "PASS")

    def test_recovery_followup_accepts_evidence_and_ledger_only(self) -> None:
        self.assertTrue(is_recovery_followup("07_working/reviews/RECOVERY_DRILL.md"))
        self.assertTrue(is_recovery_followup("07_working/reviews/recovery_evidence.toml"))
        self.assertTrue(is_recovery_followup("02_registry/tasks.toml"))
        self.assertFalse(is_recovery_followup("05_harness/release_audit.py"))
        self.assertFalse(is_recovery_followup("SYSTEM.toml"))
        self.assertFalse(is_recovery_followup("07_working/reviews/nested/deep.md"))

    def init_repo(self, root: Path) -> str:
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "PAOS Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "paos-test@example.invalid"], cwd=root, check=True)
        (root / "payload.txt").write_text("verified\n", encoding="utf-8")
        subprocess.run(["git", "add", "payload.txt"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "verified payload"], cwd=root, check=True, capture_output=True)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

    def write_recovery_evidence(self, root: Path, commit: str) -> None:
        review = root / "07_working/reviews"
        review.mkdir(parents=True)
        digest = commit_tree_digest(root, commit)
        (review / "recovery_evidence.toml").write_text(
            'schema_version = "0.1.0-working"\nstatus = "PASS"\n'
            f'tested_commit = "{commit}"\nrecovered_commit = "{commit}"\n'
            f'bundle_head = "{commit}"\nbundle_sha256 = "{"a" * 64}"\n'
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
            subprocess.run(["git", "add", "implementation.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "implementation changed"], cwd=root, check=True, capture_output=True)
            gate = recovery_gate(root)
            self.assertEqual(gate.status, "STALE")
            self.assertIn("implementation.py", gate.evidence)

    def tag_release(self, root: Path) -> str:
        """提交 Release Approval 并打 annotated tag，返回 tag 指向的 Commit。"""
        (root / "DECISIONS.md").write_text(
            "### PAOS-REL-002｜Personal AI OS V1.1.1 正式发布批准\n\n- 状态：`APPROVED`\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "DECISIONS.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "release approval"], cwd=root, check=True, capture_output=True)
        subprocess.run(
            ["git", "tag", "-a", "v1.1.1", "-m", "PAOS-REL-002 Release Personal AI OS V1.1.1"],
            cwd=root,
            check=True,
        )
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

    def write_system(self, root: Path, release_commit: str | None) -> None:
        baseline = ""
        if release_commit is not None:
            baseline = (
                "\n[approved_baseline]\n"
                'version = "1.1.1"\n'
                'git_tag = "v1.1.1"\n'
                'approval_reference = "PAOS-REL-002"\n'
                f'release_commit = "{release_commit}"\n'
            )
        (root / "SYSTEM.toml").write_text('target_version = "1.1.1"\n' + baseline, encoding="utf-8")

    def test_approval_accepts_matching_baseline_commit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            commit = self.tag_release(root)
            self.write_system(root, commit)
            self.assertEqual(approval_gate(root).status, "PASS")

    def test_approval_rejects_baseline_commit_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            self.tag_release(root)
            self.write_system(root, "0" * 40)
            gate = approval_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("release_commit", gate.evidence)

    def test_approval_rejects_baseline_tag_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            commit = self.tag_release(root)
            self.write_system(root, commit)
            (root / "SYSTEM.toml").write_text(
                (root / "SYSTEM.toml").read_text(encoding="utf-8").replace('"v1.1.1"', '"v1.1.0"'),
                encoding="utf-8",
            )
            gate = approval_gate(root)
            self.assertEqual(gate.status, "FAIL")
            self.assertIn("git_tag", gate.evidence)

    def test_approval_requires_annotated_tag_on_head(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.init_repo(root)
            (root / "SYSTEM.toml").write_text('target_version = "1.1.1"\n', encoding="utf-8")
            (root / "DECISIONS.md").write_text(
                "### PAOS-REL-002｜Personal AI OS V1.1.1 正式发布批准\n\n- 状态：`APPROVED`\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "SYSTEM.toml", "DECISIONS.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "release approval"], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "tag", "-a", "v1.1.1", "-m", "PAOS-REL-002 Release Personal AI OS V1.1.1"],
                cwd=root,
                check=True,
            )
            self.assertEqual(approval_gate(root).status, "PASS")


if __name__ == "__main__":
    unittest.main()
