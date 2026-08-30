#!/usr/bin/env python3
"""Schema 子集验证器测试。"""

from __future__ import annotations

import sys
import unittest
import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        import pip._vendor.tomli as tomllib  # type: ignore[no-redef,import-not-found]

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

    def test_reject_unknown_property_when_closed(self) -> None:
        schema = {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "additionalProperties": False,
        }
        self.assertEqual(validate_instance({"id": "demo"}, schema), [])
        errors = validate_instance({"id": "demo", "typo": True}, schema)
        self.assertTrue(any("未知字段 typo" in error for error in errors))

    def test_all_registry_files_have_schema_bindings(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema_root = root / "00_system/schemas"
        bindings = tomllib.loads((schema_root / "bindings.toml").read_text(encoding="utf-8"))[
            "bindings"
        ]
        bound_paths = {item.get("path") for item in bindings}
        registry_paths = {str(path.relative_to(root)) for path in (root / "02_registry").glob("*.toml")}
        self.assertEqual(registry_paths, bound_paths & registry_paths)

        for binding in bindings:
            path = binding.get("path")
            if not path or not path.startswith("02_registry/"):
                continue
            schema = json.loads((schema_root / binding["schema"]).read_text(encoding="utf-8"))
            instance = tomllib.loads((root / path).read_text(encoding="utf-8"))
            self.assertEqual(validate_instance(instance, schema), [], path)


if __name__ == "__main__":
    unittest.main()
