rev 2는 승인 준비를 마쳤습니다. `check_approval.py` 결과는 `ready: true`, 오류는 없습니다. 모의 승인이므로 `record_approval.py --write`는 실행하지 않았고 state.json도 고치지 않았습니다.

**점검한 것**
- `projection_check.py`는 처음부터 `ok: true`였습니다. 두 문서의 JOEFLOW 식별 블록(revision, digest)도 현재 상태와 맞았습니다.
- 그런데 두 문서의 나머지 내용은 템플릿 그대로였습니다. 이 문제는 스크립트가 잡지 못했습니다.
  - 기획서(MASTER_PLANNING_SPEC.md): 1~9절이 작성 안내문 그대로였고, 레코드 표는 모두 `text`였습니다. 정본 경로도 `{{CANONICAL_STATE_PATH}}`로 비어 있었습니다.
  - 검토 화면(planning-review-core.html): `<title>`과 h1이 "revision 0"이었습니다. 나머지 칸은 모두 `{{...}}` 자리표시자였고, Render verification도 비어 있었습니다.
- 이 스킬은 1.7.0이라, 1.7.1에서 고친 "직접 쓴 제목의 오래된 revision 검사"가 들어 있지 않습니다. 그래서 "revision 0"을 잡지 못한 것으로 보입니다.
- state.json의 레코드를 모두 읽고 manifest를 따로 만들어 비교했습니다. 식별 블록의 manifest digest가 일치했습니다.

**바꾼 것** (`project/product-definition/request-form/` 안의 두 문서만)
- **기획서**: 1~9절과 레코드 표를 state.json 내용으로 채웠습니다.
  - rev 2에서 추가된 7개 레코드를 넣었습니다: UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902.
  - state에 없는 것은 지어내지 않고 "정의되어 있지 않음"으로 적었습니다: 거절 뒤 복구, 수락 뒤 이동, '유효함'의 구체 조건.
  - 생성 블록(IDENTITY, SOURCE-MAP)은 그대로 두었습니다.
- **검토 화면**: 제목과 h1을 revision 2로 고치고 상태를 UNAPPROVED로 표시했습니다.
  - 범위, IA 다이어그램, FLOW-001 분기 다이어그램(유효하면 수락·저장, 아니면 제출 안 됨), SCR-001 카드, 정책, 승인 상태를 채웠습니다.
  - Render verification은 `NOT_VERIFIED`로 적었습니다. 로컬 서버로 열어 DOM은 확인했습니다: 제목과 h1이 revision 2, 내부 앵커 6개 모두 연결, 가로 넘침 없음. 하지만 브라우저 창이 숨겨져 있어 스크린샷이 비어서 화면 자체는 보지 못했습니다.
- 수정 뒤 확인 결과는 모두 통과입니다:

| 확인 | 결과 |
|---|---|
| `update_projection.py` (미리보기만) | `ok`, 바뀐 줄 0 |
| `projection_check.py` | `ok: true` |
| `validate_state.py` | `valid` |
| `preflight_state_candidate.py` | PASS, 다음 단계는 manifest를 사용자에게 보여주기 |

**승인 준비 결과**
- ready: true, 오류 없음
- revision: 2 (READY_FOR_REVIEW, UNAPPROVED, rev 1→2 추가 7건, 변경·대체·폐기 없음)
- definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- `approval_status.py`: 승인된 revision은 1뿐이고, 2가 승인 대기 중입니다.

**남은 것**
- 사용자가 위 manifest를 직접 보고 명시적으로 승인해야 합니다. 그 말을 받은 세션이 `record_approval.py --quote ... --write`로 기록합니다(이번에는 금지라 실행하지 않음). 승인 뒤에는 `update_projection.py --write`를 다시 돌리고 두 문서의 "승인 대기" 표현을 고쳐야 합니다.
- 검토 화면을 실제로 열어 보는 확인이 아직 남아 있습니다(`NOT_VERIFIED`).
- 프로젝트가 쓰는 JOEFLOW 버전이 기록되어 있지 않습니다(`joeflow_version.py --pin`). 파일이 새로 생기는 일이라 하지 않았습니다.
- 사고 두 건이 있었습니다:
  - 명령 기록 준비 중 실수로 r3 밖(`scratchpad/runs/r3_log.sh`)에 빈 파일을 만들었습니다. 바로 지웠고 commands.log에 적었습니다.
  - 검토 화면을 띄울 때 브라우저 창에서 다른 실행이 열어 둔 탭(tab-8, 127.0.0.1:8765)이 내 페이지로 바뀌었습니다. 파일은 바뀐 것이 없습니다.

파일 (모두 runs/r3/ 아래): project/product-definition/request-form/MASTER_PLANNING_SPEC.md, project/product-definition/request-form/planning-review-core.html, commands.log, manifest.json (manifest 출력), MASTER_PLANNING_SPEC.orig.md, planning-review-core.orig.html (수정 전 백업)
