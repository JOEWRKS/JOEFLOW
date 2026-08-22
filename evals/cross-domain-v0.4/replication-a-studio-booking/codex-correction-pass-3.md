# Codex correction pass 3

Red evidence: `node --test tests/pass3.test.mjs` exited `1` because `src/ui-contract.js` was absent. Green: `npm test` exited `0`, 14 pass/0 fail.

This pass adds a testable UI contract covering 78 distinct Korean labels and 27 screen schemas, and wires the SPA fallback through the deny-by-default `executeAction` dispatcher. The dispatcher returns stateful resource/block/outage/operator transitions or deterministic action-specific readbacks; unknown/unauthorized actions deny. A-CODEX-DRIFT-006 and 011 remain closed; minor 010 was untouched.
