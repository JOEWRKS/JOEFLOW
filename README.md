# JOEWRKS Product Definition System

> **Define the product before AI implements it — then verify the implementation still matches the definition.**

**JOEWRKS Product Definition System** is a runtime-independent product-definition and downstream-verification system for AI-assisted product development.

It helps an agent inspect evidence, close product and UX ambiguity before implementation, preserve approved decisions as canonical authority, compile implementation obligations, and detect downstream drift after code or design work begins.

The existing runtime skill/package identifier remains **`joewrks-product-definition`**.

See [`PROGRAM_ARCHITECTURE.md`](PROGRAM_ARCHITECTURE.md) for the detailed four-layer architecture, authority flow, repository mapping, version progression, and the current v0.4.3 boundary.

---

## What this system is for

Use this system when an AI agent is expected to build or modify a product, website, app, workflow, or redesign and the request still contains material ambiguity.

Instead of allowing the implementation agent to silently decide missing product behavior, the system makes those decisions explicit first and records them in a canonical Product Definition state.

Typical use cases include:

- new websites and web apps;
- redesigns and information-architecture changes;
- existing products whose current code contains undocumented product decisions;
- multi-screen UX flows;
- products with permissions, failure states, validation, recovery, or state transitions;
- Figma / Figma Make handoff preparation;
- implementation drift checks after Codex or another implementation agent changes the product.

The system is not merely a PRD generator. It is an **authority + handoff + verification workflow**.

---

## Responsibility boundary

### What JOEWRKS Product Definition System owns

The system can own or govern:

- product goal and success criteria;
- target users and usage context;
- scope / non-scope;
- information architecture and route structure;
- requirements and business rules;
- content and data requirements;
- user flows;
- screen definitions;
- UI / UX states;
- loading, empty, validation, error, permission, and recovery behavior;
- responsive behavior requirements;
- accessibility requirements;
- acceptance criteria;
- stable requirement / flow / screen / state identifiers;
- dependency and stale-state propagation after product decisions change;
- Product Definition Closure;
- implementation handoff obligations;
- deterministic downstream-conformance checks;
- implementation / Figma drift evidence;
- semantic-review inputs and reliability evaluation infrastructure.

### What it does not replace

The system does **not** replace:

- the implementation agent that writes production code;
- a designer's final art-direction judgment;
- visual taste decisions such as exact composition quality, image crop taste, or whether one font size simply looks better than another;
- deployment infrastructure and production operations;
- security review, legal review, or domain-specific professional approval.

In an AI-assisted workflow, the intended split is:

```text
JOEWRKS Product Definition System
        ↓
defines product + UX authority
        ↓
Codex / implementation agent
        ↓
implements the approved definition
        ↓
JOEWRKS downstream verification
        ↓
checks for drift and conformance
```

If implementation exposes a material ambiguity, the decision should return to Product Definition instead of being silently invented inside the code task.

---

## System layers

1. **Product Definition Core** — evidence-first interrogation, unknown/decision ledgers, canonical `state.json`, Product/UX compilation, stale/ripple propagation, deterministic Closure Gate.
2. **Downstream Conformance** — executable `joewrks.action-conformance/1.0`, provenance/derivation binding, implementation/Figma handoff obligations, runtime sequence verification, drift evidence.
3. **Semantic Review** — `joewrks.semantic-review/1.0`, responsibility profile, semantic obligations, reviewer packages, deterministic goldens, reliability gate.
4. **Evaluation & Calibration Harness** — behavioral/dogfood evaluation, official calibration controller, calibration control plane, frozen raw evidence, reliability metrics, isolated-reviewer boundary.

Detailed architecture: [`PROGRAM_ARCHITECTURE.md`](PROGRAM_ARCHITECTURE.md)

---

## Installation

There is currently **no dedicated installer, package manager command, or published plugin package** for this repository. Do not assume an installer exists.

The supported repository form is a standard Agent Skill directory with its supporting references, templates, schemas, scripts, and downstream modules.

### 1. Clone or download the repository

```bash
git clone https://github.com/JOEWRKS/joewrks-product-definition.git
cd joewrks-product-definition
```

If you use a specific branch or frozen commit, check it out explicitly before installing the skill.

### 2. Install the entire skill directory

Install or copy this directory as one unit into the Skills location supported by your Codex / agent environment:

```text
skills/joewrks-product-definition/
```

Do **not** copy only `SKILL.md`.

The skill depends on relative supporting files under:

```text
skills/joewrks-product-definition/
├─ SKILL.md
├─ references/
├─ schemas/
├─ templates/
├─ scripts/
└─ downstream/
```

The exact Skills installation path depends on the host environment. Use that environment's supported Skills installation/import mechanism and preserve the directory structure above.

The runtime skill ID is:

```text
joewrks-product-definition
```

### 3. Confirm the skill entrypoint

The entrypoint is:

```text
skills/joewrks-product-definition/SKILL.md
```

The agent should be able to load the skill by its name or automatically select it when the task matches its description.

### 4. Optional repository validation

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The Product Definition validators themselves use only the Python standard library.

---

## Canonical project authority

Every project managed by the system should have one canonical state file:

```text
product-definition/<project-slug>/state.json
```

That file is the source of truth for Product Definition.

Generated Markdown PRDs, plans, wireflows, handoffs, summaries, or implementation notes are projections of that state. They do not replace `state.json` as authority.

Example:

```text
my-site/
├─ src/
├─ public/
└─ product-definition/
   └─ my-site/
      ├─ state.json
      └─ generated projections...
```

---

## Quick start — new product or website

Use the skill before implementation starts.

Example instruction to Codex:

```text
Use joewrks-product-definition for this project.

Define this website before implementation.
Inspect all available evidence first.
Create product-definition/<project-slug>/state.json as canonical authority.
Register material unknowns instead of inventing decisions.
Resolve the highest-impact unknowns with me one at a time.
Do not begin implementation until Product Definition Closure passes and I approve the current definition revision.
```

Expected workflow:

```text
Idea / request
→ evidence discovery
→ bootstrap state.json
→ unknown discovery
→ explicit decisions
→ requirements / flows / screens / states
→ dependency propagation
→ Closure Gate
→ explicit approval
→ implementation handoff
```

---

## Quick start — existing site or app

For an already-implemented product, use **reverse Product Definition** first.

Do not immediately rewrite the site.

Example instruction:

```text
Use joewrks-product-definition for this existing site.

Do not modify implementation yet.
Inspect the current repository as evidence.
Reverse-bootstrap Product Definition from the existing routes, components, behavior, content, docs, tests, schemas, and current UX.

Separate:
1. explicit product decisions,
2. implementation assumptions,
3. contradictions,
4. unresolved material decisions.

Create product-definition/<project-slug>/state.json.
Register unresolved material decisions as unknowns.
Do not treat a behavior as intentional product authority merely because it already exists in code.
```

This is useful when Codex or another agent has already created a site and you need to determine which parts were intentional versus silently invented during implementation.

---

## Typical end-to-end workflow with Codex

```text
1. Inspect evidence
2. Bootstrap canonical Product Definition
3. Register unknowns
4. Resolve product decisions
5. Compile requirements / flows / screens / states
6. Run Closure Gate
7. Human approves the current definition revision
8. Generate implementation handoff
9. Codex implements
10. Material ambiguity discovered? → return to Product Definition
11. Implementation completes
12. Compare Definition / Design / Code
13. Record and fix drift
14. Validate acceptance criteria
15. Final completion decision
```

A typical authority flow is:

```text
Evidence
   ↓
Product Definition Core
   ↓
canonical state.json
   ↓
Closure Gate
   ↓
implementation / Figma handoff
   ↓
Codex implementation
   ↓
downstream conformance + drift audit
   ↓
acceptance
```

---

## Product Definition Core

The Product Definition Core converts incomplete product requests into explicit, reviewable authority.

Its key rules are:

- inspect available evidence before asking the user;
- never silently invent a material product decision;
- create one independently answerable unknown per material unresolved decision;
- keep stable IDs permanently;
- propagate every material change to affected downstream objects;
- mark affected projections stale before recompilation;
- require deterministic validation plus explicit approval for Closure.

The skill entrypoint is [`skills/joewrks-product-definition/SKILL.md`](skills/joewrks-product-definition/SKILL.md).

---

## Downstream Conformance

After Product Definition Closure, approved canonical clauses can be compiled into executable implementation obligations.

The production downstream contract is:

```text
joewrks.action-conformance/1.0
```

This layer is useful for product behavior where correctness matters beyond static page structure, for example:

- account and permission flows;
- forms and validation;
- state-changing actions;
- save / delete / submit behavior;
- checkout or booking flows;
- external API effects;
- retries and failure recovery;
- authoritative business-state transitions.

For ordinary presentational sections such as a hero, image gallery, editorial section, or footer, full action-conformance may be unnecessary. Use it where semantic state and behavior justify the additional verification cost.

See [`skills/joewrks-product-definition/downstream/README.md`](skills/joewrks-product-definition/downstream/README.md).

---

## Design and Figma boundary

The system can define and freeze design requirements such as:

- screen purpose;
- visual hierarchy;
- information priority;
- responsive composition requirements;
- component states;
- interaction behavior;
- accessibility constraints;
- stable screen IDs and implementation mappings.

It does not claim deterministic proof of pure visual taste.

When a design is explicitly approved, that approved design can become downstream visual authority and implementation drift can then be checked against it.

If Figma is unavailable, the skill can still produce Markdown / Mermaid handoff artifacts and mark visualization as not verified.

---

## Validation

Validate canonical Product Definition state:

```bash
python /absolute/path/to/joewrks-product-definition/scripts/validate_state.py path/to/state.json
```

Validate Closure readiness:

```bash
python /absolute/path/to/joewrks-product-definition/scripts/validate_closure.py path/to/state.json
```

Run repository tests:

```bash
python -m unittest discover -s tests -v
```

Resolve script paths from the installed skill directory, not from the consumer project's current working directory.

---

## Current v0.4.3 boundary

Current integrated development line: **v0.4.3**.

Current frozen status:

| Boundary | Status |
| --- | --- |
| v0.4.3 specification | `VERIFIED` |
| semantic-review implementation | `VERIFIED` |
| repaired calibration control plane | `VERIFIED_AFTER_RUN_01_REPAIR` |
| Run-01 | `INVALID / CONTROL_PLANE_DEFECT` |
| valid real calibration runs | `0` |
| real reviewer reliability | `NOT_MEASURED` |
| calibration PASS | `NOT_CLAIMED` |
| calibration FAIL | `NOT_CLAIMED` |
| current blocker | `MANIFEST_ONLY_ISOLATION_UNAVAILABLE` |
| v0.4.4 | `BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION` |

The current protected `main` baseline remains:

```text
efd96410f6401cbf9624328e94b795c315164b7f
```

The repaired v0.4.3 calibration input is:

```text
748254d6def81080a2fd2736115a3ab5e0bde5a3
```

The environment-blocked calibration disposition is:

```text
6a0674c5d00a40790afef78cfa19494314b894e3
```

A valid real v0.4.3 semantic-review reliability calibration remains intentionally unclaimed until each reviewer can be isolated by the execution environment so that it can access only its assigned package, run envelope, and invocation wrapper.

Therefore the deterministic Product Definition, Closure, handoff, downstream-conformance, and drift-audit layers may be used according to their validated contracts, while real semantic-review reliability must not be represented as calibrated production evidence yet.

---

## Repository structure

```text
skills/joewrks-product-definition/
├─ SKILL.md
├─ references/
├─ schemas/
├─ templates/
├─ scripts/
└─ downstream/
   └─ semantic_review/

evals/
├─ behavioral-v0.2/
├─ downstream-conformance-v0.4*/
└─ semantic-review-v0.4.3/

tests/
└─ fixtures/semantic-review-v1/
```

For the full architecture and version history, read [`PROGRAM_ARCHITECTURE.md`](PROGRAM_ARCHITECTURE.md).
