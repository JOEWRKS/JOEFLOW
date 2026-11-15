## 결과
rev 2 승인 준비 점검을 통과했습니다(`ready: true`). revision 2, Approval Manifest digest `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`, definition digest `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`. 승인은 모의라서 `record_approval.py --write`는 실행하지 않았습니다. state는 READY_FOR_REVIEW / UNAPPROVED 그대로이고, 마지막 승인은 rev 1입니다.

다만 승인 전에 사용자가 직접 확인해야 할 것이 하나 있습니다(아래 "바꾸지 않은 지적").

## 점검한 것
- **정본 상태**: `validate_state.py`는 valid, 오류 0개. `preflight_state_candidate.py`는 모든 단계 PASS이고 다음 행동은 "정확한 Manifest를 사용자에게 보여 줄 것"입니다. `approval_status.py` 기준 rev 1 이후 대기 중인 변경은 추가 7건입니다. `build_approval_manifest.py`로 다시 계산한 digest가 두 문서에 적힌 값과 같습니다.
- **투영 검사**: `projection_check.py`가 처음엔 `ok: false`였습니다. 원인은 기획서 5행의 `stale_spec_title_revision` 하나였습니다. 빠진 추가 레코드, 오래된 식별 정보, 대체되거나 폐기된 레코드를 아직 언급하는 곳은 없었습니다.
- **식별 블록**: `update_projection.py`를 `--write` 없이 돌려 보니 바꿀 내용이 없었습니다(diff 0줄).
- **내용 대조**: 수기로 쓴 줄 중 새로 추가된 레코드(EVD-901/902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)를 언급하는 줄을 정본과 직접 맞춰 봤습니다. 조건부 분기를 무조건으로 바꾼 곳이나 정본에 없는 동작은 없습니다. 정의되지 않은 항목(거부 문구, 복구, 제출 뒤 이동)도 두 문서 모두 "정의되지 않음"으로 남겨 두었습니다.
- **화면 렌더링**: 검토 화면을 브라우저 창에서 열어 봤지만 로컬 파일은 화면을 캡처하거나 읽을 수 없었습니다. 그래서 HTML에 적힌 `NOT_VERIFIED`를 그대로 두었습니다.

## 바꾼 것
- `<SCRATCH>\r09\project\product-definition\request-form\MASTER_PLANNING_SPEC.md` 5행만 고쳤습니다.
  - 전: `> 승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)`
  - 후: `> revision 2(승인 대기) 기준으로 작성됨. 마지막 승인은 revision 1.`
  - 이유: 문서는 실제로 rev 2 내용인데 "rev 1 기준"이라고 적혀 있어 사실과 달랐습니다. 고친 뒤 `projection_check.py`가 `ok: true`입니다.
- `planning-review-core.html`과 `state.json`은 바꾸지 않았습니다.

## 바꾸지 않은 지적
- **DEC-002 근거 문제(정본 레코드)**:
  - DEC-002와 UNK-002는 "사용자가 추천안 BELOW(항상 표시)를 받아들였다"로 기록되어 있습니다. 하지만 근거 EVD-901은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"뿐입니다. 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이었습니다.
  - 사용자가 BELOW와 NEAR_LIMIT(180자부터만 표시) 두 안을 보고 고른 증거는 없습니다. 그래서 "사용자 결정"이라는 기록은 근거가 약합니다.
  - 정본은 고치지 않았습니다. 고치려면 새 revision을 열고 UNK-002를 다시 OPEN으로 되돌려야 하는데, 이는 사용자 없이 할 수 없는 제품 판단이고 이번 작업 범위(투영 점검·승인 준비)도 넘습니다.
  - 대신 두 문서가 이미 "승인 전에 '항상 표시'가 의도와 맞는지 확인"을 눈에 띄게 적어 두었으므로 그대로 두었습니다.
- **기획서의 "Approved identity" 제목**: rev 2가 아직 승인 전이라 어색하지만, 템플릿이 정한 섹션 이름이고 바로 아래 내용이 "승인 대기"라고 밝히므로 두었습니다.

## 남은 것
1. 사용자에게 Manifest(rev 2, `6b50eb33…2906`)를 보여 주고 명시적인 승인을 받아야 합니다. 이때 DEC-002의 '항상 표시(BELOW)'와 '180자부터 표시(NEAR_LIMIT)' 중 무엇을 원하는지 확인해야 합니다.
   - BELOW로 승인하면: 사용자 원문을 받은 세션에서 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33…2906 --at <UTC> --quote "<원문>" --write`를 실행합니다. 그 다음 `update_projection.py --write`와 `projection_check.py`를 다시 돌립니다.
   - NEAR_LIMIT를 고르면: rev 3을 열어 DEC-002, RULE-002, AC-002를 바꿔야 하고, digest가 달라집니다.
2. 검토 화면의 렌더링은 아직 확인하지 못했습니다(`NOT_VERIFIED`).
3. 프로젝트에 JOEFLOW 버전이 기록되어 있지 않습니다(현재 1.7.2로 실행). `joeflow_version.py --pin`은 설정 파일을 새로 쓰는 일이라 하지 않았습니다.
4. 이 폴더는 git 저장소가 아닙니다. `git status`가 exit 128로 실패해 그대로 로그에 남겼습니다.

명령 기록은 `<SCRATCH>\r09\commands.log`에 있습니다(`pwd`부터 마지막 명령까지 한 줄씩, 종료 코드 포함).
