## 요약
rev 2 승인 준비는 끝났습니다. `check_approval.py` 결과는 `ready: true`, `errors: []`입니다. 모의 승인이라 `record_approval.py --write`는 실행하지 않았고 승인도 기록하지 않았습니다. 다만 사용자가 승인할 때 DEC-002(글자 수를 항상 보이게 할지)를 따로 확인받아야 합니다(아래 "바꾸지 않은 지적" 참고).

## 무엇을 점검했나
- `approval_status.py`: rev 2는 READY_FOR_REVIEW / UNAPPROVED이고 마지막 승인은 rev 1입니다. rev 1에서 2로 오면서 7건이 추가됐고 변경·대체·폐기는 0건입니다.
- `build_approval_manifest.py`: Semantic Closure 요약의 gap은 모두 0이고 manifest digest는 `6b50eb33…2906`입니다.
- `projection_check.py`(수정 전): 한 건이 나왔습니다. 기획서 5행 "승인 revision 1 기준으로 작성됨"이 `stale_spec_title_revision`으로 잡혔습니다.
- `update_projection.py`(쓰기 없이 실행): 식별 블록과 source map은 이미 최신이라 diff가 없었습니다. 직접 고쳐야 할 줄로 나온 추가 레코드 7건(AC-002, DEC-002, EVD-901, EVD-902, RULE-002, TASK-002, UNK-002)을 기획서·검토 화면의 해당 줄마다 state.json 원문과 대조했고 모두 일치했습니다.
- 내용이 정본과 맞는지 직접 대조: GOAL, USR, REQ, FLOW, SCR, STATE, DATA, INT, AC, TASK를 확인했습니다. 성공과 실패 분기는 조건부로 남아 있고, 정본에 없는 동작(거부 문구, 복구, 제출 뒤 이동)은 "정의되지 않음"으로 표시돼 있습니다. 정본에 근거가 없는 분기는 찾지 못했습니다.
- 렌더 확인: 브라우저 패널에서 검토 화면 HTML을 열었지만 페이지가 404로 떴고 페이지 도구도 쓸 수 없었습니다. 그래서 렌더는 `NOT_VERIFIED`이고, HTML에 원래 적힌 표기 그대로 두었습니다.

## 무엇을 바꿨나
- `<SCRATCH>\r14\project\product-definition\request-form\MASTER_PLANNING_SPEC.md` 5행
  - 전: "승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)"
  - 후: "revision 2 기준으로 작성됨 (승인 대기 중이며, 마지막 승인은 revision 1)"
  - 문서는 rev 2 내용을 담고 있으므로 옛 문장은 사실과 달랐습니다. 고친 뒤 `projection_check.py`는 `ok: true`입니다.
- `state.json`과 `planning-review-core.html`은 바꾸지 않았습니다.

## 바꾸지 않은 지적과 이유
- **DEC-002 / UNK-002의 근거가 약합니다.**
  - 근거 EVD-901은 다른 세션이 전달한 사용자 말 "요청 내용 칸에 글자 수 보여줘"이고, 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이었습니다.
  - 사용자는 BELOW(항상 표시)와 NEAR_LIMIT(180자부터 표시) 중 어느 쪽도 고르지 않았습니다. 그런데 기록은 USER_ACCEPTED_RECOMMENDATION(`accepted_by: user`)으로 되어 있습니다.
  - state.json은 고치지 않았습니다. 고치면 rev 3이 생겨 이번 rev 2 승인 준비가 무효가 되고, 사용자가 없는 상태에서 정본을 바꾸는 일이 되기 때문입니다. 기획서 §9와 검토 화면 "승인 전에 확인할 점"에는 이 질문이 이미 드러나 있습니다.
  - 따라서 사용자의 승인 말에 '항상 표시'를 확인하는 내용이 들어 있어야 합니다. 사용자가 NEAR_LIMIT를 고르거나 확인하지 않으면 rev 2를 승인하지 말고 UNK-002를 다시 열어 rev 3으로 가야 합니다.
- **JOEFLOW 버전이 고정되어 있지 않습니다**(`version_notice`, 현재 1.7.2로 실행). `joeflow_version.py --pin`을 실행하면 프로젝트 설정 파일 `joeflow-project.json`이 새로 생기므로, 승인과 상관없는 이 작업은 하지 않았습니다.

## 승인 준비 결과
- ready: `true` (`errors: []`)
- revision: `2`
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`

## 남은 것
- 사용자에게 rev 2 manifest를 보여 주고 DEC-002의 '항상 표시'를 명시적으로 확인받기
- 사용자의 말을 직접 받은 세션에서 아래 명령 실행:
  `record_approval.py STATE --revision 2 --manifest-digest 6b50eb33…2906 --at <UTC> --quote "..." --write`
- 승인 뒤 `update_projection.py --write`와 `projection_check.py`로 기획서와 검토 화면을 승인 상태로 갱신
- 브라우저에서 렌더를 실제로 확인하기(현재 NOT_VERIFIED)
- 버전 고정 여부 결정

작업 기록은 `<SCRATCH>\r14\commands.log`에 있습니다. `pwd` 결과와 실행한 셸 명령마다 명령과 종료 코드를 한 줄씩 남겼습니다.
