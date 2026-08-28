"""Materialize all run-01 reviewer inputs before any reviewer output exists."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
RUN_ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_ROOT = RUN_ROOT.parent
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.goldens import verify_golden_packages
from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes
from downstream.semantic_review.package import load_and_verify_package


INPUTS_ROOT = RUN_ROOT / "inputs"
INPUT_MANIFEST_PATH = RUN_ROOT / "INPUT_FREEZE_MANIFEST.json"
INVOCATION_PATH = RUN_ROOT / "REVIEWER_INVOCATION.txt"
COHORT_PROTOCOL_PATH = CALIBRATION_ROOT / "cohort-protocol-v1.json"
GOLDEN_CASES_PATH = ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-cases.json"
FULL_PACKAGE_ROOT = (
    CALIBRATION_ROOT
    / "semantic-review-calibration-v1"
    / "reviewer-package"
)
BRIEF_HASH = "3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c"
FULL_PACKAGE_HASH = "ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603"
ATTESTATION = {
    "fresh_context": True,
    "previous_verdict_access": False,
    "manifest_only_evidence": True,
}
FORBIDDEN_FILENAMES = {
    "golden-answers.json",
    "golden-review-outputs.json",
    "human-adjudication-manifest.json",
    "official_calibration_controller.py",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_new(path: Path, data: bytes) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite frozen input: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _file_inventory(root: Path) -> list[dict[str, Any]]:
    inventory = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        data = path.read_bytes()
        inventory.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
        )
    return inventory


def _bundle_hash(root: Path) -> str:
    return sha256_bytes(canonical_json_bytes(_file_inventory(root)))


def _copy_full_package(destination: Path) -> dict[str, Any]:
    for source in sorted(item for item in FULL_PACKAGE_ROOT.rglob("*") if item.is_file()):
        relative = source.relative_to(FULL_PACKAGE_ROOT)
        _write_new(destination / relative, source.read_bytes())
    verified = load_and_verify_package(destination)
    if verified["reviewer_input_package_hash"] != FULL_PACKAGE_HASH:
        raise RuntimeError("full reviewer package hash drift")
    if verified["reviewer_brief_hash"] != BRIEF_HASH:
        raise RuntimeError("full reviewer brief hash drift")
    return verified


def _write_golden_package(
    case: dict[str, Any], destination: Path, expected_verified: dict[str, Any]
) -> dict[str, Any]:
    package = case["reviewer_package"]
    for relative, embedded in sorted(package["embedded_files"].items()):
        if embedded.get("encoding") != "utf-8" or set(embedded) != {"encoding", "text"}:
            raise RuntimeError(f"invalid embedded golden file: {case['case_id']}:{relative}")
        _write_new(destination / relative, embedded["text"].encode("utf-8"))
    _write_new(destination / "manifest.json", canonical_json_bytes(package["manifest"]))
    for relative, embedded in package["embedded_files"].items():
        if (destination / relative).read_bytes() != embedded["text"].encode("utf-8"):
            raise RuntimeError(f"golden byte drift: {case['case_id']}:{relative}")
    if (destination / "manifest.json").read_bytes() != canonical_json_bytes(
        package["manifest"]
    ):
        raise RuntimeError(f"golden manifest byte drift: {case['case_id']}")
    if expected_verified["reviewer_input_package_hash"] != package["reviewer_input_package_hash"]:
        raise RuntimeError(f"golden package hash drift: {case['case_id']}")
    if expected_verified["reviewer_brief_hash"] != BRIEF_HASH:
        raise RuntimeError(f"golden brief hash drift: {case['case_id']}")
    return expected_verified


def _envelope(
    *, context_id: str, package_hash: str, include_attestation_hash: bool
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "review_run_id": f"V043-RUN-01-{context_id}",
        "reviewer_context_id": context_id,
        "reviewer_input_package_hash": package_hash,
        "reviewer_brief_hash": BRIEF_HASH,
        "isolation_attestation": dict(ATTESTATION),
    }
    if include_attestation_hash:
        value["isolation_attestation_hash"] = sha256_bytes(
            canonical_json_bytes(ATTESTATION)
        )
    return value


def _materialize_context(
    *,
    cohort_id: str,
    context_id: str,
    kind: str,
    case: dict[str, Any] | None,
    expected_golden_package: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle_root = INPUTS_ROOT / context_id
    package_root = bundle_root / "package"
    if bundle_root.exists():
        raise RuntimeError(f"input context already exists: {context_id}")
    if kind == "full":
        verified = _copy_full_package(package_root)
        case_id = None
        schema_path = "package/semantic-review-output.schema.json"
    else:
        if case is None:
            raise RuntimeError(f"missing golden case: {context_id}")
        if expected_golden_package is None:
            raise RuntimeError(f"missing verified golden package: {context_id}")
        verified = _write_golden_package(
            case, package_root, expected_golden_package
        )
        case_id = case["case_id"]
        schema_path = "package/review-output.schema.json"
    envelope = _envelope(
        context_id=context_id,
        package_hash=verified["reviewer_input_package_hash"],
        include_attestation_hash=kind == "golden",
    )
    envelope_bytes = canonical_json_bytes(envelope) + b"\n"
    _write_new(bundle_root / "run-envelope.json", envelope_bytes)
    return {
        "cohort_id": cohort_id,
        "kind": kind,
        "case_id": case_id,
        "planned_context_id": context_id,
        "review_run_id": envelope["review_run_id"],
        "reviewer_input_package_hash": verified["reviewer_input_package_hash"],
        "reviewer_brief_hash": verified["reviewer_brief_hash"],
        "run_envelope_sha256": hashlib.sha256(envelope_bytes).hexdigest(),
        "input_bundle_sha256": _bundle_hash(bundle_root),
        "input_file_count": len(_file_inventory(bundle_root)),
        "output_schema_path": schema_path,
        "reviewer_outputs": "ABSENT",
    }


def main() -> int:
    if INPUTS_ROOT.exists() or INPUT_MANIFEST_PATH.exists():
        raise RuntimeError("run-01 inputs are already materialized")
    protocol = _load_json(COHORT_PROTOCOL_PATH)
    cases = _load_json(GOLDEN_CASES_PATH)
    if protocol.get("cohort_ids") != ["C1", "C2", "C3"]:
        raise RuntimeError("cohort protocol drift")
    if protocol.get("REAL_CALIBRATION_RUNS") != 0:
        raise RuntimeError("real calibration already executed")
    if protocol.get("executed_output_paths") != []:
        raise RuntimeError("reviewer outputs already present")
    if not isinstance(cases, list) or len(cases) != 15:
        raise RuntimeError("golden case set drift")
    verified_golden_packages = verify_golden_packages(cases)
    cases_by_id = {case["case_id"]: case for case in cases}
    if set(cases_by_id) != {f"G-{index:03d}" for index in range(1, 16)}:
        raise RuntimeError("golden case IDs drift")
    invocation_bytes = INVOCATION_PATH.read_bytes()
    if not invocation_bytes.endswith(b"\n"):
        raise RuntimeError("invocation wrapper must end with LF")

    contexts: list[dict[str, Any]] = []
    for cohort in protocol["cohorts"]:
        cohort_id = cohort["cohort_id"]
        full_id = cohort["full_review_context"]["planned_context_id"]
        contexts.append(
            _materialize_context(
                cohort_id=cohort_id,
                context_id=full_id,
                kind="full",
                case=None,
            )
        )
        for planned in cohort["golden_contexts"]:
            case_id = planned["case_id"]
            contexts.append(
                _materialize_context(
                    cohort_id=cohort_id,
                    context_id=planned["planned_context_id"],
                    kind="golden",
                    case=cases_by_id[case_id],
                    expected_golden_package=verified_golden_packages[case_id],
                )
            )

    ids = [item["planned_context_id"] for item in contexts]
    if len(contexts) != 48 or len(set(ids)) != 48:
        raise RuntimeError("context population mismatch")
    if sum(item["kind"] == "full" for item in contexts) != 3:
        raise RuntimeError("full context count mismatch")
    if sum(item["kind"] == "golden" for item in contexts) != 45:
        raise RuntimeError("golden context count mismatch")
    for path in INPUTS_ROOT.rglob("*"):
        if path.is_file() and path.name.lower() in FORBIDDEN_FILENAMES:
            raise RuntimeError(f"forbidden reviewer input file: {path}")

    manifest = {
        "schema_version": "joewrks.semantic-review-input-freeze/1.0",
        "run_id": "v0.4.3-semantic-review-calibration-run-01",
        "calibration_input_commit": "96b2b6e7c5435ccdbab5f7371073ec34c2d04078",
        "pre_run_lock_commit": "f08eb78428b6f43ef76c2eed94f10be56f46cf9a",
        "invocation_wrapper_sha256": hashlib.sha256(invocation_bytes).hexdigest(),
        "invocation_wrapper_bytes": len(invocation_bytes),
        "execution_parameters": {
            "mechanism": "codex-cli exec",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "high",
            "sandbox": "read-only",
            "ephemeral": True,
            "ignore_user_config": True,
            "ignore_project_rules": True,
            "repository_check": "SKIPPED_PROJECTLESS_CONTEXT",
            "no_retry": True,
            "max_concurrency": 3,
        },
        "planned_context_count": 48,
        "full_context_count": 3,
        "golden_context_count": 45,
        "all_inputs_frozen_before_first_output": True,
        "reviewer_outputs": "ABSENT",
        "contexts": contexts,
    }
    _write_new(INPUT_MANIFEST_PATH, canonical_json_bytes(manifest) + b"\n")
    print(f"MATERIALIZED_CONTEXTS={len(contexts)}")
    print(f"INVOCATION_WRAPPER_SHA256={manifest['invocation_wrapper_sha256']}")
    print(f"INPUT_MANIFEST_SHA256={hashlib.sha256(INPUT_MANIFEST_PATH.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
