#!/usr/bin/env python3
"""无第三方依赖的 JSON Schema 最小子集验证。"""

from __future__ import annotations

import re
from typing import Any


TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
}


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        python_type = TYPE_MAP.get(expected)
        if python_type is None:
            return [f"{path}: 不支持的 Schema type {expected}"]
        if expected in {"integer", "number"} and isinstance(instance, bool):
            errors.append(f"{path}: 预期 {expected}，实际 boolean")
            return errors
        if not isinstance(instance, python_type):
            errors.append(f"{path}: 预期 {expected}，实际 {type(instance).__name__}")
            return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: 值不在 enum 中")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: 字符串长度不足")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: 不匹配 pattern {schema['pattern']}")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: 数组项目不足")
        if schema.get("uniqueItems"):
            normalized = [repr(item) for item in instance]
            if len(normalized) != len(set(normalized)):
                errors.append(f"{path}: 数组项目不唯一")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: 缺少必填字段 {key}")
        properties = schema.get("properties", {})
        for key, child_schema in properties.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], child_schema, f"{path}.{key}"))

    return errors
