# Replication B Aggregate Results — Provisional Through Figma

| Measure | Result |
|---|---:|
| Canonical revision | 55 |
| Reconstructed visible question turns | 55 (54 interrogation + 1 closure approval) |
| Initial unknowns | 28 (reconstructed) |
| Emergent unknowns | 26 |
| Final unknown records | 54 |
| Final blocking unknowns | 0 |
| Decisions | 55 (54 current answers, 1 superseded) |
| Assumptions / deferred items | 0 / 0 recorded |
| Reversal | Verified, DEC-021 → DEC-022 |
| State validator | PASS |
| Closure validator | PASS |
| Actual native Figma | VERIFIED — file `fyow2BHoAXzpkzpozDGWXf` |
| Canonical Figma screen IDs | 4/4 present |
| Reusable components | 2 native components; 57 instances |
| Corrected coverage root | VERIFIED — `4:69` |
| Responsive variants | PASS — four desktop + four 320 × 620 mobile frames |
| Exact state coverage | PASS — 16/16 at `4:146` |
| Material action/recovery coverage | PASS — four role matrices at `4:195` |
| Figma visual audit | PASS — ready for Make handoff |
| Critical failures | 0 observed |

Provisional Replication B status: Figma gate **PASS; ready for Make handoff**. The targeted correction added four native mobile variants, an exact 16-state matrix, and four role-specific material action/recovery matrices; fresh native metadata and a live screenshot verify the post-wrap-fix artifact. The preserved `figma-coverage-rev55.png` predates the final text constraint and is historical evidence only. Make has not been performed, so the run is not end-to-end verified and Make drift/correction counts remain not applicable. No cross-run failure-family classification is made here because the v0.4 contract requires A and B to finish before aggregation.
