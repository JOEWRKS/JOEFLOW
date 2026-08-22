# Codex Correction Pass 1 — Replication B

## Frozen inputs and scope

- Initial audit: `codex-initial-audit.md`
- Initial source: `4881528083e97a5bbe6a9bc8b8941b343c1a503c`
- Correction source: `465831be07d0b857b8642cd18ed3ae2e8b681029`
- Corrected `codex-implementation/` tree: `a0410ea06cdcb9a49e7ed17d1eb0914580c14ae6`
- Pass used: `1/3`
- Initial finding counts: BLOCKING `9`, MAJOR `9`, MINOR `3`

This pass changed only the isolated implementation and its tests. Product Definition revision 55, approved digest, Figma, Skill, interrogation engine, validators, schema, Closure rules, baseline branch, and `main` were not changed.

## Test-first reproduction

The pass added failing tests for stale changed fields, rejected-result idempotency replay, Manager/Finance processing scope, separated revision editing/resubmission, fresh draft creation, current-manager submission binding, exact receipt-hash duplicate blocking, adjustment ownership, Scheduled-only hold, verified actual adjustment amount, zero-active categories, actual file selection, truthful autosave, and public Manager scope. The first run produced `17` failures against the frozen implementation.

## Corrections

| Initial finding | Correction and evidence |
|---|---|
| B-CODEX-001 | Manager selectors now expose only non-self `Submitted` and revocable `Payment pending` claims assigned to the actor. Finance selectors expose the shared pending queue plus only actor-owned downstream work. Unit/UI/E2E tests assert hidden Draft/self/Finance-history items. |
| B-CODEX-002 | Approval revocation now clears approval metadata and returns the same revision to `Submitted`; confirmation text no longer requests a new revision. Lifecycle and UI tests assert revision identity remains unchanged. |
| B-CODEX-003 | Added public `CREATE_DRAFT`. Changes requested now creates an editable Draft revision with no submission timestamp; editing and `SUBMIT_CLAIM` are separate public actions. |
| B-CODEX-004 | Submission reads the Employee's latest active direct Manager, updates current routing, and records `managerIdSnapshot` on the submitted revision before delivery creation. |
| B-CODEX-005 | Draft edits immediately show `Unsaved changes`, save on blur and after a two-second idle interval, show Saving/Saved/Failed truth, keep the browser form stable across server generation updates, and install an unload warning while dirty. |
| B-CODEX-006 | Every committed or rejected result is stored under the exact idempotency fingerprint. Exact rejected replay returns the original rejection after conditions change. Stale results include version/input changed-field reconciliation and preserve input. UI keys distinguish changed retry input. |
| B-CODEX-007 | Adjustment create/complete/fail/resolve require the current Finance owner; payment hold accepts only the Scheduled owner path. |
| B-CODEX-008 | Executed adjustment recovery requires positive actual amount, approval-to-today date, and unique reference. Completed totals use verified actual amount. |
| B-CODEX-009 | File records carry SHA-256; submission compares receipt hashes across retained company claims and blocks exact duplicates with a non-identifying message. Seed evidence is claim-owned and uniquely hashed. |

Directly related corrections also changed attachment validation to 10 MB per file and independent 10-receipt/5-FX limits, added real browser file/camera inputs with byte hashing, removed linked evidence on draft deletion, allowed zero active categories while submission remains blocked, and aligned the nine seeded category names with revision 55.

## Fresh verification

| Check | Result |
|---|---|
| Unit/integration | `npm test -- --run --reporter=dot` — `6` files, `55/55` PASS |
| Build | `npm run build` — TypeScript/Vite PASS, `39` modules transformed |
| E2E failure recheck | Obsolete self-review UI test failed because the corrected queue intentionally hides the item; test was replaced with the canonical absence assertion |
| Full browser E2E | task-owned Chromium, `npx playwright test --reporter=line --workers=2` — `11/11` PASS |

This report does not claim the initial MAJOR/MINOR findings are all resolved. A fresh scoped re-audit must determine the pass-1 disposition; no source correction may be inferred from test counts alone.
