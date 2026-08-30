# Semantic Review Contract 2.1

Status: normative assurance-only review boundary for action-conformance/2.1.

## Identities

```text
review package/output: joewrks.semantic-review/2.1
source action contract: joewrks.action-conformance/2.1
responsibility profile: joewrks.downstream-responsibility/2.0
reliability status: NOT_MEASURED
```

Semantic-review/2.1 is a sibling of frozen semantic-review/2.0. Package and output identities from 2.0 and 2.1 are mutually invalid. The 2.1 validator does not import or infer any 2.0 or v1 reliability/calibration identity.

## Review responsibility

Only semantic fields whose responsibility-profile entry explicitly permits `REVIEW_REQUIRED` become obligations. The initial 2.1 profile permits review only for action `visible_success` and `visible_error`; lifecycle fields and all other action fields remain outside this boundary.

The removed action-conformance/2.0 fields remain absent:

```text
default_result
result_expectations
test_obligations
```

The review package is accepted only when built from a structurally and semantically valid action-conformance/2.1 contract. Machine-only contracts produce no package.

## Exact bindings

Every package binds:

```text
source semantic_contract_hash
source approved_definition_digest
responsibility profile ID and digest
exact REVIEW_REQUIRED field path
exact proposed value and proposed-value SHA-256
ordered exact source seed references and complete seed snapshots
deterministic obligation and package hashes
```

Each seed snapshot retains its location, source record, pointer, value hash, current status, and exact value. Review cannot add Product Definition authority or read authority outside the consumed action contract.

## Output and completion

An output binds the exact package hash and covers every obligation exactly once. Its `reviewed_value_sha256` must equal the obligation's `proposed_value_sha256`; replacement values and extra result fields are invalid.

Permitted verdicts are:

```text
CONFIRMED_INTERPRETATION
REJECTED_INTERPRETATION
UPSTREAM_AUTHORITY_GAP
```

Completion is structural:

```text
NOT_REQUIRED
PENDING
REVIEW_OUTPUT_RECORDED
REENTRY_REQUIRED
```

A confirmed complete output records `REVIEW_OUTPUT_RECORDED`. A rejected interpretation or upstream authority gap records `REENTRY_REQUIRED` for semantic conflict routing. Review output never mutates the source contract or Product Definition state.

Completion never establishes reliability. Package and output reliability remain exactly `NOT_MEASURED`; `PASS`, `RELIABLE`, `CALIBRATED`, or any inherited v1/v2.0 calibration claim is invalid.

## Machine-readable schemas

```text
downstream_v21/schemas/semantic-review-input-v21.schema.json
downstream_v21/schemas/semantic-review-output-v21.schema.json
```

Runtime validation additionally enforces exact package hashes, obligation identities, responsibility-permitted field paths, aligned source-seed snapshots, sorted unique seed refs, full output coverage, and immutable reviewed-value hashes.
