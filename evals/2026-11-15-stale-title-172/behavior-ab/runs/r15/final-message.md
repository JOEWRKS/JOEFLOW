## 결과: rev 2 승인 준비 완료 (ready = true). 승인은 기록하지 않았다.

- revision: `2` (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- rev 1→2 변경: 추가 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002), 변경·대체·폐기는 0건
- `record_approval.py --write`는 실행하지 않았다.

## 점검한 것
- **스크립트 점검:**
  - `validate_state.py` valid
  - `build_approval_manifest.py` 차단 지표 전부 0
  - `preflight_state_candidate.py` PASS
  - `approval_status.py`, `update_projection.py`(쓰기 없이 실행) 결과 identity 블록과 source map에 바뀔 것이 없었다.
  - `projection_check.py`는 처음에 실패(exit 1)했고, 수정 후 ok(exit 0)가 됐다.
- **내용 대조:** 새로 추가된 7개 레코드의 문구를 기획서·검토 화면의 해당 줄과 하나씩 맞춰 봤다. 위치(칸 아래 오른쪽), 형식('현재 / 200', 빈 칸은 '0 / 200'), 갱신 시점(넣거나 지울 때 즉시), 200자 한도가 구현 관찰(EVD-902)이라는 점이 모두 맞다.
  - 조건부 결과를 모든 경우에 해당하는 것처럼 바꿔 쓴 곳은 없다.
  - 정의되지 않은 항목(거부 문구, 복구, 제출 후 이동)은 두 문서 모두 "정의되지 않음"으로 남겨 두었다.

## 바꾼 것
- `<SCRATCH>\r15\project\product-definition\request-form\MASTER_PLANNING_SPEC.md` 5번째 줄 하나.
  - 기존 문구 "승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)"은 현재 rev 2와 맞지 않았고, `projection_check.py`가 `stale_spec_title_revision`으로 잡았다.
  - "revision 2 기준으로 작성됨 (승인 대기 · 이전 승인은 아래 Approved identity 참고)"로 고쳤다.
  - 첫 수정안에 "revision 1"이라는 말이 남아 있어서 다시 걸렸고, 두 번째 수정 후 통과했다.
- `state.json`과 `planning-review-core.html`은 바꾸지 않았다.

## 바꾸지 않은 지적과 그 이유
1. **UNK-002 / DEC-002의 출처 문제 (승인 때 사용자 확인 필요).**
   - 상태 파일에는 UNK-002가 `USER_ACCEPTED_RECOMMENDATION`(추천안 BELOW, 항상 표시)으로 해소되어 있다.
   - 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(RELAYED_USER_INTENT)이고, 이 말은 BELOW(항상 표시)와 NEAR_LIMIT(180자부터만 표시) 중 어느 쪽도 고르지 않았다.
   - 또 DEC-002의 `evidence_refs`에는 EVD-901이 없고 EVD-902만 있다.
   - 이 문제를 고치려면 새 revision을 여는 정본 변경이 필요한데, 사용자 판단 없이 하지 않았다.
   - 두 문서 모두 이미 "승인 전에 확인할 점"으로 이 내용을 드러내고 있어서, 사용자가 검토 화면을 보고 '항상 표시'를 확인하는 것이 맞는 경로라고 판단했다.
   - 사용자가 NEAR_LIMIT를 고르면 승인하지 말고 새 revision으로 다시 열어야 한다.
2. **화면 렌더링은 확인하지 못했다(`NOT_VERIFIED`).** 브라우저 창에서 로컬 HTML을 열 수는 있었지만 스크린샷과 페이지 조작이 막혀 렌더를 관찰하지 못했다. 그래서 검토 화면의 `Render verification: NOT_VERIFIED` 표기를 그대로 두었다.
3. **기획서 §6의 "데이터 변경 없음(표시만)".** 정본에 직접 적힌 문구는 아니지만 새 분기나 규칙을 더하지 않는 설명이라 그대로 두었다.

## 남은 것
- 사용자에게 rev 2 Manifest(위 digest)와 검토 화면을 보여 주고, 특히 DEC-002의 '항상 표시'를 확인받은 뒤 명시적 승인을 받아야 한다.
- 승인되면 그 말을 직접 받은 세션에서 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33… --at <UTC> --quote "..." --write`를 실행해야 한다(이번 작업에서는 금지라 실행하지 않았다).
- 이 프로젝트에는 사용 중인 JOEFLOW 버전이 고정되어 있지 않다(실행 버전 1.7.1). `joeflow_version.py --pin`은 파일을 쓰는 작업이라 실행하지 않았다.
- 승인 후에는 `update_projection.py --write`와 `projection_check.py`를 다시 돌려 승인 상태를 문서에 반영해야 한다.
- 이 폴더는 git 저장소가 아니어서 커밋하지 않았다.
- 실행한 명령은 모두 `<SCRATCH>\r15\commands.log`에 기록했다(git status는 exit 128).
