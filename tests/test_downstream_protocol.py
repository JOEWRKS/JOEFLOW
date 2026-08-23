import json
import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.protocol import (
    PROTOCOL_VERSION,
    ProtocolError,
    decode_typed_numbers,
    dumps_record,
    encode_typed_numbers,
    loads_record,
    validate_execution_record,
)


def record():
    return {
        "protocol_version": PROTOCOL_VERSION,
        "record_kind": "execution_evidence",
        "sequence_id": "SEQ-B031",
        "test_id": "B031",
        "product_slug": "expense-reimbursement-dogfood",
        "authority": {"approved_revision": 55, "approved_digest": "digest"},
        "contract_hash": "a" * 64,
        "adapter": {"name": "frozen-b-vitest", "version": "1.0.0"},
        "frozen_source": {"commit": "b" * 40, "tree": "c" * 40},
        "command": {"type": "UPDATE_DRAFT", "input": {"krwAmount": {"$number": "NaN"}}},
        "before": {
            "authoritative_state": {},
            "revision": 1,
            "history": [],
            "business_side_effects": [],
            "delivery_effects": [],
        },
        "result": {"status": "committed", "code": "UPDATED"},
        "after": {
            "authoritative_state": {},
            "revision": 2,
            "history": [],
            "business_side_effects": [],
            "delivery_effects": [],
        },
        "deltas": {"history": [], "business_side_effects": [], "delivery_effects": []},
    }


class TypedNumberProtocolTest(unittest.TestCase):
    def test_non_finite_numbers_round_trip_losslessly(self):
        value = {"nan": math.nan, "positive": math.inf, "negative": -math.inf, "nested": [1.5, math.nan]}
        encoded = encode_typed_numbers(value)
        serialized = json.dumps(encoded, allow_nan=False, sort_keys=True)
        self.assertIn('"$number": "NaN"', serialized)
        self.assertIn('"$number": "+Infinity"', serialized)
        decoded = decode_typed_numbers(json.loads(serialized))
        self.assertTrue(math.isnan(decoded["nan"]))
        self.assertEqual(math.inf, decoded["positive"])
        self.assertEqual(-math.inf, decoded["negative"])
        self.assertTrue(math.isnan(decoded["nested"][1]))

    def test_malformed_or_unknown_typed_number_is_rejected(self):
        invalid = [
            {"$number": "NaN", "extra": True},
            {"$number": "Infinity"},
            {"$number": 1},
        ]
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ProtocolError):
                    decode_typed_numbers(value)

    def test_execution_record_is_versioned_complete_jsonl(self):
        value = record()
        validate_execution_record(value)
        line = dumps_record(value)
        self.assertTrue(line.endswith("\n"))
        self.assertNotIn("NaN", line.replace('"$number":"NaN"', ""))
        self.assertEqual(value, loads_record(line))

    def test_missing_identity_or_wrong_protocol_is_rejected(self):
        for mutation in ("protocol", "contract", "before_component"):
            value = record()
            if mutation == "protocol":
                value["protocol_version"] = "legacy"
            elif mutation == "contract":
                del value["contract_hash"]
            else:
                del value["before"]["delivery_effects"]
            with self.subTest(mutation=mutation):
                with self.assertRaises(ProtocolError):
                    validate_execution_record(value)


if __name__ == "__main__":
    unittest.main()
