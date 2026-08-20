# RERUN-EVAL-04-TREATMENT observable record

## Scope

- Skill used: `joewrks-product-definition`
- Authoritative state: `D:/JOEWRKS/JOEWRKS-Product/evals/behavioral-v0.2/run-state/rerun-eval-04-treatment/product-definition/rerun-eval-04-treatment/state.json`
- Only product evidence read: `D:/JOEWRKS/JOEWRKS-Product/evals/behavioral-v0.2/fixtures/decision-change/initial-definition.md`
- Change evidence: User said, “아까 게스트도 편집 가능하게 하자고 했는데, 생각 바뀌었어. 게스트는 읽기만 가능하게 바꿔.”
- No source implementation files were changed.

## Authoritative baseline created

The fixture was compiled into a unique revision 7 state with the supplied approved guest-edit policy and dependencies:

- `DEC-004`: Guests may edit shared documents.
- `REQ-006`: Valid-link guests can edit document content.
- `RULE-003`: Guest sessions grant read and edit permission.
- `FLOW-005`: Guest opens, edits, and saves.
- `SCR-004`: Guest editing controls are exposed.
- `AC-009`: Guest edits persist and appear in history.
- `TASK-011`: Implement the guest edit mutation and editor controls.

Baseline structure validation result:

```json
{"validator":"state","valid":true,"errors":[]}
```

Baseline closure validation result:

```json
{"validator":"closure","closed":true,"definition_digest":"748abd932288d3f93f5082c4b03913720a77bb9b39b0f9c1a63a6addda619eed","errors":[],"metrics":{"blocking_unknowns":0,"contradictions":0,"coverage_gaps":0,"invalid_closed_status":0,"minimum_definition_gaps":0,"missing_acceptance_criterion":0,"missing_active_goal":0,"missing_material_requirement":0,"missing_user_approval":0,"open_material_decisions":0,"orphan_acceptance_criteria":0,"orphan_requirements":0,"orphan_screens":0,"screen_action_gaps":0,"screen_state_gaps":0,"stale_approval":0,"stale_artifacts":0,"stale_user_approval":0,"unmapped_implementation_tasks":0}}
```

## Material revision and approval invalidation

The explicit policy reversal was recorded as a material change:

1. `definition_revision` advanced from 7 to 8.
2. Project approval was cleared: `user_approved=false`; revision, digest, and timestamp are `null`.
3. `DEC-004` was preserved as `SUPERSEDED` and linked to new stable ID `DEC-005`.
4. `DEC-005` records the user-answer evidence: guests have read-only access.

## Dependency ripple and stale-before-recompile record

Traversal followed `DEC → REQ/RULE → FLOW/SCR → AC/TASK`. Before projection edits, the following active dependents were marked `STALE`:

`REQ-006`, `RULE-003`, `FLOW-005`, `SCR-004`, `AC-009`, `TASK-011`.

They were then checked against `DEC-005`, recompiled, and returned to `CURRENT`:

- `REQ-006`: Valid-link guests can read but cannot edit.
- `RULE-003`: Guest sessions grant read permission and deny edit permission.
- `FLOW-005`: Guest opens and reads; no edit/save path exists.
- `SCR-004`: Content remains visible; guest editing controls are absent.
- `AC-009`: Reading succeeds, controls are absent, and no guest edit mutation can be submitted or persisted.
- `TASK-011`: Remove guest editor controls and reject guest mutations while preserving valid-link read access.

The authoritative state also preserves this stale/recompile list in `project.revision_history`.

## Rediscovery

After recompilation, the supplied fixture and exact user change were swept again across the permission, flow, screen, persistence, security/privacy boundary, acceptance, and implementation mapping. No new independently answerable material unknown or contradiction appeared within the permitted evidence scope. No unsupported failure or recovery behavior was invented.

## Final validation

Final structure validation result:

```json
{"validator":"state","valid":true,"errors":[]}
```

Final closure validation result:

```json
{"validator":"closure","closed":false,"definition_digest":"c4ff238c27d539946f10fabdd277787f57f51682259ba043b540faaa097d8c9b","errors":[],"metrics":{"blocking_unknowns":0,"contradictions":0,"coverage_gaps":0,"invalid_closed_status":1,"minimum_definition_gaps":0,"missing_acceptance_criterion":0,"missing_active_goal":0,"missing_material_requirement":0,"missing_user_approval":1,"open_material_decisions":0,"orphan_acceptance_criteria":0,"orphan_requirements":0,"orphan_screens":0,"screen_action_gaps":0,"screen_state_gaps":0,"stale_approval":1,"stale_artifacts":0,"stale_user_approval":1,"unmapped_implementation_tasks":0}}
```

The definition is mechanically valid and `READY_FOR_REVIEW`, not closed. Closure requires explicit approval of revision 8 with digest `c4ff238c27d539946f10fabdd277787f57f51682259ba043b540faaa097d8c9b`, followed by recording that approval and rerunning both validators.
