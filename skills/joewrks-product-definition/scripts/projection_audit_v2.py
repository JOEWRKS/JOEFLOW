from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from approval_v2 import compute_approval_manifest, definition_digest
from authority_binding_v2 import (
    BindingError,
    canonical_record_index,
    resolve_record_pointer,
)
from build_approval_manifest import _finish, _reject_constant


INPUT_SCHEMA = "joewrks.projection-audit-input/1.0"
OUTPUT_SCHEMA = "joewrks.projection-audit/1.0"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(value: object) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _resolve_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("path must be a nonempty string")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _load_json(path: Path) -> tuple[object, bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8"), parse_constant=_reject_constant), raw


def _decode_pointer(pointer: object) -> list[str]:
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise ValueError("invalid RFC 6901 pointer")
    if not pointer:
        return []
    tokens = []
    for raw in pointer[1:].split("/"):
        tokens.append(raw.replace("~1", "/").replace("~0", "~"))
    return tokens


def _resolve_pointer(value: object, pointer: object) -> object:
    current = value
    for token in _decode_pointer(pointer):
        if isinstance(current, dict):
            current = current[token]
        elif isinstance(current, list):
            current = current[int(token)]
        else:
            raise ValueError("pointer traverses a scalar")
    return current


def _load_ref(root: Path, ref: object) -> tuple[object, str, Path]:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256", "pointer"}:
        raise ValueError("reference must contain exactly path, sha256, pointer")
    path = _resolve_path(root, ref["path"])
    value, raw = _load_json(path)
    observed = _sha256_bytes(raw)
    if observed != ref["sha256"]:
        raise ValueError(f"reference hash mismatch: {path}")
    return _resolve_pointer(value, ref["pointer"]), observed, path


def _finding(code: str, cause: str, next_action: str, **extra: object) -> dict[str, object]:
    return {"code": code, "cause": cause, "next_action": next_action, **extra}


def _review_semantics(
    root: Path,
    projection: dict[str, Any],
    content: str | None,
    observed_sha: str | None,
    canonical_state: dict[str, Any],
    canonical_sha: str,
    required: bool,
    approved_coverage: list[str],
) -> tuple[dict[str, object], list[dict[str, object]], str | None]:
    if not required:
        return {"status": "NOT_REQUIRED", "findings": [], "coverage": approved_coverage}, [], None
    review = projection.get("review")
    findings: list[dict[str, object]] = []
    if not isinstance(review, dict):
        return {"status": "UNKNOWN", "findings": None, "coverage": []}, [
            _finding("semantic_review_missing", "semantic review metadata is absent", "PROVIDE_BOUND_REVIEW_EVIDENCE_FOR_THIS_PROJECTION")
        ], None
    scope = review.get("scope") if isinstance(review.get("scope"), list) else []
    if scope != approved_coverage:
        findings.append(_finding(
            "semantic_coverage_mismatch",
            "declared semantic review scope differs from the approved projection coverage",
            "REVIEW_THE_EXACT_APPROVED_PROJECTION_COVERAGE",
            required_coverage=approved_coverage,
            declared_coverage=scope,
        ))
    status = review.get("semantic_status")
    declared_findings = review.get("semantic_findings")
    if status == "NOT_REVIEWED":
        if declared_findings is not None:
            findings.append(_finding(
                "unreviewed_findings_must_be_null",
                "unreviewed semantics must use null rather than zero findings",
                "SET_FINDINGS_TO_NULL_OR_COMPLETE_A_BOUND_SEMANTIC_REVIEW",
            ))
        return {"status": "UNKNOWN", "findings": None, "coverage": scope}, findings, None

    evidence_sha: str | None = None
    evidence_loaded = False
    try:
        evidence, evidence_sha, _ = _load_ref(root, review.get("review_evidence"))
        evidence_loaded = True
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
        findings.append(_finding(
            "semantic_review_evidence_invalid", str(exc),
            "RECREATE_OR_REBIND_THE_REVIEW_EVIDENCE_TO_CURRENT_SOURCE_AND_PROJECTION",
        ))
        evidence = None
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer:
        findings.append(_finding("semantic_reviewer_missing", "reviewer identity is absent", "RECORD_THE_ACTUAL_REVIEWER_IN_BOUND_EVIDENCE"))
    if review.get("reviewed_projection_sha256") != observed_sha:
        findings.append(_finding("stale_projection_review", "reviewed projection hash differs from current bytes", "REVIEW_THE_CURRENT_PROJECTION_BYTES"))
    if review.get("reviewed_source_sha256") != canonical_sha:
        findings.append(_finding("stale_source_review", "reviewed source hash differs from current canonical bytes", "REVIEW_AGAINST_THE_CURRENT_CANONICAL_SOURCE"))
    if isinstance(evidence, dict):
        expected = {
            "reviewer": reviewer,
            "projection_sha256": observed_sha,
            "source_sha256": canonical_sha,
            "scope": scope,
            "coverage": approved_coverage,
            "verdict": status,
        }
        if evidence != expected:
            findings.append(_finding(
                "semantic_review_evidence_mismatch",
                "bound review evidence does not exactly match reviewer, source, projection, scope, coverage, and verdict",
                "CORRECT_THE_REVIEW_RECORD_OR_RERUN_THE_REVIEW",
            ))
    elif evidence_loaded:
        findings.append(_finding(
            "semantic_review_evidence_mismatch",
            "bound review evidence must be an object with the exact reviewer, source, projection, scope, coverage, and verdict",
            "CORRECT_THE_REVIEW_RECORD_OR_RERUN_THE_REVIEW",
        ))

    claims = projection.get("semantic_claims")
    if not isinstance(claims, list) or (required and approved_coverage and not claims):
        findings.append(_finding("semantic_claim_inventory_missing", "required semantic claim inventory is empty", "BIND_REVIEWED_PROJECTION_CLAIMS_TO_EXACT_CANONICAL_POINTERS"))
        claims = []
    try:
        index = canonical_record_index(canonical_state)
    except BindingError as exc:
        findings.append(_finding("canonical_authority_invalid", str(exc), "REPAIR_CANONICAL_AUTHORITY_BEFORE_PROJECTION_REVIEW"))
        index = {}
    for claim in claims:
        if not isinstance(claim, dict):
            findings.append(_finding("invalid_semantic_claim", "claim must be an object", "RECORD_AN_EXACT_CANONICAL_CLAIM_BINDING"))
            continue
        record_id, pointer, quote = claim.get("record_id"), claim.get("pointer"), claim.get("projection_quote")
        if record_id not in index:
            findings.append(_finding("unknown_projection_authority", f"unknown record {record_id}", "BIND_TO_AN_EXISTING_CURRENT_CANONICAL_RECORD", object_id=record_id))
            continue
        _, record = index[record_id]
        try:
            canonical_value = resolve_record_pointer(record, pointer)
        except (BindingError, TypeError) as exc:
            findings.append(_finding("invalid_projection_authority_pointer", str(exc), "USE_AN_EXACT_VALID_RECORD_RELATIVE_POINTER", object_id=record_id, pointer=pointer))
            continue
        if quote != canonical_value or content is None or not isinstance(quote, str) or quote not in content:
            findings.append(_finding(
                "projection_claim_missing",
                "current projection bytes do not contain the exact reviewed canonical value",
                "UPDATE_THIS_PROJECTION_FROM_THE_NAMED_CANONICAL_POINTER_THEN_RERUN_ITS_REVIEW",
                object_id=record_id,
                pointer=pointer,
            ))

    effective = "PASS" if status == "PASS" and not findings and declared_findings == [] else "FAIL"
    return {"status": effective, "findings": [] if effective == "PASS" else findings, "coverage": scope}, findings, evidence_sha


def _review_render(
    root: Path,
    projection: dict[str, Any],
    observed_sha: str | None,
    canonical_sha: str,
    required: bool,
) -> tuple[dict[str, object], list[dict[str, object]], str | None]:
    review = projection.get("review") if isinstance(projection.get("review"), dict) else {}
    status = review.get("render_status")
    findings = review.get("render_findings")
    problems: list[dict[str, object]] = []
    if not required:
        if review.get("render_required") is True:
            problems.append(_finding("render_scope_mismatch", "projection marks render required although approved scope does not", "ALIGN_RENDER_REQUIREMENT_WITH_APPROVED_SCOPE"))
        return {"status": "NOT_REQUIRED", "findings": []}, problems, None
    if review.get("render_required") is not True:
        problems.append(_finding("render_requirement_downgrade", "approved scope requires render review", "RESTORE_REQUIRED_RENDER_REVIEW_AND_OBSERVE_THE_CURRENT_OUTPUT"))
    if status == "NOT_REVIEWED":
        return {"status": "UNKNOWN", "findings": None}, problems, None
    evidence_sha: str | None = None
    evidence_loaded = False
    try:
        evidence, evidence_sha, _ = _load_ref(root, review.get("render_evidence"))
        evidence_loaded = True
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
        problems.append(_finding(
            "render_review_evidence_invalid", str(exc),
            "OBSERVE_THE_CURRENT_RENDER_AND_BIND_ITS_EVIDENCE_TO_CURRENT_SOURCE_AND_PROJECTION",
        ))
        evidence = None
    reviewer = review.get("render_reviewer")
    scope = review.get("render_scope") if isinstance(review.get("render_scope"), list) else []
    if not isinstance(reviewer, str) or not reviewer:
        problems.append(_finding("render_reviewer_missing", "render reviewer identity is absent", "RECORD_THE_ACTUAL_RENDER_REVIEWER_IN_BOUND_EVIDENCE"))
    if review.get("rendered_projection_sha256") != observed_sha:
        problems.append(_finding("stale_render_projection_review", "rendered projection hash differs from current bytes", "OBSERVE_THE_CURRENT_PROJECTION_RENDER"))
    if review.get("rendered_source_sha256") != canonical_sha:
        problems.append(_finding("stale_render_source_review", "render review source hash differs from current canonical bytes", "OBSERVE_AGAINST_THE_CURRENT_CANONICAL_SOURCE"))
    if isinstance(evidence, dict):
        expected = {
            "reviewer": reviewer,
            "projection_sha256": observed_sha,
            "source_sha256": canonical_sha,
            "scope": scope,
            "verdict": status,
        }
        if evidence != expected:
            problems.append(_finding(
                "render_review_evidence_mismatch",
                "bound render evidence does not exactly match reviewer, source, projection, scope, and verdict",
                "CORRECT_THE_RENDER_RECORD_OR_RERUN_THE_RENDER_REVIEW",
            ))
    elif evidence_loaded:
        problems.append(_finding(
            "render_review_evidence_mismatch",
            "bound render evidence must be an object with the exact reviewer, source, projection, scope, and verdict",
            "CORRECT_THE_RENDER_RECORD_OR_RERUN_THE_RENDER_REVIEW",
        ))
    if status == "PASS" and findings == [] and not problems:
        return {"status": "PASS", "findings": []}, problems, evidence_sha
    problems.append(_finding("render_review_incomplete", "required render review is not a bound PASS", "OBSERVE_AND_RECORD_THE_CURRENT_RENDER_OR_KEEP_IT_UNKNOWN"))
    return {"status": "FAIL", "findings": problems}, problems, evidence_sha


def audit_projection_input(input_path: Path | str) -> dict[str, object]:
    path = Path(input_path).resolve()
    root = path.parent
    value, input_raw = _load_json(path)
    if not isinstance(value, dict) or value.get("schema_version") != INPUT_SCHEMA:
        raise ValueError(f"input must use {INPUT_SCHEMA}")

    canonical_ref = value.get("canonical_state")
    if not isinstance(canonical_ref, dict) or set(canonical_ref) != {"path", "sha256"}:
        raise ValueError("canonical_state must contain exactly path and sha256")
    canonical_path = _resolve_path(root, canonical_ref["path"])
    canonical_value, canonical_raw = _load_json(canonical_path)
    canonical_sha = _sha256_bytes(canonical_raw)
    if canonical_sha != canonical_ref["sha256"] or not isinstance(canonical_value, dict):
        raise ValueError("canonical state identity mismatch")

    scope, scope_sha, _ = _load_ref(root, value.get("scope_authority"))
    if not isinstance(scope, dict):
        raise ValueError("scope authority must resolve to an object")
    required_ids = scope.get("required_projection_ids")
    semantic_required_ids = scope.get("semantic_review_required_ids")
    render_required_ids = scope.get("render_review_required_ids")
    if not all(isinstance(item, list) and len(item) == len(set(item)) for item in (required_ids, semantic_required_ids, render_required_ids)):
        raise ValueError("scope projection inventories must be unique arrays")
    if not required_ids:
        raise ValueError("approved scope must name at least one required projection")
    required_set = set(required_ids)
    semantic_required_set = set(semantic_required_ids)
    render_required_set = set(render_required_ids)
    if not semantic_required_set.issubset(required_set) or not render_required_set.issubset(required_set):
        raise ValueError("review-required projections must be required projections")
    projection_contracts = scope.get("projection_contracts")
    if not isinstance(projection_contracts, dict) or not required_set.issubset(projection_contracts):
        raise ValueError("scope must define a projection contract for every required projection")
    for projection_id in required_set:
        contract = projection_contracts[projection_id]
        if not isinstance(contract, dict) or set(contract) != {"kind", "required_markers", "semantic_coverage", "recovery_owner"}:
            raise ValueError(f"invalid projection contract: {projection_id}")
        if (
            not isinstance(contract["kind"], str)
            or not contract["kind"]
            or not isinstance(contract["required_markers"], list)
            or not all(isinstance(item, str) and item for item in contract["required_markers"])
            or not isinstance(contract["semantic_coverage"], list)
            or len(contract["semantic_coverage"]) != len(set(contract["semantic_coverage"]))
            or not all(isinstance(item, str) and item for item in contract["semantic_coverage"])
            or not isinstance(contract["recovery_owner"], str)
            or not contract["recovery_owner"]
        ):
            raise ValueError(f"invalid projection contract values: {projection_id}")
        if projection_id not in semantic_required_set and contract["semantic_coverage"]:
            raise ValueError(f"semantic coverage requires semantic review: {projection_id}")

    declarations = value.get("projections")
    if not isinstance(declarations, list):
        raise ValueError("projections must be an array")
    by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for declaration in declarations:
        projection_id = declaration.get("projection_id") if isinstance(declaration, dict) else None
        if not isinstance(projection_id, str) or not projection_id:
            raise ValueError("each projection requires a nonempty projection_id")
        if projection_id in by_id:
            duplicate_ids.add(projection_id)
        else:
            by_id[projection_id] = declaration

    roster = [
        {
            "projection_id": projection_id,
            "kind": projection_contracts[projection_id]["kind"],
            "path": by_id.get(projection_id, {}).get("path"),
        }
        for projection_id in sorted(required_set)
    ]
    resume_identity = _sha256_json({
        "canonical_sha256": canonical_sha,
        "scope_sha256": scope_sha,
        "required_roster": roster,
    })

    projections: list[dict[str, object]] = []
    for projection_id in sorted(required_set | set(by_id)):
        declaration = by_id.get(projection_id)
        if declaration is None:
            projections.append({
                "projection_id": projection_id,
                "kind": None,
                "path": None,
                "sha256": None,
                "required": True,
                "materialization": "FAIL",
                "structure": "FAIL",
                "source_identity": "UNKNOWN",
                "semantic_review": {"status": "UNKNOWN", "findings": None, "coverage": []},
                "coverage": {"status": "UNKNOWN", "required": projection_contracts[projection_id]["semantic_coverage"], "reviewed": None},
                "render_review": {"status": "UNKNOWN" if projection_id in render_required_set else "NOT_REQUIRED", "findings": None if projection_id in render_required_set else []},
                "review_evidence_sha256": None,
                "render_evidence_sha256": None,
                "status": "FAILED",
                "findings": [_finding("required_projection_missing", "approved scope requires a projection omitted from the input", "MATERIALIZE_AND_DECLARE_THE_REQUIRED_PROJECTION")],
                "recovery_owner": projection_contracts[projection_id]["recovery_owner"],
                "next_action": "MATERIALIZE_AND_DECLARE_THE_REQUIRED_PROJECTION",
            })
            continue

        findings: list[dict[str, object]] = []
        required = projection_id in required_set
        contract = projection_contracts.get(projection_id, {
            "kind": declaration.get("kind"),
            "required_markers": [],
            "semantic_coverage": [],
            "recovery_owner": declaration.get("recovery_owner") or "PRODUCT_DEFINITION_OWNER",
        })
        if required and declaration.get("required") is not True:
            findings.append(_finding("scope_requirement_downgrade", "input cannot lower an approved required projection", "RESTORE_THE_APPROVED_REQUIRED_PROJECTION"))
        if projection_id in duplicate_ids:
            findings.append(_finding("duplicate_projection_id", "projection_id appears more than once", "KEEP_ONE_EXACT_DECLARATION_PER_PROJECTION_ID"))
        projection_path: Path | None = None
        content: str | None = None
        observed_sha: str | None = None
        materialization = "FAIL"
        try:
            projection_path = _resolve_path(root, declaration.get("path"))
            raw = projection_path.read_bytes()
            observed_sha = _sha256_bytes(raw)
            content = raw.decode("utf-8")
            if observed_sha != declaration.get("sha256"):
                findings.append(_finding("projection_hash_mismatch", "declared projection hash differs from current bytes", "REBIND_TO_CURRENT_BYTES_AND_RERUN_REQUIRED_REVIEWS"))
            else:
                materialization = "PASS"
        except (OSError, UnicodeError, ValueError) as exc:
            findings.append(_finding("projection_not_materialized", str(exc), "MATERIALIZE_THE_PROJECTION_AT_THE_DECLARED_PATH"))

        tokens = declaration.get("source_identity_tokens")
        project = canonical_value.get("project") if isinstance(canonical_value.get("project"), dict) else {}
        expected_identity = {
            "definition_revision": project.get("definition_revision"),
            "definition_digest": definition_digest(canonical_value),
        }
        source_identity = "PASS"
        if content is None or not isinstance(tokens, list) or len(tokens) != 2:
            source_identity = "FAIL"
        else:
            seen_fields: set[str] = set()
            for token in tokens:
                if not isinstance(token, dict) or set(token) != {"field", "value", "token"}:
                    source_identity = "FAIL"
                    continue
                field = token["field"]
                seen_fields.add(field)
                expected_value = expected_identity.get(field)
                literal = token.get("token")
                if (
                    field not in expected_identity
                    or token["value"] != expected_value
                    or not isinstance(literal, str)
                    or str(expected_value) not in literal
                    or literal not in content
                ):
                    source_identity = "FAIL"
            if seen_fields != set(expected_identity):
                source_identity = "FAIL"
        if source_identity == "FAIL":
            findings.append(_finding("source_identity_missing", "projection does not contain every required current source identity token", "UPDATE_SOURCE_IDENTITY_WITHOUT_CLAIMING_SEMANTIC_REVIEW"))

        structure = "PASS"
        if materialization != "PASS" or projection_id in duplicate_ids:
            structure = "FAIL"
        if declaration.get("kind") != contract["kind"]:
            structure = "FAIL"
            findings.append(_finding("projection_kind_mismatch", "projection kind differs from the approved scope contract", "RESTORE_THE_APPROVED_PROJECTION_KIND"))
        missing_markers = [marker for marker in contract["required_markers"] if content is None or marker not in content]
        if missing_markers:
            structure = "FAIL"
            findings.append(_finding(
                "projection_structure_missing",
                "projection bytes omit markers required by the approved scope contract",
                "RESTORE_THE_MISSING_APPROVED_STRUCTURE_AND_RERUN_REVIEW",
                missing_markers=missing_markers,
            ))

        semantic, semantic_problems, evidence_sha = _review_semantics(
            root, declaration, content, observed_sha, canonical_value, canonical_sha,
            projection_id in semantic_required_set,
            contract["semantic_coverage"],
        )
        findings.extend(semantic_problems)
        review_value = declaration.get("review") if isinstance(declaration.get("review"), dict) else {}
        declared_coverage = review_value.get("scope") if isinstance(review_value.get("scope"), list) else None
        if projection_id not in semantic_required_set:
            coverage = {"status": "PASS", "required": [], "reviewed": []}
        elif semantic["status"] == "UNKNOWN":
            coverage = {"status": "UNKNOWN", "required": contract["semantic_coverage"], "reviewed": None}
        elif declared_coverage == contract["semantic_coverage"]:
            coverage = {"status": "PASS", "required": contract["semantic_coverage"], "reviewed": declared_coverage}
        else:
            coverage = {"status": "FAIL", "required": contract["semantic_coverage"], "reviewed": declared_coverage}
        render, render_problems, render_evidence_sha = _review_render(
            root, declaration, observed_sha, canonical_sha,
            projection_id in render_required_set,
        )
        findings.extend(render_problems)

        if declaration.get("kind") == "APPROVAL_MANIFEST" and content is not None:
            try:
                if json.loads(content) != compute_approval_manifest(canonical_value):
                    findings.append(_finding("approval_manifest_projection_mismatch", "manifest bytes are not the current builder projection", "REBUILD_THE_MANIFEST_FROM_THE_EXACT_CANONICAL_STATE"))
            except (BindingError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                findings.append(_finding("approval_manifest_projection_invalid", str(exc), "REBUILD_THE_MANIFEST_FROM_THE_EXACT_CANONICAL_STATE"))

        complete = (
            required
            and declaration.get("required") is True
            and structure == "PASS"
            and source_identity == "PASS"
            and coverage["status"] == "PASS"
            and semantic["status"] in {"PASS", "NOT_REQUIRED"}
            and render["status"] in {"PASS", "NOT_REQUIRED"}
            and not findings
        )
        status = "COMPLETE" if complete else ("PENDING" if semantic["status"] == "UNKNOWN" or render["status"] == "UNKNOWN" else "FAILED")
        next_action = "NONE" if complete else (findings[0]["next_action"] if findings else "COMPLETE_THE_UNREVIEWED_REQUIRED_AXIS")
        projections.append({
            "projection_id": projection_id,
            "kind": declaration.get("kind"),
            "path": str(projection_path) if projection_path is not None else declaration.get("path"),
            "sha256": observed_sha,
            "required": required,
            "materialization": materialization,
            "structure": structure,
            "source_identity": source_identity,
            "semantic_review": semantic,
            "coverage": coverage,
            "render_review": render,
            "review_evidence_sha256": evidence_sha,
            "render_evidence_sha256": render_evidence_sha,
            "status": status,
            "findings": findings,
            "recovery_owner": contract["recovery_owner"],
            "next_action": next_action,
        })

    completed = sorted(item["projection_id"] for item in projections if item["status"] == "COMPLETE" and item["projection_id"] in required_set)
    pending = sorted(item["projection_id"] for item in projections if item["status"] == "PENDING" and item["projection_id"] in required_set)
    failed = sorted(item["projection_id"] for item in projections if item["status"] == "FAILED" and item["projection_id"] in required_set)

    resumed: list[str] = []
    receipt_value = value.get("resume_receipt")
    if receipt_value is not None:
        receipt_path = _resolve_path(root, receipt_value)
        receipt, _ = _load_json(receipt_path)
        if isinstance(receipt, dict) and receipt.get("schema_version") == OUTPUT_SCHEMA and receipt.get("resume_identity") == resume_identity:
            previous = {
                item.get("projection_id"): item
                for item in receipt.get("projections", [])
                if isinstance(item, dict)
            }
            for item in projections:
                old = previous.get(item["projection_id"])
                if (
                    item["status"] == "COMPLETE"
                    and isinstance(old, dict)
                    and old.get("status") == "COMPLETE"
                    and old.get("sha256") == item["sha256"]
                    and old.get("review_evidence_sha256") == item["review_evidence_sha256"]
                    and old.get("render_evidence_sha256") == item["render_evidence_sha256"]
                    and old.get("source_identity") == "PASS"
                ):
                    resumed.append(item["projection_id"])

    overall = "PASS" if set(completed) == required_set and not pending and not failed else "PARTIAL"
    result = {
        "schema_version": OUTPUT_SCHEMA,
        "input": {"path": str(path), "sha256": _sha256_bytes(input_raw)},
        "canonical_source": {"path": str(canonical_path), "sha256": canonical_sha},
        "scope_authority_sha256": scope_sha,
        "source_unchanged": canonical_path.read_bytes() == canonical_raw,
        "overall_status": overall,
        "resume_identity": resume_identity,
        "completed_projection_ids": completed,
        "pending_projection_ids": pending,
        "failed_projection_ids": failed,
        "resumed_projection_ids": sorted(resumed),
        "projections": projections,
        "next_actions": [
            {
                "projection_id": item["projection_id"],
                "owner": item["recovery_owner"],
                "action": item["next_action"],
                "path": item["path"],
            }
            for item in projections if item["status"] != "COMPLETE"
        ],
        "limitations": [
            "Exact hashes, pointers, and review-record binding prove identity and coverage only; they do not authenticate the reviewer's authority or make the semantic verdict true.",
            "This audit never edits canonical state or projections and never creates product approval.",
        ],
    }
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return _finish(
            {"error": "usage: audit_planning_projections.py AUDIT_INPUT_JSON"},
            stream=sys.stderr,
            return_code=2,
        )
    try:
        result = audit_projection_input(argv[1])
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
        return _finish({"error": str(exc)}, stream=sys.stderr, return_code=2)
    return _finish(result, stream=sys.stdout, return_code=0 if result["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
