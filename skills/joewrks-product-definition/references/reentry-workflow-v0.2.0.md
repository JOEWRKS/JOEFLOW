# Product Definition re-entry workflow — State 0.2.0

This installed workflow consumes `joewrks.product-definition-reentry/1.0`
artifacts without turning them into Product Definition authority.

Normative boundaries:

```text
AFFECTED_ONLY
CANDIDATE_UNKNOWN_IS_NOT_CANONICAL_AUTHORITY
REENTER_PRODUCT_DEFINITION_ONLY_FOR_A_REAL_AUTHORITY_GAP
NO_AUTOMATIC_PRODUCT_DECISION
NO_AUTOMATIC_STATE_MUTATION
```

The canonical authority remains
`product-definition/<project-slug>/state.json`. A re-entry artifact is a
read-only proposal or evidence about downstream work. It does not allocate a
canonical `UNK-*`, increment a revision, change approval, rewrite a contract,
or decide a replacement value.

No general-purpose state mutator is part of this workflow. Product Definition
changes continue through the ordinary evidence, unknown, decision,
Materiality, binding, manifest, and explicit-approval contracts.

## Inspect before routing

Read the complete event before changing anything.

The event payload fields are exactly:

```text
schema_version
event_id
event_type
source_definition_digest
source_contract_hash
affected_authority_ids
affected_action_ids
affected_lifecycle_ids
evidence_refs
halt_scope
candidate_unknown
recommended_action
```

Confirm the event type, `AFFECTED_ONLY` halt scope, affected authority, action,
and lifecycle IDs, and evidence references. The event does not contain a
consumed-seed inventory or scope-commitment inventory; source those facts from
the matching upstream artifact described below.

### Non-null source contract

When `source_contract_hash` is non-null, resolve the exact
`joewrks.action-conformance/2.0` contract for which
`semantic_contract_hash == source_contract_hash`. Inspect the
`source_seed_inventory` and `scope_commitments` from that contract, then inspect
the exact current Product Definition authority and evidence for only those
affected dependencies. A different contract is not evidence about this event.

### Null source contract

When `source_contract_hash` is `null`, treat it as a pre-contract event: no
materialized action contract exists to supply inventories. Inspect the exact
handoff definition that produced the event together with the current Product
Definition state authority and evidence named by the event's affected IDs and
`evidence_refs`.

Do not infer a global Product Definition problem from a runtime failure or
from the existence of a re-entry artifact. Choose exactly one of the following
routes from the observed authority state.

## Route A — clear authority, incorrect implementation

Use this route when the action contract and its local dependencies are still
exact, Product Definition already gives one clear meaning, and runtime behavior
does not implement that meaning.

The required outcome is an implementation correction. The mismatch may be
registered as `OBSERVED_IMPLEMENTATION`, `OBSERVED_RUNTIME`, or test evidence
when useful, but it does not require a Product Definition revision or approval
change. Do not create a new Product Definition decision or a canonical unknown
merely to explain a code bug. Correct the implementation, then rerun the
affected verification against the unchanged approved authority.

## Route B — downstream semantic authority gap or real ambiguity

Use this route when the affected behavior lacks one authoritative meaning,
when exact consumed authority conflicts, or when evidence inspection confirms
a real unresolved product question.

Follow this order without writing canonical state during preparation:

1. inspect and resolve the exact affected authority and evidence where the
   existing sources are sufficient;
2. register the event as evidence if useful, using only the claim class it can
   support;
3. when a real unresolved product question remains, truthfully assess
   Materiality and decision authority under the ordinary V2 rules;
4. independently author and prepare a complete V2 unknown record off-state.
   Populate every field required by `schemas/state-v0.2.0.schema.json`, bind its
   truthful evidence and affected IDs, and validate the complete working record.
   The off-state record is not authority;
5. as one canonical mutation:
   - increment `definition_revision`;
   - move the definition to the truthful non-`CLOSED` lifecycle state and set
     approval to `UNAPPROVED`;
   - stale only affected authority and downstream dependencies; and
   - register the complete `UNK-*` under the new revision;
6. validate the complete resulting state, then re-run the affected DISCOVER,
   Grill, binding, and approval flow;
7. after exact user approval and Semantic Closure, recompile and verify the
   affected downstream contract.

Never write incomplete authority, register the unknown under the old revision,
or expose a half-applied revision/approval/staleness transition.

If inspection shows that authority was already clear and only the
implementation was wrong, stop this route and use Route A. A downstream label
does not override the current evidence.

## Candidate proposal boundary

The artifact's `candidate_unknown` is suggestion text only and has no canonical
ID. Its wording must never be copied directly or verbatim into canonical
authority, a decision, a canonical unknown, or a user question, including after
review or evidence registration. Any later unknown or question is independently
authored from the inspected evidence and ordinary V2 semantics. The downstream
proposal can identify where inspection is needed; it cannot supply Product
Definition wording or authority.

## Route C — `OUT_OF_SCOPE_REQUEST`

An `OUT_OF_SCOPE_REQUEST` does not become in scope merely because an
implementation agent requested it. Resolve Product Definition scope first.
There is no provisional, temporary, or automatic expansion of approved scope.

Inspect the exact current scope authority and its evidence or decision basis.
If scope is already clearly out of scope, do not implement the request as
approved behavior. If a real material scope question remains, use Route B to
register that question and obtain the required authority. Implementation may
resume only after the scope decision is canonical, approved, and reflected in
a current downstream contract.

## Affected-only continuation

Block only the action and lifecycle scope named by the event. Unrelated work
may continue when its exact source seeds and scope commitments remain current.
Final acceptance must use the current approved Product Definition revision and
current contract after any real semantic change.

This Task 4 workflow documents routing only. It does not exercise a re-entry
mutation, fabricate dogfood, record approval, generate a timestamp, or perform
Task 5 work.
