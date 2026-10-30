# First plan guide

A short path through a first State 0.2.0 definition. The contracts in
[workflow-v0.2.0.md](workflow-v0.2.0.md) still decide; this page only says where to start
and where evidence goes, so a first plan does not need the validator source.

## 1. Start from an example

| File | Stage | Use it to see |
|---|---|---|
| `templates/state-v0.2.0.example.json` | empty | the skeleton to copy for a new project |
| `templates/examples/discover-one-question.state.json` | DISCOVER | one brief (evidence), one OPEN surface, one question with a recommendation; `next_product_question.py` asks it |
| `templates/examples/closed-minimal.state.json` | CLOSED | the smallest definition that passes closure: one requirement with Core, UX and Grill coverage, approval and history |

Validate after every change: `python <skill>/scripts/validate_state.py state.json`.
When an error names a field, `explain_state_errors.py state.json` adds the allowed values.

## 2. The loop

1. Record what you found as evidence, and each open product choice as a question
   (`new_records.py --patch PATCH evidence|question ...`).
2. `next_product_question.py state.json` picks the one question to ask now.
3. Record the user's answer: `new_records.py --patch PATCH user-decision ...`. If the
   question was holding a coverage cell OPEN (a Grill axis, a Core or UX cell), add
   `--address CELL` so the same patch closes that cell with the new decision.
   Without it the cell stays OPEN with no OPEN question and validation fails.
4. Apply the patch: `open_revision.py state.json --patch PATCH --status OPEN --write`
   while discovering, `--status READY_FOR_REVIEW` when the definition is complete.
   Each applied patch is one revision. While the status is `OPEN`, requirements and
   screens may exist before their coverage rows; when a surface's questions are all
   answered, mark it `IN_SCOPE` with its requirement as authority. Missing rows become
   errors at `READY_FOR_REVIEW`.
5. FREEZE, APPROVE and HANDOFF as in the workflow. After approval,
   `update_projection.py` refreshes the identity and source-map blocks of the planning
   documents and lists the rows that name changed records.

## 3. Where evidence goes

| You have | Put it in | Not in | Why |
|---|---|---|---|
| What the user said they want | the question's `recommendation.reasoning_refs` | the question's `evidence_refs` | intent evidence that supports the question's `required_authority_class` *answers* it: the question becomes `EVIDENCE_RESOLVABLE` and is never asked |
| Facts about the current product or code (observed implementation, runtime, a measurement) | the question's `evidence_refs` to frame it, and `reasoning_refs` when they justify the recommendation | — | facts never answer an `INTENT` question, so they cannot hide it; inferred intent and design artifacts are not accepted as reasons |
| A requirement, rule, flow, data or integration record behind a recommendation | `reasoning_refs` | — | `DEC` records are not allowed there; cite the rule or requirement the decision produced |
| Why a coverage cell does not apply | the cell's `basis_bindings` plus a `rationale` | `authority_bindings` | `N/A` needs both a basis and a meaningful rationale |
| Why a whole specialist domain does not apply | `surface_manifest.grill_profile.<DOMAIN>` as `N/A` with `basis_refs` | each cell | AUTH/PERMISSION `N/A` also lets screens omit the account, permission and session UX axes |
| The options shown when the user accepts a recommendation | `accepted_recommendation.alternatives_presented` = **every** option ID, the recommended one included | only the alternatives | the validator compares it with the full option list |
| A user instruction relayed by another session or person | evidence with a `locator` naming who relayed it | — | there is no separate source kind yet; say it was relayed |
| A decision that replaces an earlier one, agent defaults included | the new records in a patch, then `supersede_records.py --replace OLD=NEW` for the decision and its question | editing the old decision | the old pair stays as history; an agent default may be superseded like a user decision |

## 4. Size before you freeze

FREEZE binds every Core axis of every requirement and every UX axis of every screen.
A feature with about a dozen decisions needed roughly 37 records and 120 bound cells in
practice. Keep requirements and screens few and broad; split only where behavior differs.
