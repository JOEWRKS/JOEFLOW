rev 2는 승인 준비가 끝났습니다. check_approval.py 결과 **ready: true**, **revision 2**, **manifest digest `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`** 입니다. 승인 기록(record_approval.py --write)은 실행하지 않았고, state.json도 바꾸지 않았습니다.

**점검한 것**
- **상태:** approval_status.py 결과 rev 2는 READY_FOR_REVIEW / UNAPPROVED이고, 마지막 승인은 rev 1입니다. rev 1→2 변경은 추가 7건이고 변경·대체·폐기는 0건입니다.
- **검증:** validate_state.py는 오류가 없습니다. validate_closure.py는 승인이 없다는 3개 항목만 걸려 종료 코드 1이 나왔고, 승인 전이므로 정상입니다. preflight_state_candidate.py는 PASS입니다.
- **신원 정보:** build_approval_manifest.py가 낸 digest가 두 문서의 IDENTITY 블록에 적힌 값과 같습니다. definition digest는 `70067b7e…5182` 입니다.
- **기계 점검:** projection_check.py는 수정 전과 후 모두 ok입니다. update_projection.py는 `--write` 없이 미리보기로만 돌렸고 diff가 0줄이었습니다. 직접 다시 읽으라고 나온 줄은 추가된 7개 레코드를 언급하는 줄들이었고, 모두 state.json과 맞는지 대조했습니다.
- **내용 대조:** 두 문서의 흐름·화면·규칙·완료 기준을 state.json과 하나씩 맞춰 봤습니다. 예외 경로가 기본 결과로 뭉개진 곳은 없었고, 실패 분기는 RULE-001에 근거가 있습니다.
- **렌더 확인:** 검토 화면을 미리보기 창에서 실제로 열어 폭 800px과 375px에서 봤습니다. 글자·IA 도식·섹션이 잘리지 않고 읽히며, 375px에서 페이지 가로 스크롤은 없습니다(IA 도식만 상자 안에서 가로로 스크롤). 내비게이션 링크는 눌러도 이동하지 않았는데, 정적 스냅샷 환경의 한계로 보여 NOT_VERIFIED로 남겼습니다.

**바꾼 것** (투영 문서만 수정, 두 군데)
1. `MASTER_PLANNING_SPEC.md` §6 "요청 내용 입력"에 있던 "데이터 변경 없음(표시만)"은 정본에 근거가 없는 주장이었습니다. "이 표시 자체의 데이터 효과는 정본에 정의되어 있지 않다."로 바꿨습니다.
2. `planning-review-core.html`의 렌더 확인 줄은 "렌더·클릭을 관찰하지 못함"이었는데, 실제로 관찰한 범위(폭 800·375px 렌더 확인, 링크 이동은 NOT_VERIFIED)로 고쳤습니다.

**지적했지만 바꾸지 않은 것**
- **기획서 머리의 `> 승인: revision 1 (dd1e837b…)` 줄:** rev 2 문서 머리에 있지만 rev 1 승인에 대한 사실 문장이고 맞는 내용입니다. 바로 위 줄이 rev 2가 승인 대기임을 밝히고, 그 줄에 rev 1 승인 digest 앞자리가 함께 있어 점검기도 통과시킵니다. 워크플로 문서도 사실인 문장은 그대로 두라고 하므로 두었습니다.
- **200자 한도(`EVD-902`):** 현재 구현을 관찰한 사실일 뿐 제품 결정은 아닙니다. 두 문서 모두 이미 그렇게 표시하고 있어 고칠 게 없습니다.
- **DEC-002 근거(정본 쪽 문제라 투영에서 고칠 수 없음):** "추천 수락"으로 기록돼 있지만, 근거는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(`EVD-901`) 하나입니다. 이 원문은 위치나 '항상 표시 vs 180자부터 표시'를 고르지 않았습니다. 두 문서 모두 이 점을 "승인 전에 확인할 점"으로 사용자에게 보여주고 있습니다. 정본을 고치려면 새 revision이 필요하고 사용자 판단이 걸리므로 손대지 않았습니다.

**남은 것**
- **실제 승인:** 사용자에게 rev 2와 manifest digest `6b50eb33…2906`을 보여주고, 특히 DEC-002의 '항상 표시'를 확인받아야 합니다. 그 뒤 사용자의 말을 직접 받은 세션에서 `record_approval.py STATE --revision 2 --manifest-digest 6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906 --at <UTC> --quote "..." --write`를 실행합니다. 사용자가 '180자부터 표시'를 원하면 새 revision을 열어야 합니다.
- **승인 뒤 문서 갱신:** `update_projection.py --write`와 `projection_check.py`를 다시 돌려 두 문서의 상태 표시를 승인됨으로 갱신해야 합니다.
- **JOEFLOW 버전 고정:** 이 프로젝트에는 사용할 JOEFLOW 버전이 기록돼 있지 않습니다(지금 실행한 것은 1.7.3). `joeflow_version.py --pin`으로 기록할 수 있지만 프로젝트 파일(`joeflow-project.json`)을 새로 쓰는 일이라 하지 않았습니다.
- **링크 이동 확인:** 검토 화면의 링크 클릭 이동은 실제 브라우저에서 아직 확인되지 않았습니다(NOT_VERIFIED).

실행한 셸 명령은 모두 `commands.log`에 한 줄씩 남겼습니다. 브라우저 조작은 셸 명령이 아니라서 기록하지 않았습니다.

Files are in <SCRATCH>\runs\r03:
- project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- project\product-definition\request-form\planning-review-core.html
- commands.log
