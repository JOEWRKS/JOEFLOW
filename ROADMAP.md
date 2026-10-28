# JOEFLOW 로드맵

현재: 별도 워크트리 `JOEFLOW-reinforce`(브랜치 `claude/joeflow-reinforce`)에서 작업한다. U1-1~U1-3 complete·설치본 반영. 2026-10-28 사용자 결정으로 U1-4·U1-5·U1-6을 한 번에 진행 중(항목별 커밋, 끝에 설치본 반영, 새 SKILL 규칙 A/B 4회, JOEFLOW-ux fast-forward 후 오목 세션 알림). U1-7·U1-8은 이번 범위 밖. 푸시 안 함.
다음 작업: 남은 결정(experience pass 설치·버전 출시·브랜치 합치기·U1-7/U1-8·추가 A/B)은 사용자 선택 대기. 2026-10-28 결정: 승인 시각을 모르면 기록 시각(`--at observed`)을 허용하고 보고에 기록 시각임을 밝힌다.

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
| U1-1 | 사람이 읽는 CLI 4개의 표준 출력·오류를 UTF-8로 고정(`scripts/cli_output.py`, `PYTHONIOENCODING`을 지정하면 그 값을 따름) | F5 | 중(Windows 매 실행) | 작음 | complete | cp949 콘솔 파이프로 한글·`—` 출력 CLI 4개 실행 시 오류 0, 바이트가 UTF-8, 기존 출력 바이트 비교 시험 통과 — 전체 회귀 1,135개 중 새 실패 0(기준과 같은 환경 원인 8건), 커밋 `08d376f` |
| U1-2 | `record_approval.py`: 사용자가 말한 Manifest digest·revision을 현재 state로 다시 계산해 대조한 뒤 `approval`·`approval_history`·`CLOSED`를 한 번에 기록. 시각은 `--at`(사용자 메시지 시각) 또는 `--at observed`(기록 시각, 출력에 표시) | F1 | 높음(rev마다) | 중간 | complete | digest·revision 불일치·READY_FOR_REVIEW 아님·시각 없음 거부 시험, 성공 후 `validate_state`·`validate_closure` 통과, 오목 rev 30 사본에 재현해 손 기록과 같은 결과 — 2026-10-26 결과: 오목 rev 30을 승인 전으로 되돌린 사본에 사용자 digest·시각으로 기록하니 손으로 쓴 rev 30 state와 바이트 동일, 검증·closure 통과. 시험 `tests/test_record_approval_v020.py` — 전체 회귀 1,144개 중 새 실패 0(기준과 같은 환경 원인 8건), 커밋 `9b7bf3c`, 설치본 반영·실행 확인 |
| U1-3 | 승인 현황 명령: 현재 rev·승인 rev·승인 없이 지난 rev·마지막 승인 이후 바뀐 레코드 수를 한 화면에. SKILL에 "승인 전 구현은 사용자 지시가 있을 때만, 보고에 승인 대기 표시" 규칙 | F8 | 높음(보이지 않던 위험) | 작음~중간 | complete | 오목 rev 30 사본에서 rev 13·14·26·28이 "따로 승인 안 됨"으로 나옴, UNAPPROVED 상태에서 "승인 대기 rev N" 표시 — 2026-10-26 결과: `approval_status.py`가 오목 rev 30에서 13·14·26·28을 보고, 승인 전 사본에서 "rev 30 대기, rev 29 대비 추가 13·변경 8". SKILL APPROVE 단계·빠른 참조와 workflow APPROVE 절에 `record_approval.py`·`approval_status.py` 규칙 추가 — 전체 회귀 1,144개 중 새 실패 0(기준과 같은 환경 원인 8건), 커밋 `9b7bf3c`, 설치본 반영·실행 확인 |
| U1-4 | 자주 걸리는 검증 오류에 허용 값·기대 값 넣기(authority class, reasoning_refs 종류, alternatives_presented, 축 허용 타입, ACTIVE rationale null) | F3 | 중간 | 중간 | complete | 오목 마찰 기록 3·8·12·16·24번 오류를 재현하면 메시지에 허용 값이 나옴, 오류 코드 불변 — 2026-10-28: `state_validation_v2.py`·`authority_binding_v2.py`는 시험이 blob을 고정하므로 고치지 않음. 고정 아닌 `grill_v2.py` 문구 4종(unknown 필드, reasoning_refs, 추천 수락, grill profile)에 허용 값을 넣고, 고정 모듈 오류는 읽기 전용 `explain_state_errors.py`가 힌트(source kind별 class, 축별 허용 타입·포인터, 바인딩별 해시)를 붙임. 오목 rev 30 사본에 다섯 오류를 넣어 확인, 시험 `tests/test_error_hints_v020.py` — 전체 회귀 1,165개 중 새 실패 0(기준과 같은 환경 원인 8건) |
| U1-5 | 개정 도우미: `open_revision`(rev+1·UNAPPROVED·비CLOSED 한 번에), `refresh_bindings`(가리키는 내용이 바뀐 바인딩만 목록으로 보여 주고 확인 플래그로 해시 갱신) | F2 | 높음 | 큼 | complete | 오목 rev 29→30을 사본에서 도우미로 재현해 freeze 스크립트 없이 같은 state digest, 내용이 바뀐 바인딩을 묻지 않고 갱신하지 않음 — 2026-10-28: `open_revision.py`(패치 적용·패치한 레코드 바인딩만 재해시·baseline 재계산·검증 통과 시에만 기록)와 `refresh_bindings.py`. 커밋된 오목 rev 29(`4bb3f53`)에 레코드 21개·셀 추가 3건 패치를 적용하고 `record_approval.py`로 승인하니 커밋된 rev 30과 바이트 동일(freeze30.py는 셀 212개 재작성). 패치 밖 변경·SUPERSEDED 바인딩은 기록 거부. 시험 `tests/test_revision_v020.py`. 참고: 오목 `build_state.py`를 rev 29에서 잘라 재실행하면 승인된 rev 29와 다름(승인 뒤 앞부분이 고쳐짐) — 전체 회귀 1,165개 중 새 실패 0(기준과 같은 환경 원인 8건) |
| U1-6 | 레코드 작성 CLI(`add_unknown`·`add_decision` 등): 기본값을 채우고 바로 검증 | F4 | 중간 | 중간~큼 | complete | 최소 인자로 만든 unknown이 검증 통과, 오목 질문 1건을 CLI로 재현 — 2026-10-28: `new_records.py`(evidence·question·user-decision·authoring, 패치 파일에 추가)와 `record_builders.py`. 오목 rev 30의 근거 2·unknown 4·결정 4를 작성자가 정하는 필드만으로 다시 만들어 10개 모두 동일(결정 2개는 `--decision-affects` 사용). `grill_v2.py`의 'invalid unknown semantic shape'에 틀린 조건 이름, EVIDENCE_RESOLVABLE 판정에 이유·해법(마찰 24번)을 넣음. 시험 `tests/test_new_records_v020.py` — 전체 회귀 1,165개 중 새 실패 0(기준과 같은 환경 원인 8건) |
| U1-7 | 로컬·무계정 앱 프로필: ASYNC 경량 축, UX 계정·세션 축 일괄 N/A 한 근거 | F7 | 중간 | 큼(계약 의미 변경) | not started | 프로필 없는 기존 fixture 결과 불변, 오목 사본에서 N/A 반복 셀 수 감소 측정 |
| U1-8 | `FEATURE_EXTENSION` 부트스트랩 모드 | F6 | 중간 | 매우 큼(스키마·계약 버전) | deferred | 별도 설계 문서와 A/B 뒤 결정 |

범위 밖 후보(마찰 기록에서 함께 나옴, 이번 계획에 넣지 않음): 사용자 직접 지시를 질문 없이 결정으로 기록(22번), 대체·폐기 연쇄 자동 추적(26번), 질문 종료와 FREEZE 사이 중간 상태(15·26번).

A/B(2026-10-28, [보고](evals/joeflow-u1-approval-ab/REPORT.md)): 새 규칙(B) 2회는 승인을 `record_approval.py`로 기록하고 시각을 '기록 시각'으로 밝힘, 이전(A) 2회는 시각을 지어낼 수 없다며 사용자에게 물음. 묶인 rev는 양쪽 모두 맞힘. 기록 시각 허용은 2026-10-28 사용자 결정으로 유지(보고에 기록 시각임을 밝힘). 22번(사용자 직접 지시 기록)은 U1-6 `new_records.py user-decision`이 다룸.
