# Core Semantic Closure V2 — M5.1 Downstream Executability Remediation Design

**Status:** `DESIGN_READY_FOR_USER_REVIEW`

**Program:** JOEWRKS Product Definition System

**Inserted milestone:** M5.1 — Downstream Executability Remediation

**Purpose:** Repair the boundary discovered during M6 dogfood between approved Product Definition meaning, downstream semantic handoff, and runtime verification without reopening approved product meaning merely because the downstream contract cannot express or execute it.

---

## 1. Trigger and evidence boundary

M6 Phase B was intentionally stopped after the approved bounded dogfood reached Product Definition Semantic Closure but the frozen M5 downstream compiler returned `REENTRY_REQUIRED` with no materialized action contract.

The implementer reported 25 gaps:

- 24 action-field gaps: `input_invariants`, `default_result`, `result_expectations`, and `test_obligations` across six actions;
- 1 `reply_thread.actor` gap because two approved actors could not be represented losslessly in the single-source `actor` field.

The local Phase-B commit containing that dogfood evidence has not been pushed, so the exact 25-gap runtime result is **user-execution-reported**, not remote-source-verified.

The architectural cause is independently visible in the frozen M5 remote source:

- `actor` is `DIRECT_REQUIRED`;
- `input_invariants`, `default_result`, `result_expectations`, and `test_obligations` are `DETERMINISTIC_REQUIRED`;
- `DIRECT_AUTHORITY` accepts exactly one source seed;
- `MACHINE_DERIVED` accepts only one source seed and only `extract` or `select`;
- any derivation failure caught by the compiler is normalized into `SEMANTIC_AUTHORITY_GAP` and therefore Product Definition re-entry.

That means the current contract cannot distinguish:

```text
product meaning is genuinely missing
```

from:

```text
product meaning exists, but the downstream contract cannot carry it losslessly
```

or:

```text
product meaning is carried, but runtime verification still needs implementation-side mapping metadata
```

M5.1 exists to restore those boundaries.

---

## 2. Core ruling

The M6 dogfood failure is not, by itself, evidence that Product Definition revision 1 is semantically incomplete.

The system must distinguish three failure classes:

```text
SEMANTIC_AUTHORITY_GAP
→ Product Definition meaning is missing, conflicting, stale, or unauthorized
→ Product Definition re-entry

CONTRACT_EXPRESSIVENESS_GAP
→ approved product meaning exists in exact source authority,
  but the current downstream semantic contract cannot represent it losslessly
→ downstream contract evolution, no Product Definition revision by itself

RUNTIME_MAPPING_GAP
→ semantic handoff is complete,
  but executable verification mapping or evidence coverage is incomplete/invalid
→ runtime-plan remediation, no Product Definition revision by itself
```

A runtime/compiler limitation must never be disguised as a user product decision.

---

## 3. Goals

M5.1 must:

1. preserve every frozen M5 and historical contract identity;
2. introduce a new downstream semantic contract that can carry multi-source approved authority without adding product literals;
3. separate verifier-specific test/result/snapshot mapping from canonical product semantic handoff;
4. make gap routing epistemically correct;
5. let the preserved M6 approved dogfood resume without changing Product Definition meaning if its exact approved digests remain unchanged;
6. keep runtime verification fail-closed and full-coverage;
7. preserve semantic-review reliability as `NOT_MEASURED`.

---

## 4. Non-goals

M5.1 does **not**:

- change state schema `0.2.0`;
- change M4 binding contracts or Approval Manifest semantics;
- change the approved dogfood Product Definition merely to satisfy a verifier;
- redefine `joewrks.action-conformance/2.0`;
- redefine `joewrks.handoff-definition/2.0`;
- redefine `joewrks.downstream-responsibility/1.0`;
- redefine `joewrks.semantic-review/2.0`;
- redefine `joewrks.downstream.execution/1.0`;
- modify downstream v1 or v0.4.3 historical evidence;
- introduce arbitrary `compose`, templates, callbacks, expression languages, `eval`, or natural-language parsing;
- claim semantic-review reliability;
- merge to `main`;
- assign a whole-program `v0.5` release number.

---

## 5. Version and package strategy

Historical M5 remains frozen.

Freeze the M5 package tree as historical input:

```text
skills/joewrks-product-definition/downstream_v2/
```

M5.1 creates a parallel sibling package:

```text
skills/joewrks-product-definition/downstream_v21/
```

New contract identities:

```text
joewrks.action-conformance/2.1
joewrks.handoff-definition/2.1
joewrks.downstream-responsibility/2.0
joewrks.runtime-conformance-plan/1.0
joewrks.runtime-responsibility/1.0
joewrks.semantic-review/2.1
```

`joewrks.semantic-review/2.1` is an identity-compatible review boundary for action-conformance/2.1. It does not add a new assurance claim and retains:

```text
reliability_status = NOT_MEASURED
```

The new compiler identity is:

```text
joewrks-product-definition/downstream-v2.1
```

Its program-internal compiler version may be milestone-specific, but contract identity is determined by the contract IDs above, not by a hidden reuse of `/2.0`.

---

## 6. Frozen compatibility boundary

M5.1 must leave these exact historical authorities unchanged:

```text
skills/joewrks-product-definition/downstream/
= b63568d8c4632b14bc806e7bff1908e94dea9669

evals/semantic-review-v0.4.3/
= a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
```

The complete M5 `downstream_v2/` package becomes frozen at its M5 tree identity and may be read/imported but not modified in M5.1.

The four frozen legacy `0.1.2.1` blobs remain exact.

M4 authority/approval/binding behavior remains unchanged.

---

# Part I — Action Conformance 2.1

## 7. Semantic handoff remains authority-only

`joewrks.action-conformance/2.1` remains a semantic handoff contract.

It answers:

> What approved product behavior constrains this action/lifecycle, and exactly which Product Definition authority supports it?

It does **not** answer:

> What test ID should the harness use?
> Which JSONL record should be emitted?
> Which snapshot component should the verifier classify as CHANGED?

Those are runtime verification mapping concerns and move to `joewrks.runtime-conformance-plan/1.0`.

---

## 8. Action field inventory change

Action-conformance/2.1 preserves the semantic fields from 2.0 except three verifier-specific fields are removed from semantic authority:

```text
default_result
result_expectations
test_obligations
```

They move to the runtime-conformance plan.

`input_invariants` remains in the semantic contract because validation/input constraints can be genuine product meaning. However, it no longer has to already be encoded as verifier-executable assertion syntax. It may carry an exact approved authority bundle.

All other action semantic fields remain conceptually unchanged unless a field-level 2.1 schema adjustment is required to support exact multi-source authority.

Lifecycle semantic fields remain in action-conformance/2.1. Runtime lifecycle case inventory belongs to the runtime plan.

---

## 9. Responsibility profile 2.0

Create:

```text
joewrks.downstream-responsibility/2.0
```

Each field entry contains at least:

```text
expectation
required_authority_class
allowed_seed_selectors
allowed_derivations
```

This makes permitted operations explicit instead of inferring them only from broad expectation classes.

Initial derivation vocabulary:

```text
DIRECT_AUTHORITY
extract
select
collect_exact
REVIEW_REQUIRED
```

No other derivation is valid.

### 9.1 Exact-authority fields

Fields such as action `actor` and lifecycle `authority` use an expectation that allows only:

```text
DIRECT_AUTHORITY
collect_exact
```

They do not permit `extract`, `select`, or semantic review merely to combine multiple actors/authorities.

### 9.2 Deterministic fields

Normal deterministic fields may permit:

```text
DIRECT_AUTHORITY
extract
select
collect_exact
```

subject to each field's exact `allowed_seed_selectors`.

### 9.3 Review-permitted fields

Review-permitted fields may additionally permit:

```text
REVIEW_REQUIRED
```

Review remains a last-line assurance mechanism, never a replacement for missing structured authority.

---

## 10. `collect_exact` operator

M5.1 introduces exactly one new multi-source semantic operator:

```json
{
  "kind": "MACHINE_DERIVED",
  "operator": "collect_exact",
  "source_seed_refs": ["SEED-...", "SEED-..."]
}
```

Rules:

- `source_seed_refs` must contain at least two unique seed refs;
- refs are normalized to deterministic lexical order;
- every seed must independently satisfy the field's allowed selector and authority class;
- the output is the ordered array of exact source seed values;
- no literal may be introduced;
- no string concatenation, label insertion, filtering by natural-language meaning, precedence, conflict resolution, or value rewriting is allowed;
- the array order exists only for deterministic serialization and carries no product priority semantics;
- provenance keeps every source seed ref;
- `collect_exact` counts as `MACHINE_DERIVED` semantic debt because the container structure is machine-produced, even though every member value is exact authority.

This operator solves cases like multiple approved actors without pretending one source is authoritative over the other.

If multiple seeds conflict in a way that requires a product choice rather than set-valued coexistence, `collect_exact` is invalid and the case remains a real `SEMANTIC_AUTHORITY_GAP` or contradiction.

---

## 11. No arbitrary construction operator

M5.1 explicitly rejects introducing:

```text
compose
construct
merge arbitrary objects
format/template
concat
map/filter expressions
callbacks
Python/JavaScript snippets
natural-language parsing
```

The downstream compiler may preserve, extract, select, or collect exact approved values. It may not synthesize new product policy structures from prose.

This is the main epistemic safety boundary of action-conformance/2.1.

---

## 12. Handoff Definition 2.1

Create:

```text
joewrks.handoff-definition/2.1
```

It preserves the same high-level shape:

```text
product_slug
actions
lifecycles
authority_scope_refs
ux_action_locator
fields
```

but its field-spec union supports `collect_exact` and matches the 2.1 field inventory.

The handoff definition remains a constrained derivation instruction, not product authority.

A caller cannot embed arbitrary product values into a deterministic field.

---

# Part II — Correct gap taxonomy

## 13. Semantic authority gap

Emit:

```text
SEMANTIC_AUTHORITY_GAP
```

only when product meaning itself is genuinely unresolved, for example:

- the handoff explicitly contains `UNRESOLVED`;
- required authority does not exist in the approved seed pool;
- selected authority is stale or no longer permitted;
- two authorities conflict and coexistence is not semantically valid;
- a required product choice would be needed to continue.

Result:

```text
status = REENTRY_REQUIRED
contract = null
Product Definition re-entry artifacts allowed
halt_scope = AFFECTED_ONLY
```

---

## 14. Contract expressiveness gap

Emit:

```text
CONTRACT_EXPRESSIVENESS_GAP
```

when all necessary product meaning is present in exact eligible authority but the requested semantic representation cannot be produced by the closed 2.1 operator set.

Examples:

- a caller attempts a lossless multi-source representation that is semantically valid but not supported by the current contract;
- a future product topology needs a structured semantic representation beyond direct/extract/select/collect_exact without needing a new product decision.

Result:

```text
status = CONTRACT_EVOLUTION_REQUIRED
contract = null
Product Definition re-entry = forbidden solely for this reason
canonical UNK creation = forbidden solely for this reason
```

The result reports exact source seed refs, field path, required semantic form, and contract limitation.

---

## 15. Compiler routing rule

The compiler must never catch every derivation failure and blindly relabel it `SEMANTIC_AUTHORITY_GAP`.

At minimum distinguish:

```text
SemanticGap
→ SEMANTIC_AUTHORITY_GAP

ExpressivenessGap
→ CONTRACT_EXPRESSIVENESS_GAP

Malformed/invalid handoff or contract
→ INVALID_* / fail closed
```

Re-entry events are generated only for semantic authority gaps.

---

# Part III — Runtime Conformance Plan 1.0

## 16. Why runtime mapping is separate

Test identifiers, execution result classes, evidence-case inventory, and snapshot comparison expectations are needed to verify an implementation, but they are not automatically product meaning.

Therefore M5.1 introduces:

```text
joewrks.runtime-conformance-plan/1.0
```

This artifact is verification metadata bound to an approved semantic contract.

It is **not**:

- Product Definition authority;
- part of state `0.2.0`;
- part of the Product Definition definition digest;
- part of the Approval Manifest;
- permission to introduce new product behavior.

Changing only runtime verification mapping does not require a Product Definition revision when the semantic contract hash is unchanged.

---

## 17. Runtime plan source binding

Every runtime plan commits:

```text
source action contract ID/version
source semantic_contract_hash
source approved_definition_digest
product_slug
runtime responsibility profile ID/digest
planner ID/version
```

If the action contract semantic hash changes, the runtime plan is stale.

The plan may not silently rebind to a new contract.

---

## 18. Runtime responsibility profile 1.0

Create:

```text
joewrks.runtime-responsibility/1.0
```

It defines which action/lifecycle semantic contract fields must be covered for a `FULL_CONTRACT` runtime claim.

The profile distinguishes:

```text
RUNTIME_CRITICAL
NON_RUNTIME_PRESENTATION
ASSURANCE_ONLY
```

A field excluded from runtime evidence must be excluded by the frozen profile, not by an ad hoc caller decision.

The profile is versioned and digest-bound into every runtime plan.

---

## 19. Runtime plan shape

The deterministic plan contains at least:

```text
plan_schema_version
planner
source_contract
runtime_profile
actions
lifecycles
coverage_summary
plan_hash
```

Each action plan contains:

```text
action_id
covered_contract_field_refs
cases
```

Each case contains at least:

```text
case_id
test_id
result_class
contract_field_refs
component_expectations
evidence_assertions
```

`case_id` is deterministically derived from the canonical case content.

`test_id` is verification metadata used to bind runtime evidence. It is not Product Definition authority.

---

## 20. Product-literal prohibition in runtime plans

A runtime plan must not become a shadow Product Definition.

Product-specific expected values may enter an executable assertion only by exact reference to the source action contract, for example conceptually:

```json
{
  "type": "path_equals",
  "pointer": "/result/state",
  "expected_value_source": {
    "contract_field_path": "actions/send_review_request/version_result",
    "pointer": "/..."
  }
}
```

Allowed direct constants are only verifier vocabulary defined by the runtime plan contract, such as:

```text
SUCCESS
REJECTED
STALE
IDEMPOTENT_REPLAY
CHANGED
UNCHANGED
ANY
path_present
path_absent
path_equals
collection_item_field_equals
```

A runtime plan may not contain a new product-specific expected string/number/object literal merely to make a test pass.

If an expected value cannot be traced to the semantic action contract and is not verifier vocabulary, the plan is invalid.

---

## 21. Component expectations are verification interpretation

Snapshot component expectations such as:

```text
authoritative_state = CHANGED
history = CHANGED
business_side_effects = UNCHANGED
```

are verification mappings, not automatically Product Definition decisions.

Each such expectation must cite one or more source action-contract field refs that justify the mapping.

If the mapping can be selected without changing product meaning, it is a runtime-plan concern.

If constructing the mapping reveals that the underlying product outcome itself is ambiguous, the issue is promoted to a genuine `SEMANTIC_AUTHORITY_GAP` and Product Definition re-entry.

---

## 22. Runtime mapping gap

Emit:

```text
RUNTIME_MAPPING_GAP
```

when the semantic action contract is valid but the runtime plan lacks required executable coverage or cannot create a permitted assertion mapping.

Result:

```text
runtime plan status = INCOMPLETE
Product Definition re-entry = no, unless a separately proven semantic authority gap exists
IMPLEMENTATION_CONFORMANT = forbidden
```

Malformed plans fail closed with `INVALID_RUNTIME_PLAN` rather than Product Definition re-entry.

---

## 23. Full-contract coverage

`IMPLEMENTATION_CONFORMANT` requires:

```text
verification_scope = FULL_CONTRACT
coverage_status = COMPLETE
contract_dependency_status = CONFORMANT
runtime_status = CONFORMANT
```

Completeness is computed from the runtime responsibility profile plus the runtime plan's cases.

For actions:

- every `RUNTIME_CRITICAL` semantic field must appear in at least one case's `contract_field_refs`/coverage inventory;
- every required case/test ID in the runtime plan must have admitted execution evidence for the exact action;
- all admitted required evidence must pass runtime verification;
- missing required cases/evidence means `INCOMPLETE`.

No Product Definition `test_obligations` field is required to define verifier test IDs in 2.1.

---

## 24. Lifecycle runtime coverage

Action-conformance/2.1 lifecycle semantic authority remains separate from runtime case inventory.

The runtime plan may define lifecycle cases only when they can be justified from structured lifecycle semantic fields.

Coverage states remain:

```text
NOT_APPLICABLE
FULL
INCOMPLETE
```

`NOT_APPLICABLE` is allowed only when the semantic contract has zero lifecycle items.

`FULL` requires complete case coverage under the runtime responsibility profile.

If complete executable mapping cannot be formed without inventing meaning:

```text
INCOMPLETE
```

and global `IMPLEMENTATION_CONFORMANT` is forbidden.

---

## 25. Execution transport remains frozen

M5.1 does not redefine runtime transport.

Continue using:

```text
joewrks.downstream.execution/1.0
```

The runtime verifier applies a binding/admission profile:

```text
execution.contract_hash
= action-conformance/2.1 semantic_contract_hash

execution.authority.approved_digest
= source approved_definition_digest
```

This is a stricter admission rule, not `execution/2.0`.

No file in the frozen downstream v1 package is modified.

---

# Part IV — Semantic Review 2.1

## 26. Review identity bump

Because semantic-review/2.0 validates and binds specifically to action-conformance/2.0, action-conformance/2.1 requires a matching new review identity:

```text
joewrks.semantic-review/2.1
```

The behavior remains intentionally conservative:

- only `REVIEW_REQUIRED` fields are packaged;
- every proposed value remains bound to exact semantic contract provenance;
- review does not create Product Definition authority;
- review does not mutate the semantic action contract;
- rejected interpretation may trigger contract conflict/re-entry according to existing authority rules;
- reliability remains exactly `NOT_MEASURED`.

M5.1 does not calibrate semantic-review/2.1.

---

# Part V — Identity and drift

## 27. Semantic contract identity

Action-conformance/2.1 semantic hash commits at least:

```text
contract identity
source approved definition/manifest provenance
binding contract identities
responsibility profile identity
consumed seed inventory
scope commitments
semantic actions/lifecycles
semantic debt
```

As in 2.0, observation-only full-state snapshot identity is excluded from semantic hash and included only in artifact identity where applicable.

---

## 28. Runtime plan identity

Runtime plan `plan_hash` commits:

```text
runtime plan version
source semantic contract hash
runtime responsibility profile
all action/lifecycle verification cases
coverage inventory
verification metadata/test IDs
```

Changing runtime cases or test IDs changes the runtime plan hash but does not change Product Definition or semantic action-contract identity.

---

## 29. Dependency-scoped drift remains intact

Existing M5 dependency-local audit semantics remain the model:

- unrelated Product Definition changes do not stale unaffected semantic contracts;
- used seed/scope drift stales only affected consumers;
- a runtime plan becomes stale if its source semantic contract changes;
- changing only runtime-plan metadata never rewrites Product Definition.

---

# Part VI — M6 resumption

## 30. Preserve the approved dogfood authority

The preserved M6 bounded dogfood approval is treated as still authoritative **only if** fresh checks prove its semantic identity is unchanged.

Before resuming downstream compilation after M5.1 integration, verify exactly:

```text
definition_revision = 1
project.definition_status = CLOSED
approval.status = APPROVED
approved_definition_digest = e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c
approved_manifest_digest = 60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705
approved_at = 2026-08-30T11:54:26Z
approved_by = user
closure = true
```

If those semantic approval commitments remain exact, M5.1 contract evolution does not require Product Definition revision 2 or user reapproval because Product Definition meaning did not change.

If the Product Definition digest or manifest digest changes for any reason, stop and request reapproval instead of reusing the old approval.

---

## 31. M6 branch integration strategy

The currently preserved M6 Phase-B work is local/unpushed and must remain untouched while M5.1 is designed/implemented.

M5.1 is implemented on an isolated branch descended from the common planning baseline, leaving the M6 worktree preserved.

After M5.1 passes its own gate:

1. integrate the verified M5.1 commit range into the preserved M6 implementation worktree;
2. re-run the exact Product Definition approval/digest checks above;
3. re-run downstream compile using action-conformance/2.1;
4. if no true semantic gap remains, build runtime-conformance-plan/1.0;
5. resume runtime verification and Task 6;
6. do not rerun user product questioning solely because the old 2.0 compiler could not express execution metadata.

The old 2.0 `REENTRY_REQUIRED` evidence remains historical evidence of the discovered contract limitation.

---

# Part VII — Verification gates

## 32. M5.1 focused tests

At minimum verify:

### Contract versioning

- action-conformance/2.0 bytes/tree unchanged;
- handoff-definition/2.0 unchanged;
- responsibility/1.0 unchanged;
- semantic-review/2.0 unchanged;
- 2.1 identities reject 2.0 artifacts and vice versa.

### `collect_exact`

- two valid actor seeds compile losslessly;
- one source seed remains direct authority, not forced into a collection;
- duplicate refs rejected;
- disallowed selector rejected;
- stale/unknown seed rejected;
- no literal injection possible;
- no precedence/order semantics inferred from collection order;
- conflicting product authority is not hidden by collection.

### Gap taxonomy

- explicit unresolved product meaning → `SEMANTIC_AUTHORITY_GAP` + affected-only re-entry;
- exact authority + unsupported semantic form → `CONTRACT_EXPRESSIVENESS_GAP` + no Product Definition re-entry;
- malformed input → deterministic invalid result/fail closed;
- runtime-plan incompleteness → `RUNTIME_MAPPING_GAP`, not canonical UNK.

### Runtime plan

- source semantic contract hash binding exact;
- no arbitrary product literal allowed;
- verifier vocabulary constants accepted;
- expected product values must come from contract references;
- every runtime-critical field covered for FULL_CONTRACT;
- missing case/test evidence makes coverage incomplete;
- partial probe cannot claim global implementation conformance;
- runtime plan mutation changes plan hash but not semantic contract/Product Definition digest.

### Semantic review 2.1

- only REVIEW_REQUIRED fields packaged;
- review cannot mutate contract/state;
- reliability remains NOT_MEASURED;
- 2.0 review artifacts remain valid only under their frozen contract.

---

## 33. Dogfood replay gate

Using an exact copy of the already-approved bounded dogfood semantic state, M5.1 must demonstrate:

```text
Product Definition digest unchanged
Approval Manifest digest unchanged
closure = true
```

Then the known 2.0 failure slice is replayed through 2.1.

Expected architectural outcome:

```text
reply_thread.actor
→ lossless exact multi-authority representation

input_invariants
→ semantic authority bundle remains in action contract

default_result / result_expectations / test_obligations
→ no longer required as Product Definition semantic fields;
  represented by runtime-conformance-plan/1.0 verification metadata
```

The gate passes only if:

```text
authority_gap_count = 0
CONTRACT_EXPRESSIVENESS_GAP = 0 for the known dogfood slice
materialized action-conformance/2.1 exists
runtime plan validates
runtime coverage can reach COMPLETE with the planned deterministic fixture
```

If a residual field requires an actual new product choice, M5.1 must report it as a true semantic gap rather than stretching the new contract.

---

## 34. Full regression and frozen-boundary gate

Run:

- all new M5.1 focused tests;
- complete M5 regression;
- M4/M3/M2/V2-core regression;
- legacy/downstream-v1 regression;
- semantic-review v1/v0.4.3 regression;
- full repository suite;
- `git diff --check`;
- exact tree/blob checks for every frozen boundary.

No M6 final completion claim is made by M5.1 alone.

---

# Part VIII — Alternatives considered

## 35. Alternative A — mutate action-conformance/2.0

Rejected.

Adding `compose`, multi-source direct values, or runtime mapping behavior under the existing `/2.0` identity would silently redefine a frozen contract and invalidate historical evidence discipline.

---

## 36. Alternative B — reopen Product Definition and encode verifier DSL as product authority

Rejected.

This would make users decide test IDs, snapshot comparison vocabulary, and harness representation merely because the verifier needs them. It collapses Product Definition into implementation instrumentation and violates the intent-integrity boundary.

---

## 37. Alternative C — allow arbitrary construct/compose in downstream compiler

Rejected.

It would solve the immediate fixture quickly but permit downstream code to synthesize product meaning from several prose fragments, recreating the ambiguity M4 exact binding was designed to eliminate.

---

## 38. Selected approach

Selected:

```text
freeze /2.0
→ add action-conformance/2.1
→ add only literal-free collect_exact for lossless multi-source semantic authority
→ move verifier-only result/test mapping to runtime-conformance-plan/1.0
→ separate semantic / expressiveness / runtime-mapping gaps
→ preserve Product Definition approval when semantic digest is unchanged
→ resume M6 on the new contract
```

This is the smallest architecture that fixes the observed boundary without weakening Product Definition authority or turning verification mechanics into product policy.

---

# Part IX — Status discipline

## 39. M5.1 success label

The strongest M5.1-only success label is:

```text
CORE_SEMANTIC_CLOSURE_V2_M5_1_IMPLEMENTED
— DOWNSTREAM_EXECUTABILITY_REMEDIATED / M6_RESUME_READY / NOT_INTEGRATED
```

It does not claim M6 complete.

After M5.1 is integrated into the preserved M6 branch, M6 must still complete runtime dogfood, R1–R10 traceability, regressions, and final review before any `READY_FOR_MERGE` claim.

---

## 40. Final design invariant

The M5.1 boundary is summarized as:

> **Missing product meaning re-enters Product Definition. Missing contract expressiveness evolves the contract. Missing verification mapping fixes the verifier plan. None may impersonate the other.**
