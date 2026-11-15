## 결과
rev 2는 승인 준비가 끝났습니다. `check_approval.py` 결과는 `ready: true`, `errors: []`, `written: false`입니다. 고친 것은 검토 화면 HTML의 잘못된 revision 표기 두 곳뿐이고, 승인 기록(`record_approval.py --write`)은 실행하지 않았습니다.

- **revision:** 2 (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- **Approval Manifest digest:** `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- **Definition digest:** `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

## 점검한 것
- `projection_check.py`는 처음에 `ok: false`로 끝났습니다. 검토 화면의 `<title>`(6행)과 `<h1>`(23행)이 "revision 0"으로 되어 있었습니다(`stale_review_title_revision`). 고친 뒤 다시 돌려 `ok: true`가 나왔습니다.
- `update_projection.py`를 쓰기 없이 돌렸을 때 바뀌는 줄은 0개였습니다. identity 블록과 source map이 이미 최신이어서 `--write`는 하지 않았습니다.
- `build_approval_manifest.py`가 다시 계산한 manifest digest는 두 문서에 적힌 값(6b50eb33…)과 같습니다.
- `validate_state.py`는 valid, 오류 0건입니다. `approval_status.py`로는 rev 2만 승인 대기 중이고, rev 1 대비 추가 7건·변경 0건·대체 0건·폐기 0건임을 확인했습니다.
- 정본(state.json)과 두 문서를 직접 대조했습니다. rev 2에서 추가된 EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002가 두 문서 모두에 들어 있습니다. 조건이 붙은 분기를 일반 결과로 바꾼 곳도, 정본에 없는 분기를 더한 곳도 찾지 못했습니다.

## 바꾼 것
- `<SCRATCH>\r08\project\product-definition\request-form\planning-review-core.html`
  - `<title>`: "revision 0" → "revision 2"
  - `<h1>`: "(revision 0)" → "(revision 2)"
- `state.json`과 `MASTER_PLANNING_SPEC.md`는 바꾸지 않았습니다.

## 바꾸지 않은 지적과 이유
- **DEC-002 / UNK-002 (실질적인 문제):** UNK-002는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)를 근거로, 추천안 BELOW(항상 표시)를 사용자가 수락한 것(USER_ACCEPTED_RECOMMENDATION)으로 해소되어 있습니다. 그런데 이 원문은 BELOW(항상 표시)와 NEAR_LIMIT(180자부터 표시) 가운데 어느 것도 고르지 않았습니다. 따라서 사용자가 이 추천을 직접 수락했다는 근거는 약합니다.
  - 정본을 고치려면 새 revision을 열고 사용자에게 결정을 받아야 합니다. 사용자가 이 대화에 없어 정본은 그대로 두었습니다.
  - 두 문서 모두 이미 "승인 전에 확인할 점"(검토 화면)과 §9 "확인 권장"(Master)에 이 점과 대안을 적어 두고 있습니다.
  - 따라서 사용자는 승인할 때 '항상 표시'가 의도와 맞는지 직접 확인해야 합니다. 사용자가 NEAR_LIMIT를 고르면 새 revision이 필요합니다.
- **렌더 확인 못 함 (NOT_VERIFIED):** 브라우저 창이 여러 세션과 공유되어 페이지가 열리지 않았습니다. 그래서 화면 표시와 클릭 동작은 관찰하지 못했고 결과는 `NOT_VERIFIED`입니다. HTML에도 이미 `NOT_VERIFIED`로 적혀 있습니다.
- **JOEFLOW 버전 미기록:** 스크립트가 버전이 기록되지 않았다고 알립니다(`version_notice`, 현재 1.7.2로 실행). `joeflow_version.py --pin`은 `joeflow-project.json`이라는 설정 파일을 새로 만드는 작업이라 요청 범위 밖이어서 하지 않았습니다.

## 남은 것
1. 사용자가 위 manifest(rev 2, `6b50eb33…2906`)를 보고 명시적으로 승인해야 합니다. 이때 DEC-002의 '항상 표시'도 확인받아야 합니다.
2. 승인을 받으면, 사용자의 말을 직접 받은 세션이 `record_approval.py ... --revision 2 --manifest-digest 6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906 --at <UTC> --quote "..." --write`를 실행합니다.
3. 기록한 뒤에는 `update_projection.py --write`와 `projection_check.py`를 다시 돌려 문서의 승인 상태를 갱신합니다.
4. 검토 화면 렌더를 실제 브라우저로 확인해야 합니다.
5. 선택 사항으로 버전 pin이 남아 있습니다.

명령마다 남긴 실행 기록(명령과 종료 코드)은 `<SCRATCH>\r08\commands.log`에 있습니다.
