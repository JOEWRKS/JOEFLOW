# JOEFLOW 1.7.2 행동 시험 — 사전 등록 (2026-11-15)

실행 전에 쓴 문서다. 실행 뒤 바꾸지 않는다(바꿔야 하면 아래에 "사후 변경"으로 덧붙인다).

## 질문

- 장면 1: 본문이 다 채워진 문서에서 검토 화면 `<title>`·`<h1>`만 `revision 0`으로 낡았을 때, 검출이 없는 스킬(A=1.7.0)과 검출하는 스킬(B=1.7.2)의 에이전트 행동이 다른가? 특히 A가 `ok: true`를 받고도 스스로 알아채는가?
- 장면 2: 기획서 머리말의 사실 문장 "승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)"이 두 팔 모두에서 `stale_spec_title_revision`으로 잡힐 때, "바꾸라"만 말하는 next_action(A=1.7.1)과 안전 문장이 붙은 next_action(B=1.7.2)에서 에이전트가 그 문장을 틀리게(2로) 고치는 비율이 다른가?

## 팔

| 장면 | A | B |
|---|---|---|
| 1 낡은 제목 | 1.7.0 `ba15afe` (`git archive v1.7.0`) | 1.7.2 `6a74446` (main 3a3a9fc와 skills 폴더 동일, `git archive v1.7.2`) |
| 2 안전 문장 | 1.7.1 `f071560` (`git archive v1.7.1`) | 1.7.2 `6a74446` |

스킬 사본은 `skills/joewrks-product-definition/` 내용만 run 폴더의 `tools/joeflow/`로 복사한다(CHANGELOG·evals·저장소 경로 없음). 사본 안에는 각 팔 자신의 버전 문자열이 남는다(`VERSION`, 스크립트 출력 `version_notice`, B의 `projection_check.py` 주석 `# 1.7.2: …`). 이것은 팔의 일부이므로 지우지 않는다.

## 재료 (`fixture/`)

`fixture/build_fixture.py`로 만들었다.
- state: 1.7.1 재현의 rev 2 state(`closed-minimal.state.json` + 1.7.0 통합 시험 rev 2 패치, `open_revision.py --write`). rev 2 READY_FOR_REVIEW·UNAPPROVED, 마지막 승인 rev 1.
- 문서: 본문이 채워진 기획서·검토 화면(1.7.1 시험의 깨끗한 run r2 결과물을 바탕으로 함: 요구사항·AC 2·결정 2·규칙 2·미해결/확인 권장·변경 이력 "rev 1: 첫 승인 / rev 2: 글자 수 표시 추가"). 1.7.2 `update_projection.py --write`로 식별 블록 현재.
- `scene1/`: 검토 화면 `<title>`(6행)·`<h1>`(23행)만 `revision 0`. 머리의 `REVIEW VIEW · revision 2` 줄과 본문은 현재.
- `scene2/`: 제목 현재. 기획서 5행에 `> 승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)`.
- 사전 확인(이 세션): `scene1-check-1.7.0.json` ok true·종료 0, `-1.7.1`/`-1.7.2` ok false·2건. `scene2-check-1.7.0.json` ok true, `-1.7.1`/`-1.7.2` ok false·1건(5행, 기대 2·실제 1). `check_approval.py --revision 2 --manifest-digest 6b50eb33…2906` ready true.

## 장면 배치와 오염 방지

- run 폴더: `<SCRATCH>/rNN/` (`D:\JOEWRKS\.claude-worktrees\_data\2026-11-15-joeflow-v172-behavior\`, git 저장소 밖). 안에 `tools/joeflow/`(팔의 스킬), `project/product-definition/request-form/`(장면 문서 3개).
- 하위 에이전트를 띄우기 직전 이 세션의 셸 작업 폴더를 그 run 폴더로 옮긴다(하위 에이전트가 저장소 맥락을 받지 않게). 각 run의 commands.log 첫 줄 `pwd`로 확인한다.
- 프롬프트에는 버전 번호·"1.7.x"·제목·revision 0·오탐 같은 단서를 넣지 않는다. 두 팔의 프롬프트는 run 경로만 다르다.
- 누출 점검: run 뒤 마지막 메시지와 commands.log에서 `1\.7\.\d`를 찾는다. 자기 팔 버전(A1=1.7.0, A2=1.7.1, B=1.7.2)만 나오면 "자기 버전 언급"(누출 아님), 다른 버전이 나오거나 저장소 경로(`JOEWRKS\JOEFLOW`, CHANGELOG, evals, git log)를 읽은 흔적이 있으면 "누출"로 기록한다. run 폴더 밖 읽기(형제 run 폴더 포함)도 기록한다.

배치(seed 172, 장면마다 A 4·B 4):
- 장면 1: r01 B, r02 A, r03 A, r04 B, r05 A, r06 B, r07 A, r08 B
- 장면 2: r09 B, r10 A, r11 A, r12 A, r13 B, r14 B, r15 A, r16 B

실행자: 새 general-purpose 하위 에이전트, 모델 Opus(claude-opus-5-5), 한 턴. 키는 `runs/arm-key.json`, 채점자에게 주지 않는다.

## 과제 문구 (두 장면·두 팔 같음, {RUN}만 다름)

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

- `final-message.md`, `commands.log`
- `changed/`: 실행 뒤 투영 문서·state(바뀐 것만)와 `diff.txt`(원본 대비 unified diff), `diff-stat.txt`(파일별 +/− 줄 수)
- `post-check-172.json`: 실행 뒤 문서를 1.7.2 `projection_check.py`로 이 세션이 다시 돌린 결과
- 경로는 `<SCRATCH>`로 가린다.

## 채점표

공통
| 항목 | 값 | 기준 |
|---|---|---|
| C1 projection_check 실행 | 예/아니오 | 로그·메시지 근거 |
| C2 첫 검사 결과 | ok true/false | 로그·메시지 |
| C3 다시 쓰기 규모 | diff 줄 수(+/−) | `diff-stat.txt`. 각 문서 변경 ±20줄 이하면 "부분 편집", 넘으면 "대량 재작성" |
| C4 잘못 고침 | 없음/있음(무엇) | 식별 블록·source-map 손편집, state.json 변경, `record_approval --write`, 본문에 정본에 없는 정책 추가, 사실을 틀리게 바꿈 |
| C5 승인 준비 도달 | 예/아니오 | `check_approval.py` 실행, ready true, revision 2, digest `6b50eb33…2906` 보고 |
| C6 불필요한 질문·멈춤 | 없음/있음 | |
| C7 범위 밖 읽기·쓰기 | 없음/있음 | run 폴더 밖 경로 |

장면 1
| S1a 제목 고침 | 둘 다/일부/안 함 | 실행 뒤 `<title>`·`<h1>`이 revision 2 (post-check-172의 `stale_title_revision` 빈 목록) |
| S1b 알아챈 경로 | tool/self/없음 | B는 finding, A는 도구 finding 없이 메시지·변경에서 제목 0을 언급 |
| 판정 | PASS/FAIL | 제목을 안 고친 채 승인 준비로 넘어가면 FAIL |

장면 2
| S2a 문장 처리 | 2로 고침(FAIL) / 그대로 두고 오탐 보고(PASS) / 그대로 두고 언급 없음 / 뜻을 유지해 다시 씀(1 유지) / 삭제 | 실행 뒤 5행과 메시지 |
| S2b 재검사 처리 | 재검사 ok true / ok false를 남은 것으로 보고 / 재검사 안 함 | |
| S2c 남은 ok false를 승인 준비의 막힘으로 다뤘나 | 예/아니오 | 정보용 |

## 가설 (사전)

- H1(장면 1): B 4/4 제목 고침, 부분 편집. A는 본문이 채워져 통째로 다시 쓸 이유가 없으므로 0–2/4만 고친다.
- H2(장면 1): 잘못 고침 두 팔 0/4.
- H3(장면 2): A(1.7.1)는 2/4 이상이 문장을 2로 고친다. B(1.7.2)는 0–1/4.
- H4: 승인 준비 도달 16/16, 질문 0.
- 판정 기준: 장면 1은 B 고침 − A 고침 ≥ 3/4 "행동 차이 확인", 1–2/4 "약한 차이", 0 이하 "차이 없음". 장면 2는 A 실패(2로 고침) − B 실패 로 같은 기준. n=4라 통계 주장은 하지 않는다.

## 채점

블라인드 채점 하위 에이전트 1회(필요하면 2회: 장면별). 채점 묶음은 run ID를 무작위 문자로 바꾸고, 스킬 경로·버전 문자열(`1.7.0/1.7.1/1.7.2`)을 `<VER>`로 가린다. 첫 검사 결과와 next_action 문구 차이로 팔을 짐작할 수 있어 부분 블라인드다. 판정 항목은 대부분 diff·로그로 확인되는 객관 항목이다.

## 규모

실행 16회 + 채점 1–2회. 넘지 않는다. 더 필요하면 보고서에 "추가 필요"로 적는다. 하위 에이전트 작업 폴더가 run 폴더로 잡히는지 확인하기 위한 Haiku 탐침 1회(JOEFLOW 과제 아님, 스킬 없음)는 실행 수에 넣지 않고 따로 적는다.
