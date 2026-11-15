rev 2 승인 준비는 기계적으로 통과했습니다. `check_approval.py`는 ready: true, errors 없음입니다. 다만 사용자가 실제로 승인할 때 `DEC-002`의 '항상 표시'(BELOW)를 직접 확인받아야 합니다. 승인은 기록하지 않았습니다(record_approval.py --write 미실행).

**승인 준비 결과**
- ready: **true**
- revision: **2** (READY_FOR_REVIEW / UNAPPROVED, 마지막 승인은 rev 1)
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- 두 문서에 적힌 manifest digest는 `build_approval_manifest.py`로 다시 계산한 값과 같습니다.

**점검한 것**
- `approval_status.py`: rev 1 이후 대기 중인 것은 rev 2 하나이고, 추가 7건, 변경·대체·폐기 0건입니다.
- `projection_check.py`: 고치기 전과 후 모두 ok입니다. 빠진 추가 레코드, 낡은 식별 정보, 폐기된 레코드 언급이 없습니다.
- `update_projection.py`는 `--write` 없이만 돌렸습니다. 자동 블록(식별 정보, 소스 맵)은 바꿀 것이 없었습니다.
- 손으로 쓴 부분은 rev 2에 추가된 7건(`EVD-901`, `EVD-902`, `UNK-002`, `DEC-002`, `RULE-002`, `AC-002`, `TASK-002`)을 state.json 원문과 대조했고 의미가 맞습니다.
- 흐름의 정상·실패 분기도 원래 조건대로 남아 있습니다. 유효하지 않은 요청이 제출되지 않는다는 건 `RULE-001`의 조건으로 쓰여 있고, 정본에 없는 문구와 복구 방법은 "정의되지 않음"으로 적혀 있습니다.

**바꾼 것**
- `<SCRATCH>\r03\project\product-definition\request-form\planning-review-core.html`: `<title>`과 `<h1>`에 "revision 0"이라고 남아 있던 것을 "revision 2"로 고쳤습니다. 식별 블록 밖이라 `projection_check.py`가 잡지 못하는 결함이었습니다.
- state.json과 MASTER_PLANNING_SPEC.md는 바꾸지 않았습니다.

**바꾸지 않은 지적: `DEC-002`의 근거**
- 무엇이 문제인가: `UNK-002`가 USER_ACCEPTED_RECOMMENDATION(`accepted_by: user`)으로 닫혀 있습니다. 그런데 근거인 `EVD-901`은 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘"입니다. 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"라는 다른 질문에 대한 답이고, BELOW와 NEAR_LIMIT 중 하나를 고르지 않았습니다.
- 그래서 사용자가 추천을 받아들였다는 기록은 근거가 약합니다.
- state를 고치지 않은 이유: 이건 투영 문서가 아니라 정본의 문제입니다. 바로잡으려면 rev 3를 열어 `UNK-002`를 다시 열어야 하는데, 사용자 없이 제품 정의를 바꾸는 일이라 이번 범위(rev 2 승인 준비)를 넘습니다.
- 두 문서 모두 이 점을 "승인 전에 확인할 점"으로 이미 밝히고 있어서 문서는 그대로 두었습니다.

**남은 것**
1. 사용자에게 rev 2 manifest(위 digest)를 보여 주고 명시적 승인을 받습니다. 이때 '항상 표시'(BELOW)를 확인받아야 합니다.
   - 사용자가 NEAR_LIMIT(180자부터 표시)를 원하거나 확인하지 않으면 rev 2는 승인하지 말고 rev 3에서 `UNK-002`를 다시 엽니다.
   - 사용자가 승인하면, 그 말을 직접 받은 세션이 같은 인자에 `--quote`, `--write`를 붙여 `record_approval.py`를 실행합니다. 그 뒤 `update_projection.py --write`와 `projection_check.py`를 다시 돌립니다.
2. 검토 화면을 브라우저에서 보지 못했습니다. 로컬 파일이라 브라우저 도구가 다루지 못해서, 렌더와 클릭은 NOT_VERIFIED입니다(HTML에도 그렇게 적혀 있습니다).
3. 프로젝트에 JOEFLOW 버전이 고정되어 있지 않습니다. 실행한 스크립트는 1.7.0입니다. `joeflow_version.py --pin`은 파일을 새로 쓰는 일이라 실행하지 않았습니다.

**작업 기록**
- `<SCRATCH>\r03\commands.log`에 pwd와 명령마다 종료 코드를 남겼습니다.
- git 저장소가 아니어서 `git status`는 128로 끝났습니다.
- 출력을 /tmp로 보내려던 첫 manifest 명령은 자동 모드가 거부해 실행되지 않았고 로그에도 없습니다. r03 밖에 쓰지 않는 방식으로 다시 실행했습니다.
