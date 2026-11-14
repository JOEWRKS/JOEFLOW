rev 2 승인 준비는 끝났습니다. `check_approval.py` 결과는 **ready: true**, revision **2**, Approval Manifest digest **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`**(definition digest `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`)입니다. 승인 기록은 하지 않았습니다(`record_approval.py --write` 미실행). `state.json`은 고치지 않았습니다.

**점검한 것**
- `state.json`은 `validate_state.py`에서 오류가 없었습니다. 상태는 READY_FOR_REVIEW / UNAPPROVED이고, 마지막 승인은 rev 1입니다. rev 2에서 추가된 레코드는 7개입니다: UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902.
- `projection_check.py`는 처음부터 ok였습니다. 하지만 기획서·검토 화면 본문을 직접 읽어 보니 사실상 쓸 수 없는 상태였습니다.
  - **검토 화면 제목과 h1이 "revision 0"으로 낡아 있었습니다.** 실행 중인 스킬이 1.7.0이라, 손으로 쓴 제목의 낡은 revision을 잡아내는 검사(1.7.1 수정분)가 없어 통과된 것입니다.
  - HTML 본문 대부분이 `{{...}}` 템플릿 자리표시자로 남아 있었습니다: 범위, IA, 흐름, 화면, 정책, 렌더 확인.
  - 기획서 1~9절은 템플릿 안내문 그대로였고, 레코드 표는 모두 `| ID | text |`였습니다. `{{CANONICAL_STATE_PATH}}`도 남아 있었고, 승인 대기인데 제목이 "Approved identity"였습니다.
- 자동 생성 블록(식별 정보·출처 지도)은 이미 최신이었습니다. `update_projection.py` 미리보기에서 바뀌는 줄이 0줄이었습니다.

**바꾼 것** (`.../runs/r1/project/product-definition/request-form/` 안의 두 파일만)
- `MASTER_PLANNING_SPEC.md`: 1~9절, 레코드 표, 변경 이력을 `state.json` 내용으로 채웠습니다.
  - 근거가 없는 것은 지어내지 않고 "정의되어 있지 않음"으로 적었습니다: "유효함"의 구체 항목, 거부 뒤 복구 방식, 제출 후 다음 화면.
  - 200자 한도는 구현을 관찰한 사실(EVD-902)이지 이번에 정한 정책이 아니라고 구분했습니다.
  - 제목은 "식별 정보 (revision 2 · 승인 대기)"로 바꿨습니다. 자동 생성 블록은 그대로 두었습니다.
- `planning-review-core.html`:
  - 제목과 h1을 revision 2(승인 대기)로 고쳤습니다.
  - 범위, 화면 하나짜리 IA 도식, 흐름 도식을 넣었습니다. 흐름 도식은 FLOW-001 정상 경로와, 유효하지 않을 때만 생기는 거부 분기를 그린 것입니다.
  - SCR-001 카드에 글자 수 표시를 rev 2 표시와 함께 넣고, 정책, rev 2 추가 레코드 목록, 렌더 확인 상태도 넣었습니다.
- 다시 돌린 결과: `update_projection.py`는 바뀌는 줄 0, `projection_check.py`는 ok, 자리표시자와 "revision 0" 검색은 0건입니다.

**검토 화면 렌더 확인: 일부만 확인(PARTIAL)**
- 로컬 서버(127.0.0.1:8765, 확인 후 종료)로 1024px 폭에서 열었습니다.
- 화면으로 본 것: 머리말, 흐름 도식, 화면 카드. 가로 넘침은 없었고 목차 링크 6개의 이동 대상이 모두 있었습니다.
- 정책·상태 섹션은 백그라운드 창이라 스크린샷이 빈 화면으로 나와 텍스트 추출로만 확인했습니다. 모바일 폭은 보지 않았습니다. 둘 다 HTML에 `NOT_VERIFIED`로 적어 두었습니다.

**`validate_closure.py` 종료 코드 1**
- 걸린 항목은 `missing_or_stale_approval_manifest: 1` 하나뿐입니다. 사용자 승인이 아직 없어서 생기는 정상 결과입니다.

**남은 것**
1. 사용자가 위 Manifest를 직접 승인해야 합니다. 그다음 사용자의 말을 받은 세션에서 `record_approval.py --revision 2 --manifest-digest 6b50eb33… --at … --quote "…" --write`를 실행합니다. 승인 뒤에는 `update_projection.py --write`로 식별 블록을 CLOSED로 갱신하고 `projection_check.py`를 다시 돌려야 합니다.
2. **확인이 필요합니다.** DEC-002는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901)를 추천안(칸 아래 오른쪽, 항상 보임) 수락으로 기록했습니다. 그런데 원문은 위치나 표시 시점을 고르지 않았습니다. 승인을 받을 때 이 부분을 사용자에게 명시적으로 확인받는 것이 좋습니다. 기기 검사는 통과했으므로 제품 결정은 바꾸지 않고 기획서·검토 화면에만 이 점을 적었습니다.
3. 버전 고정이 안 되어 있습니다. `joeflow-project.json`이 없어 1.7.0으로 실행됐습니다. 저장소는 1.7.1이고, 1.7.1에는 손으로 쓴 제목의 낡은 revision을 찾는 검사가 들어 있습니다. 버전 고정은 쓰기 작업이라 이번에는 하지 않았습니다.
4. 사소한 불일치: project slug는 `semantic-closure-v2`인데 폴더 이름은 `request-form`입니다.

실행한 명령은 `runs/r1/commands.log`에 한 줄씩(명령, 종료 코드) 남겼습니다.
