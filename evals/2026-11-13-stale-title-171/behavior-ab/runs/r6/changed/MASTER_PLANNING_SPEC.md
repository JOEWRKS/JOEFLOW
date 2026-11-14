# MASTER PLANNING SPEC — 요청 폼

> Human-readable projection of the Product Definition at revision 2.
> Canonical authority remains `product-definition/request-form/state.json`
> (같은 폴더의 `state.json`). 이 문서와 state.json이 다르면 state.json이 맞다.
> Revision 2는 **아직 승인되지 않았다**(READY_FOR_REVIEW · UNAPPROVED).
> 마지막으로 승인된 것은 revision 1이다.

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

- **목표 (GOAL-001):** 요청자가 유효한 요청을 끝까지 제출한다.
- **사용자 (USR-001):** 로그인한 요청자(REQUESTER) 한 종류.
- **요구사항 (REQ-001):** 요청자는 유효한 요청을 제출할 수 있다. 범위는 기본 요청 워크플로이며 UI가 필요하다.
- **범위 안 (SURF-001):** 요청 제출 기능 영역.
- **범위 밖:** 결제(MONEY), 파일 업로드(FILE_UPLOAD), 비동기 처리(ASYNC), 역할별 권한(PERMISSION), 파괴적 동작(DESTRUCTIVE_ACTION)은 이 제품에 해당하지 않는다고 사용자가 확인했다(EVD-900). 로그인(AUTH) 축만 적용된다.
- **외부 의존:** 요청 API(INT-001)가 접수된 요청을 저장한다.
- **rev 2에서 더한 것:** 요청 내용 칸의 글자 수 표시(DEC-002, RULE-002, AC-002, TASK-002).

## 2. IA, navigation, and return relationships

- 화면은 하나다: **SCR-001 요청 폼** — 목적: 요청 제출.
- 진입: 요청 폼을 연다(FLOW-001 entry). 전제: 요청자가 로그인해 있다.
- 나감: 유효한 요청을 제출하면 요청이 접수된다(FLOW-001 outcome).
- 다른 화면으로의 이동·돌아오기 관계는 승인 대상 state에 정의돼 있지 않다. 제출 후 어느 화면으로 가는지는 이 문서에서 정하지 않는다.

## 3. Shared behavior, data, and state contracts

- **RULE-001 (DEC-001 근거):** 유효한 요청만 제출할 수 있다. 제출 전에 요청을 검증한다.
- **RULE-002 (DEC-002 근거, rev 2 추가):** 요청 내용 칸 아래 오른쪽에 `현재 글자 수 / 200`을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다.
- **DATA-001 Request:** 요청 입력을 담는다. 소유자는 요청자.
- **STATE-001 REQUEST_READY (SCR-001):** 필수 입력이 유효한 상태.
- 사실 근거 **EVD-902** (구현 관찰, 2026-11-12 `src/index.html`): 요청 내용 칸은 textarea 하나이고 최대 200자(`maxlength=200`)다. 200이라는 상한은 이 관찰에서 온 사실이며, 새 제품 정책이 아니다.

## 4. Screen specifications

### SCR-001 요청 폼

- **목적:** 요청 제출. 상호작용 화면(INTERACTIVE).
- **주요 동작:** submit (제출).
- **상태:** REQUEST_READY(STATE-001) — 필수 입력이 유효하면 제출할 수 있다. 유효하지 않으면 제출할 수 없다(RULE-001).
- **입력:** 요청 내용 textarea(최대 200자, EVD-902).
- **글자 수 표시 (RULE-002 / AC-002, rev 2):**
  - 위치: 요청 내용 칸 바로 아래, 오른쪽.
  - 형식: `현재 글자 수 / 200`. 빈 칸이면 `0 / 200`.
  - 시점: 글자를 넣거나 지울 때마다 즉시 바뀐다. 입력 중 항상 보인다(가까워질 때만 보이는 방식은 고르지 않았다 — UNK-002의 NEAR_LIMIT 대안).
  - 대가: 칸 아래 한 줄이 늘어난다(DEC-002에 제시된 tradeoff).
- **쓰기/저장:** 접수된 요청은 요청 API(INT-001)가 저장한다(AC-001).
- **승인 state에 없는 것(정하지 않음):** 검증 실패 시 보이는 문구와 위치, 200자에 닿았을 때 표시 색 변화 여부, 작은 화면에서의 배치 변경, 보조기기 낭독 방식. 이것들은 구현에서 새로 정하지 말고 필요하면 Product Definition으로 되돌린다.

## 5. User flows

### FLOW-001 요청 제출 (목표 GOAL-001)

- **요청자 시점 걸음:** 로그인한 요청자가 요청 폼을 연다 → 요청 내용을 적는다. 적는 동안 칸 아래 오른쪽 숫자(`n / 200`)로 남은 여유를 본다(RULE-002) → 제출한다.
- **진입:** 요청 폼을 연다. **전제:** 로그인 상태.
- **시스템 판단:** 제출 전에 검증한다(DEC-001 / RULE-001).
- **정상:** 유효하면 요청이 접수되고 저장된다(AC-001, INT-001).
- **거부:** 유효하지 않으면 제출되지 않는다(RULE-001). 거부를 화면에 어떻게 알리는지와 복구 안내는 승인 state에 정의돼 있지 않다.
- **사후 상태:** 요청이 접수된다.

## 6. Action contracts

| 동작 | 행위자 | 전제 | 실행 | 결과 | 근거 |
|---|---|---|---|---|---|
| submit (SCR-001) | 요청자(USR-001) | 로그인, 필수 입력 유효(STATE-001) | 제출 전 검증 | 유효 → 접수·저장(AC-001). 무효 → 제출 안 됨(RULE-001) | REQ-001, DEC-001, RULE-001, INT-001 |
| 요청 내용 입력/삭제 | 요청자(USR-001) | 요청 폼이 열려 있음 | 글자 추가·삭제 | 칸 아래 오른쪽 `현재 글자 수 / 200`이 즉시 갱신, 빈 칸은 `0 / 200`(AC-002) | REQ-001, DEC-002, RULE-002 |

글자 수 표시는 제출 가능 여부를 바꾸지 않는다. 표시 규칙(RULE-002)과 제출 규칙(RULE-001)은 서로 다른 규칙이다.

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

- **AC-001 (REQ-001, TASK-001):** 유효한 요청은 접수되고 저장된다.
- **AC-002 (REQ-001, TASK-002, rev 2 추가):** 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 `현재 글자 수 / 200`으로 바뀐다. 빈 칸은 `0 / 200`.

## 8. Responsive, accessibility, and downstream choice boundaries

- 승인 대상 요구: 위 RULE-001, RULE-002와 AC-001, AC-002.
- 이후 시각·기술 선택(글꼴, 색, 간격, 숫자 계산 방식 등)은 구현 쪽 선택이다. 단, 표시 위치(칸 아래 오른쪽), 형식(`n / 200`), 즉시 갱신은 바꿀 수 없다.
- 작은 화면 배치와 접근성 요구는 승인 state에 따로 정해져 있지 않다.

## 9. Remaining unknowns, external verification, and approval state

- 열린 제품 질문: 없음(UNK-001, UNK-002 모두 RESOLVED).
- **승인 전에 확인할 점 — UNK-002 / DEC-002의 근거:** UNK-002(글자 수를 어디에 어떻게 보이나)는 "추천 수락(USER_ACCEPTED_RECOMMENDATION)"으로 닫혀 있다. 그런데 근거로 남은 사용자 말(EVD-901, 다른 세션이 전한 말)은 "요청 내용 칸에 글자 수 보여줘"이고, 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이다. 위치·시점 선택지(BELOW / NEAR_LIMIT)를 보고 고른 말로는 기록돼 있지 않다(`accepted_at`도 비어 있다). rev 2를 승인하면 이 배치(칸 아래 오른쪽, 항상 표시)를 사용자가 확정하는 것이 되므로, 승인 전에 이 점을 직접 확인해야 한다. 다른 배치를 원하면 승인하지 말고 UNK-002를 다시 연다.
- 아직 돌리지 않은 확인: 실제 구현 동작, 요청 API 연동, 브라우저 렌더링 — 제품 모호함이 아니라 실행하지 않은 검증이다.
- 승인 상태: revision 2 UNAPPROVED. revision 1만 승인됨.

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

| ID | 내용 (state.json 기준 요약) |
|---|---|
| GOAL-001 | 요청자가 유효한 요청을 끝까지 제출한다. |
| USR-001 | 로그인한 요청자. |
| REQ-001 | 요청자는 유효한 요청을 제출할 수 있다(기본 요청 워크플로). |
| UNK-001 | 어떤 제출 정책을 쓸까? → RESOLVED, 사용자 결정(DEC-001). |
| UNK-002 | 글자 수를 어디에 어떻게 보이나? → RESOLVED, 추천(BELOW) 수락으로 기록(DEC-002). 9장의 확인 사항 참고. |
| DEC-001 | 제출 전에 요청을 검증한다. |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다. |
| RULE-001 | 유효한 요청만 제출할 수 있다. |
| RULE-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다. |
| FLOW-001 | 요청 폼 열기(로그인 전제) → 검증 후 제출 → 요청 접수. |
| SCR-001 | 요청 제출 화면. 주요 동작 submit. |
| STATE-001 | REQUEST_READY: 필수 입력이 유효하다. |
| DATA-001 | Request: 요청 입력을 담는다. 소유자 요청자. |
| INT-001 | Request API: 접수된 요청을 저장한다. |
| AC-001 | 유효한 요청은 접수되고 저장된다. |
| AC-002 | 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸 '0 / 200'). |
| TASK-001 | REQ-001 구현, AC-001 확인. |
| TASK-002 | REQ-001 구현, AC-002 확인. |

## 변경 이력

- rev 1: 첫 승인(요청 제출과 제출 전 검증).
- rev 2 (승인 대기): 요청 내용 칸 글자 수 표시 추가 — UNK-002, DEC-002, RULE-002, AC-002, TASK-002, 근거 EVD-901·EVD-902. 기존 레코드 변경·대체·폐기 없음.
