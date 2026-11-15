rev 2는 승인 준비가 끝났습니다. check_approval.py 결과 ready=true, revision 2, Approval Manifest digest `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`(Definition digest `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`), errors 0입니다. 다만 승인 전에 사용자가 직접 확인해야 할 제품 결정이 하나 남아 있습니다(아래 "바꾸지 않은 지적"). 승인은 기록하지 않았습니다(record_approval.py --write 미실행).

**점검한 것**
- 정본 state.json: validate_state는 오류 없음. approval_status는 rev 2가 UNAPPROVED이고 rev 1 대비 추가 7·변경 0입니다. preflight_state_candidate는 PASS이며 다음 할 일은 PRESENT_EXACT_MANIFEST_FOR_USER_REVIEW입니다.
- validate_closure는 closed=false이지만 원인은 승인 관련 항목뿐입니다(missing_user_approval, stale_approval, missing_or_stale_approval_manifest 각 1). 승인 전 상태에서 예상되는 결과입니다.
- 기획서와 검토 화면을 rev 2 레코드(EVD-901/902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)와 흐름·화면·상태 레코드에 하나씩 대조했습니다.
  - 두 문서 모두 revision과 digest가 맞고, 새로 추가된 레코드가 빠짐없이 들어 있습니다.
  - 조건부 분기(유효/무효)는 조건부 그대로 남아 있고, 정본에 없는 동작은 "정의되지 않음"으로 표시되어 있습니다.
- update_projection.py는 미리보기로만 돌렸고 바뀔 내용이 없었습니다(diff 없음).

**바꾼 것(MASTER_PLANNING_SPEC.md만)**
1. 5번째 줄 머리말이 "승인 revision 1 기준으로 작성됨"으로 옛 revision을 가리키고 있었습니다(projection_check의 stale_spec_title_revision 지적). "revision 2 기준으로 작성됨 (승인 대기; 이전 승인 이력은 아래 Approved identity 참조)"로 고쳤습니다.
2. §4의 "(제시된 tradeoff)"를 "(추천안 BELOW의 tradeoff, `UNK-002`)"로 바꿨습니다. 전달받은 증거만으로는 사용자에게 tradeoff가 제시됐다는 사실이 뒷받침되지 않기 때문입니다.
- 수정 후 projection_check.py는 ok=true입니다. 검토 화면은 고칠 곳이 없어 손대지 않았습니다. state.json은 바꾸지 않았습니다.

**바꾸지 않은 지적과 이유**
- **DEC-002 / UNK-002 출처 문제:** 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)는 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답입니다. 표시 위치나 시점(BELOW 항상 표시 / NEAR_LIMIT 180자부터)을 고른 말이 아닙니다. 그런데 정본은 이를 "추천 수락"으로, 그것도 대안을 보여준 뒤 받은 것처럼(alternatives_presented) 기록하고 있습니다.
  - 정본을 고치려면 새 revision(rev 3)을 열어 실질 의미를 바꿔야 하고, 사용자 확인 없이는 그럴 근거가 없습니다. 그래서 정본은 그대로 두었습니다.
  - 기획서 §9와 검토 화면 "승인 전에 확인할 점"에 이미 "'항상 표시'가 맞는지 확인, 대안은 NEAR_LIMIT"가 드러나 있어 그대로 유지했습니다.
- **렌더 확인:** 검토 화면을 브라우저 창에 열었지만 로컬 파일이라 정지 화면으로만 떠서 화면 캡처나 텍스트 읽기를 할 수 없었습니다. 렌더와 클릭 동작은 NOT_VERIFIED이고, HTML에도 이미 그렇게 적혀 있습니다.

**남은 것**
- 사용자에게 Manifest(rev 2, digest 위 값)를 보여 주고 "글자 수 항상 표시(BELOW)"를 명시적으로 확인받은 뒤 승인받아야 합니다.
  - BELOW로 확인되면: 사용자의 말을 직접 받은 세션에서 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33... --at <UTC> --quote "..." --write`를 실행합니다.
  - NEAR_LIMIT를 고르거나 출처를 바로잡아야 하면: rev 3을 열고 다시 승인받아야 합니다.
- 승인 후에는 update_projection.py --write와 projection_check.py를 다시 돌리고 HANDOFF(compile_downstream_v2.py)로 넘어갑니다.
- 이 프로젝트에는 사용 중인 JOEFLOW 버전이 기록되어 있지 않습니다(현재 실행 버전 1.7.1). 요청 범위가 아니어서 `joeflow_version.py --pin`은 실행하지 않았습니다.
- r10은 git 저장소가 아니어서 커밋은 하지 않았습니다.

파일:
- <SCRATCH>\r10\project\product-definition\request-form\MASTER_PLANNING_SPEC.md (수정)
- <SCRATCH>\r10\project\product-definition\request-form\planning-review-core.html (변경 없음)
- <SCRATCH>\r10\project\product-definition\request-form\state.json (변경 없음)
- <SCRATCH>\r10\commands.log (pwd 결과와 실행한 명령·종료 코드)
  - 한 줄은 "projection_check.py (rerun after first edit)"처럼 인자를 줄여 적었습니다.
  - 마지막 git status는 저장소가 아니어서 실패했는데(종료 코드 128) 0으로 잘못 기록되었습니다.
