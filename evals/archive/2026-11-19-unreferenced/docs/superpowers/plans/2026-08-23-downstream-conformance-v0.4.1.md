# Downstream Conformance v0.4.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile approved Product Definition truth into executable downstream contracts and prove the harness detects the frozen Replication A/B semantic defects without changing canonical authority.

**Architecture:** A Python standard-library core owns provenance, contract validation, expected semantics, sequence execution, and deep verification. Versioned JSONL adapters only invoke/read back actual runtimes. Product-specific adapter data maps canonical clauses to executable action/lifecycle obligations.

**Tech Stack:** Python 3 standard library, JSON/JSONL/JSON Schema documents, Node.js, frozen JavaScript/TypeScript runtimes, `unittest`, frozen Vitest toolchain where required by TypeScript execution.

**Spec:** `docs/superpowers/specs/2026-08-23-downstream-conformance-v0.4.1-design.md`

## Global constraints

- Work only on `feat/v0.4.1-downstream-conformance` based on `16fc6edc362321ea03613339e224472b98bc1a04`.
- Preserve canonical Product Definition, state schema, validators, taxonomy, stable IDs, interrogation, and Closure blobs.
- Never patch frozen A/B source. External adapters/runners may import and invoke it.
- Adapter output is observation; Python contract evaluation is authority.
- Use RED-GREEN-REFACTOR for every production behavior.
- Responsive verification is excluded.

### Task 1: Define contract/provenance schemas

**Files:**
- Create: `skills/joewrks-product-definition/downstream/schemas/action-contract.schema.json`
- Create: `skills/joewrks-product-definition/downstream/schemas/lifecycle-contract.schema.json`
- Create: `skills/joewrks-product-definition/downstream/schemas/execution-record.schema.json`
- Create: `tests/test_downstream_contracts.py`

- [ ] RED: test deterministic JSON hashing, exact JSON Pointer/hash provenance, approved authority identity, current-only references, and superseded rejection.
- [ ] GREEN: implement the minimal model/compiler/provenance modules using only the standard library.
- [ ] REFACTOR: keep product-specific semantics out of the core and validate deterministic bundle hashing.

### Task 2: Implement the versioned JSONL protocol

**Files:**
- Create: `skills/joewrks-product-definition/downstream/protocol.py`
- Create: `tests/test_downstream_protocol.py`

- [ ] RED: test required identity fields, one-record-per-line behavior, and rejection of invalid records.
- [ ] RED: test lossless `NaN`, `+Infinity`, and `-Infinity` sentinel round trips and malformed sentinel rejection.
- [ ] GREEN: implement recursive typed sentinel encode/decode and protocol record validation.
- [ ] REFACTOR: guarantee ordinary JSON remains unchanged and no non-finite standard JSON number is emitted.

### Task 3: Implement deep verification and sequence runner

**Files:**
- Create: `skills/joewrks-product-definition/downstream/verifier.py`
- Create: `skills/joewrks-product-definition/downstream/runner.py`
- Create: `skills/joewrks-product-definition/downstream/invariants.py`
- Create: `tests/test_downstream_verifier.py`
- Create: `tests/test_downstream_runner.py`

- [ ] RED: distinguish domain, version, history, business, and delivery no-op verdicts.
- [ ] RED: detect rejected partial mutation, stale mutation, duplicate replay, delivery/business conflation, authority loss, and undeclared allowed changes.
- [ ] RED: reject active superseded transition sentinels and verify terminal stop behavior.
- [ ] GREEN: implement generic result semantics, invariant hooks, evidence records, and aggregate sequence verdicts.
- [ ] REFACTOR: retain component-level failure evidence and never let adapter self-verdict override the contract.

### Task 4: Compile concrete downstream bundles

**Files:**
- Create: `skills/joewrks-product-definition/downstream/products/*.json`
- Create: `skills/joewrks-product-definition/downstream/compile_contract.py`
- Create: `tests/test_downstream_product_bundles.py`

- [ ] RED: verify every material clause has an exact current stable ID + JSON Pointer/hash.
- [ ] RED: verify action/lifecycle semantics compile for frozen A, frozen B, and revision 44 without invented authority.
- [ ] GREEN: add provenance-pinned product adapters and deterministic compiled bundle generation.
- [ ] REFACTOR: document explicit not-applicable fields and current/superseded separation.

### Task 5: Execute frozen external runtimes

**Files:**
- Create: `skills/joewrks-product-definition/downstream/adapters/node_a_adapter.mjs`
- Create: `skills/joewrks-product-definition/downstream/adapters/vitest_b_adapter.test.ts`
- Create: `skills/joewrks-product-definition/downstream/run_frozen_regressions.py`
- Create: `tests/test_downstream_frozen_regressions.py`

- [ ] RED: make adapter conformance tests fail before runtime adapters exist.
- [ ] GREEN: execute pinned A public JavaScript via Node without source changes.
- [ ] GREEN: execute pinned B TypeScript engine/selectors through an external runner and frozen toolchain without source changes.
- [ ] Verify B030 rejected partial mutation is detected.
- [ ] Verify B031 sentinels become actual JavaScript `NaN`/`Infinity` before engine submission and are detected.
- [ ] Execute/report A UI-to-domain disconnect plus applicable stale, replay, delivery, historical, and terminal sequences.

### Task 6: Integrate handoff and audit procedure

**Files:**
- Modify: `skills/joewrks-product-definition/references/figma-make-handoff.md`
- Modify: `skills/joewrks-product-definition/templates/figma-make-handoff.md`
- Create: `skills/joewrks-product-definition/downstream/README.md`
- Create: `skills/joewrks-product-definition/downstream/references/drift-audit-procedure.md`
- Modify/Create tests under `tests/`.

- [ ] RED: prove current handoff cannot identify executable bundle/hash/runner obligations.
- [ ] GREEN: add a compact downstream bundle section while preserving human-readable prose.
- [ ] Add blind-audit evidence chain and non-authoritative evidence exclusions.
- [ ] Validate the existing skill package and downstream instructions.

### Task 7: Freeze evaluation evidence

**Files:** Create all required files under `evals/downstream-conformance-v0.4.1/`.

- [ ] Record exact source/evidence pins, commands, actual sequence results, contract hashes, and adapter identities.
- [ ] Separate harness PASS from expected frozen implementation NONCONFORMANT verdicts.
- [ ] Record revision 44 expressiveness without issuing a new Make verdict.
- [ ] Include exact limitations and no responsive claim.

### Task 8: Verify and publish branch only

**Files:** No further product semantics.

- [ ] Run all new unit/integration tests and the original 43-test baseline.
- [ ] Run state/Closure validators and Python compilation checks.
- [ ] Compare every protected blob and canonical state against `16fc6ed…`.
- [ ] Confirm frozen source worktrees/trees are unchanged.
- [ ] Inspect staged scope and commit `feat: add executable downstream conformance harness v0.4.1`.
- [ ] Push only `feat/v0.4.1-downstream-conformance` and read back remote commit/tree/files.
