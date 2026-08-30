import json
from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from migration_v2 import migrate_state_v020, verify_migration_result  # noqa: E402
from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    build_approval_commitment,
    build_approval_manifest_for_review,
    definition_digest,
    semantic_readiness_metrics,
)
from authority_binding_v2 import (  # noqa: E402
    canonical_record_index,
    resolve_record_pointer,
    sha256_json,
)
from state_validation_v2 import validate_state_v2  # noqa: E402


LEGACY_ROOT = ROOT / "product-definition" / "client-feedback-portal-dogfood"
EVAL_ROOT = ROOT / "evals" / "core-semantic-closure-v2-m6"
DOGFOOD_ROOT = EVAL_ROOT / "dogfood"
MIGRATION_ROOT = DOGFOOD_ROOT / "migration"
STATE_PATH = (
    DOGFOOD_ROOT
    / "product-definition"
    / "client-feedback-portal-dogfood-v2"
    / "state.json"
)
MIGRATION_CANDIDATE_PATH = MIGRATION_ROOT / "legacy-candidate.json"
MIGRATION_RECEIPT_PATH = MIGRATION_ROOT / "migration-receipt.json"
MANIFEST_PATH = DOGFOOD_ROOT / "approval-manifest.json"
EVIDENCE_MAP_PATH = DOGFOOD_ROOT / "phase-a-evidence-map.json"
RUNBOOK_PATH = EVAL_ROOT / "DOGFOOD_RUNBOOK.md"
README_PATH = EVAL_ROOT / "README.md"
AUDIT_PATH = EVAL_ROOT / "MIGRATION_AUDIT.md"
EXPECTED_DEFINITION_DIGEST = "ea4a1d0f899fdfd44f8c75068579555f2e198f90ae320500ad1bc5d8933e8ed7"
EXPECTED_MANIFEST_DIGEST = "bbdf01e34da4973efb07d9f0c9bf2de5839492b4cf4c9bcd193bc0327e9e69a1"
EXPECTED_ADDED_COUNT = 102

ANALYTICS_DECISION = (
    "For this bounded M6 existing-product V2 dogfood Product Definition only, "
    "product analytics/telemetry is NOT used. REQ-005/REQ-006 review-link access and "
    "thread actions emit no analytics events. Introduce no analytics event names, "
    "properties, tracking identifiers, analytics retention/access policy, funnels, "
    "or success metrics. Existing domain/business history remains ordinary product "
    "state/history where already required. Existing email delivery/send status remains "
    "ordinary product operational/domain state where already required. Neither is "
    "reclassified as analytics telemetry. This is an explicit current user product "
    "decision/boundary, not an inference from missing implementation. It is not a "
    "permanent system-wide prohibition for future products/revisions."
)

INTERACTION_DECISION = (
    "For this bounded M6 existing-product V2 dogfood Product Definition only: "
    "Loading and Submitting show pending state and never success. Empty shows the "
    "screen-specific zero state. Partial shows available authoritative data plus an "
    "explicit recovery notice. Completed follows only authoritative confirmation. "
    "Cancelled, Cancel, and Back cause no mutation and preserve eligible unsent text. "
    "Refresh reloads latest authoritative state. Committed review-link/thread mutations "
    "have no direct Undo; recovery uses documented new-link, new-reply, or reopen paths. "
    "Offline and Timeout withhold success, preserve eligible input, refresh authoritative "
    "state before retry, and must not duplicate mutation or notification. Destructive "
    "confirmation is N/A for this bounded fixture. This interaction policy is bounded "
    "to this dogfood Product Definition and is not a system-wide rule."
)

SCR_006_PURPOSE = (
    "Designer-only Review Access Management for an exact-Version target, designated "
    "Reviewer email, one active 30-day link, and send, resend, and revoke outcomes."
)
SCR_007_PURPOSE = (
    "Designer/Client exact-Version review canvas with immutable viewer, exact Version "
    "identity and state, pins, thread chronology and history, and role-scoped actions."
)

EXPECTED_MEANINGS = {
    ("SCR-006", "/purpose"): SCR_006_PURPOSE,
    ("SCR-006", "/major_actions"): [
        "send_review_request", "revoke_review_link", "resend_review_request",
    ],
    ("SCR-007", "/purpose"): SCR_007_PURPOSE,
    ("SCR-007", "/major_actions"): ["create_pin", "reply_thread", "resolve_thread"],
    ("FLOW-005", "/preconditions"): [
        "Designer session is authenticated and the project is ACTIVE."
    ],
    ("FLOW-005", "/paths"): [
        "Designer sends or resends an exact-Version review request, rotates the one "
        "active 30-day project link when issuing a new link, or manually revokes it."
    ],
    ("FLOW-005", "/outcomes/0"): "Send changes the exact Version from DRAFT to IN_REVIEW and immediately emails the active review link to the Client Reviewer.",
    ("FLOW-005", "/outcomes/1"): "Revoke invalidates the current active review link and its project sessions.",
    ("FLOW-005", "/outcomes/2"): "Resend issues a new active review link and immediately emails it to the Client Reviewer.",
    ("FLOW-006", "/preconditions"): [
        "The actor has current project access and the exact Version is mutable for the "
        "requested action."
    ],
    ("FLOW-006", "/paths"): [
        "Client Reviewer creates an exact-Version pin; Designer or Client Reviewer "
        "appends a reply; Designer resolves an OPEN thread."
    ],
    ("FLOW-006", "/outcomes/0"): "A valid Client Reviewer pin is stored on the exact Version and immediately notifies the Designer.",
    ("FLOW-006", "/outcomes/1"): "A valid reply appends to the exact-Version thread and immediately notifies the counterpart.",
    ("FLOW-006", "/outcomes/2"): "A valid Designer resolution changes the OPEN exact-Version thread to RESOLVED without notification.",
    ("DATA-002", "/purpose"): (
        "Exact-Version pin/thread state: image normalized x/y; PDF page plus normalized "
        "x/y; root pin comment; append-only replies; resolution status and history; "
        "APPROVED read-only behavior; message-attempt idempotency."
    ),
    ("DATA-004", "/purpose"): (
        "Project-scoped magic review-link lifecycle: designated Reviewer email identity; "
        "one ACTIVE link; 30-day expiry; rotation or manual revoke; lifecycle metadata; "
        "global session invalidation; old links are never restored."
    ),
    ("DATA-007", "/purpose"): (
        "New-pin email event: exact Version and pin identity, Client Reviewer actor, "
        "Designer recipient, immediate delivery status, and no Reviewer self-notification."
    ),
    ("DATA-008", "/purpose"): (
        "Thread-reply email event: exact Version, thread and reply identity, actor, "
        "counterpart recipient, immediate delivery status, and no author self-notification."
    ),
    ("DATA-009", "/purpose"): (
        "Review-request input and effect: project, exact Version, designated Client "
        "Reviewer recipient, and active review link; DRAFT to IN_REVIEW plus immediate "
        "email and no Designer self-notification."
    ),
    ("INT-001", "/purpose"): (
        "Transactional email delivery for review requests, new pins, and thread replies "
        "with the documented recipient and self-notification exclusions."
    ),
    ("STATE-001", "/conditions"): [
        "Review request changes only the exact Version from DRAFT to IN_REVIEW.",
        "Expected Version state revision mismatch rejects mutation and shows latest state.",
        "APPROVED exact Versions allow existing history reads and reject pin/reply mutation.",
    ],
    ("STATE-002", "/conditions/0"): "Loading and Submitting show pending state and never show success.",
    ("STATE-002", "/conditions/1"): "Completed and success follow only authoritative confirmation.",
    ("RULE-014", "/statement"): "Feedback is a point pin with a connected comment.",
    ("RULE-015", "/statement"): (
        "Image pins use normalized x/y; PDF pins use page number and normalized x/y."
    ),
    ("RULE-020", "/statement"): (
        "Only Client Reviewer creates a new pin; Designer and Client Reviewer may reply."
    ),
    ("RULE-021", "/statement"): "Only Designer resolves an OPEN comment thread.",
    ("RULE-027", "/statement"): (
        "Expired review-link access shows the expiry screen and blocks new reads/writes."
    ),
    ("RULE-033", "/statement"): "Only Designer manually revokes the current ACTIVE link.",
    ("RULE-046", "/statement"): (
        "Designer review request moves the exact Version from DRAFT to IN_REVIEW and "
        "immediately emails the active review link to Client Reviewer."
    ),
    ("RULE-063", "/statement"): (
        "APPROVED exact Versions reject new pin comments and all thread replies."
    ),
    ("RULE-077", "/statement"): (
        "ARCHIVED projects reject new comments, replies, review requests, approvals, and "
        "changes requests."
    ),
    ("RULE-084", "/statement"): (
        "Concurrent mutation is guarded by exact Version ID and expected state revision."
    ),
    ("RULE-110", "/statement"): (
        "Expired Designer session requires a new email magic-link authentication."
    ),
    ("RULE-119", "/statement"): (
        "Review Access Management empty shows no active review link or pending request; "
        "Review Canvas empty shows no pins or threads for the exact Version."
    ),
    ("RULE-120", "/statement"): (
        "Review Access Management and Review Canvas partial show their available "
        "authoritative data plus an explicit recovery notice."
    ),
    ("RULE-122", "/statement"): (
        "Cancelled, Cancel, and Back cause no mutation and preserve eligible unsent text."
    ),
    ("RULE-123", "/statement"): "Refresh reloads latest authoritative state.",
    ("RULE-124", "/statement"): (
        "Committed review-link and thread mutations have no direct Undo; recovery uses "
        "documented new-link, new-reply, or reopen paths."
    ),
    ("RULE-125", "/statement"): (
        "Offline and Timeout withhold success, preserve eligible input, refresh "
        "authoritative state before retry, and do not duplicate mutation or notification."
    ),
    ("RULE-128", "/statement"): (
        "Error withholds success and shows the applicable documented access, permission, "
        "archive, approved-state, or expected-revision rejection and recovery."
    ),
    ("RULE-129", "/statement"): (
        "Only an authenticated Designer may use Review Access Management actions."
    ),
    ("RULE-130", "/statement"): (
        "Designer enters the review canvas with an authenticated session; Client Reviewer "
        "enters with an active project-scoped link and designated email identity."
    ),
    ("EVD-014", "/claim"): (
        "The documented bounded transactional-email inventory includes review-request "
        "link delivery, new-pin notification, and thread-reply notification; it defines "
        "no revocation or thread-resolution email use."
    ),
    ("EVD-015", "/claim"): INTERACTION_DECISION,
}


def refs(*pairs):
    return list(pairs)


STATE_BINDINGS = {
    "SCR-006": {
        "default": refs(("SCR-006", "/purpose")),
        "loading": refs(("STATE-002", "/conditions/0")),
        "empty": refs(("RULE-119", "/statement")),
        "partial": refs(("RULE-120", "/statement")),
        "success": refs(("STATE-002", "/conditions/1")),
        "error": refs(("RULE-128", "/statement")),
        "disabled": refs(("RULE-077", "/statement")),
        "permission_denied": refs(("RULE-129", "/statement")),
        "unauthenticated": refs(("FLOW-005", "/preconditions")),
        "offline": refs(("RULE-125", "/statement")),
        "timeout": refs(("RULE-125", "/statement")),
        "retrying": refs(("RULE-125", "/statement")),
        "submitting": refs(("STATE-002", "/conditions/0")),
        "completed": refs(("STATE-002", "/conditions/1")),
        "cancelled": refs(("RULE-122", "/statement")),
        "expired": refs(("RULE-027", "/statement")),
    },
    "SCR-007": {
        "default": refs(("SCR-007", "/purpose")),
        "loading": refs(("STATE-002", "/conditions/0")),
        "empty": refs(("RULE-119", "/statement")),
        "partial": refs(("RULE-120", "/statement")),
        "success": refs(("STATE-002", "/conditions/1")),
        "error": refs(("RULE-128", "/statement")),
        "disabled": refs(("RULE-063", "/statement")),
        "permission_denied": refs(
            ("RULE-020", "/statement"), ("RULE-021", "/statement")
        ),
        "unauthenticated": refs(("RULE-130", "/statement")),
        "offline": refs(("RULE-125", "/statement")),
        "timeout": refs(("RULE-125", "/statement")),
        "retrying": refs(("RULE-125", "/statement")),
        "submitting": refs(("STATE-002", "/conditions/0")),
        "completed": refs(("STATE-002", "/conditions/1")),
        "cancelled": refs(("RULE-122", "/statement")),
        "expired": refs(("RULE-027", "/statement")),
    },
}


COMMON_ACTION_BINDINGS = {
    "retry": refs(("RULE-125", "/statement")),
    "cancel": refs(("RULE-122", "/statement")),
    "back": refs(("RULE-122", "/statement")),
    "refresh": refs(("RULE-123", "/statement")),
    "duplicate_concurrent_action": refs(("RULE-125", "/statement")),
    "timeout": refs(("RULE-125", "/statement")),
    "offline": refs(("RULE-125", "/statement")),
    "undo": refs(("RULE-124", "/statement")),
}


def action_refs(**overrides):
    result = dict(COMMON_ACTION_BINDINGS)
    result.update(overrides)
    return result


ACTION_BINDINGS = {
    ("SCR-006", "send_review_request"): action_refs(
        entry=refs(("SCR-006", "/major_actions")),
        precondition=refs(("RULE-046", "/statement"), ("RULE-129", "/statement")),
        input=refs(("DATA-009", "/purpose")),
        validation=refs(("RULE-046", "/statement")),
        submit=refs(("FLOW-005", "/paths")),
        success=refs(("FLOW-005", "/outcomes/0"), ("STATE-002", "/conditions/1")),
        failure=refs(("RULE-128", "/statement")),
        permission=refs(("RULE-129", "/statement")),
        session_expiration=refs(("RULE-110", "/statement")),
        data_mutation=refs(("DATA-009", "/purpose")),
        side_effect=refs(("DATA-009", "/purpose")),
        notification=refs(("INT-001", "/purpose")),
        persistence=refs(("DATA-004", "/purpose"), ("DATA-009", "/purpose")),
    ),
    ("SCR-006", "revoke_review_link"): action_refs(
        entry=refs(("SCR-006", "/major_actions")),
        precondition=refs(("RULE-033", "/statement"), ("RULE-129", "/statement")),
        input=refs(("DATA-004", "/purpose")),
        validation=refs(("DATA-004", "/purpose")),
        submit=refs(("FLOW-005", "/paths")),
        success=refs(("FLOW-005", "/outcomes/1"), ("STATE-002", "/conditions/1")),
        failure=refs(("RULE-128", "/statement")),
        permission=refs(("RULE-129", "/statement")),
        session_expiration=refs(("RULE-110", "/statement")),
        data_mutation=refs(("DATA-004", "/purpose")),
        side_effect=refs(("DATA-004", "/purpose")),
        notification=None,
        persistence=refs(("DATA-004", "/purpose")),
    ),
    ("SCR-006", "resend_review_request"): action_refs(
        entry=refs(("SCR-006", "/major_actions")),
        precondition=refs(("FLOW-005", "/preconditions"), ("RULE-129", "/statement")),
        input=refs(("DATA-009", "/purpose")),
        validation=refs(("DATA-009", "/purpose")),
        submit=refs(("FLOW-005", "/paths")),
        success=refs(("FLOW-005", "/outcomes/2"), ("STATE-002", "/conditions/1")),
        failure=refs(("RULE-128", "/statement")),
        permission=refs(("RULE-129", "/statement")),
        session_expiration=refs(("RULE-110", "/statement")),
        data_mutation=refs(("DATA-009", "/purpose")),
        side_effect=refs(("DATA-009", "/purpose")),
        notification=refs(("INT-001", "/purpose")),
        persistence=refs(("DATA-009", "/purpose")),
    ),
    ("SCR-007", "create_pin"): action_refs(
        entry=refs(("SCR-007", "/major_actions")),
        precondition=refs(("FLOW-006", "/preconditions"), ("RULE-020", "/statement")),
        input=refs(("DATA-002", "/purpose")),
        validation=refs(("RULE-014", "/statement"), ("RULE-015", "/statement")),
        submit=refs(("FLOW-006", "/paths")),
        success=refs(("FLOW-006", "/outcomes/0"), ("STATE-002", "/conditions/1")),
        failure=refs(("RULE-128", "/statement")),
        permission=refs(("RULE-020", "/statement")),
        session_expiration=refs(("RULE-130", "/statement"), ("RULE-027", "/statement")),
        data_mutation=refs(("DATA-002", "/purpose")),
        side_effect=refs(("DATA-007", "/purpose")),
        notification=refs(("INT-001", "/purpose")),
        persistence=refs(("DATA-002", "/purpose")),
    ),
    ("SCR-007", "reply_thread"): action_refs(
        entry=refs(("SCR-007", "/major_actions")),
        precondition=refs(("FLOW-006", "/preconditions"), ("RULE-020", "/statement")),
        input=refs(("DATA-002", "/purpose")),
        validation=refs(("RULE-020", "/statement"), ("RULE-063", "/statement")),
        submit=refs(("FLOW-006", "/paths")),
        success=refs(("FLOW-006", "/outcomes/1"), ("STATE-002", "/conditions/1")),
        failure=refs(("RULE-128", "/statement")),
        permission=refs(("RULE-020", "/statement")),
        session_expiration=refs(("RULE-130", "/statement"), ("RULE-027", "/statement")),
        data_mutation=refs(("DATA-002", "/purpose")),
        side_effect=refs(("DATA-008", "/purpose")),
        notification=refs(("INT-001", "/purpose")),
        persistence=refs(("DATA-002", "/purpose")),
    ),
    ("SCR-007", "resolve_thread"): action_refs(
        entry=refs(("SCR-007", "/major_actions")),
        precondition=refs(("FLOW-006", "/preconditions"), ("RULE-021", "/statement")),
        input=refs(("DATA-002", "/purpose")),
        validation=refs(("RULE-021", "/statement")),
        submit=refs(("FLOW-006", "/paths")),
        success=refs(("FLOW-006", "/outcomes/2"), ("STATE-002", "/conditions/1")),
        failure=refs(("RULE-128", "/statement"), ("RULE-084", "/statement")),
        permission=refs(("RULE-021", "/statement")),
        session_expiration=refs(("RULE-130", "/statement"), ("RULE-027", "/statement")),
        data_mutation=refs(("DATA-002", "/purpose")),
        side_effect=refs(("DATA-002", "/purpose")),
        notification=None,
        persistence=refs(("DATA-002", "/purpose")),
    ),
}

NA_ACTION_BASIS = {
    (screen_id, action_name, axis): refs((evidence_id, "/claim"))
    for (screen_id, action_name), axes in ACTION_BINDINGS.items()
    for axis, evidence_id in (
        ("destructive_confirmation", "EVD-015"),
        *((("notification", "EVD-014"),) if axes["notification"] is None else ()),
    )
}

ACTION_AXES = {
    "entry", "precondition", "input", "validation", "submit", "success", "failure",
    "retry", "cancel", "back", "refresh", "duplicate_concurrent_action", "timeout",
    "offline", "permission", "session_expiration", "data_mutation", "side_effect",
    "notification", "persistence", "undo", "destructive_confirmation",
}

EXPECTED_CONTINUATION_EVIDENCE = {
    "DEC-042": ["EVD-015"], "UNK-050": ["EVD-015"],
    "STATE-002": ["EVD-015"], "DATA-009": ["EVD-011"],
    "RULE-014": ["EVD-009", "EVD-016"], "RULE-015": ["EVD-016"],
    "RULE-027": ["EVD-002", "EVD-016"], "RULE-063": ["EVD-012", "EVD-016"],
    "RULE-077": ["EVD-016"], "RULE-110": ["EVD-016"],
    "RULE-119": ["EVD-015"], "RULE-120": ["EVD-015"],
    "RULE-122": ["EVD-015"], "RULE-123": ["EVD-015"],
    "RULE-124": ["EVD-015"], "RULE-125": ["EVD-015"],
    "RULE-128": ["EVD-016"], "RULE-129": ["EVD-006", "EVD-016"],
    "RULE-130": ["EVD-006", "EVD-016"],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def legacy_ids(state):
    return sorted(
        record["id"]
        for records in state["objects"].values()
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    )


def statuses(value):
    if isinstance(value, dict):
        if isinstance(value.get("status"), str):
            yield value["status"]
        for child in value.values():
            yield from statuses(child)
    elif isinstance(value, list):
        for child in value:
            yield from statuses(child)


def screen_coverage(state, screen_id):
    return next(item for item in state["ux_coverage"] if item["screen_id"] == screen_id)


def action_coverage(screen, action_name):
    return next(item for item in screen["actions"] if item["key"] == action_name)


def binding_pairs(cell, key):
    return [(item["record_id"], item["pointer"]) for item in cell[key]]


def semantic_correspondence_errors(state):
    errors = []
    index = canonical_record_index(state)
    for screen_id, expected_states in STATE_BINDINGS.items():
        screen = screen_coverage(state, screen_id)
        if set(screen["states"]) != set(expected_states):
            errors.append(f"{screen_id} state inventory differs")
        for state_name, expected_pairs in expected_states.items():
            cell = screen["states"][state_name]
            if cell["status"] != "COVERED":
                errors.append(f"{screen_id}.{state_name} must be COVERED")
                continue
            actual_pairs = binding_pairs(cell, "authority_bindings")
            if actual_pairs != expected_pairs:
                errors.append(f"{screen_id}.{state_name} authority differs")
            if cell["basis_bindings"] or cell["unknown_refs"]:
                errors.append(f"{screen_id}.{state_name} has foreign basis/unknowns")
            for binding in cell["authority_bindings"]:
                pair = (binding["record_id"], binding["pointer"])
                if pair not in EXPECTED_MEANINGS:
                    errors.append(f"{screen_id}.{state_name} has no hand-derived meaning for {pair}")
                    continue
                expected_value = EXPECTED_MEANINGS[pair]
                try:
                    actual_value = resolve_record_pointer(index[pair[0]][1], pair[1])
                except (KeyError, ValueError, TypeError) as exc:
                    errors.append(f"{screen_id}.{state_name} cannot resolve {pair}: {exc}")
                    continue
                if actual_value != expected_value:
                    errors.append(f"{screen_id}.{state_name} meaning differs for {pair}")
                if binding["value_sha256"] != sha256_json(expected_value):
                    errors.append(f"{screen_id}.{state_name} digest differs for {pair}")

    for (screen_id, action_name), expected_axes in ACTION_BINDINGS.items():
        action = action_coverage(screen_coverage(state, screen_id), action_name)
        if set(action["cells"]) != ACTION_AXES:
            errors.append(f"{screen_id}.{action_name} axis inventory differs")
        for axis in sorted(ACTION_AXES):
            cell = action["cells"][axis]
            na_key = (screen_id, action_name, axis)
            if na_key in NA_ACTION_BASIS:
                if cell["status"] != "N/A":
                    errors.append(f"{screen_id}.{action_name}.{axis} must be N/A")
                    continue
                if cell["authority_bindings"] or cell["unknown_refs"]:
                    errors.append(f"{screen_id}.{action_name}.{axis} has authority/unknowns")
                if binding_pairs(cell, "basis_bindings") != NA_ACTION_BASIS[na_key]:
                    errors.append(f"{screen_id}.{action_name}.{axis} basis differs")
                expected_bindings = cell["basis_bindings"]
            else:
                expected_pairs = expected_axes[axis]
                if cell["status"] != "COVERED":
                    errors.append(f"{screen_id}.{action_name}.{axis} must be COVERED")
                    continue
                if binding_pairs(cell, "authority_bindings") != expected_pairs:
                    errors.append(f"{screen_id}.{action_name}.{axis} authority differs")
                if cell["basis_bindings"] or cell["unknown_refs"]:
                    errors.append(f"{screen_id}.{action_name}.{axis} has foreign basis/unknowns")
                expected_bindings = cell["authority_bindings"]
            for binding in expected_bindings:
                pair = (binding["record_id"], binding["pointer"])
                if pair not in EXPECTED_MEANINGS:
                    errors.append(f"{screen_id}.{action_name}.{axis} has no hand-derived meaning for {pair}")
                    continue
                expected_value = EXPECTED_MEANINGS[pair]
                try:
                    actual_value = resolve_record_pointer(index[pair[0]][1], pair[1])
                except (KeyError, ValueError, TypeError) as exc:
                    errors.append(f"{screen_id}.{action_name}.{axis} cannot resolve {pair}: {exc}")
                    continue
                if actual_value != expected_value:
                    errors.append(f"{screen_id}.{action_name}.{axis} meaning differs for {pair}")
                if binding["value_sha256"] != sha256_json(expected_value):
                    errors.append(f"{screen_id}.{action_name}.{axis} digest differs for {pair}")
    return errors


class CoreSemanticClosureV2M6DogfoodPhaseATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legacy = load_json(LEGACY_ROOT / "state.json")
        cls.migrated = load_json(MIGRATION_CANDIDATE_PATH)
        cls.receipt = load_json(MIGRATION_RECEIPT_PATH)

    def test_track_a_artifacts_exist(self):
        required = (
            EVAL_ROOT / "README.md",
            EVAL_ROOT / "MIGRATION_AUDIT.md",
            MIGRATION_CANDIDATE_PATH,
            MIGRATION_RECEIPT_PATH,
        )
        self.assertEqual([path for path in required if not path.is_file()], [])

    def test_track_a_is_the_complete_open_unapproved_migration_audit(self):
        fresh_candidate, fresh_receipt = migrate_state_v020(self.legacy)

        self.assertEqual(self.migrated, fresh_candidate)
        self.assertEqual(self.receipt, fresh_receipt)
        self.assertEqual(
            verify_migration_result(self.legacy, self.migrated, self.receipt), []
        )
        self.assertEqual(self.migrated["project"]["definition_status"], "OPEN")
        self.assertEqual(self.migrated["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(self.migrated["approval_history"], [])
        self.assertEqual(
            self.migrated["migration"]["preserved_ids"], legacy_ids(self.legacy)
        )
        self.assertNotIn(
            "COVERED",
            set(
                statuses(
                    {
                        "coverage": self.migrated["coverage"],
                        "ux_coverage": self.migrated["ux_coverage"],
                        "grill_coverage": self.migrated["grill_coverage"],
                    }
                )
            ),
        )
        self.assertIsNotNone(
            self.migrated["migration"]["source_legacy_approval_digest"]
        )
        self.assertTrue(self.migrated["migration"]["reconciliation_gaps"])
        self.assertTrue(
            all(
                isinstance(gap["source_path"], str) and gap["source_path"]
                for gap in self.migrated["migration"]["reconciliation_gaps"].values()
            )
        )
        for unknown in self.migrated["objects"]["unknowns"]:
            if unknown.get("origin", {}).get("kind") == "MIGRATION_RECONCILIATION":
                self.assertTrue(unknown["origin"]["source_path"])


class CoreSemanticClosureV2M6DogfoodTrackBTest(unittest.TestCase):
    def test_exact_field_level_semantic_correspondence_and_mutations(self):
        self.assertTrue(STATE_PATH.is_file(), "approved decisions must recreate Track B")
        state = load_json(STATE_PATH)
        self.assertEqual(semantic_correspondence_errors(state), [])

        wrong_pointer = deepcopy(state)
        loading = screen_coverage(wrong_pointer, "SCR-006")["states"]["loading"]
        loading["authority_bindings"][0]["pointer"] = "/state_name"
        loading["authority_bindings"][0]["value_sha256"] = sha256_json("Bounded interaction state")
        self.assertTrue(semantic_correspondence_errors(wrong_pointer))

        wrong_value = deepcopy(state)
        index = canonical_record_index(wrong_value)
        index["STATE-002"][1]["conditions"][0] = "Pending."
        for screen in wrong_value["ux_coverage"]:
            for cell in screen["states"].values():
                for binding in cell["authority_bindings"]:
                    if binding["record_id"] == "STATE-002" and binding["pointer"] == "/conditions/0":
                        binding["value_sha256"] = sha256_json("Pending.")
            for action in screen["actions"]:
                for cell in action["cells"].values():
                    for binding in cell["authority_bindings"]:
                        if binding["record_id"] == "STATE-002" and binding["pointer"] == "/conditions/0":
                            binding["value_sha256"] = sha256_json("Pending.")
        self.assertTrue(semantic_correspondence_errors(wrong_value))

    def test_checkpoint_is_ready_unapproved_and_deterministic(self):
        required = (STATE_PATH, MANIFEST_PATH, EVIDENCE_MAP_PATH, RUNBOOK_PATH)
        self.assertEqual([path for path in required if not path.is_file()], [])
        state = load_json(STATE_PATH)
        manifest = load_json(MANIFEST_PATH)
        self.assertEqual(state["project"]["definition_status"], "READY_FOR_REVIEW")
        self.assertEqual(state["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(state["approval_history"], [])
        self.assertEqual(validate_state_v2(state), [])
        self.assertEqual(sum(semantic_readiness_metrics(state).values()), 0)
        self.assertEqual(build_approval_manifest_for_review(state), manifest)
        self.assertEqual(definition_digest(state), EXPECTED_DEFINITION_DIGEST)
        self.assertEqual(approval_manifest_digest(manifest), EXPECTED_MANIFEST_DIGEST)
        self.assertEqual(len(manifest["added"]), EXPECTED_ADDED_COUNT)
        self.assertEqual(manifest["changed"], [])
        self.assertEqual(manifest["superseded"], [])
        self.assertEqual(manifest["retired"], [])
        serialized = json.dumps(state, ensure_ascii=False)
        for forbidden in ("approved_by", "approved_at", "timestamp"):
            self.assertNotIn(forbidden, serialized)

        evidence = {item["id"]: item for item in state["evidence"]}
        self.assertEqual(evidence["EVD-008"]["claim"], ANALYTICS_DECISION)
        self.assertEqual(evidence["EVD-015"]["claim"], INTERACTION_DECISION)
        evidence_map = load_json(EVIDENCE_MAP_PATH)["record_evidence"]
        current_ids = {
            record["id"]
            for records in state["objects"].values()
            for record in records
            if record.get("status") == "CURRENT"
        }
        all_object_ids = {
            record["id"] for records in state["objects"].values() for record in records
        }
        self.assertLessEqual(current_ids, set(evidence_map))
        self.assertLessEqual(set(evidence_map), all_object_ids)
        for record_id, expected_refs in EXPECTED_CONTINUATION_EVIDENCE.items():
            self.assertEqual(evidence_map[record_id], expected_refs)
        docs = README_PATH.read_text(encoding="utf-8") + RUNBOOK_PATH.read_text(encoding="utf-8")
        self.assertIn("READY_FOR_REVIEW", docs)
        self.assertIn("UNAPPROVED", docs)
        self.assertNotIn("NEEDS_CONTEXT", docs)


if __name__ == "__main__":
    unittest.main()
