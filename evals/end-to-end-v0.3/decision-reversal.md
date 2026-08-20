# Decision Reversal — Review-link Expiry

## Observable before and after

| Field | Before | After |
|---|---|---|
| Policy | Magic review link expires 7 days after issuance | Magic review link expires 30 days after issuance |
| Decision | `DEC-011` | `DEC-015` |
| Status | `DEC-011` was active when chosen | `DEC-011` preserved as `SUPERSEDED`; `DEC-015` is `ANSWERED` and active |
| Revision | 15 | 16 |
| User evidence | Option A: 7-day expiry | “7 days is too short; change it to 30 days.” |

`DEC-011.superseded_by = DEC-015`. The reversal did not rewrite history.

## Affected IDs recorded with the reversal

- `REQ-001`
- `RULE-026`
- `DATA-004`
- `FLOW-001`
- `SCR-001`
- `AC-001`
- `UNK-012`
- `UNK-022`
- `UNK-033`

The propagated concerns were review-link access rules, link lifecycle/data, expiry flow, expiry UI/state, acceptance, and notification/resend consequences. Approval metadata remained clear because the definition was not yet approved.

## Rediscovery

The 30-day reversal rediscovered `UNK-033`: whether to send a pre-expiry notification before the 30-day deadline. The user answered that v1 sends no pre-expiry notification; after expiry, Designer may issue a new link. This became `DEC-016` and affected `DEC-015`, `RULE-026`, `RULE-035`, `RULE-036`, `DATA-004`, `FLOW-001`, `SCR-001`, and `AC-001`.

## Active-projection residue audit

- Active review-link policy: 30 days under `DEC-015`.
- Historical 7-day review-link policy: present only as `DEC-011 SUPERSEDED` evidence.
- No active 7-day review-link policy remained in current REQ/FLOW/SCR/AC/TASK projections.
- Active 7-day references that remain are exclusively the separate Designer-session idle timeout (`RULE-111`, `RULE-112`, and authentication task evidence), not review-link expiry.
- Final approved revision 44 and digest `2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1` validated with `closed: true`.
