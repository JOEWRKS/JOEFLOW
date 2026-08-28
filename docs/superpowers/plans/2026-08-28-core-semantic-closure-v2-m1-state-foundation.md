# Core Semantic Closure V2 — M1 State 0.2 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the parallel `state.json` 0.2.0 foundation, deterministic version dispatch, typed semantic minima, lifecycle/ID rules, and a deterministic migration-planning entrypoint without changing or weakening the frozen legacy 0.1.2.1 contract.

**Architecture:** Keep the existing 0.1.2.1 schema, validator core, state-contract reference, and legacy example byte-identical. Add a separate V2 validation backend and version dispatcher; the two existing CLI entrypoints become thin routers. M1 accepts structurally valid 0.2.0 foundation states but deliberately refuses to claim V2 Semantic Closure until M2–M4 add discovery, Grill, coverage-binding, and informed-approval semantics. Migration in M1 is a deterministic read-only planning interface, not a completed 0.1.2.1→0.2.0 semantic conversion.

**Tech Stack:** Python 3 standard library, JSON, JSON Schema documents, `unittest`, SHA-1 Git-blob commitments for frozen legacy bytes, SHA-256 canonical JSON commitments for migration planning.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-self-review.md`

## Global Constraints

- Start implementation from exact design-freeze history at or after commit `26f1c0514206764e684799a5dbe1b3ec5ba1aa53`; create an implementation branch/worktree instead of writing implementation code directly on the design branch.
- Preserve these legacy contract files byte-for-byte throughout M1:
  - `skills/joewrks-product-definition/schemas/state.schema.json` — Git blob `6a03894cc2164a9bfabbe8627a8468124d19b1f7`
  - `skills/joewrks-product-definition/scripts/state_validation.py` — Git blob `9a3b44359bddfd64c98392f235cb815a0b777cce`
  - `skills/joewrks-product-definition/references/state-contract.md` — Git blob `05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf`
  - `skills/joewrks-product-definition/templates/state.example.json` — Git blob `5fed7e87da243b3d234148bbbbf3baf7350d8ab0`
- `validate_state.py` and `validate_closure.py` may change only into version-aware wrappers; legacy 0.1.2.1 behavior remains delegated to the frozen `state_validation.py` implementation.
- Do not modify `joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, semantic-review v0.4.3 calibration evidence, or any frozen downstream v1 artifact.
- M1 does not implement Product Surface semantics, Evidence authority classes, Grill Pack activation, Coverage→Authority Binding, Approval Manifest semantics, or downstream 2.0. Those are M2–M5 responsibilities.
- A 0.2.0 state must never return `closed: true` during M1. Use the explicit closure metric `semantic_closure_not_implemented = 1` until the later semantic-closure milestones replace that guard.
- Do not create a provisional V2 definition digest in M1. `definition_digest` for V2 closure evaluation is JSON `null` until M4 defines the approved semantic digest boundary.
- V2 IDs use `^[A-Z]+-[0-9]{3,}$`; existing IDs are never renumbered.
- Canonical migration output must contain no current-time field. Same legacy semantic input plus the same migration version must produce byte-identical migration-plan JSON.
- Every production-code behavior change follows RED → GREEN → refactor. Characterization/freeze tests are allowed to start GREEN because their purpose is to pin existing bytes/behavior.
- No milestone status may say `Core V2 complete`; the strongest successful M1 status is `IMPLEMENTED_M1 / NOT_INTEGRATED`.

---

## File map locked by this plan

### New runtime/validator files

- `skills/joewrks-product-definition/scripts/state_contract_dispatch.py` — schema-version routing only.
- `skills/joewrks-product-definition/scripts/state_validation_v2.py` — V2 structural/typed/lifecycle validation plus the M1 closure guard.
- `skills/joewrks-product-definition/scripts/migration_v2.py` — deterministic migration-plan primitives.
- `skills/joewrks-product-definition/scripts/migrate_state.py` — CLI exposing only the M1 `--plan` operation.

### New contract/docs/template files

- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json` — V2 structural schema; never replaces legacy `state.schema.json`.
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json` — native OPEN V2 foundation example.
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md` — M1 foundation contract and explicit partial-status boundary.

### Modified wrappers only

- `skills/joewrks-product-definition/scripts/validate_state.py`
- `skills/joewrks-product-definition/scripts/validate_closure.py`

### New tests/support

- `tests/v020_support.py` — reusable literal V2 foundation state builders; no production helpers.
- `tests/test_legacy_v0121_frozen.py` — byte and behavior characterization.
- `tests/test_state_contract_dispatch.py` — CLI/backend routing.
- `tests/test_state_v020_foundation.py` — V2 shape, typed minima, IDs, lifecycle, and closure guard.
- `tests/test_migration_v020_foundation.py` — source validation, deterministic plan, generated-ID allocation.

---

### Task 1: Freeze legacy 0.1.2.1 bytes and introduce version dispatch

**Files:**
- Create: `tests/test_legacy_v0121_frozen.py`
- Create: `tests/test_state_contract_dispatch.py`
- Create: `skills/joewrks-product-definition/scripts/state_contract_dispatch.py`
- Modify: `skills/joewrks-product-definition/scripts/validate_state.py`
- Modify: `skills/joewrks-product-definition/scripts/validate_closure.py`

**Interfaces:**
- Consumes: frozen legacy `state_validation.validate_state`, `state_validation.closure_metrics`, `state_validation.definition_digest`, `state_validation.load_state`.
- Produces:
  - `validate_state_for_version(state: dict[str, object]) -> list[dict[str, str]]`
  - `evaluate_closure_for_version(state: dict[str, object]) -> dict[str, object]`
- Unsupported versions return one stable error with code `unsupported_schema_version`; they never fall back to the newest schema.

- [ ] **Step 1: Add byte-freeze characterization tests for legacy authorities**

Create `tests/test_legacy_v0121_frozen.py` with this helper and exact commitments:

```python
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FROZEN = {
    "skills/joewrks-product-definition/schemas/state.schema.json": "6a03894cc2164a9bfabbe8627a8468124d19b1f7",
    "skills/joewrks-product-definition/scripts/state_validation.py": "9a3b44359bddfd64c98392f235cb815a0b777cce",
    "skills/joewrks-product-definition/references/state-contract.md": "05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf",
    "skills/joewrks-product-definition/templates/state.example.json": "5fed7e87da243b3d234148bbbbf3baf7350d8ab0",
}


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class LegacyV0121FrozenTest(unittest.TestCase):
    def test_frozen_legacy_contract_bytes(self):
        for relative, expected in FROZEN.items():
            with self.subTest(relative=relative):
                self.assertEqual(git_blob_sha1((ROOT / relative).read_bytes()), expected)
```

- [ ] **Step 2: Run the freeze test and verify the baseline is GREEN before implementation**

Run:

```bash
python -m unittest tests.test_legacy_v0121_frozen -v
```

Expected: `OK`. If it fails before M1 code changes, stop; the implementation base does not match the frozen design authority.

- [ ] **Step 3: Add dispatch RED tests without importing production V2 helpers**

In `tests/test_state_contract_dispatch.py`, use subprocess calls to the existing CLI wrappers. Reuse `closed_state()` from `tests.test_validators` for 0.1.2.1 and assert:

```python
legacy_state_code == 0
legacy_state_payload["valid"] is True
legacy_closure_code == 0
legacy_closure_payload["closed"] is True
```

Add an unsupported-version case by changing `schema_version` to `"9.9.9"` and assert both CLIs exit `1`, with `unsupported_schema_version` present in the state-validator errors and closure-validator errors.

- [ ] **Step 4: Run dispatch tests and verify RED**

Run:

```bash
python -m unittest tests.test_state_contract_dispatch -v
```

Expected: FAIL because the current wrappers hard-code the legacy validator and do not expose `unsupported_schema_version` dispatch semantics.

- [ ] **Step 5: Implement `state_contract_dispatch.py` with lazy V2 loading**

Use this exact public surface:

```python
from __future__ import annotations

from typing import Any

import state_validation as legacy

LEGACY_VERSION = "0.1.2.1"
V2_VERSION = "0.2.0"
SUPPORTED_SCHEMA_VERSIONS = (LEGACY_VERSION, V2_VERSION)


def _unsupported(version: Any) -> dict[str, str]:
    return {
        "code": "unsupported_schema_version",
        "message": f"unsupported schema_version {version!r}",
        "path": "schema_version",
    }


def validate_state_for_version(state: dict[str, Any]) -> list[dict[str, str]]:
    version = state.get("schema_version")
    if version == LEGACY_VERSION:
        return legacy.validate_state(state)
    if version == V2_VERSION:
        from state_validation_v2 import validate_state_v2
        return validate_state_v2(state)
    return [_unsupported(version)]


def evaluate_closure_for_version(state: dict[str, Any]) -> dict[str, Any]:
    version = state.get("schema_version")
    if version == LEGACY_VERSION:
        errors = legacy.validate_state(state)
        metrics = legacy.closure_metrics(state)
        return {
            "errors": errors,
            "metrics": metrics,
            "closed": not errors and all(value == 0 for value in metrics.values()),
            "definition_digest": legacy.definition_digest(state),
        }
    if version == V2_VERSION:
        from state_validation_v2 import evaluate_closure_v2
        return evaluate_closure_v2(state)
    return {
        "errors": [_unsupported(version)],
        "metrics": {},
        "closed": False,
        "definition_digest": None,
    }
```

At this task V2 import is deliberately lazy so legacy validation continues to work before Task 2 adds `state_validation_v2.py`.

- [ ] **Step 6: Convert both CLI scripts into thin dispatch wrappers**

`validate_state.py` keeps its current JSON output keys and exit-code contract but calls `validate_state_for_version(state)`.

`validate_closure.py` keeps its current JSON output keys and calls `evaluate_closure_for_version(state)`. Do not duplicate closure logic inside the CLI.

- [ ] **Step 7: Run legacy and dispatch tests GREEN**

Run:

```bash
python -m unittest tests.test_legacy_v0121_frozen tests.test_state_contract_dispatch tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`; no frozen-file hash changes and legacy 0.1.2.1 behavior remains green.

- [ ] **Step 8: Commit Task 1**

```bash
git add tests/test_legacy_v0121_frozen.py tests/test_state_contract_dispatch.py \
  skills/joewrks-product-definition/scripts/state_contract_dispatch.py \
  skills/joewrks-product-definition/scripts/validate_state.py \
  skills/joewrks-product-definition/scripts/validate_closure.py
git commit -m "refactor: dispatch product definition state contracts"
```

---

### Task 2: Add the V2 top-level contract and typed semantic foundation

**Files:**
- Create: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Create: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/v020_support.py`
- Create: `tests/test_state_v020_foundation.py`
- Modify: `skills/joewrks-product-definition/scripts/state_contract_dispatch.py` only if import/interface alignment is required; do not change the public names from Task 1.

**Interfaces:**
- Produces:
  - `validate_state_v2(state: dict[str, object]) -> list[dict[str, str]]`
  - `evaluate_closure_v2(state: dict[str, object]) -> dict[str, object]`
- V2 validation uses `schema_version == "0.2.0"`, `project.definition_status`, top-level `approval`, and all 13 typed object groups.
- M1 closure always returns `closed: false`, `definition_digest: None`, and metric `semantic_closure_not_implemented: 1` for a structurally valid V2 state.

- [ ] **Step 1: Create literal V2 test builders**

Create `tests/v020_support.py`. The native empty foundation state is exactly shaped like this:

```python
def materiality(*, classification="NON_MATERIAL"):
    return {
        "outcome_divergence": "LOW",
        "fan_out": "LOCAL",
        "user_visible": False,
        "reversibility": "TRIVIALLY_REVERSIBLE",
        "risk_flags": {
            "security": False,
            "privacy": False,
            "money": False,
            "legal_or_policy": False,
            "destructive": False,
            "data_loss": False,
            "external_commitment": False,
        },
        "classification": classification,
    }


def foundation_state():
    return {
        "schema_version": "0.2.0",
        "project": {
            "slug": "v2-foundation",
            "definition_status": "OPEN",
            "definition_revision": 1,
            "closure_contract": {"level": "SEMANTIC_CLOSURE"},
        },
        "migration": {"mode": "NATIVE"},
        "evidence": [],
        "surface_manifest": {"records": []},
        "contradictions": [],
        "objects": {
            "goals": [],
            "users": [],
            "requirements": [],
            "unknowns": [],
            "decisions": [],
            "rules": [],
            "flows": [],
            "screens": [],
            "states": [],
            "data": [],
            "integrations": [],
            "acceptance_criteria": [],
            "tasks": [],
        },
        "coverage": [],
        "ux_coverage": [],
        "discovery_baseline": {"status": "NOT_ESTABLISHED"},
        "approval": {"status": "UNAPPROVED"},
        "approval_history": [],
    }
```

This helper is test data only; production code must not import it.

- [ ] **Step 2: Write top-level V2 RED tests**

In `tests/test_state_v020_foundation.py`, assert:

1. `foundation_state()` returns state-validator exit `0` and `valid: true`.
2. Removing each required top-level field causes state-validator exit `1`.
3. `project.status` is rejected; V2 requires `project.definition_status`.
4. `user_approved` is rejected at the top-level/project contract; V2 approval is the single top-level `approval` object.
5. `schema_version: 0.2.0` is routed to V2 and not rejected as unsupported.
6. closure for `foundation_state()` exits `1`, returns `closed: false`, `definition_digest: null`, and `metrics.semantic_closure_not_implemented == 1`.

- [ ] **Step 3: Run only the new V2 tests and verify RED**

```bash
python -m unittest tests.test_state_v020_foundation -v
```

Expected: FAIL because `state_validation_v2.py` and the V2 schema do not exist.

- [ ] **Step 4: Create the V2 JSON Schema with final M1 top-level and typed-object names**

`state-v0.2.0.schema.json` must use Draft 2020-12 syntax and `additionalProperties: false` for the root, `project`, materiality objects, risk flags, and typed object definitions. Use ID pattern `^[A-Z]+-[0-9]{3,}$`.

The schema requires the exact top-level keys used by `foundation_state()`. The 13 object arrays bind to distinct `$defs` rather than one generic object definition.

The typed semantic minima are:

| Group | Required fields beyond `id`, `status` |
| --- | --- |
| goals | `statement` |
| users | `description`, `actor_kind` |
| requirements | `statement`, `scope`, `ui_required`, `materiality` |
| unknowns | `question`, `materiality`, `decision_authority` |
| decisions | `statement`, `decision_type`, `resolution_mode`, `decision_authority`, `source_unknown_refs`, `evidence_refs`, `materiality`, `affects` |
| rules | `statement`, `applies_to` |
| flows | `goal_refs`, `entry`, `preconditions`, `paths`, `outcomes` |
| screens | `purpose`, `requirement_refs`, `interaction_mode`, `major_actions` |
| states | `owner_refs`, `state_name`, `conditions` |
| data | `name`, `purpose`, `ownership` |
| integrations | `name`, `purpose` |
| acceptance_criteria | `requirement_refs`, `assertion` |
| tasks | `implements`, `acceptance_refs` |

Use non-empty strings (`minLength: 1`) for semantic text. Arrays that are semantic mappings (`goal_refs`, `requirement_refs`, `implements`, `acceptance_refs`, `applies_to`, `owner_refs`) use unique string items; `implements` and `acceptance_refs` require `minItems: 1`. `major_actions` may be empty because passive-screen semantics are tightened in later UX work.

`materiality` uses the exact final shape from the design:

```json
{
  "type": "object",
  "required": ["outcome_divergence", "fan_out", "user_visible", "reversibility", "risk_flags", "classification"],
  "properties": {
    "outcome_divergence": {"enum": ["NONE", "LOW", "MEDIUM", "HIGH"]},
    "fan_out": {"enum": ["LOCAL", "MULTI_OBJECT", "MULTI_FLOW", "SYSTEMIC"]},
    "user_visible": {"type": "boolean"},
    "reversibility": {"enum": ["TRIVIALLY_REVERSIBLE", "REVERSIBLE", "COSTLY_TO_REVERSE", "IRREVERSIBLE"]},
    "risk_flags": {
      "type": "object",
      "required": ["security", "privacy", "money", "legal_or_policy", "destructive", "data_loss", "external_commitment"],
      "properties": {
        "security": {"type": "boolean"},
        "privacy": {"type": "boolean"},
        "money": {"type": "boolean"},
        "legal_or_policy": {"type": "boolean"},
        "destructive": {"type": "boolean"},
        "data_loss": {"type": "boolean"},
        "external_commitment": {"type": "boolean"}
      },
      "additionalProperties": false
    },
    "classification": {"enum": ["MATERIAL", "NON_MATERIAL"]}
  },
  "additionalProperties": false
}
```

M1 validates this structure but does **not** yet recompute whether `classification` is correct; that semantic classifier belongs to M3.

- [ ] **Step 5: Implement `state_validation_v2.py` without importing the legacy validator as a fallback**

Use these stable constants and public functions:

```python
SCHEMA_VERSION = "0.2.0"
ID_RE = re.compile(r"^[A-Z]+-[0-9]{3,}$")
ARTIFACT_STATUSES = {"CURRENT", "STALE", "SUPERSEDED", "RETIRED"}
UNKNOWN_STATUSES = {"OPEN", "RESOLVED", "DEFERRED", "BLOCKED", "SUPERSEDED", "RETIRED"}
DEFINITION_STATUSES = {"OPEN", "READY_FOR_REVIEW", "CLOSED", "BLOCKED"}
DECISION_AUTHORITIES = {
    "EVIDENCE_RESOLVABLE",
    "AGENT_AUTONOMOUS",
    "USER_CONFIRMATION",
    "USER_DECISION_REQUIRED",
    "EXTERNAL_AUTHORITY_REQUIRED",
}
RESOLUTION_MODES = {
    "EVIDENCE",
    "USER_DECISION",
    "USER_ACCEPTED_RECOMMENDATION",
    "AGENT_NON_MATERIAL_DEFAULT",
    "EXTERNAL_CONSTRAINT",
    "MIGRATION_RECONCILIATION",
}


def validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]:
    ...


def evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]:
    errors = validate_state_v2(state)
    metrics = {"semantic_closure_not_implemented": 1}
    return {
        "errors": errors,
        "metrics": metrics,
        "closed": False,
        "definition_digest": None,
    }
```

Implementation must explicitly validate the top-level shape and typed semantic minima rather than silently delegating V2 to the legacy generic-object validator. Keep error objects in the existing `{code, message, path}` form.

- [ ] **Step 6: Run V2 top-level tests GREEN and legacy tests again**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_state_contract_dispatch tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`; V2 OPEN state is structurally valid but cannot close, and legacy remains unchanged.

- [ ] **Step 7: Commit Task 2**

```bash
git add tests/v020_support.py tests/test_state_v020_foundation.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/scripts/state_contract_dispatch.py
git commit -m "feat: add state 0.2 foundation contract"
```

---

### Task 3: Enforce V2 semantic minima, IDs, supersession, and retirement lifecycle

**Files:**
- Modify: `tests/test_state_v020_foundation.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`

**Interfaces:**
- Extends `validate_state_v2` only; no new public entrypoint.
- `CURRENT`, `STALE`, `SUPERSEDED`, and `RETIRED` semantics apply to normal authority records; unknowns keep the separate lifecycle in the design.

- [ ] **Step 1: Add RED tests for semantic-empty typed objects**

Add one subtest per object group that inserts the smallest `{id, status}` record and assert validation fails with `semantic_minimum_missing` or a schema-equivalent stable code. Then add one valid literal per group using these shapes:

```python
{"id":"GOAL-001","status":"CURRENT","statement":"Reduce failed onboarding."}
{"id":"USR-001","status":"CURRENT","description":"Workspace member","actor_kind":"END_USER"}
{"id":"REQ-001","status":"CURRENT","statement":"User can submit feedback.","scope":"IN_SCOPE","ui_required":True,"materiality":materiality(classification="MATERIAL")}
{"id":"UNK-001","status":"OPEN","question":"Who may submit?","materiality":materiality(classification="MATERIAL"),"decision_authority":"USER_DECISION_REQUIRED"}
{"id":"DEC-001","status":"CURRENT","statement":"Members may submit feedback.","decision_type":"PRODUCT_POLICY","resolution_mode":"USER_DECISION","decision_authority":"USER_DECISION_REQUIRED","source_unknown_refs":["UNK-001"],"evidence_refs":[],"materiality":materiality(classification="MATERIAL"),"affects":["REQ-001"]}
{"id":"RULE-001","status":"CURRENT","statement":"Only members may submit.","applies_to":["REQ-001"]}
{"id":"FLOW-001","status":"CURRENT","goal_refs":["GOAL-001"],"entry":"Feedback page","preconditions":["Authenticated"],"paths":["submit"],"outcomes":{"success":"saved"}}
{"id":"SCR-001","status":"CURRENT","purpose":"Collect feedback","requirement_refs":["REQ-001"],"interaction_mode":"INTERACTIVE","major_actions":["submit"]}
{"id":"STATE-001","status":"CURRENT","owner_refs":["SCR-001"],"state_name":"submitting","conditions":["request pending"]}
{"id":"DATA-001","status":"CURRENT","name":"feedback","purpose":"Store feedback","ownership":"workspace"}
{"id":"INT-001","status":"CURRENT","name":"mail","purpose":"Send feedback notifications"}
{"id":"AC-001","status":"CURRENT","requirement_refs":["REQ-001"],"assertion":"Valid feedback is persisted once."}
{"id":"TASK-001","status":"CURRENT","implements":["REQ-001"],"acceptance_refs":["AC-001"]}
```

M1 requires semantic presence and local shape, not the later R1/R3/R4 cross-authority proofs.

- [ ] **Step 2: Add RED tests for 3+ digit IDs and global uniqueness**

Assert:

```text
REQ-001   valid
REQ-999   valid
REQ-1000  valid
REQ-01    invalid
REQ-A01   invalid
```

Also assert duplicate IDs across object groups fail. Reserve global collision checks across `evidence` and `surface_manifest.records` when those entries contain an `id`; M2 will add their full semantic schemas.

- [ ] **Step 3: Add RED tests for supersession and retirement**

Required cases:

- `SUPERSEDED` without `superseded_by` fails.
- superseding self fails.
- same-prefix supersession cycles fail.
- cross-type supersession fails.
- `RETIRED` without all of `retired_by`, `retired_at_revision`, `retirement_reason` fails.
- each `retired_by` target must exist and be `DEC-*`.
- `retired_at_revision` must be a positive integer not greater than the current `definition_revision`.
- retirement does not mutate or auto-retire dependents; validation reports them as they are and later propagation logic owns stale reconciliation.

- [ ] **Step 4: Run the new lifecycle/minimum tests and verify RED**

```bash
python -m unittest tests.test_state_v020_foundation -v
```

Expected: new cases fail until V2 validator/schema rules are implemented.

- [ ] **Step 5: Implement typed minima and lifecycle validation in focused helpers**

Keep `state_validation_v2.py` readable by splitting internal concerns into helpers with these names:

```python
def _validate_top_level(state: dict[str, Any]) -> list[dict[str, str]]: ...
def _iter_records(state: dict[str, Any]): ...
def _collect_ids(state: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]: ...
def _validate_typed_semantic_minima(state: dict[str, Any]) -> list[dict[str, str]]: ...
def _validate_lifecycle(state: dict[str, Any], index: dict[str, dict[str, Any]]) -> list[dict[str, str]]: ...
def _validate_supersession_cycles(index: dict[str, dict[str, Any]]) -> list[dict[str, str]]: ...
```

Do not fold M3 materiality-classification logic or M4 coverage-binding logic into these helpers.

- [ ] **Step 6: Run focused and legacy regression tests GREEN**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`.

- [ ] **Step 7: Commit Task 3**

```bash
git add tests/test_state_v020_foundation.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json
git commit -m "feat: enforce state 0.2 typed authority lifecycle"
```

---

### Task 4: Add deterministic migration-planning foundation

**Files:**
- Create: `skills/joewrks-product-definition/scripts/migration_v2.py`
- Create: `skills/joewrks-product-definition/scripts/migrate_state.py`
- Create: `tests/test_migration_v020_foundation.py`

**Interfaces:**
- Produces:
  - `class MigrationError(ValueError)` with `.code` and `.detail`.
  - `canonical_json_bytes(value: object) -> bytes`
  - `allocate_generated_ids(prefix: str, existing_ids: set[str], canonical_paths: list[str]) -> dict[str, str]`
  - `build_migration_plan(state: dict[str, object]) -> dict[str, object]`
- CLI supported in M1:

```text
python skills/joewrks-product-definition/scripts/migrate_state.py --plan SOURCE_JSON
```

- M1 CLI output is a migration **plan**, not a migrated V2 state. It declares `status: FOUNDATION_PLAN_ONLY` so no caller can confuse M1 with the complete M6 migration.

- [ ] **Step 1: Add RED source-validation and deterministic-output tests**

In `tests/test_migration_v020_foundation.py` assert:

1. `closed_state()` from the legacy tests is accepted as a migration-plan source.
2. a legacy state with a broken reference raises/emits `MIGRATION_SOURCE_INVALID`.
3. a source with `schema_version: 0.2.0` is rejected because this migration path is specifically 0.1.2.1→0.2.0.
4. invoking `migrate_state.py --plan` twice on byte-identical source emits byte-identical stdout.
5. plan JSON contains no `migrated_at`, `created_at`, or current-time-derived field.
6. source plan includes exact `from_schema: "0.1.2.1"`, `to_schema: "0.2.0"`, and `migration_version: "0.2.0-foundation.1"`.

- [ ] **Step 2: Add RED generated-ID tests for the approved self-review rule**

Use:

```python
existing = {"UNK-001", "UNK-007", "UNK-103"}
paths = ["/coverage/REQ-002/security", "/coverage/REQ-001/actor", "/coverage/REQ-001/security"]
```

Assert the returned mapping, sorted by canonical path, is:

```python
{
    "/coverage/REQ-001/actor": "UNK-104",
    "/coverage/REQ-001/security": "UNK-105",
    "/coverage/REQ-002/security": "UNK-106",
}
```

Also assert `REQ-999` plus one generated REQ path becomes `REQ-1000`, proving the 3+ digit rule.

- [ ] **Step 3: Add RED reconciliation-site enumeration tests**

For each legacy coverage/UX cell, the migration plan classifies unresolved V2 proof needs without inventing bindings:

```text
legacy COVERED → COVERED_BINDING_REQUIRED
legacy N/A     → NA_BASIS_BINDING_REQUIRED
legacy OPEN    → OPEN_UNKNOWN_BINDING_REQUIRED
```

The plan contains canonical paths and generated `UNK-*` IDs but does not claim those unknowns are resolved.

- [ ] **Step 4: Run migration tests RED**

```bash
python -m unittest tests.test_migration_v020_foundation -v
```

Expected: FAIL because the migration modules do not exist.

- [ ] **Step 5: Implement `migration_v2.py` using the frozen legacy validator as the source authority**

Use these constants and error shape:

```python
MIGRATION_VERSION = "0.2.0-foundation.1"
FROM_SCHEMA = "0.1.2.1"
TO_SCHEMA = "0.2.0"

class MigrationError(ValueError):
    def __init__(self, code: str, detail: object = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}: {detail}")
```

`build_migration_plan()` must call the frozen `state_validation.validate_state(state)` and reject any error as `MIGRATION_SOURCE_INVALID`. Compute `source_digest` as SHA-256 of canonical sorted compact UTF-8 JSON, not wall-clock metadata.

Plan output has this exact root contract:

```python
{
    "schema_version": "joewrks.state-migration-plan/1.0",
    "status": "FOUNDATION_PLAN_ONLY",
    "from_schema": "0.1.2.1",
    "to_schema": "0.2.0",
    "migration_version": "0.2.0-foundation.1",
    "source_digest": "<sha256>",
    "preserved_ids": [...],
    "reconciliation_sites": [...],
}
```

`preserved_ids` is sorted lexicographically. `reconciliation_sites` is sorted by canonical source path. Generated IDs use the approved max-existing-plus-one rule.

- [ ] **Step 6: Implement `migrate_state.py --plan` as a thin JSON CLI**

On success: exit `0`, print deterministic JSON using `sort_keys=True`, `ensure_ascii=False`, `separators=(",", ":")`, followed by one newline.

On source failure: exit `1` and print:

```json
{"error":{"code":"MIGRATION_SOURCE_INVALID","detail":...}}
```

Argument/IO failures exit `2`. Do not provide an in-place mutation flag in M1.

- [ ] **Step 7: Run migration and legacy tests GREEN**

```bash
python -m unittest tests.test_migration_v020_foundation tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK` and the legacy byte-freeze test remains unchanged.

- [ ] **Step 8: Commit Task 4**

```bash
git add skills/joewrks-product-definition/scripts/migration_v2.py \
  skills/joewrks-product-definition/scripts/migrate_state.py \
  tests/test_migration_v020_foundation.py
git commit -m "feat: add deterministic state 0.2 migration planner"
```

---

### Task 5: Document the M1 contract, add the V2 native example, and run the milestone gate

**Files:**
- Create: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Create: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- Modify: `tests/test_state_v020_foundation.py`
- Do not modify: `README.md`, `SKILL.md`, or the legacy state-contract/template in M1; V2 becomes the default user workflow only during M6 adoption.

**Interfaces:**
- The new reference describes exactly what M1 implements and explicitly states `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1`.
- The example is a native `OPEN` V2 state matching `foundation_state()` and state-validator success.

- [ ] **Step 1: Add RED documentation/fixture contract tests**

Extend `tests/test_state_v020_foundation.py` to assert:

```python
schema_path = ROOT / "skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json"
reference_path = ROOT / "skills/joewrks-product-definition/references/state-contract-v0.2.0.md"
template_path = ROOT / "skills/joewrks-product-definition/templates/state-v0.2.0.example.json"
```

Required assertions:

- all three files exist;
- schema const is `0.2.0`;
- template has `schema_version == "0.2.0"` and `approval.status == "UNAPPROVED"`;
- template passes the real state validator;
- template fails closure with `semantic_closure_not_implemented == 1`;
- reference contains the literal boundaries `LEGACY_CLOSURE`, `SEMANTIC_CLOSURE`, `FOUNDATION_PLAN_ONLY`, and `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1`.

- [ ] **Step 2: Run the focused test and verify RED**

```bash
python -m unittest tests.test_state_v020_foundation -v
```

Expected: FAIL because the reference/template files do not exist yet.

- [ ] **Step 3: Create the V2 native OPEN template**

Write `state-v0.2.0.example.json` with the same literal structure as `foundation_state()` and no product objects. It is intentionally OPEN and unapproved.

- [ ] **Step 4: Write `state-contract-v0.2.0.md` with the M1 boundary**

The reference must state all of the following explicitly:

```text
- state 0.2.0 is parallel to, not a replacement-in-place for, legacy 0.1.2.1.
- legacy 0.1.2.1 validation remains frozen.
- M1 validates V2 top-level shape, typed semantic minima, lifecycle, IDs, and migration planning.
- M1 does not claim V2 Semantic Closure.
- validate_closure on 0.2.0 returns semantic_closure_not_implemented = 1 and closed = false.
- migrate_state.py --plan emits FOUNDATION_PLAN_ONLY and never manufactures V2 authority.
- later milestones must replace the M1 closure guard only when their own gates are implemented and verified.
```

- [ ] **Step 5: Run all M1-focused tests GREEN**

```bash
python -m unittest \
  tests.test_legacy_v0121_frozen \
  tests.test_state_contract_dispatch \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation -v
```

Expected: `OK`.

- [ ] **Step 6: Run the full legacy regression cluster GREEN**

```bash
python -m unittest tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK` with no changed frozen legacy hashes.

- [ ] **Step 7: Run the complete repository suite**

```bash
python -m unittest discover -s tests -v
```

Expected: exit `0`, no failures or errors. No new skip is allowed; any pre-existing environment-dependent skip may remain only if its reason is unchanged.

- [ ] **Step 8: Run source-tree integrity checks**

```bash
git diff --check
python -m unittest tests.test_legacy_v0121_frozen -v
```

Expected: both exit `0`.

Then verify no files under these frozen areas changed from the M1 implementation base:

```text
skills/joewrks-product-definition/downstream/
evals/semantic-review-v0.4.3/
skills/joewrks-product-definition/schemas/state.schema.json
skills/joewrks-product-definition/scripts/state_validation.py
skills/joewrks-product-definition/references/state-contract.md
skills/joewrks-product-definition/templates/state.example.json
```

- [ ] **Step 9: Commit Task 5**

```bash
git add skills/joewrks-product-definition/references/state-contract-v0.2.0.md \
  skills/joewrks-product-definition/templates/state-v0.2.0.example.json \
  tests/test_state_v020_foundation.py
git commit -m "docs: define state 0.2 foundation boundary"
```

- [ ] **Step 10: Record M1 milestone result without overstating completion**

If and only if every gate above is green, report:

```text
CORE_SEMANTIC_CLOSURE_V2_M1_IMPLEMENTED
— STATE_0_2_FOUNDATION / NOT_INTEGRATED
```

Include the implementation branch HEAD/tree, changed-file list, focused/full test commands and exact results, frozen legacy hash check, and confirmation that M2–M6 have not been claimed complete.

---

## M1 plan self-review checklist

Before executing this plan, verify these mappings:

| Frozen design requirement | M1 task |
| --- | --- |
| Parallel 0.2.0 contract without rewriting 0.1.2.1 | Tasks 1–2 |
| Typed semantic minima | Tasks 2–3 |
| `CURRENT/STALE/SUPERSEDED/RETIRED` foundation | Task 3 |
| 3+ digit stable IDs | Task 3 |
| No legacy Closure auto-upgrade | Tasks 2 and 5 |
| Deterministic migration foundation | Task 4 |
| No manufactured migration certainty | Task 4 |
| Deterministic generated IDs | Task 4 |
| V2 semantic digest not invented before M4 | Tasks 1–2 global closure interface |
| Legacy v1/downstream/calibration unchanged | Global constraints + Task 5 gate |

No M2 Product Surface/Evidence authority behavior, M3 Grill semantics, M4 Coverage Binding/Approval Manifest, M5 downstream 2.0 behavior, or M6 default-skill adoption is authorized by this M1 plan.
