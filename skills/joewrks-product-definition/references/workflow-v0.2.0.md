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

## FREEZE — bind claims to exact authority

Bind Core, specialist Grill, and UX coverage to exact CURRENT canonical pointers and hashes. `COVERED` requires a valid authority binding, `OPEN` requires a truthful unknown, and `N/A` requires a rationale plus basis binding.

Run from any consumer working directory by using the absolute installed skill directory:

```text
python <skill-directory>/scripts/validate_state.py STATE_JSON
python <skill-directory>/scripts/validate_closure.py STATE_JSON
python <skill-directory>/scripts/build_approval_manifest.py STATE_JSON
```

Do not set a persistent `PYTHONPATH`.

## APPROVE — show the exact change before recording approval

Present the deterministic Approval Manifest for the current definition revision and digest. Record approval only from the user's explicit approval of that exact manifest. Do not infer approval, invent an approval time, or copy legacy approval into the V2 current approval object.

After approval, rerun state and closure validation. `definition_status = CLOSED` means the current bounded Product Definition satisfies Semantic Closure; it does not mean implementation or deployment is complete.

## HANDOFF — compile V2 downstream authority

Compile only from a valid approved V2 state and a handoff definition:

```text
python <skill-directory>/scripts/compile_downstream_v2.py STATE_JSON HANDOFF_DEFINITION_JSON
```

The wrapper resolves its own installed roots. It preserves the M5 canonical JSON and exit-code contract and does not write Product Definition authority. A `SEMANTIC_AUTHORITY_GAP` produces affected-scope re-entry rather than a contract with invented meaning.

The current downstream identity is `joewrks.action-conformance/2.0`. Historical `joewrks.action-conformance/1.0` remains factual compatibility and is not redefined.

## VERIFY — audit exact dependencies and review only legitimate qualitative meaning

Audit a compiled contract against current Product Definition state:

```text
python <skill-directory>/scripts/audit_downstream_v2.py CONTRACT_JSON STATE_JSON
```

If the valid contract contains legitimate `REVIEW_REQUIRED` obligations, build the exact review package:

```text
python <skill-directory>/scripts/build_semantic_review_v2.py CONTRACT_JSON
```

The semantic-review identity is `joewrks.semantic-review/2.0`, and its reliability remains `NOT_MEASURED`. Review output is assurance evidence; it never creates or rewrites product authority.

Task 2 installs compile, dependency-audit, and semantic-review-package wrappers only. It does not install the runtime-evidence verifier, which is a separate M6 task.

## Re-enter only the affected scope

Implementation ambiguity or a downstream authority gap returns to DISCOVER/CLOSE for the affected scope. A re-entry artifact is a read-only proposal, not canonical authority. Register a canonical unknown only when a real unresolved product question remains, then increment the definition revision, set approval to UNAPPROVED, reconcile affected bindings, and repeat the Approval step.

An unrelated scope whose exact authority commitments remain current may continue. Final acceptance must still use the current approved definition.
