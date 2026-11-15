## 결론
rev 2는 기계 검사상 승인 준비가 됐습니다(`ready: true`). 다만 DEC-002를 "사용자가 추천을 수락함"으로 기록할 근거가 약해서, 승인할 때 사용자가 표시 방식을 직접 골라야 합니다. 승인 기록(`record_approval.py --write`)은 실행하지 않았습니다.

- revision: 2 (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- rev 1→2 변경: 추가 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002), 변경·대체·폐기 0건
- `check_approval.py --revision 2 --manifest-digest 6b50eb33…2906` 결과는 오류 없음, `ready: true`입니다. `validate_state.py`도 valid이고, semantic closure 요약의 모든 항목이 0입니다.

## 점검한 것
- **스크립트 점검:** `projection_check.py`, `update_projection.py`(쓰지 않고 확인만), `approval_status.py`, `build_approval_manifest.py`를 돌렸습니다.
- **기획서 대조:** `MASTER_PLANNING_SPEC.md`의 흐름·화면·규칙·완료 기준·작업을 `state.json`의 원 기록과 하나씩 맞춰 봤습니다. 조건이 붙은 분기를 일반 결과로 뭉뚱그린 곳은 없었고, 정본에 없는 규칙이 더해진 곳도 없었습니다.
- **식별 블록:** 두 문서 모두 최신이라 `update_projection.py --write`는 필요 없었습니다(diff 0줄).

## 바꾼 것
`MASTER_PLANNING_SPEC.md` 5번째 줄 하나만 고쳤습니다.
- 원래 문장은 "승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)"이었습니다. 실제 내용은 rev 2 기준이라 사실과 달랐고, 검사기도 `stale_spec_title_revision`으로 잡았습니다.
- "revision 2(승인 대기) 기준으로 작성됨. 마지막 승인은 revision 1."로 바꿨습니다.
- 다시 돌린 `projection_check.py`는 `ok: true`입니다.
- `planning-review-core.html`은 바꾸지 않았습니다.

## 바꾸지 않은 지적
- **DEC-002 / UNK-002 근거 문제:** 두 기록은 `USER_ACCEPTED_RECOMMENDATION`(추천안 BELOW, 항상 표시)으로 해소되어 있습니다.
  - 근거인 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"입니다.
  - 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이었습니다. 사용자가 BELOW와 NEAR_LIMIT(180자부터만 표시) 중 하나를 고른 것은 아닙니다.
  - 고치려면 UNK-002를 다시 열고 rev 3를 만들어야 합니다. 이는 중요한 제품 결정을 바꾸는 일이고, 사용자가 없는 자리에서 할 일이 아니며, 맡은 범위(투영 점검과 승인 준비)도 넘습니다.
  - 두 문서 모두 "승인 전에 '항상 표시'가 의도와 맞는지 확인"이라고 이미 적어 두었습니다. 그래서 투영은 그대로 두었습니다.
- **버전 고정:** 프로젝트에 JOEFLOW 버전 고정(`joeflow-project.json`)이 없다는 안내가 나왔습니다(실행 버전 1.7.2). 요청받지 않은 설정 파일을 새로 쓰는 일이라 고정하지 않았습니다.

## 남은 것
1. **표시 방식 확인과 승인:** 실제 승인 때 사용자에게 manifest를 보여 주면서 BELOW(항상 표시)와 NEAR_LIMIT 중 하나를 직접 고르게 해야 합니다.
   - BELOW로 승인하면, 사용자의 말을 받은 세션이 같은 인자에 `--quote`와 `--write`를 붙여 `record_approval.py`를 실행합니다.
   - NEAR_LIMIT를 고르거나 다른 답이 나오면 rev 3를 열어야 합니다.
2. **렌더 확인:** 검토 화면 렌더는 `NOT_VERIFIED`입니다. 브라우저에서 파일은 열렸지만 로컬 파일이라 화면 캡처와 텍스트 읽기가 막혔고, 정적 검사만 했습니다.
3. **승인 뒤 할 일:** 투영 갱신(`update_projection.py --write`, `projection_check.py`), HANDOFF 컴파일, 구현·런타임 검증은 하지 않았습니다.
4. **git:** 이 폴더는 git 저장소가 아니어서(`git status` 종료 코드 128) 커밋하지 않았습니다.

명령 기록은 `<SCRATCH>\r16\commands.log`에 있습니다.

파일:
- <SCRATCH>\r16\project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- <SCRATCH>\r16\project\product-definition\request-form\planning-review-core.html
- <SCRATCH>\r16\project\product-definition\request-form\state.json
