# Semantic Review Calibration Corpus Audit

Baseline HEAD: `9d99706356df62566d387f00a870fa254eafbe0f`

Correction-pass count: 2

## Aggregate construction evidence

- The package has 114 unique review identities: 38 responsibility rules with exactly three candidates per rule, comprising 78 action identities and 36 lifecycle identities.
- Independent reconstruction found exactly two semantically supported candidates and one genuinely defective candidate for every rule, for aggregate counts of 76 supported and 38 defective candidates. All 38 defective candidates contain exactly one explicit owner-owned defect; none depends on an omission inferable from the remaining wording, and none is compound.
- Completeness modes are 90 `LOCAL`, 15 `COMPOSITIONAL`, and 9 `REFERENCE_ONLY`. All 15 compositional obligations have one required sibling reference; supported references resolve exactly, while each defective compositional candidate has only its single intended reference defect. All 114 canonical references, 114 provenance records, and 114 unique required test references resolve and bind exactly except for the single intended candidate defect in each affected rule.
- The authority declares `synthetic_calibration_fixture`, `product_definition_authority: false`, and the semantic scope `neutral generic request and document approval semantics`. The reviewed language is product-neutral synthetic authority.
- The contract, identity inventory, obligation index, canonical authority, and provenance inventory form an exact 114-record graph. Every canonical and provenance record is unique, active, and `CURRENT`.
- `FR-L13` is absent. Lifecycle `superseded_sentinels` remains a raw provenance-only array with no semantic identity or obligation.
- The controller evidence contains 114 unique bindings with the exact 76/38 aggregate, and all 114 candidate hashes and all 114 canonical hashes bind to the package values without mismatch.
- Non-semantic location checks covered rule number and order, owner and visible identity, contract and inventory field order, clause/value count, text and word length, equality/paraphrase form, candidate/canonical/provenance hash rank, canonical pointer rank, repeating cycles, universal tokens and phrases, and other reviewer-visible metadata. No tested feature or combination supplied a deterministic answer mechanism without semantic comparison.

## Production verification

- Production `load_and_verify_package`: `PASS`
- Loader preflight errors: `[]`
- Loader expected identity count: `114`
- Frozen reviewer brief, responsibility profile, and output schema are byte-identical to production artifacts.
- The reviewer package contains exactly its manifest and nine declared files. No per-identity answer label, controller path, reviewer run/output, prior-review result, or hidden-answer material is present in reviewer-visible or tracked package surfaces.
- Production core, schema, implementation, and main surfaces were unchanged from the clean baseline before this audit artifact was written.

## Aggregate hashes

| Binding | SHA-256 |
|---|---|
| Manifest file bytes | `c40da265fe41fb56819ed9a952eeb14d2cf3ce221b6e8cbe9e650e8620770c32` |
| Reviewer input manifest | `86cf39560dea5fa01732c981f7df7880d7faa2836713be99a3243f06a582eff7` |
| Reviewer input package | `ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603` |
| Contract logical hash | `a680b0e6f4ca7330aa810c445bcaa67d93575e79ae59f159a87992061a885755` |
| Current controller evidence | `ba0125fb217af613f2cd96c845a4972b42c061d2c29bd2306dd9a7249e80e1bc` |

| Package file | Bytes | SHA-256 |
|---|---:|---|
| `action-contract.json` | 64,267 | `2a835fffa5a19d161136febb9045d45201eb895bfd96454889b521b659fce76b` |
| `canonical-authority.json` | 33,668 | `e90d63cadb09e441387258cc4c6d43fb1d403470d0b87d78894386c0ee787637` |
| `exclusion-manifest.json` | 158 | `ee943d115bb3212be0f1afcf977fa4c9df8080c9abeec8801b6f015896e9accc` |
| `manifest.json` | 2,323 | `c40da265fe41fb56819ed9a952eeb14d2cf3ce221b6e8cbe9e650e8620770c32` |
| `provenance-inventory.json` | 23,227 | `87e548d6ab79d4cfa2b7710a78e3267b4007428d93dfc6b6e26ce0b743e6221d` |
| `responsibility-profile-v1.json` | 25,116 | `f8010b9410bfb786cc3107e78a001e226bf30ce6cf8aafcfca303851dce56fc5` |
| `review-identity-inventory.json` | 62,376 | `e524f2371854596fec1b8241f1a1d1db9e5a2225d44f0cd7845fd5300974e033` |
| `reviewer-brief-v1.md` | 9,991 | `3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c` |
| `semantic-obligation-index.json` | 90,119 | `a2f88e3a9dd289c11f8b2e0545ada958fefd4d6e036bfb6495d2d07a97df7904` |
| `semantic-review-output.schema.json` | 7,821 | `4fd8fdc780759c258046cc6f5260ee315be6d1bd0e5df95f7c7c5d87a502adb5` |

CALIBRATION CORPUS AUDIT — PASS
