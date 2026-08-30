# Core Semantic Closure V2 — M5.1 Executability Design Self-Review

**Status:** `NORMATIVE_DESIGN_CLARIFICATION`

**Applies to:** `docs/superpowers/specs/2026-08-30-core-semantic-closure-v2-m5-1-executability-remediation-design.md`

Where this clarification conflicts with the main M5.1 design, this clarification controls. The frozen Core Semantic Closure V2 design and already-approved Product Definition authority remain higher authority.

---

## 1. Self-review result

The main design direction is sound:

```text
freeze action-conformance/2.0
→ action-conformance/2.1 for semantic handoff
→ runtime-conformance-plan/1.0 for verifier mapping
→ semantic / expressiveness / runtime-mapping gaps remain distinct
```

Fresh-eye review found several places where the first draft was still too permissive or could accidentally lose authority. The following rules close those gaps.

---

## 2. Freeze the exact M5 downstream_v2 tree

The main design says the complete M5 package becomes frozen but does not record its exact tree.

Freeze:

```text
skills/joewrks-product-definition/downstream_v2/
= 33fb2653531fa85dcc8fd8c94cbbb7cc5c41d41e
```

M5.1 implementation may import/read this package, but no file beneath that path may change.

The historical downstream v1 and v0.4.3 tree freezes in the main design remain unchanged.

---

## 3. `collect_exact` is field-gated, not a generic deterministic escape hatch

The main design allows normal deterministic fields to permit `collect_exact`. That is too broad.

A compiler must not hide conflicting or alternative authority merely by putting every eligible seed into an array.

Freeze responsibility profile 2.0 so every field has an explicit:

```text
allowed_derivations
collection_semantics
```

where:

```text
collection_semantics = NONE | MEMBERSHIP_SET | CONJUNCTIVE_SET
```

`collect_exact` is valid only when `collection_semantics != NONE`.

Initial M5.1 allowlist is deliberately narrow:

```text
action.actor
  collection_semantics = MEMBERSHIP_SET

action.input_invariants
  collection_semantics = CONJUNCTIVE_SET

lifecycle.authority
  collection_semantics = MEMBERSHIP_SET
```

Every other 2.1 field starts with:

```text
collection_semantics = NONE
```

unless an implementation-time source audit proves an already-approved field has the same unavoidable exact-set requirement. Adding another allowlisted field requires an explicit design-review finding in the M5.1 implementation audit, not a convenience change inside the derivation function.

### Semantics

`MEMBERSHIP_SET` means every exact collected member is independently an allowed semantic member. Array order is serialization-only and carries no priority.

`CONJUNCTIVE_SET` means every exact collected constraint applies. Array order is serialization-only.

If exact source authorities cannot coexist under the field's declared collection semantics, `collect_exact` must not be used. The issue is a contradiction/semantic gap, not a collection operation.

---

## 4. `collect_exact` normalization is exact and deterministic

Freeze the operator behavior more precisely:

```json
{
  "kind": "MACHINE_DERIVED",
  "operator": "collect_exact",
  "source_seed_refs": ["SEED-...", "SEED-..."]
}
```

Rules:

- minimum two refs;
- refs unique;
- compiler normalizes refs lexically before derivation;
- every ref must satisfy authority class, scope, selector, and field collection policy;
- derived `value` is an array aligned to normalized source refs;
- every element is a deep exact copy of that source seed value;
- duplicates are not silently removed because provenance must remain one-to-one with source refs;
- consumers may not treat array order as priority;
- no extra labels, tags, wrappers carrying product meaning, or caller literals are introduced.

It remains classified as `MACHINE_DERIVED` because only the container structure is machine-created.

---

## 5. Removing runtime fields must not drop their product authority provenance

The main design removes these verifier-specific values from action-conformance/2.1:

```text
default_result
result_expectations
test_obligations
```

That separation is correct, but simply deleting them could cause exact acceptance/outcome seeds that were consumed only by those fields to disappear from the semantic handoff.

Add a required per-action semantic section:

```json
{
  "verification_basis": {
    "outcome_basis_seed_refs": ["SEED-..."],
    "acceptance_basis_seed_refs": ["SEED-..."]
  }
}
```

This section contains **source seed references only**, not runtime expectations or test IDs.

### Allowed basis selectors

`outcome_basis_seed_refs` may select only exact eligible seeds from the already-approved outcome-oriented locations used by the 2.0 result fields, initially:

```text
CORE:happy_path
CORE:alternative_path
CORE:error
CORE:recovery
CORE:acceptance
UX_ACTION:success
UX_ACTION:failure
UX_STATE:success
UX_STATE:error
```

`acceptance_basis_seed_refs` may select only:

```text
CORE:acceptance
```

The 2.1 responsibility profile freezes the exact selector sets.

### Identity effect

All verification-basis refs count as consumed semantic authority:

- their seeds remain in the consumed seed inventory;
- their seed refs participate in semantic contract hash;
- 2.1 validation rejects unused basis refs and missing required basis refs;
- runtime plans may reference the basis through the semantic contract but may not go back to Product Definition directly.

This preserves the M4→M5 exact provenance chain while moving verifier mechanics out of product semantic fields.

---

## 6. Runtime plans consume the semantic contract only

The runtime planner/verifier must not read `state.json`, M4 coverage cells, or unconsumed Product Definition evidence to fill a mapping gap.

Its semantic inputs are limited to:

```text
valid action-conformance/2.1
valid semantic-review/2.1 output where required
runtime responsibility profile
implementation/runtime evidence
```

Product-specific runtime expectations may reference:

```text
action semantic field paths
verification_basis seed refs already embedded in the semantic contract
```

No direct new Product Definition pointer is permitted in a runtime plan.

If the action contract lacks required product meaning, that is a semantic handoff problem and must not be repaired by runtime mapping.

---

## 7. Freeze the initial runtime responsibility classification

The first draft leaves the runtime profile abstract enough that an implementation could classify difficult fields as non-runtime merely to reach `COMPLETE`.

Freeze the initial action field classes.

### `RUNTIME_CRITICAL`

```text
actor
authentication
relationship_predicate
object_binding
concurrency
preconditions
allowed_current_states
forbidden_states
input_invariants
command
expected_domain_mutation
forbidden_mutations
version_result
history_result
business_side_effects
delivery_effects
idempotency
rejection
recovery
superseded_rules
```

### `NON_RUNTIME_PRESENTATION`

```text
visible_success
visible_error
```

### `ASSURANCE_ONLY`

```text
trace
```

All lifecycle semantic fields are `RUNTIME_CRITICAL` in runtime-responsibility/1.0.

Any later reclassification requires a new runtime responsibility profile identity/digest; a caller cannot override it per plan.

---

## 8. Coverage requires concrete mapping, not a list of field refs

A runtime case does not cover a semantic field merely because its path appears in `contract_field_refs`.

For a field to count as covered, the case must contain at least one concrete executable relationship linked to that field, such as:

- an input/admission condition;
- a concrete result class expectation;
- `CHANGED` / `UNCHANGED` component expectation;
- a path/evidence assertion whose expected product-specific value is sourced exactly from the semantic contract;
- an exact lifecycle transition check.

A bare citation is traceability, not verification coverage.

The runtime plan validator computes coverage from executable relationships, then compares that inventory with the frozen runtime responsibility profile.

---

## 9. `ANY` cannot satisfy FULL_CONTRACT semantic coverage

The verifier vocabulary may retain:

```text
ANY
```

for components genuinely irrelevant to a particular runtime case.

But:

> `ANY` never counts as evidence that a Product Definition semantic field was verified.

A plan containing `ANY` for a component must still cover its linked runtime-critical semantic fields through other concrete assertions or expectations.

An all-`ANY` plan therefore remains `INCOMPLETE`.

---

## 10. Fixture data and product literals are separate

The main design correctly bans arbitrary product-specific expected literals, but runtime tests still need synthetic fixture values such as generated IDs and starting revision numbers.

Freeze two categories:

```text
CONTRACT_DERIVED
FIXTURE_ONLY
```

`CONTRACT_DERIVED` expected values must be resolved exactly from action-conformance/2.1 fields or verification-basis seeds.

`FIXTURE_ONLY` values may be generated by the runtime fixture only when they are semantically inert test data, for example:

- opaque object IDs;
- synthetic attempt IDs;
- fixture-only timestamps chosen only to order test steps;
- initial counter/revision instances used to exercise an already-approved revision rule.

A `FIXTURE_ONLY` value may not define a product threshold, timeout, retention duration, permission rule, business state name, allowed actor, success policy, or other product meaning.

If a test needs such a product-specific value, it must be `CONTRACT_DERIVED`.

---

## 11. Runtime-critical REVIEW_REQUIRED fields block automated full conformance until review completion

If action-conformance/2.1 contains `REVIEW_REQUIRED` on a `RUNTIME_CRITICAL` field, a runtime plan may be constructed but cannot become `FULL_CONTRACT / COMPLETE` until a valid semantic-review/2.1 output records `CONFIRMED_INTERPRETATION` for that exact obligation.

The runtime plan binds the relevant review package/output identities.

Rules remain:

```text
review completion != reliability
reliability = NOT_MEASURED
```

A rejected interpretation routes through the normal semantic contract conflict/re-entry path.

No review output may rewrite contract or Product Definition values.

---

## 12. Runtime plan weakening is detectable identity drift

Runtime-plan cases, coverage relationships, result classes, component expectations, assertions, test IDs, and semantic-review commitments are all inside `plan_hash`.

Changing a plan to remove a case, replace `CHANGED` with `ANY`, alter an assertion, or drop field coverage changes `plan_hash` and invalidates old runtime evidence admission.

Runtime evidence must bind both:

```text
source semantic_contract_hash
source runtime plan hash
```

The frozen `joewrks.downstream.execution/1.0` transport has no native runtime-plan-hash field, so M5.1 must not alter its bytes. The binding must therefore live in the M5.1 verifier input/envelope or aggregate evidence manifest, not by redefining protocol 1.0.

The exact transport-preserving envelope is an implementation-plan deliverable, but it must be deterministic, hash-bound, and outside Product Definition authority.

---

## 13. Expressiveness gaps require proven eligible authority

An invalid or unknown handoff operator must not be reclassified as a contract expressiveness gap merely because the caller says so.

`CONTRACT_EXPRESSIVENESS_GAP` is valid only after the M5.1 planner/compiler proves:

1. exact source seeds exist;
2. each source is current and eligible for the target field;
3. no unresolved Product Definition contradiction blocks their joint use;
4. the desired semantic relation does not require a new product choice;
5. the closed 2.1 representation vocabulary still cannot encode it losslessly.

Malformed input remains `INVALID_*`.

Explicit `UNRESOLVED` product meaning remains `SEMANTIC_AUTHORITY_GAP`.

For M5.1's known dogfood case, `collect_exact` should remove the multi-actor expressiveness failure. This taxonomy rule primarily protects future cases.

---

## 14. Approval preservation is conditional on semantic identity, not milestone labels

The M6 dogfood Product Definition may retain its revision-1 approval only if, after M5.1 integration, fresh official computation proves the exact already-approved Product Definition identity remains:

```text
definition digest
= e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c

manifest digest
= 60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705
```

and the current revision-1 approval/history commitment remains exact.

A new downstream contract identity alone does not change Product Definition semantic projection because downstream action-contract identity is not part of state `0.2.0` Product Definition authority.

However, if any integration step edits canonical Product Definition meaning and changes either digest, the existing approval may not be reused.

---

## 15. M6 integration must preserve the stopped evidence before retrying compile

The user-reported M6 Phase-B stop is valuable evidence that action-conformance/2.0 hit the old boundary.

When M5.1 is later integrated into the preserved M6 worktree:

- preserve the old 2.0 failure summary/re-entry probe as historical dogfood evidence;
- do not rewrite it to make 2.0 appear successful;
- add separate 2.1 remediation evidence;
- verify the canonical approved dogfood state itself did not change;
- only then resume downstream compile/runtime verification.

This makes M6 evidence show both the discovered failure and the corrected contract boundary.

---

## 16. Planning/implementation branch boundary

This M5.1 planning line is documentation-only.

Implementation must occur on a separate isolated branch/worktree.

The preserved local M6 implementation worktree containing Phase-B approval and the stopped 2.0 dogfood result must not be used as the M5.1 coding worktree.

After M5.1 implementation is independently verified, integrate its exact commit range into the M6 worktree and resume from the stopped point.

---

## 17. Self-review acceptance criteria

The M5.1 design is ready for implementation planning only if the user accepts all of these boundaries:

1. `/2.0` stays byte/tree frozen;
2. action-conformance/2.1 removes verifier-only result/test values but preserves their exact authority via `verification_basis`;
3. `collect_exact` is limited to explicit set-valued fields, initially actor/input-invariants/lifecycle-authority;
4. runtime-conformance-plan/1.0 is non-authoritative verification mapping;
5. full runtime coverage is computed from a frozen responsibility profile and concrete mappings, not citations;
6. `ANY` cannot satisfy coverage;
7. runtime-critical semantic review must be completed before full runtime conformance, while reliability remains `NOT_MEASURED`;
8. product-specific expected values come only from the semantic contract; fixture-only values cannot create product policy;
9. only true semantic gaps re-enter Product Definition;
10. the already-approved M6 Product Definition may be reused only when its exact semantic digests remain unchanged.

---

## 18. Final clarified invariant

> **Product authority stays in Product Definition. Semantic handoff carries exact approved meaning. Runtime plans map that meaning into tests without becoming authority. A limitation at one layer never impersonates uncertainty at another.**
