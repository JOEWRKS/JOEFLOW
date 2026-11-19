# JOEWRKS Product Definition Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify the `joewrks-product-definition` Agent Skill described by the approved implementation specification.

**Architecture:** A lean skill entrypoint routes to focused references and reusable templates. Two dependency-free Python validators treat project `state.json` as authority and produce deterministic diagnostics suitable for both Codex-only and ChatGPT-to-Codex handoffs.

**Tech Stack:** Markdown, YAML, Python 3 standard library, `unittest`

**Spec:** `docs/superpowers/specs/2026-08-20-joewrks-product-definition-design.md`

## Global Constraints

- Persist all authoritative decision state in files; never rely on chat history or memory.
- Do not silently invent material decisions.
- Preserve stable IDs and propagate changed decisions to `STALE` downstream artifacts.
- Closure requires every configured counter to be zero and explicit user approval.
- Add no mandatory external dependency.

---

### Task 1: Executable State Contract

**Files:**
- Create: `tests/test_validators.py`
- Create: `skills/joewrks-product-definition/scripts/state_validation.py`
- Create: `skills/joewrks-product-definition/scripts/validate_state.py`
- Create: `skills/joewrks-product-definition/scripts/validate_closure.py`

**Interfaces:**
- Consumes: a path to `state.json`
- Produces: JSON `{validator, valid|closed, errors, metrics}` and exit code `0` on success, `1` on validation failure, `2` on invocation/read errors

- [ ] Write `unittest` cases using temporary state files for valid state, duplicate IDs, broken references, invalid statuses, dependency cycles, closure blockers, stale artifacts, gaps, missing mappings, and successful closure.
- [ ] Run `python -m unittest discover -s tests -v`; verify RED because validator scripts do not exist.
- [ ] Implement shared parsing, ID traversal, reference validation, graph-cycle detection, metrics, and deterministic CLI output with only the Python standard library.
- [ ] Re-run the validator suite and keep it GREEN.

### Task 2: Skill Package and Artifact Compiler Guidance

**Files:**
- Create: `skills/joewrks-product-definition/SKILL.md`
- Create: `skills/joewrks-product-definition/agents/openai.yaml`
- Create: `skills/joewrks-product-definition/references/*.md`
- Create: `skills/joewrks-product-definition/templates/*.md`

**Interfaces:**
- Consumes: repository evidence and user decisions
- Produces: `product-definition/<project-slug>/` artifacts and authoritative `state.json`

- [ ] Add package-contract tests that exercise generated sample state and validators rather than matching prose.
- [ ] Verify the new package tests fail because the package and templates are absent.
- [ ] Create the lean orchestrator, focused references, and complete templates required by the approved specification.
- [ ] Run all tests and the bundled skill `quick_validate.py` validator.

### Task 3: Evaluation and Integration Verification

**Files:**
- Create: `evals/scenarios.md`
- Create: `evals/baseline-results.md`
- Create: `evals/skill-enabled-results.md`
- Create: `tests/fixtures/*.json`

**Interfaces:**
- Consumes: the six approved evaluation scenarios and package outputs
- Produces: reproducible evidence of baseline gaps, expected skill behavior, decision ripple handling, closure failures, and Figma-less fallback

- [ ] Record the baseline control boundary and observable gaps without representing an unexecuted agent run as observed evidence.
- [ ] Add fixtures for open, closed, stale, and broken-reference states and verify each validator outcome.
- [ ] Check skill discovery metadata, non-target trigger boundaries, required handoff contracts, and no external imports.
- [ ] Run the complete regression suite, inspect final artifacts, and record exact commands/results.
