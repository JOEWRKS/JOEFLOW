# Core Semantic Closure V2 — Design Freeze Manifest

**Status:** `DESIGN_FROZEN`

**Frozen on:** `2026-08-28`

**State contract target:** `0.2.0`

**Program:** `JOEWRKS Product Definition System`

## Authority

This manifest records final approval of the Core Semantic Closure V2 architecture and supersedes the earlier `WRITTEN_SPEC_PENDING_FINAL_USER_REVIEW` header in the design document. The design is frozen for implementation planning; changing any normative rule below requires an explicit design revision rather than silent implementation drift.

The frozen normative specification set is:

1. `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md`
   - Git blob: `e7c10a7e3dfada1408f46b1f5fb4fddcaa3de829`
2. `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-self-review.md`
   - approved clarification content blob at freeze: `11d388839c2a19684b5152b43a95f660d0f6d73f`
3. `README.md`
   - human-facing explanation baseline blob: `1dd3d35293878eb5c1dc7e74d4ab26fe200bc24b`

If wording in the human-facing README conflicts with the technical normative specification, the normative specification set controls implementation behavior. The README must remain simpler, not redefine the contract.

## Frozen product definition

The primary user-facing explanation is:

> **AI가 중요한 걸 빠뜨리거나 제멋대로 결정하지 않게 해주는 제품 기획·검증 도구입니다.**

The user-facing workflow is:

> **빠진 걸 찾고 → 애매한 걸 정하고 → 정한 대로 만들게 하고 → 제대로 만들었는지 확인한다.**

The core rule is:

> **AI가 알아서 만들게 하되, 중요한 건 멋대로 정하지 못하게 한다.**

Internally this is implemented as `DISCOVER → CLOSE → FREEZE → CONSTRAIN → VERIFY`, with material ambiguity re-entering Product Definition.

## Frozen architecture decisions

- Exactly one canonical Product Definition authority remains: `product-definition/<project-slug>/state.json`.
- V2 state contract identity is `schema_version: 0.2.0`; legacy `0.1.2.1` remains a distinct frozen contract.
- Migration is deterministic and may expose uncertainty but may never manufacture authority or auto-upgrade legacy Closure to V2 Semantic Closure.
- Product surface, evidence, contradictions, unknown resolution, materiality, coverage bindings, discovery commitments, and approval become traceable parts of the canonical authority model.
- Grill behavior is internally broad and externally selective; evidence-resolvable issues are not unnecessarily asked of the user.
- Material/high-risk product decisions cannot be silently made inside the AI-autonomous implementation boundary.
- `COVERED` becomes an exact authority-bound proof; `OPEN` requires unknowns; `N/A` requires rationale plus basis authority.
- Product Definition approval becomes informed through a deterministic Approval Manifest and semantic definition digest.
- Existing implementation is evidence of implementation, not automatic evidence of intended product meaning.
- Semantic Review is a last-line assurance mechanism and may not hide an upstream `SEMANTIC_AUTHORITY_GAP`.
- V2 downstream identities are new contracts; v1 downstream and frozen v0.4.3 evidence are not redefined.
- Semantic Review 2.0 reliability, if introduced, begins at `NOT_MEASURED` and requires its own valid calibration.

## Approved self-review clarifications

### Semantic digest boundary

Downstream V2 semantic validity is bound to the approved semantic definition digest plus exact consumed source/binding commitments. The whole `state.json` file hash may be recorded as provenance but is not, by itself, the semantic-staleness authority. Unconsumed evidence may change without invalidating unchanged approved product meaning.

### Migration-generated IDs

Generated reconciliation IDs preserve legacy IDs and allocate per prefix from the greatest existing numeric suffix plus one, in canonical source-path order. The same source bytes and migrator version must generate the same IDs and canonical migrated bytes.

## Frozen remediation scope

All ten architectural remediation items remain in scope:

- `R1` Coverage → Authority Binding
- `R2` Definition Surface Manifest
- `R3` First-class Evidence
- `R4` Decision Integrity
- `R5` Materiality + Autonomy
- `R6` Reverse Bootstrap
- `R7` Informed Approval
- `R8` Adaptive Grill Packs
- `R9` Semantic Debt Reduction
- `R10` Lifecycle / Migration

## Frozen implementation order

Implementation is gated in this order:

1. `M1` State 0.2 Foundation
2. `M2` Discover Authority
3. `M3` Grill Engine V2
4. `M4` Semantic Freeze
5. `M5` Downstream V2
6. `M6` Integration and Adoption

Intermediate milestones must use precise partial status and must not claim `Core V2 complete`. Full completion is permitted only after the M6 integration gate passes.

## M0 result

`M0 — DESIGN FREEZE: PASS`

Implementation planning may proceed. No production implementation is authorized to change the frozen architecture implicitly; any discovered architectural contradiction must stop the affected work and return to design review.
