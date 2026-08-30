#!/usr/bin/env python3
"""Release Audit V2 结构与门禁顺序测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_audit_v2 import audit


class ReleaseAuditV2Test(unittest.TestCase):
    def test_ids_are_unique_and_expected(self) -> None:
        gates = audit()
        ids = [gate.id for gate in gates]
        self.assertEqual(len(ids), len(set(ids)))
        for required in ("R5a", "R5b", "R6a", "R6b", "R6c", "R7b", "R7c", "R7d", "R12", "P1", "P2"):
            self.assertIn(required, ids)

    def test_promotion_is_not_readiness_gate(self) -> None:
        gates = {gate.id: gate for gate in audit()}
        self.assertEqual(gates["P1"].phase, "PROMOTION")
        self.assertFalse(gates["P1"].mandatory)
        self.assertEqual(gates["P2"].phase, "PROMOTION")
        self.assertFalse(gates["P2"].mandatory)

    def test_template_and_runtime_capabilities_are_split(self) -> None:
        gates = {gate.id: gate for gate in audit()}
        self.assertNotEqual(gates["R5a"].name, gates["R5b"].name)
        self.assertNotEqual(gates["R7c"].name, gates["R7d"].name)


if __name__ == "__main__":
    unittest.main()
