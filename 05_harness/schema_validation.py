#!/usr/bin/env python3
"""无第三方依赖的 JSON Schema 最小子集验证。"""

from __future__ import annotations

import json
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

# 本实现真正会执行的关键字；未列出的关键字必须显式报错，不得静默忽略。
SUPPORTED_KEYWORDS = {
    "type",
    "enum",
    "minLength",
    "pattern",
    "minItems",
    "uniqueItems",
    "items",
    "required",
    "properties",
    "additionalProperties",
}

# 只承载说明信息、不影响校验结果的关键字。
ANNOTATION_KEYWORDS = {"$schema", "$id", "title", "description"}


def unsupported_keywords(schema: Any, path: str = "$") -> list[str]:
    """递归检查 Schema 是否只使用本实现支持的关键字。"""
    errors: list[str] = []
    if not isinstance(schema, dict):
        return [f"{path}: Schema 必须是对象"]

    for keyword in schema:
        if keyword not in SUPPORTED_KEYWORDS and keyword not in ANNOTATION_KEYWORDS:
            errors.append(f"{path}: 未实现的 Schema 关键字 {keyword}")

    expected = schema.get("type")
    if expected is not None and (not isinstance(expected, str) or expected not in TYPE_MAP):
        errors.append(f"{path}: 不支持的 Schema type {expected}")

    if "enum" in schema and not isinstance(schema["enum"], list):
        errors.append(f"{path}: enum 必须是数组")
    for keyword in ("minLength", "minItems"):
        if keyword in schema and (
            not isinstance(schema[keyword], int)
            or isinstance(schema[keyword], bool)
            or schema[keyword] < 0
        ):
            errors.append(f"{path}: {keyword} 必须是非负整数")
    if "uniqueItems" in schema and not isinstance(schema["uniqueItems"], bool):
        errors.append(f"{path}: uniqueItems 必须是布尔值")
    if "required" in schema and (
        not isinstance(schema["required"], list)
        or any(not isinstance(item, str) for item in schema["required"])
    ):
        errors.append(f"{path}: required 必须是字符串数组")
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            errors.append(f"{path}: pattern 必须是字符串")
        else:
            try:
                re.compile(schema["pattern"])
            except re.error as exc:
                errors.append(f"{path}: pattern 正则无效: {exc}")

    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        errors.append(f"{path}: additionalProperties 只支持布尔值")

    if "items" in schema:
        if not isinstance(schema["items"], dict):
            errors.append(f"{path}.items: 必须是对象")
        else:
            errors.extend(unsupported_keywords(schema["items"], f"{path}.items"))

    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            errors.append(f"{path}.properties: 必须是对象")
        else:
            for key, child in properties.items():
                errors.extend(unsupported_keywords(child, f"{path}.properties.{key}"))

    return errors


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    shape_errors = unsupported_keywords(schema, path)
    if shape_errors:
        return shape_errors
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
        # JSON Schema Draft 2020-12 的 pattern 不隐式锚定；整串约束由 Schema 显式使用 ^...$。
        if "pattern" in schema:
            try:
                matched = re.search(schema["pattern"], instance)
            except (re.error, TypeError) as exc:
                errors.append(f"{path}: Schema pattern 无效: {exc}")
            else:
                if not matched:
                    errors.append(f"{path}: 不匹配 pattern {schema['pattern']}")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: 数组项目不足")
        if schema.get("uniqueItems"):
            try:
                normalized = [
                    json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    for item in instance
                ]
            except (TypeError, ValueError) as exc:
                errors.append(f"{path}: 无法规范化 uniqueItems: {exc}")
                normalized = []
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
        if schema.get("additionalProperties") is False:
            for key in instance.keys() - properties.keys():
                errors.append(f"{path}: 不允许未知字段 {key}")
        for key, child_schema in properties.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], child_schema, f"{path}.{key}"))

    return errors
