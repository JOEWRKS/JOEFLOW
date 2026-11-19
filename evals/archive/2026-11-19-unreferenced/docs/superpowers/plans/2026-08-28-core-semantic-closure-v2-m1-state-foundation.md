# Core Semantic Closure V2 — M1 State 0.2 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the parallel `state.json` 0.2.0 foundation, deterministic version dispatch, typed semantic minima, lifecycle/ID rules, and deterministic migration planning without changing or weakening the frozen legacy 0.1.2.1 contract.

**Architecture:** Keep the legacy schema, validator core, state-contract reference, and example byte-identical. Add a separate V2 backend and a thin schema-version dispatcher behind the existing validator CLIs. M1 accepts structurally valid V2 states but always blocks V2 Closure until later milestones implement discovery, Grill, semantic coverage, and informed approval. Migration in M1 is read-only planning, never a completed semantic conversion.

**Tech Stack:** Python 3 standard library, JSON, JSON Schema documents, `unittest`, Git-blob SHA-1 freeze commitments, canonical JSON SHA-256 migration commitments.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-self-review.md`

## Global Constraints

- Implement from a branch/worktree whose base contains this plan and descends from design-freeze commit `26f1c0514206764e684799a5dbe1b3ec5ba1aa53`.
- Preserve these legacy files byte-for-byte:
  - `skills/joewrks-product-definition/schemas/state.schema.json` — `6a03894cc2164a9bfabbe8627a8468124d19b1f7`
  - `skills/joewrks-product-definition/scripts/state_validation.py` — `9a3b44359bddfd64c98392f235cb815a0b777cce`
  - `skills/joewrks-product-definition/references/state-contract.md` — `05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf`
  - `skills/joewrks-product-definition/templates/state.example.json` — `5fed7e87da243b3d234148bbbbf3baf7350d8ab0`
- `validate_state.py` and `validate_closure.py` may become version-aware wrappers; legacy semantics remain delegated to frozen `state_validation.py`.
- Do not change `skills/joewrks-product-definition/downstream/`, `evals/semantic-review-v0.4.3/`, downstream contract 1.0, or semantic-review 1.0.
- M1 excludes Product Surface/Evidence semantics, Grill Pack logic, Coverage→Authority Binding, Approval Manifest semantics, and downstream 2.0.
- Every V2 closure evaluation in M1 returns `closed: false`, `definition_digest: null`, and metric `semantic_closure_not_implemented: 1`.
- Do not invent a V2 semantic digest before M4.
- V2 stable IDs match `^[A-Z]+-[0-9]{3,}$`; existing IDs are never renumbered.
- Migration-plan JSON contains no current-time-derived canonical field.
- Behavior-changing work follows RED → GREEN → refactor. Freeze/characterization tests begin GREEN by design.
- Strongest M1 success label: `IMPLEMENTED_M1 / NOT_INTEGRATED`.

## File Map

**Create runtime/contract files**
- `skills/joewrks-product-definition/scripts/state_contract_dispatch.py`
- `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- `skills/joewrks-product-definition/scripts/migration_v2.py`
- `skills/joewrks-product-definition/scripts/migrate_state.py`
- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`

**Modify wrappers**
- `skills/joewrks-product-definition/scripts/validate_state.py`
- `skills/joewrks-product-definition/scripts/validate_closure.py`

**Create tests/support**
- `tests/v020_support.py`
- `tests/test_legacy_v0121_frozen.py`
- `tests/test_state_contract_dispatch.py`
- `tests/test_state_v020_foundation.py`
- `tests/test_migration_v020_foundation.py`

---

### Task 1: Freeze legacy bytes and add schema-version dispatch

**Files:**
- Create: `tests/test_legacy_v0121_frozen.py`
- Create: `tests/test_state_contract_dispatch.py`
- Create: `skills/joewrks-product-definition/scripts/state_contract_dispatch.py`
- Modify: `skills/joewrks-product-definition/scripts/validate_state.py`
- Modify: `skills/joewrks-product-definition/scripts/validate_closure.py`

**Interfaces:**
- `validate_state_for_version(state: dict[str, Any]) -> list[dict[str, str]]`
- `evaluate_closure_for_version(state: dict[str, Any]) -> dict[str, Any]`

- [ ] **Step 1: Pin legacy bytes with a GREEN characterization test**

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

Run:
```bash
python -m unittest tests.test_legacy_v0121_frozen -v
```
Expected: `OK`. Any failure blocks M1.

- [ ] **Step 2: Add RED dispatch tests**

`tests/test_state_contract_dispatch.py` invokes the actual CLI scripts with temporary JSON files. Assert the existing `closed_state()` from `tests.test_validators` still validates/closes, and `schema_version = "9.9.9"` makes both CLIs exit `1` with `unsupported_schema_version`.

Run:
```bash
python -m unittest tests.test_state_contract_dispatch -v
```
Expected: FAIL before dispatch exists.

- [ ] **Step 3: Implement `state_contract_dispatch.py`**

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

V2 imports remain lazy until Task 2 creates the backend.

- [ ] **Step 4: Make validator CLIs thin dispatch wrappers**

Preserve existing read-error/output/exit-code shapes. `validate_state.py` calls `validate_state_for_version`; `validate_closure.py` calls `evaluate_closure_for_version`. No closure semantics live in either wrapper.

- [ ] **Step 5: Run Task 1 GREEN**

```bash
python -m unittest tests.test_legacy_v0121_frozen tests.test_state_contract_dispatch tests.test_validators tests.test_semantic_v012 -v
```
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add tests/test_legacy_v0121_frozen.py tests/test_state_contract_dispatch.py \
  skills/joewrks-product-definition/scripts/state_contract_dispatch.py \
  skills/joewrks-product-definition/scripts/validate_state.py \
  skills/joewrks-product-definition/scripts/validate_closure.py
git commit -m "refactor: dispatch product definition state contracts"
```

---

### Task 2: Add V2 top-level foundation and explicit Closure guard

**Files:**
- Create: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Create: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/v020_support.py`
- Create: `tests/test_state_v020_foundation.py`

**Interfaces:**
- `validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]`
- `evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]`

- [ ] **Step 1: Create literal V2 foundation state test data**

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

- [ ] **Step 2: Add RED top-level tests**

Assert: valid foundation passes state validation; every root field is required; unknown root/project properties fail; V2 requires `project.definition_status` and rejects legacy `project.status`/`user_approved`; V2 is dispatched correctly; Closure returns exit `1`, `closed: false`, `definition_digest: null`, and `semantic_closure_not_implemented == 1`.

Run:
```bash
python -m unittest tests.test_state_v020_foundation -v
```
Expected: FAIL before V2 backend exists.

- [ ] **Step 3: Create top-level V2 JSON Schema**

Root required keys are exactly:
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

Root and `project` use `additionalProperties: false`; `schema_version` is const `0.2.0`; `definition_revision >= 1`; `closure_contract.level` is const `SEMANTIC_CLOSURE`; `definition_status` enum is `OPEN|READY_FOR_REVIEW|CLOSED|BLOCKED`. During Task 2, object-array items may be plain objects; Task 3 replaces them with final M1 typed definitions before M1 is reported.

- [ ] **Step 4: Implement top-level V2 validation**

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


def validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]:
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
    if not isinstance(objects, dict) or set(objects) != OBJECT_GROUPS:
        errors.append(_error("schema_error", "objects must contain all 13 canonical groups", "objects"))
    elif any(not isinstance(objects[name], list) for name in OBJECT_GROUPS):
        errors.append(_error("schema_error", "every canonical object group must be an array", "objects"))
    return errors


def evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "errors": validate_state_v2(state),
        "metrics": {"semantic_closure_not_implemented": 1},
        "closed": False,
        "definition_digest": None,
    }
```

Add local type checks for `slug`, `definition_revision`, `closure_contract`, `migration`, `evidence`, `surface_manifest`, `contradictions`, `coverage`, `ux_coverage`, `discovery_baseline`, `approval`, and `approval_history`. Do not add M2/M4 meaning rules.

- [ ] **Step 5: Run Task 2 GREEN plus legacy regression**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_state_contract_dispatch tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add tests/v020_support.py tests/test_state_v020_foundation.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py
git commit -m "feat: add state 0.2 foundation contract"
```

---

### Task 3: Enforce typed semantic minima, ID/lifecycle rules, and schema/runtime parity

**Files:**
- Modify: `tests/v020_support.py`
- Modify: `tests/test_state_v020_foundation.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`

**Interfaces:**
- Normal authority status: `CURRENT|STALE|SUPERSEDED|RETIRED`.
- Unknown status: `OPEN|RESOLVED|DEFERRED|BLOCKED|SUPERSEDED|RETIRED`.
- `TYPE_MINIMA: dict[str, frozenset[str]]` is the runtime source for required semantic field names; tests require JSON Schema `$defs` to contain the same required names.

- [ ] **Step 1: Add final Materiality test data**

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

M1 validates this shape but does not recompute classification; M3 owns classification semantics.

- [ ] **Step 2: Add RED semantic-minimum and parity tests**

For each group, `{id,status}` alone must fail. Valid semantic records use these required fields:

| Group | Required fields beyond `id,status` |
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

Add one test that loads `state-v0.2.0.schema.json` and asserts, per group, the schema-required semantic field set exactly equals runtime `TYPE_MINIMA[group]` after removing `id/status`. This prevents schema/runtime drift.

- [ ] **Step 3: Add RED ID/lifecycle tests**

Require `REQ-001`, `REQ-999`, `REQ-1000` to pass ID syntax and `REQ-01`, `REQ-A01` to fail. Duplicate IDs across object groups fail. Reserved `evidence`/`surface_manifest.records` IDs, when present, participate in global collision checks even though M2 defines their meaning.

Require:
- `SUPERSEDED` has a different existing same-prefix `superseded_by` target;
- self-reference, cross-type target, and supersession cycles fail;
- `RETIRED` has non-empty `retired_by`, positive `retired_at_revision`, meaningful `retirement_reason`;
- every `retired_by` target resolves to `DEC-*`;
- `retired_at_revision <= project.definition_revision`;
- validation never auto-retires dependents.

Run:
```bash
python -m unittest tests.test_state_v020_foundation -v
```
Expected: RED against Task-2 permissive object validation.

- [ ] **Step 4: Add final M1 typed `$defs` to the V2 schema**

Use `additionalProperties: false` for typed definitions. Permit the common lifecycle fields `superseded_by`, `retired_by`, `retired_at_revision`, `retirement_reason` in every normal authority definition. Semantic text is `minLength: 1`. Mapping arrays use unique strings; `TASK.implements` and `TASK.acceptance_refs` use `minItems: 1`; `major_actions` may be empty during M1.

Materiality shape is exact:

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
        "security": {"type": "boolean"}, "privacy": {"type": "boolean"}, "money": {"type": "boolean"},
        "legal_or_policy": {"type": "boolean"}, "destructive": {"type": "boolean"},
        "data_loss": {"type": "boolean"}, "external_commitment": {"type": "boolean"}
      },
      "additionalProperties": false
    },
    "classification": {"enum": ["MATERIAL", "NON_MATERIAL"]}
  },
  "additionalProperties": false
}
```

- [ ] **Step 5: Implement runtime typed/lifecycle helpers**

`state_validation_v2.py` defines:

```python
TYPE_MINIMA = {
    "goals": frozenset({"statement"}),
    "users": frozenset({"description", "actor_kind"}),
    "requirements": frozenset({"statement", "scope", "ui_required", "materiality"}),
    "unknowns": frozenset({"question", "materiality", "decision_authority"}),
    "decisions": frozenset({"statement", "decision_type", "resolution_mode", "decision_authority", "source_unknown_refs", "evidence_refs", "materiality", "affects"}),
    "rules": frozenset({"statement", "applies_to"}),
    "flows": frozenset({"goal_refs", "entry", "preconditions", "paths", "outcomes"}),
    "screens": frozenset({"purpose", "requirement_refs", "interaction_mode", "major_actions"}),
    "states": frozenset({"owner_refs", "state_name", "conditions"}),
    "data": frozenset({"name", "purpose", "ownership"}),
    "integrations": frozenset({"name", "purpose"}),
    "acceptance_criteria": frozenset({"requirement_refs", "assertion"}),
    "tasks": frozenset({"implements", "acceptance_refs"}),
}
```

Use focused internal helpers named `_iter_records`, `_collect_ids`, `_validate_typed_semantic_minima`, `_validate_materiality_shape`, `_validate_lifecycle`, `_validate_supersession_cycles`. `validate_state_v2` calls them after top-level validation. Keep M3 materiality classification and M4 authority binding out of M1.

- [ ] **Step 6: Run Task 3 GREEN plus legacy regression**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```
Expected: `OK`.

- [ ] **Step 7: Commit**

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
- `MigrationError(code: str, detail: object)` with `.code`, `.detail`.
- `canonical_json_bytes(value: object) -> bytes`.
- `allocate_generated_ids(prefix: str, existing_ids: set[str], canonical_paths: list[str]) -> dict[str, str]`.
- `build_migration_plan(state: dict[str, object]) -> dict[str, object]`.
- CLI: `python skills/joewrks-product-definition/scripts/migrate_state.py --plan SOURCE_JSON`.
- Output status: `FOUNDATION_PLAN_ONLY`; M1 never writes migrated V2 authority.

- [ ] **Step 1: Add RED migration tests**

Require valid legacy `closed_state()` to produce a plan; broken legacy source to return `MIGRATION_SOURCE_INVALID`; a `0.2.0` source to be rejected; repeated CLI calls on the same source to have identical stdout; no current-time keys; exact `from_schema=0.1.2.1`, `to_schema=0.2.0`, `migration_version=0.2.0-foundation.1`.

- [ ] **Step 2: Add RED generated-ID tests**

For:

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

An existing `REQ-999` followed by one generated REQ site allocates `REQ-1000`.

- [ ] **Step 3: Add RED reconciliation-site tests**

Canonical paths:
```text
/coverage/{feature_id}/cells/{axis}
/ux_coverage/{screen_id}/states/{axis}
/ux_coverage/{screen_id}/actions/{escaped-action-key}/cells/{axis}
```
Use JSON Pointer escaping (`~`→`~0`, `/`→`~1`). Reasons:
```text
COVERED → COVERED_BINDING_REQUIRED
N/A     → NA_BASIS_BINDING_REQUIRED
OPEN    → OPEN_UNKNOWN_BINDING_REQUIRED
```
Every site gets a deterministic generated `UNK-*`; none is marked resolved.

Run:
```bash
python -m unittest tests.test_migration_v020_foundation -v
```
Expected: RED before migration modules exist.

- [ ] **Step 4: Implement deterministic migration primitives**

```python
from __future__ import annotations
import hashlib
import json
import re
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

`build_migration_plan` requires exact legacy schema version, then requires frozen `legacy.validate_state(state)` to return no errors. Otherwise raise `MigrationError("MIGRATION_SOURCE_INVALID", errors)`.

Collect preserved IDs from legacy object groups and contradiction records with string IDs. `allocate_generated_ids` considers only the requested prefix plus decimal suffix, starts at the greatest existing suffix + 1, sorts source paths, and formats with `f"{prefix}-{number:03d}"` so 1000 remains four digits.

Return:

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

Each reconciliation item contains exactly `path`, `reason`, `generated_unknown_id` and the array is sorted by `path`.

- [ ] **Step 5: Implement deterministic `migrate_state.py --plan`**

Success:

```python
print(json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
return 0
```

Migration failure:

```python
print(json.dumps({"error": {"code": exc.code, "detail": exc.detail}}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
return 1
```

Usage/read errors return `2`. No in-place mutation option exists in M1.

- [ ] **Step 6: Run Task 4 GREEN plus legacy regression**

```bash
python -m unittest tests.test_migration_v020_foundation tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
```
Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add skills/joewrks-product-definition/scripts/migration_v2.py \
  skills/joewrks-product-definition/scripts/migrate_state.py \
  tests/test_migration_v020_foundation.py
git commit -m "feat: add deterministic state 0.2 migration planner"
```

---

### Task 5: Document the M1 boundary, add the native V2 example, and run the gate

**Files:**
- Create: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Create: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- Modify: `tests/test_state_v020_foundation.py`
- Do not modify: `README.md`, `SKILL.md`, legacy state contract, or legacy template in M1.

- [ ] **Step 1: Add RED docs/template assertions**

Require schema, new reference, and new template to exist. Assert schema const `0.2.0`; template is `0.2.0`, OPEN, UNAPPROVED; template passes real state validation and fails Closure with `semantic_closure_not_implemented == 1`; reference contains `LEGACY_CLOSURE`, `SEMANTIC_CLOSURE`, `FOUNDATION_PLAN_ONLY`, `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1`.

Run:
```bash
python -m unittest tests.test_state_v020_foundation -v
```
Expected: RED until reference/template exist.

- [ ] **Step 2: Create `state-v0.2.0.example.json`**

Use the JSON equivalent of `foundation_state()`: no product objects, `definition_status: OPEN`, `migration.mode: NATIVE`, `discovery_baseline.status: NOT_ESTABLISHED`, `approval.status: UNAPPROVED`.

- [ ] **Step 3: Write `state-contract-v0.2.0.md`**

It states exactly:
```text
state 0.2.0 is parallel to, not an in-place replacement for, legacy 0.1.2.1.
legacy 0.1.2.1 validation remains frozen.
M1 validates V2 top-level shape, typed semantic minima, lifecycle, IDs, and migration planning.
M1 does not claim V2 Semantic Closure.
validate_closure on 0.2.0 returns semantic_closure_not_implemented = 1 and closed = false.
migrate_state.py --plan emits FOUNDATION_PLAN_ONLY and never manufactures V2 authority.
The M1 closure guard may be removed only by a later milestone that implements and verifies its frozen gate.
```

- [ ] **Step 4: Run all focused M1 tests**

```bash
python -m unittest \
  tests.test_legacy_v0121_frozen \
  tests.test_state_contract_dispatch \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation -v
```
Expected: `OK`.

- [ ] **Step 5: Run legacy regression**

```bash
python -m unittest tests.test_validators tests.test_semantic_v012 -v
```
Expected: `OK`; all four frozen Git-blob commitments still match.

- [ ] **Step 6: Run the full repository suite**

```bash
python -m unittest discover -s tests -v
```
Expected: exit `0`, zero failures/errors. No new skip; a pre-existing environment-dependent skip may remain only with unchanged reason.

- [ ] **Step 7: Run tree integrity checks**

```bash
git diff --check
python -m unittest tests.test_legacy_v0121_frozen -v
```
Expected: both exit `0`.

Diff inspection must show zero M1 changes under:
```text
skills/joewrks-product-definition/downstream/
evals/semantic-review-v0.4.3/
skills/joewrks-product-definition/schemas/state.schema.json
skills/joewrks-product-definition/scripts/state_validation.py
skills/joewrks-product-definition/references/state-contract.md
skills/joewrks-product-definition/templates/state.example.json
```

- [ ] **Step 8: Commit**

```bash
git add skills/joewrks-product-definition/references/state-contract-v0.2.0.md \
  skills/joewrks-product-definition/templates/state-v0.2.0.example.json \
  tests/test_state_v020_foundation.py
git commit -m "docs: define state 0.2 foundation boundary"
```

- [ ] **Step 9: Report M1 precisely**

Only after all gates are green:
```text
CORE_SEMANTIC_CLOSURE_V2_M1_IMPLEMENTED
— STATE_0_2_FOUNDATION / NOT_INTEGRATED
```
Include implementation HEAD/tree, changed files, exact test results, frozen legacy commitment verification, and explicit M2–M6 non-completion.

---

## Plan Self-Review Mapping

| Frozen requirement | M1 task |
| --- | --- |
| Parallel 0.2.0 without rewriting 0.1.2.1 | Tasks 1–2 |
| Typed semantic minima | Task 3 |
| Schema/runtime required-field parity | Task 3 |
| `CURRENT/STALE/SUPERSEDED/RETIRED` | Task 3 |
| 3+ digit IDs | Task 3 |
| No legacy Closure auto-upgrade | Tasks 2 and 5 |
| Deterministic migration foundation | Task 4 |
| No manufactured migration certainty | Task 4 |
| Deterministic generated IDs | Task 4 |
| No premature V2 semantic digest | Tasks 1–2 |
| Legacy downstream/calibration untouched | Global constraints + Task 5 gate |

M1 intentionally leaves Product Surface/Evidence authority behavior to M2, Grill semantics to M3, Coverage Binding/Approval Manifest to M4, downstream 2.0 to M5, and default-skill adoption/end-to-end integration to M6. These are explicit scope boundaries, not incomplete M1 requirements.
