# Codex Correction Pass 2 — Replication B Expense Reimbursement

## Frozen authority and scope

- Branch: `eval/v0.4-replication-b-codex`
- Corrected source commit: `24a139ff6d97b62a7512150e86f3ec9bf6a5a368`
- Corrected `codex-implementation/` subtree: `9a788f6269160d6a76b715a50b98a390a8663e33`
- Canonical authority remains Product Definition revision 55 and approved digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`.
- Figma authority remains file `fyow2BHoAXzpkzpozDGWXf`.
- This pass changed only the isolated Codex implementation and its tests. Product Definition, Figma, Skill, schema, validators, and Closure semantics were not changed.
- Payment, email, authentication, malware scanning, immutable audit storage, and scheduled execution remain deterministic local simulations; this report makes no production-capability claim.

## Evidence-first corrections

| Prior finding | Pass-2 correction | Verification |
|---|---|---|
| B-CODEX-022 | Every role selector now checks the latest active account and exact current role. App and role surfaces hide governed claim/attachment data after deactivation. | Component/runtime regression asserts no claim or attachment visibility after deactivation. |
| B-CODEX-023 | A plain Failed adjustment without external-execution verification is treated as active and blocks another adjustment. | Engine and live-public-action regression cover the prior bypass. |
| M-CODEX-005 | Draft autosave has input generations, cancels older generation timers, retries transient failure after 1/2/4/8/16 seconds, stops after five retries, preserves browser input, and exposes manual retry. | Fake-timer component test proves two retry generations and preserved input before success. |
| M-CODEX-006 | Audit events now store target version, revision, and before/after snapshots. Stale responses derive changed fields from intervening target audit records and render changed fields plus browser-input preservation. | Engine regression asserts exact `revision.merchant` intervening change. |
| M-CODEX-010 | Attachment upload now has deterministic Clean/Timeout/Malware outcomes. Timeout remains Scanning and unlinked, schedules 30-second then two-minute retry generations, blocks submit, and discards bytes after final timeout or malware outcome. | Engine test proves unlinked timeout, both retry generations, and final absence; component test proves the public recovery control. |
| M-CODEX-011 | Public Admin controls now cover invitation roles/manager, multi-role account writes, direct-manager assignment, stable category creation, Manager/Finance reassignment, and held-payment reopen. | Admin component tests exercise roles, direct manager, and category creation; engine tests cover remaining guards. |
| M-CODEX-012 | Deterministic daily operations derive Payment overdue, deduplicate daily Finance notifications, issue Manager reminders and day-7 warnings, issue draft-expiry warnings, delete still-expired drafts/files with audit, and process three automatic delivery retries into permanent warning. | Clock-controlled engine tests cover same-day dedupe, overdue, reminder/escalation, 90-day deletion, and retry exhaustion. |
| M-CODEX-013 | Audit gained before/after/version/revision provenance; allowlisted related-user timelines are mounted for Employee, Manager, and Finance; Admin raw view exposes full local provenance. | Source trace and component rendering. Governed five-minute file download grants remain for independent audit classification. |
| M-CODEX-014 | Employee, Manager, and Finance lists now use current-authority search, status/category/currency/assignee/date/flag filters, and date/amount/recent sort. Finance/Admin export creates actual allowlisted CSV bytes from the filtered authorized IDs; download is separately reauthorized and audited. | Component tests exercise list filtering and Finance generation/download; engine scopes requested IDs to current Finance authority. |
| M-CODEX-015 | Payment methods exactly include Bank transfer, Corporate card settlement, Cash, and Other-with-description. Holds record whether execution may have occurred; Finance performs structured verification and Admin reopening requires Not paid where applicable, invalidates approval, and clears active payment ownership. | Engine hold/reopen regression and public controls. |
| M-CODEX-016 | Invitation acceptance requires exact invited email, pending/unexpired latest version, activates the invited role set, and loses atomically to revoke. Daily expiry invalidates elapsed pending invitations. | Engine race/email tests plus public activation component test. |
| M-CODEX-017 | Selecting any of the 16 states now replaces the current role workflow with a role-qualified state/recovery surface while leaving domain records unchanged. Role switching changes the scenario identity. | App component test asserts Employee and Manager permission-denied surfaces and hides normal Employee inputs. |
| m-CODEX-019 | Dialog focus moves inside on open, Tab/Shift+Tab remain trapped, Escape cancels, and focus returns only after a real close. | Component tests cover initial focus, Escape, cancel, and trigger restoration. |
| m-CODEX-020 | Seeded current category and immutable revision snapshot both use `Business lodging`; later category rename still preserves the snapshot. | Engine seed/snapshot regression. |
| m-CODEX-021 | All filters and role controls reflow at 320 px without page-level clipping. Admin role checkbox layout was compacted after visual inspection. The long Employee mobile document remains a non-destructive density limitation for audit classification. | Playwright responsive suite and fresh 320 px full-page screenshot. |

## Fresh verification

| Check | Result |
|---|---|
| `npm test -- --run` | PASS — 7 files, 71/71 tests |
| `npm run build` | PASS — TypeScript and Vite; 40 modules transformed |
| worktree-local `PLAYWRIGHT_BROWSERS_PATH`; `npm run test:e2e` | PASS — 11/11 Chromium tests |
| Visual inspection | Employee, Finance, and Admin desktop plus Employee 320 px captures inspected; no overlap, clipping, or page-level horizontal overflow observed. Admin role checkboxes were corrected after the capture and remain covered by component/build checks. |
| Task server cleanup | Exact task-owned PID 5284 stopped through its exec session; PID and port 4175 both read back absent. |

Visual evidence:

- `visual-check-pass-2/employee-desktop.png`
- `visual-check-pass-2/finance-desktop.png`
- `visual-check-pass-2/admin-desktop.png`
- `visual-check-pass-2/employee-mobile.png`

## Pass boundary

Pass 2 does not declare final acceptance. The corrected source is frozen at the commit above for a fresh independent blind audit. No Replication A material or hidden answer bank was used.
