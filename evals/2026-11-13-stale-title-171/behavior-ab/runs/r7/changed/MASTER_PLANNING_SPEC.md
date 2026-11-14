# MASTER PLANNING SPEC — 요청 폼

> Complete human-readable projection of the Product Definition (rev 2, 승인 대기).
> Canonical authority remains `product-definition/request-form/state.json`.
> 이 문서와 state.json이 다르면 state.json이 맞다.

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

- 목표 GOAL-001: 요청자가 유효한 요청 제출을 끝낸다.
- 사용자 USR-001: 로그인한 요청자(REQUESTER).
- 요구사항 REQ-001: 요청자는 유효한 요청을 제출할 수 있다. 범위는 주 요청 흐름 하나이며 UI가 필요하다.
- 범위 영역 SURF-001 "Request submission"(IN_SCOPE).
- 해당 없음(EVD-900, 사용자 확인): 결제, 파일 첨부, 비동기 처리, 권한 구분, 파괴적 동작 등 grill profile에서 `N/A`로 분류된 축. 인증(AUTH)만 활성.
- 외부 의존: INT-001 Request API — 받아들인 요청을 저장한다.

## 2. IA, navigation, and return relationships

- 화면은 SCR-001(요청 제출) 하나다.
- 진입: 요청 폼을 연다(FLOW-001 entry). 전제: 요청자가 로그인해 있다.
- 나가기/돌아오기: 승인된 정의에 제출 뒤 이동할 화면이나 돌아오는 경로는 정해져 있지 않다(§9 참조).

## 3. Shared behavior, data, and state contracts

- RULE-001 (DEC-001, UNK-001에서 사용자 결정): 유효한 요청만 제출할 수 있다. 제출 전에 요청을 검증한다.
- RULE-002 (DEC-002, UNK-002에서 추천 BELOW 수락): 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다.
  - 근거: EVD-901(전달된 사용자 원문 "요청 내용 칸에 글자 수 보여줘"), EVD-902(요청 내용 칸은 textarea 하나, maxlength=200 — 관찰된 구현 사실).
  - 고르지 않은 대안: NEAR_LIMIT(180자부터만 보임). 감수한 비용: 칸 아래 한 줄이 늘어난다.
- STATE-001 `REQUEST_READY` (SCR-001): 필수 입력이 유효한 상태.
- DATA-001 Request: 요청 입력을 담는다. 소유자는 요청자.

## 4. Screen specifications

### SCR-001 요청 제출

- 목적: 요청을 제출한다. 관련 요구사항 REQ-001. 상호작용 화면.
- 주요 동작: 제출(submit).
- 입력: 요청 내용 textarea(최대 200자, EVD-902).
- 글자 수 표시(RULE-002): 칸 아래 오른쪽, '현재 글자 수 / 200', 입력·삭제마다 즉시 갱신, 빈 칸은 '0 / 200'(AC-002). 항상 보인다(180자 이상일 때만 보이는 방식이 아님).
- 상태: 필수 입력이 유효하면 REQUEST_READY(STATE-001). 유효하지 않으면 제출할 수 없다(RULE-001).
- 쓰기: 받아들인 요청은 Request API(INT-001)로 저장된다(AC-001).
- 관련 완료 기준: AC-001, AC-002.
- 가장 작은 화면의 정보 예산, 입력 장치별 세부 조작, 실패 문구는 승인된 정의에 따로 정해져 있지 않다(§9).

## 5. User flows

### FLOW-001 요청 제출 (GOAL-001)

- 요청자 시점: 로그인한 요청자가 요청 폼을 열고, 요청 내용을 적는 동안 칸 아래 오른쪽 글자 수(예: '37 / 200')를 보며 200자 안에 맞춘 뒤 제출한다.
- 진입: 요청 폼을 연다. 전제: 로그인해 있다.
- 경로: 검증한 뒤 제출한다(DEC-001).
- 정상 결과: 요청이 받아들여지고 저장된다(AC-001).
- 유효하지 않은 경우: 제출되지 않는다(RULE-001). 이때 보이는 안내와 복구 방법은 승인된 정의에 정해져 있지 않다.

## 6. Action contracts

### submit (SCR-001)

- 행위자: USR-001. 대상: DATA-001 Request.
- 전제: 로그인, 필수 입력 유효(STATE-001).
- 실행: 제출 전에 검증한다(DEC-001 / RULE-001).
- 성공(유효한 요청일 때만): 받아들여지고 INT-001을 통해 저장된다(AC-001).
- 거부(유효하지 않을 때): 제출되지 않는다(RULE-001).
- 취소, 중복 제출, 재시도: 승인된 정의에 정해져 있지 않다.

### 글자 입력·삭제 (SCR-001 요청 내용 칸)

- 결과: 입력이나 삭제가 일어날 때마다 칸 아래 오른쪽 표시가 '현재 글자 수 / 200'으로 즉시 바뀐다(RULE-002, AC-002). 데이터 쓰기는 없다.

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

- AC-001 (REQ-001, TASK-001): 유효한 요청은 받아들여지고 저장된다.
- AC-002 (REQ-001, TASK-002): 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸은 '0 / 200').

## 8. Responsive, accessibility, and downstream choice boundaries

- 제품 요구: 글자 수 표시의 위치(칸 아래 오른쪽), 형식('현재 / 200'), 즉시 갱신, 항상 보임.
- 나중 선택(시각·기술): 글꼴, 색, 간격, 200자 도달 시 강조 방식 등은 승인된 정의가 정하지 않았다. 구현이 새 동작(예: 한도 근처 색 바꿈)을 더하면 제품 결정이므로 여기로 돌아와야 한다.

## 9. Remaining unknowns, external verification, and approval state

- 열린 제품 질문: 없음(UNK-001, UNK-002 모두 RESOLVED). Manifest semantic closure summary의 모든 gap이 0이다.
- 정의되지 않은 세부(현재 범위에서 질문으로 등록되지 않음): 검증 실패 시 안내 문구, 제출 뒤 이동, 작은 화면 정보 예산. 구현 중 필요해지면 re-entry로 다룬다.
- 외부 검증: 구현·Request API 동작은 아직 확인하지 않았다.
- 승인: rev 2는 READY_FOR_REVIEW / UNAPPROVED. rev 1만 승인됨. rev 2 승인은 사용자가 위 Manifest digest를 승인해야 기록된다.

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
| GOAL-001 | 요청자가 유효한 요청 제출을 끝낸다. |
| USR-001 | 로그인한 요청자. |
| REQ-001 | 요청자는 유효한 요청을 제출할 수 있다. |
| UNK-001 | 어떤 제출 정책을 따를까? → DEC-001 (사용자 결정) |
| UNK-002 | 글자 수를 어디에 어떻게 보이나? → DEC-002 (추천 BELOW 수락) |
| DEC-001 | 제출 전에 요청을 검증한다. |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다. |
| RULE-001 | 유효한 요청만 제출할 수 있다. |
| RULE-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다. |
| FLOW-001 | 요청 폼을 연다(로그인 전제) → 검증 후 제출 → 요청이 받아들여진다. |
| SCR-001 | 요청 제출 화면. 주요 동작: 제출. |
| STATE-001 | REQUEST_READY: 필수 입력이 유효하다. |
| DATA-001 | Request: 요청 입력. 소유자 요청자. |
| INT-001 | Request API: 받아들인 요청을 저장한다. |
| AC-001 | 유효한 요청은 받아들여지고 저장된다. |
| AC-002 | 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸 '0 / 200'). |
| TASK-001 | REQ-001 구현, AC-001 확인. |
| TASK-002 | REQ-001 구현, AC-002 확인. |

## 변경 이력

- rev 1: 첫 승인 (Manifest `dd1e837b…`)
- rev 1 → rev 2 (승인 대기): 글자 수 표시 추가 — UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902 (추가 7, 변경·대체·폐기 0)
