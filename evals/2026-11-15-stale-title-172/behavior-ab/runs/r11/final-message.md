## 작업 결과

rev 2 승인 준비는 끝났습니다. `check_approval.py` 결과는 **ready: true**, 오류는 없습니다. 승인은 기록하지 않았습니다(`record_approval.py --write` 미실행). `state.json`은 한 글자도 바꾸지 않았습니다.

- **revision:** 2 (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- **Approval Manifest digest:** `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- **Definition digest:** `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- **변경 범위:** rev 1→2에서 추가 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002), 변경·대체·폐기 0건

## 점검한 것

- `validate_state.py`는 통과했습니다(valid).
- `projection_check.py`가 처음에는 실패했습니다. 기획서 5번째 줄의 머리말 "승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)"이 이전 revision을 가리켰기 때문입니다(`stale_spec_title_revision`). 고친 뒤 다시 돌려 통과했습니다.
- `update_projection.py`는 미리보기로만 돌렸습니다. 두 문서의 신원 블록과 출처표가 이미 현재 상태와 같아서 diff가 0이었고, 그래서 `--write`는 하지 않았습니다.
- 추가된 7건이 기획서와 검토 화면에 어떻게 들어갔는지 정본과 하나씩 대조했습니다. 조건부 분기를 무조건적인 결과로 바꿔 쓴 곳은 없었고, 정본에 없는 정책을 더한 곳도 없었습니다. 거부 문구나 이동 경로처럼 정본에 없는 내용은 두 문서 모두 "정의되지 않음"으로 맞게 적혀 있습니다.
- 검토 화면이 실제로 어떻게 보이는지 확인했습니다. 127.0.0.1 로컬 서버에 띄워 폭 1024px과 375px에서 봤습니다.
  - 페이지가 옆으로 넘치지 않습니다. IA 도식만 자기 칸 안에서 가로로 스크롤됩니다.
  - 상단 메뉴 링크 7개가 모두 해당 절로 이동합니다.
  - 다만 링크로 이동하면 위에 붙어 있는 메뉴가 절 제목을 가렸습니다.

## 바꾼 것 (투영 문서만)

**`MASTER_PLANNING_SPEC.md`**
- 5번째 줄의 오래된 revision 머리말을 rev 2 기준 문구로 바꿨습니다.
- §4의 "제시된 tradeoff"를 "추천안 BELOW의 tradeoff"로 고쳤습니다. 선택지가 사용자에게 제시됐다는 근거가 없기 때문입니다.
- §9에 "rev 2를 승인하면 BELOW(항상 표시)를 고르는 것이고, NEAR_LIMIT을 원하면 rev 3에서 DEC-002·RULE-002·AC-002를 바꿔야 한다"는 문장을 넣었습니다.

**`planning-review-core.html`**
- "승인 전에 확인할 점"에 같은 안내 문장을 넣었습니다.
- 메뉴가 절 제목을 가리지 않도록 `section{scroll-margin-top:64px}`를 더했습니다.
- 렌더 검증 줄을 고정값 "NOT_VERIFIED"에서 실제로 본 결과로 바꿨습니다. 검토자 본인 환경에서의 렌더는 여전히 NOT_VERIFIED입니다.

## 바꾸지 않은 지적과 이유

**1. DEC-002의 출처 기록 (중요)**
- 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)는 위치도, 표시 시점(항상 / 180자부터)도 고르지 않았습니다.
- 그런데 UNK-002와 DEC-002는 이것을 `USER_ACCEPTED_RECOMMENDATION`(`decided_by: USER`, `accepted_at: null`)로 기록해 두었습니다. 사용자가 확인하지 않은 MATERIAL 질문을 닫아 버린 것에 가깝습니다.
- 그래도 state를 고치지 않은 이유는 두 가지입니다. 고치려면 새 revision을 열어야 하는 의미 변경이고, 질문을 할 수 없는 지금은 사용자의 선택을 받을 수 없습니다.
- 대신 두 문서에 "rev 2를 승인하는 것이 곧 '항상 표시'를 고르는 것"이라고 분명히 적었습니다.

**2. 기획서의 "## Approved identity" 제목**
- rev 2는 아직 승인 전이지만, 이 제목은 템플릿의 고정 제목이라 그대로 두었습니다.

**3. 버전 고정 안 됨**
- 프로젝트에 JOEFLOW 버전이 고정되어 있지 않습니다(실행한 버전은 1.7.1). `--pin`은 요청 범위 밖이라 실행하지 않았습니다.

## 남은 것

- 사용자에게 Manifest(rev 2, 위 digest)와 검토 화면을 보여주고, 특히 '항상 표시'인지 '180자부터만 표시'인지를 직접 확인받아야 합니다.
  - 사용자가 승인하면, 그 말을 직접 받은 세션에서 `record_approval.py ... --revision 2 --manifest-digest 6b50…2906 --at … --quote "…" --write`를 실행해야 합니다.
  - 사용자가 '180자부터만 표시'를 고르면 rev 3을 열어야 합니다.
- 승인한 뒤에는 두 문서를 다시 `update_projection.py --write`와 `projection_check.py`로 갱신해야 합니다.
- 필요하면 `joeflow_version.py --pin`으로 버전을 고정합니다.

## 작업 기록과 범위 위반 1건

- 셸 명령 기록은 `<SCRATCH>\r11\commands.log`에 있습니다.
- **범위 위반:** 스크립트 출력을 잘라 보려고 r11 밖의 `/tmp/o.txt`에 한 번 썼습니다. 지시 위반이고, 곧바로 지웠으며 로그에도 남겼습니다.
- `git status`는 이 폴더가 git 저장소가 아니어서 실패했습니다. 로그에 처음 "exit 0"으로 잘못 적었다가 정정 줄을 추가했습니다.
- 첫 로컬 서버(포트 8765)는 404를 돌려줘서 중지하고, 8766으로 다시 띄워 확인한 뒤 중지했습니다.

## 바뀐 파일

- `<SCRATCH>\r11\project\product-definition\request-form\MASTER_PLANNING_SPEC.md`
- `<SCRATCH>\r11\project\product-definition\request-form\planning-review-core.html`
