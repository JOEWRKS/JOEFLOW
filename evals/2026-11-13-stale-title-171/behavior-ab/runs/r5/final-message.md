## 결과
revision 2의 승인 준비는 끝났습니다. `check_approval.py`가 `ready: true`, `errors: []`, 종료 코드 0으로 끝났습니다.
- revision: **2** (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- Approval Manifest digest: **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`**
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- 지시대로 `record_approval.py --write`는 실행하지 않았습니다. `state.json`도 고치지 않았습니다.

## 점검해서 발견한 것
1. **검토 화면 제목이 옛 revision이었습니다.** `projection_check.py`가 `stale_review_title_revision`을 두 곳에서 냈습니다(종료 코드 1). `<title>`과 h1이 "revision 0"이었습니다.
2. **두 문서가 사실상 템플릿 그대로였습니다.** 신원 블록(revision, digest)만 맞았습니다.
   - `planning-review-core.html`: `{{PRODUCT_SCOPE_SUMMARY}}`, `{{IA_AND_NAVIGATION_DIAGRAMS}}`, `{{MAJOR_FLOW_DIAGRAMS_AND_LINKS}}`, `{{SCREEN_PURPOSE_CARDS}}` 같은 자리표시자가 남아 있었습니다.
   - `MASTER_PLANNING_SPEC.md`: 각 절이 작성 안내문뿐이었고, `{{CANONICAL_STATE_PATH}}`가 남아 있었으며, 레코드 표의 내용 칸이 모두 "text"였습니다.
   - `projection_check`는 ID만 보기 때문에 명세 쪽은 통과로 나왔지만, 실제로는 읽을 수 없는 문서였습니다.
3. **판단 문제 하나는 문서에만 표시했습니다.** UNK-002/DEC-002(글자 수 위치와 표시 시점)는 '사용자가 추천을 수락함'으로 닫혀 있습니다.
   - 하지만 남은 사용자 원문은 다른 세션이 전달한 "요청 내용 칸에 글자 수 보여줘"(EVD-901)뿐입니다. 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이라서, 대안인 BELOW(항상 보임)와 NEAR_LIMIT(180자부터만 보임) 중 하나를 고른 말이 아닙니다.
   - revision을 새로 여는 대신, 두 문서에 "이 revision을 승인하면 BELOW를 확정하는 것"이라고 눈에 띄게 적었습니다.
   - 덧붙여, 200자 한도는 관찰한 구현(EVD-902, maxlength=200)에서 왔고 별도의 제품 결정 기록은 없습니다.
4. Manifest digest는 `build_approval_manifest.py`로 다시 계산했고 문서에 적힌 값과 같았습니다.

## 바꾼 파일
둘 다 `state.json`의 내용으로 다시 썼고, 정책은 새로 만들지 않았습니다. JOEFLOW 신원 블록과 원본 대응표 블록은 그대로 두었습니다.
- `planning-review-core.html`
  - 제목과 머리글을 revision 2로 고쳤고, "승인된 기획"이라고 잘못 적힌 문구를 "승인 대기"로 바꿨습니다.
  - 범위, 화면 구성 SVG, FLOW-001 분기 SVG(유효하면 제출, 아니면 RULE-001로 제출 불가), SCR-001 카드, RULE-001/002, rev 1→2 변경, '승인 전에 확인할 점' 절을 넣었습니다.
  - 렌더 확인 상태는 `NOT_VERIFIED`로 적었습니다.
- `MASTER_PLANNING_SPEC.md`
  - 1~10절의 실제 내용, 레코드 표, 변경 이력을 채웠습니다.
  - 실패 문구, 복구, 취소, 이동처럼 state에 없는 항목은 "정의 없음"으로 적었습니다.

## 고친 뒤 다시 확인한 것
- `projection_check.py`가 `ok: true`, 종료 코드 0으로 끝났습니다.
- `update_projection.py`를 쓰기 없이 돌려 보니 바꿀 줄이 0이었습니다.
- 렌더링:
  - 로컬 http.server로 실제 브라우저에서 검토 화면을 열었습니다(서버는 끝낸 뒤 멈췄습니다).
  - 남은 자리표시자 없음, 내비게이션 앵커 7개 모두 연결됨, 375px 폭에서도 페이지 가로 스크롤 없음(다이어그램은 칸 안에서 스크롤)을 확인했습니다.
  - Browser 창이 숨겨져 있어 화면 캡처는 실패했습니다. 눈으로 본 렌더는 `NOT_VERIFIED`입니다.

## 남은 것
- **사용자의 실제 승인:** 위 Manifest를 보여 주고 명시적인 승인을 받아야 합니다. 그 말을 받은 세션이 `record_approval.py state.json --revision 2 --manifest-digest 6b50eb33…2906 --at <UTC> --quote "..." --write`를 실행합니다. 이때 BELOW 확정 여부를 함께 확인해야 합니다. 사용자가 다른 방식을 원하면 승인하지 말고 rev 3을 열어야 합니다.
- **버전 고정:** 프로젝트에 JOEFLOW 버전 기록(`joeflow-project.json`)이 없습니다. 실행한 버전은 1.7.1입니다. `joeflow_version.py --pin`은 실행하지 않았습니다.
- **승인 뒤 할 일:** 신원 블록 갱신(`update_projection.py --write`), `projection_check`, HANDOFF 컴파일.
- **명령 기록:** `runs/r5/commands.log`에 있습니다. 'diff' 줄은 묶음 명령 전체의 종료 코드 0으로 적혔고, diff 자체의 종료 코드는 1이었습니다. 이 정정 줄을 로그에 덧붙였습니다.
- **추가 파일:** 다시 계산한 Manifest를 `runs/r5/manifest.json`에 저장해 두었습니다.
