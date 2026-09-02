# Core Semantic Closure V2 M6 — final integration audit and Revision-2 regeneration

Date: 2026-08-31

Status: `INTEGRATION_ADOPTION_VERIFIED / R1_R10_FINAL_GATE_PASS`

This audit records the exact integrated source and dogfood evidence available
at Task 6. The continuation's fresh regression matrix, frozen/compatibility
audit, and independent 0/0/0 review passed. `READY_FOR_MERGE` applies only to
this feature branch; production deployment and a main merge are not claimed.

## Integration lineage

```text
preserved M6 pre-integration HEAD: d38b0ca04768888c47e658c79f41e1cec0a7a1ce
preserved M6 pre-integration tree: 40749d900b98936cf694b0c96db7897011cddae8

authoritative integrated M5.1 source HEAD: 8e21b3b3d6cfba79e9c1b9dd97487b87484cc802
authoritative integrated M5.1 source tree: 78d51bc24364f8b9c173ae9c5758feccd8375a64

M5.1-to-M6 merge commit: 00fa9b9bc0fce9c4895ba5097343dc6bc6cf3c77
Task-B final evidence source HEAD: 515fe09e32ed07aaa7dc19e9203a9f6e41505eae
```

The committed M5.1
`evals/core-semantic-closure-v2-m5-1/FINAL_IMPLEMENTATION_AUDIT.md`
contains pre-final-repair delivery/test metadata, including an older local
implementation HEAD and an historical `remote implementation branch: absent`
statement. Preserve it as historical evidence. It is not the authoritative
post-repair remote/integration status. The exact source integrated here is
`8e21b3b3d6cfba79e9c1b9dd97487b87484cc802`.

## Historical original-M6 Product Definition identity

The bounded dogfood Product Definition was not revised during the original
M5.1/M6 integration. That historical run used:

```text
schema: 0.2.0
definition revision: 1
definition status: CLOSED
approval status: APPROVED
approved by: user
approved at: 2026-08-30T11:54:26Z
definition digest: e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c
Approval Manifest digest: 60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705
approval history commitments: exactly 1, matching revision 1
```

Raw file commitments at the historical Task-B source HEAD:

```text
dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json
  SHA-256 728744301bc0ea2a1766852b7b46bab3c610215b31f63c0a784dd804fa3ce49d

dogfood/final-state.json
  SHA-256 d75decf1a92e67498cc7362059b7b7df2bc1276f72cfc55654d4af1e28f17423
  parsed structure equals the canonical dogfood state

dogfood/approval-manifest.json
  SHA-256 f354e7baf1001bf1cd2a763569b310947ca2fd1ae4e6eb57c6f1573d9ec2eef1
```

At that historical HEAD, the different state file byte encodings did not
represent different semantics; their parsed JSON structures were exact equals.
`dogfood/final-state.json` remains this revision-1 historical snapshot and is
not the current canonical authority.

## Current approved Revision-2 identity

After the original M6 run, DEC-042 provenance was corrected without changing
product or UX meaning. The exact current approved authority is:

```text
schema: 0.2.0
definition revision: 2
definition status: CLOSED
approval status: APPROVED
approved by: user
approved at: 2026-09-02T11:53:47Z
definition digest: 81d3b7ff59dbce321dc27fab6b51f03db4201dc1f4a1ea3d6b202f3f76afddcf
Approval Manifest digest: 079ef1bb60ccc382a66c6c764519e67e606744a9d10425310cc1b868be490003
approval history commitments: exactly 2, matching revisions 1 and 2
revision-1-to-2 changed record hashes: DEC-042, EVD-015, UNK-050
```

The revision-1 definition/manifest commitment above remains intact as the
first history entry. Revision 2 changes only provenance representation; it did
not exist during the historical original M6 run.

## Preserved historical 2.0 stop

The M6 continuation retained the old action-conformance/2.0 failure as
separate historical evidence:

```text
dogfood/handoff-definition.json
  SHA-256 11fdce0fdce90d8c2f5e069cd766aa338e5f4efd7653d38e2d152509653fbaef

dogfood/reentry-probe.json
  SHA-256 b6e0b4960211456a6dacf521a407667c0b838b5b1dee50db9ab02f2b9534e211
  status REENTRY_REQUIRED
  direct authority 131
  authority gaps 25
  re-entry events 25
```

These artifacts were not rewritten to make 2.0 successful. Their 25-gap
result remains evidence that the old contract misclassified representation
limits; it is not the current 2.1 result. It did not change revision 1 during
the original run and does not alter the current approved revision 2.

## Current installed route and frozen inputs

The documented installed V2 route is:

```text
state 0.2.0 CLOSED/APPROVED
→ joewrks.handoff-definition/2.1
→ joewrks.action-conformance/2.1
→ dependency-scoped 2.1 audit
→ joewrks.semantic-review/2.1 only when REVIEW_REQUIRED
→ joewrks.runtime-conformance-plan/1.0
→ frozen joewrks.downstream.execution/1.0 records
→ joewrks.runtime-evidence-bundle/1.0
→ joewrks.runtime-conformance-report/1.0
```

Readback at the Task-B source HEAD preserves these Git objects:

```text
skills/joewrks-product-definition/downstream/
  tree b63568d8c4632b14bc806e7bff1908e94dea9669
skills/joewrks-product-definition/downstream_v2/
  tree 33fb2653531fa85dcc8fd8c94cbbb7cc5c41d41e
skills/joewrks-product-definition/downstream_v21/
  tree d4f396103e44673cdbb10606b998304575aaaa4c
evals/semantic-review-v0.4.3/
  tree a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
product-definition/client-feedback-portal-dogfood/
  tree 22f8c2ccb8f9d77e54867c44dbdbcea63e42a052
product-definition/client-feedback-portal-dogfood/state.json
  blob 44a29cc4ecb7a8772b6441d73d7a7acb52188e6e
```

Legacy `0.1.2.1` blobs remain:

```text
schema    6a03894cc2164a9bfabbe8627a8468124d19b1f7
validator 9a3b44359bddfd64c98392f235cb815a0b777cce
reference 05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf
template  5fed7e87da243b3d234148bbbbf3baf7350d8ab0
```

The final controller audit read these identities again after the Task-C and
deterministic wiring changes. Every listed object matched exactly.

## Current Revision-2 regenerated 2.1 compile

The approved bounded state compiles through the M5.1 source with:

```text
contract: joewrks.action-conformance/2.1
source revision: 2
source definition digest: 81d3b7ff59dbce321dc27fab6b51f03db4201dc1f4a1ea3d6b202f3f76afddcf
source Approval Manifest digest: 079ef1bb60ccc382a66c6c764519e67e606744a9d10425310cc1b868be490003
handoff-definition-v21.json SHA-256: 83bce7dade12871f1289032796d6d58149b294b19788b77ecb55e1012519c062
contract artifact hash: 715ec9722174098e81470013e29c1b5059230c67ef2a015064a872716ed1668a
semantic contract hash: 56027cc08452fd0736315068cde7fa2377df661f39fc5e88c919ca4d00ff4c5b
action-contract-v21.json SHA-256: 7fe72d553f295f3d5046e548173ad79c8f8adbb83de3c64a363d47265a2bc3c3
actions: 6
lifecycles: 0
direct-authority fields: 131
machine-derived fields: 7
review-required fields: 0
authority/semantic gaps: 0
contract-expressiveness gaps: 0
re-entry events: 0
dependency audit: CONFORMANT
semantic review package/output: NOT_REQUIRED
semantic-review/2.1 reliability: NOT_MEASURED
```

The runtime plan is non-authoritative verification metadata:

```text
plan: joewrks.runtime-conformance-plan/1.0
plan hash: 9d4476123d64635727b2a313d6b453ba38245d10cba14da3c41bd1f1e0c42d80
plan file SHA-256: b91b854b1d1cc40caf6a3348c4202de644897b65b02bd3edf12fb4fe18a125d0
runtime-responsibility digest: 035e83a108f96aeedc6475fe606a60312e326cb80d52522e51d67691e172ac64
runtime-critical field refs: 120
covered field refs: 120
missing field refs: 0
runtime mapping gaps: 0
coverage: COMPLETE
planned action cases: 24
planned lifecycle cases: 0
```

## Full-contract runtime result

The deterministic fixture executed 24 distinct planned action cases covering
`SUCCESS`, `REJECTED`, `STALE`, and `IDEMPOTENT_REPLAY` for each of the six
actions. The evidence bundle contains exactly one frozen execution/1.0 record
per planned test ID.

```text
runtime evidence records: 24
required action test IDs: 24
observed action test IDs: 24
missing action test IDs: 0
unexpected action test IDs: 0
duplicate evidence count: 0

runtime-evidence.jsonl SHA-256: 060ab616c90840b72cc52c1160ad1e242da122359643444319a8c1153a1cdc37
bundle hash: 402fb2bde69f1e6af34a38cceadea4c0cd2984026df8965fba087ca3ed47a48c
bundle file SHA-256: 341f3419984bb05df69edc24dbc0400d59f107f52a3ef9da899947463d94eb40
report file SHA-256: 601fb31e8582a53b2b5e0012f10b3e80523e24ebbf4644ea81f4206e9276bbbd

verification_scope: FULL_CONTRACT
contract_dependency_status: CONFORMANT
coverage_status: COMPLETE
action_coverage_status: COMPLETE
lifecycle_applicability: NOT_APPLICABLE
lifecycle_coverage_status: COMPLETE
runtime_status: CONFORMANT
implementation_status: IMPLEMENTATION_CONFORMANT
```

`NOT_APPLICABLE` is used only because the semantic contract contains zero
lifecycle items. Bundle admission/completeness alone is not treated as runtime
conformance: the M6 verifier re-executes and independently binds each command,
result class, five-component before/after snapshot, assertion, delta,
authority, contract hash, and runtime-plan case.

## Controlled probes

The committed drift probe mutates only a copied `create_pin` command:

```text
implementation-drift-probe.json SHA-256:
  b062ab657f475b2b79cbd2f3663b4abafc1d78c33f34f0fa4b8565a4ba6ffe54
outer probe_status: PARTIAL_PROBE
nested verification_scope: PARTIAL_PROBE
nested runtime_status: NON_CONFORMANT
nested implementation_status: IMPLEMENTATION_NOT_CONFORMANT
```

The 2.1 re-entry probe mutates one copied field to genuinely unresolved:

```text
reentry-probe-v21.json SHA-256:
  03d89136ec4105fc7c85961322e44b17092bcd82cd2c13b4871b62c94988cbbf
status: REENTRY_REQUIRED
SEMANTIC_AUTHORITY_GAP: 1
CONTRACT_EXPRESSIVENESS_GAP: 0
re-entry events: 1
halt scope: AFFECTED_ONLY / create_pin
contract: null
```

Neither probe mutates the approved state, final 2.1 contract, final runtime
evidence, or historical 2.0 evidence. A partial probe cannot produce global
implementation conformance.

## Revision-1 to Revision-2 identity and semantic diff

The valid revision-1 chain at parent `486a3423cde494d912c016cb82a4137c8589f594`
was compared recursively with the regenerated revision-2 chain. The complete
leaf-difference classification is:

```text
EXPECTED_PROVENANCE_PROPAGATION: 491
EXPECTED_IDENTITY_PROPAGATION: 352
UNEXPECTED_SEMANTIC_DRIFT: 0
```

The provenance category contains only the approved revision, definition and
manifest digests, canonical state snapshot digest, and their repeated evidence
bindings. The identity category contains only derived contract/plan/bundle,
evidence, and re-entry event identities. Removing exactly those named fields
makes all eight generated chain/probe artifacts compare equal; the handoff is
already structurally equal without normalization.

All six action definitions and expected result classes remain unchanged.
Recovery, concurrency, idempotency, commands, state transitions, effects,
assertions, and probe mutations remain unchanged. No Product Definition
authority was added or removed.

## Gap and authority boundary

The integrated architecture keeps these failure classes separate:

- `SEMANTIC_AUTHORITY_GAP`: product meaning is unresolved, so only the exact
  affected scope re-enters Product Definition.
- `CONTRACT_EXPRESSIVENESS_GAP`: eligible approved meaning exists but the
  action-conformance/2.1 vocabulary cannot carry it, so the semantic contract
  evolves without a Product Definition revision by itself.
- `RUNTIME_MAPPING_GAP`: action-conformance/2.1 is complete but executable
  mapping is missing, so the non-authoritative runtime plan is repaired without
  a Product Definition revision by itself.

The runtime planner consumes the validated 2.1 semantic contract and optional
review output, never Product Definition directly. Product-specific expected
values remain contract/basis-derived; the plan is not shadow product authority.

## Migration and scope boundary

Track A is still the complete historical migration audit:

```text
candidate revision/status: 45 / OPEN
approval: UNAPPROVED
stable IDs preserved: 269/269
promoted IDs: 0
archived legacy records: 269
generated canonical IDs: 0
reconciliation gaps: 1151
legacy COVERED promoted to V2 COVERED: 0
```

Full historical client-feedback reconciliation remains an `OPEN` candidate.
Track B is the separately approved bounded native V2 workflow unit. Its
`IMPLEMENTATION_CONFORMANT` dogfood result does not close, trim, replace, or
supersede Track A.

## Historical original-M6 R1–R10 and final gates

`R1_R10_TRACEABILITY.md` binds all ten rows to production files, executable
tests, and committed M6 artifacts. Every row is now `VERIFIED / FINAL_GATE_PASS`;
none passes from documentation alone.

Historical Task-C focused verification ran the Phase-A/Phase-B dogfood, real fixture,
2.1 semantic runtime verifier, installed routing, re-entry, dependency audit,
compiler/gap routing, runtime plan/evidence, and frozen-boundary modules:

```text
150 tests, OK
```

The first documentation run exposed one stale checkpoint-wording expectation:
the current evaluation README no longer contained the historical
`READY_FOR_REVIEW` marker. The README was corrected to state both the immutable
Phase-A `READY_FOR_REVIEW / UNAPPROVED` checkpoint and the later revision-1
`CLOSED / APPROVED` state. The affected test passed, then the exact full focused
set passed 150/150. No production or test expectation was weakened.

Historical original-M6 continuation verification after all production and test changes:

```text
M6 focused: 29/29 PASS
M5.1 downstream-v21: 112/112 PASS
M5 downstream-v2: 168/168 PASS
Core V2: 337/337 PASS
state/re-entry workflow: 29/29 PASS
downstream v1: 44 PASS, 1 accepted environment skip
semantic review: 125/125 PASS
official calibration controller: 21/21 PASS
legacy: 45/45 PASS
migration Track A: 71/71 PASS
installed workflow/package: 20/20 PASS
runtime full-contract: 124/124 PASS
full repository: 925 tests, OK, skipped=1
git diff --check: PASS
frozen/compatibility readback: exact
independent review Critical/Important/Minor: 0/0/0
branch push/remote readback: controller-owned final action after this audit
```

The sole skip is
`test_pinned_a_and_b_defects_are_executed_and_detected`: its explicitly
external `JOEWRKS_FROZEN_A_ROOT` and `JOEWRKS_FROZEN_B_WORKTREE` inputs were
not supplied. This is the continuation's historically accepted environment
skip; no additional skip occurred.

## Claims not made

```text
semantic-review/2.1 reliability: NOT_MEASURED
v0.4.3 calibration disposition: unchanged
full historical client-feedback portal migration: OPEN reconciliation candidate
production deployment: NOT_CLAIMED
main merge: NOT_PERFORMED
overall program v0.5: NOT_CLAIMED
READY_FOR_MERGE: feature-branch claim only
```
