rev 2 승인 준비는 끝났습니다. `check_approval.py` 결과는 **ready: true**이고 오류는 없습니다. 승인 기록(`record_approval.py --write`)은 하지 않았습니다. 그래서 state.json은 READY_FOR_REVIEW / UNAPPROVED 그대로입니다.

**승인 준비 결과**
- revision: 2
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- rev 1→2 변경: 추가 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002), 변경·대체·폐기 0건

**점검한 것**
- 스크립트 점검은 모두 통과했습니다. `validate_state.py`(valid), `approval_status.py`, `build_approval_manifest.py`, `preflight_state_candidate.py`(PASS)를 돌렸습니다. `update_projection.py`는 `--write` 없이 돌렸고 바뀌는 줄은 0이었습니다. `projection_check.py`는 수정 전후 모두 ok이고 지적이 없었습니다.
- 두 문서의 내용을 state.json 레코드와 하나씩 대조했습니다. 흐름의 조건·분기가 보존되어 있고, 정본에 없는 화면·규칙·분기를 문서가 더하지 않았습니다. rev 2에서 추가된 레코드는 두 문서 모두에 있습니다.
- 검토 화면(planning-review-core.html)을 브라우저 미리보기로 열었습니다. 본문 글자, IA 도식, 섹션 카드가 보이고 데스크톱 폭에서 가로 넘침은 없었습니다. 미리보기가 정적 스냅샷이라 내비게이션 링크 클릭은 반영되지 않았습니다.

**바꾼 것** (state.json은 바꾸지 않았습니다)
1. `MASTER_PLANNING_SPEC.md` 머리말: `> 승인: revision 1 (…)` 줄이 이 문서가 승인된 것처럼 읽힐 수 있었습니다. `> 이전 승인 rev 1 (`dd1e837b…`). revision 2는 아직 승인되지 않았다.`로 고쳤습니다.
2. `planning-review-core.html`의 렌더 확인 줄: 원래 "렌더 전부 NOT_VERIFIED"였습니다. 실제로 본 것(본문·도식 렌더, 가로 넘침 없음, 2026-11-18, 데스크톱 폭)과 못 본 것(링크 클릭 이동, 모바일 폭 = `NOT_VERIFIED`)을 나눠 적었습니다.

**바꾸지 않은 지적과 이유**
- **200자 한도 줄(EVD-902):** 두 문서 모두 이 한도를 "현재 구현에서 관찰한 사실"로 표시하고 있고, 제품 규칙으로 올리지 않았습니다. 정본에서도 이 증거는 OBSERVED_IMPLEMENTATION / FACTUAL입니다.
  - 이 줄을 규칙처럼 고쳐 쓰면, 관찰된 구현을 제품 의도로 바꾸는 셈이 됩니다.
  - 지우면, RULE-002의 '/ 200'이 어디서 왔는지 알 수 없게 됩니다.
  - 그래서 그대로 두었습니다.
- **DEC-002가 근거로 삼은 사용자 말:** 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)를, 추천안 BELOW(항상 표시)를 수락한 것으로 기록했습니다. 그런데 이 원문은 BELOW와 NEAR_LIMIT 중 어느 쪽도 고르지 않았습니다.
  - 두 문서 모두 이 점을 "승인 전에 확인할 점"으로 이미 보여 주고 있습니다.
  - 정본을 고치려면 rev 3를 열어야 하고, 그것은 사용자가 판단할 일입니다. 그래서 정본은 그대로 두고 승인 때 확인할 항목으로 남겼습니다.

**남은 것**
- 사용자가 검토 화면과 Manifest(rev 2, `6b50eb33…`)를 실제로 보고 승인해야 합니다. 특히 "항상 표시"와 "180자부터만 표시" 중 어느 쪽인지 확인이 필요합니다. 승인을 받은 세션에서 `record_approval.py ... --quote "..." --write`를 실행하면 됩니다.
  - 사용자가 NEAR_LIMIT를 고르면 rev 3를 열어 다시 진행해야 합니다.
- 승인을 기록한 뒤에는 `update_projection.py --write`와 `projection_check.py`로 두 문서의 승인 표시를 갱신해야 합니다.
- 검토 화면의 링크 클릭 이동과 모바일 폭은 확인하지 못했습니다(`NOT_VERIFIED`).
- 프로젝트에 JOEFLOW 버전이 기록되어 있지 않습니다(지금 쓰는 스크립트는 1.7.3, `joeflow_version.py --pin`이 필요). 추가 파일을 만들어야 해서 이번에는 하지 않았습니다.
- 구현과 런타임 검증은 하지 않았습니다.

셸 명령 기록은 commands.log에 있습니다. 첫 줄이 pwd 결과이고, 그 뒤로 명령마다 한 줄씩 종료 코드와 함께 남겼습니다. 첫 시도 한 건은 cp949 출력 오류로 exit 1이었고, `PYTHONIOENCODING=utf-8`로 다시 실행했습니다. 파일 편집과 브라우저 확인은 셸 명령이 아니라서 로그에 없습니다.

Files are in `<SCRATCH>\runs\r01`:
- `project\product-definition\request-form\MASTER_PLANNING_SPEC.md`
- `project\product-definition\request-form\planning-review-core.html`
- `commands.log`
