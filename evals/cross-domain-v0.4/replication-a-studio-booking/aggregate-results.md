# Replication A Aggregate Results

| Measure | Result |
|---|---:|
| Reconstructed visible question turns | 62 (61 interrogation + 1 closure approval) |
| Initial unknowns | 37 |
| Emergent unknowns | 29 |
| Final unknown records | 66 |
| Final blocking unknowns | 0 |
| Decisions | 67 (65 current/answered, 2 superseded) |
| Assumptions / deferred items | 0 / 0 |
| Definition revision | 62 |
| Stable objects / dangling references | 610 / 0 |
| Requirements / flows / screens / states | 24 / 24 / 27 / 58 |
| Acceptance criteria / tasks | 229 / 24 |
| State validator | PASS |
| Closure validator | PASS, 19/19 metrics zero |
| Material Product Definition ambiguity | 0 |
| Critical failures | 0 |
| Figma file / audited root | `fClM2GgNhwEDIiqZcIWhNZ` / `4:2` |
| Figma correction passes | 1 |
| Native Figma descendants | 735 (370 frames, 365 text nodes) |
| Canonical low-fi screens rendered | 27/27 |
| Canonical major-action controls | 78/78 |
| Contextual failure/recovery panels | 27/27 |
| Concrete mobile journey states | 12 across Customer/Staff/Owner |
| Prototype reactions | 0 |
| Final Figma material findings | 0 BLOCKING, 0 MAJOR |
| Make correction passes | 0 (Make not started) |

Product Definition verdict: `PRODUCT_DEFINITION_VERIFIED`.

Figma verdict after targeted correction pass 1: `PASS — NATIVE_LOW_FI_VERIFIED`. The audited source is root `4:2`; superseded root `1:4` must not be used for Make.

Current per-run verdict: `PARTIAL — BLOCKED_AT_FIGMA_MAKE_EXECUTION`. Make readiness: `READY`. Actual Make generation, Make source readback, blind drift audit, and any Make correction have not started.

Cross-run failure-family aggregation is intentionally not performed here; the v0.4 contract reserves that work for `CROSS_DOMAIN_REPORT.md` after both runs complete.

## Codex implementation substitution track

Figma Make was not executed. The audited Figma was instead handed to an isolated Codex implementation agent through `CODEX_IMPLEMENTATION_HANDOFF.md`, followed by a separate blind source/behavior audit and the maximum three targeted correction passes.

| Measure | Result |
|---|---:|
| Source commit | `16fc6edc362321ea03613339e224472b98bc1a04` |
| Open Design | `UNAVAILABLE_IN_CURRENT_RUNTIME` |
| Initial Codex findings | 1 BLOCKING / 8 MAJOR / 1 MINOR |
| Authorized correction passes used | 3 / 3 |
| Final Codex tests | 14 / 14 pass |
| Final current material findings | 1 BLOCKING / 8 MAJOR |
| Final state validator | PASS |
| Final closure validator | PASS, exact revision-62 digest, 19/19 metrics zero |
| Final Codex implementation verdict | `FAIL — CODEX_DRIFT_UNRESOLVED` |

The responsive visual shell passed desktop, 375px, 320px, focus, and reduced-motion checks. It failed the required substantive booking and destructive-action scenarios: most SPA actions append generic audit records instead of invoking the canonical domain transitions. Passing unit/source-contract tests therefore do not establish end-to-end conformance.

This section supersedes the earlier `PARTIAL — BLOCKED_AT_FIGMA_MAKE_EXECUTION` status only for the Codex substitution track. The approved Product Definition and Figma verdict remain unchanged. Replication B was not started as part of this track. The failure classification is `CODEX_IMPLEMENTATION_BEHAVIOR`.

### PM-review freeze additions

- `ACTION_DOMAIN_COVERAGE.md`: complete 78-action inventory, including 66 mutating/workflow actions and 12 read-only control actions. Of the 66, 4 have partial action-specific mutations, 6 stop at an unreachable confirmation continuation, and 56 fall through to generic audit append.
- `TEST_GAP_ANALYSIS.md`: explains the 14/14 green-suite coexistence with BLOCKING 1 / MAJOR 8, severity rationale, correction chronology, delivery regression, and test-protection gaps.
- Implementation source and tests were not modified during the freeze.
