**결과: rev 2 승인 준비는 기계 검사상 ready다. 다만 사용자가 직접 정해야 할 것이 하나 남아 있다. DEC-002의 '항상 표시'(BELOW)는 사용자가 고른 적이 없다.**

## 점검한 것
- 실행한 스크립트: validate_state, validate_closure, build_approval_manifest, approval_status, update_projection(--write 없이 차이만 확인), projection_check, preflight_state_candidate, check_approval.
- 투영 문서 두 개를 state.json과 하나씩 대조했다.
  - 흐름·행동의 성공/실패 조건을 범용 결과로 뭉개지 않았는지 봤고, 문제없었다.
  - 정본에 없는 화면·규칙·분기는 없었다.
  - rev 2에 추가된 7건은 모두 문서에 반영되어 있었다.
  - 신원 블록(revision 2, definition digest, manifest digest)도 현재 값과 같았다.
- 검토 화면을 내장 브라우저(정적 스냅샷)로 열어 봤다.
  - 폭 1024px와 375px에서 글자와 도식이 렌더됐고, 도식 글자가 상자를 넘지 않았다.
  - 375px에서 페이지 가로 넘침은 없었다. 도식만 칸 안에서 가로 스크롤된다.
  - 내부 앵커는 대상이 있는지만 확인했다.

## 바꾼 것 (투영 문서만, state.json은 손대지 않음)
1. `MASTER_PLANNING_SPEC.md` 5행
   - `승인: revision 1` → "마지막 승인은 revision 1 …이고, 이 문서의 revision 2는 아직 승인되지 않았다"로 고쳤다.
   - projection_check가 이 줄을 `stale_spec_title_revision`으로 지적했고, 원래 문구는 이 문서가 rev 1 승인본처럼 읽힐 수 있었다.
2. 같은 문서 §4
   - "(제시된 tradeoff)" → "추천안 BELOW의 tradeoff — 사용자에게 제시되었다는 기록은 전달된 원문에 없다"로 고쳤다. 근거 없는 '제시됨'을 그대로 옮기지 않으려는 것이다.
3. 같은 문서 §9의 확인 권장 문구를 구체적으로 썼다.
   - 원문은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이다.
   - BELOW/NEAR_LIMIT 선택지가 제시된 기록이 없고, `accepted_at`도 비어 있다.
4. `planning-review-core.html` 상태 섹션
   - 승인 정보 옆에 "승인 전 확인 필요: DEC-002 …" 항목과 정책 섹션 링크를 넣었다.
   - Render verification 줄을 실제로 관찰한 범위로 바꿨다. 클릭 이동과 Master 링크는 `NOT_VERIFIED`로 남겼다.

수정 뒤 projection_check 결과는 `ok: true`다.

## 바꾸지 않은 지적과 이유
- **DEC-002/UNK-002의 출처 결함 (가장 중요):** state.json은 UNK-002를 `USER_ACCEPTED_RECOMMENDATION`(BELOW, `accepted_by: user`)으로 닫았다.
  - 그런데 근거는 다른 세션이 전한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)뿐이다.
  - 이 원문은 위치와 표시 시점(항상 vs 180자부터)을 고르지 않는다. SKILL 규칙상 전달된 원문으로는 그것이 실제로 답한 질문만 닫을 수 있다.
  - 고치려면 정본을 바꾸는 개정(rev 3, UNK-002 재오픈)이 필요하다. 사용자가 없는 상태에서 제품 결정을 되돌리거나 새로 정하는 일은 하지 않았다.
  - 투영 문서에는 이 문제를 승인 전 확인 사항으로 눈에 띄게 남겼다.
- `joeflow_version.py --pin`은 실행하지 않았다. version_notice가 떴지만 `joeflow-project.json`을 새로 쓰게 되어, 맡은 범위 밖으로 판단했다.
- `record_approval.py --write`는 지시대로 실행하지 않았다.

## 승인 준비 결과
- check_approval: **ready: true**, errors 없음.
- revision: **2** (READY_FOR_REVIEW / UNAPPROVED)
- manifest digest: **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`**
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- preflight: PASS, next_action는 `PRESENT_EXACT_MANIFEST_FOR_USER_REVIEW`.
- validate_closure는 승인 전이라 `closed: false`다. 남은 항목은 사용자 승인 없음, 승인 manifest 없음/오래됨, 승인 오래됨 세 가지뿐이다.

## 남은 것
- 사용자에게 rev 2 Manifest를 보여 주고, DEC-002를 BELOW(항상 표시)와 NEAR_LIMIT(180자부터) 중에서 직접 고르게 해야 한다.
  - BELOW를 확인하고 승인하면, 사용자의 말을 받은 세션이 `record_approval.py … --revision 2 --manifest-digest 6b50eb33… --quote "…" --write`로 기록한다.
  - NEAR_LIMIT를 고르거나 출처 결함을 바로잡기로 하면, rev 3을 열어 UNK-002/DEC-002를 다시 작성해야 한다.
- 검토 화면의 앵커 클릭 이동과 `MASTER_PLANNING_SPEC.md` 링크는 `NOT_VERIFIED`다.
- 프로젝트에 JOEFLOW 버전이 고정되어 있지 않다(실행 버전 1.7.2).
- 승인 뒤에는 update_projection --write, projection_check, HANDOFF 컴파일을 해야 한다.

## 파일
- <SCRATCH>\runs\r02\project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- <SCRATCH>\runs\r02\project\product-definition\request-form\planning-review-core.html
- <SCRATCH>\runs\r02\project\product-definition\request-form\state.json (변경 없음)
- <SCRATCH>\runs\r02\commands.log (pwd와 셸 명령별 종료 코드)
