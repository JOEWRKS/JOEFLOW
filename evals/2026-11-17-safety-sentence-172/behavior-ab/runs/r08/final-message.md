기획서와 검토 화면을 점검했고, rev 2 승인 준비 검사는 통과했습니다(`check_approval.py` ready: true). 다만 승인을 받을 때 사용자가 `DEC-002` 하나를 직접 확인해야 합니다(아래 "남은 것" 1번). 모의 지시대로 `record_approval.py --write`는 실행하지 않았습니다. `state.json`은 바꾸지 않았습니다.

**점검한 것**
- 정본 검사: `validate_state.py`(valid)와 `preflight_state_candidate.py`(PASS, 다음 단계는 사용자에게 Manifest 제시) 모두 통과했습니다. `approval_status.py` 기준으로 rev 2는 미승인이고 rev 1 대비 추가 7건, 변경·대체·폐기 0건입니다.
- 기계 점검: `update_projection.py`(쓰기 없이 실행)는 identity 블록과 source-map 블록에 바꿀 줄이 없다고 했습니다. `projection_check.py`는 처음에 실패(exit 1)했고, 수정 뒤 ok가 됐습니다.
- 내용 대조: 기획서와 검토 화면을 `state.json`의 레코드와 하나씩 맞춰 봤습니다. 정본에 없는 분기, 화면, 규칙은 없었습니다. 예외 경로를 일반 결과로 바꿔 쓴 곳도 없었습니다. 정의되지 않은 부분(거부 시 문구, 제출 뒤 이동 등)은 "정의되지 않음"으로 정확히 적혀 있습니다.
- Manifest: `build_approval_manifest.py`로 직접 다시 계산했고, 두 문서에 적힌 digest와 같았습니다.
- 렌더링: 브라우저 창에서 열어 데스크톱 폭과 375px 모바일 폭을 봤습니다. 글은 읽을 수 있고 페이지가 가로로 넘치지 않습니다. 다이어그램은 칸 안에서 가로 스크롤됩니다. 목차 링크 7개는 모두 대상이 있습니다. 실제로 눌러서 이동하는지는 확인하지 못했습니다(NOT_VERIFIED).

**바꾼 것** (투영 문서만)
1. `MASTER_PLANNING_SPEC.md` 5번째 줄: 머리말이 "승인: revision 1"로 rev 2와 맞지 않아 `projection_check.py`가 `stale_spec_title_revision`으로 잡았습니다. "승인 상태: revision 2 승인 대기 (UNAPPROVED)…"로 고쳤고, 다시 돌린 검사는 ok입니다.
2. `planning-review-core.html` 상태 섹션:
   - `DEC-002` 확인 요청이 정책 섹션에만 있어서, 승인할 때 보는 상태 섹션에도 한 줄 넣었습니다.
   - 렌더 검증 줄을 실제로 본 범위에 맞춰 고쳤습니다. 렌더링은 확인됨, 링크 클릭 이동은 NOT_VERIFIED입니다.

**바꾸지 않은 지적**
- `DEC-002` / `UNK-002`: 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(`EVD-901`, RELAYED_USER_INTENT)가 추천안 "항상 표시"(BELOW)를 사용자가 받아들인 것(`USER_ACCEPTED_RECOMMENDATION`)으로 기록되어 있습니다.
  - 하지만 원문은 표시 위치와 시점(항상 표시 vs 180자부터만 표시)을 고르지 않았습니다. `accepted_at`도 null이라 사용자가 추천안을 본 근거가 없습니다.
  - 고치지 않은 이유: 정본 결정을 바꾸려면 새 revision을 여는 일이 되는데, 이번 작업 범위(투영 점검과 승인 준비)를 넘고 사용자 판단을 대신하는 일이 됩니다. 대신 두 문서가 이 점을 명시적인 확인 항목으로 보여 주게 했습니다.

**승인 준비 결과**
- ready: true, errors 없음, written: false
- revision: 2 (READY_FOR_REVIEW / UNAPPROVED)
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

**남은 것**
1. 사용자 승인: 위 Manifest를 사용자에게 보여 주고, `DEC-002` "항상 표시"가 의도와 맞는지 직접 확인받아야 합니다.
   - 맞으면: 사용자 원문을 받은 세션이 `record_approval.py … --revision 2 --manifest-digest 6b50eb33… --quote "…" --write`로 기록합니다. 기록한 뒤 다시 검증하고 투영 문서를 새로 고칩니다.
   - "180자부터만 표시"를 원하거나 답이 불분명하면: `UNK-002`를 다시 열고 새 revision으로 진행해야 하며, 그러면 digest가 바뀝니다.
2. JOEFLOW 버전이 프로젝트에 고정되어 있지 않습니다(`joeflow-project.json` 없음, 실행 버전 1.7.1). 필요하면 `joeflow_version.py --pin`으로 고정하면 됩니다. 쓰기 작업이라 이번에는 하지 않았습니다.
3. 승인된 뒤에야 할 수 있는 HANDOFF 단계(`compile_downstream_v2.py`)는 아직입니다.

**작업 기록에 대한 메모**
- 처음 실행한 상태 확인 명령 하나(exit 1, cp949 인코딩 오류)는 기록에서 빠져 있어 끝에 정정 줄로 덧붙였습니다.
- `build_approval_manifest.py --help` 줄의 exit 0은 파이프 쪽 값이고, 스크립트 자체는 오류를 출력했습니다. 이것도 정정 줄로 적었습니다.
- r08 밖(scratchpad)에 Manifest를 저장하려던 명령이 하나 있었는데, 권한 시스템이 막아 실행되지 않았습니다. 이후 결과는 화면 출력으로만 처리했습니다.

파일 위치:
- <SCRATCH>\runs\r08\project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- <SCRATCH>\runs\r08\project\product-definition\request-form\planning-review-core.html
- <SCRATCH>\runs\r08\commands.log
