# Observable Emergent Decisions

This list contains decisions that were visibly rediscovered or explicitly labeled unexpected/emergent during the session and were actually asked and answered. It does not claim correspondence to, or knowledge of, any hidden answer bank.

1. APPROVED cannot be withdrawn in v1; later change requires a new Version and preserves prior approval evidence.
2. APPROVED exact-Version file, Version ID, approval actor, and timestamp are immutable.
3. CHANGES_REQUESTED requires an unresolved pin or overall reason; empty evidence is forbidden.
4. Designer reply to a RESOLVED thread leaves it RESOLVED; only Client reply reopens it.
5. Comment/reply editing is forbidden; correction is a new append-only reply.
6. At review-link expiry, new reads/writes and submit are blocked immediately; local draft text is preserved best-effort for later retry.
7. One active review link per project; issue/rotate immediately revokes the old link; manual revoke exists and blocks all sessions on the next request.
8. Revocation uses the same local-draft preservation and new-link recovery as expiry.
9. The 7-day review-link policy was materially reversed to 30 days, preserving superseded history.
10. No pre-expiry email is sent in v1; Designer may reissue after expiry.
11. Upload timeout recovery uses a client-generated attempt ID and returns the already-created Version without duplication.
12. Exact-Version state mutations require expected state revision; uncertain approval never shows success and retry cannot duplicate approval history.
13. APPROVED exact Versions reject all comment/reply mutations and show existing discussion/history read-only.
14. v1 has no PDF page-count limit; 100MB remains the file cap, rendering is lazy/on-demand, and future page cap depends on observed performance under an explicitly accepted eight-axis deferral.
15. Archive is reversible, but unarchive never restores a previous review link.
16. Same verified Reviewer identity may use multiple browser/device sessions; revoke/expiry/archive blocks them all on the next request.
17. Preserve link lifecycle metadata only; do not store raw tokens or per-request IP/device logs; token verifier is non-recoverable.
18. Audit is embedded in object screens rather than a unified audit screen, with role-scoped visibility.
19. Message submission recovery preserves text locally and uses a client message attempt ID; prior success returns the existing record with no duplicate.
20. CHANGES_REQUESTED recovery uses transition attempt ID + exact Version + expected revision and suppresses duplicate state history/email.
21. Designer authentication uses provider-neutral email magic links that expire after 15 minutes, are single-use, and rotate prior unused links; delivery failure and resend are distinct.
22. Designer session lasts at most 30 absolute days and expires after 7 idle days, then requires a new magic link.
23. No workspace project-count or total-storage hard cap; project active deliverable/version files are capped at 50 with read/download/archive preserved and only upload blocked.
24. Canonical shared review canvas has role-qualified entries; only Designer resolves, only Client creates pins, both reply, and only Client reply reopens.
