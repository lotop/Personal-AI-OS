#!/usr/bin/env python3
"""Tree Digest 确定性与变化检测。"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tree_digest import calculate, calculate_commit


class TreeDigestTest(unittest.TestCase):
    def test_deterministic_and_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "b.txt").write_text("B\n", encoding="utf-8")
            (root / "a.txt").write_text("A\n", encoding="utf-8")
            subprocess.run(["git", "add", "a.txt", "b.txt"], cwd=root, check=True)
            first, records = calculate(root)
            second, _ = calculate(root)
            self.assertEqual(first, second)
            self.assertEqual([item["path"] for item in records], ["a.txt", "b.txt"])
            (root / "a.txt").write_text("changed\n", encoding="utf-8")
            changed, _ = calculate(root)
            self.assertNotEqual(first, changed)

    def test_digest_detects_executable_mode(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            script = root / "run.sh"
            script.write_text("#!/bin/sh\n", encoding="utf-8")
            subprocess.run(["git", "add", "run.sh"], cwd=root, check=True)
            regular, _ = calculate(root)
            script.chmod(0o755)
            subprocess.run(["git", "add", "run.sh"], cwd=root, check=True)
            executable, records = calculate(root)
            self.assertNotEqual(regular, executable)
            self.assertEqual(records[0]["mode"], "100755")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unsupported")
    def test_digest_distinguishes_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            target = root / "target.txt"
            link = root / "item"
            target.write_text("payload\n", encoding="utf-8")
            link.write_text("target.txt", encoding="utf-8")
            subprocess.run(["git", "add", "target.txt", "item"], cwd=root, check=True)
            regular, _ = calculate(root)
            link.unlink()
            os.symlink("target.txt", link)
            subprocess.run(["git", "add", "item"], cwd=root, check=True)
            symlink, records = calculate(root)
            self.assertNotEqual(regular, symlink)
            self.assertEqual({item["path"]: item["object_kind"] for item in records}["item"], "symlink")

    def test_working_and_commit_use_same_v02_algorithm(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "PAOS Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "paos@example.invalid"], cwd=root, check=True)
            (root / "a.txt").write_text("A\n", encoding="utf-8")
            subprocess.run(["git", "add", "a.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "test"], cwd=root, check=True, capture_output=True)
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            self.assertEqual(calculate(root)[0], calculate_commit(root, commit)[0])


if __name__ == "__main__":
    unittest.main()
