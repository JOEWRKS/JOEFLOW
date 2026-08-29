# Core Semantic Closure V2 — M6 Integration & Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate M1–M5 into the installed Product Definition workflow, complete deterministic legacy-to-V2 migration, add contract-bound runtime verification, prove a representative existing-product V2 dogfood from discovery through approval/handoff/re-entry/verification, and produce the final R1–R10 compatibility gate without rewriting frozen historical contracts.

**Architecture:** M6 is an integration milestone, not another semantic redesign. Keep state schema `0.2.0`, `joewrks.action-conformance/2.0`, `joewrks.semantic-review/2.0`, and `joewrks.product-definition-reentry/1.0` as the authorities already established by M1–M5. Extend only the previously deferred migration/adoption/runtime surfaces. New-project skill routing becomes V2-first while legacy `0.1.2.1` remains supported and byte-frozen. Runtime verification consumes the already compiled V2 action contract and the already frozen `joewrks.downstream.execution/1.0` evidence transport without redefining that transport. A real user approval checkpoint is mandatory in the dogfood; no test fixture or agent may synthesize Product Definition approval.

**Tech Stack:** Python 3 standard library, JSON, JSONL, Draft 2020-12 repository schema subset, RFC 6901 JSON Pointer, canonical UTF-8 JSON SHA-256, `unittest`, Git.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md` — especially sections 34–47 and M6 Integration & Adoption
- `docs/superpowers/audits/2026-08-30-core-semantic-closure-v2-m5-source-audit.md`
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- `skills/joewrks-product-definition/references/semantic-freeze-contract-v0.2.0.md`
- `skills/joewrks-product-definition/references/downstream-v2-contract.md`
- `skills/joewrks-product-definition/references/implementation-reentry-contract.md`

## Global Constraints

- Base implementation on the exact final M6 planning HEAD descended from M5 HEAD `b8ac6b87dffeb5ecda0590e31e98a306a9749609`.
- M6 is the first milestone allowed to integrate M1–M5 into the installed/default skill workflow.
- Do not merge to `main` during execution. The strongest outcome is `READY_FOR_MERGE` after the final gate and user review.
- Preserve the entire historical downstream v1 tree exactly:
  - `skills/joewrks-product-definition/downstream/`
  - Git tree `b63568d8c4632b14bc806e7bff1908e94dea9669`.
- Preserve the entire historical semantic-review v0.4.3 evidence tree exactly:
  - `evals/semantic-review-v0.4.3/`
  - Git tree `a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43`.
- Preserve the four legacy `0.1.2.1` contract blobs exactly:
  - `schemas/state.schema.json` → `6a03894cc2164a9bfabbe8627a8468124d19b1f7`
  - `scripts/state_validation.py` → `9a3b44359bddfd64c98392f235cb815a0b777cce`
  - `references/state-contract.md` → `05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf`
  - `templates/state.example.json` → `5fed7e87da243b3d234148bbbbf3baf7350d8ab0`.
- Do not redefine `joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, or `joewrks.downstream.execution/1.0`.
- Preserve M5 contract identities exactly:
  - `joewrks.action-conformance/2.0`
  - `joewrks.semantic-review/2.0`
  - `joewrks.product-definition-reentry/1.0`.
- `joewrks.semantic-review/2.0` reliability remains `NOT_MEASURED` in M6. M6 integration does not inherit or manufacture reliability.
- V2 Product Definition approval remains a recorded user-approval claim. No script, test fixture, migrator, dogfood builder, or downstream compiler may auto-create an `APPROVED` state.
- Migration may expose uncertainty but may never increase epistemic confidence. A legacy `CLOSED` state never migrates directly to V2 `CLOSED` or to a current V2 approval.
- Migration must preserve every legacy stable ID and historical record. IDs are never renumbered or reused.
- New V2 project creation defaults to `templates/state-v0.2.0.example.json`; the frozen legacy template remains available only for legacy compatibility.
- Existing `0.1.2.1` projects continue to validate under the frozen legacy validator unless the user explicitly invokes migration.
- Runtime verification consumes a valid `joewrks.action-conformance/2.0` contract. It does not reinterpret Product Definition directly and does not create authority.
- Runtime evidence transport remains exactly `joewrks.downstream.execution/1.0`; M6 may consume it but may not change its schema or meaning.
- Runtime evidence must bind the V2 contract by `contract_hash = semantic_contract_hash`, and bind Product Definition by `authority.approved_digest = source_authority.approved_definition_digest`.
- A runtime mismatch creates implementation-conformance failure and, where appropriate, a read-only `CONTRACT_CONFLICT` re-entry proposal. It must never silently rewrite Product Definition or the contract.
- M6 representative dogfood must be based on an existing product/source boundary, not a greenfield product invented solely to satisfy tests.
- The dogfood may use a deliberately small material slice to keep the gate inspectable, but it must exercise the complete documented workflow for that slice.
- Dogfood approval has a hard human checkpoint. Execution must stop and present the deterministic Approval Manifest before writing approval fields.
- If the dogfood discovers a genuine material product choice not resolved by authoritative evidence, stop and ask the user; do not close with a fixture answer.
- Every behavior-changing task follows RED → GREEN → refactor and ends with a commit.
- Full completion is not claimed until Task 6 passes and the user approves the final integration result.

---

# File Map

## Migration completion

Modify:

- `skills/joewrks-product-definition/scripts/migration_v2.py`
- `skills/joewrks-product-definition/scripts/migrate_state.py`
- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json` only if required to represent the already-approved migrated-state receipt; do not change unrelated M1–M5 semantics.
- `skills/joewrks-product-definition/scripts/state_validation_v2.py` only for the corresponding migrated-state receipt validation; do not weaken any existing blocker.
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`

Create:

- `skills/joewrks-product-definition/references/migration-v0.2.0.md`
- `tests/test_migration_v020_apply.py`

## Installed V2 workflow routing

Modify:

- `skills/joewrks-product-definition/SKILL.md`
- `README.md`
- `PROGRAM_ARCHITECTURE.md`
- `skills/joewrks-product-definition/agents/openai.yaml` only if its description/routing text conflicts with V2-first behavior.
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json` only to make it a correct native V2 starting state.

Create:

- `skills/joewrks-product-definition/references/workflow-v0.2.0.md`
- `skills/joewrks-product-definition/scripts/compile_downstream_v2.py`
- `skills/joewrks-product-definition/scripts/audit_downstream_v2.py`
- `skills/joewrks-product-definition/scripts/build_semantic_review_v2.py`
- `skills/joewrks-product-definition/scripts/verify_runtime_v2.py`
- `tests/test_v2_installed_workflow.py`

## Runtime verification

Create under `skills/joewrks-product-definition/downstream_v2/`:

- `runtime.py` — V2 contract-bound action/lifecycle runtime verification.
- `runtime_report.py` — deterministic aggregate implementation-conformance report.
- `schemas/runtime-conformance-report.schema.json` — report structure only; execution evidence remains frozen protocol 1.0.

Create tests:

- `tests/test_downstream_v2_runtime.py`
- `tests/test_downstream_v2_runtime_report.py`

## M6 dogfood and final evidence

Create:

- `evals/core-semantic-closure-v2-m6/README.md`
- `evals/core-semantic-closure-v2-m6/MIGRATION_AUDIT.md`
- `evals/core-semantic-closure-v2-m6/DOGFOOD_RUNBOOK.md`
- `evals/core-semantic-closure-v2-m6/R1_R10_TRACEABILITY.md`
- `evals/core-semantic-closure-v2-m6/FINAL_INTEGRATION_AUDIT.md`
- `evals/core-semantic-closure-v2-m6/dogfood/` artifacts described in Task 5.

Do not overwrite `product-definition/client-feedback-portal-dogfood/state.json`; that file remains the legacy v1 dogfood authority used by historical regressions. The V2 dogfood uses a new slug and its own state.

---

# Task 1 — Complete deterministic legacy-to-V2 migration

**Goal:** Convert a valid legacy `0.1.2.1` state into a real V2 reconciliation candidate without claiming V2 intent, closure, or approval.

**Files:**
- Modify: `skills/joewrks-product-definition/scripts/migration_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/migrate_state.py`
- Modify narrowly if required: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify narrowly if required: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Create: `skills/joewrks-product-definition/references/migration-v0.2.0.md`
- Create: `tests/test_migration_v020_apply.py`

**Interfaces:**

Keep existing:

```python
def build_migration_plan(state: dict[str, object]) -> dict[str, object]: ...
```

Add:

```python
MIGRATION_APPLY_VERSION = "0.2.0-m6.1"


def migrate_state_v020(
    legacy_state: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    """Return (v2_reconciliation_candidate, deterministic_receipt)."""


def verify_migration_result(
    legacy_state: dict[str, object],
    candidate: dict[str, object],
    receipt: dict[str, object],
) -> list[dict[str, object]]: ...
```

## Frozen migration invariants

The candidate must always start as:

```text
schema_version = 0.2.0
project.definition_status = OPEN
project.definition_revision = legacy.definition_revision + 1
project.bootstrap_mode = EXISTING_PRODUCT_RECONCILIATION
approval.status = UNAPPROVED
approval_history = []
discovery_baseline.status = NOT_ESTABLISHED
```

It must use the exact current Product/UX binding contract identities produced by `binding_contract_identity()`.

The legacy approval is **historical evidence only**. It must not be copied into current V2 `approval` or `approval_history`.

The candidate `migration` section uses either native mode:

```json
{"mode":"NATIVE"}
```

or migrated mode with deterministic provenance. If a schema extension is required, freeze migrated mode to exactly these fields:

```json
{
  "mode": "MIGRATED",
  "from_schema": "0.1.2.1",
  "to_schema": "0.2.0",
  "migration_version": "0.2.0-m6.1",
  "source_digest": "<sha256>",
  "source_revision": 44,
  "source_legacy_closure": "CLOSED | OPEN | STALE",
  "source_legacy_approval_digest": "<sha256-or-null>",
  "plan_digest": "<sha256>",
  "preserved_ids": ["..."],
  "generated_ids": ["..."],
  "reconciliation_gap_count": 0
}
```

Do **not** put an output-state digest inside the state itself. That would create a self-referential digest. The separate returned receipt may contain:

```text
candidate_state_sha256
```

computed after the candidate is complete.

Do not generate `migrated_at` from wall-clock time inside canonical state. Operational run time may appear in an external log, not in deterministic migration authority.

## Stable record mapping

Use deterministic field mappings only. A field may become current only when the V2 semantic field can be copied or losslessly normalized from explicit legacy content. Otherwise preserve the legacy ID as a non-current reconciliation record and create a dedicated migration unknown.

Freeze the direct mapping table:

| V2 type | Direct legacy mapping |
| --- | --- |
| GOAL | `text -> statement` |
| USR | `role -> actor_kind`; `description` is canonical text assembled only from existing `role/cardinality/identity` fields with field labels preserved |
| REQ | `text -> statement`; `ui_required -> ui_required` |
| DEC | explicit legacy decision/answer text -> `statement` only when present |
| RULE | legacy rule text/statement -> `statement` |
| FLOW | existing legacy entry/preconditions/paths/outcomes fields only |
| SCR | existing purpose/requirement refs/major actions fields only |
| STATE | existing state name/conditions only |
| DATA | existing name/purpose/ownership only |
| INT | existing name/purpose only |
| AC | existing assertion/text and requirement refs only |
| TASK | existing implements/acceptance refs only |

Do not infer missing meaning from field names, implementation code, industry conventions, or natural-language heuristics during migration.

If a required V2 semantic field has no direct mapping:

1. preserve the original stable ID;
2. make the migrated record non-current (`STALE` when that type permits it, otherwise the nearest explicit non-authoritative lifecycle state permitted by the V2 contract);
3. populate required structural fields only with a clearly machine-recognizable migration scaffold that is excluded from current semantic authority by lifecycle status;
4. generate exactly one `UNK-*` with `origin.kind = MIGRATION_RECONCILIATION` and exact `origin.source_path`;
5. record the source ID and missing semantic field in the migration receipt.

A migration scaffold must never be eligible for positive authority binding, Product Definition Closure, approval, or downstream source seeding.

## Materiality during migration

Legacy `material: true/false` is not enough to manufacture a V2 Materiality Assessment.

For any REQ/DEC/UNK that lacks an evidence-backed full V2 Materiality Assessment:

- keep the migrated authority non-current;
- create a migration reconciliation unknown for materiality;
- do not guess reversibility, fan-out, user visibility, or risk flags.

Tests must prove that a legacy material boolean alone never produces a CURRENT V2 materiality record.

## Legacy coverage migration

Every legacy Core/UX cell becomes a V2 reconciliation site:

- legacy `COVERED` → V2 `OPEN` with a migration unknown saying exact authority binding must be selected;
- legacy `N/A` → V2 `OPEN` with a migration unknown saying exact N/A basis must be selected;
- legacy `OPEN` → V2 `OPEN` preserving or deterministically linking the original unknown when possible.

Migration must never convert old `COVERED` directly to V2 `COVERED` because old coverage did not carry exact V2 pointer/hash authority binding.

All six specialist Grill topology categories begin `OPEN` with distinct migration-reconciliation unknowns unless a later reverse-bootstrap pass establishes an exact V2 ACTIVE/N/A disposition from evidence.

No specialist axis is marked `ADDRESSED` or `N/A` by migration alone.

## CLI

Preserve existing plan command exactly:

```text
python migrate_state.py --plan SOURCE_JSON
```

Add:

```text
python migrate_state.py --apply SOURCE_JSON --output DEST_JSON
```

Rules:

- source file is read-only;
- destination must not already exist;
- candidate JSON is written only after `verify_migration_result()` returns zero internal migration-integrity errors;
- stdout emits one canonical JSON receipt;
- expected migration/semantic gaps exit `0` because they are represented inside the candidate;
- invalid legacy source exits `1` with structured JSON;
- usage/read/write/JSON errors exit `2` without traceback.

### Task 1 tests

- [ ] **Step 1: Write RED tests for apply mode and source immutability.**

Required tests:

```python
def test_apply_produces_open_unapproved_v2_candidate(): ...
def test_apply_never_modifies_source_bytes(): ...
def test_apply_refuses_existing_destination(): ...
def test_apply_is_byte_deterministic_for_same_source(): ...
def test_apply_preserves_every_legacy_stable_id(): ...
def test_apply_does_not_copy_legacy_approval_as_v2_approval(): ...
```

Run:

```text
python -m unittest tests.test_migration_v020_apply -v
```

Expected before implementation: FAIL because apply mode does not exist.

- [ ] **Step 2: Implement the minimal candidate/receipt transformer.**

Implement candidate creation through explicit per-type mapping functions. Do not use generic natural-language inference.

- [ ] **Step 3: Add RED uncertainty-preservation tests.**

Required cases:

```python
def test_legacy_covered_cell_becomes_open_binding_reconciliation(): ...
def test_legacy_na_cell_becomes_open_basis_reconciliation(): ...
def test_legacy_material_boolean_never_manufactures_full_materiality(): ...
def test_six_grill_topology_domains_begin_open_without_v2_evidence(): ...
def test_generated_unknown_ids_are_deterministic_and_after_existing_max(): ...
def test_migration_unknown_origin_preserves_exact_source_path(): ...
```

- [ ] **Step 4: Implement reconciliation generation and migrated-state receipt validation.**

- [ ] **Step 5: Preserve plan-mode regression.**

Run:

```text
python -m unittest tests.test_migration_v020_foundation tests.test_migration_v020_apply -v
```

Both M1 plan-only semantics and M6 apply semantics must pass.

- [ ] **Step 6: Run V2/legacy focused regression and commit.**

Run:

```text
python -m unittest \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation \
  tests.test_migration_v020_apply \
  tests.test_legacy_v0121_frozen -v
```

Commit:

```text
feat: complete deterministic state v2 migration
```

---

# Task 2 — Add installed V2-first workflow routing without breaking legacy support

**Goal:** Make the installed skill use V2 by default and remove the M5 manual `PYTHONPATH` requirement for normal documented commands.

**Files:**
- Modify: `skills/joewrks-product-definition/SKILL.md`
- Modify: `README.md`
- Modify: `PROGRAM_ARCHITECTURE.md`
- Modify if needed: `skills/joewrks-product-definition/agents/openai.yaml`
- Modify narrowly: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- Create: `skills/joewrks-product-definition/references/workflow-v0.2.0.md`
- Create: `skills/joewrks-product-definition/scripts/compile_downstream_v2.py`
- Create: `skills/joewrks-product-definition/scripts/audit_downstream_v2.py`
- Create: `skills/joewrks-product-definition/scripts/build_semantic_review_v2.py`
- Create: `tests/test_v2_installed_workflow.py`

**Interfaces:**

Each installed wrapper resolves its own skill root from `Path(__file__).resolve()` and inserts only the required skill/package roots into `sys.path` before importing `downstream_v2`. The caller must not set persistent `PYTHONPATH`.

Wrappers preserve the M5 JSON/exit-code contract:

```text
compile_downstream_v2.py STATE_JSON HANDOFF_DEFINITION_JSON
audit_downstream_v2.py CONTRACT_JSON STATE_JSON
build_semantic_review_v2.py CONTRACT_JSON
```

## V2-first skill dispatch

Freeze `SKILL.md` routing to:

```text
new project
→ create from templates/state-v0.2.0.example.json
→ validate under state-v0.2.0.schema.json / V2 dispatcher

existing state schema 0.2.0
→ resume V2 workflow

existing state schema 0.1.2.1
→ validate with frozen legacy contract
→ do not silently migrate
→ offer/execute migration only when user asks to adopt V2
```

The workflow document must present the V2 lifecycle in plain language first:

```text
찾기 → 애매한 것 정하기 → 기준 고정 → 사용자 승인 → 구현 전달 → 구현 검증
DISCOVER → CLOSE → FREEZE → APPROVE → HANDOFF → VERIFY
```

Implementation ambiguity or downstream authority gaps return to DISCOVER/CLOSE for the affected scope.

## README user-facing wording

Keep the already approved easy-language introduction. Update technical sections so they no longer describe action-conformance/1.0 as the current V2 production path.

README must explicitly distinguish:

```text
Current Product Definition state contract: 0.2.0
Current V2 downstream authority contract: joewrks.action-conformance/2.0
Current V2 semantic review boundary: joewrks.semantic-review/2.0 / reliability NOT_MEASURED
Historical compatibility: state 0.1.2.1, action-conformance/1.0, semantic-review/1.0, v0.4.3 evidence
```

Do not call the overall program `v0.5` or another release number in M6.

### Task 2 tests

- [ ] **Step 1: Write RED installed-routing tests.**

Required tests invoke wrappers from a temporary consumer working directory with `PYTHONPATH` cleared:

```python
def test_v2_compile_wrapper_works_outside_repo_cwd_without_pythonpath(): ...
def test_v2_audit_wrapper_works_outside_repo_cwd_without_pythonpath(): ...
def test_v2_review_wrapper_works_outside_repo_cwd_without_pythonpath(): ...
def test_skill_default_template_is_v020(): ...
def test_skill_keeps_legacy_dispatch_explicit(): ...
```

- [ ] **Step 2: Implement wrappers and V2-first skill workflow.**

- [ ] **Step 3: Update README/architecture wording and add exact status markers.**

Required markers:

```text
PRODUCT_DEFINITION_STATE_V2_DEFAULT
LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED
DOWNSTREAM_V2_INSTALLED_ROUTING
SEMANTIC_REVIEW_V2_RELIABILITY_NOT_MEASURED
```

- [ ] **Step 4: Run package/skill regression and commit.**

Run:

```text
python -m unittest \
  tests.test_v2_installed_workflow \
  tests.test_skill_package \
  tests.test_state_contract_dispatch \
  tests.test_validators -v
```

Commit:

```text
feat: route installed product definition workflow to v2
```

---

# Task 3 — Add V2 runtime verification and implementation-conformance reports

**Goal:** Verify actual execution evidence against a materialized action-conformance/2.0 contract without changing the frozen execution transport or Product Definition authority.

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/runtime.py`
- Create: `skills/joewrks-product-definition/downstream_v2/runtime_report.py`
- Create: `skills/joewrks-product-definition/downstream_v2/schemas/runtime-conformance-report.schema.json`
- Create: `skills/joewrks-product-definition/scripts/verify_runtime_v2.py`
- Create: `skills/joewrks-product-definition/references/runtime-conformance-v0.2.0.md`
- Create: `tests/test_downstream_v2_runtime.py`
- Create: `tests/test_downstream_v2_runtime_report.py`
- Modify: `tests/test_v2_installed_workflow.py`

**Frozen transport dependency:**

Import and use, without modifying:

```python
from downstream.protocol import (
    PROTOCOL_VERSION,
    encode_typed_numbers,
    validate_execution_record,
)
```

`PROTOCOL_VERSION` must remain exactly:

```text
joewrks.downstream.execution/1.0
```

M6 is not allowed to publish `execution/2.0` merely for convenience.

**Interfaces:**

```python
class RuntimeVerificationError(ValueError):
    code: str
    detail: object


def semantic_value(field: dict[str, object]) -> object: ...


def verify_action_execution(
    contract: dict[str, object],
    record: dict[str, object],
) -> dict[str, object]: ...


def verify_lifecycle_execution(
    contract: dict[str, object],
    observation: dict[str, object],
) -> dict[str, object]: ...
```

`runtime_report.py` exports:

```python
RUNTIME_REPORT_VERSION = "joewrks.runtime-conformance-report/1.0"


def build_runtime_conformance_report(
    contract: dict[str, object],
    audit_result: dict[str, object],
    action_results: list[dict[str, object]],
    lifecycle_results: list[dict[str, object]],
    semantic_assurance: dict[str, object],
) -> dict[str, object]: ...
```

## Evidence admission

Before semantic evaluation, action execution requires:

```text
execution protocol valid under frozen joewrks.downstream.execution/1.0
record.product_slug == contract.source_authority.product_slug
record.contract_hash == contract.semantic_contract_hash
record.authority.approved_revision == contract.source_authority.approved_revision
record.authority.approved_digest == contract.source_authority.approved_definition_digest
record.command.action_id resolves exactly one contract action
```

Do not accept `artifact_hash` as runtime semantic authority identity.

## Action verification semantics

Port the already-proven generic v1 verification behavior into V2 code without changing v1 files:

- supported result classes: `SUCCESS`, `REJECTED`, `STALE`, `IDEMPOTENT_REPLAY`;
- `input_invariants` determines rejection when violated;
- otherwise `default_result` supplies the expected class unless the test explicitly declares an allowed expected class;
- `result_expectations` must define all five snapshot components:
  - `authoritative_state`
  - `revision`
  - `history`
  - `business_side_effects`
  - `delivery_effects`;
- each component expectation is exactly `CHANGED | UNCHANGED | ANY`;
- evidence assertions use the existing supported assertion vocabulary only:
  - `path_present`
  - `path_absent`
  - `path_equals`
  - `collection_item_field_equals`.

M6 verifier reads each V2 semantic field as `field["value"]`. It never re-derives Product Definition meaning.

If runtime-critical values are not structurally executable, return `RUNTIME_CONTRACT_NOT_EXECUTABLE`; do not reinterpret prose.

## Aggregate status

A runtime report has independent dimensions:

```text
contract_dependency_status:
  CONFORMANT | REENTRY_REQUIRED | DEFINITION_NOT_READY

runtime_status:
  NOT_RUN | CONFORMANT | NON_CONFORMANT

review_completion:
  NOT_REQUIRED | PENDING | REVIEW_OUTPUT_RECORDED | REENTRY_REQUIRED

semantic_review_reliability:
  NOT_REQUIRED | NOT_MEASURED
```

`implementation_status = IMPLEMENTATION_CONFORMANT` only when:

1. dependency audit is `CONFORMANT`;
2. all required action/lifecycle runtime evidence for the declared dogfood/test scope is present;
3. every runtime result is conformant;
4. no blocking re-entry event exists;
5. semantic review is `NOT_REQUIRED` or has a structurally valid recorded output;
6. no claim is made that semantic-review/2.0 is reliable.

If REVIEW_REQUIRED exists and review output is merely recorded, `IMPLEMENTATION_CONFORMANT` means the implementation matches the recorded contract value. The report must still state `semantic_review_reliability = NOT_MEASURED`.

### Task 3 tests

- [ ] **Step 1: Write RED authority-binding tests.**

```python
def test_runtime_record_requires_semantic_contract_hash(): ...
def test_runtime_record_rejects_artifact_hash_as_contract_identity(): ...
def test_runtime_record_requires_exact_approved_definition_digest(): ...
def test_runtime_record_requires_exact_action_id(): ...
```

- [ ] **Step 2: Implement evidence admission and semantic-value reading.**

- [ ] **Step 3: Write RED execution semantics tests.**

At minimum:

```python
def test_success_component_expectations_can_pass(): ...
def test_rejected_invariant_is_verified(): ...
def test_stale_result_is_verified(): ...
def test_idempotent_replay_is_verified(): ...
def test_unexpected_side_effect_fails_conformance(): ...
def test_runtime_critical_prose_fails_closed_not_interpreted(): ...
```

- [ ] **Step 4: Implement action/lifecycle verifier.**

- [ ] **Step 5: Write RED aggregate report tests.**

```python
def test_all_deterministic_runtime_evidence_produces_implementation_conformant(): ...
def test_local_dependency_reentry_blocks_implementation_conformance(): ...
def test_runtime_failure_produces_non_conformant(): ...
def test_review_recorded_does_not_change_not_measured_reliability(): ...
```

- [ ] **Step 6: Implement report and installed wrapper.**

`verify_runtime_v2.py` input:

```text
python verify_runtime_v2.py CONTRACT_JSON CURRENT_STATE_JSON EXECUTION_JSONL [REVIEW_PACKAGE_JSON REVIEW_OUTPUT_JSON]
```

It must emit canonical JSON on stdout, empty stderr for semantic outcomes, exit `0` only when `implementation_status = IMPLEMENTATION_CONFORMANT`, exit `1` for valid non-conformance/re-entry/not-ready outcomes, and exit `2` for usage/read/JSON errors.

- [ ] **Step 7: Run runtime + M5 regressions and commit.**

Run:

```text
python -m unittest \
  tests.test_downstream_v2_runtime \
  tests.test_downstream_v2_runtime_report \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_reentry \
  tests.test_downstream_v2_semantic_review \
  tests.test_v2_installed_workflow -v
```

Commit:

```text
feat: verify runtime evidence against downstream v2 authority
```

---

# Task 4 — Integrate documented re-entry handling without automatic product decisions

**Goal:** Connect M5 re-entry artifacts to the installed Product Definition workflow while preserving the rule that re-entry proposals are not canonical authority.

**Files:**
- Create: `skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md`
- Modify: `skills/joewrks-product-definition/references/workflow-v0.2.0.md`
- Modify: `skills/joewrks-product-definition/SKILL.md`
- Create: `tests/test_v2_reentry_workflow_contract.py`

M6 does **not** add a general-purpose script that blindly writes candidate unknowns into `state.json`.

The installed workflow must distinguish:

### A. Implementation mismatch with clear existing authority

```text
runtime mismatch
→ contract/local dependency still exact
→ Product Definition authority is already clear
→ implementation correction required
→ do not create a new product decision merely to explain a code bug
```

The mismatch may be stored as observed implementation/runtime evidence when useful, but it does not automatically require revision/approval changes.

### B. Downstream semantic authority gap or real ambiguity

```text
re-entry artifact
→ inspect exact affected authority/evidence
→ register the event as evidence if needed
→ create a canonical UNK only when a real unresolved product question remains
→ increment definition_revision before semantic authority changes
→ set approval UNAPPROVED
→ re-run affected discovery / Grill / binding / approval flow
```

Candidate unknown content from `joewrks.product-definition-reentry/1.0` is suggestion text only. The agent must not copy it into canonical authority without evidence/unknown registration semantics.

### C. Out-of-scope implementation request

An `OUT_OF_SCOPE_REQUEST` does not become in-scope merely because an implementation agent requested it. Product Definition must resolve scope first.

### Task 4 tests

Tests are contract/document routing tests rather than fake product-decision tests:

```python
def test_skill_says_clear_authority_runtime_bug_requires_implementation_fix_not_new_decision(): ...
def test_skill_says_semantic_gap_reenters_product_definition(): ...
def test_candidate_unknown_is_never_described_as_canonical_authority(): ...
def test_out_of_scope_request_requires_scope_resolution(): ...
```

Run:

```text
python -m unittest tests.test_v2_reentry_workflow_contract tests.test_v2_installed_workflow -v
```

Commit:

```text
docs: integrate downstream reentry into v2 workflow
```

---

# Task 5 — Run representative existing-product V2 dogfood with real user approval checkpoint

**Goal:** Prove the complete V2 workflow on an existing product boundary without modifying the legacy dogfood authority or inventing approval.

**Dogfood source boundary:**

Use the existing legacy project and its repository evidence as the source boundary:

```text
product-definition/client-feedback-portal-dogfood/state.json
product-definition/client-feedback-portal-dogfood/*.md
evals/downstream-conformance-v0.4.1/ historical evidence as OBSERVED behavior evidence only
```

Do not edit those historical source files.

Create a new V2 dogfood slug:

```text
client-feedback-portal-dogfood-v2
```

Canonical dogfood working state during M6:

```text
evals/core-semantic-closure-v2-m6/dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json
```

This is an evaluation artifact, not a replacement for the legacy project state.

## Dogfood scope

Use a deliberately inspectable but material slice of the existing product containing at minimum:

- one current goal;
- both Designer and Client Reviewer actor meaning where applicable;
- one authentication/permission-sensitive requirement;
- one feedback/thread state-changing requirement;
- at least one screen with a major action;
- persistence/state/permission/recovery semantics;
- one acceptance criterion and implementation task per material requirement;
- applicable AUTH/PERMISSION/ASYNC or DESTRUCTIVE Grill packs as discovered from evidence.

The slice must be selected from existing documented product meaning. Do not invent a new feature to make the dogfood easier.

## Phase A — migration and reverse bootstrap

- [ ] **Step 1: Run the complete migrator against the legacy dogfood state.**

Store candidate and receipt under:

```text
evals/core-semantic-closure-v2-m6/dogfood/migration/
```

Verify:

- all legacy IDs preserved;
- old approval is historical only;
- candidate is OPEN/UNAPPROVED;
- no old COVERED cell became V2 COVERED automatically;
- migration unknown origins keep source paths.

- [ ] **Step 2: Reconcile only the selected dogfood scope using existing evidence.**

For every product meaning promoted to CURRENT V2 authority, cite a first-class V2 evidence record from documented legacy intent/user decisions or an explicit current user answer. Observed implementation/runtime may support behavioral facts but cannot create intent.

- [ ] **Step 3: Run the complete V2 discovery + Grill + exact binding flow.**

The selected scope must reach:

```text
READY_FOR_REVIEW + UNAPPROVED
```

with:

```text
validate_state.py = valid
build_approval_manifest.py = success
semantic readiness blockers = 0
```

If a real material unknown survives evidence inspection, STOP and report it to the user rather than filling it with a dogfood fixture answer.

## Mandatory PM approval checkpoint

- [ ] **Step 4: STOP before approval.**

Output exactly:

```text
CORE_SEMANTIC_CLOSURE_V2_M6_APPROVAL_REQUIRED
— DOGFOOD_V2_MANIFEST_READY
```

Report:

- dogfood state path;
- definition revision;
- definition digest;
- Approval Manifest digest;
- full user-facing Approval Manifest;
- added/changed/retired/high-risk/deferred items;
- remaining nonblocking semantic-review items;
- evidence/source summary;
- confirmation that approval is still `UNAPPROVED`;
- confirmation no downstream contract or runtime conformance was fabricated before approval.

Then STOP and wait for explicit user approval.

**No later Task-5 step may execute in the same run before that approval arrives.**

## Phase B — only after explicit user approval

The continuation run receives the exact approved manifest digest and an explicit supplied UTC approval timestamp associated with the user's approval message.

- [ ] **Step 5: Record the exact approval and prove Product Definition Closure.**

After recording approval:

```text
validate_state.py = valid
validate_closure.py → closed = true
```

- [ ] **Step 6: Compile action-conformance/2.0 for the selected dogfood scope.**

Prefer a contract with `authority_gap_count = 0` and `review_required_count = 0` for the final runtime gate. If the genuine dogfood semantics require REVIEW_REQUIRED, do not downgrade them; build the exact semantic-review/2.0 package and keep reliability `NOT_MEASURED`.

- [ ] **Step 7: Exercise one real re-entry path.**

Use one of these evidence-backed cases, in priority order:

1. an actual semantic authority gap found during handoff;
2. an actual contract/local dependency conflict found during audit;
3. if neither occurs naturally, a controlled test copy of the handoff definition with one field changed to `UNRESOLVED` using an existing dogfood authority scope.

The controlled case is an integration test only and must never be written into the approved dogfood state.

Verify that:

- re-entry is `AFFECTED_ONLY`;
- unrelated action/lifecycle scope is not halted;
- the event is a proposal, not canonical authority;
- after removing the controlled test mutation, the approved state/contract remains unchanged.

- [ ] **Step 8: Run deterministic runtime verification on the approved dogfood contract.**

Create a small deterministic local implementation fixture under:

```text
evals/core-semantic-closure-v2-m6/dogfood/runtime-fixture/
```

It must implement behavior already defined by the selected product scope; it must not invent product policy.

Produce frozen `joewrks.downstream.execution/1.0` JSONL evidence bound to the V2 semantic contract hash and approved definition digest.

Verify both:

```text
expected conformant implementation → IMPLEMENTATION_CONFORMANT
controlled implementation drift → NON_CONFORMANT or REENTRY_REQUIRED
```

Restore the conformant fixture before committing final dogfood evidence.

- [ ] **Step 9: Write dogfood evidence and commit.**

Store:

```text
dogfood/final-state.json
dogfood/approval-manifest.json
dogfood/handoff-definition.json
dogfood/action-contract-v2.json
dogfood/runtime-evidence.jsonl
dogfood/runtime-conformance-report.json
dogfood/reentry-probe.json
dogfood/dogfood-summary.md
```

No file may contain secrets, host-specific absolute paths, or mutable scratch data.

Commit:

```text
test: dogfood Core Semantic Closure V2 integration
```

---

# Task 6 — Final R1–R10 integration and compatibility gate

**Goal:** Prove that the full redesign is integrated, historically compatible, documented, and ready for merge without overstating semantic-review reliability or deployment status.

**Files:**
- Create/update: `evals/core-semantic-closure-v2-m6/README.md`
- Create: `evals/core-semantic-closure-v2-m6/MIGRATION_AUDIT.md`
- Create: `evals/core-semantic-closure-v2-m6/R1_R10_TRACEABILITY.md`
- Create: `evals/core-semantic-closure-v2-m6/FINAL_INTEGRATION_AUDIT.md`
- Modify: `README.md`, `PROGRAM_ARCHITECTURE.md`, `skills/joewrks-product-definition/SKILL.md` only for final M6 status wording if not already complete.
- Add only focused integration tests required by findings; do not broaden architecture.

## R1–R10 traceability matrix

The final matrix must map each remediation goal to code, tests, and dogfood evidence:

```text
R1  Semantic Closure Contract
R2  Definition Surface
R3  Evidence Graph
R4  Decision Integrity
R5  Materiality & Autonomy
R6  Reverse Bootstrap
R7  Informed Approval
R8  Adaptive Grill Packs
R9  Semantic Debt Reduction
R10 Lifecycle / Migration / Re-entry integration
```

Every row must contain:

```text
implemented files
test files
dogfood/evidence artifact
final status
known limitation
```

No row may be marked complete solely because a design document exists.

## Final compatibility gates

Run focused M6 tests first, then every earlier milestone regression, then the full suite.

At minimum run:

```text
python -m unittest \
  tests.test_migration_v020_apply \
  tests.test_v2_installed_workflow \
  tests.test_v2_reentry_workflow_contract \
  tests.test_downstream_v2_runtime \
  tests.test_downstream_v2_runtime_report -v
```

Run complete M5 regression:

```text
python -m unittest \
  tests.test_downstream_v2_authority \
  tests.test_downstream_v2_seeds \
  tests.test_downstream_v2_derivation \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_semantic_debt \
  tests.test_downstream_v2_reentry \
  tests.test_downstream_v2_semantic_review \
  tests.test_downstream_v2_cli \
  tests.test_downstream_v2_frozen_boundaries -v
```

Run M4/M3/M2/V2 core regression using the same test groups frozen in prior milestone plans.

Run legacy/downstream-v1/semantic-review-v1 regressions.

Run full repository:

```text
python -m unittest discover -s tests -v
```

Run:

```text
git diff --check
```

## Mandatory source-tree checks

Verify exact frozen trees/blobs at final HEAD:

```text
skills/joewrks-product-definition/downstream/
= b63568d8c4632b14bc806e7bff1908e94dea9669

evals/semantic-review-v0.4.3/
= a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
```

Verify all four legacy 0.1.2.1 blobs exact.

Verify old project:

```text
product-definition/client-feedback-portal-dogfood/state.json
```

still has its original legacy blob; the V2 dogfood must not replace it.

## Final semantic claims

M6 may claim only what fresh evidence supports.

If all gates pass, allowed claims are:

```text
CORE_SEMANTIC_CLOSURE_V2_INTEGRATED
STATE_0_2_WORKFLOW_ADOPTED
DOWNSTREAM_V2_AUTHORITY_INTEGRATED
RUNTIME_CONFORMANCE_PATH_VERIFIED
R1_R10_INTEGRATION_VERIFIED
READY_FOR_MERGE
```

The final report must still state:

```text
semantic-review/2.0 reliability = NOT_MEASURED
v0.4.3 calibration disposition = unchanged
production deployment = NOT_CLAIMED unless separately executed
main merge = NOT_PERFORMED
```

Do not call the overall program `v0.5` without a separate release/version decision.

## Final report

If and only if all Task 1–6 gates, the dogfood approval checkpoint, runtime verification, regressions, frozen boundaries, and final read-only review pass, push only the M6 implementation branch and report:

```text
CORE_SEMANTIC_CLOSURE_V2_M6_IMPLEMENTED
— INTEGRATION_ADOPTION / R1_R10_VERIFIED / READY_FOR_MERGE
```

Include:

- branch;
- planning/base SHA;
- final HEAD/parent/tree/remote SHA;
- changed-file count/list;
- per-task commits;
- migration plan/apply determinism probes;
- preserved-ID and no-confidence-increase migration probes;
- installed V2 routing probe from external cwd;
- M6 runtime focused tests;
- M5/M4/M3/M2 regressions;
- downstream v1 + semantic-review v1/v0.4.3 regressions;
- legacy/frozen regressions;
- full-suite result and all skips/reasons;
- `git diff --check`;
- frozen tree/blob verification;
- dogfood definition revision/digest/manifest digest;
- explicit user approval evidence reference;
- dogfood action-conformance/2.0 semantic hash;
- consumed seed/scope commitment counts;
- semantic debt counts;
- re-entry affected-only probe;
- runtime conformant and controlled-drift probes;
- R1–R10 traceability status;
- semantic-review/2.0 `NOT_MEASURED` confirmation;
- local/remote main SHA;
- confirmation no merge/PR was performed.

Then STOP.

Do not merge to `main` until explicit user review/approval of the M6 result.
