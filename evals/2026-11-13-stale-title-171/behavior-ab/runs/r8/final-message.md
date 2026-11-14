rev 2 승인 준비는 끝났습니다. check_approval.py 결과는 **ready: true**, revision **2**, manifest digest **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`** 입니다. 기록된 것은 없습니다(`written: false`). 지시대로 record_approval.py --write는 실행하지 않았습니다. 검토 화면을 브라우저에서 띄워 확인하는 것은 막혀서 렌더링은 `NOT_VERIFIED` 상태입니다.

**점검한 것**
- 처음 상태:
  - `validate_state.py`는 valid였습니다.
  - `approval_status.py`: rev 2가 READY_FOR_REVIEW / UNAPPROVED이고, rev 1 대비 추가 7건, 변경·대체·폐기 0건이었습니다.
  - `build_approval_manifest.py`: closure gap이 모두 0이었습니다.
- 처음 `projection_check.py`는 `ok: false`였습니다. 검토 화면의 `<title>`(6행)과 `<h1>`(22행)이 "revision 0"으로 남아 있었습니다(`stale_review_title_revision` 2건).
- 내용을 직접 읽어 보니 두 문서 모두 템플릿 상태였습니다. 자동 생성 블록(IDENTITY, SOURCE-MAP)만 맞았습니다.
  - 기획서: 섹션 1~10이 템플릿 설명문 그대로였고, `{{CANONICAL_STATE_PATH}}`가 남아 있었고, 레코드 표의 모든 행이 "text"였습니다.
  - 검토 화면: `{{PRODUCT_SCOPE_SUMMARY}}`, `{{SCREEN_PURPOSE_CARDS}}`, `{{VERIFIED_OR_NOT_VERIFIED}}` 같은 자리표시자가 그대로였습니다.
  - 검사 스크립트는 이 상태를 잡아내지 못합니다.

**바꾼 것** (`project/product-definition/request-form/` 안 두 파일만. state.json은 손대지 않음)
- `MASTER_PLANNING_SPEC.md`: 제목에 revision 2를 넣고 섹션 1~10을 state.json 레코드로 채웠습니다.
  - 기존 레코드: GOAL-001, USR-001, REQ-001, RULE-001, DEC-001, FLOW-001, SCR-001, STATE-001, DATA-001, INT-001, AC-001, TASK-001, UNK-001
  - rev 2에서 추가된 레코드: UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902
  - 레코드 표의 "text" 행을 실제 내용으로 바꾸고 변경 이력을 보강했습니다.
  - 새 정책은 만들지 않았습니다. 검증 실패 때 화면이 어떻게 반응하는지는 state.json에 없어서 "정의 없음"으로 적었습니다.
- `planning-review-core.html`: title과 h1을 revision 2로 고쳤습니다.
  - 자리표시자를 범위, IA 그림(SVG), FLOW-001 분기 그림(유효하면 제출·수락, 아니면 제출 안 됨), SCR-001 카드, 정책 목록, 렌더 확인 `NOT_VERIFIED`로 채웠습니다.
  - rev 2에서 추가된 항목에 "추가" 표시를 붙였습니다.
- IDENTITY와 SOURCE-MAP 블록은 원래대로 두었습니다. 쓰기 없이 돌린 `update_projection.py`에서 바뀌는 줄이 0줄이라 `--write`는 필요 없었습니다.
- 원본 백업: `runs/r8/MASTER_PLANNING_SPEC.orig.md`, `runs/r8/planning-review-core.orig.html`

**재점검 결과**
- `projection_check.py`: `ok: true`, stale 항목 0건
- `validate_state.py`: 다시 valid

**렌더링**
- file:// 로 연 페이지는 로드되어 탭 제목 "revision 2"까지는 확인했습니다. 하지만 로컬 파일이라 스크린샷을 찍을 수 없었습니다.
- 로컬 http.server(127.0.0.1:8765)로 다시 띄워 봤지만 이동이 거부되었습니다. 서버는 바로 종료했습니다.
- 그래서 그림, 링크, 잘림 여부는 확인하지 못했습니다.

**남은 것**
1. 사용자가 manifest(rev 2, `6b50eb33…2906`)를 보고 직접 승인해야 합니다. 승인 기록은 그 말을 받은 세션에서 다음 명령으로 합니다: `record_approval.py state.json --revision 2 --manifest-digest 6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906 --at <UTC> --quote "..." --write`
2. 승인 뒤에는 `update_projection.py --write`와 `projection_check.py`를 다시 돌려 "승인 대기" 표시를 바꿔야 합니다.
3. 검토 화면을 실제로 띄워 보는 확인이 아직 남아 있습니다.
4. 프로젝트에 JOEFLOW 버전이 기록돼 있지 않습니다(현재 실행 1.7.1). 쓰기 작업이라 `joeflow_version.py --pin`은 실행하지 않았습니다.
5. 검증 실패 때 화면 반응이 state.json에 없습니다. RULE-001은 "유효한 요청만 제출"까지만 정합니다. 필요하면 다음 revision에서 질문(UNK)으로 다뤄야 합니다.

**commands.log**: `runs/r8/commands.log`에 명령마다 한 줄씩 남겼습니다.
- `exit=1`이 두 줄 있습니다. 처음 `projection_check.py`가 stale title을 보고한 것과, 인라인 python 경로 오류입니다.
- 백업 `cp`는 한 줄로 묶어 기록했습니다.
- http.server는 시작과 종료 줄에 실제 종료 코드 대신 `exit=started`, `exit=n/a`로 적혀 있습니다.
