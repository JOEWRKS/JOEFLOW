# Pre-Figma Cross-Artifact Audit — Revision 44

## Verdict

`PASS`

- BLOCKING: `0`
- MAJOR: `0`
- MINOR: `0`
- Canonical revision: `44`
- Approved digest: `2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1`
- State validator: exit `0`, valid
- Closure validator: exit `0`, `closed: true`

Revision 44 is safe to enter the Figma capability and design stage. This audit does not claim that a Figma file has been written or verified; `FIGMA_MAKE_HANDOFF.md` correctly records visualization as not yet verified.

## Audited artifacts

- `product-definition/client-feedback-portal-dogfood/state.json`
- `PRODUCT_DEFINITION.md`
- `UNKNOWN_LEDGER.md`
- `DECISION_LEDGER.md`
- `USER_FLOWS.md`
- `SCREEN_SPEC.md`
- `IMPLEMENTATION_PLAN.md`
- `FIGMA_MAKE_HANDOFF.md`

The directory contains exactly the seven required uppercase Markdown projections plus `state.json`; no lowercase duplicate projection exists.

## Typed mapping audit

The active inventory contains 7 requirements (`REQ-002`–`REQ-008`), 7 flows (`FLOW-002`–`FLOW-008`), 8 screens (`SCR-002`–`SCR-009`), 7 acceptance criteria (`AC-002`–`AC-008`), and 7 implementation tasks (`TASK-001`–`TASK-007`). Historical `REQ-001`, `FLOW-001`, `SCR-001`, and `AC-001` remain explicitly superseded and are not counted as active inventory.

| Check | Result | Evidence summary |
|---|---|---|
| Requirement ↔ Flow | PASS | Every active flow names an active requirement and acceptance criterion; flow capability and actors agree with the mapped requirement. |
| Requirement ↔ Screen | PASS | Every requirement screen ID resolves to an active screen whose reverse `requirements` list contains that requirement. |
| Requirement ↔ Acceptance | PASS | Every `acceptance_ids` reference resolves to an active AC whose reverse requirement mapping matches. |
| Flow ↔ Screen | PASS | Every flow screen ID resolves to a screen whose reverse `flows` list contains that flow. |
| Screen ↔ State/action coverage | PASS | Every active screen has UX coverage; all 16 required screen-state keys are covered; each screen's `major_actions` set exactly equals its UX action set; all 22 interaction axes per action are covered. |
| Task ↔ Requirement/Decision/Rule | PASS | Each task maps one active requirement and contains the complete DEC/RULE upstream set of that requirement; automated comparison found zero missing or extra upstream IDs. |
| Task ↔ Acceptance | PASS | Every task maps its requirement's AC and has dependencies plus concrete completion evidence. |

## Requirement, flow, screen, and acceptance consistency

- `REQ-002` / `FLOW-002` / `SCR-002` / `AC-002`: Designer-only magic-link authentication, resend rotation, delivery distinction, and 30-day absolute/7-day idle session boundaries agree.
- `REQ-003` / `FLOW-003` / `SCR-003`,`SCR-004` / `AC-003`: Designer-only project list/detail and explicit absence of collaborator, billing, and aggregate-cap UI agree.
- `REQ-004` / `FLOW-004` / `SCR-004`,`SCR-005` / `AC-004`: immutable upload, supported types, 100MB boundary, attempt idempotency, phantom prevention, and 50-active-file recovery agree.
- `REQ-005` / `FLOW-005` / `SCR-006`,`SCR-007` / `AC-005`: both actors are mapped; one active project-scoped 30-day link, rotation, revoke, archive/expiry denial, and recovery agree.
- `REQ-006` / `FLOW-006` / `SCR-007` / `AC-006`: both actors are mapped; Client-only pin creation, shared reply, Designer-only resolve, Client reopen, append-only history, and approved read-only behavior agree.
- `REQ-007` / `FLOW-007` / `SCR-008` / `AC-007`: designated Reviewer-only exact-Version approval/change request, evidence guard, expected revision, idempotency, irreversibility, history, and email agree.
- `REQ-008` / `FLOW-008` / `SCR-004`,`SCR-009` / `AC-008`: Designer archive/unarchive, role-scoped embedded history, all-session denial, and non-restoration of old links agree.

## Routes, roles, actions, and states

Routes match between canonical state, `SCREEN_SPEC.md`, and `FIGMA_MAKE_HANDOFF.md`:

- `SCR-002`: `/login`
- `SCR-003`: `/projects`
- `SCR-004`: `/projects/:projectId`
- `SCR-005`: `/projects/:projectId/versions/new`
- `SCR-006`: `/projects/:projectId/review-access`
- `SCR-007` Designer: `/projects/:projectId/versions/:versionId/review`
- `SCR-007` Client Reviewer: `/review/:token/versions/:versionId`
- `SCR-008`: `/review/:token/versions/:versionId/decision`
- `SCR-009`: `/projects/:projectId/history`

`SCR-007` uses the same role-keyed route object in state as the two explicit projected entries. Its action contract is consistent: `create_pin` is Client-only, `reply_thread` is shared while mutable, and `resolve_thread` is Designer-only and hidden or disabled for Client. No role, route, action, or permission drift remains.

The Version status vocabulary is consistently `DRAFT`, `IN_REVIEW`, `CHANGES_REQUESTED`, and `APPROVED`. Approval is exact-Version scoped, records actor/timestamp/version, is immutable and irreversible, and never creates a project-level approval state. A new Version starts a separate review cycle and does not inherit approval. No status or approval drift remains.

## Document-versus-state completeness

No material document/state omission remains:

- `PRODUCT_DEFINITION.md` projects objective, roles, scope, active requirements, screens, acceptance mappings, locked semantics, non-goals, and failure/recovery boundaries.
- `USER_FLOWS.md` projects all active flow IDs with actors, requirements, screens, and ACs.
- `SCREEN_SPEC.md` projects all active screen IDs, exact routes, actor permissions, actions, hierarchy, relevant data, state behavior, failures, and recovery.
- `IMPLEMENTATION_PLAN.md` projects all seven tasks with TASK ID, complete upstream REQ/DEC/RULE IDs, AC, dependencies, and observable completion evidence.
- `FIGMA_MAKE_HANDOFF.md` provides objective, scope, non-goals, roles, permissions, active decisions/rules/data, routes, screens, flows, states, actions, business/version/approval/comment semantics, validation, upload limits, failure/recovery, responsive behavior, accessibility, persistence expectations, acceptance, deferred items, and forbidden invention.
- `DECISION_LEDGER.md` and `UNKNOWN_LEDGER.md` preserve the full decision/unknown history without presenting superseded policy as active.

## Review-link expiry audit

The active review-link policy is 30 days:

- `DEC-015` is active and supersedes `DEC-011`.
- Current rule, data, flow, screen, AC, task evidence, product definition, unknown ledger, decision ledger, and Make handoff all use a 30-day review-link expiry.
- `DEC-011` retains the former 7-day review-link decision only as `SUPERSEDED` historical evidence.
- Other active seven-day references apply exclusively to the Designer session idle timeout under `DEC-038`; they are not review-link policy.

No stale active seven-day review-link policy remains.

## Implementation-plan evidence

- `TASK-001`: authentication issuance, delivery/resend distinction, single use, rotation, and session-expiry tests.
- `TASK-002`: Designer route/permission, navigation, and excluded-control absence tests.
- `TASK-003`: type/100MB/lazy-PDF, attempt idempotency, phantom prevention, 50-file behavior, and no aggregate cap through `RULE-114`.
- `TASK-004`: DEC-015 expiry, single-active-link rotation/revoke, all-session denial, draft recovery, exact-Version transition, and email evidence.
- `TASK-005`: dual-role canvas entry, Client-only pin, Designer-only resolve, reopen semantics, append-only/idempotent messages, local drafts, pin/reply email, self-notification suppression, and non-duplicating notification retry; includes `RULE-040`–`RULE-044`.
- `TASK-006`: evidence guard, expected-revision conflict, decision idempotency, immutable approval denial, and single-email effect.
- `TASK-007`: Designer archive/unarchive, all-session denial, old-link non-restoration, and role-scoped history.

All task completion evidence is specific and testable; the plan is not a UI-only TODO list.

## Findings and correction history

| Finding | Initial severity | Classification | Correction and final verification |
|---|---|---|---|
| Auditor initially reported active 7-day review-link policy versus 30-day artifacts. | BLOCKING | `EVALUATOR_ERROR` | Authority was corrected: the user explicitly reversed 7 to 30 days. DEC-015 is active, DEC-011 is historical only, and the independent 7-day Designer idle timeout remains distinct. Revision 44 has no active leakage. |
| `SCR-007` exposed Designer-only `resolve_thread` as if it were a Client-route action. | BLOCKING | `PROJECTION_DRIFT` | State and projections now define dual role-qualified entries and explicitly restrict resolve to Designer, pin creation to Client, and reply to both. |
| Make handoff was only a terse route/action list and omitted required contract sections. | BLOCKING | `PROJECTION_DRIFT` | Handoff now includes all required scope, role, route, state/action, rule, data, validation, recovery, accessibility, acceptance, deferred-policy, and forbidden-invention sections. |
| Current requirements had empty Rule/Decision traceability. | MAJOR | `PROJECTION_DRIFT` | Every active REQ now carries its complete DEC and RULE sets; typed cross-check passes. |
| TASK-004 and TASK-007 contained unrelated decisions and omitted central link/archive decisions. | MAJOR | `PROJECTION_DRIFT` | Incorrect mappings were replaced with complete requirement-derived upstream sets and concrete evidence. |
| Designer-only flows incorrectly listed both actors. | MAJOR | `PROJECTION_DRIFT` | FLOW-002, FLOW-003, FLOW-004, and FLOW-008 now list USR-001 only; mixed and Reviewer-only flows remain correctly scoped. |
| Product and screen projections were too abbreviated to expose state, permission, and recovery behavior. | MAJOR | `PROJECTION_DRIFT` | Projections now expose role, route, action, state, failure, recovery, and locked semantic boundaries sufficiently for implementation/audit use. |
| REQ-005 and REQ-006 omitted one of their participating actors. | MAJOR | `PROJECTION_DRIFT` | Both now map USR-001 and USR-002 consistently with flows, screens, decisions, and ACs. |
| `SCR-007` canonical route was prose while projections introduced two exact routes. | MAJOR | `PROJECTION_DRIFT` | Canonical route is now a role-keyed object with the exact Designer and Client routes used in both projections. |
| TASK-003 omitted RULE-114; TASK-005 omitted RULE-040–RULE-044 and notification evidence. | MAJOR | `PROJECTION_DRIFT` | Task upstream sets now exactly match their REQs; TASK-005 adds explicit email/self-notification/idempotency evidence. |
| Handoff's numeric DEC range could be read as including superseded DEC-011. | MINOR | `PROJECTION_DRIFT` | Wording now selects active/current decisions and explicitly excludes superseded records. |
| Approval digest was not yet available in projections before approval. | MINOR | Expected pre-approval state | Exact revision 44 and digest were presented and approved; state approval metadata and fresh validator digest match. |

## Final gate

Blocking findings remaining: `0`.

Major findings remaining: `0`.

The approved revision 44 package passes the pre-Figma cross-artifact gate. Figma work must still begin with actual capability discovery and must not be claimed complete without verified native write/readback evidence.
