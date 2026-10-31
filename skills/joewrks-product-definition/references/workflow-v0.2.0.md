# Product Definition workflow — State 0.2.0

찾기 → 애매한 것 정하기 → 기준 고정 → 사용자 승인 → 구현 전달 → 구현 검증

```text
DISCOVER → CLOSE → FREEZE → APPROVE → HANDOFF → VERIFY
```

This is the installed workflow for native State `0.2.0` projects. The canonical authority remains `product-definition/<project-slug>/state.json` throughout the lifecycle.

## Choose the state contract first

- For a new project, copy `templates/state-v0.2.0.example.json`; [first-plan-guide.md](first-plan-guide.md) shows example states at the DISCOVER and CLOSED stages and where each kind of evidence goes. Keep `migration.mode = NATIVE`, `project.definition_status = OPEN`, and `approval.status = UNAPPROVED` until the real workflow establishes otherwise.
- For an existing State `0.2.0` project, read its canonical state first and resume from its current lifecycle position.
- For an existing State `0.1.2.1` project, validate with the frozen legacy contract. Do not silently migrate. Use `scripts/migrate_state.py --apply` only after the user explicitly asks to adopt V2; the result is an OPEN, UNAPPROVED reconciliation candidate rather than automatic Semantic Closure.

The native template does not assert Product Definition closure, user approval, approval time, downstream authority, or implementation conformance.

## DISCOVER — find what is missing

Inspect documented intent, prior decisions, repository state, tests, runtime behavior, designs, APIs, schemas, and external constraints. Record sources using the evidence class they actually support. Observed code or runtime behavior may prove what exists, but it does not by itself prove intended product meaning.

Disposition every discovered material surface as in scope, out of scope with authority, or open with a truthful unknown. Resolve contradictions by selecting or creating explicit authority; acknowledgement alone is not resolution.

## CLOSE — decide only what must be decided

Resolve factual questions from sufficient authoritative evidence. Apply the V2 Materiality and decision-authority rules before an agent default or user question. Ask the user only for a real material product choice, one highest-leverage question at a time.

Every material resolution keeps exact provenance through evidence, unknowns, decisions, and affected canonical authority. AI autonomy is limited to non-material, local, safely reversible details.

Questions about how the user experiences the product (first use, input mechanics, what fits on the smallest screen) are product choices like any other; do not let data and computation questions crowd them out.

## FREEZE — bind claims to exact authority

While a native definition is `OPEN`, requirements and screens may exist before their Core and UX coverage rows: once every question of a surface is answered, mark the surface `IN_SCOPE` with its requirement as authority and write the records and coverage at your pace. Rows that exist are validated; every missing row is an error again at `READY_FOR_REVIEW`. No placeholder authoring question is needed for this stretch. `scripts/draft_freeze.py STATE_JSON --patch PATCH_JSON` writes the missing rows into the patch (`rows`) with the exact axis inventory: cells the record graph decides are filled, every other cell is `DECIDE` with candidates and must be settled by you before `open_revision.py` will accept it. It does not choose which rule answers an axis. A row may declare a `shape` (actions) or a `default_authority` and omit the cells they imply; see [coverage-inheritance.md](coverage-inheritance.md). `scripts/compact_coverage.py STATE_JSON --write` converts existing rows where that loses nothing.

Complete the experience pass in `ux-state-taxonomy.md` first: user journey, interaction mechanics and smallest-viewport information budget. Bind Core, specialist Grill, and UX coverage to exact CURRENT canonical pointers and hashes. `COVERED` requires a valid authority binding, `OPEN` requires a truthful unknown, and `N/A` requires a rationale plus basis binding. When `surface_manifest.grill_profile.AUTH` or `PERMISSION` is a justified `N/A`, the UX axes listed for it in `ux-profile-inheritance-v1.json` (account, permission and session axes) may be omitted from every screen instead of repeating the same `N/A`; a written cell is still validated.

Run from any consumer working directory by using the absolute installed skill directory:

```text
python <skill-directory>/scripts/validate_state.py STATE_JSON
python <skill-directory>/scripts/validate_closure.py STATE_JSON
python <skill-directory>/scripts/build_approval_manifest.py STATE_JSON
```

Do not set a persistent `PYTHONPATH`.

When `validate_state.py` reports errors, `python <skill-directory>/scripts/explain_state_errors.py STATE_JSON` reruns the same validation read-only and adds a `hint` to each error it can explain: the authority classes a source kind supports, and for a coverage cell the allowed record types and pointer roots, the status shape, and each failing binding with its bound and current value hash.

To open the next revision, write a patch with every record the revision adds or changes (`evidence`, `objects` by group, `surfaces`) and any coverage-cell edits addressed by stable ID, such as `{"cell": "coverage[REQ-001].cells.acceptance", "add": [{"record_id": "AC-009", "pointer": "/assertion"}]}`, then run:

```text
python <skill-directory>/scripts/open_revision.py STATE_JSON --patch PATCH_JSON --write
```

It increments `definition_revision`, sets `UNAPPROVED` and the requested non-`CLOSED` status (`READY_FOR_REVIEW` by default), applies the patch, re-hashes only bindings that point at patched records, recomputes a `CURRENT` discovery baseline, and writes only when the result validates with no unresolved binding. A binding whose record changed without being in the patch, or that points at a record that is no longer `CURRENT`, is reported instead of refreshed. It warns when the base revision was never approved. It applies only records you authored under the ordinary evidence, unknown, decision and binding contracts; it is not a re-entry mutator and must never receive a re-entry artifact or `candidate_unknown` text. Keep the patch file next to `state.json` (for example `rev32-patch.json`): the previous approved state plus that patch reproduces the revision exactly, which is how an audit checks it. `scripts/refresh_bindings.py STATE_JSON [--accept IDS] [--write]` lists broken bindings and re-hashes only those for the record IDs you accept.

`python <skill-directory>/scripts/new_records.py --patch PATCH_JSON <kind> ...` appends complete records to that patch from the fields you decide: `evidence`; `question` (an OPEN unknown, `USER_CONFIRMATION` when it carries a recommendation); `user-decision` (a RESOLVED unknown plus the CURRENT decision the user stated or the recommendation the user accepted with `--accepted`); and `authoring` (a non-material agent unknown and decision for writing already-decided meaning into records). Options are `ID=statement|consequence`. Put the user's intent evidence of an OPEN question in `--reason`, not `--evidence`: evidence that already supports the required class makes the question `EVIDENCE_RESOLVABLE`, so it is never asked. Review the result with `open_revision.py` without `--write` before writing.

When a revision replaces records, put the new records in the patch, then run `python <skill-directory>/scripts/supersede_records.py STATE_JSON --patch PATCH_JSON --replace OLD=NEW` (repeat `--replace` for each pair, for example the decision and its source unknown). It marks each OLD record `SUPERSEDED` by NEW, re-points reference fields of current records (such as `affects`, `decision_refs`, `reasoning_refs`, `applies_to`) to NEW, and moves coverage bindings from OLD to NEW at the same pointer. Provenance (`resolved_by`, `source_unknown_refs`), free text, and historical records are left unchanged; provenance that still names OLD is listed under `provenance_to_review`. It does not rewrite rules or other meaning derived from OLD; change those records yourself in the same patch.

`build_approval_manifest.py` writes one compact, key-sorted, ASCII-safe JSON line on every machine-readable success or error path. Success and semantic/lifecycle rejection use stdout with exit codes `0` and `1`; usage, read, and output failures use stderr with exit code `2`. Consumers must parse JSON rather than depend on localized unescaped text, and must discard any partial stdout when the exit code is `2`. The command remains read-only and has no file-output option.

## APPROVE — show the exact change before recording approval

Present the deterministic Approval Manifest for the current definition revision and digest. Record approval only from the user's explicit approval of that exact manifest. Do not infer approval, invent an approval time, or copy legacy approval into the V2 current approval object.

Record the approval with:

```text
python <skill-directory>/scripts/record_approval.py STATE_JSON --revision N --manifest-digest DIGEST --at YYYY-MM-DDTHH:MM:SSZ --write
```

Take `N` and `DIGEST` from the user's approval message. When the user approves with a short reply such as "승인", take them from the exact Manifest you presented in the message they replied to. If any record changed after you presented it, the recomputed digest no longer matches and the command refuses; present the new Manifest and ask again. The command recomputes the current Approval Manifest, refuses a revision or digest mismatch, a state that is not `READY_FOR_REVIEW` / `UNAPPROVED`, or a result that does not reach Semantic Closure, and then writes `approval`, the exact `approval_history` commitment, and `CLOSED` together. Use the approval message's UTC time for `--at`; when that time is not available, pass `--at observed` and report the result's `approved_at_source: observed_at_recording`. Without `--write` it only checks and prints what it would record.

`python <skill-directory>/scripts/approval_status.py STATE_JSON` is read-only. It reports the approved revisions, revisions still pending since the last approval with their change counts, and revisions that were never approved on their own. Run it before implementing or reporting work on a revision: work built on a pending revision is unapproved until the user approves the current manifest.

After approval, rerun state and closure validation. `definition_status = CLOSED` means the current bounded Product Definition satisfies Semantic Closure; it does not mean implementation or deployment is complete.

The approved state must then be projected into the default human delivery pair before planning delivery is reported complete:

- `MASTER_PLANNING_SPEC.md` — complete human-readable planning projection for downstream design/implementation consumers.
- `planning-review-core.html` — compact user review view. It summarizes the Master/state and does not create product or visual-design authority.

## HANDOFF — deliver readable planning and compile V2 downstream authority

Before compiling machine authority, materialize the two human-facing projections from the exact approved revision.

### Projection fidelity check

For each flow and major action represented in the Master or review view:

1. Trace preconditions, actor action, system decision, success, failure, recovery, postcondition, and acceptance IDs back to the approved state/source bindings.
2. Preserve conditional outcomes as conditional. A special offline, stale, normalization, recovery, or invalid-state case must not become the default outcome for every success/failure.
3. If repeated text is deduplicated into a shared clause, keep the clause's exact source/stable-ID identity and state on each consumer when it applies.
4. Check both directions: every material approved branch has a readable destination, and every displayed branch has approved authority.
5. The Master may be comprehensive; the review HTML must remain concise. Do not copy the full action/acceptance corpus into the visual review just to prove completeness.
6. If the environment permits, open the HTML and verify readable text, diagrams, internal navigation, and clipping. If render/click observation is unavailable, record `NOT_VERIFIED`; static file/link checks are not render evidence.

## Candidate preflight

Before asking for approval of a native V2 candidate, run:

```text
python <skill>/scripts/preflight_state_candidate.py CANDIDATE_STATE_JSON [--canonical CANONICAL_STATE_JSON]
```

The command is read-only. It reports exact validation, semantic-readiness, binding, manifest-review-readiness, and approval-stage findings as `joewrks.state-candidate-preflight/1.0`. A `READY_FOR_REVIEW` / `UNAPPROVED` candidate may pass preflight without fabricating approval; actual approval remains a separate user-authority step.

## Planning projection audit and recovery

Audit materialized planning projections with:

```text
python <skill>/scripts/audit_planning_projections.py AUDIT_INPUT_JSON
```

The input must bind the exact canonical state, an independently hashed approved-scope record, every required projection, its source-identity tokens, and any semantic or render review evidence. Required projection membership comes from the scope record, never a caller downgrade. Unreviewed semantic or render work stays `UNKNOWN` with `findings: null`. A prior receipt may identify unchanged completed projections, but current source, projection, and evidence bytes are always revalidated. Recovery is projection-specific and read-only: the audit names the owner, path, and next action and never edits canonical state, creates approval, or claims that a hash authenticates reviewer authority.

A projection defect is fixed in the projection or its source mapping. Do not change product policy merely to make the projection simpler.

After each approved revision, first refresh the mechanical parts, then run the light read-only check before reporting delivery:

```text
python <skill-directory>/scripts/update_projection.py STATE_JSON --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html [--adopt] --write
```

It regenerates the `<!-- JOEFLOW:IDENTITY -->` and `<!-- JOEFLOW:SOURCE-MAP -->` blocks (revision, digests, change counts, earlier approvals, and the record ID table) and, outside them, updates the value after the `Revision:`, `Definition digest:` and `Approval Manifest digest:` labels. `--adopt` wraps an older document's identity lines in a block once. It lists, for each added, changed, superseded or retired record, the hand-written lines that name it; edit those rows yourself. Without `--write` it only shows the diff.


```text
python <skill-directory>/scripts/projection_check.py STATE_JSON --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html
```

It reports whether each projection names the current revision, definition digest and Approval Manifest digest, which records this revision added (`REQ`, `RULE`, `FLOW`, `SCR`, `STATE`, `DATA`, `INT`, `AC`, `TASK` by default) that the spec never names, which changed records the spec names and must be re-read, and which superseded or retired records the spec still names. `--draft` prints the identity lines and the current text of every added or changed record; condense it into the projection rather than pasting it. It does not replace the full audit above and does not judge meaning.

Compile only from a valid approved V2 state and a `joewrks.handoff-definition/2.1` handoff definition:

```text
python <skill-directory>/scripts/compile_downstream_v2.py STATE_JSON HANDOFF_DEFINITION_JSON
```

The wrapper resolves its own installed roots, produces `joewrks.action-conformance/2.1`, and does not write Product Definition authority. A `SEMANTIC_AUTHORITY_GAP` produces affected-scope re-entry rather than a contract with invented meaning.

The current downstream identity is `joewrks.action-conformance/2.1`. Historical `joewrks.action-conformance/2.0` and `joewrks.action-conformance/1.0` remain readable, auditable compatibility artifacts and are not the default current compilation route.

## VERIFY — audit exact dependencies and review only legitimate qualitative meaning

Audit a compiled contract against current Product Definition state:

```text
python <skill-directory>/scripts/audit_downstream_v2.py CONTRACT_JSON STATE_JSON
```

If the valid contract contains legitimate `REVIEW_REQUIRED` obligations, build the exact review package:

```text
python <skill-directory>/scripts/build_semantic_review_v2.py CONTRACT_JSON
```

The semantic-review identity is `joewrks.semantic-review/2.1`, and its reliability remains `NOT_MEASURED`. Do not invoke it when no `REVIEW_REQUIRED` obligations exist. Review output is assurance evidence; it never creates or rewrites product authority.

For a current 2.1 contract, materialize `joewrks.runtime-conformance-plan/1.0`. Before any 2.1 runtime admission, validate each raw record as frozen `joewrks.downstream.execution/1.0` evidence; retain that transport unchanged. Bind the admitted records to the plan and source contract as `joewrks.runtime-evidence-bundle/1.0`. The M6 runtime verifier/report emits the separately frozen `joewrks.runtime-conformance-report/1.0` implementation-conformance evidence; it is read-only and never changes Product Definition authority.

Verify actual execution evidence against the compiled contract with the installed runtime verifier:

```text
python <skill-directory>/scripts/verify_runtime_v21.py CONTRACT_JSON RUNTIME_PLAN_JSON RUNTIME_EVIDENCE_BUNDLE_JSON [REVIEW_PACKAGE_JSON REVIEW_OUTPUT_JSON]
```

Runtime non-conformance is not automatically a Product Definition gap. Route it by inspecting whether exact authority is already clear.

## Re-enter only the affected scope

Use the installed [reentry workflow](reentry-workflow-v0.2.0.md) before changing Product Definition. A re-entry artifact and its `candidate_unknown` are a read-only proposal or evidence, never canonical authority and never an automatic state mutation.

- Read provenance from the actual event shape. When `source_contract_hash` is non-null, resolve the exact matching action contract and inspect its `source_seed_inventory` and `scope_commitments`; when it is null, inspect the exact pre-contract handoff definition plus affected current state authority and evidence.
- If Product Definition authority and local contract dependencies are exact, a runtime mismatch is an implementation bug: correct the implementation without inventing a product decision or automatically changing revision or approval.
- If inspection confirms a real semantic authority gap or ambiguity, return to DISCOVER/CLOSE for the affected scope: inspect and resolve exact evidence first; assess Materiality and decision authority; prepare a complete V2 unknown record off-state; then, as one canonical mutation, increment `definition_revision`, move to a truthful non-`CLOSED` state, set approval to `UNAPPROVED`, stale affected authority and downstream dependencies, and register the complete unknown under the new revision. Reconcile affected Grill and authority bindings and repeat the Approval step.
- `candidate_unknown` wording must never be copied directly or verbatim. Any later canonical unknown or user question is independently authored from inspected evidence and ordinary V2 semantics.
- For `OUT_OF_SCOPE_REQUEST`, scope resolution comes first. An implementation request does not make behavior part of approved scope, even provisionally or temporarily.

An unrelated scope whose exact authority commitments remain current may continue. Final acceptance must still use the current approved definition.
