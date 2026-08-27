# Contract Review Identity Diff

## Deterministic result

All `665` REVIEW_REQUIRED identities match exactly by owner kind, owner ID, and semantic field name. Both compiled wrappers remain `REVIEW_REQUIRED`. There are no old-only or new-only identities.

- Old candidate: `2dd2f41e996b37c22f6b960aee624160dd459b04afb31ef9e78c4e09cb76e1df`
- New candidate: `2621e7da2b576ca7d902989a720b6ed7af62b6c8895c2cfca77850421871e074`
- Exact identity mismatch: `0`
- Semantic value changes: `4`
- Mechanical-only field changes: `0`
- Unchanged semantic fields with verdict flips: `176`

## Confusion matrix

| Old verdict | New verdict | Count |
|---|---|---:|
| APPROVED | APPROVED | 485 |
| APPROVED | REJECTED | 176 |
| REJECTED | APPROVED | 0 |
| REJECTED | REJECTED | 4 |

## Authorized semantic edits

Only the four authorized identities changed semantic value and provenance. Each retained the same REVIEW_REQUIRED derivation class. The new input-invariant values add required `/reason`; the new test-obligation values add missing/empty-reason rejection, no-commit, and valid-input preservation coverage. Their exact refs add current `REQ-002@/objects/requirements/1/behavior` and `AC-002@/objects/acceptance_criteria/1/statement` authority.

### `action:SCR-002-A04:input_invariants`

- Old verdict → new verdict: `REJECTED → REJECTED`
- Old value SHA-256: `52aba5a8986555cbe68d21cfe99b897ecf3d70da83e08efa12d121e54b91fb92`
- New value SHA-256: `50a5f37aa3abdaafd6df57758861704b1ae578f37543c2d68e642aad714e60b4`
- Provenance refs changed: `true`

### `action:SCR-002-A04:test_obligations`

- Old verdict → new verdict: `REJECTED → REJECTED`
- Old value SHA-256: `b73d8047abb95a9239da3ea6c9557439b340a0b226c5e5a713409a6615d2060d`
- New value SHA-256: `ac250dfadc7557154b702127aa6cf88f749e9e9eae9e9f2a7010a1cfda076425`
- Provenance refs changed: `true`

### `action:SCR-002-A05:input_invariants`

- Old verdict → new verdict: `REJECTED → REJECTED`
- Old value SHA-256: `52aba5a8986555cbe68d21cfe99b897ecf3d70da83e08efa12d121e54b91fb92`
- New value SHA-256: `50a5f37aa3abdaafd6df57758861704b1ae578f37543c2d68e642aad714e60b4`
- Provenance refs changed: `true`

### `action:SCR-002-A05:test_obligations`

- Old verdict → new verdict: `REJECTED → REJECTED`
- Old value SHA-256: `b73d8047abb95a9239da3ea6c9557439b340a0b226c5e5a713409a6615d2060d`
- New value SHA-256: `79fdf6b581c1765a171d12c546ba2707a3e5efa87784e513f743313a6da79aba`
- Provenance refs changed: `true`

## Review-instruction identity

The review schema version and identity set are the same, but the two review briefs are not byte-identical:

- Old brief SHA-256: `c9063a3e1199a30183969b44331c42c43338d0a8d1a60d50746a23d6458c232d`
- New brief SHA-256: `e5aa4ba0a302a82749341e1acf4ae46f55e3ce3363b889359c1b699dd48ae737`
- Old brief asks for field-specific rationales and says absence of canonical authority means a condition must not be added.
- New brief asks whether each emitted value is fully supported and explicitly directs the reviewer to detect omitted constraints.

This is deterministic input evidence only; semantic adjudication is deferred to the isolated adjudication phase.

## Previously approved, semantically unchanged fields that became rejected

- `action:SCR-001-A01:input_invariants`
- `action:SCR-001-A01:test_obligations`
- `action:SCR-001-A01:visible_error`
- `action:SCR-001-A02:input_invariants`
- `action:SCR-001-A02:test_obligations`
- `action:SCR-001-A02:visible_error`
- `action:SCR-001-A03:input_invariants`
- `action:SCR-001-A03:test_obligations`
- `action:SCR-001-A03:visible_error`
- `action:SCR-001-A04:input_invariants`
- `action:SCR-001-A04:test_obligations`
- `action:SCR-001-A04:visible_error`
- `action:SCR-002-A01-DELETE-DRAFT:input_invariants`
- `action:SCR-002-A01-DELETE-DRAFT:test_obligations`
- `action:SCR-002-A01-DELETE-DRAFT:visible_error`
- `action:SCR-002-A01-EDIT-DRAFT:input_invariants`
- `action:SCR-002-A01-EDIT-DRAFT:test_obligations`
- `action:SCR-002-A01-EDIT-DRAFT:visible_error`
- `action:SCR-002-A01-SUBMIT:input_invariants`
- `action:SCR-002-A01-SUBMIT:test_obligations`
- `action:SCR-002-A01-SUBMIT:visible_error`
- `action:SCR-002-A02:input_invariants`
- `action:SCR-002-A02:test_obligations`
- `action:SCR-002-A02:visible_error`
- `action:SCR-002-A03:input_invariants`
- `action:SCR-002-A03:test_obligations`
- `action:SCR-002-A03:visible_error`
- `action:SCR-002-A04:visible_error`
- `action:SCR-002-A05:visible_error`
- `action:SCR-002-A06:input_invariants`
- `action:SCR-002-A06:test_obligations`
- `action:SCR-002-A06:visible_error`
- `action:SCR-002-A07:input_invariants`
- `action:SCR-002-A07:test_obligations`
- `action:SCR-002-A07:visible_error`
- `action:SCR-002-A08:input_invariants`
- `action:SCR-002-A08:test_obligations`
- `action:SCR-002-A08:visible_error`
- `action:SCR-002-A09:input_invariants`
- `action:SCR-002-A09:test_obligations`
- `action:SCR-002-A09:visible_error`
- `action:SCR-002-A10:input_invariants`
- `action:SCR-002-A10:test_obligations`
- `action:SCR-002-A10:visible_error`
- `action:SCR-002-A11:input_invariants`
- `action:SCR-002-A11:test_obligations`
- `action:SCR-002-A11:visible_error`
- `action:SCR-002-A12:input_invariants`
- `action:SCR-002-A12:test_obligations`
- `action:SCR-002-A12:visible_error`
- `action:SCR-002-A13:input_invariants`
- `action:SCR-002-A13:test_obligations`
- `action:SCR-002-A13:visible_error`
- `action:SCR-002-A14:input_invariants`
- `action:SCR-002-A14:test_obligations`
- `action:SCR-002-A14:visible_error`
- `action:SCR-002-A15:input_invariants`
- `action:SCR-002-A15:test_obligations`
- `action:SCR-002-A15:visible_error`
- `action:SCR-002-A16:input_invariants`
- `action:SCR-002-A16:test_obligations`
- `action:SCR-002-A16:visible_error`
- `action:SCR-002-A17-NO-CREDIT-STATUS:input_invariants`
- `action:SCR-002-A17-NO-CREDIT-STATUS:test_obligations`
- `action:SCR-002-A17-NO-CREDIT-STATUS:visible_error`
- `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:input_invariants`
- `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:test_obligations`
- `action:SCR-002-A17-RETURN-TO-CUSTOMER-EXECUTE:visible_error`
- `action:SCR-002-A18:input_invariants`
- `action:SCR-002-A18:test_obligations`
- `action:SCR-002-A18:visible_error`
- `action:SCR-002-A19:input_invariants`
- `action:SCR-002-A19:test_obligations`
- `action:SCR-002-A19:visible_error`
- `action:SCR-002-A20:input_invariants`
- `action:SCR-002-A20:test_obligations`
- `action:SCR-002-A20:visible_error`
- `action:SCR-002-A21:input_invariants`
- `action:SCR-002-A21:test_obligations`
- `action:SCR-002-A21:visible_error`
- `action:SCR-002-A22:input_invariants`
- `action:SCR-002-A22:test_obligations`
- `action:SCR-002-A22:visible_error`
- `action:SCR-003-A01:input_invariants`
- `action:SCR-003-A01:test_obligations`
- `action:SCR-003-A01:visible_error`
- `action:SCR-003-A02:input_invariants`
- `action:SCR-003-A02:test_obligations`
- `action:SCR-003-A02:visible_error`
- `action:SCR-003-A03:input_invariants`
- `action:SCR-003-A03:test_obligations`
- `action:SCR-003-A03:visible_error`
- `action:SCR-003-A04:input_invariants`
- `action:SCR-003-A04:test_obligations`
- `action:SCR-003-A04:visible_error`
- `action:SCR-003-A05:input_invariants`
- `action:SCR-003-A05:test_obligations`
- `action:SCR-003-A05:visible_error`
- `action:SCR-003-A06:input_invariants`
- `action:SCR-003-A06:test_obligations`
- `action:SCR-003-A06:visible_error`
- `action:SCR-003-A07:input_invariants`
- `action:SCR-003-A07:test_obligations`
- `action:SCR-003-A07:visible_error`
- `action:SCR-003-A08:input_invariants`
- `action:SCR-003-A08:test_obligations`
- `action:SCR-003-A08:visible_error`
- `action:SCR-003-A09:input_invariants`
- `action:SCR-003-A09:test_obligations`
- `action:SCR-003-A09:visible_error`
- `action:SCR-003-A10:input_invariants`
- `action:SCR-003-A10:test_obligations`
- `action:SCR-003-A10:visible_error`
- `action:SCR-003-A11:input_invariants`
- `action:SCR-003-A11:test_obligations`
- `action:SCR-003-A11:visible_error`
- `action:SCR-003-A12:input_invariants`
- `action:SCR-003-A12:test_obligations`
- `action:SCR-003-A12:visible_error`
- `action:SCR-004-A01-DELETE-DRAFT:input_invariants`
- `action:SCR-004-A01-DELETE-DRAFT:test_obligations`
- `action:SCR-004-A01-DELETE-DRAFT:visible_error`
- `action:SCR-004-A01-EDIT-DRAFT:input_invariants`
- `action:SCR-004-A01-EDIT-DRAFT:test_obligations`
- `action:SCR-004-A01-EDIT-DRAFT:visible_error`
- `action:SCR-004-A01-SUBMIT:input_invariants`
- `action:SCR-004-A01-SUBMIT:test_obligations`
- `action:SCR-004-A01-SUBMIT:visible_error`
- `action:SCR-004-A02:input_invariants`
- `action:SCR-004-A02:test_obligations`
- `action:SCR-004-A02:visible_error`
- `action:SCR-004-A03:input_invariants`
- `action:SCR-004-A03:test_obligations`
- `action:SCR-004-A03:visible_error`
- `action:SCR-004-A04:input_invariants`
- `action:SCR-004-A04:test_obligations`
- `action:SCR-004-A04:visible_error`
- `action:SCR-004-A05:input_invariants`
- `action:SCR-004-A05:test_obligations`
- `action:SCR-004-A05:visible_error`
- `action:SCR-004-A06:input_invariants`
- `action:SCR-004-A06:test_obligations`
- `action:SCR-004-A06:visible_error`
- `action:SCR-004-A07:input_invariants`
- `action:SCR-004-A07:test_obligations`
- `action:SCR-004-A07:visible_error`
- `action:SCR-004-A08:input_invariants`
- `action:SCR-004-A08:test_obligations`
- `action:SCR-004-A08:visible_error`
- `action:SYS-A01-INTERNAL-AUTH-SESSION:input_invariants`
- `action:SYS-A02-CUSTOMER-AUTH-SESSION:input_invariants`
- `action:SYS-A03-VALIDATE-ATTACHMENT:input_invariants`
- `action:SYS-A03-VALIDATE-ATTACHMENT:visible_error`
- `action:SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL:input_invariants`
- `action:SYS-A04-PUBLISH-NOTIFICATION-AND-DELIVER-EMAIL:visible_error`
- `action:SYS-A05-MANUAL-DELIVERY-RETRY:input_invariants`
- `action:SYS-A05-MANUAL-DELIVERY-RETRY:test_obligations`
- `action:SYS-A05-MANUAL-DELIVERY-RETRY:visible_error`
- `action:SYS-A06-INBOUND-CARRIER-EVENT:input_invariants`
- `action:SYS-A06-INBOUND-CARRIER-EVENT:test_obligations`
- `action:SYS-A06-INBOUND-CARRIER-EVENT:visible_error`
- `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:input_invariants`
- `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:test_obligations`
- `action:SYS-A06-REPLACEMENT-COMMIT-EVENT:visible_error`
- `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:input_invariants`
- `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:test_obligations`
- `action:SYS-A06-RETURN-TO-CUSTOMER-COMMIT-EVENT:visible_error`
- `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:input_invariants`
- `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:test_obligations`
- `action:SYS-A07-REFUND-SETTLEMENT-SIMULATION:visible_error`
- `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:input_invariants`
- `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:test_obligations`
- `action:SYS-A08-NO-CREDIT-SETTLEMENT-AUTOMATION:visible_error`
- `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:input_invariants`
- `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:test_obligations`
- `action:SYS-A09-OUTAGE-QUEUE-RECONCILIATION:visible_error`
