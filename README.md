# JOEWRKS Product Definition System

**JOEWRKS Product Definition System** is a runtime-independent product-definition and downstream-verification system for closing product/UX ambiguity before implementation, preserving canonical authority, compiling implementation obligations, detecting drift, and evaluating semantic-review reliability.

The existing runtime skill/package identifier remains **`joewrks-product-definition`**.

See [`PROGRAM_ARCHITECTURE.md`](PROGRAM_ARCHITECTURE.md) for the official program name, four-layer system structure, authority flow, repository mapping, version progression, and current v0.4.3 boundary.

## System layers

1. **Product Definition Core** — evidence-first interrogation, unknown/decision ledgers, canonical `state.json`, Product/UX compilation, stale/ripple propagation, deterministic Closure Gate.
2. **Downstream Conformance** — executable `joewrks.action-conformance/1.0`, provenance/derivation binding, implementation/Figma handoff obligations, runtime sequence verification, drift evidence.
3. **Semantic Review** — `joewrks.semantic-review/1.0`, responsibility profile, semantic obligations, reviewer packages, deterministic goldens, reliability gate.
4. **Evaluation & Calibration Harness** — behavioral/dogfood evaluation, official calibration controller, calibration control plane, frozen raw evidence, reliability metrics, isolated-reviewer boundary.

## Current development boundary

Current integrated development line: **v0.4.3**.

Current frozen status:

- v0.4.3 specification: `VERIFIED`
- semantic-review implementation: `VERIFIED`
- repaired calibration control plane: `VERIFIED_AFTER_RUN_01_REPAIR`
- real reviewer reliability: `NOT_MEASURED`
- valid real calibration runs: `0`
- current blocker: `MANIFEST_ONLY_ISOLATION_UNAVAILABLE`
- v0.4.4: `BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION`

The current protected `main` baseline remains `efd96410f6401cbf9624328e94b795c315164b7f`. The repaired v0.4.3 calibration input is `748254d6def81080a2fd2736115a3ab5e0bde5a3`; the environment-blocked calibration disposition is `6a0674c5d00a40790afef78cfa19494314b894e3`.

## Product Definition authority

Authoritative project state lives in:

```text
product-definition/<project-slug>/state.json
```

Markdown PRDs, plans, wireflows, handoffs, and summaries are human-readable projections and must not replace `state.json` as authority.

The skill entrypoint is [`skills/joewrks-product-definition/SKILL.md`](skills/joewrks-product-definition/SKILL.md). Install or copy that entire directory into a Codex-compatible skills directory.

## What it provides

- Evidence-first interrogation and unknown/decision ledgers
- Stable Product Definition identifiers and ripple/stale propagation
- Product, flow, screen/state, implementation, and Figma Make handoff templates
- Dependency-free Python validators for state integrity and Closure readiness
- Executable downstream conformance contracts and runtime verification
- Hash-bound provenance and semantic derivation controls
- Deterministic semantic-review packages, responsibility rules, goldens, and reliability gates
- Frozen evaluation/calibration evidence with explicit PASS/FAIL/NOT-MEASURED boundaries

## Validate

```bash
python -m unittest discover -s tests -v
python /absolute/path/to/joewrks-product-definition/scripts/validate_state.py path/to/state.json
python /absolute/path/to/joewrks-product-definition/scripts/validate_closure.py path/to/state.json
```

The core validators use only the Python standard library.

## Evaluation boundary

Deterministic implementation and calibration-control logic are covered by repository tests and frozen evidence. A valid real v0.4.3 reviewer-reliability calibration remains intentionally unclaimed until reviewer contexts can be isolated by the execution environment so they can access only their assigned package, run envelope, and invocation wrapper.
