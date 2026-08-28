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
- `validate_state.py` and `validate_closure.py` may change only into version-aware wrappers; legacy 0.1.2.1 behavior remains delegated to frozen `state_validation.py`.
- Do not modify `skills/joewrks-product-definition/downstream/`, `evals/semantic-review-v0.4.3/`, `joewrks.action-conformance/1.0`, or `joewrks.semantic-review/1.0` during M1.
- M1 does not implement Product Surface semantics, Evidence authority classes, Grill Pack activation, Coverage→Authority Binding, Approval Manifest semantics, or downstream 2.0. Those belong to M2–M5.
- A 0.2.0 state must never return `closed: true` during M1. Every V2 closure evaluation includes `semantic_closure_not_implemented = 1` until the later semantic-closure milestones replace that guard.
- Do not create a provisional V2 definition digest in M1. V2 closure output uses JSON `null` for `definition_digest` until M4 defines the approved semantic digest boundary.
- V2 IDs use `^[A-Z]+-[0-9]{3,}$`; existing IDs are never renumbered.
- Canonical migration-plan output contains no current-time field. Same semantic source plus the same migration version must produce byte-identical plan JSON.
- Every behavior-changing code task follows RED → GREEN → refactor. Characterization/freeze tests start GREEN because they pin existing bytes/behavior.
- The strongest successful M1 status is `IMPLEMENTED_M1 / NOT_INTEGRATED`; do not report `Core V2 complete` before M6.

---

## File map locked by this plan

### New runtime/validator files

- `skills/joewrks-product-definition/scripts/state_contract_dispatch.py` — schema-version routing only.
- `skills/joewrks-product-definition/scripts/state_validation_v2.py` — V2 foundation validation and M1 closure guard.
- `skills/joewrks-product-definition/scripts/migration_v2.py` — deterministic migration-plan primitives.
- `skills/joewrks-product-definition/scripts/migrate_state.py` — CLI exposing the M1 `--plan` operation.

### New contract/docs/template files

- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`

### Modified wrappers only

- `skills/joewrks-product-definition/scripts/validate_state.py`
- `skills/joewrks-product-definition/scripts/validate_closure.py`

### New tests/support

- `tests/v020_support.py`
- `tests/test_legacy_v0121_frozen.py`
- `tests/test_state_contract_dispatch.py`
- `tests/test_state_v020_foundation.py`
- `tests/test_migration_v020_foundation.py`

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
  - `validate_state_for_version(state: dict[str, Any]) -> list[dict[str, str]]`
  - `evaluate_closure_for_version(state: dict[str, Any]) -> dict[str, Any]`
- Unsupported versions return `unsupported_schema_version`; they never fall back to a newest/default schema.

- [ ] **Step 1: Add byte-freeze characterization tests**

Create `tests/test_legacy_v0121_frozen.py` exactly around these commitments:

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
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class LegacyV0121FrozenTest(unittest.TestCase):
    def test_frozen_legacy_contract_bytes(self):
        for relative, expected in FROZEN.items():
            with self.subTest(relative=relative):
                self.assertEqual(git_blob_sha1((ROOT / relative).read_bytes()), expected)
```

- [ ] **Step 2: Verify the byte baseline is GREEN**

Run:

```bash
python -m unittest tests.test_legacy_v0121_frozen -v
```

Expected: `OK`. A failure here blocks M1 because the implementation base no longer matches the frozen legacy authority.

- [ ] **Step 3: Add dispatch RED tests**

In `tests/test_state_contract_dispatch.py`, invoke the existing validator CLIs via subprocess. Reuse `closed_state()` from `tests.test_validators` and assert legacy state validation and closure remain successful. Add an unsupported-version case using `schema_version = "9.9.9"` and require both CLIs to exit `1` with error code `unsupported_schema_version`.

- [ ] **Step 4: Verify dispatch tests are RED**

```bash
python -m unittest tests.test_state_contract_dispatch -v
```

Expected: FAIL because the current CLIs directly bind the legacy validator and do not expose version dispatch.

- [ ] **Step 5: Implement the dispatcher**

Create `state_contract_dispatch.py` with this public surface:

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

The V2 imports stay lazy so Task 1 can preserve legacy execution before Task 2 creates the V2 module.

- [ ] **Step 6: Convert the two CLIs into thin wrappers**

Keep their existing input/read-error/output/exit-code conventions. `validate_state.py` calls `validate_state_for_version`; `validate_closure.py` calls `evaluate_closure_for_version`. Do not duplicate validation or closure logic in the wrappers.

- [ ] **Step 7: Run Task 1 GREEN**

```bash
python -m unittest tests.test_legacy_v0121_frozen tests.test_state_contract_dispatch tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`, including unchanged frozen legacy hashes.

- [ ] **Step 8: Commit Task 1**

```bash
git add tests/test_legacy_v0121_frozen.py tests/test_state_contract_dispatch.py \
  skills/joewrks-product-definition/scripts/state_contract_dispatch.py \
  skills/joewrks-product-definition/scripts/validate_state.py \
  skills/joewrks-product-definition/scripts/validate_closure.py
git commit -m "refactor: dispatch product definition state contracts"
```

---

### Task 2: Add the V2 top-level foundation and explicit closure guard

**Files:**
- Create: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Create: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/v020_support.py`
- Create: `tests/test_state_v020_foundation.py`

**Interfaces:**
- Produces `validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]`.
- Produces `evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]`.
- M1 V2 closure always returns `closed: false`, `definition_digest: None`, and `semantic_closure_not_implemented: 1`.

- [ ] **Step 1: Create literal V2 foundation test data**

Create `tests/v020_support.py`:

```python
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
            "goals": [], "users": [], "requirements": [], "unknowns": [],
            "decisions": [], "rules": [], "flows": [], "screens": [],
            "states": [], "data": [], "integrations": [],
            "acceptance_criteria": [], "tasks": [],
        },
        "coverage": [],
        "ux_coverage": [],
        "discovery_baseline": {"status": "NOT_ESTABLISHED"},
        "approval": {"status": "UNAPPROVED"},
        "approval_history": [],
    }
```

- [ ] **Step 2: Add top-level V2 RED tests**

In `tests/test_state_v020_foundation.py`, assert:

- `foundation_state()` is accepted by `validate_state.py`.
- deleting any required root key is rejected.
- `project.status` is rejected; V2 requires `project.definition_status`.
- `project.user_approved` is rejected; approval is top-level only.
- unknown extra root/project properties are rejected.
- `schema_version: 0.2.0` routes to V2 rather than `unsupported_schema_version`.
- `validate_closure.py` exits `1`, returns `closed: false`, `definition_digest: null`, and `metrics.semantic_closure_not_implemented == 1`.

- [ ] **Step 3: Verify RED**

```bash
python -m unittest tests.test_state_v020_foundation -v
```

Expected: FAIL because the V2 validator/schema do not exist.

- [ ] **Step 4: Create the V2 top-level JSON Schema foundation**

`state-v0.2.0.schema.json` uses Draft 2020-12. Root `required` is exactly:

```text
schema_version
project
migration
evidence
surface_manifest
contradictions
objects
coverage
ux_coverage
discovery_baseline
approval
approval_history
```

Root and `project` use `additionalProperties: false`. `schema_version` is const `0.2.0`. `project.definition_status` permits `OPEN`, `READY_FOR_REVIEW`, `CLOSED`, `BLOCKED`; `definition_revision` is integer `>= 1`; `closure_contract.level` is const `SEMANTIC_CLOSURE`.

For Task 2 only, each of the 13 object arrays accepts object items without semantic minima. Task 3 replaces those item definitions with final M1 typed minima. This temporary Task-2 state is not a milestone deliverable on its own.

- [ ] **Step 5: Implement top-level-only `state_validation_v2.py`**

Use:

```python
from __future__ import annotations
from typing import Any

SCHEMA_VERSION = "0.2.0"
ROOT_KEYS = {
    "schema_version", "project", "migration", "evidence", "surface_manifest",
    "contradictions", "objects", "coverage", "ux_coverage",
    "discovery_baseline", "approval", "approval_history",
}
PROJECT_KEYS = {"slug", "definition_status", "definition_revision", "closure_contract"}
OBJECT_GROUPS = {
    "goals", "users", "requirements", "unknowns", "decisions", "rules",
    "flows", "screens", "states", "data", "integrations",
    "acceptance_criteria", "tasks",
}
DEFINITION_STATUSES = {"OPEN", "READY_FOR_REVIEW", "CLOSED", "BLOCKED"}


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _validate_top_level(state: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(_error("schema_error", "schema_version must equal 0.2.0", "schema_version"))
    if set(state) != ROOT_KEYS:
        errors.append(_error("schema_error", "state root fields do not match the 0.2.0 foundation contract", ""))
    project = state.get("project")
    if not isinstance(project, dict) or set(project) != PROJECT_KEYS:
        errors.append(_error("schema_error", "project fields do not match the 0.2.0 foundation contract", "project"))
    elif project.get("definition_status") not in DEFINITION_STATUSES:
        errors.append(_error("invalid_status", "invalid definition_status", "project.definition_status"))
    objects = state.get("objects")
    if not isinstance(objects, dict) or set(objects) != OBJECT_GROUPS or any(not isinstance(objects[name], list) for name in OBJECT_GROUPS):
        errors.append(_error("schema_error", "objects must contain all 13 canonical arrays", "objects"))
    return errors


def validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]:
    if not isinstance(state, dict):
        return [_error("schema_error", "state root must be an object", "")]
    return _validate_top_level(state)


def evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]:
    errors = validate_state_v2(state)
    return {
        "errors": errors,
        "metrics": {"semantic_closure_not_implemented": 1},
        "closed": False,
        "definition_digest": None,
    }
```

Add explicit type checks for `slug`, `definition_revision`, `closure_contract`, `migration`, arrays, `surface_manifest`, `discovery_baseline`, `approval`, and `approval_history`; keep them in `_validate_top_level` rather than adding M2/M4 semantics.

- [ ] **Step 6: Run Task 2 GREEN plus legacy regression**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_state_contract_dispatch tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`; a V2 OPEN state is structurally valid but never closed.

- [ ] **Step 7: Commit Task 2**

```bash
git add tests/v020_support.py tests/test_state_v020_foundation.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py
git commit -m "feat: add state 0.2 foundation contract"
```

---

### Task 3: Enforce typed semantic minima, IDs, supersession, and retirement

**Files:**
- Modify: `tests/v020_support.py`
- Modify: `tests/test_state_v020_foundation.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`

**Interfaces:**
- Extends `validate_state_v2`; no new public entrypoint.
- Normal authority records use `CURRENT`, `STALE`, `SUPERSEDED`, `RETIRED`.
- Unknowns use `OPEN`, `RESOLVED`, `DEFERRED`, `BLOCKED`, `SUPERSEDED`, `RETIRED`.

- [ ] **Step 1: Add final Materiality test data**

Add to `tests/v020_support.py`:

```python
def materiality(*, classification="NON_MATERIAL"):
    return {
        "outcome_divergence": "LOW",
        "fan_out": "LOCAL",
        "user_visible": False,
        "reversibility": "TRIVIALLY_REVERSIBLE",
        "risk_flags": {
            "security": False, "privacy": False, "money": False,
            "legal_or_policy": False, "destructive": False,
            "data_loss": False, "external_commitment": False,
        },
        "classification": classification,
    }
```

M1 validates the full materiality shape but does not recompute classification consistency; M3 owns that classifier.

- [ ] **Step 2: Add semantic-minimum RED tests**

For every object group, insert `{id, status}` and require rejection with `semantic_minimum_missing`. Add valid literals using these exact semantic shapes:

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

- [ ] **Step 3: Add ID/lifecycle RED tests**

Require:

```text
REQ-001   valid
REQ-999   valid
REQ-1000  valid
REQ-01    invalid
REQ-A01   invalid
```

Also require duplicate IDs across object groups to fail. If an entry in the reserved `evidence` or `surface_manifest.records` arrays contains a string `id`, include it in global collision checks even though M2 will define its semantic schema.

Lifecycle cases:

- `SUPERSEDED` requires a different existing same-prefix `superseded_by` target.
- self-reference, cross-type replacement, and supersession cycles fail.
- `RETIRED` requires non-empty `retired_by`, positive `retired_at_revision`, and meaningful `retirement_reason`.
- every `retired_by` ref must resolve to a `DEC-*` record.
- `retired_at_revision` may not exceed `project.definition_revision`.
- validation never auto-retires dependents.

- [ ] **Step 4: Verify Task 3 RED**

```bash
python -m unittest tests.test_state_v020_foundation -v
```

Expected: the new semantic/lifecycle cases fail against the Task-2 top-level-only validator.

- [ ] **Step 5: Tighten the V2 schema to final M1 typed definitions**

Replace Task-2 permissive object items with distinct `$defs`. Required fields beyond `id/status` are:

| Group | Required semantic fields |
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

Semantic text uses `minLength: 1`. Mapping arrays use unique string items. `implements` and `acceptance_refs` use `minItems: 1`. `major_actions` may be empty in M1. Normal typed definitions use `additionalProperties: false` except for the explicitly documented lifecycle fields `superseded_by`, `retired_by`, `retired_at_revision`, `retirement_reason`.

Materiality is exactly:

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
        "security": {"type": "boolean"}, "privacy": {"type": "boolean"},
        "money": {"type": "boolean"}, "legal_or_policy": {"type": "boolean"},
        "destructive": {"type": "boolean"}, "data_loss": {"type": "boolean"},
        "external_commitment": {"type": "boolean"}
      },
      "additionalProperties": false
    },
    "classification": {"enum": ["MATERIAL", "NON_MATERIAL"]}
  },
  "additionalProperties": false
}
```

- [ ] **Step 6: Implement typed/lifecycle helpers in `state_validation_v2.py`**

Use these internal helper names and responsibilities:

```text
_validate_top_level                 root/project/reserved-section shape
_iter_records                       yield group, index, record for all object groups
_collect_ids                        enforce global ID syntax/uniqueness, including reserved evidence/surface IDs when present
_validate_typed_semantic_minima     required field presence, non-empty semantic text, local collection shape
_validate_lifecycle                 allowed status plus SUPERSEDED/RETIRED requirements
_validate_supersession_cycles       same-prefix graph cycle detection
_validate_materiality_shape         exact enum/boolean/risk-flag structure only
```

`validate_state_v2` calls those helpers in that order and concatenates errors. Use the established `{code, message, path}` error object shape. Do not implement M3 materiality classification or M4 cross-authority coverage validation.

- [ ] **Step 7: Run Task 3 GREEN plus legacy regression**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`.

- [ ] **Step 8: Commit Task 3**

```bash
git add tests/v020_support.py tests/test_state_v020_foundation.py \
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
- Produces `MigrationError(code: str, detail: object)` with `.code` and `.detail`.
- Produces `canonical_json_bytes(value: object) -> bytes`.
- Produces `allocate_generated_ids(prefix: str, existing_ids: set[str], canonical_paths: list[str]) -> dict[str, str]`.
- Produces `build_migration_plan(state: dict[str, object]) -> dict[str, object]`.
- CLI: `python skills/joewrks-product-definition/scripts/migrate_state.py --plan SOURCE_JSON`.
- Output status is exactly `FOUNDATION_PLAN_ONLY`; M1 never writes a migrated V2 authority file.

- [ ] **Step 1: Add migration RED tests**

In `tests/test_migration_v020_foundation.py` require:

- a valid legacy `closed_state()` can produce a plan;
- a broken-reference legacy state returns `MIGRATION_SOURCE_INVALID`;
- a `0.2.0` source is rejected because this path accepts only `0.1.2.1`;
- two CLI executions on the same source emit byte-identical stdout;
- output contains no keys named `migrated_at` or `created_at`;
- output has `from_schema = 0.1.2.1`, `to_schema = 0.2.0`, `migration_version = 0.2.0-foundation.1`.

- [ ] **Step 2: Add generated-ID RED tests**

With:

```python
existing = {"UNK-001", "UNK-007", "UNK-103"}
paths = [
    "/coverage/REQ-002/security",
    "/coverage/REQ-001/actor",
    "/coverage/REQ-001/security",
]
```

require:

```python
{
    "/coverage/REQ-001/actor": "UNK-104",
    "/coverage/REQ-001/security": "UNK-105",
    "/coverage/REQ-002/security": "UNK-106",
}
```

Also require an existing `REQ-999` followed by one generated REQ site to allocate `REQ-1000`.

- [ ] **Step 3: Add reconciliation-site RED tests**

Canonical site paths are:

```text
/coverage/{feature_id}/cells/{axis}
/ux_coverage/{screen_id}/states/{axis}
/ux_coverage/{screen_id}/actions/{json-pointer-escaped-action-key}/cells/{axis}
```

Use JSON Pointer escaping (`~`→`~0`, `/`→`~1`) for action keys. Classify legacy cells exactly:

```text
COVERED → COVERED_BINDING_REQUIRED
N/A     → NA_BASIS_BINDING_REQUIRED
OPEN    → OPEN_UNKNOWN_BINDING_REQUIRED
```

Every reconciliation site gets a deterministic generated `UNK-*` ID. The plan never marks that unknown resolved.

- [ ] **Step 4: Verify migration tests RED**

```bash
python -m unittest tests.test_migration_v020_foundation -v
```

Expected: FAIL because migration modules do not exist.

- [ ] **Step 5: Implement deterministic migration primitives**

Use:

```python
from __future__ import annotations
import hashlib
import json
from typing import Any
import state_validation as legacy

MIGRATION_VERSION = "0.2.0-foundation.1"
FROM_SCHEMA = "0.1.2.1"
TO_SCHEMA = "0.2.0"
PLAN_SCHEMA = "joewrks.state-migration-plan/1.0"

class MigrationError(ValueError):
    def __init__(self, code: str, detail: object = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}: {detail}")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
```

`build_migration_plan` first requires `schema_version == FROM_SCHEMA`, then calls frozen `legacy.validate_state(state)`. Any validation error raises `MigrationError("MIGRATION_SOURCE_INVALID", errors)`.

Collect preserved stable IDs from all legacy object groups and contradiction records that carry string IDs. `allocate_generated_ids` parses only IDs matching the requested prefix plus a decimal suffix, starts from the greatest existing suffix plus one, sorts canonical paths, and formats numbers with at least three digits.

Return this concrete runtime structure:

```python
return {
    "schema_version": PLAN_SCHEMA,
    "status": "FOUNDATION_PLAN_ONLY",
    "from_schema": FROM_SCHEMA,
    "to_schema": TO_SCHEMA,
    "migration_version": MIGRATION_VERSION,
    "source_digest": hashlib.sha256(canonical_json_bytes(state)).hexdigest(),
    "preserved_ids": sorted(preserved_ids),
    "reconciliation_sites": reconciliation_sites,
}
```

`reconciliation_sites` is already sorted by canonical path and each item contains `path`, `reason`, `generated_unknown_id`.

- [ ] **Step 6: Implement the deterministic `--plan` CLI**

On success, print:

```python
json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
```

and exit `0`. On `MigrationError`, emit `{"error":{"code": exc.code, "detail": exc.detail}}` with the same canonical JSON formatting and exit `1`. Usage/read errors exit `2`. Do not add an in-place option.

- [ ] **Step 7: Run Task 4 GREEN plus legacy regression**

```bash
python -m unittest tests.test_migration_v020_foundation tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK`.

- [ ] **Step 8: Commit Task 4**

```bash
git add skills/joewrks-product-definition/scripts/migration_v2.py \
  skills/joewrks-product-definition/scripts/migrate_state.py \
  tests/test_migration_v020_foundation.py
git commit -m "feat: add deterministic state 0.2 migration planner"
```

---

### Task 5: Document the M1 boundary, add the V2 native example, and run the milestone gate

**Files:**
- Create: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Create: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- Modify: `tests/test_state_v020_foundation.py`
- Do not modify: `README.md`, `SKILL.md`, the legacy state contract, or the legacy template during M1. V2 becomes a default user workflow only at M6 adoption.

**Interfaces:**
- The new reference uses the literal marker `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1`.
- The example is a native OPEN V2 state matching `foundation_state()`.

- [ ] **Step 1: Add documentation/fixture RED tests**

Require these files to exist:

```python
schema_path = ROOT / "skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json"
reference_path = ROOT / "skills/joewrks-product-definition/references/state-contract-v0.2.0.md"
template_path = ROOT / "skills/joewrks-product-definition/templates/state-v0.2.0.example.json"
```

Assertions:

- schema const is `0.2.0`;
- template `schema_version` is `0.2.0` and `approval.status` is `UNAPPROVED`;
- template passes real state validation;
- template fails closure with `semantic_closure_not_implemented == 1`;
- reference contains `LEGACY_CLOSURE`, `SEMANTIC_CLOSURE`, `FOUNDATION_PLAN_ONLY`, and `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1`.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest tests.test_state_v020_foundation -v
```

Expected: FAIL because the reference and template do not exist.

- [ ] **Step 3: Create the V2 native template**

Write `state-v0.2.0.example.json` as the JSON equivalent of `foundation_state()`: no product objects, `definition_status: OPEN`, `migration.mode: NATIVE`, `discovery_baseline.status: NOT_ESTABLISHED`, `approval.status: UNAPPROVED`.

- [ ] **Step 4: Write the M1 state-contract reference**

The reference states these exact boundaries:

```text
state 0.2.0 is parallel to, not an in-place replacement for, legacy 0.1.2.1.
legacy 0.1.2.1 validation remains frozen.
M1 validates V2 top-level shape, typed semantic minima, lifecycle, IDs, and migration planning.
M1 does not claim V2 Semantic Closure.
validate_closure on 0.2.0 returns semantic_closure_not_implemented = 1 and closed = false.
migrate_state.py --plan emits FOUNDATION_PLAN_ONLY and never manufactures V2 authority.
The M1 closure guard may be removed only by later milestone work that implements and verifies its own frozen gate.
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

- [ ] **Step 6: Run legacy regression GREEN**

```bash
python -m unittest tests.test_validators tests.test_semantic_v012 -v
```

Expected: `OK` and all four frozen Git-blob hashes still match.

- [ ] **Step 7: Run the entire repository test suite**

```bash
python -m unittest discover -s tests -v
```

Expected: exit `0`, no failures or errors. No new skip is allowed; a pre-existing environment-dependent skip may remain only with its existing reason.

- [ ] **Step 8: Run source-tree integrity checks**

```bash
git diff --check
python -m unittest tests.test_legacy_v0121_frozen -v
```

Expected: both exit `0`.

Also inspect the branch diff and require zero M1 changes under:

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

- [ ] **Step 10: Report the milestone precisely**

Only after every gate above is green, report:

```text
CORE_SEMANTIC_CLOSURE_V2_M1_IMPLEMENTED
— STATE_0_2_FOUNDATION / NOT_INTEGRATED
```

Include branch HEAD/tree, changed files, exact focused/full test results, frozen legacy hash verification, and an explicit statement that M2–M6 remain outside the completed scope.

---

## M1 plan self-review mapping

| Frozen design requirement | M1 task |
| --- | --- |
| Parallel 0.2.0 contract without rewriting 0.1.2.1 | Tasks 1–2 |
| Typed semantic minima | Task 3 |
| `CURRENT/STALE/SUPERSEDED/RETIRED` | Task 3 |
| 3+ digit stable IDs | Task 3 |
| No legacy Closure auto-upgrade | Tasks 2 and 5 |
| Deterministic migration foundation | Task 4 |
| Migration may not manufacture certainty | Task 4 |
| Deterministic generated IDs | Task 4 |
| V2 semantic digest not invented before M4 | Tasks 1–2 |
| Legacy downstream/calibration remains untouched | Global constraints + Task 5 gate |

M1 intentionally leaves Product Surface/Evidence authority behavior to M2, Grill semantics to M3, Coverage Binding/Approval Manifest to M4, downstream 2.0 to M5, and default-skill adoption/end-to-end integration to M6. These are explicit scope boundaries, not incomplete M1 requirements.
