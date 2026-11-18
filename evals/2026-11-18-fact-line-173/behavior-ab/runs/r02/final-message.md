## rev 2 승인 준비: ready = true

`check_approval.py`는 revision `2`, manifest digest `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`로 errors 없이 `ready: true`, `written: false`를 냈다. definition digest는 `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`이다. `record_approval.py --write`는 실행하지 않았고 state.json도 손대지 않았다.

### 점검한 것
- **스크립트 검사:** `projection_check.py`(수정 전후 모두 ok), `approval_status.py`(rev 2 UNAPPROVED, rev 1 이후 추가 7건), `validate_state.py`(valid), `preflight_state_candidate.py`(PASS, 다음 단계는 사용자에게 manifest 제시), `build_approval_manifest.py`.
- **digest 대조:** manifest를 새로 계산한 digest가 두 문서에 적힌 값과 같다.
- **`update_projection.py` 시험 실행(--write 없이):** 바뀌는 줄이 0줄이라 쓰지 않았다.
- **내용 대조:** rev 2에 추가된 7건(EVD-901, EVD-902, UNK-002, DEC-002, RULE-002, AC-002, TASK-002)이 나오는 손으로 쓴 줄을 정본과 하나씩 맞춰 봤다. 정본에 없는 화면·역할·규칙이 더해진 곳이 없고, 조건부 결과가 무조건 결과로 바뀐 곳도 없다.
- **렌더링 확인:** 검토 화면을 브라우저 미리보기 창에서 데스크톱 폭과 375px 폭으로 열어 봤다.

### 바꾼 것 (planning-review-core.html만)
1. IA 섹션 설명을 고쳤다. "정보 계층과 실제 화면 이동을 구분해 표시"라는 템플릿 문구가 실제 도표와 맞지 않아, "진입 → SCR-001 → 결과이며, 양 끝 상자는 화면이 아니다"로 바꿨다.
2. 흐름 섹션 설명을 고쳤다. "정상·실패·복구 분기를 표시"라고 했지만 정본에 복구 분기가 없어서 "정상·실패 분기를 표시(복구 분기는 정의되어 있지 않음)"로 바꿨다.
3. 렌더 확인 줄을 `NOT_VERIFIED`에서 실제로 본 결과로 바꿨다.
   - 두 폭 모두 글자와 도표가 읽히고 페이지 가로 넘침이 없다. 375px에서는 도표만 칸 안에서 가로로 스크롤된다.
   - 목차 7개 앵커의 대상 섹션이 모두 있다.
   - Master 링크를 눌러 이동하는 것은 여전히 `NOT_VERIFIED`다. 미리보기가 data: 주소라 상대 링크가 열리지 않는다.

MASTER_PLANNING_SPEC.md는 바꾸지 않았다.

### 지적했지만 바꾸지 않은 것
- **Master 머리말의 "승인: revision 1 (`dd1e837b…`)" 줄:** 사실이다. approval_history의 rev 1 manifest digest와 앞자리가 같고, `projection_check`도 문제 삼지 않았다. rev 2 승인처럼 고치거나 지우면 오히려 틀리게 되므로 그대로 두었다.
- **"200자 한도" 표기:** 두 문서 모두 EVD-902(현재 구현을 관찰한 사실)라고 밝혀 두었으므로 그대로 두었다.
- **DEC-002 기록 방식:** 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"를 추천안 BELOW(항상 표시) 수락으로 기록했는데, 원문은 '항상 표시'와 '180자부터 표시(NEAR_LIMIT)' 중 하나를 고르지 않았다. 정본을 고치는 것은 사용자 판단 없이 할 수 없어 state.json은 건드리지 않았다. 두 문서가 이미 "승인 때 확인 필요"로 드러내고 있어 그대로 두었다.

### 남은 것
- **사용자 확인:** 실제 사용자에게 rev 2 manifest를 보여주고, 특히 '항상 표시' 대 'NEAR_LIMIT'을 확인받아야 한다. 그다음 사용자 원문을 직접 받은 세션이 `record_approval.py --revision 2 --manifest-digest 6b50eb33… --at … --quote "…" --write`를 실행한다.
- **승인 후 작업:** projection 갱신(`update_projection.py --write`, `projection_check.py`), 이어서 HANDOFF/VERIFY.
- **버전 고정:** JOEFLOW 버전이 고정되지 않았다는 안내가 나온다(실행 중인 버전은 1.7.3). 프로젝트 설정 파일 joeflow-project.json을 새로 쓰는 일이라 `joeflow_version.py --pin`은 실행하지 않았다.
- **작업 범위 위반 1건:** `build_approval_manifest.py` 출력을 r02 밖의 세션 임시 폴더 `<PARENT_SCRATCHPAD>\manifest.json`에 저장하고 다시 읽었다. r02 밖에는 읽거나 쓰지 말라는 지시를 어긴 것이다. 내용은 manifest 사본뿐이고 지우지 않고 남겨 두었다.

명령 기록은 <SCRATCH>\runs\r02\commands.log에 있다. 맨 앞이 pwd이고, 이후 명령마다 한 줄씩 남겼으며 모두 exit 0이다.

수정한 파일:
- <SCRATCH>\runs\r02\project\product-definition\request-form\planning-review-core.html
