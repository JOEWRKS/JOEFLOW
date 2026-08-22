# Replication B — Codex Implementation Final Review

## Final outcome

**FAIL — CODEX_DRIFT_UNRESOLVED**

| Gate | Final result |
|---|---:|
| BLOCKING | **2** |
| MAJOR | **5** |
| MINOR | **2** |
| Critical Failure | **Yes** |
| Correction passes used | **3/3** |
| Product re-entry | **None** |
| New product decisions | **None** |

The required PASS gate was BLOCKING `0`, MAJOR `0`, and Critical Failure `0`. It was not met. The failed implementation is frozen as evaluation evidence; no fourth correction was attempted.

## Frozen identity

- Branch: `eval/v0.4-replication-b-codex`
- Baseline parent: `585325a6fb76658d54ec631e224bf6aeb96137d8`
- Canonical Product Definition: revision `55`
- Approved digest: `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`
- Canonical `state.json` SHA-256: `c0e790c3a8c35f0cdc894110f069ab4d7919aed388f0a4fad2c54e5ae8193395`
- Figma authority: `fyow2BHoAXzpkzpozDGWXf`
- Final implementation source commit: `eecebc28701006dd2c7be4045a22542e34719705`
- Final `codex-implementation/` tree: `6294fc9072521fdb762808b87203a7e8bac4f7f5`
- Pass-3 correction evidence: `a48fc51a01bc716fb70458b1a1a3d324c3de7d34`
- Final independent audit evidence: `edb34818c7bc230f7f8fb0fca3db354f0f3f3250`

## Finding progression

| Stage | BLOCKING | MAJOR | MINOR | Critical failure | Verdict |
|---|---:|---:|---:|---|---|
| Initial blind audit | 9 | 9 | 3 | Yes | FAIL |
| Correction pass 1 audit | 2 | 10 | 3 | Yes | FAIL |
| Correction pass 2 audit | 3 | 8 | 1 | Yes | FAIL |
| Correction pass 3 final audit | **2** | **5** | **2** | **Yes** | **FAIL** |

Pass 1 resolved or narrowed the initial scope/transition/UI gaps but left two safety failures. Pass 2 resolved those two, then exposed three new adjacent-surface authorization/retention failures. Pass 3 resolved all three pass-2 BLOCKING findings and six of the eleven pass-2 targeted findings outright; five became partial. The final audit then found two independently blocking paths not covered by the correction tests.

## Final BLOCKING findings

### B030 — rejected adjustment resolution mutates authoritative state

`RESOLVE_ADJUSTMENT` stores an `Executed` verification before validating required amount/date/reference. Rejection therefore leaks a mutation without version or audit, and the leaked verification allows a second adjustment to bypass the one-active-adjustment guard. This is BLOCKING because a rejected public command corrupts authoritative settlement state and reopens duplicate recovery/additional-payment risk.

### B031 — non-finite money can be submitted

Draft numeric inputs are converted without finite-number validation. `NaN`/`Infinity` can be committed and a KRW claim can then reach Submitted; persistence can further serialize those values as `null`. This is BLOCKING because the corrupted amount becomes the basis for approval, export, payment, and adjustment behavior.

## Final MAJOR and MINOR findings

- `M006`: Admin stale responses name changed fields but fail to return prefixed `user.*`, `category.*`, or `invitation.*` latest values.
- `M012`: terminal payment does not clear overdue, stopped Manager reminders can retry, and non-material draft commands reset the retention clock.
- `M013`: related timelines render current claim status on historical events, producing false historical provenance.
- `M014`: Admin has no current-filter controls, CSV uses mutable current category names instead of submitted snapshots, and mobile Audit/export composition is squeezed.
- `M027`: approval-revocation does not deliver the required Manager result and stopped reminders can retry.
- `m021`: Admin mobile navigation remains dense and horizontally hidden inside the tab scroller.
- `m030`: two seeded category display names differ from canonical DATA-001 labels.

No pass-3 correction itself was proven to introduce a new material regression; B030/B031 were pre-existing but newly detected by the final blind audit. They nevertheless fail the final implementation gate.

## Verification progression

| Stage | Unit/component | Build | Browser E2E | Canonical validators |
|---|---:|---|---:|---|
| Initial source | 47/47 | PASS | 11/11 | PASS |
| Pass 1 | 55/55 | PASS | 11/11 | PASS |
| Pass 2 | 71/71 | PASS | 11/11 | PASS |
| Pass 3 final | **85/85** | **PASS, 41 modules** | **11/11** | **PASS; Closure digest exact/all metrics 0** |

The green suite did not detect the final failure because it lacks the rejected-Executed-adjustment-then-create sequence, non-finite money submission, terminal overdue/reminder stop assertions, Admin-prefixed stale comparison, historical event-status assertions, and exact Admin export snapshot/mobile composition coverage.

Fresh pass-3 visual evidence covered Employee, Manager, Finance, and Admin desktop plus Admin 320 px. Page-level overflow was absent and CSV mobile guidance was visible. The final auditor independently reproduced the narrower Admin mobile audit/export obstruction at 390 px.

## Baseline and authority integrity

- Product Definition revision, digest, decisions, artifacts, Figma, Skill, interrogation engine, schema, validators, and Closure semantics were not changed by implementation or corrections.
- Implementation remained isolated under `codex-implementation/`.
- No Product Definition re-entry and no new product decision occurred.
- No Replication A artifact, drift lesson, implementation source, or cross-domain comparison was used.
- Real payment, email, authentication, encryption, malware scanning, immutable database, object storage, and production integrations were not claimed or executed.
- Figma Make was not executed.
- The audit-time Playwright personal-cache incident during pass 1 was contained: the exact four task-created cache directories were removed, task server PID lineage was stopped, and absence was read back before work resumed. All later browser runs used the worktree-local browser root.

## Runtime boundary

Verified: pure domain engine behavior exercised by the recorded tests, React public surfaces, local browser persistence, local Chromium E2E, task-owned screenshots, and canonical validators.

Unverified: current iOS Safari/Android Chrome engines, production concurrent services, real provider delivery, real bank/payment execution, real identity/session security, production storage/encryption/deletion, malware scanner behavior, and user acceptance.

## Exact decision

Correction limit `3/3` is exhausted. With BLOCKING `2`, MAJOR `5`, and Critical Failure `Yes`, the final result is:

**FAIL — CODEX_DRIFT_UNRESOLVED**

Replication B implementation stops here. No merge to `main` or the baseline branch is authorized.
