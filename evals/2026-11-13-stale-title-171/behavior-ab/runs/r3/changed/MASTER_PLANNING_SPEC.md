# MASTER PLANNING SPEC — 요청 폼

> 승인 대상 Product Definition을 사람이 읽도록 옮긴 투영 문서입니다.
> 정본(canonical authority)은 같은 폴더의 `state.json`(project `semantic-closure-v2`)이며, 이 문서와 다르면 `state.json`이 우선합니다.
> 현재 revision 2는 **승인 대기(UNAPPROVED)** 상태입니다. 승인 전까지 rev 2 내용(글자 수 표시)은 승인된 기획이 아닙니다.

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

## 1. 제품, 사용자, 목표, 범위

- **목표** (GOAL-001): 요청자가 유효한 요청 제출을 끝낸다.
- **사용자** (USR-001): 로그인한 요청자(REQUESTER). 역할은 하나뿐입니다.
- **요구사항** (REQ-001): 요청자는 유효한 요청을 제출할 수 있다. 범위는 기본 요청 흐름이며 화면이 필요합니다.
- **범위 영역** (SURF-001, Request submission): IN_SCOPE, MATERIAL.
- **적용하지 않는 축** (EVD-900, 사용자 확인): 결제(MONEY), 파일 업로드(FILE_UPLOAD), 비동기 처리(ASYNC), 권한 구분(PERMISSION), 파괴적 동작(DESTRUCTIVE_ACTION) 등은 N/A. 인증(AUTH)은 ACTIVE입니다.
- **외부 의존**: INT-001 Request API — 수락된 요청을 저장합니다.
- **rev 2 추가 범위**: 요청 내용 칸의 글자 수 표시(DEC-002, RULE-002, AC-002, TASK-002). 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901, 상위 세션이 전달한 RELAYED_USER_INTENT).

## 2. IA, 이동, 돌아가기

- 화면은 하나입니다: **SCR-001 요청 화면** — 목적: 요청 제출.
- 진입: 요청 폼을 연다(FLOW-001 entry). 전제: 요청자가 로그인해 있다.
- 나가기: 제출이 수락되면 흐름이 끝납니다(FLOW-001 outcome). 수락 뒤 이동할 화면이나 돌아가기 동작은 state에 정의되어 있지 않습니다(이 투영에서 만들지 않음).

## 3. 공통 규칙, 데이터, 상태

- **RULE-001**: 유효한 요청만 제출할 수 있다. (근거 DEC-001 ← UNK-001, 사용자가 '검증 후 제출'을 선택. 선택지의 결과: 유효하지 않은 요청은 거절된다.)
- **RULE-002** (rev 2 추가): 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 보이고, 글자를 넣거나 지울 때마다 바로 바꾼다. (근거 DEC-002 ← UNK-002, 추천안 BELOW 수락)
- **STATE-001 REQUEST_READY** (SCR-001): 필수 입력이 유효한 상태.
- **DATA-001 Request**: 요청 입력을 담는다. 소유: 요청자.
- **관찰된 구현 사실** (EVD-902, FACTUAL): 요청 내용 칸은 textarea 하나이며 최대 200자(maxlength=200). 글자 수 표시의 분모 200은 이 사실에 맞춘 것입니다.
- "유효함"의 구체 조건(필수 항목 목록, 형식 등)은 state에 따로 정의되어 있지 않습니다.

## 4. 화면 명세 — SCR-001 요청 화면

- **목적**: 요청 제출. 관련 요구사항 REQ-001. 상호작용 화면(INTERACTIVE).
- **주요 동작**: submit(제출).
- **입력**: 요청 내용 textarea(최대 200자, EVD-902).
- **글자 수 표시** (RULE-002, DEC-002): 칸 아래 오른쪽에 '현재 글자 수 / 200'. 입력 중 항상 보이고(평소에 숨기고 180자부터 보이는 NEAR_LIMIT 안은 채택하지 않음), 글자를 넣거나 지울 때마다 즉시 갱신. 빈 칸이면 '0 / 200'(AC-002). 감수한 대가: 칸 아래 한 줄이 늘어남.
- **상태**: 제출 가능 상태 = REQUEST_READY(필수 입력 유효, STATE-001). 유효하지 않으면 제출되지 않음(RULE-001).
- **읽기/쓰기**: 수락된 요청은 Request API(INT-001)로 저장(AC-001).
- **UX 상태 커버리지**: default·loading·empty·partial·success·error·disabled·unauthenticated 등은 ux_coverage에서 위 레코드(SCR-001, FLOW-001, RULE-001, STATE-001, AC-001, DEC-001)에 묶여 있습니다. 문구·배치 같은 시각 세부는 정의되어 있지 않습니다.
- 관련 완료 기준: AC-001, AC-002.

## 5. 사용자 흐름 — FLOW-001

요청자 입장에서: 로그인한 상태로 요청 폼을 열고, 요청 내용을 입력하면서 칸 아래 오른쪽 '현재 / 200'으로 남은 분량을 확인하고, 제출합니다. 유효하면 요청이 수락됩니다.

| 항목 | 내용 | 근거 |
|---|---|---|
| 진입 | 요청 폼을 연다 | FLOW-001 |
| 전제 | 요청자가 로그인해 있다 | FLOW-001, USR-001 |
| 사용자 동작 | 내용 입력(글자 수 즉시 표시) 후 제출 | SCR-001, RULE-002 |
| 시스템 판단 | 요청이 유효한가 | RULE-001, DEC-001 |
| 정상 | 검증 통과 → 제출 → 요청 수락·저장 | FLOW-001, AC-001, INT-001 |
| 실패 | 유효하지 않은 요청은 제출되지 않는다(거절) | RULE-001, UNK-001 OPT-A 결과 |
| 복구·재시도 | state에 별도 정의 없음 | — |
| 종료 상태 | 요청이 수락됨 | FLOW-001 |

## 6. 동작 계약 — submit (SCR-001)

- 주체: 로그인한 요청자(USR-001). 대상: Request(DATA-001).
- 전제: REQUEST_READY(필수 입력 유효, STATE-001).
- 실행: 제출 전에 검증(DEC-001).
- 성공: 유효한 요청이 수락되고 저장된다(AC-001, INT-001).
- 거절: 유효하지 않으면 제출 불가(RULE-001). 거절 시 화면 표현·문구는 정의되어 있지 않음.
- 글자 수 표시는 제출 동작과 별개로 입력할 때마다 항상 적용됩니다(RULE-002). 제출 성공·실패 조건을 바꾸지 않습니다.

### Projection-fidelity rule

- 승인 원본의 조건과 분기를 그대로 둔다.
- 예외 경로를 모든 성공/실패의 기본 결과로 바꾸지 않는다.
- 중복을 줄일 때도 stable ID와 적용 조건을 남긴다.
- 승인 근거로 추적되지 않는 분기는 넣지 않는다.

## 7. 완료 기준

- **AC-001** (REQ-001, TASK-001): 유효한 요청이 수락되고 저장된다.
- **AC-002** (REQ-001, TASK-002, rev 2 추가): 요청 내용에 글자를 넣거나 지우면 칸 아래 오른쪽 표시가 즉시 '현재 글자 수 / 200'으로 바뀐다(빈 칸은 '0 / 200').

## 8. 반응형·접근성·후속 선택 경계

- 승인 요구: 글자 수 표시 위치(칸 아래 오른쪽)와 형식('현재 / 200'), 즉시 갱신.
- 후속 선택(디자인·구현): 글꼴, 색, 간격, 200자 근접 시 강조 여부, 스크린리더 알림 방식 등. 이들은 state에 정의되어 있지 않으므로 제품 정책을 새로 만들면 안 되고, 정책이 필요하면 Product Definition으로 돌아와야 합니다.

## 9. 남은 질문, 외부 확인, 승인 상태

- 열린 제품 질문: 없음(UNK-001, UNK-002 모두 RESOLVED).
- 승인: rev 2는 UNAPPROVED. 위 Approval Manifest(`6b50eb33…2906`)에 대한 사용자의 명시적 승인이 필요합니다.
- 참고: rev 2 근거 EVD-901은 상위 세션이 전달한 사용자 원문입니다.
- 구현·런타임 확인: 아직 실행 안 됨(제품 모호성 아님).

## 10. Source map

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
| GOAL-001 | 요청자가 유효한 요청 제출을 끝낸다 |
| USR-001 | 로그인한 요청자 |
| REQ-001 | 요청자는 유효한 요청을 제출할 수 있다 |
| UNK-001 | 어떤 제출 정책을 따를까 → RESOLVED: 검증 후 제출(DEC-001) |
| UNK-002 | 글자 수를 어디에 어떻게 보일까 → RESOLVED: 추천안 BELOW 수락(DEC-002) |
| DEC-001 | 제출 전에 요청을 검증한다 |
| DEC-002 | 요청 내용 칸 아래 오른쪽에 '현재 글자 수 / 200'을 입력할 때마다 바로 보인다 |
| RULE-001 | 유효한 요청만 제출할 수 있다 |
| RULE-002 | 칸 아래 오른쪽 '현재 글자 수 / 200', 넣거나 지울 때마다 즉시 갱신 |
| FLOW-001 | 폼 열기(로그인 전제) → 검증 후 제출 → 요청 수락 |
| SCR-001 | 요청 제출 화면, 주요 동작 submit |
| STATE-001 | REQUEST_READY: 필수 입력이 유효 |
| DATA-001 | Request: 요청 입력, 요청자 소유 |
| INT-001 | Request API: 수락된 요청 저장 |
| AC-001 | 유효한 요청이 수락되고 저장된다 |
| AC-002 | 넣거나 지우면 즉시 '현재 글자 수 / 200'(빈 칸 '0 / 200') |
| TASK-001 | REQ-001 구현, AC-001 확인 |
| TASK-002 | REQ-001 구현, AC-002 확인 |

## 변경 이력

- rev 1: 첫 승인 (Manifest `dd1e837b…`)
- rev 1 → rev 2 (승인 대기): 글자 수 표시 추가 — UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902 (추가 7 · 변경 0 · 대체 0 · 폐기 0)
