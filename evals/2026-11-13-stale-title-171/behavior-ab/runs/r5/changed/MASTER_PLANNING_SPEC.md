# MASTER PLANNING SPEC — 요청 폼

> Complete human-readable projection of the Product Definition at revision 2
> (READY_FOR_REVIEW, not yet approved).
> Canonical authority remains `product-definition/request-form/state.json`.

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

- **GOAL-001** 요청자가 유효한 요청 제출을 마친다.
- **USR-001** 로그인한 요청자(actor kind REQUESTER).
- **REQ-001** 요청자는 유효한 요청을 제출할 수 있다. 범위: 주 요청 흐름. UI 있음. Materiality MATERIAL.
- **범위 안**: SURF-001 요청 제출(FEATURE_AREA, IN_SCOPE, 권한 근거 REQ-001).
- **범위 밖**: MONEY, FILE_UPLOAD, ASYNC 토폴로지는 사용자가 해당 없음으로 확인(EVD-900).
- **외부 의존**: INT-001 요청 API — 접수된 요청을 저장한다.

## 2. IA, navigation, and return relationships

화면은 SCR-001 하나다. 진입은 요청 폼 열기(FLOW-001 entry), 전제는 로그인 상태다.
제출 후의 이동, 이탈·복귀 동작은 state에 정의되어 있지 않다(이 문서에서 만들지 않는다).

## 3. Shared behavior, data, and state contracts

- **RULE-001** 유효한 요청만 제출할 수 있다. 적용: REQ-001. 근거: DEC-001(사용자가 UNK-001에서 OPT-A '검증 후 제출'을 선택, 결과 '유효하지 않은 요청은 거부된다').
- **RULE-002** (rev 2 추가) 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다. 적용: REQ-001. 근거: DEC-002.
- **STATE-001** REQUEST_READY — 소유 SCR-001, 조건: 필수 입력이 유효함.
- **DATA-001** Request — 요청 입력을 담는다. 소유: REQUESTER.
- **200자 한도**: 요청 내용 칸은 textarea 하나, maxlength=200(EVD-902, 2026-11-12 src/index.html 관찰, FACTUAL).

## 4. Screen specifications

### SCR-001 요청 폼

- 목적: 요청 제출(REQ-001). 상호작용: INTERACTIVE. 주 동작: submit.
- 입력: 요청 내용 textarea(최대 200자, EVD-902).
- 글자 수 표시(RULE-002, AC-002): 칸 아래 오른쪽, 형식 '현재 글자 수 / 200', 빈 칸이면 '0 / 200', 글자를 넣거나 지울 때마다 즉시 갱신. 입력 중 항상 보인다(UNK-002 선택지 BELOW; 대안 NEAR_LIMIT '180자부터만 보임'은 채택되지 않음). 대가: 칸 아래 한 줄이 늘어난다.
- 제출 가능 상태: STATE-001(필수 입력이 유효할 때). 유효하지 않으면 제출되지 않는다(RULE-001).
- 실패 문구, 복구 방법, 반응형·접근성 세부, 최소 화면 정보 예산은 state에 별도 기록이 없다.

## 5. User flows

### FLOW-001 요청 제출 (GOAL-001)

- 진입: 요청 폼을 연다. 전제: 요청자가 로그인되어 있다.
- 경로: 입력을 검증하고 제출한다. 입력 중 글자 수가 즉시 갱신된다(RULE-002).
- 성공: 요청이 접수된다(AC-001: 유효한 요청은 접수되고 저장된다, INT-001).
- 실패: 입력이 유효하지 않으면 제출할 수 없다(RULE-001). 실패 후 복구 절차는 state에 정의되어 있지 않다.

## 6. Action contracts

### submit (SCR-001)

- 행위자: USR-001. 전제: 로그인, STATE-001 REQUEST_READY.
- 실행: 요청 입력을 검증한 뒤 제출한다(DEC-001).
- 성공(입력이 유효할 때만): 요청이 접수·저장된다(AC-001, INT-001, DATA-001).
- 거부(입력이 유효하지 않을 때): 제출되지 않는다(RULE-001).
- 취소·동시성·멱등성: state에 정의 없음.

### 요청 내용 입력 (SCR-001)

- 글자를 넣거나 지울 때마다 '현재 글자 수 / 200' 표시가 즉시 바뀐다(RULE-002, AC-002). 데이터 효과 없음(표시만).

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

- **AC-001** (REQ-001) 유효한 요청은 접수되고 저장된다. — TASK-001
- **AC-002** (REQ-001, rev 2 추가) 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸은 '0 / 200'). — TASK-002

## 8. Responsive, accessibility, and downstream choice boundaries

승인 대상 제품 요구는 위 1~7절뿐이다. 글자 수 표시의 글꼴·색·크기, 200자 도달 시 시각 강조 여부 등은
state에 없으므로 제품 요구가 아니며, 새 동작(예: 한도 근처 경고)을 더하려면 Product Definition으로 되돌아온다.

## 9. Remaining unknowns, external verification, and approval state

- 열린 질문: 없음(UNK-001, UNK-002 모두 RESOLVED).
- **승인 시 확인할 점**: UNK-002는 `USER_ACCEPTED_RECOMMENDATION`으로 닫혀 있으나, 기록된 사용자 원문은
  다른 세션이 전달한 "요청 내용 칸에 글자 수 보여줘"(EVD-901, RELAYED_USER_INTENT)이고 이는 질문
  "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이다. 위치·표시 시점(BELOW vs NEAR_LIMIT)을 고른 말은 아니다.
  revision 2 승인이 BELOW 확정을 겸한다. 사용자가 다르게 원하면 새 revision이 필요하다.
- 200자 한도는 관찰된 구현(EVD-902)에서 온 사실이며 별도 제품 결정 기록은 없다.
- 승인 상태: revision 2 READY_FOR_REVIEW / UNAPPROVED. 마지막 승인은 revision 1.
- 런타임·렌더 검증: 실행되지 않음.

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
| GOAL-001 | 요청자가 유효한 요청 제출을 마친다. |
| USR-001 | 로그인한 요청자. |
| REQ-001 | 요청자는 유효한 요청을 제출할 수 있다. |
| UNK-001 | 어떤 제출 정책을 따를까? → RESOLVED(DEC-001, 사용자 결정) |
| UNK-002 | 글자 수를 어디에 어떻게 보이나? → RESOLVED(DEC-002, 추천 BELOW 수락으로 기록; 9절 참고) |
| DEC-001 | 제출 전에 요청을 검증한다. |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다. |
| RULE-001 | 유효한 요청만 제출할 수 있다. |
| RULE-002 | 칸 아래 오른쪽 '현재 글자 수 / 200', 넣거나 지울 때마다 즉시 갱신. |
| FLOW-001 | 요청 폼 열기 → 검증 후 제출 → 요청 접수(전제: 로그인). |
| SCR-001 | 요청 제출 화면, 주 동작 submit. |
| STATE-001 | REQUEST_READY — 필수 입력이 유효함. |
| DATA-001 | Request — 요청 입력, 소유 REQUESTER. |
| INT-001 | 요청 API — 접수된 요청 저장. |
| AC-001 | 유효한 요청은 접수되고 저장된다. |
| AC-002 | 넣거나 지우면 즉시 '현재 글자 수 / 200'(빈 칸 '0 / 200'). |
| TASK-001 | REQ-001 구현, AC-001 확인. |
| TASK-002 | REQ-001 구현, AC-002 확인. |

## 변경 이력

- rev 1: 첫 승인
- revision 1에서 rev 2로: 글자 수 표시(UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902 추가). 승인 대기.
