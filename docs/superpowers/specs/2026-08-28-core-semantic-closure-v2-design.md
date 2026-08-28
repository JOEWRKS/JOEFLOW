# Core Semantic Closure V2 — Design Specification

**Status:** `WRITTEN_SPEC_PENDING_FINAL_USER_REVIEW`

**State contract target:** `0.2.0`

**Program:** `JOEWRKS Product Definition System`

**Purpose:** Strengthen the Product Definition core so that a project cannot be treated as “closed” merely because its known fields and checklists are filled. V2 makes discovery scope, evidence, material decisions, coverage, approval, and downstream meaning part of one traceable authority model.

---

## 1. Plain-language product definition

JOEWRKS Product Definition System is:

> **A product planning and verification tool that keeps AI from missing important things or making important product decisions on its own.**

In plain terms, it does four things:

1. **Find what is missing.** It looks for important conditions, exceptions, states, and decisions that were not explicitly described.
2. **Clarify what matters.** It researches what can be proven from evidence and asks the user only when a real product decision still remains.
3. **Keep the decisions as the source of truth.** Once something important is decided, it becomes canonical product authority instead of being left in chat history or implementation guesses.
4. **Check the result.** It verifies that design, code, and runtime behavior still match what was decided.

The core rule is:

> **Let AI build on its own, but do not let AI invent important product meaning on its own.**

This specification uses more technical language below, but every technical mechanism must serve that simple rule.

---

## 2. Why V2 is needed

The legacy `state.json` contract (`0.1.2.1`) successfully prevents many forms of false closure: open unknowns, stale artifacts, missing UX states, unmapped acceptance criteria, invalid approval, and incomplete known coverage all block Closure.

However, several remaining gaps are architectural rather than test gaps:

- A coverage cell can say `COVERED` without binding that claim to the exact canonical authority that makes it covered.
- Known requirements can be checked thoroughly while the product surface itself may still be incomplete.
- Evidence-first discovery is a workflow rule, but evidence is not yet a strong first-class canonical contract.
- Materiality can be reduced to a weak boolean instead of an auditable decision about whether AI may decide autonomously.
- Existing implementation can be observed without a strong contract separating “what exists” from “what was intended.”
- Unknown resolution, decisions, and downstream authority are not linked strongly enough to prove how a gray area was actually closed.
- Approval proves that a revision digest was approved, but not that the user was shown the material changes that revision contains.
- Too much semantic interpretation can be deferred downstream as `REVIEW_REQUIRED` instead of first asking whether Product Definition should have made the meaning explicit upstream.
- The fixed core coverage taxonomy cannot scale by endlessly adding every domain-specific edge case.
- Legacy lifecycle and migration rules need a deterministic path to a stronger contract without rewriting history.

V2 addresses these design gaps without rewriting frozen v0.4.3 evidence or redefining existing v1 downstream contracts.

---

## 3. Core principles and non-negotiable invariants

### 3.1 One canonical authority

There is still exactly one canonical Product Definition state per project:

```text
product-definition/<project-slug>/state.json
```

No second `authority-graph.json`, `evidence.json`, or other competing source of truth is introduced. Evidence, discovered surfaces, contradictions, decisions, coverage bindings, discovery commitments, and approval are all represented inside the same canonical state.

### 3.2 Internally exhaustive, externally selective

The system should search broadly for gray areas internally while keeping user interruption minimal.

- If evidence resolves a question, do not ask the user.
- If a decision is truly non-material and safely reversible, keep it inside the allowed AI autonomy boundary.
- If a product choice materially changes user-visible behavior or risk, bring it to the user.
- Ask one highest-leverage material question at a time.

A stronger Grill must not become a question bomb.

### 3.3 No manufactured certainty

> **Migration, reverse bootstrap, summarization, and inference may expose uncertainty but may never manufacture authority.**

Observed implementation is evidence of implementation, not automatic evidence of product intent.

Absence of implementation is not evidence that something is intentionally out of scope.

### 3.4 Closure is procedural, not omniscient

V2 may claim that the defined discovery procedure, applicable surface classes, and activated Grill Packs were completed.

It must never claim that all theoretically possible unknown-unknowns in the world were discovered.

### 3.5 Structure what changes outcomes

Product meaning that changes behavior, permissions, data, money, lifecycle, validation, or other material outcomes should be structured when feasible.

Prose remains first-class authority when prose is the actual meaning—for example brand tone or a qualitative visual intention. V2 must not turn Product Definition into a giant rigid DSL merely for the sake of machine derivation.

### 3.6 Semantic Review is a last line of assurance, not a dumping ground

If downstream ambiguity could reasonably have been represented as canonical structured authority upstream, it is a Product Definition authority gap and must re-enter Product Definition.

It must not be converted into `REVIEW_REQUIRED` merely because interpretation is inconvenient.

### 3.7 Historical contracts remain historical

The following remain frozen and are not silently redefined by V2:

```text
state schema 0.1.2.1
joewrks.action-conformance/1.0
joewrks.semantic-review/1.0
v0.4.3 calibration evidence and disposition
```

New semantics require new contract identities.

---

# Part I — Authority and compatibility

## 4. State contract versioning

V2 introduces:

```text
schema_version = 0.2.0
closure level = SEMANTIC_CLOSURE
```

Program release numbering and state schema numbering remain separate. `0.2.0` is the state-contract version, not a declaration that the overall program release is v0.2.

Legacy and V2 Closure are intentionally distinguished:

```text
0.1.2.1 CLOSED → LEGACY_CLOSURE
0.2.0 CLOSED   → SEMANTIC_CLOSURE
```

A legacy `CLOSED` state remains valid under its own frozen contract. It does not automatically satisfy V2 Semantic Closure.

## 5. Canonical V2 top-level shape

The target state model contains these major sections:

```json
{
  "schema_version": "0.2.0",
  "project": {},
  "migration": {},
  "evidence": [],
  "surface_manifest": {},
  "contradictions": [],
  "objects": {},
  "coverage": [],
  "ux_coverage": [],
  "discovery_baseline": {},
  "approval": {},
  "approval_history": []
}
```

The exact JSON Schema is an implementation deliverable, but the semantic responsibilities in this specification are normative.

## 6. Stable identifiers

V2 keeps stable typed IDs and extends the namespace:

```text
GOAL-*  USR-*  REQ-*  UNK-*  DEC-*  RULE-*  FLOW-*  SCR-*
STATE-* DATA-* INT-*  AC-*   TASK-*
EVD-*   SURF-* CON-*
```

IDs are globally unique across the entire state.

The numeric suffix changes from exactly three digits to three or more digits:

```regex
^[A-Z]+-[0-9]{3,}$
```

Existing IDs are never renumbered.

## 7. Lifecycle states

Normal product-authority records use:

```text
CURRENT
STALE
SUPERSEDED
RETIRED
```

`SUPERSEDED` means the concept still exists but a newer same-type record replaces the old authority.

`RETIRED` means the concept was intentionally removed from current product scope. Retirement requires an explicit decision, retirement reason, and retirement revision.

Retiring an upstream record does not automatically retire its dependents. Dependents become `STALE` and must be explicitly reconciled to `CURRENT`, `SUPERSEDED`, or `RETIRED`.

---

# Part II — Discover

## 8. Product Surface Manifest

V2 introduces a first-class Product Surface Manifest so that the system checks not only whether known requirements are complete, but also whether discovered product surface has been explicitly handled.

Each discovered surface gets a stable `SURF-*` ID and a `kind`, such as:

```text
ACTOR
FEATURE_AREA
ENTRY_POINT
MAJOR_ACTION
DOMAIN_ENTITY
INTEGRATION
ASYNC_PROCESS
NOTIFICATION
PERSISTENT_STATE
SENSITIVE_DATA
PERMISSION
MONEY_FLOW
DESTRUCTIVE_OPERATION
LIFECYCLE_OBJECT
```

Each surface is explicitly disposed as one of:

```text
IN_SCOPE
OUT_OF_SCOPE
OPEN
SUPERSEDED
RETIRED
```

### 8.1 `IN_SCOPE`

An in-scope material surface must bind to current downstream Product Definition authority such as `REQ`, `RULE`, `FLOW`, `DATA`, or `INT`.

An in-scope surface with no authority path is an `UNBOUND_PRODUCT_SURFACE` blocker.

### 8.2 `OUT_OF_SCOPE`

Out-of-scope status requires a meaningful rationale and evidence or decision basis.

“Not implemented today” is not sufficient evidence of out-of-scope intent.

### 8.3 `OPEN`

An open material surface must point to at least one `UNK-*` explaining what remains unresolved.

### 8.4 Discovery assurance boundary

Closure may record:

```json
{
  "procedure_complete": true,
  "applicable_surface_classes_complete": true,
  "active_grill_packs_complete": true,
  "unknown_unknown_exhaustiveness_claimed": false
}
```

This is a deliberate epistemic boundary.

## 9. First-class Evidence Graph

Evidence becomes a canonical typed record using `EVD-*` IDs.

Minimum concepts include:

```text
source_kind
locator
observed revision/version when available
content hash when available
claim
confidence
status
```

Supported initial `source_kind` values include:

```text
USER_CONFIRMED_INTENT
DOCUMENTED_INTENT
HISTORICAL_DECISION
EXTERNAL_CONSTRAINT
OBSERVED_IMPLEMENTATION
OBSERVED_RUNTIME
TEST_ASSERTION
DESIGN_ARTIFACT
INFERRED_INTENT
```

Evidence status uses:

```text
CURRENT
STALE
SUPERSEDED
UNAVAILABLE
```

### 9.1 Evidence authority classes

Evidence also declares the class of claim it can support, for example:

```text
FACTUAL
INTENT
CONSTRAINT
BEHAVIORAL
PREFERENCE
```

The validator must reject attempts to use evidence for a stronger kind of claim than that evidence is permitted to support.

For example, `OBSERVED_IMPLEMENTATION` may prove current behavior but cannot, by itself, close a product-preference decision as intended policy.

### 9.2 Evidence drift

Where the evidence source can be versioned or hashed, the state stores its commitment. If consumed evidence drifts, dependent semantic authority must become stale and approval must be invalidated when product meaning is affected.

Unconsumed evidence may change without automatically invalidating Product Definition approval.

## 10. Typed contradictions

Contradictions use `CON-*` records rather than unstructured objects.

A contradiction records:

```text
claim_a_refs
claim_b_refs
scope_refs
materiality
status
resolution
resolved_by
selected_authority_refs
```

A material contradiction may close only when the system records which authority was selected or which explicit decision resolved the conflict.

Acknowledging a contradiction without resolving authority is not closure.

## 11. Reverse bootstrap contract

Discovery declares one of:

```text
NEW_PRODUCT
EXISTING_PRODUCT_RECONCILIATION
```

An existing product follows:

```text
Evidence
→ Observed Product Surface
→ Intent Classification
→ Reconciliation
→ Canonical Authority
```

Observed items are classified as:

```text
AUTHORITATIVE
OBSERVED_ONLY
CONFLICTING
UNEXPLAINED
```

- `AUTHORITATIVE`: supported by valid product intent authority.
- `OBSERVED_ONLY`: exists in code/runtime but intent is not established.
- `CONFLICTING`: implementation conflicts with stronger authority.
- `UNEXPLAINED`: exists without a known requirement or rationale.

Material `OBSERVED_ONLY` and `UNEXPLAINED` items produce unknowns or reconciliation work instead of silently becoming requirements.

## 12. Discovery baseline

After discovery procedure completion, the state records a digest-bound baseline containing at least:

```text
definition revision
surface manifest digest
evidence commitment digest
active Grill Pack set
open material surface count
unresolved material contradiction count
```

The baseline means the defined discovery process was completed against the current evidence and topology. It does not mean future discovery is impossible.

A new material ambiguity makes the baseline stale and reopens Product Definition.

---

# Part III — Close: Grill Engine V2

## 13. Unknown lifecycle and resolution mode

Unknown lifecycle state is separated from resolution mechanism.

Unknown lifecycle:

```text
OPEN
RESOLVED
DEFERRED
BLOCKED
SUPERSEDED
RETIRED
```

Resolution modes:

```text
EVIDENCE
USER_DECISION
USER_ACCEPTED_RECOMMENDATION
AGENT_NON_MATERIAL_DEFAULT
EXTERNAL_CONSTRAINT
MIGRATION_RECONCILIATION
```

Every resolved material unknown must have traceable resolution provenance.

If human judgment is required, the normal authority chain is:

```text
UNK → DEC → affected canonical authority
```

If a factual external constraint resolves the unknown, evidence may resolve it without creating a product decision.

## 14. Typed decisions

A current decision must contain at least:

```text
id
status
statement
decision_type
resolution_mode
decision_authority
source_unknown_refs
evidence_refs
materiality
affects
decided_by / decided_at where applicable
```

A semantically empty decision is invalid.

## 15. Materiality Assessment

The weak `material: false` escape hatch is removed.

Materiality is an explicit assessment over at least:

```text
outcome_divergence: NONE | LOW | MEDIUM | HIGH
fan_out: LOCAL | MULTI_OBJECT | MULTI_FLOW | SYSTEMIC
user_visible: boolean
reversibility: TRIVIALLY_REVERSIBLE | REVERSIBLE | COSTLY_TO_REVERSE | IRREVERSIBLE
risk flags:
  security
  privacy
  money
  legal_or_policy
  destructive
  data_loss
  external_commitment
classification: MATERIAL | NON_MATERIAL
```

The classifier must deterministically treat high-risk and high-outcome-divergence cases as material. A record cannot become non-material merely by asserting a boolean.

## 16. Decision authority / autonomy policy

Every unresolved decision is assigned one authority class:

```text
EVIDENCE_RESOLVABLE
AGENT_AUTONOMOUS
USER_CONFIRMATION
USER_DECISION_REQUIRED
EXTERNAL_AUTHORITY_REQUIRED
```

### 16.1 Policy table

| Situation | Required behavior |
| --- | --- |
| Sufficient authoritative evidence exists | Resolve without asking |
| Non-material, local, trivially reversible detail | Agent may decide within autonomy boundary |
| Material choice with a strong recommendation | Ask for user confirmation |
| Material choice that changes product meaning | Explicit user decision required |
| High-risk or externally constrained decision | User/external authority required |
| External constraint is missing | Block instead of guessing |
| Evidence conflicts | Resolve contradiction first |

`MATERIAL + AGENT_NON_MATERIAL_DEFAULT` is invalid and must raise `UNAUTHORIZED_AUTONOMOUS_PRODUCT_DECISION`.

## 17. Recommendations

A material recommendation is structured rather than being an untracked prose hint.

It includes:

```text
recommended_option
reasoning_refs
tradeoffs
confidence
alternatives_presented where applicable
```

When a user accepts an AI recommendation, the resolution mode is `USER_ACCEPTED_RECOMMENDATION`, not `USER_DECISION` or an implicit assumption.

## 18. User question policy

Questions are projections, not canonical authority objects.

Canonical state stores the unknown, evidence, options/recommendation, decision, and resolution. Question wording may change without changing Product Definition meaning.

The system asks one high-leverage material question at a time, ranking by:

```text
1. unlocks other unknowns
2. high risk
3. high fan-out
4. core flow
5. scope boundary
6. state/recovery
7. secondary behavior
8. preference
9. cosmetic detail
```

## 19. Adaptive Grill Packs

V2 keeps a universal Core Grill and adds topology-triggered specialist packs.

### 19.1 Core Grill

The existing 20 product axes remain the baseline:

```text
actor
goal
entry_point
precondition
happy_path
alternative_path
error
recovery
permission
state
data
side_effect
notification
validation
boundary
persistence
security
privacy
analytics
acceptance
```

### 19.2 Initial specialist packs

Initial versioned packs are:

```text
AUTH
MONEY
FILE_UPLOAD
ASYNC
PERMISSION
DESTRUCTIVE_ACTION
```

Each pack defines declaratively:

```text
pack_id
version
digest
trigger_conditions
surface requirements
required axes
materiality overrides
recommended unknown patterns
closure conditions
```

Suggested initial specialist areas are:

- **AUTH:** registration, verification, login/logout, expiry/renewal, recovery, revocation, role change, provider failure, duplicate identity, account linking.
- **MONEY:** currency, price authority, tax, discounts, payment failure, duplicate payment, refund/partial refund, cancellation, chargeback, settlement, receipt.
- **FILE_UPLOAD:** type, size, quota, malware handling, processing, partial failure, resume, retention, deletion, ownership, download permission.
- **ASYNC:** pending, polling, timeout, retry, idempotency, duplicate execution, late/partial completion, cancel, reconciliation.
- **PERMISSION:** role, ownership, read/write/delete, delegation, revocation, mid-flow role changes, stale permission, audit.
- **DESTRUCTIVE_ACTION:** confirmation, reason, undo, grace period, dependency effects, irreversible boundary, audit, notification.

Triggered packs activate automatically. An agent cannot suppress a required pack for convenience. N/A is handled at the axis level with justified bindings, not by disabling an applicable pack.

## 20. Grill closure blockers

V2 adds blockers including:

```text
open_material_unknowns
unresolved_unknown_provenance
invalid_resolution_authority
unassessed_materiality
unauthorized_agent_decisions
missing_required_user_decisions
active_grill_pack_gaps
unresolved_pack_axes
```

---

# Part IV — Freeze: Typed Authority and Semantic Coverage

## 21. Typed Product Definition objects

The generic “any object with `id` and `status`” model is removed for V2.

Each type has required semantic payload. Minimum responsibilities include:

| Type | Required semantic meaning |
| --- | --- |
| `GOAL` | `statement` |
| `USR` | `description`, `actor_kind` |
| `REQ` | `statement`, `materiality`, `scope`, `ui_required` |
| `DEC` | `statement`, resolution and authority provenance |
| `RULE` | `statement`, `applies_to` |
| `FLOW` | `goal_refs`, `entry`, `preconditions`, `paths`, `outcomes` |
| `SCR` | `purpose`, `requirement_refs`, interaction mode, action inventory |
| `STATE` | `owner_refs`, `state_name`, `conditions` |
| `DATA` | `name`, `purpose`, `ownership` |
| `INT` | `name`, `purpose`, external authority references where applicable |
| `AC` | `requirement_refs`, `assertion` |
| `TASK` | `implements`, `acceptance_refs` |

The implementation schema may add further required fields, but it may not weaken these semantic minima.

## 22. Coverage as proof, not a checkbox

V2 keeps the human-readable states:

```text
COVERED
OPEN
N/A
```

but strengthens their meaning.

### 22.1 `COVERED`

A covered cell requires at least one exact authority binding:

```json
{
  "status": "COVERED",
  "authority_bindings": [
    {
      "record_id": "RULE-014",
      "pointer": "/statement",
      "value_sha256": "..."
    }
  ]
}
```

Every binding must resolve to an existing `CURRENT` record, valid pointer, matching value hash, and authority type allowed for that axis.

### 22.2 `OPEN`

An open cell requires one or more `unknown_refs` identifying what remains unresolved.

### 22.3 `N/A`

N/A requires both:

```text
meaningful rationale
basis_bindings >= 1
```

The basis binding must establish why the axis does not apply. A bare N/A declaration is invalid.

## 23. Coverage Binding Contract

A versioned declarative Coverage Binding Contract defines allowed authority types per core axis.

Initial mapping includes:

| Axis | Allowed authority types |
| --- | --- |
| actor | `USR`, `DEC`, `RULE` |
| goal | `GOAL`, `REQ` |
| entry_point | `FLOW`, `SCR`, `RULE` |
| precondition | `RULE`, `STATE`, `FLOW` |
| happy_path | `FLOW`, `REQ` |
| alternative_path | `FLOW`, `RULE` |
| error | `FLOW`, `STATE`, `RULE` |
| recovery | `FLOW`, `STATE`, `RULE` |
| permission | `RULE`, `DEC`, `USR` |
| state | `STATE`, `RULE` |
| data | `DATA`, `RULE` |
| side_effect | `RULE`, `DATA`, `INT` |
| notification | `RULE`, `FLOW`, `INT` |
| validation | `RULE`, `DATA`, `AC` |
| boundary | `RULE`, `DEC` |
| persistence | `DATA`, `RULE` |
| security | `RULE`, `DEC` |
| privacy | `RULE`, `DEC`, `DATA` |
| analytics | `RULE`, `DATA`, `INT` |
| acceptance | `AC` |

The contract is versioned independently and hash-bound into the definition/approval commitment when active.

## 24. UX Coverage Binding

Screen state and major-action coverage use the same proof model.

A claimed `error`, `retry`, `permission`, or other state/action axis must point to exact current `STATE`, `FLOW`, `RULE`, `AC`, or other allowed authority under a versioned UX Binding Contract.

This prevents a screen from claiming that error behavior is covered while containing no actual canonical error behavior.

## 25. Bidirectional authority audit

Validation checks both:

```text
Coverage → Authority
Authority → Consumption
```

Material current authority that has no meaningful downstream consumption becomes an `ORPHAN_AUTHORITY` candidate unless its type is explicitly permitted to be terminal.

Transitive consumption is allowed. For example:

```text
DEC → RULE → Coverage
```

is a valid consumption path.

## 26. Semantic Closure per requirement

A material requirement is semantically closed only when all applicable conditions are satisfied, including:

```text
typed semantic payload valid
materiality assessed
surface bound
all applicable Core Grill coverage bound
all applicable specialist Grill Pack coverage bound
required UX coverage bound
acceptance bound
no unresolved material unknown
no unresolved contradiction
all authority references CURRENT
all binding hashes valid
no stale dependents required for current behavior
```

## 27. Semantic authority forms

Downstream-relevant canonical fields may declare:

```text
STRUCTURED
DECLARATIVE_TEXT
```

`STRUCTURED` is used when behavior-changing meaning is representable safely as typed data.

`DECLARATIVE_TEXT` remains valid first-class authority when prose is the actual meaning and forcing it into enums/DSL would lose information.

## 28. Semantic debt model

Downstream V2 classifies semantic fields as:

```text
DIRECT_AUTHORITY
MACHINE_DERIVED
REVIEW_REQUIRED
```

### 28.1 `DIRECT_AUTHORITY`

The exact required value is already present as canonical structured Product Definition authority.

### 28.2 `MACHINE_DERIVED`

The value is produced from canonical authority using a closed deterministic operator set such as `exact`, `extract`, `select`, or another explicitly frozen operator.

Arbitrary code and natural-language parsing are not valid derivation operators.

### 28.3 `REVIEW_REQUIRED`

Review is permitted only when the responsibility contract explicitly allows review and the meaning cannot reasonably be represented as stronger canonical authority.

If upstream structuring is reasonably possible but missing, the compiler emits:

```text
SEMANTIC_AUTHORITY_GAP
```

and the work re-enters Product Definition instead of being sent to Semantic Review.

### 28.4 Semantic debt report

Compilation reports at least:

```text
direct_authority_count
machine_derived_count
review_required_count
authority_gap_count
```

`authority_gap_count` must be zero for a valid handoff.

`review_required_count` is not required to be zero because some legitimate qualitative semantics remain review-based.

---

# Part V — Approve, constrain, verify, and re-enter

## 29. Definition status

`project.status` becomes `project.definition_status` to avoid implying that the whole product implementation is finished.

Allowed definition lifecycle:

```text
OPEN
READY_FOR_REVIEW
CLOSED
BLOCKED
```

`CLOSED` means only that the current Product Definition revision satisfies the active Semantic Closure contract.

## 30. Approval model

The redundant `user_approved` boolean is removed.

Current approval is represented by one authoritative structure:

```json
{
  "status": "APPROVED",
  "approved_revision": 24,
  "approved_definition_digest": "...",
  "approved_manifest_digest": "...",
  "approved_at": "...",
  "approved_by": "user"
}
```

Unapproved state uses `status: UNAPPROVED` and no fabricated approval values.

## 31. Approval Manifest

Before approval, a deterministic compiler generates a manifest describing what the user is approving.

It includes at least:

```text
from_revision
to_revision
added IDs
changed IDs
superseded IDs
retired IDs
high-risk decisions
deferred non-blocking items
active Grill Pack identities/versions
Semantic Closure summary
definition digest
```

The manifest is generated from canonical state and previous approval commitments, not handwritten by the agent.

Approval binds both:

```text
approved_definition_digest
approved_manifest_digest
```

Any relevant change to state or manifest invalidates the approval.

## 32. Approval history and comparison commitments

Approval history stores commitments rather than full duplicated state snapshots, including:

```text
revision
definition_digest
manifest_digest
record hashes
coverage digest
surface digest
Grill Pack set digest
```

These commitments allow deterministic calculation of later `added`, `changed`, `superseded`, and `retired` records.

## 33. Definition digest boundary

The V2 definition digest includes product meaning and the consumed evidence that supports it, including:

```text
active semantic authority
active surfaces
decisions/materiality
coverage and UX bindings
resolved contradictions
active Grill Pack IDs, versions, digests
discovery baseline commitment
consumed evidence commitments
```

It excludes operational/non-semantic material such as:

```text
current approval object
approval history payload formatting
unconsumed evidence
run timestamps that do not change meaning
migration execution time
pure presentation metadata
```

Adding unconsumed evidence does not automatically bump the definition revision. Evidence that changes consumed authority, contradictions, scope, coverage, or other semantic state does.

## 34. Implementation authority boundary

After Closure and approval, the implementation agent may:

```text
implement approved authority
make explicitly non-material implementation decisions within autonomy policy
report feasibility constraints
report ambiguity
```

It may not silently:

```text
invent a product policy
change scope
change permission semantics
choose a missing recovery rule
change a material requirement
convert implementation convenience into product intent
```

## 35. Product Definition re-entry

If implementation discovers a material gray area:

```text
implementation ambiguity
→ evidence
→ UNK
→ materiality/authority classification
→ Product Definition re-entry
```

Material re-entry causes:

```text
definition_revision++
approval → UNAPPROVED
affected authority → STALE
affected downstream contracts/tasks → STALE or BLOCKED
```

The system then loops through:

```text
DISCOVER → CLOSE → FREEZE → APPROVE → CONSTRAIN
```

Authority invalidation is dependency-scoped. Unaffected in-flight work may continue if it remains bound to still-valid authority, but final acceptance must use the current approved revision.

## 36. Downstream V2 contract identity

Legacy downstream contracts remain unchanged.

V2 introduces new identities:

```text
state schema 0.2.0
→ joewrks.action-conformance/2.0
→ joewrks.semantic-review/2.0 when semantic review is needed
```

V1 artifacts remain reproducible under their frozen contracts.

Semantic Review 2.0 starts with reliability status `NOT_MEASURED`; it does not inherit a reliability PASS from a prior contract version.

Core Semantic Closure V2 deterministic functionality may be developed and used without claiming that Semantic Review 2.0 has been reliability-calibrated.

The existing v0.4.4 calibration dependency remains a separate historical/product-development boundary and is not silently redefined by this work.

---

# Part VI — Deterministic migration

## 37. Migration tool

The official migration entrypoint is planned as:

```text
skills/joewrks-product-definition/scripts/migrate_state.py
```

Input:

```text
0.1.2.1 state
```

Output:

```text
0.2.0 state
```

Migration is never in-place by default.

The legacy source must first pass the frozen legacy validator. Otherwise migration stops with `MIGRATION_SOURCE_INVALID`.

## 38. Determinism

For the same input bytes and migrator version, canonical migrated output must be byte-deterministic.

Canonical output therefore does not include the current execution timestamp.

Migration provenance records deterministic facts such as:

```text
from_schema
to_schema
source_digest
migration_version
preserved IDs
generated records
reconciliation gaps
```

Operational run time may be logged outside canonical state if desired.

## 39. Migration confidence rule

> **Migration must never increase epistemic confidence.**

Legacy `COVERED` without exact authority binding cannot become V2 `COVERED` by guesswork.

Legacy N/A without basis binding cannot become V2 justified N/A by guesswork.

Unknown resolution mode that cannot be determined from legacy evidence is not guessed.

## 40. Reconciliation behavior

Legacy coverage that cannot prove V2 binding becomes `OPEN` plus a deterministic `MIGRATION_RECONCILIATION` unknown.

Reconciliation unknown IDs are generated in a deterministic canonical path order.

The agent must first attempt to resolve them from preserved evidence and canonical authority before interrupting the user.

## 41. Legacy custom fields

Unknown legacy custom fields that cannot map safely into V2 typed semantics are preserved under a legacy extension namespace, for example:

```json
{
  "extensions": {
    "legacy_0_1_2_1": {}
  }
}
```

Preserved extension data does not, by itself, satisfy V2 Semantic Closure. It must be reconciled into typed V2 authority before being used as semantic proof.

## 42. Legacy approval

Legacy approval is preserved in history as `LEGACY_CLOSURE_0.1.2.1` evidence.

The migrated V2 current approval is `UNAPPROVED` until Semantic Closure V2 is achieved and the user approves the V2 Approval Manifest.

---

# Part VII — Closure and blocker model

## 43. New V2 blocker families

In addition to retained legacy-equivalent integrity checks, V2 adds blocker families including:

```text
UNBOUND_PRODUCT_SURFACE
open_material_surfaces
unresolved_material_contradictions
stale_consumed_evidence
open_material_unknowns
unresolved_unknown_provenance
invalid_resolution_authority
unassessed_materiality
unauthorized_agent_decisions
missing_required_user_decisions
active_grill_pack_gaps
unresolved_pack_axes
semantic_empty_authority
invalid_authority_binding
stale_authority_binding
coverage_without_authority
open_coverage_without_unknown
unjustified_na_without_basis
invalid_coverage_authority_type
orphan_material_authority
unconsumed_material_decision
semantic_authority_gap
unauthorized_review_required
stale_downstream_source_binding
missing_or_stale_approval_manifest
```

All blocker metrics required by the active closure contract must equal zero before `definition_status = CLOSED` is valid.

## 44. V2 Closure meaning

A V2 `CLOSED` state means:

> Against the current discovery procedure, current consumed evidence, current active Product Surface Manifest, and current active Grill Packs, every discovered material product surface has been explicitly disposed; every applicable semantic coverage claim is bound to exact current canonical authority or explicitly open/justified N/A; all material gray areas and contradictions are resolved or validly blocked/deferred under policy; approval is bound to the current semantic definition and change manifest; and no known stale authority is being represented as current.

It does **not** mean the implementation is finished, all future unknowns are impossible, or Semantic Review reliability has been measured when it has not.

---

# Part VIII — R1–R10 remediation roadmap

## 45. Remediation items

| ID | Design gap | V2 remediation |
| --- | --- | --- |
| R1 | Coverage can claim `COVERED` without semantic proof | Exact Coverage→Authority Binding + hash/pointer validation |
| R2 | Known requirements can be complete while product surface is incomplete | Product Surface Manifest + discovery baseline |
| R3 | Evidence-first philosophy lacks strong first-class evidence contract | Typed Evidence Graph + authority classes + drift |
| R4 | Unknown→Decision→Authority provenance is weak | Split lifecycle/resolution mode + explicit resolution graph |
| R5 | Materiality and AI autonomy are weak/implicit | Materiality Assessment + deterministic autonomy policy |
| R6 | Existing implementation can be mistaken for intended behavior | Reverse-bootstrap reconciliation contract |
| R7 | Approval does not prove informed review of changes | Deterministic Approval Manifest + dual digest binding |
| R8 | Fixed coverage taxonomy cannot scale to domain blind spots | Versioned topology-triggered Grill Packs |
| R9 | Downstream Review may absorb upstream semantic debt | DIRECT/MACHINE/REVIEW model + hard `SEMANTIC_AUTHORITY_GAP` |
| R10 | Long-term lifecycle/migration is incomplete | RETIRED lifecycle + schema 0.2 migration + deterministic compatibility |

No R item is intentionally deferred from the V2 target architecture.

---

# Part IX — Implementation milestones and gates

## 46. Milestone sequence

Implementation proceeds in this order so that later layers depend on stable earlier contracts.

### M0 — Design Freeze

**Scope:** R1–R10 normative design.

**Deliverables:**

- this design specification;
- approved human-facing definition;
- fixed compatibility/version boundaries;
- fixed milestone roadmap.

**Gate:** written specification reviewed and approved; no unresolved architecture decision remains before implementation planning.

### M1 — State 0.2 Foundation

**Scope:** R10 foundation plus typed-object basis.

**Deliverables:**

- state schema `0.2.0`;
- V2 validation dispatch alongside frozen legacy validation;
- lifecycle `CURRENT/STALE/SUPERSEDED/RETIRED`;
- 3+ digit IDs;
- migration skeleton and deterministic migration metadata;
- typed-object semantic minimum enforcement.

**Gate:**

- frozen legacy artifacts remain unchanged and valid under legacy validation;
- V2 rejects semantically empty typed objects;
- migration source validation is explicit;
- no legacy closure is represented as V2 closure.

### M2 — Discover Authority

**Scope:** R2, R3, R6.

**Deliverables:**

- Evidence Graph;
- Surface Manifest;
- contradiction contract;
- reverse-bootstrap classification and reconciliation;
- discovery baseline.

**Gate:**

- observed implementation cannot automatically become product intent;
- all material discovered surfaces require authority/exclusion/unknown disposition;
- contradictions cannot close without explicit authority selection/decision.

### M3 — Grill Engine V2

**Scope:** R4, R5, R8.

**Deliverables:**

- unknown/decision provenance model;
- materiality classifier;
- autonomy/decision-authority policy;
- structured recommendations;
- Core Grill + initial six specialist Grill Packs;
- automatic pack activation.

**Gate:**

- high-risk/material product decisions cannot be agent-autonomous;
- evidence-resolvable questions do not require user interruption;
- triggered packs cannot be silently suppressed;
- umbrella unknown compression cannot hide independently answerable material decisions.

### M4 — Semantic Freeze

**Scope:** R1, R7.

**Deliverables:**

- product Coverage Binding Contract;
- UX Coverage Binding Contract;
- exact pointer/hash authority bindings;
- bidirectional authority audit;
- Approval Manifest compiler;
- V2 definition digest and approval history commitments.

**Gate:**

- `COVERED` without valid current authority is impossible;
- `OPEN` without an unknown is impossible;
- `N/A` without rationale+basis is impossible;
- rubber-stamp revision approval cannot satisfy V2 approval without a matching manifest digest.

### M5 — Downstream V2

**Scope:** R9 plus implementation re-entry.

**Deliverables:**

- `joewrks.action-conformance/2.0`;
- Product Definition binding reuse as downstream source seed;
- `DIRECT_AUTHORITY / MACHINE_DERIVED / REVIEW_REQUIRED` classification;
- semantic debt report;
- hard `SEMANTIC_AUTHORITY_GAP`;
- ambiguity re-entry protocol;
- semantic-review/2.0 boundary when review is required.

**Gate:**

- `authority_gap_count == 0` for valid handoff;
- `REVIEW_REQUIRED` cannot bypass an upstream authority gap;
- legacy v1 downstream artifacts remain untouched;
- semantic-review/2.0 reliability starts `NOT_MEASURED`.

### M6 — Integration and Adoption

**Scope:** R1–R10 integration.

**Deliverables:**

- complete deterministic migrator;
- templates and references updated to V2;
- skill workflow updated;
- README/user guidance updated;
- existing-site reverse-bootstrap dogfood using the new V2 flow;
- final compatibility and regression audit.

**Gate:**

- one full V2 project can go from discovery through approval, handoff, re-entry, and verification using only documented contracts;
- migration preserves all legacy meaning without inventing new certainty;
- legacy frozen evidence and current v0.4.3 disposition remain unchanged;
- all R1–R10 design goals are mapped to implemented, validated behavior.

## 47. Milestone status discipline

Intermediate milestones must not be reported as “Core V2 complete.”

Use precise status such as:

```text
IMPLEMENTED_M2 / NOT_INTEGRATED
```

Full completion is claimed only after M6 passes its gate.

---

# Part X — User-facing model and internal model

## 48. User-facing explanation

The primary README and product explanation should use simple language:

> **Find what is missing → clarify what matters → build from the decisions → check the result.**

Avoid leading with terms such as “Intent Integrity Layer,” “canonical authority graph,” “semantic assurance,” or “epistemic integrity.” Those terms may remain in architecture documentation where they are useful, but they are not the product’s first explanation.

## 49. Internal architecture shorthand

Internally, the workflow may be summarized as:

```text
DISCOVER
  Evidence + Product Surface + Grill Packs
        ↓
CLOSE
  Unknowns + Materiality + Decisions
        ↓
FREEZE
  Typed Authority + Coverage Binding + Approval
        ↓
CONSTRAIN
  Design / Implementation handoff with no silent product invention
        ↓
VERIFY
  Drift + Runtime Conformance + Semantic Assurance
        ↺
  Material ambiguity re-enters DISCOVER/CLOSE
```

This shorthand is for maintainers, not the primary user-facing pitch.

---

# 50. Final design acceptance criteria

The written design is ready for implementation planning when the reviewer can answer **yes** to all of the following:

- There is exactly one canonical Product Definition state.
- State schema `0.2.0` has a defined relationship to legacy `0.1.2.1`.
- Migration cannot manufacture certainty or auto-upgrade legacy closure.
- Product surface discovery is canonical and explicitly dispositioned.
- Evidence is typed, versionable, and restricted by authority class.
- Existing implementation cannot become product intent merely by being observed.
- Contradictions have explicit authority resolution.
- Unknown lifecycle is separated from resolution mode.
- Materiality is auditable and cannot be bypassed by a boolean.
- AI autonomy is deterministic enough to prevent material silent decisions while avoiding unnecessary user questions.
- Adaptive Grill Packs are automatic, versioned, and declarative.
- Product objects have typed semantic minima.
- `COVERED`, `OPEN`, and `N/A` each require the correct proof structure.
- Coverage binds exact canonical pointers and hashes.
- Material authority is audited for downstream consumption.
- Approval is informed through a deterministic Approval Manifest.
- Product Definition status is clearly separated from implementation completion.
- Implementation ambiguity has a dependency-scoped re-entry path.
- Downstream V2 has a new identity instead of mutating v1 contracts.
- Review is not permitted to hide an upstream semantic authority gap.
- Semantic Review reliability is never claimed without valid calibration for the actual review contract version.
- R1–R10 are all assigned to concrete implementation milestones and gates.

---

## 51. Final product principle

Everything in this design exists to preserve one simple behavior:

> **AI can research broadly and build quickly. It may not quietly decide the important parts of the product for the user.**
