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

from schema_validation import unsupported_keywords, validate_instance


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

    def test_pattern_is_full_match(self) -> None:
        schema = {"type": "string", "pattern": "[a-z]+"}
        self.assertEqual(validate_instance("demo", schema), [])
        self.assertTrue(validate_instance("demo1", schema))

    def test_unsupported_keyword_is_rejected(self) -> None:
        self.assertTrue(unsupported_keywords({"type": "object", "oneOf": []}))
        self.assertTrue(unsupported_keywords({"type": "string", "maxLength": 3}))
        self.assertTrue(unsupported_keywords({"$ref": "paos://schemas/system/0.3"}))

    def test_unsupported_keyword_is_detected_in_subschema(self) -> None:
        schema = {
            "type": "object",
            "properties": {"items": {"type": "array", "items": {"format": "uuid"}}},
        }
        errors = unsupported_keywords(schema)
        self.assertTrue(any("format" in error for error in errors))

    def test_additional_properties_must_be_boolean(self) -> None:
        self.assertTrue(unsupported_keywords({"additionalProperties": {"type": "string"}}))
        self.assertEqual(unsupported_keywords({"additionalProperties": False}), [])

    def test_repository_schemas_stay_within_supported_subset(self) -> None:
        schema_root = Path(__file__).resolve().parents[1] / "00_system/schemas"
        for path in sorted(schema_root.glob("*.schema.json")):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(unsupported_keywords(schema), [], path.name)

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
