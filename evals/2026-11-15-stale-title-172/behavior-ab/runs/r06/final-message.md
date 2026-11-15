## rev 2 승인 준비 결과: ready, 승인은 기록하지 않음

- **ready: true**. `check_approval.py`가 오류 없이 종료됐다(종료 코드 0, `written: false`).
- **revision:** 2 (READY_FOR_REVIEW / UNAPPROVED)
- **Approval Manifest digest:** `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- **definition digest:** `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

`record_approval.py --write`는 실행하지 않았다. state.json의 승인 상태는 그대로 UNAPPROVED다.

## 점검한 것

- `validate_state.py`는 valid였고 오류가 없었다.
- `build_approval_manifest.py`로 다시 계산한 manifest digest가 두 투영 문서에 적힌 값과 같았다.
- `projection_check.py`를 처음 돌렸을 때 `ok: false`였다. 검토 화면 제목 두 곳이 "revision 0"으로 되어 있었다(stale_review_title_revision, 6행 `<title>`과 23행 `<h1>`).
- 기획서는 추가된 레코드 누락, 다시 읽을 변경 레코드, 대체·폐기 레코드 언급, identity 불일치가 모두 없었다.
- 기획서와 검토 화면의 문장을 state.json 레코드와 직접 맞춰 봤다. 대상은 GOAL, USR, REQ, FLOW, SCR, STATE, DATA, INT, RULE-001/002, DEC-001/002, UNK-001/002, AC-001/002, TASK-001/002, EVD-901/902다.
  - 정본에 없는 분기·정책을 더한 곳은 없었다. 조건부 결과를 일반 결과로 바꾼 곳도 없었다.
  - 정의되지 않은 것(거부 문구, 복구, 제출 후 이동)은 "정의되지 않음"으로 그대로 적혀 있었다.

## 바꾼 것

- `project/product-definition/request-form/planning-review-core.html`의 `<title>`과 `<h1>`에서 "revision 0"을 "revision 2"로 고쳤다. 다시 돌린 `projection_check.py`는 `ok: true`였다.
- `MASTER_PLANNING_SPEC.md`와 `state.json`은 바꾸지 않았다.

## 바꾸지 않은 지적과 그 이유

**DEC-002 / UNK-002의 해소 근거가 약하다.** 승인 전에 사람이 꼭 판단해야 하는 지적이다.
- state에는 USER_ACCEPTED_RECOMMENDATION(추천안 BELOW 수락, `accepted_by: user`, `accepted_at: null`)으로 기록돼 있다.
- 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"뿐이다(RELAYED_USER_INTENT).
- 이 원문은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이다. 사용자는 BELOW와 NEAR_LIMIT 두 선택지를 본 적도, 고른 적도 없다.
- 스킬 규칙상 전달받은 원문은 그 질문에 직접 답할 때만 material 질문을 닫을 수 있다. 그래서 UNK-002는 원래 OPEN으로 남아 있어야 했을 가능성이 높다.

state를 고치지 않은 이유는 세 가지다.
- 이번 일은 투영 문서 점검과 승인 준비였다. 고치려면 정본을 rev 3으로 올리는 material 변경(`open_revision.py`)이 필요하다.
- 질문할 사용자가 없어서, 질문을 다시 열어도 닫을 방법이 없다.
- 기획서 §9와 검토 화면의 "승인 전에 확인할 점"이 이미 이 점을 드러내고 있다. 원문이 위치나 표시 시점을 고르지 않았다는 점, '항상 표시'를 확인해야 한다는 점, 대안 NEAR_LIMIT가 모두 적혀 있다. 그래서 투영 문서는 정본을 충실하게 옮긴 것으로 판단했다.

## 남은 것

1. **실제 승인.** 사용자가 위 Manifest(rev 2, `6b50eb33…2906`)를 보고 '항상 표시(BELOW)'를 직접 확인한 뒤 승인해야 한다. 기록은 사용자의 말을 직접 받은 세션에서 `record_approval.py … --quote "…" --write`로 한다. 사용자가 NEAR_LIMIT를 원하거나 확인하지 않으면 UNK-002를 다시 열고 rev 3으로 가야 한다.
2. **검토 화면 렌더 확인: NOT_VERIFIED.** 브라우저 창에 로컬 파일로 열리긴 했지만 스크린샷이나 페이지 읽기를 할 수 없었다. 확인한 것은 정적 구조와 텍스트뿐이다.
3. **JOEFLOW 버전 미고정.** check_approval이 이 프로젝트에 버전 기록이 없다고 알렸다(실행 버전 1.7.2). `joeflow_version.py STATE_JSON --pin`은 `joeflow-project.json`을 새로 만드는 설정 변경이라 실행하지 않았다.
4. **승인 뒤 할 일.** `update_projection.py --write`와 `projection_check.py`로 identity를 다시 맞추고, 그다음 HANDOFF로 간다.

명령 기록은 `<SCRATCH>\r06\commands.log`에 있다. 맨 앞이 pwd 결과이고, 그 뒤로 명령마다 한 줄씩 명령과 종료 코드가 적혀 있다. 인코딩 오류로 실패한 한 번(종료 코드 1)도 들어 있다. Manifest 사본은 `<SESSION_SCRATCHPAD>\manifest.json`에 있다.
