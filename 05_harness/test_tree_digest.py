#!/usr/bin/env python3
"""Tree Digest 确定性与变化检测。"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tree_digest import calculate


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


if __name__ == "__main__":
    unittest.main()
