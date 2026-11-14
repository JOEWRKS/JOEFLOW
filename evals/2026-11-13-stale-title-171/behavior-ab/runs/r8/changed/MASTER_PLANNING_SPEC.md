# MASTER PLANNING SPEC — 요청 폼 (revision 2)

> Complete human-readable projection of the Product Definition.
> Canonical authority remains `state.json` (this folder). This document never overrides it.

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

- **목표 GOAL-001**: 요청자가 유효한 요청 제출을 끝낸다.
- **사용자 USR-001**: 로그인한 요청자(REQUESTER).
- **요구사항 REQ-001**: 요청자는 유효한 요청을 제출할 수 있다. 범위: 기본 요청 흐름(UI 필요).
- **외부 의존 INT-001**: Request API — 수락된 요청을 저장한다.
- rev 2 추가 범위: 요청 내용 칸의 글자 수 표시(DEC-002, RULE-002, AC-002, TASK-002).

## 2. IA, navigation, and return relationships

- 화면은 하나: **SCR-001** 요청 제출 화면(INTERACTIVE). 진입은 요청 폼 열기(FLOW-001 entry).
- state.json에는 다른 화면으로의 이동·복귀 관계가 정의되어 있지 않다.

## 3. Shared behavior, data, and state contracts

- **RULE-001**: 유효한 요청만 제출할 수 있다(REQ-001에 적용). 근거 결정 DEC-001: 제출 전에 요청을 검증한다(UNK-001 사용자 결정).
- **RULE-002**: 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다(REQ-001에 적용). 근거 결정 DEC-002(UNK-002, 사용자가 권고안 수락), 근거 사실 EVD-902: 요청 내용 칸은 textarea 하나, 최대 200자(maxlength=200).
- **DATA-001 Request**: 요청 입력을 담는다. 소유: REQUESTER.
- **STATE-001 REQUEST_READY** (SCR-001): 필수 입력이 유효한 상태.

## 4. Screen specifications

**SCR-001 — 요청 제출**
- 목적: 요청을 제출한다. 관련 요구사항 REQ-001.
- 주요 동작: `submit` — 필수 입력이 유효할 때(STATE-001)만 제출된다(RULE-001).
- 입력: 요청 내용 textarea(최대 200자, EVD-902). 칸 아래 오른쪽에 '현재 글자 수 / 200' 표시, 입력·삭제 즉시 갱신, 빈 칸은 '0 / 200'(RULE-002, AC-002).
- 쓰기: 수락된 요청은 INT-001로 저장(AC-001).

## 5. User flows

**FLOW-001** (GOAL-001)
- 진입: 요청 폼을 연다. 전제: 요청자가 로그인해 있다.
- 경로: 입력 → 검증 → 제출. 입력 중 글자 수 표시가 계속 갱신된다(RULE-002).
- 결과: 요청이 수락된다(AC-001).
- 검증 실패 시 화면 반응은 state.json에 별도 정의가 없다(RULE-001은 "유효한 요청만 제출"까지만 정한다).

## 6. Action contracts

| 동작 | 행위자 | 전제 | 성공 | 거부 | 근거 |
|---|---|---|---|---|---|
| submit | USR-001 | 로그인, STATE-001(필수 입력 유효) | 요청 수락·저장(INT-001) | 유효하지 않으면 제출되지 않음 | REQ-001, RULE-001, DEC-001, AC-001 |
| 요청 내용 입력·삭제 | USR-001 | SCR-001 열림 | 표시가 즉시 '현재 글자 수 / 200'으로 바뀜 | 200자 초과 입력은 칸 자체가 받지 않음(maxlength, EVD-902) | RULE-002, DEC-002, AC-002 |

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional path into the universal success/failure result.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

- **AC-001** (REQ-001): 유효한 요청은 수락되고 저장된다. — TASK-001
- **AC-002** (REQ-001): 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸은 '0 / 200'). — TASK-002

## 8. Responsive, accessibility, and downstream choice boundaries

- 승인 대상은 표시 위치(칸 아래 오른쪽), 형식('현재 / 200'), 즉시 갱신이다. 글꼴·색 등 시각 선택은 후속 디자인 몫이다.

## 9. Remaining unknowns, external verification, and approval state

- 열린 질문 없음: UNK-001, UNK-002 모두 RESOLVED.
- 승인: revision 2는 READY_FOR_REVIEW / UNAPPROVED. 사용자 승인 대기.
- 구현·런타임 검증은 아직 수행되지 않았다.

## 10. Source map

Canonical pointers are `state.json` `/objects/<kind>` by stable ID. The record table below is generated.

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
| UNK-001 | 어떤 제출 정책을 따르나? — RESOLVED(DEC-001) |
| UNK-002 | 글자 수를 어디에 어떻게 보이나? — RESOLVED(DEC-002) |
| DEC-001 | 제출 전에 요청을 검증한다. |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다. |
| RULE-001 | 유효한 요청만 제출할 수 있다. |
| RULE-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다. |
| FLOW-001 | 요청 폼 열기 → 검증 후 제출 → 요청 수락. |
| SCR-001 | 요청 제출 화면. 동작: submit. |
| STATE-001 | REQUEST_READY: 필수 입력이 유효함. |
| DATA-001 | Request: 요청 입력. 소유 REQUESTER. |
| INT-001 | Request API: 수락된 요청 저장. |
| AC-001 | 유효한 요청은 수락되고 저장된다. |
| AC-002 | 글자 입력·삭제 시 표시가 즉시 '현재 글자 수 / 200'(빈 칸 '0 / 200'). |
| TASK-001 | REQ-001 구현, AC-001 확인. |
| TASK-002 | REQ-001 구현(글자 수 표시), AC-002 확인. |

## 변경 이력

- rev 1: 첫 승인
- rev 1 → rev 2: 요청 내용 글자 수 표시 추가(UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902). 승인 대기.
