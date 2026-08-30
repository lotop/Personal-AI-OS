#!/usr/bin/env python3
"""V1.1 Minimum Release Audit 结构测试。"""

from __future__ import annotations

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_audit import approval_gate, audit, commit_tree_digest, recovery_gate


class ReleaseAuditTest(unittest.TestCase):
    def test_exactly_six_minimum_gates(self) -> None:
        self.assertEqual([gate.id for gate in audit()], ["M1", "M2", "M3", "M4", "M5", "M6"])

    def test_ids_are_unique(self) -> None:
        ids = [gate.id for gate in audit()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_promotion_gate(self) -> None:
        names = " ".join(gate.name.lower() for gate in audit())
        self.assertNotIn("promotion", names)

    def test_gemini_is_conditional(self) -> None:
        gate = {item.id: item for item in audit()}["M4"]
        if gate.status == "PASS":
            self.assertIn("CONDITIONAL", gate.evidence)

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
