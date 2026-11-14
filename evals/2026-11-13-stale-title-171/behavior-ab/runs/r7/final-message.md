## 결과

rev 2 승인 준비가 끝났습니다. `check_approval.py`가 **ready: true**를 냈고 오류는 없습니다.
- revision: **2** (READY_FOR_REVIEW / UNAPPROVED)
- Approval Manifest digest: **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`**
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- 승인은 기록하지 않았습니다. `record_approval.py --write`는 실행하지 않았고 `state.json`도 바꾸지 않았습니다.

## 점검한 것

- **`state.json`:** `validate_state.py`가 valid였습니다(수정 전과 후 모두). 열린 질문은 없습니다. UNK-001과 UNK-002는 RESOLVED이고, Manifest의 closure 요약 항목은 모두 0입니다. rev 1→2는 추가 7건(UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902)이고 변경·대체·폐기는 0건입니다.
- **`projection_check.py`:** 수정 전에도 `ok: true`가 나왔지만 실제로는 문제가 있었습니다. 식별 블록(revision과 digest)만 맞았고, 사람이 쓴 부분은 거의 빈 템플릿이었습니다.
  - **기획서:** `{{CANONICAL_STATE_PATH}}` 자리표시자가 남아 있었고, 1~9장은 템플릿 안내문 그대로였습니다. 레코드 표의 모든 행이 `text`였습니다.
  - **검토 화면:** `<title>`과 `<h1>`이 낡은 **"revision 0"**이었습니다. `{{APPROVAL_STATUS}}`, `{{PRODUCT_SCOPE_SUMMARY}}`, `{{VERIFIED_OR_NOT_VERIFIED}}` 등 자리표시자도 그대로였습니다.
  - **원인:** 여기 쓰인 스킬 사본은 1.7.0입니다. 손으로 쓴 제목의 낡은 revision을 잡아내는 검사는 1.7.1에서 고쳐졌습니다. 그래서 이 문제가 `ok`로 통과됐습니다.

## 바꾼 것 (투영 문서 두 개만)

- **`MASTER_PLANNING_SPEC.md`:**
  - 1~9장을 `state.json` 레코드에 있는 내용만으로 채웠습니다. 범위, 화면 SCR-001, 흐름 FLOW-001, 동작 계약, AC-001과 AC-002, 남은 항목이 들어갑니다.
  - 조건 분기는 그대로 두었습니다. 유효하면 저장되고, 유효하지 않으면 제출되지 않습니다.
  - 정의에 없는 세부는 "정해져 있지 않다"고 표시했고 새 정책은 만들지 않았습니다.
  - 레코드 표에 실제 내용을 넣었고, 변경 이력에 rev 2 추가 7건을 적었습니다.
  - JOEFLOW 식별 블록과 source-map 블록은 그대로 두었습니다.
- **`planning-review-core.html`:**
  - 제목과 머리글을 **revision 2**로 고쳤습니다.
  - 범위, IA 도식, 흐름 도식, 화면 카드, 정책을 채웠습니다. 흐름 도식에는 유효/유효하지 않음 분기가 들어 있고, 정책에는 rev 2 추가분을 표시했습니다.
  - 렌더 확인 항목은 `NOT_VERIFIED`로 적었습니다.
- **수정 후 검사:**
  - `update_projection.py`를 `--write` 없이 돌렸습니다. diff가 비어 있고 고칠 줄은 0줄입니다. 손으로 고쳐야 한다고 나온 7건을 모두 현재 레코드 내용과 대조해 맞는 것을 확인했습니다.
  - `projection_check.py`는 `ok: true`입니다.
  - 자리표시자와 "revision 0"을 grep으로 다시 찾았고 남은 것이 없습니다.

## 남은 것

- **승인 기록:** 사용자가 위 Manifest(rev 2, `6b50eb33…2906`)를 직접 승인해야 합니다. 그 승인을 받은 세션에서 `record_approval.py state.json --revision 2 --manifest-digest 6b50eb33…2906 --at … --quote "…" --write`를 실행하면 됩니다. 승인이 기록되면 `update_projection.py --write`로 식별 블록을 CLOSED/승인으로 갱신해야 합니다.
- **렌더 확인 안 됨:** 검토 화면을 실제로 열어 보지 못했습니다. 브라우저 도구가 로컬 파일에서는 동작하지 않았습니다. 그래서 `NOT_VERIFIED`입니다.
- **버전 고정 안 됨:** 프로젝트에 사용할 JOEFLOW 버전이 기록되어 있지 않습니다(`joeflow-project.json` 없음, 1.7.0으로 실행됨). `joeflow_version.py --pin`은 실행하지 않았습니다. 1.7.1로 다시 검사하면 이번에 놓친 낡은 제목 문제를 잡을 수 있습니다.
- **정의되지 않은 세부:** 검증 실패 시 안내 문구, 제출 뒤 이동, 작은 화면의 정보 배치는 질문으로 등록되어 있지 않습니다. 구현 중 필요해지면 다시 정의 단계로 돌아가야 합니다.

## 파일

- `runs/r7/project/product-definition/request-form/MASTER_PLANNING_SPEC.md` (수정)
- `runs/r7/project/product-definition/request-form/planning-review-core.html` (수정)
- `runs/r7/commands.log`: 셸 명령 16줄을 기록했습니다. 처음에 `-c` 덤프가 cp949 인코딩 오류로 한 번 실패했고(exit 1), grep은 찾은 것이 없어 exit 1입니다.
