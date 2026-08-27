# v0.4.3 Field Responsibility Matrix

This matrix is normative for `joewrks.semantic-review/1.0`. It assigns one responsibility rule to every current `joewrks.action-conformance/1.0` action semantic field and every current lifecycle semantic field.

The implemented machine-readable profile SHALL begin with `rubric_calibration_revision: 1` and increase it monotonically. Its complete file SHA-256 is the normative rubric hash. Every failed calibration increments that revision even when the diagnosed rule text does not otherwise change; old and new hashes are never pooled.

## Completeness modes

- `LOCAL`: complete for the semantics owned by this field; sibling-owned semantics MUST NOT be required here.
- `COMPOSITIONAL`: owns a distinct projection and SHALL identify the sibling obligations on which that projection depends.
- `REFERENCE_ONLY`: owns stable references or coverage links, not copied business semantics.

An omission exists only when an owned semantic projection is missing, contradicted, untestable where testing is required, or replaced by an unresolved reference. Unsupported overreach exists when a field invents a constraint, outcome, disclosure, recovery, side effect, or test meaning not supported by its exact canonical evidence and responsibility rule.

## Action semantic fields

| Rule | Field | Mode | Owns | May reference | Must not duplicate | Omission | Unsupported overreach |
|---|---|---|---|---|---|---|---|
| `FR-A01` | `actor` | LOCAL | Eligible business/system actor identity and role | authentication, relationship | session mechanics or relationship predicates | required actor class absent/wrong | extra role or broadened actor |
| `FR-A02` | `authentication` | LOCAL | Authentication/session prerequisite | actor | authorization relationship or object scope | required authentication condition absent | invented authentication factor/session rule |
| `FR-A03` | `relationship_predicate` | LOCAL | Current authority/ownership/organization relationship | actor, object binding | authentication mechanics or object identity | required relationship test absent | broader/narrower relationship than authority |
| `FR-A04` | `object_binding` | LOCAL | Exact target object, tenant, scope, and revision binding | relationship, command | permission or lifecycle prose | target/scope binding missing | cross-object or cross-tenant scope invented |
| `FR-A05` | `concurrency` | LOCAL | Expected-version, atomicity, conflict, and single-winner rule | object binding, idempotency | visible conflict UI or generic command predicates | required concurrency boundary absent | unsupported lock/version behavior |
| `FR-A06` | `preconditions` | LOCAL | Non-input domain prerequisites before command acceptance | states, relationship, object binding | raw input validation or result behavior | required domain prerequisite absent | invented prerequisite |
| `FR-A07` | `allowed_current_states` | LOCAL | States in which invocation may proceed | preconditions, lifecycle | forbidden-state outcome or recovery | allowed-state set incomplete/wrong | unsupported allowed state |
| `FR-A08` | `forbidden_states` | LOCAL | States that block invocation | rejection, lifecycle | complete rejection/visible-error behavior | forbidden state absent | unsupported forbidden state |
| `FR-A09` | `input_invariants` | LOCAL | Command-input predicates evaluated before/as acceptance: required reason/evidence, bounds, enums, confirmation input, input-level binding | command, object binding, preconditions | visible error, recovery, tests, domain mutation, non-input authority rules | applicable input predicate absent | non-input domain/UX/test rule represented as input predicate |
| `FR-A10` | `command` | LOCAL | Command name, envelope, parameters, and declared target | input invariants, object binding | guards, mutation outcome, UI | required command input/variant absent | command capability not authorized |
| `FR-A11` | `expected_domain_mutation` | LOCAL | Required authoritative state change on successful commit | command, result expectations | history/effects/delivery details owned elsewhere | required mutation absent/wrong | mutation not supported by authority |
| `FR-A12` | `forbidden_mutations` | LOCAL | State/effect areas that MUST remain unchanged for the scoped action/result | result expectations, rejection | complete result table or visible response | protected area missing | prohibits authorized mutation |
| `FR-A13` | `default_result` | LOCAL | Default result class after all owned guards pass | result expectations | guards or component changes | missing/wrong default class | result class not supported by action semantics |
| `FR-A14` | `result_expectations` | COMPOSITIONAL | Per-result five-component change classification and evidence assertions | default result, mutations, version/history/effects, rejection | source fields' full prose | applicable result class/component/reference absent | component change or assertion not supported |
| `FR-A15` | `version_result` | LOCAL | Revision/version effect by result boundary | concurrency, result expectations | state/history behavior | required version change/no-op absent | unsupported version increment/preservation |
| `FR-A16` | `history_result` | LOCAL | Audit/history append, preservation, or no-op | result expectations, trace | domain mutation or delivery | required audit effect absent | invented audit event/content |
| `FR-A17` | `business_side_effects` | LOCAL | Non-authoritative business effects and their commit boundary | result expectations, idempotency | delivery/notification effects | required business effect/no-op absent | unsupported or duplicated effect |
| `FR-A18` | `delivery_effects` | LOCAL | Notification/delivery attempt, separation, retry, and delivery state | result expectations, recovery | authoritative business commit | required delivery effect/separation absent | notification treated as business commit or invented delivery |
| `FR-A19` | `idempotency` | LOCAL | Key scope, same-input replay, different-input conflict, and effect deduplication | command, concurrency, effects | general version or recovery prose | required replay/conflict rule absent | unsupported replay/deduplication behavior |
| `FR-A20` | `rejection` | LOCAL | Failure categories, rejection result, authoritative no-op, and permitted audit-only effects | guards, result expectations | visible presentation or recovery affordance | required rejection/no-op branch absent | candidate rejects authorized input or mutates forbidden state |
| `FR-A21` | `recovery` | LOCAL | Permitted retry, refresh, correction, resumption, or terminal stop after failure | rejection, concurrency, delivery | visible copy/layout | required recovery path absent | invented retry/correction capability |
| `FR-A22` | `visible_success` | COMPOSITIONAL | Externally observable success only after authoritative readback/commit | expected mutation, result expectations, delivery | domain mutation prose | required visible success/readback absent | reports success before commit or exposes unsupported data |
| `FR-A23` | `visible_error` | COMPOSITIONAL | Externally observable error category, authorized disclosure, preserved input, latest-state comparison, and recovery affordance | rejection, recovery, input invariants, relationship, concurrency | every triggering guard or precondition | required presentation/preservation/affordance absent | invented recovery, unauthorized disclosure, or unconditional latest-state exposure |
| `FR-A24` | `superseded_rules` | REFERENCE_ONLY | Inactive superseded authority sentinels relevant to this action | provenance inventory | current semantics or old prose | applicable sentinel reference absent | superseded rule treated as active/current |
| `FR-A25` | `test_obligations` | REFERENCE_ONLY | Stable references proving coverage of owned obligations/result classes | all obligation IDs and result classes | copied canonical or sibling-field prose | a material obligation lacks a stable test reference | invented test semantics or contradictory copied prose |
| `FR-A26` | `trace` | REFERENCE_ONLY | Stable precondition→public action→handler→command→state/effects→visible result chain references | all material fields | business semantics already owned by fields | required trace link absent | trace claims a link not present in candidate/public surface |

## Lifecycle semantic fields

| Rule | Field | Mode | Owns | May reference | Must not duplicate | Omission | Unsupported overreach |
|---|---|---|---|---|---|---|---|
| `FR-L01` | `current_states` | LOCAL | Complete current lifecycle state vocabulary | none | transition rules | required state absent | invented state |
| `FR-L02` | `allowed_transitions` | LOCAL | Authorized directed transitions and actor/scope if transition-local | states, authority | forbidden or reversal prose | allowed transition absent/wrong | invented transition |
| `FR-L03` | `forbidden_transitions` | LOCAL | Explicitly disallowed transitions | states, boundary | rejection/UX | forbidden transition absent | valid transition prohibited |
| `FR-L04` | `boundary_conditions` | LOCAL | Commit/terminal/irreversible boundary predicates | transitions, evidence | full reversal behavior | material boundary absent | invented boundary |
| `FR-L05` | `reversibility` | COMPOSITIONAL | Whether and how state may be reversed around the boundary | boundary, reversal window, history | complete transitions/history prose | required reversible/irreversible behavior absent | unsupported reversal |
| `FR-L06` | `reversal_window` | LOCAL | Exact temporal/state window for reversal | boundary, states | reversal operation details | window absent/wrong | unsupported extension/contraction |
| `FR-L07` | `object_outcome` | LOCAL | Resulting object state/disposition after transition | transitions | side effects/visible result | required outcome absent | invented outcome |
| `FR-L08` | `required_reason` | LOCAL | Reason requirement for lifecycle transition/reversal | transition, input invariant | other evidence/confirmation | required reason absent | reason required without authority |
| `FR-L09` | `required_confirmation` | LOCAL | Confirmation requirement at lifecycle boundary | boundary, transition | reason/evidence | required confirmation absent | confirmation invented |
| `FR-L10` | `required_evidence` | LOCAL | Evidence required for transition/reversal | transition, boundary | general provenance | required evidence absent | unsupported evidence requirement |
| `FR-L11` | `authority` | LOCAL | Actor/relationship allowed to perform transition | action actor/relationship | state or evidence rules | required authority absent | unauthorized actor allowed/valid actor denied |
| `FR-L12` | `history_preservation` | COMPOSITIONAL | Immutable history and audit requirements across transitions/reversal | boundary, reversibility, reason/evidence | transition semantics | preservation/audit link absent | history rewrite or invented audit behavior |
| `FR-L13` | `superseded_sentinels` | REFERENCE_ONLY | Inactive superseded lifecycle authority sentinels relevant to this lifecycle | provenance inventory | current lifecycle semantics or old prose | applicable sentinel reference absent | superseded rule treated as active/current |

## Canonical obligation taxonomy and owner selection

| Obligation type | Unique owning rule | Required secondary projection |
|---|---|---|
| actor eligibility | `FR-A01` | test ref in `FR-A25` |
| authentication prerequisite | `FR-A02` | rejection + test ref when failure is material |
| relationship authority | `FR-A03` | rejection; visible disclosure gate when applicable |
| object/scope binding | `FR-A04` | rejection + test ref |
| concurrency/version conflict | `FR-A05` | `FR-A15`, rejection, recovery, visible error, test ref |
| non-input domain precondition | `FR-A06` | state/rejection/test projections as applicable |
| allowed state | `FR-A07` | rejection/test projection |
| forbidden state | `FR-A08` | rejection/test projection |
| input validity | `FR-A09` | rejection, visible error, test ref |
| command shape | `FR-A10` | input/test refs |
| authoritative mutation | `FR-A11` | result expectation, visible success, test ref |
| protected no-op | `FR-A12` | result expectation/rejection/test ref |
| result class | `FR-A13` | result expectation/test ref |
| component result behavior | `FR-A14` | component owner/test ref |
| version effect | `FR-A15` | result expectation/test ref |
| history effect | `FR-A16` | result expectation/test ref |
| business side effect | `FR-A17` | result expectation/test ref |
| delivery effect | `FR-A18` | result expectation/test ref |
| idempotency/replay | `FR-A19` | concurrency/effect/result/test projections |
| rejection semantics | `FR-A20` | visible error/recovery/test projections |
| recovery semantics | `FR-A21` | visible error/test projection |
| visible success | `FR-A22` | test ref |
| visible error | `FR-A23` | test ref |
| superseded sentinel | `FR-A24` | provenance/package validation |
| verification coverage | `FR-A25` | stable obligation reference only |
| end-to-end trace | `FR-A26` | stable chain references only |
| lifecycle state vocabulary | `FR-L01` | action/test projection only when an action crosses it |
| allowed lifecycle transition | `FR-L02` | action/test projection only when an action crosses it |
| forbidden lifecycle transition | `FR-L03` | action/test projection only when an action crosses it |
| lifecycle boundary | `FR-L04` | action/test projection only when an action crosses it |
| lifecycle reversibility | `FR-L05` | boundary/window/history sibling refs + test ref |
| lifecycle reversal window | `FR-L06` | reversal/test projection |
| lifecycle object outcome | `FR-L07` | action/result/test projection only when crossed |
| lifecycle reason requirement | `FR-L08` | input/rejection/test projection when action-supplied |
| lifecycle confirmation requirement | `FR-L09` | input/rejection/test projection when action-supplied |
| lifecycle evidence requirement | `FR-L10` | input/rejection/test projection when action-supplied |
| lifecycle transition authority | `FR-L11` | action actor/relationship/rejection/test projection |
| lifecycle history preservation | `FR-L12` | boundary/reversal/test sibling refs |
| lifecycle superseded sentinel | `FR-L13` | provenance/package validation |

## Deterministic completeness decision

For review identity `I`:

1. Load its single responsibility rule `R`; missing or multiple rules is `RUBRIC_ERROR/RESPONSIBILITY_UNDEFINED`.
2. Select obligation-index entries whose `owner_kind`, `owner_id`, and `owning_field` equal `I`.
3. Verify every selected obligation is represented by the candidate value and exact evidence. A missing owned projection is `REJECTED_CANDIDATE/MISSING_OWNED_SEMANTIC`.
4. Verify declared sibling references exist and use allowed rules. A missing required reference is `REJECTED_CANDIDATE/MISSING_REQUIRED_REFERENCE`.
5. Ignore absent sibling-owned prose when the sibling obligation and allowed reference exist. Requiring such duplication is a rubric violation, not candidate rejection.
6. Reject candidate text/value that contradicts an owner or adds unsupported semantics as `CONTRADICTS_OWNER` or `UNSUPPORTED_OVERREACH`.
7. For `REFERENCE_ONLY`, compare stable identities and hashes; semantic prose duplication is not a completeness requirement.

## Disputed-family resolution

### `input_invariants`

`FR-A09` owns only command-input predicates. Authority relationships, lifecycle state, visible errors, recovery behavior, mutations, and tests are sibling-owned. An input predicate that is required by canonical authority must be present; an unrelated sibling constraint need not be copied.

### `visible_error`

`FR-A23` owns observable failure/recovery presentation and authorized disclosure. It references the triggering rejection/invariant and recovery rule. It does not copy every guard. Display of latest state is approved only when the referenced relationship/authorization rule permits that disclosure.

### `test_obligations`

`FR-A25` owns stable verification references. Each material obligation must be covered, but full semantic prose belongs only to its owner. Contradictory copied prose is candidate overreach; a stable reference to the correct obligation is sufficient.
