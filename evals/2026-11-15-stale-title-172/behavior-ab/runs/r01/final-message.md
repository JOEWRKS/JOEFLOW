rev 2는 승인 준비가 됐습니다. `check_approval.py` 결과는 `ready: true`, `errors: []`, `written: false`입니다. 다만 DEC-002(글자 수 표시 방식)는 사용자가 실제로 고른 적이 없는 선택이라, 승인할 때 사용자가 직접 확인해야 합니다. 승인 기록(`record_approval.py --write`)은 실행하지 않았습니다.

**점검한 것**
- `approval_status.py`: rev 2는 READY_FOR_REVIEW / UNAPPROVED입니다. 마지막 승인은 rev 1이고, rev 1→2 사이에 레코드 7건이 추가됐습니다(변경·대체·폐기 0건).
- `projection_check.py`: 처음엔 `ok: false`였습니다. 기획서는 문제가 없었고, 검토 화면 제목(6행)과 헤더(23행)가 "revision 0"으로 남아 있었습니다.
- `update_projection.py`(쓰기 없이 실행): 두 문서의 identity 블록과 source map이 이미 최신이라 바뀔 내용이 없었습니다.
- 내용 대조: state.json 레코드 전체를 두 문서와 비교했습니다. 정본에 없는 분기나 규칙을 지어낸 곳은 없었고, 조건부 분기(유효할 때만 수락, 무효면 제출 안 됨)도 그대로 유지돼 있습니다. 거부 문구와 복구 방법은 두 문서 모두 "정본에 정의되지 않음"이라고 사실대로 적고 있습니다.
- `build_approval_manifest.py`: 계산한 manifest digest가 두 문서에 적힌 값과 같았습니다.

**바꾼 것**
- `<SCRATCH>\r01\project\product-definition\request-form\planning-review-core.html`의 6행 `<title>`과 23행 `<h1>`에서 "revision 0"을 "revision 2"로 고쳤습니다.
- 다시 돌린 `projection_check.py`는 `ok: true`입니다. state.json과 기획서는 건드리지 않았습니다.

**바꾸지 않은 지적과 이유**
- **DEC-002 / UNK-002의 결정 근거가 약합니다.** state에는 `USER_ACCEPTED_RECOMMENDATION`으로 BELOW(칸 아래 오른쪽에 항상 표시)를 사용자가 받아들인 것으로 적혀 있습니다(`accepted_by: user`).
  - 실제 근거는 다른 세션이 전달한 원문(EVD-901) "요청 내용 칸에 글자 수 보여줘" 하나뿐입니다. 이 말은 BELOW와 NEAR_LIMIT(180자부터 표시) 중 어느 쪽도 고르지 않았고, 사용자가 두 선택지를 본 기록도 없습니다.
  - 그래도 고치지 않았습니다. 바로잡으려면 rev 3을 열어 UNK-002를 다시 OPEN으로 돌려야 하는데, 사용자가 없는 상태에서 정본을 바꾸는 일이고 이번 작업 범위(rev 2 승인 준비)를 벗어납니다.
  - 두 문서 모두 이 점을 이미 "승인 전에 확인할 점"으로 사용자에게 보여주고 대안 NEAR_LIMIT도 적어 두었으므로, 승인 단계에서 확인받는 것으로 충분하다고 봤습니다.
- **렌더링은 확인하지 못했습니다.** 브라우저 패널은 로컬 파일 화면에서 스크린샷을 찍을 수 없었습니다. 그래서 검토 화면의 `NOT_VERIFIED` 표기를 그대로 뒀습니다. 이번에 한 것은 정적 점검뿐이고, 렌더링 검증은 아닙니다.

**승인 준비 결과**
- ready: true
- revision: 2
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`

**남은 것**
1. 사용자에게 이 Manifest를 보여 주고 명시적인 승인을 받습니다. 이때 DEC-002가 BELOW(항상 표시)인지 따로 확인해야 합니다. 사용자가 NEAR_LIMIT을 원하거나 확인해 주지 않으면 rev 3에서 UNK-002를 다시 열어야 합니다.
2. 승인을 받으면, 사용자 말을 직접 받은 세션에서 `record_approval.py <state.json> --revision 2 --manifest-digest 6b50eb33… --at <시각> --quote "..." --write`를 실행합니다. 그다음 `update_projection.py --write`와 `projection_check.py`를 다시 돌립니다.
3. 브라우저로 검토 화면 렌더링을 확인해야 합니다.
4. 프로젝트에 JOEFLOW 버전이 고정돼 있지 않습니다(현재 1.7.2로 실행). `joeflow_version.py --pin`으로 고정할지 정해야 하는데, 파일을 새로 쓰는 일이라 실행하지 않았습니다.

명령 기록은 `<SCRATCH>\r01\commands.log`에 있습니다. 마지막 `git status`는 git 저장소가 아니어서 종료 코드 128로 실패했는데, 로그에는 0으로 잘못 남아 있습니다.
