# Replication B Codex Implementation Report

## Frozen target

- Branch: `eval/v0.4-replication-b-codex`
- Initial blind-audit source commit: `4881528083e97a5bbe6a9bc8b8941b343c1a503c`
- `codex-implementation/` Git tree: `03bfbea19e466446ac1471de13791bb8fed0820d`
- Baseline parent: `585325a6fb76658d54ec631e224bf6aeb96137d8`
- Canonical authority: Product Definition revision `55`, approved digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`
- Canonical `state.json` SHA-256: `c0e790c3a8c35f0cdc894110f069ab4d7919aed388f0a4fad2c54e5ae8193395`
- Implementation handoff SHA-256 (worktree bytes): `b2430dfc88db9135a861ea7f7eebc6181a5141f0233b432c670a856cadb927e0`
- Figma authority: file `fyow2BHoAXzpkzpozDGWXf`; audited desktop root `1:6`, corrective coverage root `4:69`; live readback used nodes `4:73`, `4:91`, `4:109`, `4:127`, `4:146`, and `4:195`.

The implementation is isolated under `codex-implementation/`. No Product Definition, Figma, Skill, interrogation engine, validator, schema, Closure rule, baseline branch, or `main` mutation is part of this source snapshot.

## Capability and design inputs

| Capability | Exact result | Use |
| --- | --- | --- |
| Open Design MCP | `UNAVAILABLE_IN_CURRENT_RUNTIME` | No Open Design mutation or claim |
| UI/UX Pro Max | Available; one bounded operational-form/queue/responsive/accessibility query | Mobile table/card behavior, explicit feedback, no page-level horizontal overflow |
| Apple Design | Available; relevant references only | System typography, immediate feedback, reduced motion, predictable hierarchy; no Apple branding or Liquid Glass |
| Figma | Available and live-read | Native hierarchy and role/state/action coverage as implementation structure; no Figma writes |

The approved implementation design is React 19 + TypeScript + Vite with a pure command-driven domain engine. React renders state and dispatches versioned commands; browser persistence is explicitly a local simulation and can be reset to a deterministic revision-55 fixture.

## Implemented contract

- Four role-scoped surfaces: Employee, Manager, Finance, Admin.
- Shared command envelope: actor, target, expected version, idempotency key, command type, structured input.
- Relationship/role checks, self-approval denial, stale no-op, exact committed-result idempotency replay, latest-revision review pinning, append-only simulated audit, and separate simulated delivery events.
- Employee draft editing, active categories, future/late-date validation, receipt/FX attachment scan simulation, ±1 KRW conversion guard, duplicate reason, manager guard, submit, withdraw, destructive draft delete, revision history, and Changes-requested resubmission.
- Manager queue/detail, late/duplicate/FX evidence visibility, approve, changes request, final reject, and approval revoke before Scheduled.
- Finance atomic claim/schedule, completion/failure/hold, owner/date/method/reference guards, structured failed-payment verification, verified reschedule, linked adjustments, one-active constraint, Needs verification block, and completed-only net totals.
- Admin invitation issue/reissue/revoke, account/session versioning, category snapshot/zero-active behavior, legal hold, bounded reassignment commands, operational warning/manual retry, raw audit, and governed CSV simulation.
- All 16 canonical UX presentations: default, loading, empty, partial, success, error, disabled, permission denied, unauthenticated, offline, timeout, retrying, submitting, completed, cancelled, expired.
- Text-plus-color statuses, labeled controls, dialog focus restoration, 44px control floor, 1440/375/320 responsive layouts, and reduced-motion media behavior.

## Verification before blind audit

| Check | Exact invocation/result |
| --- | --- |
| Unit/integration | `npm test -- --run --reporter=dot` — `6` files, `47/47` tests PASS |
| Browser E2E | task-owned `PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers`; `npm run test:e2e` — `11/11` Chromium tests PASS |
| Production build | `npm run build` — TypeScript project build and Vite build PASS; 39 modules transformed |
| Desktop/mobile overflow | Playwright at `1440`, `375`, and `320` — document overflow delta `<=1px`, primary action in viewport after scroll |
| Accessible names/focus | Public rendered controls all named; skip/focus and dialog trigger restoration PASS |
| Reduced motion | Chromium media emulation matched; computed duration `1e-05s` under reduce |

The first E2E invocation stopped before app execution because the Playwright browser was absent. Chromium `1234` was installed only under the ignored task-owned `.playwright-browsers/` root and the full run then passed. No personal installation or external product system was changed.

Build outputs are ignored and reproducible. Current readback hashes are:

- `dist/index.html`: `18fe49d0dc7c80c763ea9a37d9d311258507fb06718bae3498a90243f09f0da8`
- `dist/assets/index-BtHcBWam.js`: `702d42822516a9100b94a1612b74b90fc80ed72fc0b6ce9e9d2c2d8a199c0220`
- `dist/assets/index-Dxh_XaFX.css`: `9955c638cbe3762f008bc20002af2653f655f2377560b4e22a936713e1b4fb8f`
- `package-lock.json`: `4e8a586144e1003203a575db127d907895e1ad3e7a094ab18ba0ea2475143708`

## Visual check attempt 1

Sources: approved Figma file/root readback above; `CODEX_IMPLEMENTATION_HANDOFF.md` responsive/accessibility/role contracts; user-approved neutral React implementation boundary.

| Check | Expected observable | Concrete observation | Result |
| --- | --- | --- | --- |
| VC-01 role hierarchy | Four distinct role entry points and role-specific work hierarchy | Employee desktop shows persistent four-role rail, claim queue, selected detail, evidence, revision history, and terminal action area; Admin desktop shows six separate governance tabs and a separate audit/export panel | PASS |
| VC-02 operational restraint | Neutral, dense, legible operational UI without invented consumer branding | Actual 1440 renders use restrained green/neutral palette, system typography, compact status chips, bordered data surfaces, and no decorative imagery or unapproved brand system | PASS |
| VC-03 responsive reflow | Current mobile web reaches core Employee work with no page-level horizontal overflow | Actual 320 render reflows rail, summary, queue, form, evidence, history, and actions to one column; Playwright measured no page-level overflow and reached Submit | PASS |
| VC-04 state/action clarity | Status cannot rely on color; recovery/action boundaries visible | Every sampled state chip includes a symbol and text; upload scan/recovery copy, destructive delete styling, sticky action area, Admin raw-audit/export separation, and 16-state preview are visible | PASS |
| VC-05 no clipping/overlap | Text and controls remain readable in sampled desktop/mobile states | Direct inspection found no clipped labels, overlapped controls, or truncated action text in the three preserved renders | PASS |

Overall visual-check attempt 1: **PASS** for the sampled implementation states. This is not user acceptance and does not prove every unsampled state.

Evidence hashes:

- `visual-check-attempt-1-employee-1440.png`: `fcab98cdc87fa7d2fe09a82ea8d2f52dbb557269f98652a8efd320f598b7b73c`
- `visual-check-attempt-1-admin-1440.png`: `283f9c0553f642cadea54412efdadcdc5fe373b9e6d55f919747852b277bc9de`
- `visual-check-attempt-1-employee-320.png`: `c687f78c3dc353269da94bf7ea1fa8e46552209f7bbaf16583783cf08a88a145`

## Explicit capability boundary

This is a deterministic local product-behavior simulation. It does not implement or claim real payment execution, email delivery, authentication security, encryption, immutable database storage, provider integration, production concurrency, production file scanning, or external CSV transfer. Figma remains design authority; the SPA is a bounded implementation derivative to be independently audited for drift.
