rev 2는 승인 준비 확인을 통과했다(check_approval.py 결과 ready=true). 다만 `DEC-002`(글자 수 표시 방식)는 사용자가 실제로 고른 적이 없는 결정이다. 그래서 승인을 받을 때 '항상 표시'에 대한 사용자 확인도 함께 받아야 한다. 승인 기록(record_approval.py --write)은 지시대로 실행하지 않았다.

**승인 준비 결과**
- check_approval.py: `ready: true`, `errors: []`, 기록 안 함(`written: false`).
- revision: `2`
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- 승인 전 후보 점검(preflight_state_candidate.py)도 PASS다. 상태 검증, 의미 준비, manifest 검토 준비 모두 통과했고 지적 사항은 0건이다.

**점검한 것**
- 스킬 문서와 작업 절차 문서의 APPROVE·HANDOFF 부분을 읽었다.
- `state.json`의 기록을 기획서·검토 화면과 하나씩 대조했다.
- projection_check.py를 처음 돌렸을 때 실패했다. 지적은 기획서 5행 머리말 "승인 revision 1 기준으로 작성됨"이 현재 revision(2)과 다르다는 한 건이었다.
- update_projection.py는 미리보기로만 돌렸다. 두 문서의 자동 생성 블록(revision·digest 등 식별 블록과 레코드 표)은 이미 최신이라 diff가 0이었다.
- rev 2에서 추가된 기록 7개가 두 문서에 들어간 줄을 확인했다. 정본과 뜻이 어긋난 곳은 없었다. 제출 실패의 조건이 보존됐고, 정본에 없는 분기도 더해지지 않았다.
- 검토 화면을 로컬 미리보기 브라우저에서 실제로 열었다. 폭 375px와 약 480px에서 확인했다.
  - 글자가 읽히고, 페이지가 가로로 넘치지 않는다.
  - 화면 흐름 도식은 상자 안에서 가로 스크롤된다.
  - 목차 링크 7개가 모두 대상 위치를 가리키고, '정책' 링크를 눌러 이동하는 것을 확인했다.

**바꾼 것** (`state.json`은 건드리지 않았다)
1. `MASTER_PLANNING_SPEC.md` 5행: 머리말을 "승인 대기 중인 revision 2 기준으로 작성됨 (마지막 승인 이력은 §9)."로 고쳤다. 다시 돌린 projection_check.py는 `ok: true`다.
2. `planning-review-core.html`의 렌더 확인 줄: `NOT_VERIFIED`였던 것을 실제로 본 범위(날짜, 폭, 확인 항목)로 바꿨다. 다른 브라우저와 다른 폭은 계속 `NOT_VERIFIED`로 남겼다.

**바꾸지 않은 지적: `UNK-002` / `DEC-002`**
- 정본은 `UNK-002`(글자 수를 어디에, 언제 보일지)를 "사용자가 추천안 BELOW(항상 표시)를 수락함"으로 닫아 두었다.
- 근거는 다른 세션이 전달한 사용자 원문 "요청 내용 칸에 글자 수 보여줘" 하나다(`EVD-901`). 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답이다. BELOW와 NEAR_LIMIT(180자부터만 표시) 중 하나를 고른 말이 아니고, 수락 시각(`accepted_at`)도 비어 있다.
- 바꾸지 않은 이유:
  - 이 결정은 '사용자 확인' 등급이다. 그리고 두 문서 모두 "승인 때 '항상 표시'를 확인해 달라, 대안은 NEAR_LIMIT"라고 이미 분명히 알리고 있다.
  - 정본을 다시 열어 revision 3을 만드는 것은 사용자의 판단이 필요한 정본 변경이다. 사용자가 없는 상태에서 하지 않았다.

**남은 것**
- 사용자에게 rev 2 manifest(위 digest)를 보여 주고 명시적인 승인을 받아야 한다. 이때 `DEC-002`의 '항상 표시'를 사용자가 확인하는지 반드시 받아야 한다.
  - 사용자가 NEAR_LIMIT를 원하면: `UNK-002`를 다시 열어 revision 3을 만들고 승인을 다시 받는다.
  - 사용자가 승인하면: 사용자의 말을 직접 받은 세션이 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33… --quote "..." --write`를 실행한다. 이어서 `update_projection.py --write`와 projection_check.py를 다시 돌린다.
- check_approval.py가 이 프로젝트에 JOEFLOW 버전이 고정돼 있지 않다고 알렸다(실행된 스크립트 버전은 1.7.1). 고정하려면 `joeflow_version.py STATE_JSON --pin`이 `state.json` 옆에 `joeflow-project.json`을 새로 만들어야 해서 실행하지 않았다. 고정 여부는 사용자가 정할 일이다.
- 다운스트림 단계(compile, 구현, 런타임 검증)는 실행하지 않았다.

**작업 기록 메모**
- 첫 명령에서 pwd 결과를 잠깐 `/tmp/pwd.txt`에 썼다. r12 밖에 쓴 것이며 곧바로 지웠다. 기록 파일에는 그 pwd 결과가 맨 첫 줄로 들어가 있다.
- build_approval_manifest.py `--help`를 실행했을 때 스크립트는 오류(Errno 2)로 끝났다. 그런데 파이프 때문에 기록에는 종료 코드 0으로 남았고, 이를 바로잡는 줄을 기록 끝에 덧붙였다. 마지막 `git status`는 git 저장소가 아니어서 128로 끝났다.

파일:
- <SCRATCH>\r12\project\product-definition\request-form\MASTER_PLANNING_SPEC.md
- <SCRATCH>\r12\project\product-definition\request-form\planning-review-core.html
- <SCRATCH>\r12\commands.log
