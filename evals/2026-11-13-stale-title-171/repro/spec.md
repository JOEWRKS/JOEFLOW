# MASTER PLANNING SPEC — 요청 폼

> Complete human-readable projection of the approved Product Definition.
> Canonical authority remains `{{CANONICAL_STATE_PATH}}`.

## Approved identity

<!-- JOEFLOW:IDENTITY:BEGIN -->
- Revision: `2` · READY_FOR_REVIEW · 승인 대기
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906` (rev 1→2: 추가 7 · 변경 0 · 대체 0 · 폐기 0)
- 이전 승인: rev 1 `dd1e837b…`
<!-- JOEFLOW:IDENTITY:END -->

`scripts/update_projection.py STATE --spec THIS_FILE --review REVIEW_FILE --write`
regenerates the two `JOEFLOW:` blocks and lists the rows that name changed
records; the condensed text elsewhere stays hand-written.

## 1. Product, users, goals, scope

Describe the user outcome, actors, goals, included scope, explicit exclusions,
external dependencies, and important product boundaries.

## 2. IA, navigation, and return relationships

Describe information hierarchy separately from screen-to-screen movement.
For every screen, include stable ID, purpose, entry, exit, and return behavior.

## 3. Shared behavior, data, and state contracts

Define shared rules once and link exact stable IDs/source pointers. A shared
clause may reduce duplication but must not erase when or where it applies.

## 4. Screen specifications

For each screen: purpose, information priority, major actions, applicable
states, inputs, reads/writes, persistence, failures/recovery, responsive and
accessibility requirements, and related acceptance IDs.
Also state interaction mechanics per major action (input per device, preview/
confirm, cancel/undo) and the information budget for the smallest supported
viewport (visible at once, behind disclosure, dropped).

## 5. User flows

For every material flow: entry, preconditions, actor action, system decision,
happy path, alternatives, failures, recovery/retry, exit, postcondition, and
acceptance IDs.
Start with a user walkthrough for each primary user, written from their side:
first use, main task, likely mistakes and recovery, return visit.

## 6. Action contracts

For every major action: actor, target, input, preconditions, execution,
conditional success outcomes, rejection/failure, recovery, cancellation,
concurrency/idempotency where applicable, visible result, data effect, and
source binding.

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

Include the full assertion/expected-result meaning and requirement references.
Do not reduce acceptance to an ID list.

## 8. Responsive, accessibility, and downstream choice boundaries

Separate approved product requirements from later visual/technical choices.

## 9. Remaining unknowns, external verification, and approval state

List only real unresolved items. Distinguish product ambiguity from runtime,
provider, visual, or integration verification that has simply not run.

## 10. Source map

Provide exact canonical pointers/stable IDs so reviewers and downstream agents
can trace each material section without reconstructing product meaning from
many editable documents. The record table below is generated.

<!-- JOEFLOW:SOURCE-MAP:BEGIN -->
| 종류 | 현재 | 대체·폐기 |
|---|---|---|
| 목표 (`/objects/goals`) | GOAL-001 | - |
| 사용자 (`/objects/users`) | USR-001 | - |
| 요구사항 (`/objects/requirements`) | REQ-001 | - |
| 결정 (`/objects/decisions`) | DEC-001, DEC-002 | - |
| 규칙 (`/objects/rules`) | RULE-001, RULE-002 | - |
| 흐름 (`/objects/flows`) | FLOW-001 | - |
| 화면 (`/objects/screens`) | SCR-001 | - |
| 상태 (`/objects/states`) | STATE-001 | - |
| 데이터 (`/objects/data`) | DATA-001 | - |
| 연동 (`/objects/integrations`) | INT-001 | - |
| 완료 기준 (`/objects/acceptance_criteria`) | AC-001, AC-002 | - |
| 작업 (`/objects/tasks`) | TASK-001, TASK-002 | - |
| 질문 (`/objects/unknowns`) | UNK-001, UNK-002 | - |
<!-- JOEFLOW:SOURCE-MAP:END -->

## 레코드

| GOAL-001 | text |
| USR-001 | text |
| REQ-001 | text |
| UNK-001 | text |
| UNK-002 | text |
| DEC-001 | text |
| DEC-002 | text |
| RULE-001 | text |
| RULE-002 | text |
| FLOW-001 | text |
| SCR-001 | text |
| STATE-001 | text |
| DATA-001 | text |
| INT-001 | text |
| AC-001 | text |
| AC-002 | text |
| TASK-001 | text |
| TASK-002 | text |

## 변경 이력

- rev 1: 첫 승인
- revision 1에서 rev 2로: 글자 수 표시
