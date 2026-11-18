# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed structural validation for ASTON Agent Attestation 1.0.0.

Implements the JSON Schema keywords used by the published ASTON schema only.
It is not a general-purpose JSON Schema engine and does not verify signatures,
issuer identity, digests, external timestamps, runtime integrity, or claim truth.
"""
from __future__ import annotations
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "agent-attestation.schema.json"

class ValidationError(ValueError):
    """Raised when an attestation violates the supported ASTON schema."""

def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object": return isinstance(value, dict)
    if expected == "array": return isinstance(value, list)
    if expected == "string": return isinstance(value, str)
    if expected == "integer": return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number": return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean": return isinstance(value, bool)
    if expected == "null": return value is None
    return False

def _resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValidationError(f"Unsupported external schema reference: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise ValidationError(f"Unresolvable schema reference: {ref}")
        node = node[part]
    if not isinstance(node, dict):
        raise ValidationError(f"Schema reference is not an object: {ref}")
    return node

def _format_valid(value: str, fmt: str) -> bool:
    if fmt == "date-time":
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None and parsed.utcoffset() is not None
        except ValueError:
            return False
    if fmt == "uri":
        parsed = urlparse(value)
        return bool(parsed.scheme) and not any(ch.isspace() for ch in value)
    return True

def _validate(value: Any, rule: dict[str, Any], root: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if "$ref" in rule:
        return _validate(value, _resolve_ref(root, rule["$ref"]), root, path)
    expected = rule.get("type")
    if expected and not _type_matches(value, expected):
        return [f"{path}: expected {expected}"]
    if "const" in rule and value != rule["const"]:
        errors.append(f"{path}: value must equal {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path}: value is not an allowed value")
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0): errors.append(f"{path}: shorter than minLength")
        if len(value) > rule.get("maxLength", float("inf")): errors.append(f"{path}: exceeds maxLength")
        if "pattern" in rule and re.search(rule["pattern"], value) is None:
            errors.append(f"{path}: does not match required pattern")
        if "format" in rule and not _format_valid(value, rule["format"]):
            errors.append(f"{path}: invalid {rule['format']} format")
    if isinstance(value, dict):
        for key in rule.get("required", []):
            if key not in value: errors.append(f"{path}: missing required property {key!r}")
        properties = rule.get("properties", {})
        if rule.get("additionalProperties") is False:
            for key in value:
                if key not in properties: errors.append(f"{path}: unexpected property {key!r}")
        for key, child in properties.items():
            if key in value: errors.extend(_validate(value[key], child, root, f"{path}.{key}"))
        if isinstance(rule.get("additionalProperties"), dict):
            for key in value.keys() - properties.keys():
                errors.extend(_validate(value[key], rule["additionalProperties"], root, f"{path}.{key}"))
        if "anyOf" in rule and not any(not _validate(value, option, root, path) for option in rule["anyOf"]):
            errors.append(f"{path}: does not satisfy any allowed alternative")
    if isinstance(value, list) and "items" in rule:
        for index, item in enumerate(value):
            errors.extend(_validate(item, rule["items"], root, f"{path}[{index}]"))
    return errors

def validate_attestation(document: dict[str, Any], schema_path: str | Path | None = None) -> None:
    """Validate structure; raise ValidationError on failure, return None on success."""
    if not isinstance(document, dict):
        raise ValidationError("$: attestation must be a JSON object")
    path = Path(schema_path) if schema_path is not None else _SCHEMA_PATH
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Could not load attestation schema: {exc}") from exc
    errors = _validate(document, schema, schema, "$")
    if errors:
        raise ValidationError("Attestation validation failed:\n- " + "\n- ".join(errors))
