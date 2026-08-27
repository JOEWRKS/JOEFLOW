# Contract Review Adjudication

## Verdict

The isolated adjudicator classified all `176` semantically unchanged verdict flips as `REVIEW_RUBRIC_AMBIGUOUS`. It found no defensible basis in the supplied common rules to call either run systematically right or wrong. The four authorized semantic edits are separately classified `CANDIDATE_SEMANTICALLY_CHANGED`; both reviews rejected those identities, so they are not reviewer-instability evidence.

- Old candidate: `2dd2f41e996b37c22f6b960aee624160dd459b04afb31ef9e78c4e09cb76e1df`
- New candidate: `2621e7da2b576ca7d902989a720b6ed7af62b6c8895c2cfca77850421871e074`
- Adjudication source SHA-256: `deb4a75907cd70fef01d14dbb91f6089a811bb85c42c9bebf604c19b74b4d758`
- Canonical source citations: `360`
- Review-rule citations: `540`

## Classification counts

| Classification | Count |
|---|---:|
| `FIRST_REVIEW_FALSE_NEGATIVE` | 0 |
| `SECOND_REVIEW_FALSE_POSITIVE` | 0 |
| `REVIEW_RUBRIC_AMBIGUOUS` | 176 |
| `CANDIDATE_SEMANTICALLY_CHANGED` | 4 |
| `UNRESOLVED` | 0 |

## Adjudicated interpretation

The disputed fields are `input_invariants`, `test_obligations`, and `visible_error`. Canonical product constraints exist, but the common frozen schema and compiler do not define whether each of those fields must independently restate every action constraint or may rely on sibling fields such as `relationship_predicate`, `object_binding`, `preconditions`, `forbidden_states`, `rejection`, `recovery`, and `result_expectations`. The two run-specific briefs phrase that missing completeness rule differently. That makes both the distributed-field approval interpretation and the exact-field completeness rejection interpretation defensible.

## Complete per-identity adjudication

Display-only replacement glyphs in the source adjudication JSON are normalized to apostrophes below; the immutable source JSON and its hash remain preserved.

### `action:SCR-001-A01:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-001-A01: canonical sources USR-003, RULE-044, RULE-004, RULE-068, RULE-070 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-001-A01:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/0`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-001-A01: canonical sources SCR-001, USR-003, RULE-004, RULE-068, RULE-070, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-001-A01:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/0`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-001-A01: canonical sources SCR-001, USR-003, RULE-044, RULE-056, RULE-004, RULE-068, RULE-070 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-001-A02:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-001-A02: canonical sources USR-003, RULE-044, RULE-004, RULE-058 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-001-A02:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/1`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-001-A02: canonical sources SCR-001, USR-003, RULE-004, RULE-058, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-001-A02:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/1`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-001-A02: canonical sources SCR-001, USR-003, RULE-044, RULE-056, RULE-004, RULE-058 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-001-A03:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-001-A03: canonical sources USR-003, RULE-044, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-001-A03:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/2`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-001-A03: canonical sources SCR-001, USR-003, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-001-A03:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/2`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-001-A03: canonical sources SCR-001, USR-003, RULE-044, RULE-056, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-001-A04:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-001-A04: canonical sources USR-003, RULE-044, RULE-070 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-001-A04:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/3`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-001-A04: canonical sources SCR-001, USR-003, RULE-070, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-001-A04:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-001@/objects/screens/0/major_actions/3`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-001-A04: canonical sources SCR-001, USR-003, RULE-044, RULE-056, RULE-070 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A01-DELETE-DRAFT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A01-DELETE-DRAFT: canonical sources USR-003, RULE-044, RULE-023, RULE-073 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A01-DELETE-DRAFT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/0`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A01-DELETE-DRAFT: canonical sources SCR-002, USR-003, RULE-023, RULE-073, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A01-DELETE-DRAFT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/0`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A01-DELETE-DRAFT: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-023, RULE-073 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A01-EDIT-DRAFT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A01-EDIT-DRAFT: canonical sources USR-003, RULE-044, RULE-023, RULE-024, RULE-057 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A01-EDIT-DRAFT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/0`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A01-EDIT-DRAFT: canonical sources SCR-002, USR-003, RULE-023, RULE-024, RULE-057, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A01-EDIT-DRAFT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/0`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A01-EDIT-DRAFT: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-023, RULE-024, RULE-057 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A01-SUBMIT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A01-SUBMIT: canonical sources USR-003, RULE-044, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A01-SUBMIT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/0`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A01-SUBMIT: canonical sources SCR-002, USR-003, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A01-SUBMIT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/0`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A01-SUBMIT: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A02:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A02: canonical sources USR-003, RULE-044, RULE-043, RULE-017, RULE-023, RULE-075 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A02:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/1`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A02: canonical sources SCR-002, USR-003, RULE-043, RULE-017, RULE-023, RULE-075, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-003, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A02:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/1`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A02: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-043, RULE-017, RULE-023, RULE-075 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A03:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A03: canonical sources USR-003, RULE-044, RULE-025, RULE-026 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A03:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/2`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A03: canonical sources SCR-002, USR-003, RULE-025, RULE-026, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-002, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A03:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/2`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A03: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-025, RULE-026 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A04:input_invariants`

- Scope: `AUTHORIZED_SEMANTIC_CHANGE`
- Classification: `CANDIDATE_SEMANTICALLY_CHANGED`
- Canonical refs: `REQ-002@/objects/requirements/1/behavior`, `AC-002@/objects/acceptance_criteria/1/statement`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A04: REQ-002 /objects/requirements/1/behavior and AC-002 /objects/acceptance_criteria/1/statement require a reason for the current-owner additional-information request. The old value lacked /reason; the new value adds a required /reason predicate. This field owns command-input presence checks, while sibling command, rejection, and result_expectations carry the decision and no-op/result behavior. The value genuinely changed although both verdicts stayed REJECTED; broader completeness ambiguity does not make it instability evidence.

### `action:SCR-002-A04:test_obligations`

- Scope: `AUTHORIZED_SEMANTIC_CHANGE`
- Classification: `CANDIDATE_SEMANTICALLY_CHANGED`
- Canonical refs: `REQ-002@/objects/requirements/1/behavior`, `AC-002@/objects/acceptance_criteria/1/statement`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A04: REQ-002 /objects/requirements/1/behavior and AC-002 /objects/acceptance_criteria/1/statement require a reason for the current-owner additional-information request. The new test_obligations adds ["more-info-required-reason-missing-or-empty-rejects-without-commit-and-preserves-valid-input"] to the old generic list. Sibling input_invariants now requires /reason, while rejection/result_expectations carry no-commit and preservation behavior; this field adds explicit executable coverage. The value genuinely changed although both verdicts stayed REJECTED; broader coverage ambiguity does not make it instability evidence.

### `action:SCR-002-A04:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/3`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A04: canonical sources SCR-002, USR-003, RULE-044, RULE-045, RULE-056, RULE-029 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A05:input_invariants`

- Scope: `AUTHORIZED_SEMANTIC_CHANGE`
- Classification: `CANDIDATE_SEMANTICALLY_CHANGED`
- Canonical refs: `REQ-002@/objects/requirements/1/behavior`, `AC-002@/objects/acceptance_criteria/1/statement`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A05: REQ-002 /objects/requirements/1/behavior and AC-002 /objects/acceptance_criteria/1/statement require a reason for the current-owner approval-or-rejection decision. The old value lacked /reason; the new value adds a required /reason predicate. This field owns command-input presence checks, while sibling command, rejection, and result_expectations carry the decision and no-op/result behavior. The value genuinely changed although both verdicts stayed REJECTED; broader completeness ambiguity does not make it instability evidence.

### `action:SCR-002-A05:test_obligations`

- Scope: `AUTHORIZED_SEMANTIC_CHANGE`
- Classification: `CANDIDATE_SEMANTICALLY_CHANGED`
- Canonical refs: `REQ-002@/objects/requirements/1/behavior`, `AC-002@/objects/acceptance_criteria/1/statement`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A05: REQ-002 /objects/requirements/1/behavior and AC-002 /objects/acceptance_criteria/1/statement require a reason for the current-owner approval-or-rejection decision. The new test_obligations adds ["approve-or-reject-required-reason-missing-or-empty-rejects-without-commit-and-preserves-valid-input"] to the old generic list. Sibling input_invariants now requires /reason, while rejection/result_expectations carry no-commit and preservation behavior; this field adds explicit executable coverage. The value genuinely changed although both verdicts stayed REJECTED; broader coverage ambiguity does not make it instability evidence.

### `action:SCR-002-A05:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/4`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A05: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-027, RULE-028 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A06:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A06: canonical sources USR-003, RULE-044, RULE-030, RULE-031 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A06:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/5`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A06: canonical sources SCR-002, USR-003, RULE-044, RULE-030, RULE-031, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-003, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A06:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/5`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A06: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-030, RULE-031 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A07:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A07: canonical sources USR-003, RULE-044, RULE-004, RULE-051, RULE-074 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A07:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/6`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A07: canonical sources SCR-002, USR-003, RULE-004, RULE-051, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A07:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/6`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A07: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-004, RULE-051, RULE-074 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A08:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A08: canonical sources USR-003, RULE-044, RULE-003 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A08:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/7`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A08: canonical sources SCR-002, USR-003, RULE-003, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A08:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/7`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A08: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-003 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A09:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A09: canonical sources USR-003, RULE-044, RULE-034, RULE-058 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A09:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/8`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A09: canonical sources SCR-002, USR-003, RULE-034, RULE-058, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A09:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/8`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A09: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-034, RULE-058 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A10:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A10: canonical sources USR-003, RULE-044, RULE-028, RULE-034, RULE-035 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A10:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/9`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A10: canonical sources SCR-002, USR-003, RULE-028, RULE-034, RULE-035, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A10:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/9`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A10: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-028, RULE-034, RULE-035 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A11:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A11: canonical sources USR-003, RULE-044, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A11:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/10`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A11: canonical sources SCR-002, USR-003, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A11:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/10`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A11: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A12:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A12: canonical sources USR-003, RULE-044, RULE-043 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A12:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/11`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A12: canonical sources SCR-002, USR-003, RULE-044, RULE-043, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A12:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/11`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A12: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-043 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A13:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A13: canonical sources USR-003, RULE-044, RULE-050, RULE-077 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A13:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/12`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A13: canonical sources SCR-002, USR-003, RULE-050, RULE-077, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason, compensation-execution-requires-detailed-confirmation, compensation-confirmation-cancel-has-no-effect, committed-compensation-is-immutable-with-linked-follow-up); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A13:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/12`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A13: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-050, RULE-077 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A14:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A14: canonical sources USR-003, RULE-044, RULE-066, RULE-071, RULE-074 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A14:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/13`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A14: canonical sources SCR-002, USR-003, RULE-066, RULE-071, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A14:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/13`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A14: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-066, RULE-071, RULE-074 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A15:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A15: canonical sources USR-003, RULE-044, RULE-066, RULE-074 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A15:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/14`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A15: canonical sources SCR-002, USR-003, RULE-066, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A15:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/14`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A15: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-066, RULE-074 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A16:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-005@/objects/users/4/actor`, `USR-005@/objects/users/4/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A16: canonical sources USR-005, RULE-044, RULE-067, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A16:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/15`, `USR-005@/objects/users/4/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A16: canonical sources SCR-002, USR-005, RULE-067, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A16:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/15`, `USR-005@/objects/users/4/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A16: canonical sources SCR-002, USR-005, RULE-044, RULE-056, RULE-067, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A17-NO-CREDIT-STATUS:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A17-NO-CREDIT-STATUS: canonical sources USR-003, RULE-044, RULE-048, RULE-051 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A17-NO-CREDIT-STATUS:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/16`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A17-NO-CREDIT-STATUS: canonical sources SCR-002, USR-003, RULE-048, RULE-051, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A17-NO-CREDIT-STATUS:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/16`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A17-NO-CREDIT-STATUS: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-048, RULE-051 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE: canonical sources USR-003, RULE-044, RULE-039, RULE-062, RULE-063, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/16`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE: canonical sources SCR-002, USR-003, RULE-039, RULE-062, RULE-063, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/16`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-039, RULE-062, RULE-063, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A18:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A18: canonical sources USR-003, RULE-044, RULE-040, RULE-047, RULE-049 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A18:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/17`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A18: canonical sources SCR-002, USR-003, RULE-040, RULE-047, RULE-049, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A18:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/17`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A18: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-040, RULE-047, RULE-049 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A19:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A19: canonical sources USR-003, RULE-044, RULE-046 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A19:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/18`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A19: canonical sources SCR-002, USR-003, RULE-046, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A19:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/18`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A19: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-046 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A20:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A20: canonical sources USR-003, RULE-044, RULE-048, RULE-076 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A20:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/19`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A20: canonical sources SCR-002, USR-003, RULE-048, RULE-076, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A20:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/19`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A20: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-048, RULE-076 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A21:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A21: canonical sources USR-003, RULE-044, RULE-053 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A21:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/20`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A21: canonical sources SCR-002, USR-003, RULE-053, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A21:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/20`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A21: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-053 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-002-A22:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-003@/objects/users/2/actor`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-002-A22: canonical sources USR-003, RULE-044, RULE-054 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-002-A22:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/21`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-002-A22: canonical sources SCR-002, USR-003, RULE-054, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-002-A22:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-002@/objects/screens/1/major_actions/21`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-002-A22: canonical sources SCR-002, USR-003, RULE-044, RULE-056, RULE-054 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A01:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A01: canonical sources USR-004, RULE-044, RULE-032, RULE-034 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A01:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/0`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A01: canonical sources SCR-003, USR-004, RULE-032, RULE-034, REQ-003, AC-003, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A01:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/0`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A01: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-034 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A02:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A02: canonical sources USR-004, RULE-044, RULE-011, RULE-019, RULE-021, RULE-032 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A02:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/1`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A02: canonical sources SCR-003, USR-004, RULE-011, RULE-019, RULE-021, RULE-032, REQ-003, AC-003, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A02:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/1`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A02: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-011, RULE-019, RULE-021, RULE-032 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A03:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A03: canonical sources USR-004, RULE-044, RULE-032, RULE-065 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A03:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/2`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A03: canonical sources SCR-003, USR-004, RULE-032, RULE-065, REQ-003, AC-003, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A03:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/2`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A03: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-065 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A04:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A04: canonical sources USR-004, RULE-044, RULE-033, RULE-057 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A04:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/3`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A04: canonical sources SCR-003, USR-004, RULE-033, RULE-057, REQ-003, AC-003, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A04:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/3`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A04: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-033, RULE-057 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A05:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A05: canonical sources USR-004, RULE-044, RULE-032, RULE-033 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A05:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/4`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A05: canonical sources SCR-003, USR-004, RULE-032, RULE-033, REQ-003, AC-003, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A05:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/4`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A05: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-033 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A06:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A06: canonical sources USR-004, RULE-044, RULE-034 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A06:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/5`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A06: canonical sources SCR-003, USR-004, RULE-034, REQ-003, AC-003, STATE-004, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A06:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/5`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A06: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-034 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A07:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A07: canonical sources USR-004, RULE-044, RULE-066, RULE-071, RULE-074 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A07:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/6`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A07: canonical sources SCR-003, USR-004, RULE-066, RULE-071, RULE-074, REQ-003, AC-003, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A07:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/6`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A07: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-066, RULE-071, RULE-074 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A08:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A08: canonical sources USR-004, RULE-044, RULE-040, RULE-051 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A08:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/7`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A08: canonical sources SCR-003, USR-004, RULE-040, RULE-051, REQ-003, AC-003, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A08:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/7`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A08: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-040, RULE-051 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A09:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A09: canonical sources USR-004, RULE-044, RULE-040, RULE-051 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A09:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/8`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A09: canonical sources SCR-003, USR-004, RULE-040, RULE-051, REQ-003, AC-003, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A09:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/8`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A09: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-040, RULE-051 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A10:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A10: canonical sources USR-004, RULE-044, RULE-051, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A10:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/9`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A10: canonical sources SCR-003, USR-004, RULE-051, RULE-071, REQ-003, AC-003, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A10:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/9`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A10: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-051, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A11:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A11: canonical sources USR-004, RULE-044, RULE-053 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A11:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/10`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A11: canonical sources SCR-003, USR-004, RULE-053, REQ-003, AC-003, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A11:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/10`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A11: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-053 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-003-A12:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-004@/objects/users/3/actor`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-003-A12: canonical sources USR-004, RULE-044, RULE-054 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-003-A12:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/11`, `USR-004@/objects/users/3/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-003-A12: canonical sources SCR-003, USR-004, RULE-054, REQ-003, AC-003, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-003-A12:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-003@/objects/screens/2/major_actions/11`, `USR-004@/objects/users/3/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-003-A12: canonical sources SCR-003, USR-004, RULE-044, RULE-056, RULE-054 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A01-DELETE-DRAFT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A01-DELETE-DRAFT: canonical sources USR-002, RULE-044, RULE-023, RULE-073 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A01-DELETE-DRAFT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/0`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A01-DELETE-DRAFT: canonical sources SCR-004, USR-002, RULE-023, RULE-073, REQ-007, AC-007, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A01-DELETE-DRAFT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/0`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A01-DELETE-DRAFT: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-073 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A01-EDIT-DRAFT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A01-EDIT-DRAFT: canonical sources USR-002, RULE-044, RULE-023, RULE-024, RULE-057 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A01-EDIT-DRAFT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/0`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A01-EDIT-DRAFT: canonical sources SCR-004, USR-002, RULE-023, RULE-024, RULE-057, REQ-007, AC-007, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A01-EDIT-DRAFT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/0`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A01-EDIT-DRAFT: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-024, RULE-057 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A01-SUBMIT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A01-SUBMIT: canonical sources USR-002, RULE-044, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A01-SUBMIT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/0`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A01-SUBMIT: canonical sources SCR-004, USR-002, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072, REQ-007, AC-007, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A01-SUBMIT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/0`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A01-SUBMIT: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A02:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A02: canonical sources USR-002, RULE-044, RULE-043, RULE-017, RULE-023, RULE-075 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A02:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/1`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A02: canonical sources SCR-004, USR-002, RULE-043, RULE-017, RULE-023, RULE-075, REQ-007, AC-007, STATE-003, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-reason); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A02:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/1`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A02: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-043, RULE-017, RULE-023, RULE-075 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A03:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A03: canonical sources USR-002, RULE-044, RULE-029, RULE-057, RULE-075 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A03:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/2`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A03: canonical sources SCR-004, USR-002, RULE-029, RULE-057, RULE-075, REQ-007, AC-007, STATE-007, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A03:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/2`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A03: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-029, RULE-057, RULE-075 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A04:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A04: canonical sources USR-002, RULE-044, RULE-031, RULE-039, RULE-063 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A04:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/3`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A04: canonical sources SCR-004, USR-002, RULE-031, RULE-039, RULE-063, REQ-007, AC-007, STATE-003, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A04:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/3`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A04: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-031, RULE-039, RULE-063 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A05:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A05: canonical sources USR-002, RULE-044, RULE-045, RULE-022, RULE-023 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A05:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/4`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A05: canonical sources SCR-004, USR-002, RULE-045, RULE-022, RULE-023, REQ-007, AC-007, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A05:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/4`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A05: canonical sources SCR-004, USR-002, RULE-044, RULE-045, RULE-056, RULE-022, RULE-023 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A06:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A06: canonical sources USR-002, RULE-044, RULE-045, RULE-043, RULE-023, RULE-047 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A06:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/5`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A06: canonical sources SCR-004, USR-002, RULE-045, RULE-043, RULE-023, RULE-047, REQ-007, AC-007, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A06:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/5`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A06: canonical sources SCR-004, USR-002, RULE-044, RULE-045, RULE-056, RULE-043, RULE-023, RULE-047 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A07:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A07: canonical sources USR-002, RULE-044, RULE-023, RULE-040, RULE-047, RULE-049 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A07:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/6`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A07: canonical sources SCR-004, USR-002, RULE-023, RULE-040, RULE-047, RULE-049, REQ-007, AC-007, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A07:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/6`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A07: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-040, RULE-047, RULE-049 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SCR-004-A08:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `USR-002@/objects/users/1/actor`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SCR-004-A08: canonical sources USR-002, RULE-044, RULE-022, RULE-046 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SCR-004-A08:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/7`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SCR-004-A08: canonical sources SCR-004, USR-002, RULE-022, RULE-046, REQ-007, AC-007, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-authorized-read, wrong-role-and-object-scope-no-op, authoritative-readback-before-visible-success, read-does-not-change-authoritative-state-version-or-effects); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SCR-004-A08:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `SCR-004@/objects/screens/3/major_actions/7`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SCR-004-A08: canonical sources SCR-004, USR-002, RULE-044, RULE-056, RULE-022, RULE-046 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A01-INTERNAL-AUTH-SESSION:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-059@/objects/rules/58/rule`, `USR-001@/objects/users/0/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A01-INTERNAL-AUTH-SESSION: canonical sources RULE-059, USR-001, RULE-044 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /accountId, /authOperation, /proof; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A02-CUSTOMER-AUTH-SESSION:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-059@/objects/rules/58/rule`, `USR-002@/objects/users/1/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A02-CUSTOMER-AUTH-SESSION: canonical sources RULE-059, USR-002, RULE-044, RULE-022 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /accountId, /authOperation, /proof; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A03-VALIDATE-ATTACHMENT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-057@/objects/rules/56/rule`, `USR-002@/objects/users/1/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A03-VALIDATE-ATTACHMENT: canonical sources RULE-057, USR-002, USR-003, USR-004, RULE-044, RULE-033 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /file/name, /file/mimeType, /file/sizeBytes, /file/signature; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A03-VALIDATE-ATTACHMENT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-057@/objects/rules/56/rule`, `RULE-044@/objects/rules/43/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A03-VALIDATE-ATTACHMENT: canonical sources RULE-057, RULE-044, RULE-056, RULE-033 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-047@/objects/rules/46/rule`, `RULE-045@/objects/rules/44/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL: canonical sources RULE-047, RULE-045, RULE-044 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /caseId, /notificationRef, /content/caseId, /content/resultAllocationScope, /content/result, /content/reason, /content/evidence, /content/trackingValues, /content/feeOrSettlementException, /content/isolationEnd, /content/disposalSchedule, /content/disputeDeadline, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-047@/objects/rules/46/rule`, `RULE-045@/objects/rules/44/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL: canonical sources RULE-047, RULE-045, RULE-044, RULE-056 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A05-MANUAL-DELIVERY-RETRY:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-045@/objects/rules/44/rule`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A05-MANUAL-DELIVERY-RETRY: canonical sources RULE-045, USR-003, RULE-044, RULE-047 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A05-MANUAL-DELIVERY-RETRY:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-045@/objects/rules/44/rule`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A05-MANUAL-DELIVERY-RETRY: canonical sources RULE-045, USR-003, RULE-047, REQ-005, REQ-006, AC-005, AC-006, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A05-MANUAL-DELIVERY-RETRY:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-045@/objects/rules/44/rule`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A05-MANUAL-DELIVERY-RETRY: canonical sources RULE-045, USR-003, RULE-044, RULE-056, RULE-047 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A06-INBOUND-CARRIER-EVENT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/system_of_record`, `RULE-044@/objects/rules/43/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A06-INBOUND-CARRIER-EVENT: canonical sources INT-004, RULE-044, RULE-031, RULE-039 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A06-INBOUND-CARRIER-EVENT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/purpose`, `INT-004@/objects/integrations/3/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A06-INBOUND-CARRIER-EVENT: canonical sources INT-004, RULE-044, RULE-031, RULE-039, REQ-003, REQ-004, AC-003, AC-004, STATE-003, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A06-INBOUND-CARRIER-EVENT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/purpose`, `INT-004@/objects/integrations/3/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A06-INBOUND-CARRIER-EVENT: canonical sources INT-004, RULE-044, RULE-056, RULE-031, RULE-039 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/system_of_record`, `RULE-044@/objects/rules/43/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A06-REPLACEMENT-COMMIT-EVENT: canonical sources INT-004, RULE-044, RULE-066, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/purpose`, `INT-004@/objects/integrations/3/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A06-REPLACEMENT-COMMIT-EVENT: canonical sources INT-004, RULE-044, RULE-066, RULE-071, REQ-003, REQ-004, AC-003, AC-004, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary, affirmative-confirmation-precedes-commit-start, confirmation-cancel-has-no-business-or-delivery-effect, confirmed-execution-reference-is-idempotent-and-audited); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/purpose`, `INT-004@/objects/integrations/3/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A06-REPLACEMENT-COMMIT-EVENT: canonical sources INT-004, RULE-044, RULE-056, RULE-066, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/system_of_record`, `RULE-044@/objects/rules/43/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT: canonical sources INT-004, RULE-044, RULE-039, RULE-062, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/purpose`, `INT-004@/objects/integrations/3/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT: canonical sources INT-004, RULE-039, RULE-062, RULE-071, REQ-003, REQ-004, AC-003, AC-004, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary, affirmative-confirmation-precedes-commit-start, confirmation-cancel-has-no-business-or-delivery-effect, confirmed-execution-reference-is-idempotent-and-audited); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-004@/objects/integrations/3/purpose`, `INT-004@/objects/integrations/3/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT: canonical sources INT-004, RULE-044, RULE-056, RULE-039, RULE-062, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-006@/objects/integrations/5/system_of_record`, `RULE-044@/objects/rules/43/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A07-REFUND-SETTLEMENT-SIMULATION: canonical sources INT-006, RULE-044, RULE-067, RULE-071 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-006@/objects/integrations/5/purpose`, `INT-006@/objects/integrations/5/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A07-REFUND-SETTLEMENT-SIMULATION: canonical sources INT-006, RULE-044, RULE-067, RULE-071, REQ-004, AC-004, STATE-005, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation, required-confirmation-before-irreversible-boundary, affirmative-confirmation-precedes-commit-start, confirmation-cancel-has-no-business-or-delivery-effect, confirmed-execution-reference-is-idempotent-and-audited); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-006@/objects/integrations/5/purpose`, `INT-006@/objects/integrations/5/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A07-REFUND-SETTLEMENT-SIMULATION: canonical sources INT-006, RULE-044, RULE-056, RULE-067, RULE-071 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-006@/objects/integrations/5/system_of_record`, `RULE-044@/objects/rules/43/rule`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION: canonical sources INT-006, RULE-044, RULE-040, RULE-047, RULE-049 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-006@/objects/integrations/5/purpose`, `INT-006@/objects/integrations/5/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION: canonical sources INT-006, RULE-044, RULE-040, RULE-047, RULE-049, REQ-004, AC-004, STATE-008, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `INT-006@/objects/integrations/5/purpose`, `INT-006@/objects/integrations/5/system_of_record`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION: canonical sources INT-006, RULE-044, RULE-056, RULE-040, RULE-047, RULE-049 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

### `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:input_invariants`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-056@/objects/rules/55/rule`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/verifier.py::_expected_result` — Evaluate listed command-input invariants; on no listed failure, use the declared or default result.
- Rationale: SYS-A09-OUTAGE-QUEUE-RECONCILIATION: canonical sources RULE-056, USR-003, RULE-044 impose action-specific authority, scope, state, validation/evidence, and result boundaries. input_invariants owns executable command-input predicates and lists /actorId, /targetId, /expectedVersion, /idempotencyKey; sibling actor, relationship_predicate, object_binding, preconditions, forbidden_states, rejection, and result_expectations carry the other guards/outcomes. The common verifier consumes this list but does not require it to repeat every sibling constraint. The old brief's whole-meaning reading supports approval, while the new brief's exact-field/omission wording supports rejection; both are defensible because common field-completeness is unspecified.

### `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:test_obligations`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-056@/objects/rules/55/rule`, `USR-003@/objects/users/2/actor`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/contracts.py::_validate_action_result_contract` — Require an array of non-empty test-obligation strings without defining exhaustive action-semantic coverage.
- Rationale: SYS-A09-OUTAGE-QUEUE-RECONCILIATION: canonical sources RULE-056, USR-003, RULE-044, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001 impose action-specific scope, happy path, validation/evidence, state, mutation/result, and failure behavior. test_obligations names reusable coverage (valid-happy-transition, wrong-role-and-object-scope-no-op, stale-expected-version-no-op, same-key-replay-without-duplicate-effects, authoritative-readback-before-visible-success, business-state-and-delivery-state-separation); sibling object_binding, preconditions, expected_domain_mutation, forbidden_mutations, rejection, result_expectations, and visible_error carry exact product semantics. The common compiler validates non-empty labels but does not say whether this list must enumerate every cited constraint or rely on sibling semantics and sequence definitions. The old brief supports approval and the new exact-field/omission wording supports rejection; both are defensible under an underspecified rubric.

### `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:visible_error`

- Scope: `VERDICT_DISAGREEMENT`
- Classification: `REVIEW_RUBRIC_AMBIGUOUS`
- Canonical refs: `RULE-056@/objects/rules/55/rule`, `USR-003@/objects/users/2/constraint`
- Review rules:
  - `old-candidate/REVIEW_BRIEF.md::Review target, step 4` — Interpret the complete current canonical meaning.
  - `new-candidate/REVIEW_BRIEF.md::Review task, steps 3-4` — Judge full support for the exact field and detect omitted constraints.
  - `frozen/downstream/schemas/action-contract.schema.json::$defs.action.properties.visible_error / $defs.semanticField` — Require a provenance-bound semantic field without an independent conditional-access or completeness structure.
- Rationale: SYS-A09-OUTAGE-QUEUE-RECONCILIATION: canonical sources RULE-056, USR-003, RULE-044 impose authority/scope and no-op/recovery boundaries. visible_error projects {"preserve":"saved server checkpoint and canonical no-op boundary","show":["reason or validation error","latest authoritative state","latest scope version"]}; sibling authentication, relationship_predicate, object_binding, forbidden_states, rejection, recovery, and result_expectations carry access gates and no-op behavior. The common schema does not say whether state/version display is evaluated only after sibling gates or must repeat them conditionally here. The old brief supports the gated distributed reading, while the new exact-field wording supports the unconditional-leak reading; both verdicts are defensible under the unspecified boundary.

