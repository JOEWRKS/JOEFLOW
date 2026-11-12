# JOEFLOW 1.7.0

오목(AI-Gomoku) 실사용에서 2026-11-11에 기록된 JOEFLOW 마찰 4건을 고치고, JOENESS 1.4.0·JOEDESIGN 1.3.0과 함께 한 바퀴 돌린 통합 시험에서 찾은 JOEFLOW 결함 3건을 고쳤습니다. State 0.2.0, 고정 검증 모듈(`authority_binding_v2.py`, `approval_v2.py`, `state_validation_v2.py`, state 스키마, semantic-freeze 계약), 바인딩 계약은 바뀌지 않았고 기존 승인은 그대로 유효합니다. 상세: [보고서](https://github.com/JOEWRKS/JOEFLOW/blob/main/evals/2026-11-12-friction-170/report.md).

## 바뀐 것

- **오류 메시지**: 선택지·추천 검증 오류가 칸·값·이유를 말합니다(예: `options[1].id 'NONE' is a reserved non-answer word`). 예약어 `none, false, n/a, na, later, tbd`(대소문자 무시)는 `new_records.py`가 패치를 만들 때 거절합니다.
- **`new_records.py`**: `--recommend`에는 `--reason`·`--tradeoff`가 하나 이상 필요하고, `--accepted`에는 `--recommend`가 필요합니다. `relayed --asked|--asked-summary`로 답한 질문을 근거에 남깁니다.
- **승인**: 쓰기 옵션이 없는 `check_approval.py`. `record_approval.py --quote`·`--relayed-from`이 승인 원문과 전달 경로를 state.json 옆 `joeflow-project.json`에 남기고 `approval_status.py`가 보여 줍니다. 전달받은 승인은 원문을 받은 세션이 기록하는 절차를 SKILL·workflow에 적었습니다.
- **판 고정**: `joeflow_version.py [--pin]`과 `skills/joewrks-product-definition/VERSION`. 고정이 없거나 다르면 주요 명령이 `version_notice`로 알립니다(막지 않음). 스키마가 맞지 않으면 찾은 판과 할 일을 말합니다.
- **통합 시험에서 찾은 것**: `open_revision.py`가 READY_FOR_REVIEW에서 semantic readiness 실패 시 쓰지 않고 막는 레코드를 이름으로 알립니다. `build_approval_manifest.py` 실패 출력에 `findings`. `update_projection.py`가 빈 블록·CRLF 블록을 알아봅니다. JOENESS ROADMAP·JOEDESIGN DESIGN.md와 revision·AC·TASK ID로 인계하는 문장을 더했습니다.

## 확인된 것

- 오목 rev 43 사본에서 마찰 A·B 재현, 고친 뒤 메시지가 칸·값·인자를 말하고 생성 단계에서 막힘.
- 승인 원문·전달 경로 기록, `--relayed-from` 단독 거절, 읽기 전용 검사, 판 고정·불일치 알림: 새 테스트 20개와 샘플 프로젝트 시험에서 동작.
- 세 도구 한 바퀴(샘플 프로젝트, 모의 승인): JOEFLOW ID가 ROADMAP·DESIGN·보고·TASK로 이어지고, JOEDESIGN 도장 `--verify` 일치, spot check 불일치가 완료를 막음.
- 회귀: 테스트 1,244개, 실패 8건이 1.6.0 기준과 같은 환경 원인 목록. 오목 rev 43 사본의 `validate_state`·`validate_closure`·`projection_check` 출력이 1.6.0과 같고 `approval_status`는 새 키 `joeflow_version`만 늘었음.

## 확인되지 않은 것

- 자동 권한 분류기가 `check_approval.py`를 통과시키는지. 오목에서 막힌 전달 승인 상황을 재현하지 않았고, 이 세션에서는 검사·기록 명령 모두 막히지 않았다.
- 에이전트가 새 지침만 보고 전달 승인을 원문 세션에 넘기는지(행동 A/B 없음, 유료 실행 0회).
- 실제 사용자 승인 흐름에서의 `--at` 시각(시험 승인은 모의).
- JOEFLOW-ux 1.2.0 → 1.6.0 사이 레코드 호환성의 상세.
- 시험 렌더 측정은 앱 미리보기 창에 같은 CSS를 주입해 한 값.

## 세션이 대신 내린 결정

1. 승인 원문·판 고정은 state가 아니라 `joeflow-project.json`에 둔다(스키마를 바꾸면 기존 승인이 모두 낡음). `--quote` 없이 승인하면 이 파일을 만들지 않는다.
2. 판 불일치는 알리기만 하고 막지 않는다.
3. READY_FOR_REVIEW 쓰기는 semantic readiness 실패 때 막는다(1.6.0은 썼다). `--status OPEN`으로는 쓸 수 있다.

## 다음 후보 (이번에 고치지 않음)

- JOENESS: 연결 본문의 `<joedesign>` 경로가 기계별 절대 경로로 커밋됨, DESIGN 템플릿 두 개(JOENESS 쪽에 Rule Coverage 표 없음), ROADMAP `Product authority`에 revision 칸 없음.
- JOEDESIGN: 여섯 줄 보고와 결과 목록의 배치 지침 없음, 주입 CSS 측정을 "rendered"와 구별하지 않음.
- JOEFLOW: `projection_check.py`가 손으로 만든 검토 화면 제목의 낡은 revision을 잡지 못함(템플릿 형식만 대조).
