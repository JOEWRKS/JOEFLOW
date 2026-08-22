# Mandatory Decision Reversal

Initial DEC-021 made manager approval irreversible and locked the approved revision into Finance processing. The user later changed this rule.

Current DEC-022 permits only the approving manager to revoke their own approval before Finance commits `Scheduled`; reason is mandatory; the same revision returns to `Submitted`; at or after `Scheduled`, revocation is forbidden.

Verification:

- DEC-021 is `SUPERSEDED` and points to DEC-022.
- DEC-022 is `ANSWERED` and lists DEC-021 in `supersedes`.
- UNK-005 preserves the historical resolution and separately records the amended resolution.
- RULE-061 is current and the former reversal rule is the sole superseded rule.
- REQ-001..003 explicitly record recompilation against DEC-022/RULE-061.
- Active flow projections describe pre-Scheduled revocation; later correction uses Payment hold, Admin Changes requested, a new employee revision, and current-manager reapproval.
- All seven Markdown projections identify revision 55; no old no-revocation statement was found in them.
- Stable-reference audit found zero broken object references.

The historical old rule remains only where required for provenance (the superseded decision/rule and UNK-005's original resolution), not as active truth.
