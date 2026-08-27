# v0.4.3 Schema and Compatibility Decision

## Decision

Select option A:

`joewrks.semantic-review/1.0` is a mandatory hash-bound sidecar over `joewrks.action-conformance/1.0`.

Retain `joewrks.action-conformance/1.0` for the v0.4.3 specification and planned reliability implementation. Do not introduce `joewrks.action-conformance/1.1` in this workstream.

## Why the sidecar is sufficient

The v0.4.2 failure did not establish a runtime result-class, compiler derivation, source-resolution, or action-contract structural defect. It established that independent reviewers lacked a shared normative answer for field ownership and composition.

The missing information can be bound orthogonally and deterministically through:

- a versioned field-responsibility profile;
- a contract-hash-bound semantic obligation index;
- a byte-identical reviewer brief;
- a package manifest and exact identity inventory;
- an output schema with distinct candidate/rubric/package verdicts;
- a repeated-review reliability gate.

These artifacts define how an existing semantic field is reviewed. They do not change what `action-conformance/1.0` means to the compiler or runtime verifier. The sidecar can name stable review identities and value hashes without adding properties to the action contract.

## Why brief-only compatibility is insufficient

A canonical brief without a machine-readable responsibility profile and obligation index would still require each reviewer to infer:

- canonical clause splitting;
- obligation type;
- owning field;
- allowed sibling references;
- required test projections.

That reproduces the v0.4.2 ambiguity in more polished prose and is therefore rejected.

## Why an action-contract bump is not justified now

An immediate `action-conformance/1.1` could embed obligation IDs and sibling references, but it would also:

- change every full-contract hash and generator;
- require schema/compiler/product-adapter migration;
- mix review reliability with runtime contract evolution;
- broaden v0.4.3 beyond the diagnosed failure;
- prevent proving whether the orthogonal review contract alone resolves the ambiguity.

Avoiding migration is not the reason to retain v1.0. The reason is architectural separation: review responsibility and repeatability can be completely expressed and hash-bound outside the runtime contract without weakening either layer.

## Compatibility matrix

| Action contract | Semantic-review sidecar | Compiler/runtime status | v0.4.3 review-gate status |
|---|---|---|---|
| `action-conformance/1.0` | valid `semantic-review/1.0` | unchanged and supported | eligible |
| `action-conformance/1.0` | absent | unchanged and supported | ineligible; `INPUT_PACKAGE_ERROR` at review gate |
| `action-conformance/1.0` | hash/version mismatch | unchanged until review | ineligible; package failure |
| `downstream.regression-slice/1.0` | any | remains evaluator-only | never production-gate eligible; negative/calibration fixture only |
| future `action-conformance/1.1` | unspecified | unsupported by this specification | requires a new compatibility decision and review profile version |
| legacy review output with `APPROVED/REJECTED` only | absent/incomplete | no runtime impact | incompatible; cannot be translated losslessly |

## Sidecar compatibility rules

- The sidecar SHALL declare exactly one action-contract schema version and contract hash.
- One sidecar SHALL NOT review multiple contract hashes.
- Responsibility profile changes require a new profile version/hash and full recalibration.
- Reviewer brief changes require a new brief version/hash and full recalibration.
- Output records from different sidecar/brief/profile hashes SHALL NOT be merged.
- Existing action contracts remain valid runtime inputs, but prior binary reviews are not retroactively upgraded.

## Future action-contract version-bump triggers

A future action-contract schema version is required only if one or more of these become runtime/production-contract requirements rather than review-sidecar requirements:

1. runtime verifier directly consumes semantic obligation IDs or sibling references;
2. action-contract validity itself requires responsibility-rule properties;
3. `test_obligations` changes from string identifiers to structured executable references in the production contract;
4. contract compilation must fail before review when obligation ownership is missing;
5. a field value cannot be unambiguously addressed by owner identity, semantic field, value hash, and value pointer;
6. the sidecar cannot remain atomic with the contract through package/hash validation.

If a trigger occurs, the new action schema and its semantic-review compatibility profile SHALL be specified and calibrated as a separate versioned change. v0.4.3 does not pre-authorize that migration.

## Scope boundary

This decision does not claim that every current action contract is semantically correct. It states only that correctness can be reviewed deterministically without changing action-contract v1.0 representation.
