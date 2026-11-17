## 요약
rev 2는 승인 준비가 됐습니다. `check_approval.py`가 `ready: true`, `errors: []`를 반환했습니다. 다만 아래 "남은 것" 1번(DEC-002 근거가 약함)을 승인 요청 때 사용자에게 꼭 확인해야 합니다.

## 승인 준비 결과
- **ready:** `true` (`errors: []`, `written: false`)
- **revision:** 2 (READY_FOR_REVIEW / UNAPPROVED)
- **manifest digest:** `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- **definition digest:** `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- Semantic Closure 요약 항목은 모두 0입니다. rev 1에서 rev 2로 추가 7건, 변경·대체·폐기는 0건입니다.
- `approval_status.py`: 마지막 승인은 rev 1이고, rev 2가 승인 대기입니다.
- `record_approval.py --write`는 실행하지 않았습니다. 승인 기록은 없습니다.

## 점검한 것
- 기획서(MASTER_PLANNING_SPEC.md)와 검토 화면(planning-review-core.html)을 state.json과 대조했습니다.
- 매니페스트를 다시 계산했고, 두 문서에 적힌 revision과 두 digest가 모두 일치합니다.
- `projection_check.py`를 돌렸습니다. 처음엔 `ok: false`, 수정 후 `ok: true`입니다.
- `update_projection.py`를 쓰기 없이 돌렸습니다. 자동 생성 블록의 차이는 0줄이라 `--write`는 필요 없었습니다.
- rev 2에 추가된 7개 기록(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)이 두 문서에서 나오는 줄을 읽어 원문과 맞는지 봤습니다. 정본에 없는 정책은 추가되지 않았습니다. 성공/실패 분기도 원래 조건대로 유지됩니다. 정본에 정의되지 않은 것(거부 시 문구, 복구, 제출 뒤 이동)은 "정의되지 않음"으로 맞게 적혀 있습니다.
- 브라우저 창에서 검토 화면을 열어 봤습니다.

## 바꾼 것 (투영 문서 2곳만, state.json은 그대로)
1. **MASTER_PLANNING_SPEC.md 5번째 줄:** `> 승인: revision 1 (`dd1e837b…`)`가 rev 2 문서 머리에서 rev 1이 승인된 것처럼 읽혔습니다(`stale_spec_title_revision`). `> 승인 상태: revision 2 승인 대기 (이전 승인 기록은 아래 Approved identity 블록 참조)`로 고쳤습니다. 이전 승인 정보는 identity 블록에 이미 있습니다.
2. **planning-review-core.html 렌더 검증 줄:** 실제로 본 범위만 적었습니다.
   - 데스크톱 폭(약 1000px)에서 정적 스냅샷으로 렌더를 확인했습니다. 7개 섹션이 보이고, 목차 링크 7개의 대상이 모두 있고, 가로 넘침이 없습니다.
   - 클릭 이동과 모바일 폭은 `NOT_VERIFIED`로 남겼습니다.

## 고치지 않은 지적과 이유
- **DEC-002 / UNK-002의 근거가 약합니다.** UNK-002는 `USER_ACCEPTED_RECOMMENDATION`(BELOW, 항상 표시)로 닫혀 있고 `accepted_by: user`입니다. 그런데 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"뿐입니다. 이 말은 BELOW(항상 표시)와 NEAR_LIMIT(180자부터 표시) 중 하나를 고르지 않았습니다. `accepted_at`도 null입니다.
- 그래도 state.json은 바꾸지 않았습니다.
  - 질문을 다시 열면 rev 3으로 바꾸는 제품 정의 변경이 되고, 지금 매니페스트가 무효가 됩니다.
  - 이것은 사용자가 정할 일이고, 이번 작업 범위(rev 2 승인 준비)를 벗어납니다.
  - 두 문서 모두 이미 "승인 전에 '항상 표시'를 확인해 달라"고 대안과 함께 적고 있습니다.

## 남은 것
1. **승인 요청 때 사용자에게 rev 2 / `6b50eb33…` 매니페스트를 보여 주고, '항상 표시(BELOW)'가 맞는지 따로 물어야 합니다.** 사용자가 NEAR_LIMIT를 원하면 승인하지 말고 `open_revision.py`로 rev 3에서 UNK-002를 다시 열어야 합니다.
2. **실제 승인 기록**은 사용자의 말을 직접 받은 세션이 해야 합니다. 명령은 `record_approval.py STATE --revision 2 --manifest-digest 6b50eb33… --at … --quote "…" --write`입니다. 승인 뒤에는 `update_projection.py --write`와 `projection_check.py`로 문서를 승인 상태로 맞춥니다.
3. **버전 고정이 없습니다.** 스크립트가 "프로젝트가 JOEFLOW 버전을 기록하지 않음(실행 버전 1.7.1)"이라고 알립니다. `joeflow_version.py --pin`을 쓰면 joeflow-project.json이 새로 생기므로 실행하지 않았고, 사용자가 정할 일입니다.
4. **검토 화면의 클릭 이동과 모바일 렌더**는 확인하지 못했습니다(NOT_VERIFIED).

## 참고
- 명령 기록은 `<SCRATCH>\runs\r05\commands.log`에 있습니다.
- 매니페스트 결과를 시스템 임시 폴더(r05 밖)에 저장하려던 명령 하나는 권한 분류기가 막아 실행되지 않았습니다. 그래서 로그에 없습니다. 같은 일은 파일 없이 stdout으로 다시 했습니다.
- r05 밖의 파일은 읽거나 쓰지 않았습니다.

파일:
- <SCRATCH>\runs\r05\project\product-definition\request-form\MASTER_PLANNING_SPEC.md (수정)
- <SCRATCH>\runs\r05\project\product-definition\request-form\planning-review-core.html (수정)
- <SCRATCH>\runs\r05\project\product-definition\request-form\state.json (변경 없음)
