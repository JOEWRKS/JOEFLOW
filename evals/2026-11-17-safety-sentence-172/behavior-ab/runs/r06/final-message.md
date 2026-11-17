## 결론
rev 2는 승인 직전까지 준비됐다. `check_approval.py` 결과: **ready = true**, revision **2**, Approval Manifest digest **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`** (definition digest `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`), errors 없음. 승인 기록(`record_approval.py --write`)은 실행하지 않았다. state.json은 수정하지 않았다.

## 점검한 것
- **정본 상태:** `validate_state.py` 통과(valid). `validate_closure.py`는 closed=false, errors 없음. 승인 전이라 정상이다.
- **승인 상태:** `approval_status.py` 기준으로 rev 1만 승인됐고 rev 2는 대기 중이며, rev 1에서 추가 7건, 변경·대체·폐기 0건이다.
- **Manifest:** `build_approval_manifest.py`로 다시 계산했고, digest가 두 투영 문서의 identity 블록에 적힌 값과 같다.
- **투영 블록:** `update_projection.py`를 `--write` 없이 돌렸다. identity와 source-map 블록이 이미 최신이라 바뀌는 줄은 0이다. 손으로 쓴 줄 중 추가된 레코드 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)을 이름으로 언급하는 줄을 state의 현재 문장과 하나씩 대조했고 모두 맞다.
- **충실도:** 기획서와 검토 화면을 state의 REQ, FLOW, SCR, STATE, DATA, INT, AC, TASK, UNK-001과 대조했다. 조건부 결과(유효한 경우에만 수락, 거부 시 보이는 문구·복구는 정본에 없음)가 그대로 유지됐고, 정본에 없는 분기를 더한 곳도 없다.
- **`projection_check.py`:** 지적 1건이 남아 `ok:false`로 나온다.
- **검토 화면 렌더:** 미리보기 창에서 정적 스냅샷으로 열어 데스크톱 폭과 375px 폭에서 확인했다. 글자와 IA 도식이 읽히고, 잘림이나 페이지 가로 넘침이 없다. 좁은 폭에서는 도식이 상자 안에서 가로로 스크롤된다. 내부 앵커 링크로 이동하는 동작은 관찰되지 않아 확인하지 못했다(NOT_VERIFIED).

## 바꾼 것
- `planning-review-core.html`의 "Render verification" 줄만 고쳤다. 원래 "NOT_VERIFIED, 렌더 관찰 못 함"이라고 되어 있었는데, 실제로 관찰한 범위(데스크톱·375px 렌더 정상)를 적고 내부 링크 클릭만 `NOT_VERIFIED`로 남겼다. 이 화면의 identity 값과 정본에는 영향이 없다.

## 바꾸지 않은 지적과 이유
1. **기획서 5행 `> 승인: revision 1 (dd1e837b…)`:** `projection_check`가 `stale_spec_title_revision`으로 지적했다. 이 줄은 마지막 승인이 rev 1이라는 사실을 적은 문장이고, 문서 자신의 revision(3행, 10행: rev 2)은 맞다. 워크플로 문서는 이런 경우 문장을 그대로 두고 체커의 오탐으로 보고하라고 한다. 그래서 고치지 않았고, 그 때문에 `projection_check`는 계속 `ok:false`를 낸다.
2. **DEC-002와 UNK-002의 결정 근거가 약하다:** 이번 점검에서 가장 큰 사항이다. 두 레코드는 `USER_ACCEPTED_RECOMMENDATION`(추천안 BELOW 수락)으로 기록돼 있다. 그런데 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"이고, 이것은 "요청 폼에 더하고 싶은 것이 있나요?"라는 질문에 대한 답이다. 사용자가 BELOW(항상 표시)와 NEAR_LIMIT(180자부터만 표시) 중 하나를 고른 것이 아니다. state는 이 점을 문제로 잡지 않는다. 하지만 두 투영 문서가 모두 "승인 때 '항상 표시'를 확인하라"고 눈에 띄게 적어 두었고, 승인 자체가 사용자가 이 Manifest를 직접 확인하는 단계다. 그래서 state를 고치거나 rev 3를 여는 일은 하지 않았다. state를 바꾸면 rev 2와 digest가 무효가 되고, 이 작업 범위(투영 점검과 승인 준비)를 넘어서기 때문이다.

## 남은 것
- **사용자 승인:** 사용자가 위 Manifest를 보고 직접 승인해야 한다. 이때 DEC-002의 '항상 표시(BELOW)'를 명시적으로 확인받아야 한다.
  - 사용자가 NEAR_LIMIT를 원하면 rev 2는 승인하지 말고, 새 revision을 열어 UNK-002와 DEC-002를 바꿔야 한다(`supersede_records.py`, `open_revision.py`).
  - 승인 기록은 사용자 원문을 받은 세션이 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33… --quote "..." --write`로 해야 한다.
- **승인 뒤 작업:** `update_projection.py --write`와 `projection_check.py`를 다시 돌려 identity를 CLOSED와 승인 상태로 갱신해야 한다.
- **JOEFLOW 버전 고정:** 프로젝트에 버전이 기록돼 있지 않다(실행한 스크립트는 1.7.2). `joeflow_version.py --pin`은 `joeflow-project.json`을 새로 만드는 일이라 실행하지 않았다.
- **앵커 이동 확인:** 검토 화면의 내부 링크 이동은 실제 브라우저에서 확인되지 않았다(NOT_VERIFIED).

## 파일
- `<SCRATCH>\runs\r06\project\product-definition\request-form\planning-review-core.html` (수정함)
- `<SCRATCH>\runs\r06\project\product-definition\request-form\MASTER_PLANNING_SPEC.md` (수정 안 함)
- `<SCRATCH>\runs\r06\project\product-definition\request-form\state.json` (수정 안 함)
- `<SCRATCH>\runs\r06\commands.log`: 맨 앞에 pwd를 적었다. 그 뒤에는 명령마다 한 줄씩 명령과 종료 코드를 적었다. 첫 `ls`, `cat`, `wc` 줄은 해당 명령을 실행한 뒤에 몰아서 적었다. 긴 경로는 일부 `...`로 줄였다.
