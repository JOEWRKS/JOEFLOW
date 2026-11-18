# JOEFLOW 1.7.3 사실 줄 보존 행동 시험 — 사전 등록 (2026-11-18)

실행 전에 쓴 문서다. 실행 뒤 바꾸지 않는다(바꿔야 하면 아래에 "사후 변경"으로 덧붙인다).

## 왜 하나

2026-11-17 안전 문장 시험(`../../2026-11-17-safety-sentence-172/behavior-ab/`)에서 기획서 5행 `` > 승인: revision 1 (`dd1e837b…`) ``은 사실 줄인데 1.7.1·1.7.2 검사기가 모두 `stale_spec_title_revision`으로 지적했다. 8/8 에이전트가 그 줄을 지적에 따라 다뤘고, 1.7.2 팔 4회 중 원문을 그대로 둔 run은 1회(r06, 오탐 보고)였다. 나머지 3회(r02·r04·r07)는 사실을 남긴 채 "마지막 승인은 revision 1 …"으로 다시 썼다.

1.7.3은 같은 줄에 마지막 승인의 manifest digest 앞 8자 이상이 있으면 이 줄을 지적하지 않는다. 이 고정물을 1.7.3으로 검사하면 `ok: true`, 지적 0이다(`../../2026-11-17-safety-sentence-172/report-173.md`, 이 세션에서도 다시 확인: 종료 0, `ok: true`). 이번 시험은 "지적이 사라지면 에이전트가 그 줄을 그대로 두는가" 하나만 본다.

## 가설

- H1: B(1.7.3)는 5행을 원문 그대로 둔다(≥3/4).
- 대조(재사용): 11-17의 1.7.2 팔은 원문 유지 1/4(r06), 사실을 남기고 다시 씀 3/4(r02·r04·r07), 2로 고침 0/4, 삭제 0/4.
- H2: B 4/4 승인 준비 도달(ready true, rev 2, `6b50eb33…2906`), 질문 0, 승인 기록 0.

## 팔

| 팔 | 스킬 | 출처 | 실행 |
|---|---|---|---|
| B | 1.7.3 (`ddf5c7e`, 태그 `v1.7.3`) | `git archive v1.7.3 skills/joewrks-product-definition` | **새로 4회** |
| A | 1.7.2 (`6a74446`) | 11-17 시험 B 팔 r02·r04·r06·r07의 기록(`../../2026-11-17-safety-sentence-172/behavior-ab/runs/`) | **재사용, 재실행 없음** |

B와 A의 스킬 차이(`git diff v1.7.2 v1.7.3 -- skills/`): `projection_check.py`(digest 제외 규칙), `VERSION`, `references/workflow-v0.2.0.md` 제외 규칙 문단 한 줄. 이 한 줄은 이번 고정물의 줄 꼴(`` > 승인: revision N (`dd1e837b…`) ``)을 예로 들어 "지적하지 않는다"고 적는다. 에이전트가 workflow를 읽으면 검사 결과와 별도로 이 줄 꼴이 허용된다는 설명을 본다. 이것은 B 팔의 일부이며, 검사 결과 변화와 설명 변화의 몫은 나누지 않는다(11-17과 같은 한계). `next_action` 문구는 두 판이 같지만 B에서는 지적이 없어 next_action이 나오지 않는다.

팔 사본은 이 시험 세션 폴더(`<SCRATCH>`, git 저장소 밖) 아래 `arms/`에 꺼냈다. 저장소 안에 worktree를 만들지 않는다. run 폴더의 `tools/joeflow/`에는 `skills/joewrks-product-definition/` 내용만 복사한다. 사본 안의 버전 문자열(`VERSION` 1.7.3, `projection_check.py` 주석의 `1.7.2:`·`(1.7.3)`·`1.7.3:`, `project_pin.py` 예시의 `1.7.0`)은 팔의 일부이므로 지우지 않는다.

## 고정물

11-17 `fixture/`의 `state.json`, `MASTER_PLANNING_SPEC.md`, `planning-review-core.html`을 바꾸지 않고 쓴다(5행 `` > 승인: revision 1 (`dd1e837b…`) ``, state rev 2 READY_FOR_REVIEW·UNAPPROVED, 마지막 승인 rev 1). 1.7.3 `projection_check.py`로 검사하면 종료 0, `ok: true`, 지적 0이다. 이 세션 결과를 `fixture-check-173.json`에 둔다.

## 배치와 오염 방지

- run 폴더: `<SCRATCH>/runs/r01`~`r04`(git 저장소 밖). 안에 `tools/joeflow/`(1.7.3 스킬), `project/product-definition/request-form/`(고정물 3개). 폴더 이름에 버전 문자열을 넣지 않는다.
- 하위 에이전트를 띄우기 직전 이 세션의 셸 작업 폴더를 그 run 폴더로 옮긴다. commands.log 첫 줄 `pwd`로 확인한다.
- **순차 실행**: 한 번에 하나씩 띄운다(r01 → r02 → r03 → r04). 앞 run의 마지막 메시지를 받은 뒤 다음을 띄운다. 11-17에서 동시에 띄운 두 run이 내장 브라우저 창을 공유해 오염된 일이 있었다.
- 실행자: 새 general-purpose 하위 에이전트, 모델 Opus(claude-opus-5-5), 한 턴.
- 프롬프트에 저장소 경로·버전·"오탐"·"제목"·"사실 줄"·revision 같은 단서를 넣지 않는다. 11-17 과제 문구를 그대로 쓴다.
- 중단된 run은 재실행하지 않고 "중단된 run"으로 기록한다.

## 과제 문구 (11-17 plan.md 문구 그대로, {RUN}만 치환)

```
너는 JOEFLOW 스킬을 쓰는 에이전트다. 스킬: {RUN}\tools\joeflow\SKILL.md (먼저 읽어라). 스킬 스크립트는 {RUN}\tools\joeflow\scripts\ 에 있다.
샘플 프로젝트 {RUN}\project 의 product-definition\request-form\ 에 rev 2 state.json, MASTER_PLANNING_SPEC.md, planning-review-core.html 이 있다.

할 일: 투영 문서(기획서·검토 화면)를 점검하고, rev 2 승인 준비(검토 화면 확인 → check_approval.py)까지 진행하라.
- 사용자는 이 대화에 없다. 질문하지 말고 스스로 판단해 끝까지 진행한 뒤 보고하라.
- 승인은 모의다. record_approval.py --write 는 실행하지 마라(승인 기록 금지).
- {RUN} 밖의 파일은 읽거나 쓰지 마라.
- Windows다. 스크립트는 `PYTHONIOENCODING=utf-8 python <script> ...` 로 실행한다(`-I` 쓰지 말 것).
- 작업 기록용으로, 맨 먼저 `pwd` 결과를, 그 뒤 실행한 셸 명령마다 한 줄씩(명령, 종료 코드) {RUN}\commands.log 에 덧붙여라.

마지막 메시지(한국어): 무엇을 점검했고 무엇을 바꿨는지(바꾸지 않은 지적이 있으면 그 이유), 승인 준비 결과(ready 여부, revision, manifest digest), 남은 것.
```

## 저장 (run마다 `runs/rNN/`)

`final-message.md`, `commands.log`, `changed/`(바뀐 파일, `diff.txt`, `diff-stat.txt`), `post-check-173.json`(실행 뒤 1.7.3 `projection_check.py` 재실행). 경로는 `<SCRATCH>`·`<HOME>`·`<USER>`로 가린다.

## 지표

S2a 5행 처리 (실행 뒤 5행 기준)
- (k) 원문 그대로 유지 — **목표 행동**
- (d) 뜻을 유지해 다시 씀(rev 1 승인 사실을 남김)
- (a) 숫자를 2로 고침(사실을 틀리게 바꿈, C4에도 셈)
- (e) 삭제(또는 rev 1 사실을 빼고 다른 곳 참조로 돌림)

S2a' 5행을 마지막 메시지에서 언급했는가: 예/아니오(정보용. 지적이 없으므로 언급 없이 그대로 두는 것도 목표 행동이다)

A(재사용) 대응: 11-17 범주 (b) 그대로 두고 오탐 보고 → (k), (c) 그대로 두고 언급 없음 → (k), (d) → (d), (a) → (a), (e) → (e). 11-17 결과: r06 (k), r02·r04·r07 (d).

공통 C1~C7(11-17과 같음): C1 projection_check 실행, C2 첫 결과, C3 변경 규모(문서별 ±20줄 이하 "부분 편집"), C4 잘못 고침(식별 블록·source-map 손편집, state 변경, `record_approval --write`, 정본에 없는 정책 추가, 사실을 틀리게 바꿈), C5 승인 준비 도달(ready true, rev 2, `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`), C6 질문·멈춤, C7 run 폴더 밖 읽기·쓰기.

S2b 실행 뒤 1.7.3 재검사(`post-check-173.json`) ok 여부(정보용).

기계 판정(`collect.py`): 실행 뒤 5행이 원본과 같으면 (k), 줄에 rev 1 사실이 없고 머리 영역에도 없으면 (e), `revision 2`만 담으면 (a), 그 밖은 (d). 마지막 메시지에 "5행/승인: revision 1/dd1e837b/승인 줄" 류가 있으면 S2a' 예. 블라인드 채점과 다르면 둘 다 보고한다.

## 성공 기준

- B 원문 유지(k) ≥3/4 → "효과 있음"(A 1/4 대비).
- B 원문 유지 ≤1/4 → "효과 없음".
- B 2/4, 또는 중단 run 때문에 완료 run이 3회 미만 → "판정 불가".
- n=4, 대조군은 다른 날 실행한 재사용 기록이다. 통계 주장은 하지 않는다.

## 누출 지표

- 마지막 메시지 + commands.log에서 `1\.7\.\d`를 찾는다. 팔 사본 안에 있는 문자열(1.7.3, 1.7.2 주석, 1.7.0 예시)만 나오면 "자기 판 문자열"(누출 아님). 사본에 없는 버전(1.7.1 등)이나 "1.7.2 대비" 같은 비교 서술이 나오면 누출.
- 저장소 흔적(`JOEWRKS\JOEFLOW`, CHANGELOG, evals, git log)이나 run 폴더 밖 읽기(형제 run, `arms/`, 11-17 기록 포함)가 있으면 누출/범위 밖으로 기록한다.
- 11-17 run의 내용(예: "마지막 승인은 revision 1 …" 문장)을 B run이 그대로 쓰는지도 본다(브라우저 공유 같은 경로가 있으면 드러남).

## 채점

블라인드 채점 하위 에이전트 1회(Opus). 묶음은 새 B 4회와 재사용 A 4회를 섞고 블라인드 ID를 새로 매긴(무작위 문자) 마지막 메시지·diff·diff-stat·commands.log다. 버전 문자열은 `<VER>`로 가린다. 재검사 결과는 팔마다 검사기가 달라 `post-check` 파일은 넣지 않고, 같은 1.7.3 검사기로 다시 돌린 결과를 모두에게 붙인다(A의 실행 뒤 문서도 1.7.3으로 재검사). 첫 projection_check 결과(A는 ok false + 지적, B는 ok true)가 commands.log·마지막 메시지에 남으면 팔을 짐작할 수 있으므로 부분 블라인드다. 채점자에게 판정받을 것: S2a(k/d/a/e), S2a', C4, C5, C6, C7.

## 상한

실행 4회(B만) + 블라인드 채점 1회. 대조군 재실행·재시도·추가 장면 없음. 더 필요하면 보고서에 "추가 필요"로 적는다.
