# joewrks-product-definition

Runtime-independent Agent Skill for closing product and UX decisions before implementation.

Current contract: **v0.1.1 Closure Hardening**.

## What it provides

- Evidence-first interrogation and unknown/decision ledgers
- Stable product-definition identifiers and ripple/stale propagation
- Product, flow, screen/state, implementation, and Figma Make handoff templates
- Dependency-free Python validators for state integrity and closure readiness
- Deterministic fixtures and regression tests
- Canonical `schemas/state.schema.json`, `references/state-contract.md`, and `templates/state.example.json`

## Package

The skill entrypoint is [`skills/joewrks-product-definition/SKILL.md`](skills/joewrks-product-definition/SKILL.md). Install or copy that entire directory into a Codex-compatible skills directory.

Authoritative project state lives in `product-definition/<project-slug>/state.json`. Markdown artifacts are human-readable projections and must not replace the state file as authority.

## Validate

```bash
python -m unittest discover -s tests -v
python /absolute/path/to/joewrks-product-definition/scripts/validate_state.py path/to/state.json
python /absolute/path/to/joewrks-product-definition/scripts/validate_closure.py path/to/state.json
```

The validators use only the Python standard library.

## Evaluation boundary

Deterministic contracts are covered locally. Fresh-agent behavioral runs for the six scenarios and Figma-native generation remain separately documented in [`evals/skill-enabled-results.md`](evals/skill-enabled-results.md).
