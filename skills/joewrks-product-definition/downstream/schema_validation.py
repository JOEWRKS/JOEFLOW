"""Deterministic validation for the JSON Schema keyword subset used here."""

from __future__ import annotations

import re
from typing import Any


class SchemaValidationError(ValueError):
    """A schema definition or its instance is invalid for the supported subset."""


SUPPORTED_KEYWORDS = {
    "$schema",
    "$id",
    "title",
    "description",
    "$defs",
    "$ref",
    "type",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minItems",
    "minimum",
    "const",
    "enum",
    "pattern",
    "oneOf",
}


def _check_schema(schema: Any, path: str = "#") -> None:
    if not isinstance(schema, dict):
        raise SchemaValidationError(f"schema at {path} must be an object")
    unsupported = sorted(set(schema) - SUPPORTED_KEYWORDS)
    if unsupported:
        raise SchemaValidationError(f"unsupported schema keyword: {unsupported[0]}")
    definitions = schema.get("$defs", {})
    if not isinstance(definitions, dict):
        raise SchemaValidationError(f"$defs at {path} must be an object")
    for name, subschema in definitions.items():
        _check_schema(subschema, f"{path}/$defs/{name}")
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        raise SchemaValidationError(f"properties at {path} must be an object")
    for name, subschema in properties.items():
        _check_schema(subschema, f"{path}/properties/{name}")
    items = schema.get("items")
    if items is not None:
        _check_schema(items, f"{path}/items")
    additional = schema.get("additionalProperties")
    if isinstance(additional, dict):
        _check_schema(additional, f"{path}/additionalProperties")
    alternatives = schema.get("oneOf", [])
    if not isinstance(alternatives, list):
        raise SchemaValidationError(f"oneOf at {path} must be an array")
    for index, subschema in enumerate(alternatives):
        _check_schema(subschema, f"{path}/oneOf/{index}")


def _resolve_local_ref(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not isinstance(reference, str) or not reference.startswith("#/"):
        raise SchemaValidationError(f"only local schema references are supported: {reference!r}")
    value: Any = root
    for raw_token in reference[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value:
            raise SchemaValidationError(f"schema reference does not resolve: {reference}")
        value = value[token]
    if not isinstance(value, dict):
        raise SchemaValidationError(f"schema reference is not an object: {reference}")
    return value


def _matches_type(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "null":
        return instance is None
    raise SchemaValidationError(f"unsupported schema type: {expected}")


def _child_path(path: str, token: str | int) -> str:
    encoded = str(token).replace("~", "~0").replace("/", "~1")
    return f"{path}/{encoded}" if path else f"/{encoded}"


def _validate(instance: Any, schema: dict[str, Any], root: dict[str, Any], path: str) -> None:
    if "$ref" in schema:
        _validate(instance, _resolve_local_ref(root, schema["$ref"]), root, path)

    alternatives = schema.get("oneOf")
    if alternatives is not None:
        matches = 0
        for alternative in alternatives:
            try:
                _validate(instance, alternative, root, path)
            except SchemaValidationError:
                continue
            matches += 1
        if matches != 1:
            raise SchemaValidationError(f"{path or '/'} must match exactly one oneOf branch")

    if "const" in schema and instance != schema["const"]:
        raise SchemaValidationError(f"{path or '/'} does not match const")
    if "enum" in schema:
        enum = schema["enum"]
        if not isinstance(enum, list) or instance not in enum:
            raise SchemaValidationError(f"{path or '/'} is not in enum")

    expected_type = schema.get("type")
    if expected_type is not None:
        if not isinstance(expected_type, str):
            raise SchemaValidationError("schema type must be a string")
        if not _matches_type(instance, expected_type):
            raise SchemaValidationError(f"{path or '/'} must be {expected_type}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        if not isinstance(required, list) or not all(isinstance(key, str) for key in required):
            raise SchemaValidationError("schema required must be an array of strings")
        for key in required:
            if key not in instance:
                raise SchemaValidationError(f"{_child_path(path, key)} is required")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                _validate(value, properties[key], root, _child_path(path, key))
                continue
            additional = schema.get("additionalProperties", True)
            if additional is False:
                raise SchemaValidationError(f"{_child_path(path, key)} is not allowed")
            if isinstance(additional, dict):
                _validate(value, additional, root, _child_path(path, key))

    if isinstance(instance, list):
        minimum_items = schema.get("minItems")
        if minimum_items is not None:
            if not isinstance(minimum_items, int) or isinstance(minimum_items, bool):
                raise SchemaValidationError("schema minItems must be an integer")
            if len(instance) < minimum_items:
                raise SchemaValidationError(f"{path or '/'} has fewer than {minimum_items} items")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, value in enumerate(instance):
                _validate(value, item_schema, root, _child_path(path, index))

    minimum = schema.get("minimum")
    if minimum is not None and isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance < minimum:
            raise SchemaValidationError(f"{path or '/'} is less than minimum {minimum}")

    pattern = schema.get("pattern")
    if pattern is not None and isinstance(instance, str):
        if not isinstance(pattern, str):
            raise SchemaValidationError("schema pattern must be a string")
        try:
            matched = re.search(pattern, instance)
        except re.error as error:
            raise SchemaValidationError(f"invalid schema pattern: {pattern}") from error
        if matched is None:
            raise SchemaValidationError(f"{path or '/'} does not match pattern")


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    *,
    root_schema: dict[str, Any] | None = None,
) -> None:
    """Validate an instance against the repository-supported schema subset."""

    root = schema if root_schema is None else root_schema
    _check_schema(root)
    _validate(instance, schema, root, path="")
