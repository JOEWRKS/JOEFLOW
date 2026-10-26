# Product Definition workflow — State 0.2.0

찾기 → 애매한 것 정하기 → 기준 고정 → 사용자 승인 → 구현 전달 → 구현 검증

```text
DISCOVER → CLOSE → FREEZE → APPROVE → HANDOFF → VERIFY
```

This is the installed workflow for native State `0.2.0` projects. The canonical authority remains `product-definition/<project-slug>/state.json` throughout the lifecycle.

## Choose the state contract first

- For a new project, copy `templates/state-v0.2.0.example.json`. Keep `migration.mode = NATIVE`, `project.definition_status = OPEN`, and `approval.status = UNAPPROVED` until the real workflow establishes otherwise.
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

Complete the experience pass in `ux-state-taxonomy.md` first: user journey, interaction mechanics and smallest-viewport information budget. Bind Core, specialist Grill, and UX coverage to exact CURRENT canonical pointers and hashes. `COVERED` requires a valid authority binding, `OPEN` requires a truthful unknown, and `N/A` requires a rationale plus basis binding.

Run from any consumer working directory by using the absolute installed skill directory:

```text
python <skill-directory>/scripts/validate_state.py STATE_JSON
python <skill-directory>/scripts/validate_closure.py STATE_JSON
python <skill-directory>/scripts/build_approval_manifest.py STATE_JSON
```

Do not set a persistent `PYTHONPATH`.

`build_approval_manifest.py` writes one compact, key-sorted, ASCII-safe JSON line on every machine-readable success or error path. Success and semantic/lifecycle rejection use stdout with exit codes `0` and `1`; usage, read, and output failures use stderr with exit code `2`. Consumers must parse JSON rather than depend on localized unescaped text, and must discard any partial stdout when the exit code is `2`. The command remains read-only and has no file-output option.

## APPROVE — show the exact change before recording approval

Present the deterministic Approval Manifest for the current definition revision and digest. Record approval only from the user's explicit approval of that exact manifest. Do not infer approval, invent an approval time, or copy legacy approval into the V2 current approval object.

Record the approval with:

```text
python <skill-directory>/scripts/record_approval.py STATE_JSON --revision N --manifest-digest DIGEST --at YYYY-MM-DDTHH:MM:SSZ --write
```

Take `N` and `DIGEST` from the user's own approval message. The command recomputes the current Approval Manifest, refuses a revision or digest mismatch, a state that is not `READY_FOR_REVIEW` / `UNAPPROVED`, or a result that does not reach Semantic Closure, and then writes `approval`, the exact `approval_history` commitment, and `CLOSED` together. Use the approval message's UTC time for `--at`; when that time is not available, pass `--at observed` and report the result's `approved_at_source: observed_at_recording`. Without `--write` it only checks and prints what it would record.

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
