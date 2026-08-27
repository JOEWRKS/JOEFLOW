"""Frozen golden-case scoring for semantic-review calibration."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
from typing import Any

from downstream.schema_validation import SchemaValidationError, validate_instance

from .hashing import canonical_json_bytes, manifest_hash, package_hash, sha256_bytes
from .output import OutputError, validate_review_output
from .package import EXPECTED_SCHEMA_IDENTITIES, REQUIRED_ROLES


class GoldenError(ValueError):
    """A deterministic golden-suite identity or answer failure."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


def _answer_items(answers: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    return answers["answers"] if isinstance(answers, dict) else answers


def _embedded_bytes(package: dict[str, Any], path: str) -> bytes:
    try:
        embedded = package["embedded_files"][path]
    except (KeyError, TypeError) as error:
        raise GoldenError("GOLDEN_PACKAGE_INVALID", f"missing embedded file: {path}") from error
    if set(embedded) != {"encoding", "text"} or embedded["encoding"] != "utf-8":
        raise GoldenError("GOLDEN_PACKAGE_INVALID", f"invalid encoding: {path}")
    try:
        return embedded["text"].encode("utf-8")
    except (AttributeError, UnicodeEncodeError) as error:
        raise GoldenError("GOLDEN_PACKAGE_INVALID", f"invalid text: {path}") from error


def _role_value(
    package: dict[str, Any], role_paths: dict[str, str], role: str
) -> Any:
    data = _embedded_bytes(package, role_paths[role])
    if role == "reviewer_brief":
        return data.decode("utf-8")
    try:
        return json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GoldenError("GOLDEN_PACKAGE_INVALID", f"invalid JSON role: {role}") from error


def verify_golden_packages(cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Verify all embedded package bytes and return output-validation packages."""

    frozen_ids = {f"G-{index:03d}" for index in range(1, 16)}
    case_ids = [case.get("case_id") for case in cases]
    if len(cases) != 15 or len(set(case_ids)) != 15 or set(case_ids) != frozen_ids:
        raise GoldenError("GOLDEN_IDENTITY_SET_MISMATCH")
    result: dict[str, dict[str, Any]] = {}
    for case in cases:
        case_id = case["case_id"]
        declared_case_hash = case.get("case_manifest_hash")
        unhashed_case = {
            key: value for key, value in case.items() if key != "case_manifest_hash"
        }
        if declared_case_hash != sha256_bytes(canonical_json_bytes(unhashed_case)):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"case hash: {case_id}")
        package = case.get("reviewer_package")
        if not isinstance(package, dict) or set(package) != {
            "schema_version",
            "manifest",
            "reviewer_input_package_hash",
            "embedded_files",
        }:
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"package shape: {case_id}")
        if package["schema_version"] != "joewrks.semantic-review-golden-package/1.0":
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"package version: {case_id}")
        manifest = package["manifest"]
        if (
            not isinstance(manifest, dict)
            or manifest.get("previous_reviewer_verdicts_present") is not False
            or manifest.get("reviewer_input_manifest_hash") != manifest_hash(manifest)
        ):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"manifest: {case_id}")
        schema_root = Path(__file__).resolve().parents[1] / "schemas"
        try:
            input_schema = json.loads(
                (schema_root / "semantic-review-input-manifest.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            validate_instance(manifest, input_schema)
        except (OSError, json.JSONDecodeError, SchemaValidationError) as error:
            raise GoldenError(
                "GOLDEN_PACKAGE_INVALID", f"manifest schema: {case_id}"
            ) from error
        files = manifest.get("files")
        if not isinstance(files, list):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"files: {case_id}")
        roles = [item.get("logical_role") for item in files if isinstance(item, dict)]
        paths = [item.get("path") for item in files if isinstance(item, dict)]
        if (
            len(roles) != len(files)
            or set(roles) != REQUIRED_ROLES
            or len(roles) != len(set(roles))
            or len(paths) != len(set(paths))
            or set(paths) != set(package["embedded_files"])
        ):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"role inventory: {case_id}")
        role_paths: dict[str, str] = {}
        role_hashes: dict[str, str] = {}
        for item in files:
            role = item["logical_role"]
            if item.get("schema_identity") != EXPECTED_SCHEMA_IDENTITIES[role]:
                raise GoldenError("GOLDEN_PACKAGE_INVALID", f"schema identity: {case_id}")
            data = _embedded_bytes(package, item["path"])
            observed_hash = sha256_bytes(data)
            if (observed_hash, len(data)) != (item.get("sha256"), item.get("bytes")):
                raise GoldenError("GOLDEN_PACKAGE_INVALID", f"file bytes: {case_id}")
            role_paths[role] = item["path"]
            role_hashes[role] = observed_hash
        if package["reviewer_input_package_hash"] != package_hash(
            manifest["reviewer_input_manifest_hash"], files
        ):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"package hash: {case_id}")

        contract = _role_value(package, role_paths, "action_contract")
        unhashed_contract = {
            key: value for key, value in contract.items() if key != "contract_hash"
        }
        if contract.get("contract_hash") != sha256_bytes(
            canonical_json_bytes(unhashed_contract)
        ):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"contract hash: {case_id}")
        try:
            action_schema = json.loads(
                (schema_root / "action-contract.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            lifecycle_schema = json.loads(
                (schema_root / "lifecycle-contract.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            validate_instance(contract, action_schema)
            for lifecycle in contract["lifecycles"]:
                validate_instance(
                    lifecycle,
                    lifecycle_schema["$defs"]["lifecycle"],
                    root_schema=lifecycle_schema,
                )
        except (OSError, KeyError, json.JSONDecodeError, SchemaValidationError) as error:
            raise GoldenError(
                "GOLDEN_PACKAGE_INVALID", f"contract schema: {case_id}"
            ) from error
        identity_inventory = _role_value(
            package, role_paths, "review_identity_inventory"
        )
        identity_records = identity_inventory.get("identities", [])
        expected_identities = [item.get("review_identity") for item in identity_records]
        if expected_identities != sorted(set(expected_identities)):
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"identity order: {case_id}")
        output_schema_bytes = _embedded_bytes(
            package, role_paths["review_output_schema"]
        )
        frozen_output_schema_path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "semantic-review-output.schema.json"
        )
        if output_schema_bytes != frozen_output_schema_path.read_bytes():
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"output schema: {case_id}")
        exclusion = _role_value(package, role_paths, "exclusion_manifest")
        if exclusion != {
            "previous_reviewer_verdicts_present": False,
            "hidden_answers_present": False,
            "implementation_outcomes_present": False,
            "unrelated_product_evidence_present": False,
        }:
            raise GoldenError("GOLDEN_PACKAGE_INVALID", f"exclusions: {case_id}")
        result[case_id] = {
            "reviewer_brief_hash": role_hashes["reviewer_brief"],
            "reviewer_input_manifest_hash": manifest[
                "reviewer_input_manifest_hash"
            ],
            "reviewer_input_package_hash": package["reviewer_input_package_hash"],
            "contract_hash": contract["contract_hash"],
            "responsibility_profile_hash": role_hashes["responsibility_profile"],
            "semantic_obligation_index_hash": role_hashes[
                "semantic_obligation_index"
            ],
            "review_identity_inventory_hash": role_hashes[
                "review_identity_inventory"
            ],
            "role_hashes": role_hashes,
            "expected_identities": expected_identities,
            "identity_inventory": {
                item["review_identity"]: item for item in identity_records
            },
            "semantic_obligation_index": _role_value(
                package, role_paths, "semantic_obligation_index"
            ),
            "review_output_schema": _role_value(
                package, role_paths, "review_output_schema"
            ),
        }
    return result


def evaluate_goldens(
    outputs: list[dict[str, Any]],
    answers: dict[str, Any] | list[dict[str, Any]],
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate package-bound finalized outputs, then score hidden answer pairs."""

    answer_items = _answer_items(answers)
    expected = {item["case_id"]: item for item in answer_items}
    output_by_id = {item.get("case_id"): item for item in outputs}
    frozen_ids = {f"G-{index:03d}" for index in range(1, 16)}
    if (
        len(answer_items) != 15
        or len(expected) != 15
        or set(expected) != frozen_ids
        or len(output_by_id) != len(outputs)
        or set(output_by_id) != set(expected)
    ):
        raise GoldenError("GOLDEN_IDENTITY_SET_MISMATCH")
    verified_packages = verify_golden_packages(cases)
    cases_by_id = {case["case_id"]: case for case in cases}
    observed: dict[str, dict[str, str]] = {}
    for case_id in sorted(frozen_ids):
        item = output_by_id[case_id]
        if set(item) != {
            "case_id",
            "case_manifest_hash",
            "run_envelope",
            "review_output",
        } or item["case_manifest_hash"] != cases_by_id[case_id]["case_manifest_hash"]:
            raise GoldenError("GOLDEN_OUTPUT_INVALID", f"binding: {case_id}")
        try:
            validate_review_output(
                verified_packages[case_id],
                item["run_envelope"],
                item["review_output"],
            )
        except (OutputError, KeyError, TypeError) as error:
            raise GoldenError("GOLDEN_OUTPUT_INVALID", f"{case_id}: {error}") from error
        output = item["review_output"]
        case = cases_by_id[case_id]
        if case["review_phase"] == "preflight":
            if len(output["preflight_errors"]) != 1 or output["records"]:
                raise GoldenError("GOLDEN_OUTPUT_INVALID", f"preflight: {case_id}")
            terminal = output["preflight_errors"][0]
        else:
            if output["preflight_errors"]:
                raise GoldenError("GOLDEN_OUTPUT_INVALID", f"identity: {case_id}")
            focus = case["focus_review_identity"]
            focus_records = [
                record for record in output["records"] if record["review_identity"] == focus
            ]
            if len(focus_records) != 1:
                raise GoldenError("GOLDEN_OUTPUT_INVALID", f"focus: {case_id}")
            terminal = focus_records[0]
        observed[case_id] = {
            "verdict": terminal["verdict"],
            "rationale_code": terminal["rationale_code"],
        }
    verdict_hits = sum(
        observed[key]["verdict"] == expected[key]["verdict"] for key in expected
    )
    rationale_hits = sum(
        observed[key]["rationale_code"] == expected[key]["rationale_code"]
        for key in expected
    )
    unexpected_rubric = sum(
        observed[case_id]["verdict"] == "RUBRIC_ERROR"
        and expected[case_id]["verdict"] != "RUBRIC_ERROR"
        for case_id in observed
    )
    unexpected_package = sum(
        observed[case_id]["verdict"] == "INPUT_PACKAGE_ERROR"
        and expected[case_id]["verdict"] != "INPUT_PACKAGE_ERROR"
        for case_id in observed
    )
    count = len(expected)
    return {
        "case_count": count,
        "verdict_hits": verdict_hits,
        "rationale_code_hits": rationale_hits,
        "verdict_accuracy": Fraction(verdict_hits, count),
        "rationale_code_accuracy": Fraction(rationale_hits, count),
        "unexpected_rubric_error_count": unexpected_rubric,
        "unexpected_input_package_error_count": unexpected_package,
    }
