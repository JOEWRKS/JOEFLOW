# MASTER PLANNING SPEC — 요청 폼

> Complete human-readable projection of the Product Definition at revision 2 (READY_FOR_REVIEW, 승인 대기).
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

- 사용자 `USR-001`: 로그인한 요청자 (REQUESTER).
- 목표 `GOAL-001`: 요청자가 유효한 요청을 끝까지 제출한다.
- 요구사항 `REQ-001`: 요청자는 유효한 요청을 제출할 수 있다. 범위: 기본 요청 흐름 하나. UI 필요.
- 범위 표면 `SURF-001` Request submission (IN_SCOPE).
- 외부 의존: `INT-001` Request API — 수락된 요청을 저장한다.
- 정본에 명시된 제외 범위는 없다. 이 문서는 정본에 없는 화면·역할·규칙을 더하지 않는다.

## 2. IA, navigation, and return relationships

- 화면은 `SCR-001` 요청 폼 하나다. 진입: 요청 폼을 연다(`FLOW-001` entry). 나가는 경로: 유효한 요청이 수락된다(`FLOW-001` outcome).
- 제출 뒤 이동할 화면, 되돌아가기 동작은 정본에 정의되어 있지 않다.

## 3. Shared behavior, data, and state contracts

- `RULE-001` 유효한 요청만 제출할 수 있다 (적용: `REQ-001`; 근거 결정 `DEC-001` "제출 전에 요청을 검증한다", 사용자 결정으로 `UNK-001` 해소 — 대안 '아무 요청이나 허용'은 기각).
- `RULE-002` (rev 2 추가) 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다 (적용: `REQ-001`; 근거 결정 `DEC-002`).
- `STATE-001` REQUEST_READY — 조건: 필수 입력이 유효하다 (소유: `SCR-001`).
- `DATA-001` Request — 요청 입력을 담는다. 소유: 요청자.

## 4. Screen specifications

### `SCR-001` 요청 폼

- 목적: 요청을 제출한다 (`REQ-001`). 상호작용: INTERACTIVE. 주요 동작: 제출(submit).
- 요청 내용 칸: textarea 하나, 최대 200자(maxlength=200) — 현재 구현 관찰 사실 `EVD-902`.
- 글자 수 표시 (rev 2): 칸 아래 오른쪽, '현재 글자 수 / 200', 입력 중 항상 보이며 넣거나 지울 때마다 즉시 갱신, 빈 칸은 '0 / 200' (`RULE-002`, `DEC-002`, `AC-002`). 이 표시로 칸 아래 한 줄이 늘어난다(제시된 tradeoff).
- 상태: `STATE-001` REQUEST_READY (필수 입력 유효).
- 관련 완료 기준: `AC-001`, `AC-002`.
- 거부 시 문구, 복구 방법, 반응형·접근성 세부는 정본에 정의되어 있지 않다(§8, §9).

## 5. User flows

### `FLOW-001` 요청 제출

- 진입: 요청 폼을 연다. 전제: 요청자가 로그인되어 있다.
- 요청자 동작: 요청 내용을 입력한다. 입력하는 동안 글자 수 표시가 바로 바뀐다(`RULE-002`).
- 시스템 판단: 제출 전에 요청을 검증한다(`DEC-001`, `RULE-001`).
- 정상: 유효한 요청이 수락된다(outcome), 저장된다(`AC-001`, `INT-001`).
- 실패: 유효하지 않은 요청은 제출되지 않는다(`RULE-001`). 실패 시 보이는 결과·재시도는 정본에 없다.
- 완료 기준: `AC-001`, `AC-002`.

## 6. Action contracts

### submit (`SCR-001`)

- 행위자: 로그인한 요청자 `USR-001`. 대상: 요청 `DATA-001`.
- 전제: 필수 입력이 유효하다(`STATE-001`).
- 실행: 제출 전 검증(`DEC-001`) 뒤 Request API(`INT-001`)로 저장.
- 성공 결과: 유효한 요청이 수락·저장된다(`AC-001`) — 유효한 경우에만.
- 거부: 유효하지 않으면 제출되지 않는다(`RULE-001`). 표시·복구·취소·중복 제출 처리는 정의되지 않음.

### 요청 내용 입력 (`SCR-001`, rev 2)

- 글자를 넣거나 지울 때마다 '현재 글자 수 / 200' 표시가 즉시 바뀐다(`RULE-002`, `AC-002`). 데이터 변경 없음(표시만).

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

- `AC-001` (`REQ-001`, `TASK-001`): 유효한 요청은 수락되고 저장된다.
- `AC-002` (`REQ-001`, `TASK-002`, rev 2): 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸은 '0 / 200').

## 8. Responsive, accessibility, and downstream choice boundaries

- 승인 대상 제품 요구: 표시 위치(칸 아래 오른쪽), 형식('현재 / 200'), 갱신 시점(입력·삭제 즉시), 항상 표시.
- 후속 선택에 남는 것: 글꼴·색·간격 등 시각 표현. 반응형·접근성 요구는 정본에 별도 기록이 없다.

## 9. Remaining unknowns, external verification, and approval state

- 열린 제품 질문: 없음(`UNK-001`, `UNK-002` 모두 RESOLVED).
- 확인 권장: `DEC-002`는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(`EVD-901`, RELAYED_USER_INTENT)를 추천안 BELOW(항상 표시) 수락으로 기록했다. 원문이 위치·표시 시점을 직접 고르지 않았으므로 승인 때 사용자가 '항상 표시'를 확인해야 한다. 대안: NEAR_LIMIT(180자부터만 표시).
- 승인 상태: revision 2 READY_FOR_REVIEW / UNAPPROVED. 마지막 승인 revision 1.
- 구현·런타임 검증은 실행되지 않았다.

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
| GOAL-001 | 요청자가 유효한 요청을 완료한다 |
| USR-001 | 로그인한 요청자 |
| REQ-001 | 요청자는 유효한 요청을 제출할 수 있다 |
| UNK-001 | 어떤 제출 정책을 쓰나? → RESOLVED (`DEC-001`) |
| UNK-002 | 글자 수를 어디에 어떻게 보이나? → RESOLVED (`DEC-002`) |
| DEC-001 | 제출 전에 요청을 검증한다 (사용자 결정) |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다 (추천 수락) |
| RULE-001 | 유효한 요청만 제출할 수 있다 |
| RULE-002 | 칸 아래 오른쪽 '현재 글자 수 / 200', 입력·삭제 때마다 즉시 갱신 |
| FLOW-001 | 요청 폼 열기 → 검증·제출 → 요청 수락 (전제: 로그인) |
| SCR-001 | 요청 폼 — 요청 제출, 주요 동작 submit |
| STATE-001 | REQUEST_READY — 필수 입력 유효 |
| DATA-001 | Request — 요청 입력, 요청자 소유 |
| INT-001 | Request API — 수락된 요청 저장 |
| AC-001 | 유효한 요청은 수락·저장된다 |
| AC-002 | 입력·삭제 시 표시가 즉시 '현재 / 200'으로 바뀐다(빈 칸 '0 / 200') |
| TASK-001 | REQ-001 구현, AC-001 |
| TASK-002 | REQ-001 구현, AC-002 |

## 변경 이력

- rev 1: 첫 승인
- revision 1에서 rev 2로: 요청 내용 칸 글자 수 표시 추가(`EVD-901`, `EVD-902`, `UNK-002`, `DEC-002`, `RULE-002`, `AC-002`, `TASK-002`) — 승인 대기
