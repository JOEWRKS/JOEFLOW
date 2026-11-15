## 결과 보고 (JOEFLOW rev 2 투영 점검과 승인 준비)

**결론:** rev 2는 승인 준비가 끝났습니다(`ready: true`). 검토 화면에서 고칠 곳 두 군데를 고쳤습니다. 다만 승인할 때 사용자가 꼭 확인해야 할 판단 하나(`DEC-002`)가 남아 있습니다. 승인 기록(`record_approval.py --write`)은 지시대로 실행하지 않았습니다.

### 점검한 것
- **state.json:** `validate_state.py`는 오류 없이 통과했습니다. `approval_status.py` 결과 rev 2는 미승인이고, rev 1과 비교해 추가된 레코드가 7건, 변경·대체·폐기는 0건입니다.
- **두 투영 문서의 식별 정보:** `projection_check.py`가 문제 없음을 보고했습니다(식별 정보 낡음 없음, 추가 레코드 누락 없음). `update_projection.py`를 쓰기 없이 실행해 보니 바뀔 줄이 0줄이었습니다.
- **투영 문서 내용:** 기획서와 검토 화면의 문장을 state.json 레코드와 하나씩 대조했습니다(`GOAL/USR/REQ/RULE-001·002/FLOW/SCR/STATE/DATA/INT/AC-001·002/TASK`, `UNK-002`의 선택지). 정본에 없는 분기나 정책을 더한 곳은 없었습니다. 정의되지 않은 부분(거부 시 문구, 복구, 제출 후 이동)도 "정의되지 않음"으로 맞게 적혀 있었습니다.
- **승인 Manifest:** `build_approval_manifest.py`로 다시 계산한 manifest digest가 두 문서에 적힌 값과 같았습니다. 이전 승인 rev 1 `dd1e837b…`도 `approval_history`와 같았습니다.
- **검토 화면을 실제로 열어 확인:** `127.0.0.1:8765`에 임시 로컬 서버를 띄워 내장 브라우저로 1000px 폭과 375px 폭에서 열어 봤고, 확인 후 서버는 종료했습니다.
  - 글자, IA 다이어그램, 흐름, 정책 구역이 보였습니다.
  - 내부 링크 7개가 모두 제자리로 이동했습니다.
  - 가로 넘침이나 잘림은 없었습니다. 375px에서는 다이어그램만 가로로 스크롤됩니다.
  - 모든 구역을 화면 캡처로 본 것은 아닙니다. 일부는 DOM 측정으로만 확인했습니다.

### 바꾼 것 (`project/product-definition/request-form/planning-review-core.html`만)
1. `<title>`과 `<h1>`에 "revision 0"이라고 잘못 적혀 있어 "revision 2"로 고쳤습니다.
2. 상단 메뉴 링크를 누르면 구역 제목이 고정 메뉴 밑에 가려져서, 각 구역에 `scroll-margin-top:64px`를 넣었습니다. 고친 뒤 제목이 메뉴 아래쪽에 보이는 것을 확인했습니다.
3. 렌더 확인 줄의 `NOT_VERIFIED`를 실제로 관찰한 범위로 바꿨습니다. 날짜, 화면 폭, 캡처로 보지 않은 부분이 있다는 점을 함께 적었습니다.

`MASTER_PLANNING_SPEC.md`와 `state.json`은 바꾸지 않았습니다.

### 바꾸지 않은 지적과 그 이유
- **`DEC-002`가 사용자 결정으로 기록되어 있는 점:** `DEC-002`는 `USER_ACCEPTED_RECOMMENDATION`이고 `accepted_by: user`로 적혀 있습니다. 근거는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"(`EVD-901`, `RELAYED_USER_INTENT`)뿐입니다. 이 원문은 BELOW(항상 표시)와 NEAR_LIMIT(180자부터 표시) 중 어느 쪽도 고르지 않았으니, 추천안 수락으로 보기는 근거가 부족합니다.
  - 이것을 고치려면 state를 실제로 바꿔야 합니다(새 revision, 질문을 OPEN으로 되돌리기). 사용자가 없는 상황에서 제가 결정할 일이 아니라고 봐서 그대로 두었습니다.
  - 두 투영 문서에는 이미 "승인 전에 '항상 표시'를 확인해 달라"는 안내가 들어 있어서 내용은 손대지 않았습니다.
- **JOEFLOW 버전 미기록:** 프로젝트에 사용하는 JOEFLOW 버전이 기록되어 있지 않다는 안내가 나왔습니다(현재 실행 버전 1.7.0). `joeflow_version.py --pin`을 실행하면 새 파일 `joeflow-project.json`이 생기는데, 이번 작업 범위 밖이라 실행하지 않았습니다.

### 승인 준비 결과 (`check_approval.py`)
- `ready: true`, `errors: []`, `written: false`
- revision: **2**
- manifest digest: **`6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`**
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`

### 남은 것
- **사용자의 직접 승인:** 사용자가 위 Manifest(rev 2, `6b50eb33…`)를 보고 직접 승인해야 합니다. 이때 `DEC-002`의 "항상 표시"가 맞는지 함께 확인받아야 합니다. NEAR_LIMIT를 고르면 rev 3을 새로 열어야 합니다.
- **승인 기록:** 승인은 사용자의 말을 직접 받은 세션에서 `record_approval.py ... --quote "..." --write`로 기록합니다.
- **승인 후 작업:** 기록한 뒤에는 `update_projection.py --write`와 `projection_check.py`를 다시 실행하고(승인 상태 표기 갱신), HANDOFF 단계로 넘어갑니다.
- **JOEFLOW 버전 고정:** 원하면 별도로 진행합니다.

### 작업 기록 관련
- `<SCRATCH>\r02\commands.log`에 첫 줄로 `pwd` 결과를, 이어서 실행한 명령과 종료 코드를 남겼습니다.
- 처음의 조회용 명령(ls, cat, python -c 조회 등)은 실행할 때 바로 적지 못해서 로그 끝에 "사후 추가"라고 표시하고 덧붙였습니다.
- 맨 처음 명령에서 실수로 r02 밖 임시 파일 `/tmp/p.txt`를 하나 만들었습니다. 그 파일에는 `pwd` 결과만 있었고, 바로 삭제했습니다.
- r02는 git 저장소가 아니어서 `git status`는 종료 코드 128로 실패했고, 그 외 영향은 없습니다.
