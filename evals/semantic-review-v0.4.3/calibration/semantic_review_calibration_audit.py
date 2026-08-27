"""Answer-blind structural audits for the synthetic calibration fixture."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


IDENTITY_RE = re.compile(r"^(?:action|lifecycle):[A-Za-z0-9_.-]+:[A-Za-z0-9_]+$")
IDENTITY_IN_TEXT_RE = re.compile(
    r"\b(?:action|lifecycle):[A-Za-z0-9_.-]+:[A-Za-z0-9_]+\b"
)
CASE_ID_RE = re.compile(r"^G-(?:00[1-9]|01[0-5])$")
CASE_ID_IN_TEXT_RE = re.compile(r"\bG-(?:00[1-9]|01[0-5])\b")
OWNER_ID_IN_TEXT_RE = re.compile(r"\b(?:ACT|LC)-[A-Za-z0-9_.-]+\b")
WINDOWS_CONTROLLER_PATH_RE = re.compile(
    r"[A-Za-z]:[\\/][^\r\n\"']*(?:calibration-controller-evidence|seed-oracle\.json)",
    re.IGNORECASE,
)
POSIX_CONTROLLER_PATH_RE = re.compile(
    r"/(?:[^/\r\n\"']+/)*(?:calibration-controller-evidence)(?:/|$)",
    re.IGNORECASE,
)
OUTCOME_HINT_RE = re.compile(
    r"\b(?:approved|rejected(?: candidate)?|supported(?: exactly)?|defective|defect|"
    r"missing(?: required reference| owned semantic)?|unsupported(?: overreach)?|"
    r"omit(?:ted|s)?|omission|overreach(?:ed|es|ing)?|"
    r"contradict(?:s|ed|ion|ions|ory)?(?: owner)?|"
    r"duplicat(?:e|ed|es|ing|ion|ions)|invalid(?: duplication)?|rationale)\b",
    re.IGNORECASE,
)
OUTCOME_KEYS = {
    "answer",
    "classification",
    "defect",
    "defect_label",
    "defect_summary",
    "defective",
    "expected_outcome",
    "expected_support",
    "expected_verdict",
    "golden_answer",
    "hidden_answer",
    "intended_rationale_code",
    "intended_verdict",
    "is_defective",
    "oracle_outcome",
    "outcome",
    "rationale",
    "rationale_code",
    "supported",
    "verdict",
}
ALLOWED_VERDICTS = (
    "APPROVED",
    "REJECTED_CANDIDATE",
    "RUBRIC_ERROR",
    "INPUT_PACKAGE_ERROR",
)
ALLOWED_RATIONALE_CODES = (
    "SUPPORTED_EXACTLY",
    "MISSING_OWNED_SEMANTIC",
    "MISSING_REQUIRED_REFERENCE",
    "UNSUPPORTED_OVERREACH",
    "CONTRADICTS_OWNER",
    "INVALID_DUPLICATION",
    "INVALID_PROVENANCE",
    "ACTIVE_SUPERSEDED_SOURCE",
    "RESPONSIBILITY_UNDEFINED",
    "COMPLETENESS_UNDEFINED",
    "PACKAGE_HASH_MISMATCH",
    "BRIEF_HASH_MISMATCH",
    "CONTRACT_HASH_MISMATCH",
    "RESPONSIBILITY_PROFILE_HASH_MISMATCH",
    "OBLIGATION_INDEX_HASH_MISMATCH",
    "IDENTITY_SET_MISMATCH",
    "PREVIOUS_VERDICT_EXPOSURE",
    "OUTPUT_SCHEMA_VIOLATION",
)
ALLOWED_ENUMERATIONS = {
    "allowed_verdicts": ALLOWED_VERDICTS,
    "allowed_rationale_codes": ALLOWED_RATIONALE_CODES,
}
# Canonical SHA-256 commitments for the exact responsibility-profile evidence
# blocks materialized from G-001 through G-015.  Only these normative blocks
# may contain ownership criteria vocabulary that overlaps outcome-hint terms.
ALLOWED_RESPONSIBILITY_PROFILE_EVIDENCE_SHA256 = frozenset(
    {
        "75eb729833d000744f162104c3df020dcac69b97d865c57f933c74b41af8d86b",
        "a18f7eda25fe12604e054bb2e2345ebe19711ba00f9a58e8fb3465bb601ffdc1",
        "7d90a016757bda788c72b1bdd89e7888bdac8d3e7e3ff92d8e8379e265a2e561",
        "a305f9513f17ed41e3efe634320c7bd380c9dfd61bc020606e4763d142f629d7",
        "23789ea605023db30fe5c6843c0c976fca9fa037ca9e50c276a28bcf184d884d",
        "58661105187209371446ead53849dd371e6ec1a778b1be2685478e237f7fcb96",
        "5576336c118f677eb3c9f56dc0e87d6fb5a3ad14ac096de2c4c750aa00da1cbf",
    }
)

ACTION_OWNER_RE = re.compile(r"^ACT-CAL-REQUEST-0[1-3]$")
LIFECYCLE_OWNER_RE = re.compile(r"^LC-CAL-DOCUMENT-0[1-3]$")
TEST_REFERENCE_RE = re.compile(
    r"^TEST-CAL-(?:ACT-CAL-REQUEST|LC-CAL-DOCUMENT)-0[1-3]-FR-[AL][0-9]{2}$"
)
STABLE_REFERENCE_TOKEN_RE = re.compile(
    r"\b[A-Z]+-CAL-(?:REQUEST|DOCUMENT)-0[1-3]\b"
)
REFERENCE_ONLY_RULE_IDS = frozenset({"FR-A24", "FR-A25", "FR-A26"})
REFERENCE_ONLY_FIELDS = frozenset({"superseded_rules", "test_obligations", "trace"})
TOKEN_RE = re.compile(r"[a-z]+")
NEUTRAL_SEMANTIC_TERMS = frozenset(
    """
    a absent accept act action actor actors after all allow allowed also an and another append
    apply approval approver archival archived as assigned assignment attempt attempts audit
    authenticated authentication author authoritative authority avoid be before bind binding blocks
    bound boundary business by bytes cal calibration carry category classes close
    change class command commit committed concurrency conditions confirmation contain correctable
    create current deadline decision decline declining default define deleted delivery detach
    discard document documents domain draft duplicate earlier effects empty enter entering entry
    error event
    every evidence exclude expectations expected expired explicit failing failure final
    finalization finalized for forbid forbidden from guarded history idempotency identifier
    effect execute guards immutable in increment incrementing input intended interval invariants irreversible is
    it its keep key lc leave lifecycle limit must mutation mutations no non notice
    new notification object obligation obligations on once one only op operation other outcome
    outside owned participant participants pass pending per perform permit preconditions predicate
    preservation preserve prevent prior projection queue ready reason recipient record recovery
    reference reject remain replace requires
    rejection relationship report request require required result resulting retain retained
    requesting retry return reuse reversal reversibility reversible reversing rule rules same select separate
    session set show side stable stale state stated states submitted success successful superseded
    supersession synthetic target test than that the to trace transition transitions treat
    unassigned unchanged undeclared unrelated unresolved uploaded validation version visible well
    when while whitespace window with without
    """.split()
)


def _finding(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _normalize_key(key: Any) -> str:
    return str(key).strip().lower().replace("-", "_")


def _outcome_hint_text(value: str) -> bool:
    normalized = re.sub(r"[^A-Za-z0-9]+", " ", value)
    return OUTCOME_HINT_RE.search(normalized) is not None


def _is_full_allowed_enumeration(key: Any, value: Any) -> bool:
    normalized_key = _normalize_key(key)
    allowed = ALLOWED_ENUMERATIONS.get(normalized_key)
    return allowed is not None and isinstance(value, list) and tuple(value) == allowed


def _is_empty_response_slot(key: Any, value: Any) -> bool:
    return _normalize_key(key) in {"verdict", "rationale_code"} and value is None


def _is_exact_responsibility_profile_evidence(key: Any, value: Any) -> bool:
    if _normalize_key(key) != "responsibility_profile_evidence" or not isinstance(
        value, dict
    ):
        return False
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return (
        hashlib.sha256(canonical).hexdigest()
        in ALLOWED_RESPONSIBILITY_PROFILE_EVIDENCE_SHA256
    )


def _contains_outcome_hint(value: Any) -> bool:
    if isinstance(value, str):
        return _outcome_hint_text(value)
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = _normalize_key(key)
            if (
                _is_full_allowed_enumeration(key, child)
                or _is_empty_response_slot(key, child)
                or _is_exact_responsibility_profile_evidence(key, child)
            ):
                continue
            if normalized_key in OUTCOME_KEYS or _contains_outcome_hint(child):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_outcome_hint(child) for child in value)
    return False


def _json_answer_findings(value: Any, path: str, pointer: str = "") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(value, dict):
        normalized = {_normalize_key(key): child for key, child in value.items()}
        identity = normalized.get("review_identity")
        if isinstance(identity, str) and IDENTITY_RE.fullmatch(identity):
            outcome_keys = sorted(
                key
                for key in set(normalized) & OUTCOME_KEYS
                if not _is_empty_response_slot(key, normalized[key])
            )
            hinted_values = any(
                _contains_outcome_hint(child)
                for key, child in normalized.items()
                if key != "review_identity"
                and not _is_full_allowed_enumeration(key, child)
                and not _is_empty_response_slot(key, child)
                and not _is_exact_responsibility_profile_evidence(key, child)
            )
            if outcome_keys or hinted_values:
                findings.append(
                    _finding(
                        "PER_IDENTITY_OUTCOME",
                        f"{path}{pointer}",
                        "review identity is paired with an outcome or defect hint",
                    )
                )
        identity_tuple_keys = {"owner_kind", "owner_id", "semantic_field"}
        if identity_tuple_keys.issubset(normalized):
            outcome_keys = sorted(
                key
                for key in set(normalized) & OUTCOME_KEYS
                if not _is_empty_response_slot(key, normalized[key])
            )
            hinted_values = any(
                _contains_outcome_hint(child)
                for key, child in normalized.items()
                if key not in identity_tuple_keys
                and not _is_full_allowed_enumeration(key, child)
                and not _is_empty_response_slot(key, child)
                and not _is_exact_responsibility_profile_evidence(key, child)
            )
            if outcome_keys or hinted_values:
                findings.append(
                    _finding(
                        "PER_IDENTITY_OUTCOME",
                        f"{path}{pointer}",
                        "owner/field tuple is paired with an outcome or defect hint",
                    )
                )
        case_id = normalized.get("case_id")
        if isinstance(case_id, str) and CASE_ID_RE.fullmatch(case_id):
            outcome_keys = sorted(
                key
                for key in set(normalized) & OUTCOME_KEYS
                if not _is_empty_response_slot(key, normalized[key])
            )
            hinted_values = any(
                _contains_outcome_hint(child)
                for key, child in normalized.items()
                if key != "case_id"
                and not _is_full_allowed_enumeration(key, child)
                and not _is_empty_response_slot(key, child)
                and not _is_exact_responsibility_profile_evidence(key, child)
            )
            partial_enumerations = any(
                _normalize_key(key) in ALLOWED_ENUMERATIONS
                and not _is_full_allowed_enumeration(key, child)
                for key, child in value.items()
            )
            if outcome_keys or hinted_values or partial_enumerations:
                findings.append(
                    _finding(
                        "PER_CASE_OUTCOME",
                        f"{path}{pointer}",
                        "golden case is paired with a filled outcome or outcome hint",
                    )
                )
        for key, child in value.items():
            key_text = str(key)
            if IDENTITY_RE.fullmatch(key_text) and _contains_outcome_hint(child):
                findings.append(
                    _finding(
                        "PER_IDENTITY_OUTCOME",
                        f"{path}{pointer}/{key_text}",
                        "identity-keyed value contains an outcome or defect hint",
                    )
                )
            findings.extend(
                _json_answer_findings(child, path, f"{pointer}/{key_text}")
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_json_answer_findings(child, path, f"{pointer}/{index}"))
    return findings


def find_answer_leaks(
    paths: Iterable[Path], *, allowed_exact_sha256: set[str]
) -> list[dict[str, str]]:
    """Return answer-bearing or controller-path findings from calibration surfaces."""

    findings: list[dict[str, str]] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_file():
            findings.append(
                _finding("MISSING_AUDIT_SURFACE", str(path), "tracked surface is missing")
            )
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() in allowed_exact_sha256:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(
                _finding("NON_TEXT_AUDIT_SURFACE", str(path), "surface is not UTF-8")
            )
            continue
        if WINDOWS_CONTROLLER_PATH_RE.search(text) or POSIX_CONTROLLER_PATH_RE.search(text):
            findings.append(
                _finding(
                    "EXTERNAL_ORACLE_PATH",
                    str(path),
                    "controller-only evidence path is present",
                )
            )
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            for line_number, line in enumerate(text.splitlines(), start=1):
                has_identity = (
                    IDENTITY_IN_TEXT_RE.search(line)
                    or OWNER_ID_IN_TEXT_RE.search(line)
                    or CASE_ID_IN_TEXT_RE.search(line)
                )
                if has_identity and _outcome_hint_text(line):
                    findings.append(
                        _finding(
                            "PER_IDENTITY_OUTCOME",
                            f"{path}:{line_number}",
                            "text pairs a review identity with an outcome or defect hint",
                        )
                    )
        else:
            findings.extend(_json_answer_findings(value, str(path)))
    return findings


def _semantic_text_findings(
    text: str,
    *,
    path: str,
    required_tag: str,
    allow_stable_reference: bool = False,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if required_tag.lower() not in text.lower():
        findings.append(
            _finding(
                "MISSING_GENERIC_SCOPE",
                path,
                f"semantic text does not bind generic scope {required_tag}",
            )
        )
    vocabulary_text = (
        STABLE_REFERENCE_TOKEN_RE.sub("", text) if allow_stable_reference else text
    )
    unexpected = sorted(
        set(TOKEN_RE.findall(vocabulary_text.lower())) - NEUTRAL_SEMANTIC_TERMS
    )
    if unexpected:
        findings.append(
            _finding(
                "NON_NEUTRAL_TERM",
                path,
                "semantic text contains terms outside the closed neutral vocabulary: "
                + ", ".join(unexpected),
            )
        )
    return findings


def _owner_tag(owner_kind: str, owner_id: str) -> str | None:
    if owner_kind == "action" and ACTION_OWNER_RE.fullmatch(owner_id):
        return f"REQUEST-{owner_id[-2:]}"
    if owner_kind == "lifecycle" and LIFECYCLE_OWNER_RE.fullmatch(owner_id):
        return f"DOCUMENT-{owner_id[-2:]}"
    return None


def audit_product_neutrality(
    authority: dict[str, Any],
    contract: dict[str, Any],
    obligation_index: dict[str, Any],
    identity_inventory: dict[str, Any],
) -> list[dict[str, str]]:
    """Enforce generic owners, scope binding, and a closed neutral vocabulary."""

    findings: list[dict[str, str]] = []
    expected_authority_metadata = {
        "fixture_name": "semantic-review-calibration-v1",
        "fixture_kind": "synthetic_calibration_fixture",
        "product_definition_authority": False,
        "semantic_scope": "neutral generic request and document approval semantics",
    }
    for key, expected in expected_authority_metadata.items():
        if authority.get(key) != expected:
            findings.append(
                _finding(
                    "INVALID_SYNTHETIC_AUTHORITY",
                    f"authority/{key}",
                    "synthetic authority metadata differs from the calibration contract",
                )
            )

    rules = authority.get("objects", {}).get("rules", [])
    if not isinstance(rules, list) or len(rules) != 114:
        findings.append(
            _finding(
                "INVALID_SYNTHETIC_AUTHORITY",
                "authority/objects/rules",
                "canonical authority must contain 114 synthetic rules",
            )
        )
        rules = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            findings.append(
                _finding(
                    "INVALID_SYNTHETIC_AUTHORITY",
                    f"authority/objects/rules/{index}",
                    "rule is not an object",
                )
            )
            continue
        owner_kind = rule.get("owner_kind")
        owner_id = rule.get("owner_id")
        tag = _owner_tag(owner_kind, owner_id) if isinstance(owner_id, str) else None
        if tag is None:
            findings.append(
                _finding(
                    "NON_GENERIC_OWNER",
                    f"authority/objects/rules/{index}/owner_id",
                    "authority owner is outside the closed generic owner set",
                )
            )
            continue
        text = rule.get("text")
        if not isinstance(text, str):
            findings.append(
                _finding(
                    "INVALID_SEMANTIC_TEXT",
                    f"authority/objects/rules/{index}/text",
                    "canonical semantic text is not a string",
                )
            )
            continue
        findings.extend(
            _semantic_text_findings(
                text,
                path=f"authority/objects/rules/{index}/text",
                required_tag=tag,
                allow_stable_reference=(
                    rule.get("responsibility_rule_id") in REFERENCE_ONLY_RULE_IDS
                ),
            )
        )

    source_authority = contract.get("source_authority", {})
    if source_authority.get("product_slug") != "semantic-review-calibration-v1":
        findings.append(
            _finding(
                "NON_GENERIC_PRODUCT_SLUG",
                "contract/source_authority/product_slug",
                "contract is not bound to the synthetic fixture slug",
            )
        )

    owners: dict[tuple[str, str], dict[str, Any]] = {}
    for owner_kind, collection_name, id_key in (
        ("action", "actions", "action_id"),
        ("lifecycle", "lifecycles", "lifecycle_id"),
    ):
        collection = contract.get(collection_name, [])
        if not isinstance(collection, list) or len(collection) != 3:
            findings.append(
                _finding(
                    "NON_GENERIC_OWNER_SET",
                    f"contract/{collection_name}",
                    "contract must contain exactly three generic owners",
                )
            )
            continue
        for owner in collection:
            if not isinstance(owner, dict) or not isinstance(owner.get(id_key), str):
                findings.append(
                    _finding(
                        "NON_GENERIC_OWNER",
                        f"contract/{collection_name}",
                        "owner record lacks a generic identifier",
                    )
                )
                continue
            owner_id = owner[id_key]
            if _owner_tag(owner_kind, owner_id) is None:
                findings.append(
                    _finding(
                        "NON_GENERIC_OWNER",
                        f"contract/{collection_name}/{owner_id}",
                        "owner identifier is outside the closed generic owner set",
                    )
                )
                continue
            owners[(owner_kind, owner_id)] = owner

    identities = identity_inventory.get("identities", [])
    if not isinstance(identities, list) or len(identities) != 114:
        findings.append(
            _finding(
                "INVALID_GENERIC_IDENTITY_SET",
                "identity_inventory/identities",
                "identity inventory must contain 114 generic identities",
            )
        )
        identities = []
    for index, identity in enumerate(identities):
        if not isinstance(identity, dict):
            findings.append(
                _finding(
                    "INVALID_GENERIC_IDENTITY_SET",
                    f"identity_inventory/identities/{index}",
                    "identity is not an object",
                )
            )
            continue
        owner_kind = identity.get("owner_kind")
        owner_id = identity.get("owner_id")
        semantic_field = identity.get("semantic_field")
        review_identity = identity.get("review_identity")
        tag = _owner_tag(owner_kind, owner_id) if isinstance(owner_id, str) else None
        expected_identity = f"{owner_kind}:{owner_id}:{semantic_field}"
        if tag is None or review_identity != expected_identity:
            findings.append(
                _finding(
                    "INVALID_GENERIC_IDENTITY_SET",
                    f"identity_inventory/identities/{index}",
                    "identity is outside the generic owner/field structure",
                )
            )
            continue
        owner = owners.get((owner_kind, owner_id))
        semantic = owner.get(semantic_field) if owner else None
        values = semantic.get("value") if isinstance(semantic, dict) else None
        if not isinstance(values, list) or not values or not all(
            isinstance(value, str) for value in values
        ):
            findings.append(
                _finding(
                    "INVALID_SEMANTIC_TEXT",
                    f"contract/{review_identity}",
                    "semantic candidate must be a non-empty string list",
                )
            )
            continue
        for value_index, text in enumerate(values):
            findings.extend(
                _semantic_text_findings(
                    text,
                    path=f"contract/{review_identity}/value/{value_index}",
                    required_tag=tag,
                    allow_stable_reference=semantic_field in REFERENCE_ONLY_FIELDS,
                )
            )

    obligations = obligation_index.get("obligations", [])
    if not isinstance(obligations, list) or len(obligations) != 114:
        findings.append(
            _finding(
                "INVALID_GENERIC_OBLIGATION_SET",
                "obligation_index/obligations",
                "obligation index must contain 114 generic obligations",
            )
        )
        obligations = []
    for index, obligation in enumerate(obligations):
        if not isinstance(obligation, dict):
            findings.append(
                _finding(
                    "INVALID_GENERIC_OBLIGATION_SET",
                    f"obligation_index/obligations/{index}",
                    "obligation is not an object",
                )
            )
            continue
        owner_id = obligation.get("owner_id")
        owner_kind = obligation.get("owner_kind")
        if not isinstance(owner_id, str) or _owner_tag(owner_kind, owner_id) is None:
            findings.append(
                _finding(
                    "NON_GENERIC_OWNER",
                    f"obligation_index/obligations/{index}/owner_id",
                    "obligation owner is outside the generic owner set",
                )
            )
        test_refs = obligation.get("required_test_refs")
        if (
            not isinstance(test_refs, list)
            or not test_refs
            or not all(
                isinstance(reference, str) and TEST_REFERENCE_RE.fullmatch(reference)
                for reference in test_refs
            )
        ):
            findings.append(
                _finding(
                    "NON_GENERIC_TEST_REFERENCE",
                    f"obligation_index/obligations/{index}/required_test_refs",
                    "test reference is outside the synthetic calibration namespace",
                )
            )
        notes = obligation.get("projection_notes")
        if isinstance(notes, str):
            findings.extend(
                _semantic_text_findings(
                    notes,
                    path=f"obligation_index/obligations/{index}/projection_notes",
                    required_tag="calibration",
                )
            )
        else:
            findings.append(
                _finding(
                    "INVALID_SEMANTIC_TEXT",
                    f"obligation_index/obligations/{index}/projection_notes",
                    "projection notes are not text",
                )
            )
    return findings
