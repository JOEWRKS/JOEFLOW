## rev 2 승인 준비 보고

rev 2는 승인 준비가 끝났습니다. `check_approval.py` 결과는 `ready: true`, `errors: []`입니다. 승인 기록(`record_approval.py --write`)은 지시대로 실행하지 않았고, `state.json`도 바꾸지 않았습니다.

### 점검한 것
- **정본과 두 문서 대조:** `state.json` rev 2(READY_FOR_REVIEW / UNAPPROVED)와 `MASTER_PLANNING_SPEC.md`, `planning-review-core.html`의 내용을 서로 맞춰 봤습니다.
  - rev 2에서 추가된 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)이 두 문서에 모두 들어가 있습니다.
  - 정본에 없는 정책이나 분기를 문서가 지어낸 곳은 없습니다. 정의되지 않은 부분(거부 시 문구, 복구, 제출 뒤 이동)은 "정의되지 않음"으로 바르게 적혀 있습니다.
- **`projection_check.py`:** 처음에는 실패했습니다(`stale_spec_title_revision`, 기획서 5행 "> 승인: revision 1 …"). 고친 뒤 다시 돌려서 `ok: true`가 나왔습니다.
- **Manifest 재계산:** `build_approval_manifest.py`로 다시 계산한 manifest digest가 두 문서에 적힌 값과 같습니다.
- **검토 화면 렌더:** 미리보기 창에서 열어 데스크톱 폭으로 확인했습니다. 정적 스냅샷이고, 본문과 SVG가 보이는 것까지 확인했습니다.

### 바꾼 것 (투영 문서 두 줄만)
1. **`MASTER_PLANNING_SPEC.md` 5행:**
   - 바꾼 내용: "> 승인: revision 1 (…)" → "> 마지막 승인은 revision 1 (`dd1e837b…`)이며, 이 문서의 revision 2는 아직 승인되지 않았다."
   - 이유: 원래 문장은 사실이었지만, 문서 자체의 승인 revision처럼 읽힐 수 있었습니다. rev 2는 아직 승인 전이라 숫자를 2로 바꾸면 틀린 말이 됩니다. 그래서 숫자 대신 뜻이 분명한 문장으로 고쳤습니다.
2. **`planning-review-core.html`의 Render verification 줄:**
   - 바꾼 내용: "렌더를 관찰하지 못함" → "데스크톱 폭 렌더 관찰됨(정적 스냅샷)".
   - 탐색 링크와 Master 링크 클릭, 모바일 폭은 확인하지 못해서 `NOT_VERIFIED`로 남겼습니다.

### 바꾸지 않은 지적: DEC-002 (실제로 남은 위험)
- **문제:** DEC-002는 다른 세션이 전달한 사용자 말(EVD-901, RELAYED_USER_INTENT) "요청 내용 칸에 글자 수 보여줘"를 근거로, 추천안 BELOW(칸 아래 오른쪽에 항상 표시)를 "추천 수락"으로 기록했습니다. 그런데 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"라는 질문에 대한 답입니다. 표시 위치나 시점(항상 표시 / 180자부터만 표시)을 직접 고른 말이 아닙니다. `accepted_at`도 비어 있습니다.
- **고치지 않은 이유:** 이건 문서 표현 문제가 아니라 정본의 권한 문제입니다. 사용자가 이 대화에 없으니 제가 정본을 바꾸거나 결정할 수 없습니다.
- **현재 처리:** 두 문서 모두 "승인 전에 확인할 점"에 이 사실과 대안(NEAR_LIMIT)을 이미 분명히 적어 두었습니다. 사용자가 그 내용을 본 뒤 rev 2를 승인하면 확인이 됩니다. 사용자가 NEAR_LIMIT를 고르면 새 revision을 열어야 합니다.

### 승인 준비 결과 (`check_approval.py`)
- ready: **true**, errors: []
- revision: **2**
- manifest digest: **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`**
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- `version_notice`: 이 프로젝트에는 JOEFLOW 버전 고정 기록이 없고, 실행한 스크립트는 1.7.2입니다. 고정 기록 파일을 새로 쓰게 되므로 `--pin`은 실행하지 않았습니다.

### 남은 것
- **사용자 승인:** 사용자가 위 Manifest를 직접 보고 승인해야 합니다. 특히 DEC-002의 "항상 표시"가 맞는지 확인이 필요합니다. 그 뒤 사용자의 말을 받은 세션에서 `record_approval.py … --revision 2 --manifest-digest 6b50eb33… --quote "…" --write`를 실행해야 합니다.
- **승인 뒤 문서 갱신:** 승인되면 `update_projection.py --write`와 `projection_check.py`를 다시 돌려야 합니다.
- **버전 고정:** `joeflow_version.py --pin`을 실행할지 정해야 합니다.
- **미확인 렌더 항목:** 검토 화면의 링크 클릭과 모바일 폭 렌더는 확인하지 못했습니다(`NOT_VERIFIED`).

### 작업 기록
- `commands.log`에 `pwd`와 이후 명령, 종료 코드를 적었습니다.
- 맨 처음 `ls` 한 번은 기록하지 못했습니다.
- manifest를 r07 밖의 scratchpad에 저장하려던 명령 하나는 권한 거부로 실행되지 않았습니다. 대신 화면 출력으로 확인했습니다.

파일:
- <SCRATCH>\runs\r07\project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- <SCRATCH>\runs\r07\project\product-definition\request-form\planning-review-core.html
- <SCRATCH>\runs\r07\commands.log
