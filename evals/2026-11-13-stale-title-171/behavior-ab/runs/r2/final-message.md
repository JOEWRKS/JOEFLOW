rev 2는 모의 승인 준비가 끝났습니다. check_approval.py 결과는 `ready: true`, `errors: []`이고, 승인 기록(`record_approval.py --write`)은 하지 않았습니다.

**점검 결과**
- `validate_state.py`: valid, 오류 0.
- `approval_status.py`: rev 2는 READY_FOR_REVIEW / UNAPPROVED입니다. 마지막 승인은 rev 1이고, rev 1→2 변경은 추가 7건, 변경·대체·폐기 0건입니다.
- `build_approval_manifest.py`: Semantic Closure 요약의 모든 항목이 0입니다.
- `projection_check.py`(처음 실행): `ok: false`, 종료 코드 1. 검토 화면의 `<title>`(6행)과 헤더 `<h1>`(22행)이 `revision 0`으로 남아 있었습니다(`stale_review_title_revision`).
- 두 투영 문서는 identity 블록만 맞았고, 본문은 거의 채워지지 않은 템플릿이었습니다.
  - HTML에는 `{{PRODUCT_SCOPE_SUMMARY}}` 등 자리표시자가 남아 있었습니다.
  - Master는 §1~9가 템플릿 설명문 그대로였고, 레코드 표는 내용이 모두 `text`였습니다.
  - 이 상태로는 사용자가 볼 검토 화면이 성립하지 않는다고 판단했습니다.

**바꾼 것** (state.json은 고치지 않았습니다)
- `planning-review-core.html`
  - 제목과 헤더를 revision 2로 고치고, 상태 줄을 READY_FOR_REVIEW · UNAPPROVED(승인 대기)로 바꿨습니다.
  - 범위, IA(화면 1개 SVG), FLOW-001, SCR-001 카드, RULE-001/002 정책을 state.json 내용만으로 채웠고 rev 2 추가분을 표시했습니다.
  - "승인 전에 확인할 점"을 넣었습니다.
  - 렌더 검증은 `NOT_VERIFIED`로 적었습니다. 브라우저 패널에 로컬 파일이 정적 스냅샷으로만 열려 화면을 관찰하지 못했습니다.
- `MASTER_PLANNING_SPEC.md`
  - §1~9와 레코드 표를 정본 내용으로 다시 썼습니다. 자동 생성 블록(IDENTITY, SOURCE-MAP)은 그대로 두었습니다.
  - 정본에 없는 내용(거부 시 문구·복구, 제출 후 이동, 반응형·접근성)은 지어내지 않고 "정의되어 있지 않음"으로 적었습니다.
  - 원본은 `runs/r2/MASTER_PLANNING_SPEC.orig.md`에 백업했습니다.
- 다시 실행한 결과: `update_projection.py`는 diff 0이라 `--write`가 필요 없었고, `projection_check.py`는 `ok: true`였습니다.

**승인 준비 결과** (`check_approval.py`)
- ready: true (errors 없음)
- revision: 2
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- `validate_closure.py`는 종료 코드 1, `closed: false`입니다. 오류는 없고 `missing_or_stale_approval_manifest: 1`만 남았는데, 아직 승인 전이라 예상된 결과입니다.

**남은 것**
1. 사용자가 위 Manifest를 직접 승인해야 합니다. 승인을 받은 세션에서 `record_approval.py state.json --revision 2 --manifest-digest 6b50eb33… --at … --quote "…" --write`를 실행해야 하며, 이번에는 모의라 실행하지 않았습니다.
2. 승인 때 사용자가 꼭 확인해야 할 점이 하나 있습니다.
   - DEC-002는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(EVD-901, RELAYED_USER_INTENT)를 추천안 BELOW(항상 표시) 수락으로 기록했습니다.
   - 원문은 글자 수를 보여 달라는 말일 뿐, 위치나 표시 시점(항상 vs 180자부터)을 고르지 않았습니다.
   - 검증기는 통과했지만 이것을 '추천 수락'으로 본 근거는 약합니다. 그래서 검토 화면과 Master §9에 확인 항목으로 표시했습니다.
3. 검토 화면 렌더 확인은 NOT_VERIFIED입니다. 실제 브라우저에서 열어 확인해야 합니다.
4. 프로젝트에 버전 고정(pin)이 없습니다(`joeflow_version.py --pin` 안내). 버전 고정은 승인 준비 범위 밖이라 하지 않았습니다.

실행한 명령은 모두 종료 코드와 함께 `runs/r2/commands.log`에 남겼습니다. r2 밖의 파일은 수정하지 않았습니다.
