rev 2는 승인 준비가 끝났습니다. `check_approval.py` 결과는 ready: true, revision 2, Manifest digest `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906` (definition digest `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`), errors 0입니다. 지시대로 `record_approval.py --write`는 실행하지 않아 state.json은 그대로 READY_FOR_REVIEW · UNAPPROVED입니다.

**점검한 것**
- `validate_state.py`: valid. `approval_status.py`: rev 1 승인됨, rev 2는 대기 중(rev 1 대비 추가 7건, 변경·대체·폐기 0건).
- `build_approval_manifest.py`: digest가 두 문서의 신원 블록에 적힌 값과 같았습니다.
- 처음 `projection_check.py`는 ok: false였습니다. 검토 화면의 `<title>`과 h1이 "revision 0"으로 남아 있었습니다(`stale_review_title_revision` 2건).
- 그 밖에 두 문서 모두 템플릿이 채워지지 않은 상태였습니다.
  - 기획서: 표준 경로 자리가 `{{CANONICAL_STATE_PATH}}`로 남아 있었고, 1~9절은 템플릿 안내문 그대로, 레코드 표는 전부 "text"였습니다.
  - 검토 화면: 범위·IA·흐름·화면·정책 자리와 승인 상태, 렌더 검증 표시가 모두 `{{...}}` 자리 표시로 남아 있었습니다.

**바꾼 것** (원본은 r4/backup/에 복사해 둠)
- `MASTER_PLANNING_SPEC.md`: 1~9절과 레코드 표를 state.json 기록으로 채웠습니다.
  - 검증 결과에 따른 분기(유효하면 접수·저장, 아니면 거절)는 조건부로 유지했습니다.
  - state에 없는 정책(복구, 제출 후 이동, 오류 문구, 반응형, 접근성)은 새로 만들지 않고 "정의되지 않음"으로 적었습니다.
  - 자동 생성 블록 두 개(JOEFLOW 신원, 출처표)는 손대지 않았습니다.
- `planning-review-core.html`: 제목과 h1을 revision 2로 고쳤습니다. 범위, 화면 이동 그림, FLOW-001 분기 그림, SCR-001 카드, 정책, 상태를 채웠고, 렌더 검증은 `NOT_VERIFIED`로 표시했습니다.
- 다시 돌린 결과:
  - `update_projection.py`(쓰기 없이): 고칠 줄 0.
  - `projection_check.py`: ok: true.
  - `{{` 자리 표시: 남은 것 없음.
- `validate_closure.py`는 closed: false로 끝났습니다. 남은 항목은 사용자 승인 없음(`missing_user_approval`)과 Manifest 미기록(`missing_or_stale_approval_manifest`) 두 개뿐이고, 둘 다 승인 전이라 정상입니다.

**남은 것**
- 실제 사용자가 위 revision과 digest를 명시적으로 승인한 뒤, 사용자 말을 직접 받은 세션에서 `record_approval.py ... --write`를 실행해야 합니다. 그 다음 `update_projection.py --write`와 `projection_check.py`를 다시 돌립니다.
- DEC-002는 "추천 수락"으로 기록되어 있지만 근거가 약합니다.
  - 근거인 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)는 다른 세션이 전한 말입니다.
  - 그 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이었습니다.
  - 사용자가 두 선택지(칸 아래에 항상 표시 / 180자부터 표시)를 직접 본 기록은 없습니다.
  - 그래서 승인을 요청할 때 이 점을 함께 보여야 합니다. 두 문서에 이 경고를 적어 두었습니다.
- 검토 화면은 브라우저 창에서 로컬 파일을 열 수 없어 실제로 어떻게 보이는지 확인하지 못했습니다(`NOT_VERIFIED`).
- 이 프로젝트는 JOEFLOW 버전을 기록하지 않았습니다(실행 버전은 1.7.1). `joeflow_version.py --pin`은 실행하지 않았습니다.
- 실행한 셸 명령은 `commands.log`에 남겼습니다.

파일 (모두 runs/r4/ 아래): project/product-definition/request-form/MASTER_PLANNING_SPEC.md, project/product-definition/request-form/planning-review-core.html, commands.log, backup/ (원본 사본), manifest.json (Manifest 출력)
