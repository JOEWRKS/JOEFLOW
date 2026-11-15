## 결론
rev 2는 기계적으로 승인 준비가 끝났습니다. `check_approval.py`가 `ready: true`, errors 0을 반환했습니다. 다만 DEC-002의 근거가 약해서, 승인을 받을 때 사용자가 표시 방식을 직접 골라야 합니다. 승인 기록(`record_approval.py --write`)은 지시대로 실행하지 않았습니다.

## 점검한 것
- **정본 검증**
  - `validate_state.py`: valid.
  - `validate_closure.py`: exit 1. 남은 지표는 승인이 없다는 것뿐입니다(missing_user_approval, stale_approval, missing_or_stale_approval_manifest 각 1). 그 밖의 지표는 모두 0입니다.
  - `preflight_state_candidate.py`: PASS. 다음 할 일은 `PRESENT_EXACT_MANIFEST_FOR_USER_REVIEW`입니다.
  - `approval_status.py`: rev 2 미승인, 마지막 승인은 rev 1, 추가 7건·변경/대체/폐기 0건.
- **투영 기계 점검**
  - `projection_check.py`: 처음에는 `ok: false`였습니다. 기획서 5행의 `stale_spec_title_revision` 1건 때문입니다.
  - `update_projection.py`를 dry-run으로 돌렸더니 diff가 비어 있었습니다. 식별 정보·source map 블록이 이미 최신이라 `--write`는 하지 않았습니다.
  - 손으로 고쳐야 한다고 지목된 추가 레코드 7건(EVD-901/902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)이 나오는 줄을 현재 정본 내용과 대조했고, 어긋난 곳은 없었습니다.
- **충실도 점검(사람이 직접)**: FLOW-001, SCR-001, STATE-001, DATA-001, INT-001, AC-001/002, TASK를 state.json과 대조했습니다.
  - 조건부 결과를 무조건 결과처럼 바꿔 쓴 곳은 없습니다.
  - 정본에 없는 분기·화면을 만들어 넣은 곳도 없습니다.
  - 정의되지 않은 항목(거부 문구, 복구, 제출 뒤 이동)은 두 문서 모두 "정의되지 않음"으로 정직하게 적혀 있습니다.
- **렌더 확인**: 브라우저 창에서 로컬 파일은 화면 캡처나 조작이 막혀 있어 화면을 관찰하지 못했습니다. 그래서 `NOT_VERIFIED`로 둡니다. 검토 화면에도 이미 그렇게 적혀 있습니다.

## 바꾼 것
- `<SCRATCH>\r13\project\product-definition\request-form\MASTER_PLANNING_SPEC.md` 5행 한 줄만 고쳤습니다.
  - 전: "승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)". 문서는 rev 2 내용을 담고 있어서 사실과 다르고, 점검기도 이 줄을 지적했습니다.
  - 후: "이 문서는 승인 대기 중인 revision 2의 내용을 담는다. 마지막 승인은 revision 1이다."
  - 고친 뒤 `projection_check.py`는 `ok: true`입니다.
- `planning-review-core.html`과 `state.json`은 바꾸지 않았습니다.

## 바꾸지 않은 지적
**DEC-002의 근거.** UNK-002는 `USER_ACCEPTED_RECOMMENDATION`(추천안 BELOW를 사용자가 수락함)으로 해소된 것으로 기록되어 있습니다. 그런데 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"뿐입니다. 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이지, 위치나 표시 시점(항상 보임 / 180자부터 보임)을 고른 말이 아닙니다. 사용자가 추천안을 보고 받아들였다는 근거가 없고, `accepted_at`도 null입니다.

state를 고치지 않은 이유는 다음과 같습니다.
- 고치려면 rev 3을 열어 UNK-002를 다시 OPEN으로 돌려야 합니다. 사용자가 없는 상태에서 하는 중대한 의미 변경입니다.
- 이번 작업 범위(투영 점검과 승인 준비)를 벗어납니다.
- 두 투영 문서가 이미 "승인 전에 확인할 점"으로 이 문제를 사용자에게 드러내고 있습니다.

## 승인 준비 결과
- ready: **true**
- revision: **2**
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

## 남은 것
- **사용자 승인.** 위 Manifest를 그대로 보여 주고, 그 자리에서 DEC-002를 고르게 해야 합니다: BELOW(항상 표시)인지 NEAR_LIMIT(180자부터 표시)인지.
  - 사용자가 BELOW를 명시적으로 확인하면 사용자의 말을 받은 세션이 `record_approval.py … --quote "…" --write`로 기록합니다.
  - NEAR_LIMIT을 고르거나 답이 분명하지 않으면 승인하지 말고 rev 3을 열어 다시 정해야 합니다.
- **버전 고정.** `joeflow-project.json`이 없어서 버전이 고정되어 있지 않습니다(실행 버전 1.7.2). `joeflow_version.py --pin`은 요청 범위 밖이라 실행하지 않았습니다.
- **승인 뒤 할 일.** 승인되면 투영을 갱신하고(`update_projection.py --write`, `projection_check.py`) HANDOFF 단계로 넘어갑니다. 검토 화면 렌더 확인도 여전히 필요합니다.
- **명령 기록.** `<SCRATCH>\r13\commands.log`에 남겼습니다. 이 폴더는 git 저장소가 아니어서 커밋은 없습니다.
