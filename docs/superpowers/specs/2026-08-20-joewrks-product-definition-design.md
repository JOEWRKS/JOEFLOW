# JOEWRKS Product Definition Skill Design

## Outcome

Create `skills/joewrks-product-definition` as a runtime-independent Agent Skill that closes material product and UX decisions before implementation and persists every decision in project files rather than conversation memory.

## Architecture

- `SKILL.md` is a lean orchestrator: discover evidence, register and rank unknowns, ask decisions, propagate changes, compile artifacts, and enforce closure.
- Focused references hold interrogation, taxonomies, coverage, dependency, closure, and Figma Make rules.
- Markdown templates define human-readable projections. `state.json` remains the machine-readable authority in each consuming project.
- Two Python standard-library validators check structural integrity and closure readiness. They emit deterministic JSON and non-zero exit codes on failure.

## Contracts

- Stable IDs are never renumbered: `GOAL`, `USR`, `REQ`, `UNK`, `DEC`, `RULE`, `FLOW`, `SCR`, `STATE`, `DATA`, `INT`, `AC`, and `TASK`.
- Material unknowns cannot be silently assumed. Accepted recommendations use `ASSUMED_ACCEPTED`.
- A changed decision marks dependent artifacts `STALE`; any stale artifact blocks closure.
- Closure requires zero blocking unknowns, open material decisions, contradictions, stale artifacts, coverage gaps, and required orphan mappings, plus explicit user approval.
- Figma is optional. Without it, generate Markdown wireframes, Mermaid flows, screen specifications, build instructions, and a handoff marked `Figma visualization: NOT VERIFIED`.
- No mandatory external dependency is permitted.

## Deliverables

The package contains the entrypoint, `agents/openai.yaml`, nine focused references, seven artifact templates, two validators, validator tests, and evaluation scenarios/results. High-fidelity design, production implementation, deployment, cloud synchronization, and a standalone UI/CLI are excluded.

## Verification

Validation covers malformed state, duplicate and broken IDs, invalid status values, dependency graph integrity, blockers, coverage gaps, stale artifacts, contradictions, missing mappings, successful closure, Figma-less handoff instructions, skill metadata, and package discovery.
