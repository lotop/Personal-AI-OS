#!/usr/bin/env python3
"""V1.1 Minimum Release Audit 结构测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_audit import audit


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


if __name__ == "__main__":
    unittest.main()
