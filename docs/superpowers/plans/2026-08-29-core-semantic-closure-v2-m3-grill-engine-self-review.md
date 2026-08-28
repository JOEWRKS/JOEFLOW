# Core Semantic Closure V2 — M3 Plan Self-Review Clarifications

**Status:** `NORMATIVE_PLAN_CLARIFICATION`

**Applies to:** `docs/superpowers/plans/2026-08-29-core-semantic-closure-v2-m3-grill-engine.md`

Where this addendum conflicts with the M3 plan, this addendum controls. The frozen Core Semantic Closure V2 design remains the higher authority.

## 1. Strict NON_MATERIAL means agent-autonomous by default

The main plan added an extra `user_visible=false` condition before `AGENT_AUTONOMOUS`. That is stricter than the frozen autonomy principle and would unnecessarily interrupt the user for low-impact reversible choices.

M3 already defines `NON_MATERIAL` conservatively. It is possible only when:

```text
outcome_divergence ∈ {NONE, LOW}
fan_out = LOCAL
reversibility = TRIVIALLY_REVERSIBLE
all risk_flags = false
```

Therefore freeze the authority derivation order as:

```text
1. qualifying evidence for required_authority_class → EVIDENCE_RESOLVABLE
2. required class FACTUAL / CONSTRAINT / BEHAVIORAL with no qualifying evidence → EXTERNAL_AUTHORITY_REQUIRED
3. materiality = NON_MATERIAL → AGENT_AUTONOMOUS
4. MATERIAL + high risk → USER_DECISION_REQUIRED
5. MATERIAL + confirmation-ready recommendation → USER_CONFIRMATION
6. otherwise → USER_DECISION_REQUIRED
```

`user_visible` remains an auditable Materiality factor and may inform recommendations, but it does not by itself revoke autonomy after the record has passed the strict NON_MATERIAL classifier.

Update Task-3 tests accordingly:

- non-material + user-visible + otherwise valid strict profile → `AGENT_AUTONOMOUS`;
- no non-material record may contain medium/high divergence, non-local fan-out, non-trivial reversibility, or any risk flag.

This preserves the product rule: internally exhaustive, externally selective.

## 2. Optional topology tags are not sufficient authority for Grill Pack activation

The main plan proposed optional `surface.topology_tags`. That leaves an escape hatch: an agent could fail to tag AUTH or FILE_UPLOAD and thereby suppress a required pack.

Do **not** use optional topology tags as the canonical activation authority.

Instead, extend `surface_manifest` in M3 to require a complete six-domain Grill Topology Profile:

```json
{
  "records": [],
  "grill_profile": {
    "AUTH": {},
    "MONEY": {},
    "FILE_UPLOAD": {},
    "ASYNC": {},
    "PERMISSION": {},
    "DESTRUCTIVE_ACTION": {}
  }
}
```

Each profile cell has this exact shape:

```json
{
  "status": "ACTIVE | N/A | OPEN",
  "surface_refs": [],
  "unknown_refs": [],
  "basis_refs": [],
  "rationale": null
}
```

### ACTIVE

Requires:

- at least one current `SURF-*` in `surface_refs`;
- `unknown_refs = []`;
- `rationale = null`.

The profile is the explicit discovery classification saying that topology exists. Specialist pack instances target the listed surfaces.

### N/A

Requires:

- `surface_refs = []`;
- `unknown_refs = []`;
- meaningful `rationale`;
- at least one current `basis_ref` to evidence, decision, or discovered-surface authority establishing why the domain does not apply.

A bare `N/A` cannot suppress a pack.

### OPEN

Requires:

- at least one current/open `UNK-*` in `unknown_refs`;
- `rationale = null`.

Each topology OPEN unknown uses origin:

```json
{
  "kind": "GRILL_TOPOLOGY",
  "surface_ref": null,
  "pack_id": "GRILL-AUTH-1",
  "axis_id": null,
  "source_path": null
}
```

### Forced topology from existing surface kinds

These M2 surface kinds make the corresponding profile cell **necessarily ACTIVE** and require those surfaces to appear in `surface_refs`:

```text
MONEY_FLOW            → MONEY
ASYNC_PROCESS          → ASYNC
PERMISSION             → PERMISSION
DESTRUCTIVE_OPERATION  → DESTRUCTIVE_ACTION
```

A profile claiming `N/A` or `OPEN` while such a current surface exists fails `grill_topology_contradiction`.

AUTH and FILE_UPLOAD have no unique M2 surface kind, so discovery must explicitly classify their profile as ACTIVE, N/A with basis, or OPEN with an unknown. The category can never be silently omitted.

Pack activation is compiled from `grill_profile.ACTIVE`, not from optional tags.

Consequences for the main plan:

- remove the proposed required `surface.topology_tags` field;
- add `surface_manifest.grill_profile` instead;
- add profile validation to `grill_v2.py`;
- `active_grill_pack_gaps` includes OPEN/invalid/missing profile classifications;
- `active_grill_packs_complete` may be true only when all six profile cells are validly ACTIVE or N/A and every ACTIVE pack instance is instantiated with matching axis inventory/identity;
- OPEN profile cells keep completeness false even before specialist axis coverage is considered.

Add RED tests proving a complete profile is mandatory and that no specialist pack can be suppressed by omission.

## 3. Unknown origin must preserve migration source provenance

The main plan's `origin` shape loses the canonical reconciliation path for `MIGRATION_RECONCILIATION` unknowns.

Freeze the origin shape with five keys:

```json
{
  "kind": "PRODUCT_SURFACE | GRILL_TOPOLOGY | GRILL_PACK_AXIS | MIGRATION_RECONCILIATION | MANUAL",
  "surface_ref": null,
  "pack_id": null,
  "axis_id": null,
  "source_path": null
}
```

Rules:

- `PRODUCT_SURFACE`: current `SURF-*` required; pack/axis/source_path null.
- `GRILL_TOPOLOGY`: valid specialist `pack_id` required; surface/axis/source_path null.
- `GRILL_PACK_AXIS`: current `SURF-*`, valid specialist `pack_id`, and valid axis ID required; source_path null.
- `MIGRATION_RECONCILIATION`: non-empty canonical `source_path` required; surface/pack/axis null.
- `MANUAL`: all locator fields null.

This preserves the deterministic M1 migration-planner path when M6 later materializes reconciliation unknowns.

## 4. Reference integrity for M3 unknown fields is mandatory

Task 2 must explicitly validate:

- `affects` refs exist as stable canonical IDs;
- `blocks_unknown_refs` resolve to distinct current/open `UNK-*` records and never self-reference;
- `evidence_refs` resolve to `EVD-*`;
- `resolved_by` resolve to `DEC-*`;
- all option IDs are unique within the unknown;
- recommendation reasoning refs resolve to existing current records permitted by the recommendation contract.

Cycle detection is required for `blocks_unknown_refs`; an unknown-unlock cycle is invalid because it makes deterministic question priority incoherent. Emit `unknown_dependency_cycle`.

## 5. Grill Topology/Pack metric semantics

Freeze the new metrics so implementation and later audits use one meaning:

```text
open_material_unknowns
  = OPEN unknowns whose recomputed Materiality is MATERIAL

missing_required_user_decisions
  = OPEN unknowns whose derived authority is USER_CONFIRMATION or USER_DECISION_REQUIRED

unresolved_unknown_provenance
  = RESOLVED unknowns whose declared resolution is not backed by the required evidence/decision/constraint authority

invalid_resolution_authority
  = unknown/decision records whose resolution mode or declared decision authority conflicts with deterministic policy

unauthorized_agent_decisions
  = agent decisions that are not AGENT_NON_MATERIAL_DEFAULT over a NON_MATERIAL / AGENT_AUTONOMOUS source unknown

active_grill_pack_gaps
  = invalid/missing/OPEN topology-profile cells + missing/mismatched pack identities/rows/axis inventories

unresolved_pack_axes
  = Core Grill cells with status OPEN + specialist Grill axes with status OPEN

umbrella_unknown_compression
  = reuse/mismatch of an origin unknown across specialist axes marked independent_decision=true

pack_materiality_floor_violations
  = OPEN specialist axes with MATERIAL floor whose origin unknown is not recomputed MATERIAL
```

These metrics may overlap intentionally; they expose different failure meanings.

## 6. Baseline completeness after the topology-profile correction

M3 baseline `active_grill_packs` is compiled from the mandatory Grill Topology Profile plus the always-present Core Pack.

`active_grill_packs_complete=true` requires:

1. all six specialist profile cells validly classified ACTIVE or N/A;
2. no specialist profile cell OPEN;
3. Core Pack identity valid;
4. each ACTIVE specialist pack identity/version/digest valid;
5. every required pack instance/axis inventory instantiated;
6. no `active_grill_pack_gaps`.

It does **not** require `unresolved_pack_axes == 0`; that remains a separate metric.

`unknown_unknown_exhaustiveness_claimed` remains hard-coded false.

## Self-review result

With these clarifications, the M3 design has no remaining known blocking plan contradiction. Execution must read the frozen design, M2 audit, M3 plan, and this addendum before coding.