# Mandatory Decision Reversal

The initial current truth allowed customer cancellation and rescheduling through exactly 24 hours before the shoot (`DEC-014`, `DEC-015`). The responder later changed both boundaries to exactly 48 hours. `DEC-014` and `DEC-015` are `SUPERSEDED`; `DEC-016` and `DEC-017` are current and point back through `supersedes`.

Affected canonical IDs include UNK-004, UNK-006, DEC-014..017, REQ-005, REQ-006, REQ-008, REQ-012, RULE-014..016, RULE-020, FLOW-005, FLOW-006, FLOW-012, SCR-003, SCR-007, SCR-008, STATE-016..019, DATA-005, DATA-006, and AC-029..036, AC-040..041, AC-115..119. The 48-hour boundary also appears consistently in global-time and policy surfaces.

Independent active-truth review found no stale 24-hour cancellation/reschedule cutoff. The old value remains only in the two superseded decision records and explicit provenance sentences explaining supersession. Other active `24시간` text refers to a distinct 24-hour customer-consent-link lifetime and is not stale cutoff truth.

No approval invalidation was needed after closure: the final approval was recorded only at revision 62, after reversal propagation, and its digest matches the final canonical definition.

