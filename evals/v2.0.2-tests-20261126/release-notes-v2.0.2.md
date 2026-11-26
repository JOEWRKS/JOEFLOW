# JOEFLOW 2.0.2

입력은 ATELIER 실사용 23개 리비전의 마찰 기록(JOEFLOW 1~15)과 검토의 묶음 A·B·C·D·G이며, 사용자가 2026-11-26에 범위를 확정했습니다(E 에이전트 기본값 묶음·F 상태–흐름 린트는 2.0.3). 시험 기록은 [evals/v2.0.2-tests-20261126/report.md](evals/v2.0.2-tests-20261126/report.md)입니다.

**바뀐 것**

- (A) `new_records.py resolve UNK --option OPT --words "..." [--also UNK=OPT ...]`: 기존 OPEN 질문을 state에서 읽어 RESOLVED 질문과 결정을 만들고, 답한 ID를 모든 `blocks_unknown_refs`에서 빼고, 표면 `decision_refs`에 결정을 붙이고, 그 질문이 잡고 있던 OPEN coverage 칸을 결정으로 답합니다. `resolve --accept-recommended --pack PACK [--surface SURF]`는 묶음 수락(질문마다 결정 하나). `next_product_question.py --grouped [--markdown]`은 팩·표면 단위 추천표를 내고, 독립 축만 한 표로 묶습니다. 워크플로 CLOSE 절에 그 경로를 적었습니다. 모든 상태 빌더는 `--state`로 기존 기록을 읽고, 같은 패치를 여러 명령이 이어 씁니다.
- (B) 템플릿은 여섯 도메인을 OPEN과 분류 질문(UNK-901~906)으로 시작하고 근거를 미리 채우지 않습니다(2.0.1의 EVD-900 N/A 제거). `open_revision.py` 패치 키 `grill_profile`. `new_records.py question --pack ID [--axis ID]`(GRILL_TOPOLOGY·GRILL_PACK_AXIS origin). `topology-on DEC`는 강제 kind 표면, 팩 coverage 행(버전·digest), 축별 OPEN 질문 뼈대를 한 패치로, `topology-off DEC --rationale`은 N/A를 씁니다. ACTIVE 팩의 행 누락 허용은 고르지 않았습니다(아래 결정).
- (C) `scripts/decision_policy.py`: 빌더가 검증기의 `derive_decision_authority`·`classify_materiality`를 그대로 부릅니다. 질문의 `decision_authority`는 파생값이고, 파생이 허용하지 않는 해결(파생이 `USER_DECISION_REQUIRED`인데 `--accepted`, `EVIDENCE_RESOLVABLE`·`EXTERNAL_AUTHORITY_REQUIRED` 질문에 사용자 답, 분류와 다른 `MATERIAL`/`NON_MATERIAL` 주장, 모르는 위험 플래그)은 이유를 말하며 거절합니다. 검증기의 파생 오류 문구도 이유를 말합니다.
- (D) `new_records.py requirement --from-decisions DEC-a,DEC-b --surface SURF --requirement REQ`: 결정문을 이어 붙인 요구사항 초안과 표면 IN_SCOPE. `resolve`는 질문이 다 떨어진 표면과 이 명령을 알려 주고, `OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN` 문구와 CLOSE 절이 같은 길을 말합니다.
- (G) 오류 문구가 실제 조건을 말합니다: coverage 칸 `axis back: allowed [FLOW, RULE, SCR], actual STATE (STATE-001 /state_name)`(축별 허용 타입 표는 `coverage-inheritance.md`), 토폴로지 프로필 칸, `blocks_unknown_refs`. `projection_check.py --draft --full`, 첫 승인 표기(`rev None→` 대신 `첫 승인`), 읽는 쪽이 파이프를 닫아도 `OSError [Errno 22]` 없음.
- `new_records.py edit ID --set|--set-json|--replace-text`(레코드 문구 수정; 해결 필드는 바꾸지 않음), `--replace`(같은 패치의 레코드나 state의 OPEN 질문 다시 쓰기). 버전 2.0.2.

**확인된 것**

- 재현(ATELIER 커밋된 rev N−1 → 새 빌더만으로 rev N): rev15는 `definition_digest`가 같습니다. rev18·22·23은 다르며, 차이는 파생 정책이 만든 필드(질문·결정의 `evidence_refs`, 위험 질문의 모드·권한·`accepted_recommendation`)뿐이고 그 필드만 커밋본 값으로 되돌리면 digest가 같아집니다.
- 새 템플릿에서 READY_FOR_REVIEW와 Approval Manifest까지 걷기 시험 38단계, 바뀐 오류 문구 11개의 2.0.1/2.0.2 비교, 새 시험 `tests/test_builders_202.py` 10건. 전체 테스트 결과는 시험 기록에 있습니다.

**확인되지 않은 것**

- 행동 시험(에이전트가 새 CLOSE 절과 빌더를 실제로 쓰는지) 없음. ATELIER rev14(토폴로지 ON + 26개 수락)와 rev2·rev4는 재현하지 않았습니다.

**세션이 대신 내린 결정(사용자 확인 필요)**

- 위험 질문(되돌리기 비쌈·위험 플래그)의 추천 수락은 `USER_DECISION`으로 기록하고 `--accepted`를 거절합니다. 검증기의 OPEN 파생과 맞추는 선택이며, 그 때문에 ATELIER rev18·22·23은 같은 digest로 재현되지 않습니다(ATELIER는 사용자 의도 근거를 `evidence_refs`에 넣어 파생이 `EVIDENCE_RESOLVABLE`이 됐고, RESOLVED 기록은 다시 파생하지 않아 통과했습니다). 검증기는 바꾸지 않아 기존 state는 그대로 유효합니다.
- ACTIVE 팩의 coverage 행 누락은 계속 오류로 두고, `topology-on`이 같은 패치에 행을 씁니다. 도메인이 OPEN이면 행이 필요 없습니다.
- 보호된 `state_validation_v2.py`·`authority_binding_v2.py`의 문구는 그대로 두고 `explain_state_errors.py`(open_revision이 출력) 층에서 조건을 덧붙였습니다. `validate_state.py`의 원 출력은 2.0.1과 같습니다.


기록: [report.md](report.md). 개인 설치: [install_2_0_2.py](install_2_0_2.py).
