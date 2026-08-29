#!/usr/bin/env python3
"""Schema 子集验证器测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema_validation import validate_instance


class SchemaValidationTest(unittest.TestCase):
    def test_valid_object(self) -> None:
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string", "pattern": "^[a-z]+$"}},
        }
        self.assertEqual(validate_instance({"id": "demo"}, schema), [])

    def test_missing_required(self) -> None:
        errors = validate_instance({}, {"type": "object", "required": ["id"]})
        self.assertTrue(errors)

    def test_enum_and_unique_items(self) -> None:
        schema = {
            "type": "array",
            "items": {"type": "string", "enum": ["A", "B"]},
            "uniqueItems": True,
        }
        self.assertEqual(validate_instance(["A", "B"], schema), [])
        self.assertTrue(validate_instance(["A", "A"], schema))
