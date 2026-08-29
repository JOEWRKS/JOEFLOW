# Runtime conformance for Product Definition state 0.2.0

This reference defines how installed V2 verification checks runtime evidence against an already materialized `joewrks.action-conformance/2.0` contract. It does not read Product Definition prose to invent implementation meaning, modify `state.json`, create approval, or start re-entry work.

## Frozen transport and V2 admission profile

Runtime evidence remains byte-compatible with the frozen transport:

```text
joewrks.downstream.execution/1.0
```

V2 adds an admission profile over a record that first satisfies that frozen protocol:

```text
record.product_slug
  = contract.source_authority.product_slug

record.contract_hash
  = contract.semantic_contract_hash

record.authority.approved_revision
  = contract.source_authority.approved_revision

record.authority.approved_digest
  = contract.source_authority.approved_definition_digest
```

`artifact_hash` is observation/provenance identity and is never accepted as the semantic contract identity. No `joewrks.downstream.execution/2.0` protocol is introduced.

Every action and lifecycle verifier result, including a contained failure result, carries an exact `source_contract` identity containing the contract schema version, semantic contract hash, product slug, approved revision, and approved definition digest. Each result also carries `runtime_evidence`, an exact bounded canonical deep copy of the admitted frozen execution record or lifecycle observation. Admission first recomputes the existing V2 semantic projection and requires the claimed semantic contract hash to match the actual contract contents. Report aggregation then checks exact type and value parity with the report's contract before duplicate handling or coverage accounting. In particular, a boolean is never accepted as an integer approved revision.

The aggregate report never treats claimed verifier summaries as authority. It re-runs the action or lifecycle verifier against each result's preserved `runtime_evidence` and the supplied full contract, then requires the entire supplied result to equal the freshly derived canonical result. This comparison binds result class, all five before/after snapshot outcomes, assertion observations and verdicts, lifecycle facts and failures, source identity, evidence hash, and conformance. A canonical contained-error result is derived the same way; its rejected input is preserved, but it never counts toward action or lifecycle coverage.

Action and lifecycle IDs resolve exactly one contract item. Missing, blank, malformed, or duplicate identifiers fail closed. Runtime-critical fields are read only from their materialized `field["value"]`. Prose is not parsed into executable behavior.

## Action evidence

The action verifier supports the existing result classes:

```text
SUCCESS
REJECTED
STALE
IDEMPOTENT_REPLAY
```

Failed structured `input_invariants` select `REJECTED`. Otherwise the verifier uses the structured `default_result`, unless `command.expected_result` explicitly names another result class that is present in the contract's structured `result_expectations`.

Every result expectation defines all five components as `CHANGED`, `UNCHANGED`, or `ANY`:

```text
authoritative_state
revision
history
business_side_effects
delivery_effects
```

Evidence assertions are limited to the frozen vocabulary:

```text
path_present
path_absent
path_equals
collection_item_field_equals
```

Each action's nonempty, unique `test_obligations.value` is the complete required test-ID inventory for a full-contract run. Missing or unexpected evidence keeps action coverage `INCOMPLETE`. Conflicting duplicate evidence fails conformance; byte-identical duplicates are deterministically deduplicated and counted.

## Lifecycle evidence

An individual lifecycle observation can be verified only when all existing lifecycle semantic fields form an executable structured profile. The profile must provide a unique, complete case inventory through structured allowed and forbidden transitions. Current states, case boundaries, reversibility, outcomes, reason/confirmation/evidence requirements, authority, and history preservation must also be structured.

If a complete case inventory cannot be derived without interpretation, lifecycle coverage is `INCOMPLETE` and global conformance is forbidden. A contract with zero lifecycle items records `lifecycle_applicability = NOT_APPLICABLE`; its lifecycle coverage gate is complete because the exact contract inventory is empty. M6 does not add lifecycle obligations to `joewrks.action-conformance/2.0`.

## Report gates

The deterministic report identity is:

```text
joewrks.runtime-conformance-report/1.0
```

The report keeps independent status dimensions for dependency audit, runtime results, review completion, and semantic-review reliability. It also records:

```text
verification_scope = FULL_CONTRACT | PARTIAL_PROBE
coverage_status = COMPLETE | INCOMPLETE
action_coverage_status = COMPLETE | INCOMPLETE
lifecycle_coverage_status = COMPLETE | INCOMPLETE
```

`IMPLEMENTATION_CONFORMANT` is allowed only when all of these are true:

- scope is explicitly `FULL_CONTRACT`;
- dependency audit is `CONFORMANT`;
- action and lifecycle coverage gates are both `COMPLETE`;
- every supplied runtime result is conformant;
- no blocking re-entry event exists;
- semantic review is not required or has a structurally valid recorded output;
- semantic-review/2.0 reliability is never claimed beyond `NOT_MEASURED`.

A `PARTIAL_PROBE` may report individual passing evidence but cannot produce the global conformance status. When review output is recorded, conformance means the implementation matches the recorded contract value; semantic-review/2.0 reliability remains `NOT_MEASURED`.

The published report schema defines the complete verified-result and contained-error-result shapes for both actions and lifecycles, including preserved runtime evidence and a type-exact Boolean `false` for contained errors. `validate_runtime_conformance_report(report, contract)` additionally re-runs both verifiers against that contract, requires canonical result equality, recomputes required inventories from the contract, rechecks inventory differences, coverage/runtime implications, review reliability, re-entry state, and every global conformance gate that JSON Schema alone cannot express. The installed command validates this complete report with the original contract before emitting it or selecting its global exit status.

## Installed command

Run from any working directory without setting `PYTHONPATH`:

```text
python <skill-root>/scripts/verify_runtime_v2.py CONTRACT_JSON CURRENT_STATE_JSON EXECUTION_JSONL
python <skill-root>/scripts/verify_runtime_v2.py CONTRACT_JSON CURRENT_STATE_JSON EXECUTION_JSONL REVIEW_PACKAGE_JSON REVIEW_OUTPUT_JSON
```

The command emits one canonical JSON document on stdout. Semantic non-conformance, re-entry, incomplete coverage, and not-ready outcomes use exit `1` with empty stderr. Only `IMPLEMENTATION_CONFORMANT` uses exit `0`. Usage, read, JSON, nesting-limit, and canonicalization errors use exit `2` without a traceback. Contract, state, and every JSONL record are bounded and canonicalizability-checked immediately after decoding, before audit, hashing, or verifier dispatch.
