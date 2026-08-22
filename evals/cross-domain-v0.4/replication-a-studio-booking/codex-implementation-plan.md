# Replication A — Codex Implementation Plan

**Spec:** `product-definition/studio-booking-dogfood/CODEX_IMPLEMENTATION_HANDOFF.md`

**Goal:** Produce and independently audit a working, dependency-free studio-booking browser prototype that preserves canonical revision 62 and audited Figma roots `4:2` / `4:656`.

**Architecture:** A static semantic HTML shell loads ES modules. `src/domain.js` owns pure guards, pricing, availability, atomic transition, optimistic-version, permission, and idempotency behavior. `src/catalog.js` owns the exact screen/action registry. `src/app.js` owns role navigation, stateful workflow rendering, dialogs, and live feedback. `styles.css` implements audited low-fi structure plus bounded token refinement. `server.mjs` uses Node built-ins only. Tests use `node:test` and must be written and observed failing before production files are implemented.

**Technology:** HTML5, CSS, JavaScript ES modules, Node.js built-ins (`node:test`, `http`, `fs`). No third-party dependencies and no package installation.

## Global constraints

- Only Replication A is in scope. Do not read, write, or start Replication B.
- Do not alter `state.json`, approved uppercase projections, Closure evidence, Figma artifacts, Skill, validator, schema, taxonomy, CI, tags, or PR state.
- Implement against exact revision 62/digest and audited Figma root `4:2`; root `1:4` is historical.
- Keep product behavior Korean-only, Asia/Seoul, one branch, KRW, no payments, no customer accounts, no recurring booking, no external calendar.
- Use `apply_patch` for all file edits.
- Do not commit or push. Preserve existing user changes.
- Initial implementer must not read historical Make drift reports, Replication B, or prior drift findings.
- Initial blind auditor receives canonical artifacts and generated source only; it must not read historical Make findings or Replication B.
- Maximum correction passes: 3. Only current BLOCKING/MAJOR findings enter a correction pass.

## Task 1: Test-first integrated prototype

**Files:**

- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/package.json`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/index.html`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/styles.css`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/server.mjs`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/src/catalog.js`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/src/domain.js`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/src/app.js`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/tests/catalog.test.mjs`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/tests/domain.test.mjs`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/tests/source-contract.test.mjs`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/README.md`
- Create: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation-report.md`

### Step 1: Write failing tests

Write exact catalog tests for 27 unique screen IDs and 78 canonical action names. Write domain tests for 30-minute bounds, 1–8h duration, buffers, 2h lead, 90-day horizon, capacity, compatibility, equipment totals, atomic conflict no-op, even-won rate, frozen KRW snapshot/delta, 48h boundary, complete policy guard, stale version no-op, idempotent replay, role denial, neutral link response/rate limit, delivery independence, and reason-required transitions. Write source-contract tests for semantic landmarks, live status, dialog/destructive confirmation, reduced-motion CSS, responsive breakpoints, and explicit prototype boundaries.

Run `npm test` and record the expected failure caused by missing production modules/files. Do not create production files before this red evidence.

### Step 2: Implement the pure domain and catalog

Implement the smallest pure APIs that make every test pass. Use explicit result objects rather than exceptions for expected product guards. Atomic transitions return unchanged input state on failure. Version checks and idempotency are observable. The catalog exactly matches the handoff and maps screens to Customer, Staff, Owner, or shared access without granting Owner-only actions to Staff.

### Step 3: Implement the browser experience

Build one cohesive SPA that exposes all screens/actions and substantive stateful core journeys. Provide deterministic sample resources/availability and a scenario control for conflict, session expiry, delivery failure, and authority loss. Destructive actions use reason + confirmation. Unsupported production services are labeled simulated/not verified. Use native controls and no external assets or libraries.

### Step 4: Apply the design contract

Match the Figma structural grammar and refinement report with semantic tokens, wide-grid and 320–375px reflow, 44px targets, visible focus, live feedback, field errors, reduced motion, and no layout-shifting press states. Preserve screen IDs in `data-screen-id` and action names in `data-action` for source/readback audit.

### Step 5: Verify and report

Run `npm test`, start the static server, and read back `/`, `/src/domain.js`, and a missing path. Record exact commands/exits. Self-review changed files, confirm frozen surfaces remain untouched, and write `codex-implementation-report.md` with red/green evidence, feature inventory, known production boundaries, and concerns. Do not read historical drift files.

## Task 2: Independent blind audit and bounded correction

The controller dispatches a separate fresh auditor after Task 1. The auditor reads only the approved A artifacts, audited Figma authority, direct handoff, and implementation source/report. It writes `codex-initial-audit.md` with findings `A-CODEX-DRIFT-001…`, severity, evidence, and verdict. Historical Make findings and Replication B remain excluded.

If the audit finds current BLOCKING/MAJOR issues, the original implementer receives only those findings, applies a test-covered correction, and writes `codex-correction-pass-N.md`. The auditor then performs a scoped re-audit. Stop after all current BLOCKING/MAJOR findings close or after three correction passes.

## Task 3: Controller verification and final A review

After blind auditing is complete, the controller may compare the final implementation finding families with v0.3.1 Make failure families. Run fresh tests, source inventory, validators, browser/visual checks at desktop and 375px, reduced-motion/accessibility checks, and frozen-surface diff checks. Write `CODEX_IMPLEMENTATION_REVIEW.md`, update A `aggregate-results.md`, issue only the allowed A verdict, and stop without starting B.
