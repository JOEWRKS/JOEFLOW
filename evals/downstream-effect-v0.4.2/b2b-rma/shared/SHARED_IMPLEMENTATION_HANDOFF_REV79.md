# Shared Human-Readable Implementation Handoff — B2B RMA rev79

## Purpose and boundary

This is the single shared human-readable handoff for the later Control and Treatment arms. Both arms must receive the same approved Product Definition and the same audited Figma artifact.

This document summarizes approved product and design authority. It is not an executable contract, does not contain Treatment-only material, does not freeze S0, and does not authorize either implementation arm to start.

## Frozen authority

- Status: `CLOSED`
- Revision: `79`
- Approved digest: `1f329295fa2f11bda80709a63c5f6005d0bf47f9549b8978c712059230780a9a`
- Canonical directory: `product-definition/b2b-rma-dogfood/`
- Figma audit: `FIGMA DESIGN AUDIT — PASS`
- Figma audit record: `evals/downstream-effect-v0.4.2/b2b-rma/shared/FIGMA_DESIGN_AUDIT_REV79.md`

Authority order:

1. `state.json` at approved revision 79 and its exact digest-bound canonical object graph.
2. The approved projections in `PRODUCT_DEFINITION.md`, `DECISION_LEDGER.md`, `UNKNOWN_LEDGER.md`, `USER_FLOWS.md`, `SCREEN_SPEC.md`, `FIGMA_MAKE_HANDOFF.md`, and `IMPLEMENTATION_PLAN.md`.
3. The audited shared Figma file as the human-readable visual projection of that authority.
4. This handoff as a navigation summary only.

If a lower item conflicts with a higher item, stop and use the higher item. Do not silently invent or repair product semantics downstream.

## Shared Figma

- File key: `C8vxL0pVRja04HhqGFwSQU`
- URL: <https://www.figma.com/design/C8vxL0pVRja04HhqGFwSQU>
- Page: `0:1` — `Shared RMA — Rev79`

Root inventory:

| Purpose | Node ID |
|---|---:|
| Rev79 authority | `4:2` |
| Local editable components | `4:3` |
| `SCR-001` Return work queue | `4:4` |
| `SCR-002` RMA case workspace | `4:5` |
| `SCR-003` Warehouse specialist workspace | `4:6` |
| `SCR-004` Customer return portal | `4:7` |
| Shared lifecycle/failure matrix | `4:8` |

Relevant responsive frames:

| Screen | Intent | Node ID |
|---|---|---:|
| `SCR-002` | RMA/Finance tablet | `8:71` |
| `SCR-002` | RMA/Finance desktop | `8:51` |
| `SCR-003` | Warehouse mobile receipt/inspection | `8:17` |
| `SCR-003` | Warehouse mobile execution | `44:8` |
| `SCR-003` | Warehouse tablet | `18:8` |
| `SCR-003` | Warehouse desktop | `19:8` |
| `SCR-004` | Customer mobile base | `8:35` |
| `SCR-004` | Customer changes/inbound | `50:8` |
| `SCR-004` | Customer results/notice | `50:9` |

The Figma is low-fi and neutral. Its editable hierarchy and state clarity are authoritative visual guidance; decoration and unsupported final branding are not.

## Roles and authority

### Customer Requester

- Works only inside their own customer organization boundary.
- Creates, edits, deletes, and submits a request draft; submission creates an immutable request snapshot.
- May submit a linked change/cancel request only before the affected return scope reaches `IN_TRANSIT`.
- Registers or updates inbound tracking only for customer-paid return shipping; supplier-arranged tracking is read-only.
- Responds only to a current-owner-opened more-info request for approval or inbound discrepancy.
- Sees externally public status, resolution, notice, appeal, linked-correction status, and own-organization public case package.
- Does not reopen a resolution, execute a physical or financial action, switch tenant, or see internal-only fields.

### Current case owner / RMA Agent

- Has organization-wide case and audit visibility; ownership controls decisions and mutations.
- Approves, rejects, requests more information, assigns specialist scopes, determines final resolution, reopens eligible uncommitted scopes, reviews exceptions, confirms completion, and owns linked correction decisions.
- Directly executes outbound `RETURN_TO_CUSTOMER` handoff/tracking or records direct pickup evidence.
- Downloads the full internal case package. Other internal roles do not receive that package authority.
- Ownership or authority loss immediately blocks writes while allowing the latest permitted read state.

### Warehouse Inspector

- Works only on assigned physical scopes.
- Uses separate `SCR-003` stages for receipt/inspection, `REPLACEMENT` dispatch, and `NO_CREDIT` physical execution.
- Records observed quantity, mismatch/excess, serial or lot, fixed inspection values, local stock/location changes, tracking, actor/time, and required evidence.
- `RETURN_TO_CUSTOMER` destination/tracking/COD is read-only context; the current case owner executes the outbound handoff.
- Does not decide final resolution, reopen a resolution, decide exception ownership/cost, or download the full internal package.

### Finance Operator

- Works only on a current-owner-assigned `REFUND` result-allocation/partial-quantity scope.
- Confirms the authoritative KRW amount and deterministic local settlement-account snapshot, then requests transfer.
- Reads settlement-simulation progress and evidence.
- Does not reopen a resolution, change final resolution, decide linked correction/compensation, or gain broader case mutation rights.

## Screen responsibilities

### `SCR-001` — Return work queue

- Organization-wide operational queue for authorized RMA Agents.
- Shows role-scoped work, current owner, status, next action, exceptions, mixed-scope progress, SLA warnings, completion visibility, and linked-correction lineage.
- Supports approved filters and limited CSV analysis export without evidence files, raw audit events, contacts, or settlement accounts.
- Keeps navigation and actions role-scoped; it does not broaden current-owner authority.

### `SCR-002` — RMA case workspace

- Shared case summary, line scopes, immutable request snapshot, timeline, decisions, and evidence.
- Current-owner approval/rejection/more-info, final-resolution composition, specialist assignment, eligible pre-commit reopen and cleanup, commit confirmation, exception/completion confirmation, and post-commit linked-correction visibility.
- Finance execution appears only for assigned `REFUND` scope and includes the deterministic account snapshot and KRW evidence.
- Desktop-first and fully usable on tablet.

### `SCR-003` — Warehouse specialist workspace

- Mobile-priority, with tablet and desktop full-function projections.
- Separate stages for receipt/inspection, assigned `REPLACEMENT` dispatch, and assigned `NO_CREDIT` physical execution.
- Preserves fixed inspection choices, mismatch/excess handling, mixed line outcomes, upload/checkpoint recovery, commit confirmation, and role loss.
- Shows outbound `RETURN_TO_CUSTOMER` only as necessary read-only context.

### `SCR-004` — Customer return portal

- Customer-mobile projection for request draft, evidence, submit, decisions, inbound tracking, more-info, and result visibility.
- Includes the pre-`IN_TRANSIT` linked change/cancel boundary, `RETURN_TO_CUSTOMER` destination/contact and COD visibility, `NO_CREDIT` notice/appeal, linked correction status, and external-public package download.
- Never exposes other organizations or internal-only fields.

## Domain and lifecycle model

The main unit is an RMA case containing Return Lines. A Return Line can be split into result-allocation/partial-quantity execution scopes. Each scope has its own active resolution version and commit status, so committed, uncommitted, and cleanup-held scopes may coexist without stopping unrelated scopes.

Core lifecycle:

`DRAFT → REQUESTED → APPROVAL_PENDING / MORE_INFO_REQUESTED → RETURN_AUTHORIZED → INBOUND / RECEIVED → INSPECTION → RESOLUTION → EXECUTION → COMPLETED`

Exceptions such as mismatch, unauthorized excess, cleanup hold, physical exception, settlement exception, and linked correction are explicit states around the core lifecycle; they do not erase immutable history.

Final resolution is one of:

- `REFUND`
- `REPLACEMENT`
- `RETURN_TO_CUSTOMER`
- `NO_CREDIT`

Mixed line outcomes are allowed. Each approved result allocation and partial quantity remains independently traceable.

## Reopen, commit, and post-commit correction

The active history is `DEC-033 → DEC-034` and `RULE-042 → RULE-043`: the old save-time total irreversibility decision is preserved as superseded history, while eligible scopes may reopen before their approved execution commit boundary.

Only the current case owner may reopen an uncommitted scope, with a required reason and immutable audit event. Cleanup blocks new execution for the selected scope, cancels or invalidates uncommitted instructions, recalculates/relinks affected references, supersedes old notifications, and activates a new version only after all required evidence succeeds. Failure places only that scope in `REOPEN_CLEANUP_HOLD`.

Commit boundaries:

- `REFUND`: `TRANSFER_ACCEPTED` on the unique execution reference. `TRANSFER_SETTLED` plus amount, KRW, account snapshot, accepted/completed times, and result reference proves completion.
- `REPLACEMENT`: both local stock deduction and carrier-simulation acceptance recorded on the same unique execution reference.
- `RETURN_TO_CUSTOMER`: physical carrier handoff or customer direct-pickup signature. Label generation or result notice is not commit.
- `NO_CREDIT`: disposal execution begins. Notice, quarantine, and amount calculation are not commit.

After commit, the original resolution does not reopen. Errors or disputes use a linked correction case that immutably references the original case, scope, resolution version, and commit evidence. Unrelated scopes and the original case may continue.

## Concurrency, idempotency, and recovery

- Creation, save, submit, approval, transition, and execution reuse the original idempotency key for retries.
- Same key plus same input returns stored progress or result; same key plus different input is a conflict.
- Material writes require the expected scope version and commit atomically once. Losing concurrent attempts must read the latest server state; there is no automatic merge.
- Simulations use a unique reference per scope, resolution version, and action. A timeout checks saved progress/result before retrying with the same key.
- Successful server saves are the only authoritative checkpoints. Unsaved input may remain only in the current open tab.
- Connection loss blocks new save/submit, distinguishes saved from unsaved state, and resumes from the last server checkpoint after reconnect or reauthentication.
- Upload failure retains valid input and successful files, identifies the failed file, and retries only that file. Allowed evidence is JPG/PNG/PDF, at most 20 MB per file, with extension/MIME/signature and deterministic malware checks.
- There is no device-persistent offline editing, offline submit, offline synchronization, or automatic conflict merge.

## Notification and completion boundaries

- Customer portal posting is the business notification ledger. Auxiliary `SIMULATION` email delivery is a separate state and cannot roll back an already established business notification or physical process.
- `NO_CREDIT` notice uses one reference and becomes effective when atomically viewable in the customer portal. The 336-hour period runs continuously from that timestamp; auxiliary email failure may be retried with the same reference.
- The approved customer appeal is limited to the disposal-cost issue within 14 days of a successful viewable notice.
- Case completion requires all approved physical and evidence gates. Unresolved `NO_CREDIT` physical exceptions block the affected scope; settlement exceptions/disputes remain independently traceable and do not redefine the physical completion gate.
- Completed cases have no undo or same-case reopen. Later errors remain linked-correction lineage.

## Simulation and data boundaries

- The RMA app is authoritative for cases, requests, decisions, results, work, and audit history.
- Order/delivery and product/policy inputs are deterministic read-only local fixtures.
- Inventory, receipt, quarantine, and disposition use deterministic local warehouse state.
- Inbound, replacement, and return transport events use carrier simulation.
- Refund and disposal-cost financial events use settlement simulation.
- All fixture/simulation data, actions, states, and results must remain visibly labeled `DOGFOOD FIXTURE`, `LOCAL WAREHOUSE STATE`, or `SIMULATION` as applicable.
- Do not add actual external SSO, email, address validation, label, carrier, payment, bank, accounting, import/export integration, or real-world side effects.

## Responsive, accessibility, locale, and session expectations

- Customer: mobile.
- Warehouse: mobile-priority; tablet and desktop retain full specialist function.
- RMA/Finance: desktop-first and tablet-usable with the same functional authority.
- All user-facing screens and states target WCAG 2.2 AA: keyboard-only operation, logical focus order and visible focus, screen-reader name/role/state/error, and text/non-text contrast.
- Organization-wide locale/language is `ko-KR`, currency `KRW`, display timezone `Asia/Seoul`; amount displays separate supply amount, tax, and total when those approved values are present.
- Internal users use simulated organization SSO + MFA. Customer users use password + simulated email OTP. Both paths use 30-minute idle expiry, 8-hour absolute expiry, five consecutive failures followed by a 30-minute lock, verified recovery, and audit records.

## Explicit downstream guardrails

- Preserve canonical IDs and reversal history; do not revive superseded `DEC-033` or `RULE-042` as active behavior.
- Do not infer new product rules from low-fi spacing, placeholder copy, or hidden Figma construction layers.
- Do not add organization switching, multi-tenant administration, final branding, new roles, new screens, extra resolution codes, extra inspection values, or hard-delete behavior.
- Do not turn the shared handoff into a Treatment-only executable contract.
- Keep Control and Treatment on the same rev79 authority, shared Figma, and this shared handoff when those later stages are explicitly authorized.

## Stage boundary

At the time of this handoff:

- S0 has not been created or frozen.
- Treatment contract compilation has not started.
- Control has not started.
- Treatment has not started.
- `main` has not been modified or merged.
- Canonical `implementation_started=false` and tasks remain `0`.
