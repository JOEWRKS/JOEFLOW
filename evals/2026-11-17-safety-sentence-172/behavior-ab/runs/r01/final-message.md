## 결과
rev 2는 승인 준비가 됐습니다(check_approval.py: `ready: true`). 승인 기록(record_approval.py --write)은 실행하지 않았습니다.

- revision: 2 (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- rev 1→2 변경: 추가 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002), 변경·대체·폐기 0건
- check_approval 오류 없음.

## 점검한 것
- **state.json:** validate_state.py는 valid로 통과했습니다. validate_closure.py는 `closed:false`(exit 1)로 끝났는데, 이유는 missing_user_approval, stale_approval, missing_or_stale_approval_manifest 각 1건뿐입니다. 아직 승인 전인 revision이라 나오는 정상 결과이고, 다른 지표는 모두 0입니다.
- **build_approval_manifest.py:** 투영 문서 두 곳에 적힌 manifest digest가 다시 계산한 값과 같습니다.
- **projection_check.py:** 처음 실행에서 `stale_spec_title_revision` 1건이 나왔습니다(아래에서 고침). 고친 뒤 `ok: true`입니다.
- **update_projection.py (dry-run):** 자동 생성 블록(정체 정보·레코드 표)이 이미 최신이라 바뀌는 줄이 0줄입니다. 그래서 --write는 실행하지 않았습니다. 추가된 레코드 7건을 문서 본문의 손으로 쓴 줄과 정본(state.json)에 대조했고, 내용이 맞습니다.
- **projection-fidelity:** 조건부 분기는 조건부로 남아 있고, 정본에 없는 분기나 정책은 없습니다. 정의되지 않은 항목(거부 문구, 복구, 제출 후 이동)은 문서에 "정의되지 않음"으로 표시돼 있습니다.
- **검토 화면 렌더:** 미리보기 창에서 file://로 열어 데스크톱 폭(약 800px)에서 봤습니다. 본문 텍스트와 IA 도식이 잘 읽히고, 잘림이나 가로 넘침이 없습니다. 미리보기가 정적 스냅숏이라 내부 이동 링크를 눌러도 이동하지 않아, 링크 이동은 확인하지 못했습니다(NOT_VERIFIED). 모바일 폭은 보지 않았습니다(NOT_VERIFIED).

## 바꾼 것 (투영 문서만, state.json은 그대로)
1. **`MASTER_PLANNING_SPEC.md` 5행:** `> 승인: revision 1 (...)`이 머리말에 있어서 문서가 rev 1로 승인된 것처럼 읽혔습니다(검사기의 stale_spec_title_revision 지적). "이 revision은 아직 승인되지 않았다. 이전 승인 이력은 아래 Approved identity 블록의 '이전 승인' 줄을 따른다."로 바꿨습니다.
2. **`planning-review-core.html` 상태 섹션의 Render verification 줄:** 실제로 본 범위(데스크톱 정적 렌더)와 확인하지 못한 범위(링크 이동, 모바일, NOT_VERIFIED)를 나눠 적었습니다.

## 바꾸지 않은 지적과 이유
- **DEC-002 / UNK-002의 해결 근거가 약합니다.** 두 레코드는 `USER_ACCEPTED_RECOMMENDATION`, `accepted_by: user`로 닫혀 있습니다.
  - 근거 EVD-901은 다른 세션이 전한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"입니다.
  - 이 원문은 BELOW(항상 표시)와 NEAR_LIMIT(180자부터 표시) 중 하나를 고르지 않았습니다. 사용자가 추천안을 수락했다는 기록은 근거보다 강하게 적혀 있습니다.
  - 고치려면 rev 3을 열어 정본을 바꿔야 하는데, 이는 사용자 권한에 속하는 제품 결정이고 사용자가 지금 없습니다. 그래서 state.json은 건드리지 않았습니다.
  - 두 투영 문서는 이미 "승인 전에 확인할 점"으로 이 점을 사용자에게 묻고 있습니다. 승인을 받을 때 '항상 표시'가 맞는지 사용자에게 명시적으로 확인해야 합니다. 사용자가 NEAR_LIMIT를 원하면 rev 3을 다시 열어야 합니다.
- **JOEFLOW 버전 고정(`joeflow_version.py --pin`) 안내는 따르지 않았습니다.** 새 파일(joeflow-project.json)을 만드는 일이라 이번 범위 밖으로 보았습니다. 현재 실행 버전은 1.7.1이고 고정된 버전은 없습니다.

## 남은 것
- 사용자에게 rev 2 manifest(digest `6b50eb33…2906`)를 보여주고, DEC-002의 '항상 표시'를 확인받은 뒤 명시적 승인을 받아야 합니다. 그다음 사용자의 말을 받은 세션에서 `record_approval.py ... --quote "..." --write`를 실행합니다.
- 승인 뒤에 할 일:
  - update_projection.py --write와 projection_check.py를 다시 실행합니다.
  - HANDOFF 단계를 진행합니다(compile_downstream_v2).
- 검토 화면의 링크 이동과 모바일 렌더는 아직 확인하지 않았습니다.
- 버전 고정은 아직 하지 않았습니다.

## 파일
- 명령 기록: <SCRATCH>\runs\r01\commands.log
  - 처음 몇 개의 읽기 전용 명령(ls, grep, cat, state.json 출력)은 실행할 때 기록하지 못했습니다. 그 부분은 표시를 붙여 나중에 덧붙였습니다.
- 수정한 파일 (모두 <SCRATCH>\runs\r01\project\product-definition\request-form\ 안):
  - MASTER_PLANNING_SPEC.md
  - planning-review-core.html
