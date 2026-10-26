# JOEFLOW 로드맵

현재: U1-1(UTF-8 출력)을 별도 워크트리 `JOEFLOW-reinforce`(브랜치 `claude/joeflow-reinforce`, 기준 `9891dc3`)에서 구현, 미커밋. 실행 중인 오목 세션이 쓰는 `JOEFLOW-ux` 사본은 건드리지 않는다. 나머지 U1 항목은 사용자가 이번에는 진행하지 않기로 함(2026-10-26).
다음 작업: U1-1 커밋 여부 사용자 결정. 그 뒤 U1-2·U1-3부터 다시 고른다. 전체 회귀: `python -B -m unittest discover -s tests -p "test*.py"`.

상태어: not started · in progress · verification pending · complete · deferred

## U1. 오목 실사용 마찰 보강 (2026-10-26 계획)

근거 자료(읽기 전용): `_data/gomoku-audit-log.md`(1·2차 점검), `_data/joe-tools-friction-log.md`(26건), AI-Gomoku `product-definition/ai-coach/`(`freeze.py`·`freeze18~30.py` 14개, `build_state.py` 1,435줄, approval-manifest rev 15~30, `state.json` rev 30). 대조 기준 커밋 `9891dc3`.

### 판정

| # | 마찰 | 판정 | 근거 |
|---|---|---|---|
| F1 | 승인 기록 도구 없음, 시각 수동 작성 | 유효 | `scripts/`에 승인 기록 CLI 없음. `approval_v2._approval_analysis`가 `approved_by="user"`와 유효 UTC `approved_at`을 요구. 오목 `build_state.py`가 승인 15회를 `APPROVEDnn = {digest, revision, at}` + `approval_history` 덧붙이기로 손으로 씀 |
| F2 | 개정(rev N+1) 도구 없음, freeze 스크립트 복사 | 유효 | 바인딩 재생성·해시 갱신 CLI 없음(`authority_binding_value.py`는 셀 하나만 출력). `freeze30.py` 150줄 중 바인딩 절 96줄이 `freeze29.py`와 8줄만 다름 |
| F3 | 오류 메시지가 허용 값을 안 알려 줌 | 유효 | `grill_v2.py` 오류 69곳 중 허용 값·기대 값을 담은 문구 0곳. 예: `invalid_evidence_authority_class` "authority class is not supported by source kind"(허용 class 목록 없음), `reasoning_refs must resolve to permitted …`(허용 종류 없음), `alternatives_presented`(기대 목록 없음) |
| F4 | unknown 하나에 필드 약 20개 | 유효 | 오목 rev 30 unknown 레코드 키 20개 + materiality 6개. 레코드 생성 CLI·템플릿 없음(오목은 `unk()`·`mat()`·`opt()` 도우미를 직접 만듦) |
| F5 | Windows 한글 출력 깨짐 | 유효(부분 해결) | v1.1.0에서 `build_approval_manifest.py`만 UTF-8 경계 보강. `next_product_question.py`·`authority_binding_value.py`·`build_discovery_baseline.py`·`migrate_state.py`는 `ensure_ascii=False`로 그대로 `print` → cp949 파이프에서 `—`로 `UnicodeEncodeError` 재현(2026-10-26) |
| F6 | 기능 추가형 기획 모드 없음 | 유효 | `state_validation_v2.BOOTSTRAP_MODES = {NEW_PRODUCT, EXISTING_PRODUCT_RECONCILIATION}`. 오목은 `NEW_PRODUCT`로 우회 |
| F7 | 서버용 점검 항목이 로컬 앱에도 강제 | 유효 | `grill-packs/async.json` 활성 조건이 `ASYNC_PROCESS` 표면뿐(로컬 계산 구분 없음). UX 22축(permission·session_expiration 등)도 일괄 N/A 경로 없음. 오목 rev 30에서 N/A 근거를 셀마다 반복 |
| F8 | 승인 전 구현이 쌓이는 흐름이 안 드러남 | 유효 | 오목 git: rev 26~30 모두 구현 커밋이 JOEFLOW freeze 커밋보다 1초 먼저, 승인은 그 뒤. rev 26·28(및 13·14)은 따로 승인되지 않고 다음 Manifest에 묶임(`approval_history` revision 12,15~25,27,29,30). JOEFLOW에는 "현재 rev > 승인 rev"·"승인 없이 지나간 rev"를 보여 주는 명령이 없고, SKILL 규칙도 승인 전 구현 여부를 다루지 않음 |

### 계획 (영향 ÷ 비용 순)

| ID | 항목 | 마찰 | 영향 | 비용 | 상태 | Check |
|---|---|---|---|---|---|---|
| U1-1 | 사람이 읽는 CLI 4개의 표준 출력·오류를 UTF-8로 고정(`scripts/cli_output.py`, `PYTHONIOENCODING`을 지정하면 그 값을 따름) | F5 | 중(Windows 매 실행) | 작음 | verification pending | cp949 콘솔 파이프로 한글·`—` 출력 CLI 4개 실행 시 오류 0, 바이트가 UTF-8, 기존 출력 바이트 비교 시험 통과 |
| U1-2 | `record_approval.py`: 사용자가 말한 Manifest digest·revision을 현재 state로 다시 계산해 대조한 뒤 `approval`·`approval_history`·`CLOSED`를 한 번에 기록. 시각은 `--at`(사용자 메시지 시각) 또는 `--at observed`(기록 시각, 출력에 표시) | F1 | 높음(rev마다) | 중간 | not started | digest·revision 불일치·READY_FOR_REVIEW 아님·시각 없음 거부 시험, 성공 후 `validate_state`·`validate_closure` 통과, 오목 rev 30 사본에 재현해 손 기록과 같은 결과 |
| U1-3 | 승인 현황 명령: 현재 rev·승인 rev·승인 없이 지난 rev·마지막 승인 이후 바뀐 레코드 수를 한 화면에. SKILL에 "승인 전 구현은 사용자 지시가 있을 때만, 보고에 승인 대기 표시" 규칙 | F8 | 높음(보이지 않던 위험) | 작음~중간 | not started | 오목 rev 30 사본에서 rev 13·14·26·28이 "따로 승인 안 됨"으로 나옴, UNAPPROVED 상태에서 "승인 대기 rev N" 표시 |
| U1-4 | 자주 걸리는 검증 오류에 허용 값·기대 값 넣기(authority class, reasoning_refs 종류, alternatives_presented, 축 허용 타입, ACTIVE rationale null) | F3 | 중간 | 중간 | not started | 오목 마찰 기록 3·8·12·16·24번 오류를 재현하면 메시지에 허용 값이 나옴, 오류 코드 불변 |
| U1-5 | 개정 도우미: `open_revision`(rev+1·UNAPPROVED·비CLOSED 한 번에), `refresh_bindings`(가리키는 내용이 바뀐 바인딩만 목록으로 보여 주고 확인 플래그로 해시 갱신) | F2 | 높음 | 큼 | not started | 오목 rev 29→30을 사본에서 도우미로 재현해 freeze 스크립트 없이 같은 state digest, 내용이 바뀐 바인딩을 묻지 않고 갱신하지 않음 |
| U1-6 | 레코드 작성 CLI(`add_unknown`·`add_decision` 등): 기본값을 채우고 바로 검증 | F4 | 중간 | 중간~큼 | not started | 최소 인자로 만든 unknown이 검증 통과, 오목 질문 1건을 CLI로 재현 |
| U1-7 | 로컬·무계정 앱 프로필: ASYNC 경량 축, UX 계정·세션 축 일괄 N/A 한 근거 | F7 | 중간 | 큼(계약 의미 변경) | not started | 프로필 없는 기존 fixture 결과 불변, 오목 사본에서 N/A 반복 셀 수 감소 측정 |
| U1-8 | `FEATURE_EXTENSION` 부트스트랩 모드 | F6 | 중간 | 매우 큼(스키마·계약 버전) | deferred | 별도 설계 문서와 A/B 뒤 결정 |

범위 밖 후보(마찰 기록에서 함께 나옴, 이번 계획에 넣지 않음): 사용자 직접 지시를 질문 없이 결정으로 기록(22번), 대체·폐기 연쇄 자동 추적(26번), 질문 종료와 FREEZE 사이 중간 상태(15·26번).
