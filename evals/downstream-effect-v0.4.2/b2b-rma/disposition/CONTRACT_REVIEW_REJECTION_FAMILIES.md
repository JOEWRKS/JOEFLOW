# Contract Review Rejection Families

This clusters the final reviewer's stated rationales. A cluster count is not an adjudication that the claimed defect is canonically valid.

## Primary rationale families

| Family | Count |
|---|---:|
| `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS` | 58 |
| `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH` | 62 |
| `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION` | 60 |

## Semantic field types

| Field | Count |
|---|---:|
| `input_invariants` | 62 |
| `test_obligations` | 58 |
| `visible_error` | 60 |

## Inspected concern tags (multi-label)

| Concern | Count |
|---|---:|
| `action_specific_scope_or_output_coverage` | 58 |
| `authorization_ownership` | 180 |
| `incorrect_success_failure_mutation_semantics` | 62 |
| `lifecycle_or_window_guard` | 62 |
| `missing_rejection_no_op_behavior` | 120 |
| `missing_required_input_invariant` | 62 |
| `recovery_retry` | 60 |
| `reviewer_completeness_rule_not_stated_in_canonical_authority` | 180 |
| `state_input_preservation` | 60 |
| `under_broad_invariant` | 62 |
| `visible_error_requirements` | 60 |

No final rejection rationale claimed a direct provenance hash mismatch, stale/version omission, idempotency defect, lifecycle transition defect, notification/business-state conflation, or audit/history mutation defect as its primary family. All exact refs and hashes had already resolved.

## Counts by action

| Action | Rejected fields |
|---|---:|
| `SCR-001-A01` | 3 |
| `SCR-001-A02` | 3 |
| `SCR-001-A03` | 3 |
| `SCR-001-A04` | 3 |
| `SCR-002-A01-DELETE-DRAFT` | 3 |
| `SCR-002-A01-EDIT-DRAFT` | 3 |
| `SCR-002-A01-SUBMIT` | 3 |
| `SCR-002-A02` | 3 |
| `SCR-002-A03` | 3 |
| `SCR-002-A04` | 3 |
| `SCR-002-A05` | 3 |
| `SCR-002-A06` | 3 |
| `SCR-002-A07` | 3 |
| `SCR-002-A08` | 3 |
| `SCR-002-A09` | 3 |
| `SCR-002-A10` | 3 |
| `SCR-002-A11` | 3 |
| `SCR-002-A12` | 3 |
| `SCR-002-A13` | 3 |
| `SCR-002-A14` | 3 |
| `SCR-002-A15` | 3 |
| `SCR-002-A16` | 3 |
| `SCR-002-A17-NO-CREDIT-STATUS` | 3 |
| `SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE` | 3 |
| `SCR-002-A18` | 3 |
| `SCR-002-A19` | 3 |
| `SCR-002-A20` | 3 |
| `SCR-002-A21` | 3 |
| `SCR-002-A22` | 3 |
| `SCR-003-A01` | 3 |
| `SCR-003-A02` | 3 |
| `SCR-003-A03` | 3 |
| `SCR-003-A04` | 3 |
| `SCR-003-A05` | 3 |
| `SCR-003-A06` | 3 |
| `SCR-003-A07` | 3 |
| `SCR-003-A08` | 3 |
| `SCR-003-A09` | 3 |
| `SCR-003-A10` | 3 |
| `SCR-003-A11` | 3 |
| `SCR-003-A12` | 3 |
| `SCR-004-A01-DELETE-DRAFT` | 3 |
| `SCR-004-A01-EDIT-DRAFT` | 3 |
| `SCR-004-A01-SUBMIT` | 3 |
| `SCR-004-A02` | 3 |
| `SCR-004-A03` | 3 |
| `SCR-004-A04` | 3 |
| `SCR-004-A05` | 3 |
| `SCR-004-A06` | 3 |
| `SCR-004-A07` | 3 |
| `SCR-004-A08` | 3 |
| `SYS-A01-INTERNAL-AUTH-SESSION` | 1 |
| `SYS-A02-CUSTOMER-AUTH-SESSION` | 1 |
| `SYS-A03-VALIDATE-ATTACHMENT` | 2 |
| `SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL` | 2 |
| `SYS-A05-MANUAL-DELIVERY-RETRY` | 3 |
| `SYS-A06-INBOUND-CARRIER-EVENT` | 3 |
| `SYS-A06-REPLACEMENT-COMMIT-EVENT` | 3 |
| `SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT` | 3 |
| `SYS-A07-REFUND-SETTLEMENT-SIMULATION` | 3 |
| `SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION` | 3 |
| `SYS-A09-OUTAGE-QUEUE-RECONCILIATION` | 3 |

## Counts by explicit variant

`BASE` means the explicit mapping has no separate variant label.

| Variant | Rejected fields |
|---|---:|
| `BASE` | 147 |
| `DELETE-DRAFT` | 6 |
| `EDIT-DRAFT` | 6 |
| `INBOUND_TRACKING` | 3 |
| `NO-CREDIT-STATUS` | 3 |
| `REPLACEMENT_COMMIT` | 3 |
| `RETURN-TO-CUSTOMER-EXECUTE` | 3 |
| `RETURN_TO_CUSTOMER_COMMIT` | 3 |
| `SUBMIT` | 6 |

## Counts by cited canonical object (multi-label)

A field can cite multiple objects, so these counts do not sum to 180.

| Canonical object | Rejected fields citing it |
|---|---:|
| `USR-003` | 151 |
| `RULE-044` | 129 |
| `RULE-056` | 62 |
| `USR-004` | 61 |
| `FLOW-001` | 58 |
| `USR-002` | 53 |
| `SCR-002` | 50 |
| `RULE-023` | 33 |
| `AC-005` | 31 |
| `AC-006` | 31 |
| `REQ-005` | 31 |
| `REQ-006` | 31 |
| `AC-004` | 30 |
| `REQ-004` | 30 |
| `RULE-071` | 27 |
| `SCR-003` | 24 |
| `RULE-057` | 20 |
| `SCR-004` | 20 |
| `STATE-005` | 18 |
| `RULE-047` | 17 |
| `AC-003` | 15 |
| `INT-004` | 15 |
| `REQ-003` | 15 |
| `RULE-024` | 15 |
| `RULE-040` | 15 |
| `RULE-043` | 15 |
| `RULE-051` | 15 |
| `RULE-045` | 14 |
| `STATE-001` | 14 |
| `RULE-032` | 12 |
| `RULE-034` | 12 |
| `RULE-039` | 12 |
| `RULE-066` | 12 |
| `RULE-074` | 12 |
| `AC-007` | 10 |
| `INT-006` | 10 |
| `REQ-007` | 10 |
| `RULE-004` | 9 |
| `RULE-010` | 9 |
| `RULE-031` | 9 |
| `RULE-049` | 9 |
| `RULE-075` | 9 |
| `STATE-008` | 9 |
| `RULE-033` | 8 |
| `SCR-001` | 8 |
| `STATE-004` | 8 |
| `RULE-022` | 7 |
| `RULE-017` | 6 |
| `RULE-025` | 6 |
| `RULE-028` | 6 |
| `RULE-029` | 6 |
| `RULE-046` | 6 |
| `RULE-048` | 6 |
| `RULE-053` | 6 |
| `RULE-054` | 6 |
| `RULE-058` | 6 |
| `RULE-062` | 6 |
| `RULE-063` | 6 |
| `RULE-067` | 6 |
| `RULE-070` | 6 |
| `RULE-072` | 6 |
| `RULE-073` | 6 |
| `STATE-003` | 5 |
| `USR-005` | 5 |
| `AC-002` | 4 |
| `REQ-002` | 4 |
| `RULE-001` | 3 |
| `RULE-003` | 3 |
| `RULE-005` | 3 |
| `RULE-006` | 3 |
| `RULE-011` | 3 |
| `RULE-014` | 3 |
| `RULE-015` | 3 |
| `RULE-019` | 3 |
| `RULE-021` | 3 |
| `RULE-026` | 3 |
| `RULE-027` | 3 |
| `RULE-030` | 3 |
| `RULE-035` | 3 |
| `RULE-036` | 3 |
| `RULE-037` | 3 |
| `RULE-038` | 3 |
| `RULE-050` | 3 |
| `RULE-065` | 3 |
| `RULE-068` | 3 |
| `RULE-076` | 3 |
| `RULE-077` | 3 |
| `RULE-059` | 2 |
| `STATE-002` | 2 |
| `STATE-007` | 2 |
| `USR-001` | 2 |

## Rule-scope observation for adjudication

The final rationales consistently require `input_invariants`, `test_obligations`, or `visible_error` to restate constraints that also appear in separately reviewed fields such as `relationship_predicate`, `object_binding`, `preconditions`, `forbidden_states`, `rejection`, and `recovery`. The frozen schema requires these fields to exist but does not state whether every field must independently be complete for all cited action semantics. The two review briefs also phrase this completeness question differently. Whether that is a valid contract rule is intentionally left to isolated adjudication.

## Complete rejection inventory

### `action:SCR-001-A01:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-004, RULE-068, RULE-070`
- Rationale: For SCR-001-A01, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-004, RULE-068, RULE-070) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-001-A01:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-001, USR-003, USR-003, RULE-004, RULE-068, RULE-070, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-001-A01, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-001, USR-003, RULE-004, RULE-068, RULE-070, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-001-A01:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-001, USR-003, RULE-044, RULE-056, RULE-004, RULE-068, RULE-070`
- Rationale: For SCR-001-A01, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-001, USR-003, RULE-044, RULE-056, RULE-004, RULE-068, RULE-070). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-001-A02:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-004, RULE-058`
- Rationale: For SCR-001-A02, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-004, RULE-058) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-001-A02:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-001, USR-003, USR-003, RULE-004, RULE-058, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-001-A02, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-001, USR-003, RULE-004, RULE-058, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-001-A02:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-001, USR-003, RULE-044, RULE-056, RULE-004, RULE-058`
- Rationale: For SCR-001-A02, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-001, USR-003, RULE-044, RULE-056, RULE-004, RULE-058). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-001-A03:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025`
- Rationale: For SCR-001-A03, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-001-A03:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-001, USR-003, USR-003, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-001-A03, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-001, USR-003, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-001-A03:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-001, USR-003, RULE-044, RULE-056, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025`
- Rationale: For SCR-001-A03, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-001, USR-003, RULE-044, RULE-056, RULE-005, RULE-010, RULE-014, RULE-015, RULE-024, RULE-025). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-001-A04:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-070`
- Rationale: For SCR-001-A04, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-070) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-001-A04:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-001, USR-003, USR-003, RULE-070, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-001-A04, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-001, USR-003, RULE-070, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-001-A04:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-001, USR-003, RULE-044, RULE-056, RULE-070`
- Rationale: For SCR-001-A04, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-001, USR-003, RULE-044, RULE-056, RULE-070). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A01-DELETE-DRAFT:input_invariants`

- Variant: `DELETE-DRAFT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-023, RULE-073`
- Rationale: For SCR-002-A01-DELETE-DRAFT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-003, RULE-044, RULE-023, RULE-073) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A01-DELETE-DRAFT:test_obligations`

- Variant: `DELETE-DRAFT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-023, RULE-073, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-002-A01-DELETE-DRAFT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-023, RULE-073, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A01-DELETE-DRAFT:visible_error`

- Variant: `DELETE-DRAFT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-023, RULE-073`
- Rationale: For SCR-002-A01-DELETE-DRAFT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-023, RULE-073). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A01-EDIT-DRAFT:input_invariants`

- Variant: `EDIT-DRAFT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-023, RULE-024, RULE-057`
- Rationale: For SCR-002-A01-EDIT-DRAFT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-023, RULE-024, RULE-057) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A01-EDIT-DRAFT:test_obligations`

- Variant: `EDIT-DRAFT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-023, RULE-024, RULE-057, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-002-A01-EDIT-DRAFT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-023, RULE-024, RULE-057, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A01-EDIT-DRAFT:visible_error`

- Variant: `EDIT-DRAFT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-023, RULE-024, RULE-057`
- Rationale: For SCR-002-A01-EDIT-DRAFT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-023, RULE-024, RULE-057). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A01-SUBMIT:input_invariants`

- Variant: `SUBMIT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072`
- Rationale: For SCR-002-A01-SUBMIT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A01-SUBMIT:test_obligations`

- Variant: `SUBMIT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SCR-002-A01-SUBMIT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A01-SUBMIT:visible_error`

- Variant: `SUBMIT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072`
- Rationale: For SCR-002-A01-SUBMIT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A02:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-043, RULE-017, RULE-023, RULE-075`
- Rationale: For SCR-002-A02, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-043, RULE-017, RULE-023, RULE-075) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A02:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-043, RULE-017, RULE-023, RULE-075, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-003, FLOW-001`
- Rationale: For SCR-002-A02, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-043, RULE-017, RULE-023, RULE-075, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-003, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A02:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-043, RULE-017, RULE-023, RULE-075`
- Rationale: For SCR-002-A02, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-043, RULE-017, RULE-023, RULE-075). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A03:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-025, RULE-026`
- Rationale: For SCR-002-A03, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-025, RULE-026) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A03:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-025, RULE-026, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-002, FLOW-001`
- Rationale: For SCR-002-A03, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-025, RULE-026, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-002, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A03:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-025, RULE-026`
- Rationale: For SCR-002-A03, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-025, RULE-026). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A04:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-045, RULE-029, REQ-002, AC-002`
- Rationale: For SCR-002-A04, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-045, RULE-029, REQ-002, AC-002) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A04:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-045, RULE-029, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-007, FLOW-001, REQ-002, AC-002`
- Rationale: For SCR-002-A04, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-045, RULE-029, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-007, FLOW-001, REQ-002, AC-002. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A04:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-045, RULE-056, RULE-029`
- Rationale: For SCR-002-A04, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-045, RULE-056, RULE-029). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A05:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-027, RULE-028, REQ-002, AC-002`
- Rationale: For SCR-002-A05, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-027, RULE-028, REQ-002, AC-002) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A05:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-027, RULE-028, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-002, FLOW-001, REQ-002, AC-002`
- Rationale: For SCR-002-A05, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-027, RULE-028, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-002, FLOW-001, REQ-002, AC-002. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A05:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-027, RULE-028`
- Rationale: For SCR-002-A05, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-027, RULE-028). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A06:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-030, RULE-031`
- Rationale: For SCR-002-A06, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-030, RULE-031) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A06:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-044, RULE-030, RULE-031, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-003, FLOW-001`
- Rationale: For SCR-002-A06, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-044, RULE-030, RULE-031, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-003, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A06:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-030, RULE-031`
- Rationale: For SCR-002-A06, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-030, RULE-031). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A07:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-004, RULE-051, RULE-074`
- Rationale: For SCR-002-A07, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-004, RULE-051, RULE-074) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A07:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-004, RULE-051, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A07, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-004, RULE-051, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A07:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-004, RULE-051, RULE-074`
- Rationale: For SCR-002-A07, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-004, RULE-051, RULE-074). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A08:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-003`
- Rationale: For SCR-002-A08, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-003) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A08:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-003, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A08, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-003, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A08:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-003`
- Rationale: For SCR-002-A08, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-003). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A09:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-034, RULE-058`
- Rationale: For SCR-002-A09, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-034, RULE-058) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A09:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-034, RULE-058, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-004, FLOW-001`
- Rationale: For SCR-002-A09, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-034, RULE-058, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A09:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-034, RULE-058`
- Rationale: For SCR-002-A09, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-034, RULE-058). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A10:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-028, RULE-034, RULE-035`
- Rationale: For SCR-002-A10, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-028, RULE-034, RULE-035) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A10:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-028, RULE-034, RULE-035, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-004, FLOW-001`
- Rationale: For SCR-002-A10, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-028, RULE-034, RULE-035, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A10:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-028, RULE-034, RULE-035`
- Rationale: For SCR-002-A10, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-028, RULE-034, RULE-035). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A11:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071`
- Rationale: For SCR-002-A11, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A11:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A11, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A11:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071`
- Rationale: For SCR-002-A11, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-043, RULE-001, RULE-006, RULE-036, RULE-037, RULE-038, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A12:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-043`
- Rationale: For SCR-002-A12, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-043) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A12:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-044, RULE-043, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A12, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-044, RULE-043, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A12:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-043`
- Rationale: For SCR-002-A12, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-043). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A13:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-050, RULE-077`
- Rationale: For SCR-002-A13, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-050, RULE-077) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A13:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-050, RULE-077, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A13, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-050, RULE-077, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A13:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-050, RULE-077`
- Rationale: For SCR-002-A13, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-050, RULE-077). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A14:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-066, RULE-071, RULE-074`
- Rationale: For SCR-002-A14, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-003, RULE-044, RULE-066, RULE-071, RULE-074) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A14:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-066, RULE-071, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A14, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-066, RULE-071, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A14:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-066, RULE-071, RULE-074`
- Rationale: For SCR-002-A14, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-066, RULE-071, RULE-074). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A15:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-066, RULE-074`
- Rationale: For SCR-002-A15, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-066, RULE-074) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A15:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-066, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A15, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-066, RULE-074, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A15:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-066, RULE-074`
- Rationale: For SCR-002-A15, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-066, RULE-074). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A16:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-005, USR-005, RULE-044, RULE-067, RULE-071`
- Rationale: For SCR-002-A16, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-005, RULE-044, RULE-067, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A16:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-005, USR-005, RULE-067, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A16, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-005, RULE-067, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A16:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-005, RULE-044, RULE-056, RULE-067, RULE-071`
- Rationale: For SCR-002-A16, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-005, RULE-044, RULE-056, RULE-067, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A17-NO-CREDIT-STATUS:input_invariants`

- Variant: `NO-CREDIT-STATUS`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-048, RULE-051`
- Rationale: For SCR-002-A17-NO-CREDIT-STATUS, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-048, RULE-051) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A17-NO-CREDIT-STATUS:test_obligations`

- Variant: `NO-CREDIT-STATUS`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-048, RULE-051, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A17-NO-CREDIT-STATUS, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-048, RULE-051, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A17-NO-CREDIT-STATUS:visible_error`

- Variant: `NO-CREDIT-STATUS`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-048, RULE-051`
- Rationale: For SCR-002-A17-NO-CREDIT-STATUS, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-048, RULE-051). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:input_invariants`

- Variant: `RETURN-TO-CUSTOMER-EXECUTE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-039, RULE-062, RULE-063, RULE-071`
- Rationale: For SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-003, RULE-044, RULE-039, RULE-062, RULE-063, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:test_obligations`

- Variant: `RETURN-TO-CUSTOMER-EXECUTE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-039, RULE-062, RULE-063, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-039, RULE-062, RULE-063, RULE-071, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:visible_error`

- Variant: `RETURN-TO-CUSTOMER-EXECUTE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-039, RULE-062, RULE-063, RULE-071`
- Rationale: For SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-039, RULE-062, RULE-063, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A18:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-040, RULE-047, RULE-049`
- Rationale: For SCR-002-A18, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-040, RULE-047, RULE-049) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A18:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-040, RULE-047, RULE-049, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-008, FLOW-001`
- Rationale: For SCR-002-A18, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-040, RULE-047, RULE-049, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A18:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-040, RULE-047, RULE-049`
- Rationale: For SCR-002-A18, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-040, RULE-047, RULE-049). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A19:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-046`
- Rationale: For SCR-002-A19, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-003, RULE-044, RULE-046) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A19:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-046, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A19, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-046, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A19:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-046`
- Rationale: For SCR-002-A19, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-046). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A20:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-048, RULE-076`
- Rationale: For SCR-002-A20, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-003, RULE-044, RULE-048, RULE-076) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A20:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-048, RULE-076, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A20, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-048, RULE-076, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A20:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-048, RULE-076`
- Rationale: For SCR-002-A20, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-048, RULE-076). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A21:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-053`
- Rationale: For SCR-002-A21, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-053) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A21:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-053, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A21, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-053, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A21:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-053`
- Rationale: For SCR-002-A21, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-053). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-002-A22:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-003, USR-003, RULE-044, RULE-054`
- Rationale: For SCR-002-A22, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-003, RULE-044, RULE-054) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-002-A22:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-002, USR-003, USR-003, RULE-054, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001`
- Rationale: For SCR-002-A22, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-002, USR-003, RULE-054, REQ-004, REQ-005, REQ-006, AC-004, AC-005, AC-006, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-002-A22:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-002, USR-003, RULE-044, RULE-056, RULE-054`
- Rationale: For SCR-002-A22, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-002, USR-003, RULE-044, RULE-056, RULE-054). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A01:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-032, RULE-034`
- Rationale: For SCR-003-A01, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-032, RULE-034) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A01:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-032, RULE-034, REQ-003, AC-003, STATE-004, FLOW-001`
- Rationale: For SCR-003-A01, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-032, RULE-034, REQ-003, AC-003, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A01:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-034`
- Rationale: For SCR-003-A01, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-034). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A02:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-011, RULE-019, RULE-021, RULE-032`
- Rationale: For SCR-003-A02, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-011, RULE-019, RULE-021, RULE-032) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A02:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-011, RULE-019, RULE-021, RULE-032, REQ-003, AC-003, STATE-004, FLOW-001`
- Rationale: For SCR-003-A02, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-011, RULE-019, RULE-021, RULE-032, REQ-003, AC-003, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A02:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-011, RULE-019, RULE-021, RULE-032`
- Rationale: For SCR-003-A02, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-011, RULE-019, RULE-021, RULE-032). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A03:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-032, RULE-065`
- Rationale: For SCR-003-A03, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-032, RULE-065) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A03:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-032, RULE-065, REQ-003, AC-003, STATE-004, FLOW-001`
- Rationale: For SCR-003-A03, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-032, RULE-065, REQ-003, AC-003, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A03:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-065`
- Rationale: For SCR-003-A03, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-065). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A04:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-033, RULE-057`
- Rationale: For SCR-003-A04, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-033, RULE-057) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A04:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-033, RULE-057, REQ-003, AC-003, STATE-004, FLOW-001`
- Rationale: For SCR-003-A04, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-033, RULE-057, REQ-003, AC-003, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A04:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-033, RULE-057`
- Rationale: For SCR-003-A04, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-033, RULE-057). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A05:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-032, RULE-033`
- Rationale: For SCR-003-A05, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-032, RULE-033) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A05:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-032, RULE-033, REQ-003, AC-003, STATE-004, FLOW-001`
- Rationale: For SCR-003-A05, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-032, RULE-033, REQ-003, AC-003, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A05:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-033`
- Rationale: For SCR-003-A05, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-032, RULE-033). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A06:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-034`
- Rationale: For SCR-003-A06, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-034) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A06:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-034, REQ-003, AC-003, STATE-004, FLOW-001`
- Rationale: For SCR-003-A06, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-034, REQ-003, AC-003, STATE-004, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A06:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-034`
- Rationale: For SCR-003-A06, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-034). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A07:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-066, RULE-071, RULE-074`
- Rationale: For SCR-003-A07, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-004, RULE-044, RULE-066, RULE-071, RULE-074) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A07:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-066, RULE-071, RULE-074, REQ-003, AC-003, STATE-005, FLOW-001`
- Rationale: For SCR-003-A07, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-066, RULE-071, RULE-074, REQ-003, AC-003, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A07:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-066, RULE-071, RULE-074`
- Rationale: For SCR-003-A07, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-066, RULE-071, RULE-074). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A08:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-040, RULE-051`
- Rationale: For SCR-003-A08, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-040, RULE-051) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A08:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-040, RULE-051, REQ-003, AC-003, STATE-008, FLOW-001`
- Rationale: For SCR-003-A08, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-040, RULE-051, REQ-003, AC-003, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A08:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-040, RULE-051`
- Rationale: For SCR-003-A08, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-040, RULE-051). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A09:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-040, RULE-051`
- Rationale: For SCR-003-A09, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-040, RULE-051) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A09:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-040, RULE-051, REQ-003, AC-003, STATE-008, FLOW-001`
- Rationale: For SCR-003-A09, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-040, RULE-051, REQ-003, AC-003, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A09:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-040, RULE-051`
- Rationale: For SCR-003-A09, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-040, RULE-051). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A10:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-051, RULE-071`
- Rationale: For SCR-003-A10, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-004, RULE-044, RULE-051, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A10:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-051, RULE-071, REQ-003, AC-003, STATE-008, FLOW-001`
- Rationale: For SCR-003-A10, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-051, RULE-071, REQ-003, AC-003, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A10:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-051, RULE-071`
- Rationale: For SCR-003-A10, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-051, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A11:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-053`
- Rationale: For SCR-003-A11, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-053) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A11:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-053, REQ-003, AC-003, STATE-008, FLOW-001`
- Rationale: For SCR-003-A11, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-053, REQ-003, AC-003, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A11:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-053`
- Rationale: For SCR-003-A11, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-053). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-003-A12:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-004, USR-004, RULE-044, RULE-054`
- Rationale: For SCR-003-A12, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-004, RULE-044, RULE-054) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-003-A12:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-003, USR-004, USR-004, RULE-054, REQ-003, AC-003, STATE-008, FLOW-001`
- Rationale: For SCR-003-A12, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-003, USR-004, RULE-054, REQ-003, AC-003, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-003-A12:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-003, USR-004, RULE-044, RULE-056, RULE-054`
- Rationale: For SCR-003-A12, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-003, USR-004, RULE-044, RULE-056, RULE-054). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A01-DELETE-DRAFT:input_invariants`

- Variant: `DELETE-DRAFT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-023, RULE-073`
- Rationale: For SCR-004-A01-DELETE-DRAFT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (USR-002, RULE-044, RULE-023, RULE-073) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A01-DELETE-DRAFT:test_obligations`

- Variant: `DELETE-DRAFT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-023, RULE-073, REQ-007, AC-007, STATE-001, FLOW-001`
- Rationale: For SCR-004-A01-DELETE-DRAFT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-023, RULE-073, REQ-007, AC-007, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A01-DELETE-DRAFT:visible_error`

- Variant: `DELETE-DRAFT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-073`
- Rationale: For SCR-004-A01-DELETE-DRAFT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-073). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A01-EDIT-DRAFT:input_invariants`

- Variant: `EDIT-DRAFT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-023, RULE-024, RULE-057`
- Rationale: For SCR-004-A01-EDIT-DRAFT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-002, RULE-044, RULE-023, RULE-024, RULE-057) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A01-EDIT-DRAFT:test_obligations`

- Variant: `EDIT-DRAFT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-023, RULE-024, RULE-057, REQ-007, AC-007, STATE-001, FLOW-001`
- Rationale: For SCR-004-A01-EDIT-DRAFT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-023, RULE-024, RULE-057, REQ-007, AC-007, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A01-EDIT-DRAFT:visible_error`

- Variant: `EDIT-DRAFT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-024, RULE-057`
- Rationale: For SCR-004-A01-EDIT-DRAFT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-024, RULE-057). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A01-SUBMIT:input_invariants`

- Variant: `SUBMIT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072`
- Rationale: For SCR-004-A01-SUBMIT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-002, RULE-044, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A01-SUBMIT:test_obligations`

- Variant: `SUBMIT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072, REQ-007, AC-007, STATE-001, FLOW-001`
- Rationale: For SCR-004-A01-SUBMIT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072, REQ-007, AC-007, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A01-SUBMIT:visible_error`

- Variant: `SUBMIT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072`
- Rationale: For SCR-004-A01-SUBMIT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-010, RULE-023, RULE-024, RULE-057, RULE-072). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A02:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-043, RULE-017, RULE-023, RULE-075`
- Rationale: For SCR-004-A02, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /reason. The cited CURRENT clauses (USR-002, RULE-044, RULE-043, RULE-017, RULE-023, RULE-075) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A02:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-043, RULE-017, RULE-023, RULE-075, REQ-007, AC-007, STATE-003, FLOW-001`
- Rationale: For SCR-004-A02, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-043, RULE-017, RULE-023, RULE-075, REQ-007, AC-007, STATE-003, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A02:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-043, RULE-017, RULE-023, RULE-075`
- Rationale: For SCR-004-A02, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-043, RULE-017, RULE-023, RULE-075). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A03:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-029, RULE-057, RULE-075`
- Rationale: For SCR-004-A03, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-002, RULE-044, RULE-029, RULE-057, RULE-075) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A03:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-029, RULE-057, RULE-075, REQ-007, AC-007, STATE-007, FLOW-001`
- Rationale: For SCR-004-A03, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-029, RULE-057, RULE-075, REQ-007, AC-007, STATE-007, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A03:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-029, RULE-057, RULE-075`
- Rationale: For SCR-004-A03, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-029, RULE-057, RULE-075). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A04:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-031, RULE-039, RULE-063`
- Rationale: For SCR-004-A04, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-002, RULE-044, RULE-031, RULE-039, RULE-063) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A04:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-031, RULE-039, RULE-063, REQ-007, AC-007, STATE-003, FLOW-001`
- Rationale: For SCR-004-A04, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-031, RULE-039, RULE-063, REQ-007, AC-007, STATE-003, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A04:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-031, RULE-039, RULE-063`
- Rationale: For SCR-004-A04, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-031, RULE-039, RULE-063). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A05:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-045, RULE-022, RULE-023`
- Rationale: For SCR-004-A05, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-002, RULE-044, RULE-045, RULE-022, RULE-023) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A05:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-045, RULE-022, RULE-023, REQ-007, AC-007, STATE-001, FLOW-001`
- Rationale: For SCR-004-A05, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-045, RULE-022, RULE-023, REQ-007, AC-007, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A05:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-045, RULE-056, RULE-022, RULE-023`
- Rationale: For SCR-004-A05, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-045, RULE-056, RULE-022, RULE-023). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A06:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-045, RULE-043, RULE-023, RULE-047`
- Rationale: For SCR-004-A06, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-002, RULE-044, RULE-045, RULE-043, RULE-023, RULE-047) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A06:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-045, RULE-043, RULE-023, RULE-047, REQ-007, AC-007, STATE-001, FLOW-001`
- Rationale: For SCR-004-A06, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-045, RULE-043, RULE-023, RULE-047, REQ-007, AC-007, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A06:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-045, RULE-056, RULE-043, RULE-023, RULE-047`
- Rationale: For SCR-004-A06, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-045, RULE-056, RULE-043, RULE-023, RULE-047). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A07:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-023, RULE-040, RULE-047, RULE-049`
- Rationale: For SCR-004-A07, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (USR-002, RULE-044, RULE-023, RULE-040, RULE-047, RULE-049) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A07:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-023, RULE-040, RULE-047, RULE-049, REQ-007, AC-007, STATE-008, FLOW-001`
- Rationale: For SCR-004-A07, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-023, RULE-040, RULE-047, RULE-049, REQ-007, AC-007, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A07:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-040, RULE-047, RULE-049`
- Rationale: For SCR-004-A07, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-023, RULE-040, RULE-047, RULE-049). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SCR-004-A08:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `USR-002, USR-002, RULE-044, RULE-022, RULE-046`
- Rationale: For SCR-004-A08, the executable set checks only presence/equality at /actorId, /targetId. The cited CURRENT clauses (USR-002, RULE-044, RULE-022, RULE-046) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SCR-004-A08:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `SCR-004, USR-002, USR-002, RULE-022, RULE-046, REQ-007, AC-007, STATE-001, FLOW-001`
- Rationale: For SCR-004-A08, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by SCR-004, USR-002, RULE-022, RULE-046, REQ-007, AC-007, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SCR-004-A08:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `SCR-004, USR-002, RULE-044, RULE-056, RULE-022, RULE-046`
- Rationale: For SCR-004-A08, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (SCR-004, USR-002, RULE-044, RULE-056, RULE-022, RULE-046). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A01-INTERNAL-AUTH-SESSION:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `RULE-059, USR-001, USR-001, RULE-044`
- Rationale: For SYS-A01-INTERNAL-AUTH-SESSION, the executable set checks only presence/equality at /accountId, /authOperation, /proof. The cited CURRENT clauses (RULE-059, USR-001, RULE-044) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A02-CUSTOMER-AUTH-SESSION:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `RULE-059, USR-002, USR-002, RULE-044, RULE-022`
- Rationale: For SYS-A02-CUSTOMER-AUTH-SESSION, the executable set checks only presence/equality at /accountId, /authOperation, /proof. The cited CURRENT clauses (RULE-059, USR-002, RULE-044, RULE-022) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A03-VALIDATE-ATTACHMENT:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `RULE-057, USR-002, USR-003, USR-004, RULE-044, RULE-033`
- Rationale: For SYS-A03-VALIDATE-ATTACHMENT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /file/name, /file/mimeType, /file/sizeBytes, /file/signature. The cited CURRENT clauses (RULE-057, USR-002, USR-003, USR-004, RULE-044, RULE-033) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A03-VALIDATE-ATTACHMENT:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `RULE-057, RULE-044, RULE-056, RULE-033`
- Rationale: For SYS-A03-VALIDATE-ATTACHMENT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (RULE-057, RULE-044, RULE-056, RULE-033). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `RULE-047, RULE-045, RULE-044`
- Rationale: For SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL, the executable set checks only presence/equality at /caseId, /notificationRef, /content/caseId, /content/resultAllocationScope, /content/result, /content/reason, /content/evidence, /content/trackingValues, /content/feeOrSettlementException, /content/isolationEnd, /content/disposalSchedule, /content/disputeDeadline, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (RULE-047, RULE-045, RULE-044) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `RULE-047, RULE-045, RULE-044, RULE-056`
- Rationale: For SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (RULE-047, RULE-045, RULE-044, RULE-056). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A05-MANUAL-DELIVERY-RETRY:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `RULE-045, USR-003, USR-003, RULE-044, RULE-047`
- Rationale: For SYS-A05-MANUAL-DELIVERY-RETRY, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (RULE-045, USR-003, RULE-044, RULE-047) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A05-MANUAL-DELIVERY-RETRY:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `RULE-045, USR-003, USR-003, RULE-047, REQ-005, REQ-006, AC-005, AC-006, STATE-008, FLOW-001`
- Rationale: For SYS-A05-MANUAL-DELIVERY-RETRY, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by RULE-045, USR-003, RULE-047, REQ-005, REQ-006, AC-005, AC-006, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A05-MANUAL-DELIVERY-RETRY:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `RULE-045, USR-003, RULE-044, RULE-056, RULE-047`
- Rationale: For SYS-A05-MANUAL-DELIVERY-RETRY, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (RULE-045, USR-003, RULE-044, RULE-056, RULE-047). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A06-INBOUND-CARRIER-EVENT:input_invariants`

- Variant: `INBOUND_TRACKING`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `INT-004, RULE-044, RULE-031, RULE-039`
- Rationale: For SYS-A06-INBOUND-CARRIER-EVENT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (INT-004, RULE-044, RULE-031, RULE-039) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A06-INBOUND-CARRIER-EVENT:test_obligations`

- Variant: `INBOUND_TRACKING`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `INT-004, INT-004, RULE-044, RULE-031, RULE-039, REQ-003, REQ-004, AC-003, AC-004, STATE-003, FLOW-001`
- Rationale: For SYS-A06-INBOUND-CARRIER-EVENT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by INT-004, RULE-044, RULE-031, RULE-039, REQ-003, REQ-004, AC-003, AC-004, STATE-003, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A06-INBOUND-CARRIER-EVENT:visible_error`

- Variant: `INBOUND_TRACKING`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `INT-004, INT-004, RULE-044, RULE-056, RULE-031, RULE-039`
- Rationale: For SYS-A06-INBOUND-CARRIER-EVENT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (INT-004, RULE-044, RULE-056, RULE-031, RULE-039). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:input_invariants`

- Variant: `REPLACEMENT_COMMIT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `INT-004, RULE-044, RULE-066, RULE-071`
- Rationale: For SYS-A06-REPLACEMENT-COMMIT-EVENT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (INT-004, RULE-044, RULE-066, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:test_obligations`

- Variant: `REPLACEMENT_COMMIT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `INT-004, INT-004, RULE-044, RULE-066, RULE-071, REQ-003, REQ-004, AC-003, AC-004, STATE-005, FLOW-001`
- Rationale: For SYS-A06-REPLACEMENT-COMMIT-EVENT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by INT-004, RULE-044, RULE-066, RULE-071, REQ-003, REQ-004, AC-003, AC-004, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:visible_error`

- Variant: `REPLACEMENT_COMMIT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `INT-004, INT-004, RULE-044, RULE-056, RULE-066, RULE-071`
- Rationale: For SYS-A06-REPLACEMENT-COMMIT-EVENT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (INT-004, RULE-044, RULE-056, RULE-066, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:input_invariants`

- Variant: `RETURN_TO_CUSTOMER_COMMIT`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `INT-004, RULE-044, RULE-039, RULE-062, RULE-071`
- Rationale: For SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (INT-004, RULE-044, RULE-039, RULE-062, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:test_obligations`

- Variant: `RETURN_TO_CUSTOMER_COMMIT`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `INT-004, INT-004, RULE-039, RULE-062, RULE-071, REQ-003, REQ-004, AC-003, AC-004, STATE-005, FLOW-001`
- Rationale: For SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by INT-004, RULE-039, RULE-062, RULE-071, REQ-003, REQ-004, AC-003, AC-004, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:visible_error`

- Variant: `RETURN_TO_CUSTOMER_COMMIT`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `INT-004, INT-004, RULE-044, RULE-056, RULE-039, RULE-062, RULE-071`
- Rationale: For SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (INT-004, RULE-044, RULE-056, RULE-039, RULE-062, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `INT-006, RULE-044, RULE-067, RULE-071`
- Rationale: For SYS-A07-REFUND-SETTLEMENT-SIMULATION, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey, /confirmation. The cited CURRENT clauses (INT-006, RULE-044, RULE-067, RULE-071) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `INT-006, INT-006, RULE-044, RULE-067, RULE-071, REQ-004, AC-004, STATE-005, FLOW-001`
- Rationale: For SYS-A07-REFUND-SETTLEMENT-SIMULATION, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by INT-006, RULE-044, RULE-067, RULE-071, REQ-004, AC-004, STATE-005, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `INT-006, INT-006, RULE-044, RULE-056, RULE-067, RULE-071`
- Rationale: For SYS-A07-REFUND-SETTLEMENT-SIMULATION, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (INT-006, RULE-044, RULE-056, RULE-067, RULE-071). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `INT-006, RULE-044, RULE-040, RULE-047, RULE-049`
- Rationale: For SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (INT-006, RULE-044, RULE-040, RULE-047, RULE-049) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `INT-006, INT-006, RULE-044, RULE-040, RULE-047, RULE-049, REQ-004, AC-004, STATE-008, FLOW-001`
- Rationale: For SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by INT-006, RULE-044, RULE-040, RULE-047, RULE-049, REQ-004, AC-004, STATE-008, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `INT-006, INT-006, RULE-044, RULE-056, RULE-040, RULE-047, RULE-049`
- Rationale: For SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (INT-006, RULE-044, RULE-056, RULE-040, RULE-047, RULE-049). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

### `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:input_invariants`

- Variant: `BASE`
- Family: `UNDER_BROAD_INPUT_INVARIANT_AND_DEFAULT_SUCCESS_FALLTHROUGH`
- Canonical objects: `RULE-056, USR-003, USR-003, RULE-044`
- Rationale: For SYS-A09-OUTAGE-QUEUE-RECONCILIATION, the executable set checks only presence/equality at /actorId, /targetId, /expectedVersion, /idempotencyKey. The cited CURRENT clauses (RULE-056, USR-003, RULE-044) also require the correct authority relationship and exact object/scope plus command-specific values, evidence, lifecycle/window, or commit guards. Those value constraints are absent, so an invalid or unauthorized payload can pass these invariants and fall through to the default SUCCESS class.

### `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:test_obligations`

- Variant: `BASE`
- Family: `MISSING_COMMAND_SPECIFIC_TEST_OBLIGATIONS`
- Canonical objects: `RULE-056, USR-003, USR-003, RULE-044, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001`
- Rationale: For SYS-A09-OUTAGE-QUEUE-RECONCILIATION, the emitted list exercises only reusable happy/role/version/replay/readback/delivery categories (with generic reason or confirmation checks where present). It contains no obligation that asserts the exact command-specific values, evidence, scope boundary, failure branch, or output restriction required by RULE-056, USR-003, RULE-044, REQ-005, REQ-006, AC-005, AC-006, STATE-001, FLOW-001. A conforming implementation could therefore pass this list while violating the cited action semantics.

### `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:visible_error`

- Variant: `BASE`
- Family: `VISIBLE_ERROR_AUTHORIZATION_DISCLOSURE_AND_PRESERVATION`
- Canonical objects: `RULE-056, USR-003, RULE-044`
- Rationale: For SYS-A09-OUTAGE-QUEUE-RECONCILIATION, the same error projection unconditionally shows the latest authoritative state and scope version while citing authorization and scope rules (RULE-056, USR-003, RULE-044). It does not condition that readback on continuing read authority, so a wrong-role or wrong-organization rejection can expose state/version data; it also reduces the cited action-specific preservation and recovery behavior to a generic saved checkpoint.

