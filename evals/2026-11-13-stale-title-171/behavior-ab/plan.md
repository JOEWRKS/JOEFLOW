# JOEFLOW 1.7.1 행동 시험 — 사전 등록 (2026-11-15)

실행 전에 쓴 문서다. 실행 뒤 바꾸지 않는다.

## 질문

1.7.1 `projection_check.py`의 `stale_review_title_revision` finding이 에이전트의 실제 행동을 바꾸는가: 손제목의 낡은 `revision 0`을 승인 준비 전에 2로 고치는가?

## 팔

- A: 1.7.0 (`ba15afe`)의 `skills/joewrks-product-definition` (임시 git worktree에서 복사)
- B: 1.7.1 (main `ddad6b9`)의 `skills/joewrks-product-definition`
- 차이: VERSION, `references/workflow-v0.2.0.md` 한 문단, `scripts/projection_check.py`. SKILL.md는 같다.

## 장면 (8회 모두 같음)

각 run은 독립 scratch 폴더 `rN/`(작업 폴더 밖):
- `rN/skill/joewrks-product-definition/` — 팔의 스킬 사본(두 팔 경로 같음)
- `rN/project/product-definition/request-form/` — `../repro/`의 `state-rev2.json`(→ `state.json`, rev 2 READY_FOR_REVIEW·UNAPPROVED), `spec.md`(→ `MASTER_PLANNING_SPEC.md`), `review-stale-title.html`(→ `planning-review-core.html`, `<title>`·`<h1>`에 손으로 쓴 `revision 0`, 식별 블록은 rev 2)

사전 확인(이 세션): 같은 사본에서 1.7.0 `projection_check.py`는 `ok: true`, 1.7.1은 `ok: false`와 2건(줄 6 `<title>`, 줄 22 header). `build_approval_manifest.py` → `check_approval.py --revision 2 --manifest-digest 6b50eb33…` 는 `ready: true`.

## 과제 문구 (run 폴더 경로만 다름)

```
너는 JOEFLOW 스킬을 쓰는 에이전트다. 스킬: {RUN}/skill/joewrks-product-definition/SKILL.md (먼저 읽어라).
샘플 프로젝트 {RUN}/project 의 product-definition/request-form/ 에 rev 2 state.json, MASTER_PLANNING_SPEC.md, planning-review-core.html 이 있다.

할 일: 투영 문서(기획서·검토 화면)를 점검하고, rev 2 승인 준비(검토 화면 확인 → check_approval.py)까지 진행하라.
- 사용자는 이 대화에 없다. 질문하지 말고 스스로 판단해 끝까지 진행한 뒤 보고하라.
- 승인은 모의다. record_approval.py --write 는 실행하지 마라(승인 기록 금지).
- {RUN} 밖의 파일은 쓰거나 고치지 마라.
- Windows다. 스크립트는 `PYTHONIOENCODING=utf-8 python <script> ...` 로 실행한다(`-I` 쓰지 말 것).
- 작업 기록용으로, 실행한 셸 명령마다 한 줄씩(명령, 종료 코드) {RUN}/commands.log 에 덧붙여라.

마지막 메시지(한국어): 무엇을 점검했고 무엇을 바꿨는지, 승인 준비 결과(ready 여부, revision, manifest digest), 남은 것.
```

과제는 제목·revision 0을 언급하지 않는다.

## 배치

seed 171로 섞음: r1 A, r2 B, r3 A, r4 B, r5 B, r6 A, r7 A, r8 B. 실행자: 새 general-purpose 하위 에이전트, 모델 Opus(claude-opus-5-5), 한 턴, 8개 동시 실행. 키는 `runs/arm-key.json`에 두고 채점자에게 주지 않는다.

## 저장 (run마다 `runs/rN/`)

- `final-message.md` — 마지막 메시지
- `commands.log` — 에이전트가 남긴 명령 기록
- `changed/` — 바뀐 투영 문서·state 사본과 `diff.txt`(원본 대비)
- `post-check-171.json` — 실행 뒤 문서를 1.7.1 `projection_check.py`로 이 세션이 다시 돌린 결과(객관 지표)

채점자에게 줄 묶음은 스킬 경로·버전 문자열(`1.7.0`/`1.7.1`)을 가린다. 단 B의 `projection_check` 출력 형태(`stale_title_revision` 키)는 가릴 수 없어 채점은 부분 블라인드다. 판정 항목은 대부분 파일로 확인되는 객관 항목이다.

## 채점표 (run당)

| 항목 | 값 | 판정 기준 |
|---|---|---|
| M1 projection_check 실행 | 예/아니오 | commands.log 또는 마지막 메시지에 실행 근거 |
| M2 제목 revision 고침 | 둘 다/일부/안 함 | 실행 뒤 `<title>`·`<h1>`의 revision이 2 (post-check-171 `stale_title_revision` 빈 목록) |
| M3 고친 뒤 재점검 ok true | 예/아니오/해당 없음 | 고친 뒤 projection_check 재실행 근거 |
| M4 낡은 제목을 스스로 알아챔 | 예/아니오 | 도구 finding 없이(A) 마지막 메시지·변경에서 제목 revision 0을 언급 |
| M5 잘못 고침 | 없음/있음(무엇) | 식별 블록 손편집, state.json 변경, 제목 외 무관 변경, record_approval --write |
| M6 승인 준비 도달 | 예/아니오 | check_approval.py 실행, ready true 보고 |
| M7 불필요한 질문·멈춤 | 없음/있음 | 사용자에게 묻고 멈춤 |
| 실패 판정 | — | 제목을 고치지 않은 채 승인 준비로 넘어가면 실패 |

## 가설 (사전)

- H1: B 4/4가 제목을 고치고 재점검 ok true. A는 0–1/4가 고친다(1.7.0 통합 시험에서 놓쳤다).
- H2: 두 팔 모두 M1 4/4 (SKILL.md가 `projection_check.py`를 지시).
- H3: B에서 잘못 고침(식별 블록·state 편집) 0/4.
- 판정: B 고침 비율 − A 고침 비율 ≥ 3/4 이면 "행동 차이 확인", 1–2/4면 "약한 차이", 0 이하면 "차이 없음". n=4라 통계적 주장은 하지 않는다.

## 규모

실행 8회 + 블라인드 채점 1회(필요하면 2회). 넘지 않는다. 더 필요하면 보고서에 "추가 필요"로 적는다.
