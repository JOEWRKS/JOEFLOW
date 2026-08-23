import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.schema_validation import SchemaValidationError, validate_instance


class RepositorySchemaSubsetTest(unittest.TestCase):
    def test_supported_keyword_subset_validates_real_nested_behavior(self):
        schema = {
            "$defs": {
                "meta": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string", "pattern": "^[a-z]+$"}},
                    "additionalProperties": False,
                }
            },
            "type": "object",
            "required": ["version", "count", "tags", "choice", "meta"],
            "properties": {
                "version": {"const": "v1"},
                "count": {"type": "integer", "minimum": 1},
                "tags": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"enum": ["CURRENT", "SUPERSEDED"]},
                },
                "choice": {"oneOf": [{"type": "string"}, {"type": "boolean"}]},
                "meta": {"$ref": "#/$defs/meta"},
            },
            "additionalProperties": False,
        }
        valid = {
            "version": "v1",
            "count": 1,
            "tags": ["CURRENT"],
            "choice": True,
            "meta": {"name": "valid"},
        }
        validate_instance(valid, schema)
        invalid_instances = [
            {**valid, "version": "v2"},
            {**valid, "count": 0},
            {**valid, "tags": []},
            {**valid, "tags": ["UNKNOWN"]},
            {**valid, "choice": 3},
            {**valid, "meta": {"name": "UPPER"}},
            {**valid, "extra": True},
            {key: value for key, value in valid.items() if key != "meta"},
        ]
        for instance in invalid_instances:
            with self.subTest(instance=instance):
                with self.assertRaises(SchemaValidationError):
                    validate_instance(instance, schema)

    def test_unsupported_validation_keyword_is_rejected(self):
        with self.assertRaisesRegex(SchemaValidationError, "unsupported schema keyword: minLength"):
            validate_instance("", {"type": "string", "minLength": 1})


if __name__ == "__main__":
    unittest.main()
