# Codex Implementation Handoff — Expense Reimbursement Dogfood

## Authority pin

- Canonical source: `state.json`
- Product Definition revision: `55`
- Approved digest: `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`
- Closure: `PASS`
- Audited Figma file: `fyow2BHoAXzpkzpozDGWXf`
- Desktop structural root: `1:6`
- Corrected UX coverage root: `4:69`
- Mobile roots: Employee `4:73`, Manager `4:91`, Finance `4:109`, Admin `4:127`
- State matrix: `4:146`; action/recovery matrix: `4:195`

This document is an implementation projection of revision 55. `state.json`, current canonical projections, and the audited Figma remain authoritative in that order. Generated source never changes product truth.

## Evaluation and production boundary

The implementation is a deterministic local simulation. It must make every represented UI action agree with simulated domain state, history, and visible recovery. It must not claim real payment execution, email delivery, secure authentication, encryption, immutable database storage, provider integration, production persistence, or production concurrency. Simulated delivery, authorization, audit, retention, file scanning, and payment checks must be labeled as simulations.

## Roles and authority

- **Employee (`USR-001`)**: owns their drafts and claims; edits/deletes drafts; submits, withdraws before a manager decision, revises after Changes requested, reads every own revision/review, and requests currently authorized attachments. Employee has no CSV export and cannot select or change an approver.
- **Manager (`USR-002`)**: sees only claims whose exact submitted revision is assigned to them; reads authorized history; approves, requests changes with a required comment, finally rejects with a required comment, and may revoke only their own approval with a required reason before Scheduled. Self-approval is forbidden.
- **Finance (`USR-003`)**: sees approved payable claims; atomically self-claims a shared item when moving it to Scheduled; completes, fails, holds, and safely retries payments; operates linked settlement adjustments; and exports an authorized filtered CSV up to 10,000 rows.
- **Admin (`USR-004`)**: manages invitation lifecycle, accounts and multiple roles, direct managers, categories, legal holds, manager/Finance reassignment, raw audit, operational warnings, and authorized filtered CSV. Admin cannot invent organization charts, departments, cost centers, or automated amount policies.

Every action checks current active account, role, target relationship, object version, and state precondition. Role possession alone is insufficient.

## Object and revision ownership

- One claim represents one expense. Each submission produces or targets one immutable revision identity.
- Submission snapshots the active category ID/name and the employee's direct manager.
- A normal manager change affects future claims and the next resubmitted revision, not the already assigned submitted revision.
- Only Admin may reassign an unfinished revision when its assigned manager is inactive. Existing comments remain; old/new manager, reason, actor, and time are audited. Notification failure does not roll back reassignment.
- Only the exact latest submitted revision accepts a review decision. Older in-flight actions are stale no-ops.
- Employees see every own revision and review. Managers and Finance see all revisions only while current processing authority remains valid. Losing authority immediately removes historical and attachment access.

## Claim and approval lifecycle

Supported business states and derived branches include Draft, Submitted, Changes requested, Resubmitted, Withdrawn, Approved, Payment pending, Scheduled, Payment hold, Payment completed, Payment failed, Final rejected, payment overdue, and linked adjustment states.

- Draft → Submitted requires direct manager, expense date, merchant/payee, receipt final paid total, currency, active category, business purpose, and linked clean receipt.
- A future Asia/Seoul expense date blocks. A date over 90 days old requires a late reason but may submit.
- Foreign currency requires original-currency final total, currency, KRW-per-unit rate with at most six decimals, claimed KRW total, and an allowed exchange-rate evidence type. The rounded product must be within ±1 KRW.
- Exact receipt hash across active/retained company claims blocks submission without leaking an unauthorized claim ID. Same employee/date/merchant/amount/currency requires a duplicate reason and remains visible to the manager.
- Submitted/Resubmitted → Approved, Changes requested, or Final rejected. Changes requested and Final rejected require comments.
- Changes requested creates an unlimited sequence of new revisions until withdrawal or final rejection. Prior revisions remain read-only.
- Employee withdrawal is allowed only before a manager decision and is terminal.
- Before Scheduled, the approving manager may revoke their own approval with a mandatory reason. The same revision returns to Submitted. At or after Scheduled, revocation is rejected.

## Payment lifecycle and correction

- Approved claims appear unassigned in the shared Finance queue as Payment pending.
- Payment pending → Scheduled atomically records the acting Finance owner and a scheduled date that is today or later. Competing stale claims mutate nothing.
- Scheduled → Payment completed requires method, actual payment date, and a company-unique external reference. `Other` requires description.
- Actual payment date is an Asia/Seoul date from the latest valid payment-leading approval date through today, inclusive.
- Scheduled → Payment failed requires a failure reason.
- Payment failed → Scheduled requires an append-only verification containing channel, masked account, lookup period, prior reference or lookup result, conclusion, verifier, time, and optional evidence. Only `Not paid` permits the transition.
- Finance may place Scheduled on Payment hold with a reason. If external execution is possible, verification is required before Admin can reopen as Changes requested. Reopen leads to a new employee revision and current-manager approval.
- Payment completed is immutable. Later correction uses a linked Recovery or Additional payment adjustment.

## Settlement adjustments

- Multiple adjustments may exist sequentially, but at most one may be In progress per claim.
- Net settled amount = original payment − completed recovery total + completed additional-payment total. Failed/cancelled adjustments contribute zero.
- Failed adjustments never reactivate. Append external-execution verification:
  - `Not executed`: close old item failed/cancelled and permit a linked replacement.
  - `Executed`: complete the existing adjustment with actual amount, completion date, and unique reference.
  - `Unclear`: move to Needs verification and block new adjustment creation until resolved.
- Original completed payment and prior adjustment history remain unchanged and visible.

## Mutation, concurrency, and idempotency

Every mutation command carries `actor`, `targetId`, `expectedVersion`, `idempotencyKey`, and command-specific input.

- Version mismatch is an atomic no-op that returns latest state and changed fields.
- Editable browser input remains available for comparison and retry.
- Replaying the same idempotency key and request fingerprint returns the original committed or rejected result without duplicate state, audit, or delivery records.
- Invitation acceptance/revocation, Finance ownership, one-active-adjustment creation, and other contested transitions commit atomically in the simulation.

## Notifications and business-state separation

- Actionable events create separate simulated email and in-app delivery records.
- Delivery retries are 1, 10, and 60 minutes, then Permanent failure with an Admin warning. Admin may perform one manual retry.
- Delivery event keys deduplicate attempts. Delivery failure never changes the already committed claim, review, payment, adjustment, or reassignment state.
- Manager reminders begin after three elapsed Asia/Seoul calendar days, once per day; Admin warning begins after seven. Decision, withdrawal, or reassignment stops the old assignment schedule. No automatic delegation occurs.
- Scheduled overdue begins at 00:00 KST the following day and notifies the responsible Finance user daily until completed, failed, or held.

## Files, sensitive data, and visible timelines

- Receipt and FX evidence allow PDF/JPG/PNG, at most 10 MB each; receipt maximum 10 and FX maximum 5 per revision.
- Actual MIME, extension, and simulated malware scan must pass before a file links or becomes downloadable. Failed bytes are discarded.
- Scan timeout shows Scanning, retries at 30 seconds and two minutes, then blocks submission while preserving other draft data.
- Simulated download grants are five-minute, one-user/one-file, reusable for range/retry, and reauthorize every request. Raw tokens never appear in UI, logs, audit, or tests.
- Related-user UI/API projections expose only `RULE-185` fields with masked external reference and exclude all `RULE-186` classes. Admin raw audit is a distinct authorized view. CSV uses the same or narrower allowlist.

## Retention, legal hold, and account lifecycle

- Drafts expire 90 days after the last confirmed saved change; view-only access does not extend retention. Warnings occur seven days before deletion. The daily 02:00 KST job rechecks eligibility; failed deletion remains retriable.
- Completed/final-rejected claim material is retained through seven years after its fiscal year end. Legal hold atomically protects all revisions, attachments, and audit until Admin releases it with a required reason.
- Role removal/account deactivation invalidates simulated sessions immediately. The next action is denied using latest authority; unsaved browser input is preserved with re-login guidance.
- Invitations expire after seven days. Reissue invalidates prior unused links. Revocation requires an Admin reason and races atomically with acceptance.

## UX, responsive, and accessibility contract

- Preserve four clearly identified role surfaces, visible current state, action grouping, recovery, and neutral low-fi restraint from Figma.
- Desktop uses operational list/detail composition. At 375 px and 320 px, core workflows become single-column without page-level horizontal overflow. Finance/Admin CSV remains available with desktop-recommended guidance.
- Use semantic headings, landmarks, form labels, field-level descriptions/errors, status text in addition to color, focus restoration after dialogs and mutations, keyboard operation, and visible focus.
- Announce mutation/loading/success/error states through appropriate live regions without duplicate announcements.
- Respect `prefers-reduced-motion`; never require motion to understand state. Touch targets remain usable on current iOS Safari and Android Chrome.
- Cover default, loading, empty, partial, success, error, disabled, permission denied, unauthenticated, offline, timeout, retrying, submitting, completed, cancelled, and expired presentations through real UI states or deterministic scenario controls.

## Forbidden invention

Do not add roles, permissions, lifecycle states, approval rules, payment behavior, fields, integration claims, routes, workflows, or recovery rules not supported by revision 55. Do not modify revision 55 to match the implementation. A genuinely missing material decision is `PRODUCT_REENTRY_REQUIRED` and pauses only the affected path.
