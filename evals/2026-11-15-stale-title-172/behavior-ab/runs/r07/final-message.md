## 결과
rev 2는 승인 준비가 끝났습니다. `check_approval.py` 결과 **ready: true**, errors 없음이며, 승인은 기록하지 않았습니다(`--write` 미실행). 기획서와 검토 화면을 점검해 검토 화면의 revision 표기 오류 하나를 고쳤습니다. 승인을 요청할 때는 아래 DEC-002 확인 사항을 반드시 함께 물어야 합니다.

- revision: **2** (READY_FOR_REVIEW / UNAPPROVED, rev 1 대비 추가 7건 · 변경·대체·폐기 0건)
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

## 점검한 것
- **스크립트 점검:** `validate_state.py`(valid), `build_approval_manifest.py`(위 digest와 일치), `projection_check.py`(수정 전·후 모두 ok, 빠진 레코드나 오래된 식별자 없음), `update_projection.py`(쓰기 없이 실행, 바뀌는 줄 0), `approval_status.py`, `check_approval.py`를 실행했습니다.
- **충실도 수동 대조:** 두 투영 문서의 문장을 state.json의 GOAL·USR·REQ·FLOW·SCR·STATE·DATA·INT·RULE·DEC·UNK·AC·TASK·EVD와 하나씩 대조했습니다. 조건부 결과를 일반 결과로 뭉갠 곳이나, 정본에 없는 화면·분기·정책을 더한 곳은 없었습니다. "정의되지 않음"이라고 적은 부분(거부 시 문구, 복구, 제출 뒤 이동)도 정본과 맞습니다.

## 바꾼 것
- `<SCRATCH>\r07\project\product-definition\request-form\planning-review-core.html`: `<title>`과 `<h1>`이 "revision 0"으로 되어 있어 "revision 2"로 고쳤습니다. 식별 블록 밖이라 `projection_check.py`가 잡지 못하는 오류입니다.
- state.json과 MASTER_PLANNING_SPEC.md는 바꾸지 않았습니다.

## 바꾸지 않은 지적
- **DEC-002의 근거가 약함:** DEC-002와 UNK-002는 "추천안 BELOW(항상 표시) 수락"(USER_ACCEPTED_RECOMMENDATION)으로 기록돼 있습니다. 그런데 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"뿐입니다. 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이고, BELOW와 NEAR_LIMIT(180자부터만 표시) 중 하나를 고른 것이 아닙니다. 그래서 `accepted_recommendation`(대안을 사용자에게 보여 주고 수락받았다는 기록)을 뒷받침하는 증거가 없습니다.
  - **고치지 않은 이유:** 정본을 고치려면 새 revision(rev 3)을 열어 UNK-002를 다시 OPEN으로 돌려야 합니다. 그건 이번 일의 범위(rev 2 승인 준비)를 벗어나고, 사용자 답 없이 제품 결정을 바꾸는 일입니다. 또 decision_authority가 USER_CONFIRMATION이고 두 투영 문서 모두 "승인 전 확인할 점"으로 이 문제를 이미 드러내고 있어, 사용자가 승인할 때 직접 확인하면 해소됩니다.
  - **승인 요청 시:** '항상 표시'가 맞는지 분명히 물어야 합니다. 사용자가 NEAR_LIMIT를 고르면 rev 3로 다시 열어야 합니다.
- **MASTER 제목:** "Approved identity"라는 제목은 템플릿 제목 그대로입니다. 본문에 "승인 대기"가 적혀 있어 오해의 소지가 없다고 보고 두었습니다.

## 남은 것
- **사용자 승인:** 사용자가 위 Manifest를 보고 승인해야 합니다. 그 말을 직접 받은 세션에서 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33… --at … --quote "…" --write`를 실행해야 합니다. 이번에는 모의라 실행하지 않았습니다.
- **승인 뒤 정리:** 승인 뒤 `update_projection.py --write`와 `projection_check.py`로 승인 상태를 문서에 반영해야 합니다.
- **렌더 확인:** 브라우저 창에서 로컬 파일을 띄우지 못해 렌더·클릭은 **NOT_VERIFIED**입니다. 정적 구조 점검만 했습니다.
- **버전 고정:** 프로젝트에 JOEFLOW 버전이 고정돼 있지 않습니다(실행 버전 1.7.0, `joeflow-project.json` 없음). 지시 범위 밖이라 `joeflow_version.py --pin`은 실행하지 않았습니다.

## 작업 기록
실행한 명령과 종료 코드는 `<SCRATCH>\r07\commands.log`에 남겼습니다.
- 처음 state를 덤프한 명령은 cp949 인코딩 오류로 종료 코드 1이었고, `PYTHONIOENCODING=utf-8`로 다시 실행해 성공했습니다.
- 같은 실패가 두 줄로 중복 기록돼, 중복 한 줄을 지우고 그 정리 명령도 기록에 남겼습니다.
- r07 폴더는 git 저장소가 아니라서 `git status`는 종료 코드 128이었습니다.
