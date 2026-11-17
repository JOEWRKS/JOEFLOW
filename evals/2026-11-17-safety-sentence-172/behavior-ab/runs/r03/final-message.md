## 결과
rev 2 승인 준비 점검은 통과했습니다. `check_approval.py` 결과는 **ready: true**, revision **2**, manifest digest **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`** 입니다. 다만 제품 결정 하나(DEC-002)는 사용자가 직접 골랐다는 근거가 없습니다. 승인할 때 사용자 본인이 이 선택을 확인해야 합니다. `record_approval.py --write`는 실행하지 않았고, 승인 기록과 `state.json`도 그대로입니다.

## 점검한 것
- 상태 파일 검사(`validate_state`)는 통과했습니다.
- 닫힘 검사(`validate_closure`)는 승인이 아직 없다는 항목 3개만 남았습니다. 승인 전에는 원래 남는 항목입니다.
- 승인 목록(Approval Manifest)은 rev 1→2에서 7건이 추가됐고 변경·대체·폐기는 0건입니다.
- `approval_status`는 rev 2 미승인, 마지막 승인은 rev 1입니다.
- `projection_check`는 처음에 실패(exit 1)했습니다. 원인은 기획서 5행 머리글의 `> 승인: revision 1 (dd1e837b…)` 이었습니다.
- `update_projection.py`는 쓰기 없이 실행했고 바뀌는 줄이 0줄이었습니다. 자동 블록은 이미 최신이었습니다.
- 기획서와 검토 화면 본문이 정본(`state.json`)과 맞는지 직접 대조했습니다. 조건이 붙은 분기를 무조건 결과로 바꾼 곳은 없었습니다. 정의되지 않은 거부 문구·복구·이동 경로는 두 문서 모두 "정의 안 됨"으로 적혀 있었습니다.
- 검토 화면을 브라우저 미리보기에서 1024px와 375px로 열어 봤습니다. 글이 잘 읽히고, 페이지가 가로로 넘치지 않았습니다. 내부 링크 7개의 대상이 모두 있었습니다. 375px에서는 IA 도식이 칸 안에서 가로로 스크롤됩니다. 링크를 실제로 눌러 이동하는 것은 확인하지 못했습니다(`NOT_VERIFIED`).

## 바꾼 것 (투영 문서만)
1. `MASTER_PLANNING_SPEC.md` 5행 머리글의 rev 1 표기를 "현재 revision은 승인 대기. 이전 승인 기록은 아래 identity 블록에 있다."로 바꿨습니다. 그 뒤 `projection_check`는 ok: true 입니다.
2. 기획서 §9와 검토 화면 "승인 전에 확인할 점"에 사실 두 가지를 더했습니다.
   - 사용자 원문(EVD-901)은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답입니다. 위치·표시 시점 선택지(BELOW / NEAR_LIMIT)를 보고 한 답이 아닙니다.
   - 따라서 rev 2 승인은 "항상 표시(BELOW)"를 사용자가 직접 고르는 것입니다. 사용자가 NEAR_LIMIT를 원하거나 확인하지 않으면 승인하지 않고 UNK-002를 다시 엽니다.
3. 검토 화면의 렌더 확인 줄을 위에서 실제로 관찰한 범위로 고쳤습니다. 클릭 이동은 `NOT_VERIFIED`로 남겼습니다.

## 바꾸지 않은 지적과 이유
- **UNK-002/DEC-002의 근거 부족 (정본 문제):** 정본에는 "사용자가 추천을 수락함(`accepted_by: "user"`)"으로 기록돼 있습니다. 하지만 근거는 다른 세션이 전해 준, 다른 질문에 대한 답뿐입니다. 스킬 규칙상 이 원문으로는 위치·시점을 정하는 중요한 질문을 닫을 수 없습니다.
  - 고치려면 UNK-002를 다시 OPEN으로 두고 rev 3를 열어야 합니다. 그 질문에는 사용자만 답할 수 있습니다. 또 그렇게 하면 지금 제시할 rev 2 승인 목록이 무효가 됩니다.
  - 사용자가 없는 상태에서 정본의 결정을 바꾸지 않았습니다. 대신 투영 문서에 승인 조건으로 분명히 적었습니다.
  - 스크립트 검사는 기록 형식만 보므로 이 문제를 잡지 못합니다. ready: true 는 형식상 준비가 됐다는 뜻입니다.
- **버전 고정 안내 (`version_notice`):** 실행 중인 스크립트는 1.7.1이고, 프로젝트에는 버전 고정이 없습니다. `--pin`을 실행하면 `joeflow-project.json`이라는 새 파일이 생깁니다. 이번 작업 범위 밖이라 실행하지 않았습니다.

## 남은 것
- 사용자 본인에게 rev 2 승인 목록(digest `6b50eb33…2906`)과 DEC-002 확인 사항을 직접 보여 주고 승인을 받아야 합니다. 다른 세션이 전해 준 승인으로는 기록할 수 없습니다.
- 사용자가 승인하면, 그 말을 받은 세션에서 `record_approval.py --revision 2 --manifest-digest 6b50eb33…2906 --quote "..." --write`를 실행합니다. 그다음 `update_projection.py --write`와 `projection_check.py`를 다시 돌립니다.
- 사용자가 NEAR_LIMIT를 고르면 UNK-002를 다시 열어 rev 3를 만듭니다.
- 이후 단계인 구현 인계(HANDOFF/compile)는 하지 않았습니다.

명령마다 한 줄씩 남긴 기록은 `commands.log`에 있습니다. 첫 `ls`와 `grep` 명령은 실행할 때 빠뜨려서 마지막에 "누락분 보충"으로 덧붙였습니다. 저장소 바깥 데이터에 쓴 것은 없습니다.

파일:
- <SCRATCH>\runs\r03\project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- <SCRATCH>\runs\r03\project\product-definition\request-form\planning-review-core.html
- <SCRATCH>\runs\r03\commands.log
