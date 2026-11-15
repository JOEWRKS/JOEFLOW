# JOEFLOW 1.7.2 후보 — 마지막 승인 문장 오탐 수정

결론: 머리 영역의 "마지막 승인은 revision 1" 같은 사실 문장을 1.7.1은 `stale_spec_title_revision`으로 잡았고, 후보는 숫자가 state의 마지막 승인 revision과 같을 때만 건너뛴다. 낡은 손제목은 여전히 잡는다.

## 재현 전/후

1.7.1 행동 시험(`evals/2026-11-13-stale-title-171/behavior-ab/`)의 1.7.0 팔 r1·r6 실행 뒤 문서를 작업 폴더 밖 임시 폴더에 복사하고, state는 같은 시험의 rev 2 state(`../2026-11-13-stale-title-171/repro/state-rev2.json`, rev 2 READY_FOR_REVIEW·UNAPPROVED, 승인 revision [1])를 썼다. 1.7.1은 `git archive v1.7.1`로 꺼낸 스킬 폴더에서 돌렸다.

| run | 문제 줄 (기획서 머리) | 1.7.1 | 후보 |
|---|---|---|---|
| r1 | 5행 `> 현재 revision 2는 **승인 대기(…)** 입니다. 마지막 승인은 revision 1입니다.` | `stale_spec_title_revision` 기대 2·실제 1, ok false, 종료 1 | finding 없음, ok true, 종료 0 |
| r6 | 7행 `> 마지막으로 승인된 것은 revision 1이다.` | `stale_spec_title_revision` 기대 2·실제 1, ok false, 종료 1 | finding 없음, ok true, 종료 0 |

- 1.7.1 출력은 시험 때 저장한 `post-check-171.json`과 바이트 단위로 같다.
- 전/후 JSON: `repro/r1-check-before-171.json`, `repro/r1-check-after-172.json`, `repro/r6-…`. 후보 출력은 `stale_title_revision`과 `ok`만 다르고 나머지 키는 같다.
- 나머지 run(r2–r5, r7, r8)의 실행 뒤 문서도 후보로 돌려 모두 ok true, title finding 0이다.

## 실제 표기 조사

8개 run의 실행 뒤 문서, `templates/`, 오목 rev 44 투영(읽기 전용 사본)에서 "승인/approv"와 revision 번호가 같이 나오는 줄을 모았다.

- 머리 영역에 실제로 나온 승인 상태 문장: "마지막 승인은 revision 1입니다"(r1), "마지막으로 승인된 것은 revision 1이다"(r6).
- 본문(머리 밖)에 나온 같은 종류: "마지막 승인은 revision 1."(r5), "마지막 승인 revision 1."(r2), "revision 1만 승인됨"(r6), "rev 1만 승인됨"(r7). 머리로 올라오면 같은 오탐이 나므로 범위에 넣었다.
- 이미 1.7.1이 건너뛰는 것: "이전 승인: rev 1", "이전 승인 rev 12"(오목).
- 현재 revision과 같은 숫자("revision 2 · 승인 대기", "REVIEW VIEW · revision 2")는 원래 finding이 아니다.
- 영어 승인 상태 문장("last approved" 등)은 조사 대상에서 한 건도 나오지 않았다. 템플릿이 영어 머리를 허용하므로 대칭으로 넣었다.

## 바뀐 제외 범위

건너뛰는 조건은 둘 다 맞아야 한다.

1. 숫자가 state의 마지막 승인 revision(`approval_status`의 `last_approved_revision`)과 같다. 승인이 없으면 이 규칙은 아무것도 건너뛰지 않는다.
2. 번호 앞뒤에 승인 상태를 말하는 표현이 있다.
   - 앞(30자 안, 번호 바로 앞에서 끝남): `마지막|최근|최종|현재` + (`으로|에`) + `승인` + (`된|됨|한|받은`) + (`것|판|버전`) + (`은|는|이|가`); `승인된|승인받은` + `것|판|버전` + 조사; `last|latest|most recent(ly)|currently` + `approved|approval` + (`is|was|at|in`). 뒤에 구두점 3자까지(`:` 등) 허용.
   - 뒤: `만 승인`, `까지 승인`, `이/가 마지막(으로) 승인`, `is/was (the) last/latest/most recent approved…`, `(last approved)`.

1.7.1의 "이전/직전/previous/prior/since/from" 규칙과 범위(`rev 1→2`) 규칙은 그대로다(숫자 조건 없음).

넘기지 않는 선(지나친 제외를 막는 것):
- 꾸밈말 없는 "승인 revision 1", "승인된 revision 1 기획서", "Approved: rev 1", "revision 1 (approved)", "revision 1 승인됨"은 건너뛰지 않는다. 제목이 승인 당시 그대로 남은 낡은 제목과 글자로 구별이 안 되기 때문이다.
- "승인 검토 revision 0", "검토 revision 1 승인 대기"처럼 승인이 상태가 아니라 화면 이름·대기 표시인 경우도 그대로 검출한다.
- 승인 상태 문장이라도 숫자가 마지막 승인 revision이 아니면(예: 승인 [1]인데 "마지막 승인은 revision 0") 그 문장 자체가 틀렸으므로 검출한다.

## next_action 안전 문장

적용했다. 새 문구: `line N: if this line names the document's own revision (title, header), change revision X to Y by hand; update_projection.py rewrites only the identity block and the 'REVIEW VIEW … revision N' form. If it truthfully states another revision (an earlier or the last approval), leave it and report a checker false positive`.

이유: 제외 규칙은 표기를 다 덮지 못한다(아래 한계). 1.7.1 문구는 "바꾸라"만 말해서, 덮지 못한 사실 문장을 에이전트가 틀린 문장으로 고칠 수 있었다. 반대 위험(진짜 낡은 제목을 "오탐"으로 넘김)은 조건을 "다른 revision을 사실대로 적은 문장"으로 좁히고 제목·머리는 바꾸라는 말을 앞에 두어 줄였다. 기존 "change revision X to Y by hand"는 그대로 있어 1.7.1 테스트가 통과한다.

## 남는 한계

- 꾸밈말 없는 승인 표기("승인: revision 1", "Approved: rev 1")가 사실 문장으로 쓰이면 여전히 오탐이 난다. 그때는 next_action의 새 문장에 기댄다.
- "revision 1이 승인된 마지막 판이다", "1번째 승인" 같은 어순·표기는 덮지 않는다.
- 마지막 승인이 아닌 더 이전 승인을 꾸밈말 없이 적은 문장("rev 12 승인 기록")은 1.7.1처럼 검출된다("이전 승인"이라고 쓰면 건너뛴다).
- 앞 30자 창이라 "마지막 승인은 (아주 긴 괄호 설명) revision 1"처럼 사이가 길면 잡는다.
- 영어 형태는 실제 문서에서 나온 적이 없어 직접 만든 문장으로만 시험했다.

## 테스트 결과

- `tests/test_projection_check_v020.py`: 17개 통과(기존 12, 그중 1.7.1 제목 테스트 7건 그대로 + 새 `LastApprovedSentenceTest` 5건: 한국어 r1·r6형 등 5문장 미검출, 영어 6문장 미검출, 마지막 승인 번호를 쓴 낡은 손제목 7형 검출, 틀린 승인 문장 검출과 next_action 문구, rev 2 템플릿 통과).
- 전체(`python -B -m unittest discover -s tests -p 'test*.py'`): 후보 1,256개(새 5) 중 실패 3·오류 5·건너뜀 1. 같은 명령을 `v1.7.1` 임시 worktree에서 돌리면 1,251개 중 실패 3·오류 5·건너뜀 1. 실패·오류 8건의 목록이 줄 단위로 같다(discovery baseline digest 2, projection audit F04 fixture 1, reverse bootstrap schema 2, migration 구조 스키마 2, downstream 2.1 dogfood replay 1 — 1.7.1 보고서의 환경 원인 8건).

## 확인된 것 / 확인되지 않은 것

확인된 것
- r1·r6 오탐을 1.7.1로 재현했고(시험 때 저장한 결과와 같음) 후보에서 사라진다.
- 8개 run 문서 모두 후보에서 ok true.
- 마지막 승인 번호를 쓴 낡은 손제목 6형, Markdown 제목 1형, 틀린 승인 문장 1형은 여전히 검출된다(새 테스트).
- rev 2 state로 갱신한 템플릿은 finding이 없다(새 테스트). 1.7.1의 제목 테스트 7건은 그대로 통과한다.
- 오목 rev 44 실제 투영(세 파일 읽기 전용 사본): 1.7.1·후보 출력이 바이트 단위로 같고 ok true(`repro/gomoku-rev44-check-171.json`, `…-172.json`).

확인되지 않은 것
- 새 next_action 문장을 받은 에이전트가 실제로 사실 문장을 그대로 두고 진짜 낡은 제목은 고치는지(행동 시험). 유료 모델 실행을 하지 않아서다.
- 오목 외 다른 실사용 프로젝트 문서.

## 사용자 대신 정한 것

- 숫자 조건(마지막 승인 revision과 같을 때만 건너뜀)을 더했다. 과제 목록에 없던 조건이지만, 이게 있어야 "승인 revision 1"류를 넓게 받아도 틀린 문장을 놓치지 않는다. 대신 꾸밈말 없는 "승인 revision N"·"approved revision N"·"approval: revision N"은 제목과 구별이 안 돼 범위에서 뺐다(과제가 후보로 든 표기 중 일부를 넣지 않음).
- next_action 안전 문장을 넣었다.
- `PROGRAM_ARCHITECTURE.md`의 버전 목록에는 1.7.2를 적지 않았다(게시 전).
- 출력 JSON 모양은 바꾸지 않았다(`identity`에 키를 더하지 않고 `approval_status`를 한 번 더 불렀다).
