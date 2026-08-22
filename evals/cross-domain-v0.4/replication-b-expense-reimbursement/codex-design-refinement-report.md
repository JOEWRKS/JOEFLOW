# Replication B Codex Design Refinement Report

## Identity and authority

- Run: `CODEX_IMPLEMENTATION_BEHAVIOR`
- Product: `expense-reimbursement-dogfood`
- Baseline commit: `585325a6fb76658d54ec631e224bf6aeb96137d8`
- Canonical revision/digest: `55` / `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`
- Authority: canonical `state.json` and projections, then audited Figma. No Replication A evidence or B hidden answer bank was used.

## Capability check

- `Open Design: UNAVAILABLE_IN_CURRENT_RUNTIME`
- Figma design-to-code tooling: available and used for live readback.
- UI/UX Pro Max: available. Used only for bounded guidance on responsive table/card treatment, page overflow, and explicit submit feedback.
- Apple Design: available. Only immediate feedback, system typography, reduced motion, clear hierarchy, and predictable recovery guidance apply. Apple branding, Liquid Glass, marketing composition, cinematic motion, and Apple-specific metaphors are excluded.

## Live Figma readback

The audited file `fyow2BHoAXzpkzpozDGWXf` was inspected directly before coding.

| Node | Observed authority |
|---|---|
| `1:6` | Four neutral desktop role surfaces with list/detail or module workspace hierarchy |
| `4:69` | Corrected canonical UX coverage root for revision 55 |
| `4:73` | Employee mobile: camera/file upload, scan recovery, autosave preservation, withdrawal, read-only history |
| `4:91` | Manager mobile: exact revision, three outcomes, pre-Scheduled approval reversal, stale recovery |
| `4:109` | Finance mobile: atomic claim, duplicate verification, payment/hold/retry, adjustment uncertainty |
| `4:127` | Admin mobile: invitations/roles, reassignment, categories/hold, audit/warnings, authority loss |
| `4:146` | Exact 16-state presentation matrix |
| `4:195` | Employee destructive/recovery, Manager reversal, Finance failure/adjustment, Admin module contracts |

No Figma node was modified. Figma is structural low-fi authority, not a final brand system.

## Approved refinement

The implementation uses a neutral operational shell with four explicit role contexts, high-information list/detail layouts on desktop, and a single-column task-first layout on mobile. A compact slate/blue palette, system typography, restrained radii, and small status badges improve legibility without establishing brand identity. Status is always expressed with text and shape/border as well as color.

The most important refinement is semantic visibility: commands expose preconditions, pending state, durable simulated result, changed business state, audit reference, delivery side effect, and recovery. Destructive or outcome-changing operations use focused dialogs with required reasons where canonical rules demand them. Stale conflicts compare preserved user input with latest server state.

## Responsive and accessibility intent

- Desktop: persistent role rail/header, scoped list, and detail/workspace panel.
- 375/320 px: stacked cards and forms; table content becomes cards or an explicitly bounded internal scroller; no page-level horizontal overflow.
- Semantic navigation, headings, labels, descriptions, inline errors, keyboard dialogs, visible focus, and live regions are required.
- Reduced motion substitutes static/opacity feedback and removes nonessential translation.
- Core actions remain reachable at mobile widths; CSV carries desktop-recommended guidance but is not removed.

## Boundary

This refinement adds no product role, field, transition, permission, route, or production capability. The deterministic local domain layer and browser persistence are evaluation mechanisms only.
