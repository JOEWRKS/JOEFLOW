# Aggregate Results

## Final verdict

**v0.4.1 HARNESS PASS.**

This means the downstream conformance layer detected the frozen material failures and passed its positive semantic controls. It does not convert either failed frozen implementation into PASS.

## Acceptance criteria

| # | Criterion | Result |
|---:|---|---|
| 1 | canonical Product Definition/Closure files unchanged | PASS; protected blobs are verified separately against `16fc6ed…` |
| 2 | separate downstream contract compiles from approved authority | PASS |
| 3 | no invented product semantics | PASS; every compiled clause is stable-ID/pointer/hash pinned |
| 4 | frozen A material failure detected | PASS |
| 5 | frozen B B030 and B031 detected | PASS |
| 6 | authority-loss sequence detected/tested | PASS |
| 7 | stale/no-op sequence detected/tested | PASS |
| 8 | idempotent replay sequence detected/tested | PASS |
| 9 | business-state vs delivery-failure sequence detected/tested | PASS |
| 10 | superseded transition sentinel tested | PASS; expected NONCONFORMANT on active observation |
| 11 | human-readable handoff references executable contract | PASS |
| 12 | existing 43 baseline tests pass | PASS; baseline preflight 43/43 |

## Critical-failure check

- Canonical Product Definition was not changed to satisfy the harness.
- State schema/validators were not weakened.
- Frozen A/B regressions were not excluded or patched.
- B030/B031 did not pass the harness.
- Superseded active behavior did not pass.
- Verdicts are based on 23 runtime execution records, not green test counts.

## Verification readback

- full unittest with pinned runtime environment: **71/71 PASS**;
- original baseline only: **43/43 PASS**;
- revision 44 state validator: **PASS**, `valid=true`;
- revision 44 Closure validator: **PASS**, exact digest and all metrics `0`;
- downstream Python compilation: **PASS**;
- Skill quick validation: **PASS**;
- downstream/evaluation JSON and JSONL parse: **10 files PASS**.

## Boundary

Responsive verification is excluded. No Figma Make generation, product-definition re-entry, vendor/database implementation claim, main merge, or evaluation-branch merge occurred.
