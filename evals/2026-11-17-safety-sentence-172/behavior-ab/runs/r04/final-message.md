## 결론
revision 2는 기계 점검으로는 승인 준비가 됐다. `check_approval.py` 결과는 `ready: true`, `errors: []`이다.
- revision: 2 (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

다만 내용상 확인할 점이 하나 있다(아래 "바꾸지 않은 지적"). `record_approval.py --write`는 실행하지 않았고 승인 기록도 없다.

## 점검한 것
- **state.json 검증:** `validate_state.py` 결과 오류 0. Approval Manifest의 Semantic Closure 요약에서 모든 gap이 0이다. rev 1→2는 추가 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002), 변경·대체·폐기는 0건이다.
- **식별 블록:** `update_projection.py`를 쓰기 없이 실행했다. 두 문서 모두 식별 블록과 source-map 블록에 diff가 없다.
- **내용 대조:** 기획서와 검토 화면의 사람이 쓴 문장을 state 레코드(GOAL, REQ, RULE, FLOW, SCR, STATE, DATA, INT, AC, DEC-002, UNK-002, EVD-901/902)와 직접 맞춰 봤다.
  - 조건부 분기를 일반 규칙으로 바꾼 곳이 없다.
  - 정본에 없는 화면·규칙·분기도 추가되지 않았다.
  - 정의되지 않은 항목(거부 문구, 복구, 제출 뒤 이동)은 "정의되지 않음"으로 정직하게 적혀 있다.
- **`projection_check.py`:** 처음에는 `ok: false`였다. 기획서 5행의 `stale_spec_title_revision`("> 승인: revision 1") 때문이다. 수정한 뒤 다시 돌려 `ok: true`가 됐다.
- **렌더 확인:** Browser pane의 정적 스냅샷에서 데스크톱 폭과 375px 폭을 봤다.
  - 본문 가로 넘침이 없고, IA 도식만 자체 가로 스크롤된다.
  - 목차 링크 7개의 대상이 모두 있고, 'IA' 링크 클릭이 동작한다.
  - 첫 스냅샷은 디스크 파일과 다른 문구("…직접 고르는 것입니다")를 보여줬다. 그래서 그 스냅샷은 근거로 쓰지 않았다. 내가 파일을 수정한 뒤 다시 연 스냅샷이 디스크 내용과 일치하는 것을 확인했다.

## 바꾼 것
`project/product-definition/request-form/` 안의 투영 문서 두 개만 고쳤다. `state.json`은 건드리지 않았다.
1. **`MASTER_PLANNING_SPEC.md` 5행:** "> 승인: revision 1 (…)"을 "> 마지막 승인은 revision 1 (…). revision 2는 아직 승인되지 않았다."로 바꿨다. 사실은 그대로 두고, 이 문서의 리비전 제목으로 오인되던 문구만 고쳤다.
2. **`MASTER_PLANNING_SPEC.md` §9와 `planning-review-core.html`의 "승인 전에 확인할 점":** rev 2를 승인하면 '항상 표시(BELOW)'를 사용자가 직접 확정하는 것이 된다는 문장을 넣었다. NEAR_LIMIT를 원하면 승인하지 않고 UNK-002를 다시 열어 새 revision을 만든다는 안내도 함께 넣었다.
3. **`planning-review-core.html`의 Render verification 줄:** `NOT_VERIFIED`를 위 관찰 범위로 바꿨다. 다른 브라우저와 인쇄는 여전히 `NOT_VERIFIED`로 남겼다.

## 바꾸지 않은 지적과 이유
- **DEC-002의 근거가 약하다.** UNK-002와 DEC-002는 `USER_ACCEPTED_RECOMMENDATION`(추천안 BELOW 수락)으로 기록돼 있다. 그런데 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"뿐이다. 이 말은 "더하고 싶은 것이 있나요?"에 대한 답이었다. 위치와 표시 시점(BELOW 대 NEAR_LIMIT)을 고르지 않았고, 추천안을 받아들인 말로도 보기 어렵다.
- **state를 고치지 않은 이유:** 이를 state에서 바로잡으려면 UNK-002를 다시 열어 rev 3을 만들고 사용자에게 물어야 한다. 사용자가 없는 상황에서 제품 결정을 바꾸거나 새로 지어낼 수 없다. 그래서 정본은 그대로 두고, 승인 화면에서 이 선택이 분명히 보이도록 하는 데까지만 했다.
- **승인받을 때 할 일:** 사용자가 'BELOW 확정'을 명시적으로 승인해야 한다. 그러지 않으면 UNK-002를 다시 열어야 한다.

## 남은 것
- **실제 승인:** 사용자가 위 manifest(rev 2, `6b50eb33…2906`)를 보고 직접 승인해야 한다. 승인 말을 직접 받은 세션에서 `record_approval.py … --write`로 기록한다. 이번 작업은 모의라서 실행하지 않았다.
- **버전 고정:** JOEFLOW 버전이 고정돼 있지 않다(현재 1.7.2 실행 중). `joeflow_version.py --pin`은 `joeflow-project.json`에 쓰는 작업이라 하지 않았다.
- **승인 뒤 작업:** `update_projection.py --write`, `projection_check.py`, HANDOFF 컴파일. 구현과 런타임 검증은 하지 않았다.
- **작업 기록:** `<SCRATCH>\runs\r04\commands.log`

## 파일
- `<SCRATCH>\runs\r04\project\product-definition\request-form\MASTER_PLANNING_SPEC.md`
- `<SCRATCH>\runs\r04\project\product-definition\request-form\planning-review-core.html`
