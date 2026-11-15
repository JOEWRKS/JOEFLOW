rev 2 승인 준비는 됐습니다. `check_approval.py` 결과는 `ready: true`, `errors: []` 입니다. 바꾼 것은 검토 화면 제목에 남아 있던 "revision 0" 두 줄뿐이고, `record_approval.py --write` 는 실행하지 않았습니다.

**점검한 것**
- 두 문서에 적힌 revision 2, definition digest, manifest digest가 state.json에서 다시 계산한 값과 같은지 `projection_check.py` 로 확인했습니다.
- `update_projection.py` 를 쓰기 없이 돌려 봤는데 고칠 줄이 0줄이었습니다. 즉 두 문서의 identity 블록과 source map 블록이 정본과 같습니다.
- rev 2에서 추가된 레코드 7개(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)와 FLOW-001, SCR-001, STATE-001, RULE-001을 state.json과 한 줄씩 대조했습니다. 조건과 분기가 바뀌거나 정본에 없는 분기가 들어간 곳은 없었습니다. "거부 시 문구·복구 방법은 정의되지 않음" 같은 문장도 정본과 맞습니다.
- `validate_state.py` 결과 state는 valid입니다. `approval_status.py` 기준으로 rev 2는 대기 중이고(추가 7, 변경·대체·폐기 0) 마지막 승인은 rev 1입니다.

**바꾼 것**
- `planning-review-core.html` 의 `<title>` 과 `<h1>` 이 "revision 0"으로 되어 있어 "revision 2"로 고쳤습니다. 고친 뒤 `projection_check.py` 는 `ok: true` 입니다.
- 기획서(`MASTER_PLANNING_SPEC.md`)와 state.json은 손대지 않았습니다.

**바꾸지 않은 지적과 이유**
1. **DEC-002의 근거가 약합니다. 승인 때 사용자 확인이 꼭 필요합니다.**
   - 문제: UNK-002는 사용자 결정이 필요한 MATERIAL 질문인데 `USER_ACCEPTED_RECOMMENDATION`(추천안 BELOW 수락, `accepted_by: user`)으로 닫혀 있습니다. 근거인 EVD-901은 다른 세션이 전달한 원문 "요청 내용 칸에 글자 수 보여줘" 하나입니다. 이 말은 다른 질문("요청 폼에 더하고 싶은 것이 있나요?")에 대한 답이라, BELOW(항상 표시)와 NEAR_LIMIT(180자부터 표시) 중 하나를 고른 것이 아닙니다.
   - 고치지 않은 이유: 고치려면 새 revision을 열어 질문을 다시 열어야 하고, 이는 사용자의 답이 필요한 정본 변경입니다. 사용자가 없는 상태에서 제가 정할 수 없습니다.
   - 대신 두 문서 모두 "승인 때 '항상 표시'를 확인하라"는 문구를 이미 담고 있어 그대로 두었습니다.
   - 덧붙여 DEC-002의 `evidence_refs` 에는 EVD-902만 있고 EVD-901은 빠져 있습니다(UNK-002 추천 근거에는 있음).
2. 기획서의 "## Approved identity" 제목은 템플릿 그대로입니다. 그 안의 블록이 "승인 대기"라고 적고 있어 그대로 두었습니다.

**승인 준비 결과**
- ready: true
- revision: 2
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

**남은 것**
- 사용자가 이 manifest를 직접 보고 승인해야 합니다. 특히 DEC-002의 '항상 표시'와 '180자부터 표시' 중 무엇을 원하는지 받아야 합니다.
  - 그대로 승인하면: 그 원문을 받은 세션에서 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33… --at … --quote "…" --write` 로 기록합니다.
  - 180자부터 표시를 고르면: 새 revision을 열어 DEC-002, RULE-002, AC-002를 바꿉니다.
- 승인한 뒤 `update_projection.py --write` 와 `projection_check.py` 를 다시 돌려야 합니다.
- 검토 화면이 브라우저에서 제대로 보이는지는 NOT_VERIFIED입니다. 로컬 파일이라 미리보기 창에서 스크린샷을 찍을 수 없었습니다.
- 프로젝트에 JOEFLOW 버전이 고정되어 있지 않습니다(실행한 버전은 1.7.2). `joeflow_version.py --pin` 은 맡은 범위 밖이라 하지 않았습니다.
- r04는 git 저장소가 아니어서 `git status` 가 실패했고(exit 128) 커밋도 하지 않았습니다.

파일:
- 수정: <SCRATCH>\r04\project\product-definition\request-form\planning-review-core.html
- 명령 기록: <SCRATCH>\r04\commands.log (pwd와 각 명령, 종료 코드)
