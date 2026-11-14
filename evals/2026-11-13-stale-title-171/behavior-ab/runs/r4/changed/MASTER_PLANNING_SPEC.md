# MASTER PLANNING SPEC — 요청 폼

> Complete human-readable projection of the Product Definition (revision 2, 승인 대기).
> Canonical authority remains `product-definition/request-form/state.json`.
> 이 문서는 state.json의 투영이며, 둘이 어긋나면 state.json이 우선한다.

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

rev 2는 아직 승인되지 않았다. 아래 내용 중 rev 2에서 추가된 기록(UNK-002,
DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902)은 사용자가 위
Approval Manifest를 승인하기 전까지 승인된 의미가 아니다.

## 1. Product, users, goals, scope

- 목표 GOAL-001: 요청자가 유효한 요청을 끝까지 제출한다.
- 사용자 USR-001: 로그인한 요청자(REQUESTER) 한 종류.
- 요구사항 REQ-001: 요청자는 유효한 요청을 제출할 수 있다. 범위는 주 요청 흐름 하나이며 UI가 필요하다.
- 범위(SURF-001 "Request submission", IN_SCOPE): 요청 입력·검증·제출, 그리고 rev 2에서 더한 요청 내용 글자 수 표시.
- 외부 의존: INT-001 Request API — 접수된 요청을 저장한다.
- 명시적 제외: state에 기록된 제외 항목은 없다. 위 범위 밖의 기능(요청 조회·수정·취소 등)은 정의되지 않았으며, 구현에서 추가하지 않는다.

## 2. IA, navigation, and return relationships

- 화면은 SCR-001(요청 제출) 하나다. 진입은 "요청 폼을 연다"(FLOW-001 entry).
- 진입 조건: 요청자가 로그인해 있어야 한다(FLOW-001 precondition).
- 다른 화면으로의 이동·복귀 관계는 state에 정의되어 있지 않다. 제출 후 이동할 화면도 정의되지 않았다.

## 3. Shared behavior, data, and state contracts

- RULE-001 (DEC-001 ← UNK-001, 사용자 결정): 유효한 요청만 제출할 수 있다. 사용자는 "검증 후 제출"(OPT-A)을 골랐고 "아무 요청이나 허용"(OPT-B)은 고르지 않았다. 결과: 유효하지 않은 요청은 거절된다.
- RULE-002 (DEC-002 ← UNK-002, rev 2 추가): 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다.
  - 200은 현재 구현의 요청 내용 칸 최대 길이(maxlength=200, EVD-902, 관찰된 구현 사실)에서 온 값이다.
  - 버려진 대안: 180자부터만 보이기(NEAR_LIMIT). 채택안의 대가: 칸 아래 한 줄이 늘어난다.
- STATE-001 REQUEST_READY (SCR-001 소유): 필수 입력이 유효한 상태.
- DATA-001 Request: 요청 입력을 담는다. 소유자는 요청자(REQUESTER).
- INT-001 Request API: 접수된 요청을 저장한다.

## 4. Screen specifications

### SCR-001 요청 제출

- 목적: 요청을 제출한다. 상호작용 화면(INTERACTIVE). 관련 요구사항 REQ-001.
- 주요 동작: 제출(submit).
- 정보: 요청 내용 입력 칸(textarea, 최대 200자 — EVD-902 관찰 사실), 그 아래 오른쪽에 '현재 글자 수 / 200' 표시(RULE-002). 빈 칸이면 '0 / 200'(AC-002).
- 상태: REQUEST_READY(STATE-001)는 필수 입력이 유효할 때다. 유효하지 않으면 제출되지 않는다(RULE-001).
- 읽기/쓰기: 제출된 요청(DATA-001)을 Request API(INT-001)로 저장한다.
- 완료 기준: AC-001, AC-002.
- 정의되지 않은 것: 필수 입력 항목의 구체 목록, 검증 오류 문구·위치, 제출 중·실패 시 표시, 최소 화면 폭의 정보 배치, 기기별 입력 방식. 이것들은 state에 별도 결정이 없으므로 이 문서에서 정하지 않는다.

## 5. User flows

### FLOW-001 요청 제출 (GOAL-001)

- 요청자 시점: 로그인한 요청자가 요청 폼을 열고 요청 내용을 쓴다. 쓰는 동안 칸 아래 오른쪽 숫자가 바로 바뀌어 200자 중 몇 자를 썼는지 안다(RULE-002). 제출하면 검증을 거친다.
- 진입: 요청 폼을 연다. 사전 조건: 로그인 상태.
- 시스템 판단: 요청이 유효한가(RULE-001).
  - 유효함 → 제출되고 요청이 접수된다(FLOW-001 outcome), 접수된 요청은 저장된다(AC-001, INT-001).
  - 유효하지 않음 → 제출이 거절된다(RULE-001, DEC-001 OPT-A 결과).
- 복구·재시도, 제출 이후 이동: state에 구체 정의가 없다.

## 6. Action contracts

### submit (SCR-001)

- 행위자: 로그인한 요청자(USR-001). 대상: Request(DATA-001).
- 사전 조건: 로그인 상태(FLOW-001), 필수 입력이 유효함(STATE-001).
- 실행: 제출 전에 요청을 검증한다(DEC-001).
- 성공(유효할 때만): 요청이 접수되고 저장된다(AC-001, INT-001).
- 거절(유효하지 않을 때): 제출되지 않는다(RULE-001).
- 취소·동시성·멱등성: state에 정의되지 않았다.

### 요청 내용 입력 (SCR-001, rev 2)

- 글자를 넣거나 지울 때마다 칸 아래 오른쪽 표시가 '현재 글자 수 / 200'으로 즉시 바뀐다(RULE-002, AC-002). 제출 여부와 무관하게 입력 중 항상 보인다.

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

- AC-001 (REQ-001, TASK-001): 유효한 요청은 접수되고 저장된다.
- AC-002 (REQ-001, TASK-002, rev 2): 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다. 빈 칸은 '0 / 200'.

## 8. Responsive, accessibility, and downstream choice boundaries

- 승인 대상 제품 요구: 위 RULE-001, RULE-002와 AC-001, AC-002.
- 글자 수 표시의 위치(칸 아래 오른쪽)와 형식('현재 / 200')은 제품 결정(DEC-002)이다. 글꼴·색·간격은 이후 시각 설계 선택이다.
- 반응형 배치와 접근성(예: 글자 수 변화를 보조기기에 알리는 방식)은 state에 결정이 없다. 구현이 이를 새 정책으로 정하지 않고, 필요하면 Product Definition으로 되돌린다.

## 9. Remaining unknowns, external verification, and approval state

- 열린 제품 질문: 없음(UNK-001, UNK-002 모두 RESOLVED).
- 승인 상태: rev 2는 READY_FOR_REVIEW · UNAPPROVED. 위 Manifest digest에 대한 사용자의 명시적 승인이 남아 있다.
- 검토 때 확인할 점: DEC-002는 "추천 수락"으로 기록되어 있지만, 근거가 된 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)는 다른 세션이 전한 말이고, "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이다. 사용자가 BELOW/NEAR_LIMIT 선택지를 직접 본 기록은 없다. rev 2 Manifest를 승인하면 이 위치·형식도 함께 승인하는 것이므로, 승인 요청 때 이 점을 함께 보여 준다.
- 200자 한도는 관찰된 구현 사실(EVD-902)이다. 한도가 바뀌면 RULE-002·AC-002의 '200'도 다시 정해야 한다.
- 구현·런타임 검증: 아직 실행하지 않았다(제품 모호함이 아님).

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

| ID | 내용 |
|---|---|
| GOAL-001 | 요청자가 유효한 요청을 끝까지 제출한다. |
| USR-001 | 로그인한 요청자. |
| REQ-001 | 요청자는 유효한 요청을 제출할 수 있다(주 요청 흐름). |
| UNK-001 | 어떤 제출 정책을 따를까? → RESOLVED, 사용자 결정(OPT-A 검증 후 제출) → DEC-001 |
| UNK-002 | 글자 수를 어디에 어떻게 보이나? → RESOLVED, 추천(BELOW) 수락 → DEC-002 |
| DEC-001 | 제출 전에 요청을 검증한다. |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다. |
| RULE-001 | 유효한 요청만 제출할 수 있다. |
| RULE-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다. |
| FLOW-001 | 요청 폼을 연다(로그인 필요) → 검증 후 제출 → 요청 접수. |
| SCR-001 | 요청 제출 화면. 주요 동작: 제출. |
| STATE-001 | REQUEST_READY: 필수 입력이 유효함. |
| DATA-001 | Request: 요청 입력을 담는다. 소유자 요청자. |
| INT-001 | Request API: 접수된 요청을 저장한다. |
| AC-001 | 유효한 요청은 접수되고 저장된다. |
| AC-002 | 글자를 넣거나 지우면 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸 '0 / 200'). |
| TASK-001 | REQ-001 구현, AC-001 확인. |
| TASK-002 | REQ-001 구현, AC-002 확인. |

## 변경 이력

- rev 1: 첫 승인
- rev 1 → rev 2: 요청 내용 글자 수 표시 추가(UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902). 승인 대기.
