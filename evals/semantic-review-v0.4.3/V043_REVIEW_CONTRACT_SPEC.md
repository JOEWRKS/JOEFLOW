# v0.4.3 Deterministic Semantic Review Contract Specification

Status: `PM-APPROVED DIRECTION / SPECIFICATION ONLY`

Proposed review schema identity: `joewrks.semantic-review/1.0`

Reviewed contract identity retained in this phase: `joewrks.action-conformance/1.0`

## 1. Authority and frozen boundaries

This specification is based on:

- implementation baseline and current `main`: `efd96410f6401cbf9624328e94b795c315164b7f`;
- frozen v0.4.2 disposition evidence: `eval/v0.4.2-rma-disposition@9e734326a5b13f446a19ff9547d142b213fcf045`;
- v0.4.2 official result: `STOPPED — TREATMENT_INTERVENTION_CONSTRUCTION_FAILED`, paired efficacy result `NOT RUN`;
- PM-approved v0.4.3 architecture: mandatory hash-bound semantic-review sidecar over `joewrks.action-conformance/1.0`.

The v0.4.2 RMA evidence is diagnostic input, not generic product authority. No RMA-specific action, role, field value, or Product Definition clause becomes a generic rule through this specification.

This phase does not change Product Definition, generic downstream production code, compiler behavior, runtime verification, Figma, v0.4.2, or `main`. It does not execute calibration or a new efficacy experiment.

## 2. Normative language

`MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, and `SHALL NOT` are normative. `MAY` is optional. A review package or output that violates a normative rule is not a completed semantic review.

## 3. Current behavior versus proposed behavior

### 3.1 Current behavior at the frozen baseline

`joewrks.action-conformance/1.0` requires 26 action semantic fields and 12 lifecycle semantic fields. Each semantic field contains `value`, non-empty `source_refs`, and either a `MACHINE_DERIVED` or `REVIEW_REQUIRED` derivation. Lifecycle `superseded_sentinels` is instead a raw array of source records and is not a semantic field. The compiler validates structure, exact source identity, current/superseded status, source hashes, and machine derivations. For `REVIEW_REQUIRED`, it requires only a non-empty explanation; it does not prove the emitted meaning.

The current schema and compiler do not define:

- which canonical obligation is owned by which semantic field;
- whether a field is locally complete or composes with sibling fields;
- how a sibling reference is represented during semantic review;
- whether a field must duplicate canonical prose already represented elsewhere;
- stable test-obligation references;
- a canonical reviewer brief or reviewer input manifest;
- distinct verdicts for candidate defects, rubric defects, and package defects;
- a repeatability gate for independent semantic review.

Current runtime verification consumes compiled `input_invariants`, `default_result`, and `result_expectations`, but this does not define the semantic-review completeness boundary for all 26 fields. Existing tests verify structural/provenance/runtime properties, not independent reviewer reliability.

### 3.2 Proposed v0.4.3 behavior

Every accepted review SHALL bind one exact action contract to one exact semantic-review package through SHA-256 hashes. The package SHALL include a canonical reviewer brief, responsibility profile, canonical authority, contract, provenance inventory, semantic obligation index, output schema, and expected review identity inventory.

The sidecar SHALL define field ownership without changing `joewrks.action-conformance/1.0`. A reviewer SHALL evaluate each `REVIEW_REQUIRED` identity against the same responsibility rule and the same canonical obligation index. Missing rubric responsibility SHALL produce `RUBRIC_ERROR`; invalid package identity or provenance SHALL produce `INPUT_PACKAGE_ERROR`; neither may be reported as a candidate defect.

## 4. Sidecar architecture

The semantic-review sidecar consists of five immutable layers:

1. **Input manifest** — paths, byte hashes, logical roles, schema identities, expected review identities, and exclusion declarations; its verified file inventory is the input to the separately computed package hash.
2. **Responsibility profile** — versioned rules assigning all 26 action and 12 lifecycle semantic fields one responsibility rule and completeness mode. Its `rubric_calibration_revision` and file hash are the normative rubric version/hash for rerun control. Raw lifecycle `superseded_sentinels` is excluded and governed by package/provenance rule `PR-P01`.
3. **Semantic obligation index** — a contract-hash-bound mapping from canonical clause projection to obligation type, owning field, allowed sibling references, and required test reference.
4. **Canonical reviewer brief** — one versioned UTF-8/LF artifact whose exact bytes are included in the input manifest.
5. **Review output** — for a valid completed review, one schema-valid record for every expected `REVIEW_REQUIRED` identity plus deterministic summary counts; for a terminal preflight failure, explicit diagnostics under the rules in §10.

The sidecar is mandatory for a v0.4.3 semantic-review gate. An otherwise valid action contract without this sidecar remains compilable under v1.0, but it is not eligible to pass the v0.4.3 review reliability gate.

Each invocation SHALL also have a controller-created, non-normative run envelope containing `review_run_id`, `reviewer_context_id`, `reviewer_input_package_hash`, `reviewer_brief_hash`, and an isolation attestation. The attestation SHALL state that the context is newly created, no prior verdict is accessible, and only manifest-declared evidence is reviewable; its canonical JSON bytes SHALL be SHA-256 hashed. Run envelopes are deliberately outside the identical reviewer input package because their IDs differ per invocation, and they MUST NOT contain review instructions or product meaning. Review output copies the run/context IDs and attestation hash so the gate can reject context reuse or missing isolation evidence.

## 5. Canonical serialization and hashing

### 5.1 File hashes

Every input artifact SHALL be read as bytes and hashed with SHA-256. Text inputs SHALL be UTF-8 without a byte-order mark and SHALL use LF line endings. Hashing occurs before parsing. A byte mismatch is an input-package failure even when parsed values are equivalent.

### 5.2 Manifest hash

The manifest object SHALL contain `reviewer_input_manifest_hash` but SHALL NOT contain `reviewer_input_package_hash`. To compute the manifest hash, remove only `reviewer_input_manifest_hash`, serialize the remaining object as canonical JSON using UTF-8, sorted object keys, no insignificant whitespace, no non-finite numbers, and no Unicode normalization, then SHA-256 hash it. The resulting lowercase 64-hex digest is `reviewer_input_manifest_hash`. Excluding the package hash from the manifest prevents a circular hash dependency.

### 5.3 Package hash

The package hash SHALL be SHA-256 over canonical JSON containing:

```json
{
  "manifest_hash": "<reviewer_input_manifest_hash>",
  "ordered_files": [
    {"logical_role": "<role>", "path": "<relative-path>", "sha256": "<file-hash>", "bytes": 0}
  ]
}
```

`ordered_files` SHALL be sorted by `(logical_role, path)` using Unicode code-point order. Paths SHALL be relative POSIX-style paths, contain no `..`, and resolve within the package root.

The resulting `reviewer_input_package_hash` SHALL be carried in the immutable review-run envelope and review output, not inserted back into the manifest. Reviewers recompute it from the verified manifest hash and ordered file inventory before semantic review.

## 6. Required reviewer input package

The manifest SHALL contain exactly one value for each of the following logical roles:

- `canonical_authority` — approved canonical `state.json` and its declared revision/digest;
- `action_contract` — complete `joewrks.action-conformance/1.0` bytes and recomputed contract hash;
- `provenance_inventory` — exact current source identities, pointers, value hashes, status, and active flag;
- `responsibility_profile` — the frozen rules specified by `FIELD_RESPONSIBILITY_MATRIX.md`;
- `semantic_obligation_index` — every obligation in review scope and its unique owning rule;
- `reviewer_brief` — canonical brief bytes specified by `REVIEWER_BRIEF_SPEC.md`;
- `review_output_schema` — the implemented descendant of `REVIEW_OUTPUT_SCHEMA_PROPOSAL.json`;
- `review_identity_inventory` — sorted expected `REVIEW_REQUIRED` identities and immutable hashes;
- `exclusion_manifest` — forbidden prior verdicts, hidden answers, implementation outcomes, and unrelated product evidence;
- `golden_suite_manifest` when running calibration.

Supporting projections MAY be included only when the manifest names their supporting, non-canonical role and binds their hashes. They cannot override canonical state.

The package SHALL declare `previous_reviewer_verdicts_present: false`. Any prior verdict, rationale, confusion matrix, or candidate correction hint inside the review boundary is `INPUT_PACKAGE_ERROR`.

Package/provenance preflight SHALL validate the raw lifecycle `superseded_sentinels` array under `PR-P01`. It MUST NOT add `lifecycle:<id>:superseded_sentinels` to the review identity inventory or semantic obligation index. An active sentinel source with `source_status: SUPERSEDED` terminates as `INPUT_PACKAGE_ERROR/ACTIVE_SUPERSEDED_SOURCE`, as exercised by `G-012`.

## 7. Semantic obligation index

Each obligation record SHALL include:

- `obligation_id`: stable within the contract hash;
- `canonical_refs`: sorted exact object ID, JSON Pointer, value hash, source status, and active flag;
- `obligation_type`: one value from the responsibility profile taxonomy;
- `owner_kind`, `owner_id`, and `owning_field`;
- `responsibility_rule_id` and `completeness_mode`;
- `semantic_value_pointer` and `semantic_value_hash`;
- `allowed_sibling_refs`: sorted review identities or empty array;
- `required_test_refs`: sorted stable test-obligation references or empty array;
- `projection_notes`: non-normative explanation only.

One canonical clause MAY project to multiple obligation records only when each projection uses a different obligation type and unique owning field. The same obligation type and scope MUST NOT have multiple owning fields. Duplicate prose is not a substitute for a projection record.

## 8. Deterministic ownership algorithm

For every applicable canonical clause, package construction and review SHALL apply this order:

1. Resolve and hash the exact current canonical clause. Active `SUPERSEDED` authority stops as `INPUT_PACKAGE_ERROR`.
2. Split the clause only at independently testable normative obligations; do not split stylistically.
3. Classify each obligation using the closed taxonomy in `FIELD_RESPONSIBILITY_MATRIX.md`.
4. Select the single owning field whose responsibility rule owns that obligation type.
5. Project only the field-specific observable or executable consequence into that owner.
6. Record allowed sibling references for dependent context; sibling references never transfer ownership.
7. Bind each material obligation to at least one stable test-obligation reference unless its responsibility rule explicitly marks it non-executable.
8. Reject an unclassifiable obligation as `RUBRIC_ERROR`; do not guess and do not reject the candidate.

The reviewer evaluates the owning field for owned semantics, verifies declared sibling references, and MUST NOT demand uncontrolled duplication across fields.

## 9. Completeness modes

- `LOCAL`: the field SHALL completely express the projection it owns. It MAY reference sibling context but is not incomplete merely because sibling-owned semantics are absent.
- `COMPOSITIONAL`: the field owns a distinct projection whose correctness depends on named sibling obligations. It SHALL name those references and be evaluated together with them. It MUST NOT copy their full normative prose.
- `REFERENCE_ONLY`: the field owns an index or link relation rather than duplicated business semantics. It SHALL use stable references and SHALL be rejected if it silently introduces new semantics.

The complete action and lifecycle assignments are normative in `FIELD_RESPONSIBILITY_MATRIX.md`.

## 10. Review identity and record algorithm

The expected identity is:

```text
<owner_kind>:<owner_id>:<semantic_field>
```

`semantic_field` SHALL resolve to one of the 26 action or 12 lifecycle properties whose schema is `$ref: #/$defs/semanticField`. Raw source arrays such as lifecycle `superseded_sentinels` are structurally ineligible and MUST NOT produce a review identity.

For each expected `REVIEW_REQUIRED` identity, a completed review SHALL:

1. verify the run envelope, isolation attestation, package, brief, contract, responsibility profile, and identity-inventory hashes;
2. verify `owner_kind`, `owner_id`, `semantic_field`, semantic value hash, provenance set, responsibility rule, and completeness mode;
3. resolve canonical evidence and obligation-index entries;
4. evaluate owned semantics under the assigned completeness mode;
5. verify required and forbidden sibling references;
6. verify omission and overreach conditions;
7. emit exactly one verdict and one rationale code;
8. attach sorted canonical evidence references and a non-empty explanation.

No record may be absent, duplicated, pending, or deferred. Reviewer explanations may vary in wording, but verdict, rationale code, hashes, responsibility rule, completeness mode, and evidence identities are machine-comparable.

`preflight_errors` separates failures discovered before identity-level semantic review. A valid completed semantic review SHALL have an empty `preflight_errors` array, the exact expected record set, and `summary.complete: true`. A finalized preflight-failure output SHALL contain one or more `RUBRIC_ERROR` or `INPUT_PACKAGE_ERROR` diagnostics, omit records only for the explicitly affected scope, set `summary.complete: false`, and retain `pending_count: 0` because the work is failed rather than pending. Such an output is an auditable terminal failure, not a completed semantic review and not eligible for a full-review reliability PASS.

The JSON Schema proposal deliberately uses only keywords supported by the frozen repository schema validator. Cross-record rules that JSON Schema cannot express in that subset—record-identity uniqueness, array-item uniqueness, exact expected-set equality, sorted ordering, verdict/rationale compatibility, and summary arithmetic—SHALL be enforced by the semantic output validator before an output is considered complete.

`summary.verdict_counts` SHALL count all terminal outcomes in `records` plus `preflight_errors`. With no preflight error, the verdict-count sum SHALL equal `record_count`, and `record_count`, `unique_identity_count`, and `expected_identity_count` SHALL be equal. With preflight errors, the verdict-count sum SHALL equal `record_count + len(preflight_errors)`, `complete` SHALL be false, and the result is structurally ineligible for a full-review PASS.

## 11. Verdict semantics

- `APPROVED`: the exact candidate field satisfies its responsibility rule, owns all required local projections, uses only permitted sibling references, contains no unsupported semantics, and has valid evidence.
- `REJECTED_CANDIDATE`: a valid package and determinate rubric establish a candidate omission, contradiction, unsupported overreach, invalid duplication, or incorrect semantic projection.
- `RUBRIC_ERROR`: the package is valid but the frozen responsibility profile or brief cannot determine ownership, completeness, or the correct verdict. This verdict invalidates calibration; it is never converted into candidate rejection.
- `INPUT_PACKAGE_ERROR`: bytes, hashes, identities, provenance, source status, exclusions, or required package contents are invalid or inconsistent. Semantic candidate review SHALL stop for the affected scope.

Majority vote SHALL NOT convert `RUBRIC_ERROR` or `INPUT_PACKAGE_ERROR` into another verdict.

### 11.1 Deterministic rationale-code mapping

| Verdict | Rationale code | Exact use |
|---|---|---|
| `APPROVED` | `SUPPORTED_EXACTLY` | all owned projections, references, and evidence satisfy the frozen rule |
| `REJECTED_CANDIDATE` | `MISSING_OWNED_SEMANTIC` | an owned projection is absent, including a missing stable coverage reference owned by `FR-A25` |
| `REJECTED_CANDIDATE` | `MISSING_REQUIRED_REFERENCE` | a present compositional projection omits a required declared sibling reference |
| `REJECTED_CANDIDATE` | `UNSUPPORTED_OVERREACH` | candidate adds meaning with no canonical support |
| `REJECTED_CANDIDATE` | `CONTRADICTS_OWNER` | candidate meaning conflicts with canonical authority or the owning field |
| `REJECTED_CANDIDATE` | `INVALID_DUPLICATION` | a field duplicates semantics its rule explicitly forbids it to carry, without needing a contradiction |
| `RUBRIC_ERROR` | `RESPONSIBILITY_UNDEFINED` | valid inputs expose an obligation type for which the frozen taxonomy has no unique owner |
| `RUBRIC_ERROR` | `COMPLETENESS_UNDEFINED` | ownership is known but the frozen rule cannot decide local/compositional/reference completeness |
| `INPUT_PACKAGE_ERROR` | `INVALID_PROVENANCE` | source identity, pointer, value hash, or provenance set is missing or invalid |
| `INPUT_PACKAGE_ERROR` | `ACTIVE_SUPERSEDED_SOURCE` | an active semantic source resolves to superseded authority |
| `INPUT_PACKAGE_ERROR` | `PACKAGE_HASH_MISMATCH` | package or declared file bytes do not match |
| `INPUT_PACKAGE_ERROR` | `BRIEF_HASH_MISMATCH` | canonical brief bytes/version do not match |
| `INPUT_PACKAGE_ERROR` | `CONTRACT_HASH_MISMATCH` | action contract bytes/recomputed identity do not match |
| `INPUT_PACKAGE_ERROR` | `RESPONSIBILITY_PROFILE_HASH_MISMATCH` | profile bytes or embedded brief-table projection do not match |
| `INPUT_PACKAGE_ERROR` | `OBLIGATION_INDEX_HASH_MISMATCH` | obligation-index bytes or contract binding do not match |
| `INPUT_PACKAGE_ERROR` | `IDENTITY_SET_MISMATCH` | expected review identity inventory is invalid or inconsistent |
| `INPUT_PACKAGE_ERROR` | `PREVIOUS_VERDICT_EXPOSURE` | forbidden prior-review material is present |
| `INPUT_PACKAGE_ERROR` | `OUTPUT_SCHEMA_VIOLATION` | the supplied output-schema artifact is invalid or not the frozen schema |

The output validator SHALL reject a verdict/rationale combination not listed in this table. It SHALL also reject duplicate entries in provenance, sibling-reference, obligation-ID, or evidence arrays and any array that violates the frozen sort order.

## 12. Evidence and citation requirements

Every record SHALL cite:

- contract hash and exact semantic value hash;
- provenance-set hash and each exact canonical reference used;
- responsibility rule ID and completeness mode;
- all sibling review identities relied upon;
- applicable obligation IDs and stable test references;
- one schema-defined rationale code;
- a concise explanation that states the observed candidate value and decisive rule.

Correct provenance is necessary but not sufficient. An interpretation unsupported by the cited canonical value is `REJECTED_CANDIDATE`. Missing or invalid provenance is `INPUT_PACKAGE_ERROR`.

## 13. Calibration and reliability gate

The frozen gate is defined by `RELIABILITY_GATE_SPEC.md`. It requires at least three fresh isolated full reviews of byte-identical packages and briefs; 100% identity coverage; zero pending records; 100% golden verdict and rationale-code accuracy; no unexpected error verdicts; at least 99% three-review unanimity for unchanged identities; zero unresolved normative responsibility/completeness disagreement; zero repeated disagreement under one responsibility rule; and the PM-approved balanced/imbalanced reliability statistics.

There is no majority-vote escape hatch. Every failed calibration requires incrementing the responsibility profile's `rubric_calibration_revision`, producing a new normative rubric/profile hash, and running the complete calibration again. If brief wording changes, its version/hash SHALL also change. Results from incompatible hashes SHALL NOT be pooled.

## 14. Failure behavior

Failure evaluation order is deterministic:

1. package/hash/exclusion/provenance failure → `INPUT_PACKAGE_ERROR`;
2. missing normative ownership or completeness rule → `RUBRIC_ERROR`;
3. determinate candidate omission/overreach/contradiction → `REJECTED_CANDIDATE`;
4. otherwise → `APPROVED`.

If package validity cannot be established, downstream semantic verdicts are not emitted for that scope. If any calibration threshold fails, the gate verdict is `FAIL`; partial metrics, majority agreement, or manual waiver cannot produce `PASS`.

Expected-error golden cases are evaluated from their finalized `preflight_errors` outcome. They do not satisfy full-review structural acceptance and MUST NOT be reused as full-review packages. An unexpected preflight error in any valid full-review or non-error golden package fails the gate.

## 15. Compatibility decision

v0.4.3 retains `joewrks.action-conformance/1.0`. Responsibility, composition, obligation indexing, reviewer identity, and reliability are orthogonal review-layer concerns and can be bound safely through a mandatory sidecar without changing action-contract runtime meaning. The detailed decision and future version-bump triggers are normative in `COMPATIBILITY_DECISION.md`.

## 16. Acceptance criteria for this specification phase

This specification phase is acceptable only when:

- all ten requested specification artifacts exist and agree;
- all 26 action and all 12 lifecycle semantic fields have one responsibility rule, for 38 semantic responsibility rules total;
- lifecycle `superseded_sentinels` remains provenance-only under `PR-P01` and creates no review identity;
- exactly 15 golden cases and 8 negative-regression families are specified;
- the PM-approved reliability thresholds are copied exactly and operationally defined;
- the output schema proposal is valid JSON;
- an isolated auditor answers all six required ambiguity questions and returns `PASS`;
- no production downstream file differs from baseline;
- the specification branch history descends from `efd96410f6401cbf9624328e94b795c315164b7f`, and this repair commit is a normal, non-rewritten child of `7ffbc60e869f1681b48dd75e2085422d979ac14a`.

Implementation, calibration execution, reviewer runs, action-contract migration, and efficacy testing remain not started.
