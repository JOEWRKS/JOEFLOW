# Figma Design Audit — Corrected

Overall visual verdict: **PASS — Figma ready for Make handoff**.

Acceptance sources: canonical `state.json` revision 55, `screen-spec.md`, `figma-make-handoff.md`, the v0.4 Figma-stage contract, exact live Figma nodes in file `fyow2BHoAXzpkzpozDGWXf`, the fresh live screenshot of `4:69`, and preserved local renders.

| Check | Expected observable | Fresh observed fact | Result |
|---|---|---|---|
| B-FIG-01 Native artifact | Editable Figma frames/text/components | Live editor is `figma`; original and correction roots are native auto-layout frames with editable descendants; two reusable components and 57 instances remain | PASS |
| B-FIG-02 Canonical screens/roles | SCR-001..004 and four roles visibly separate | Four original desktop frames and four corrected role-named mobile frames exist with stable SCR identity and distinct content | PASS |
| B-FIG-03 Responsive variants | Desktop and mobile for every canonical screen | Original 1360 × 980 screens plus four 320 × 620 mobile frames; Employee camera/file handling and role actions are explicit | PASS |
| B-FIG-04 Exact state coverage | All 16 canonical states with relevant behavior | Node `4:146` has exactly 16 child cards naming every canonical state and its outcome/recovery behavior | PASS |
| B-FIG-05 Employee flow/recovery | Draft/upload/submit/withdraw/revise/history and failures | Desktop flow plus scan replacement, autosave preservation, withdrawal/history, delete confirmation/audit, and session restoration | PASS |
| B-FIG-06 Manager flow/reversal | Exact revision, three decisions, bounded revocation/conflict recovery | Exact latest approval, revoke only before Scheduled, mandatory reason, same revision to Submitted, post-Scheduled correction, and stale rejection are shown | PASS |
| B-FIG-07 Finance flow/recovery | Ownership, payment/failure/retry/hold, verification/adjustments | Atomic claim, failed-payment verification, Not paid vs executed resolution, one active adjustment, and Needs verification blocking are shown | PASS |
| B-FIG-08 Admin flow/recovery | Complete Admin and authority-change coverage | Invitation revoke, accounts/roles/manager, categories/hold, reassignment, raw audit/warnings, and session revocation are shown | PASS |
| B-FIG-09 Failure/recovery visibility | Material recovery paths concrete enough for low-fi handoff | State cards specify retry/no partial mutation, preserved input, idempotent timeout resolution, retry cancel, duplicate-action block, and expiry recovery | PASS |
| B-FIG-10 Legibility after correction | Text remains within cards without pathological wrapping/obscuring | Fresh live screenshot has no overlap; metadata found zero text nodes narrower than 30 px with more than five characters. Older local PNG clipping is explicitly pre-fix | PASS |
| B-FIG-11 Brand restraint | No unsupported final identity | Neutral grayscale low-fi explicitly disclaims final brand decisions | PASS |

## Remaining non-blocking limitations

The correction uses coverage-oriented low-fi cards rather than fully expanded pixel-level variants for every state. Repeated `Entry → precondition → action → outcome / recovery` microcopy is schematic, and interaction behavior is not executable in static Figma. Those limits are appropriate here because canonical semantics are explicit and revision 55 remains authoritative. The product projection still says Figma is unverified; it was not edited due evaluator scope.

Figma-stage result: **PASS**. The design is ready to connect to Figma Make using the canonical handoff. This does not verify Make generation or behavior; the overall run remains incomplete until actual Make execution, source readback, and blind drift audit.
