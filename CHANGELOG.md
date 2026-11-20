# JOEFLOW 변경 기록

프로그램 릴리스 기록입니다. State, schema, action contract, semantic-review 같은 런타임 identity는 프로그램 버전과 별도로 호환성을 관리합니다.

## 2.0.1 — 후보 (미게시)

2026-11-19 2.0.0 시험 두 건(QUICKSTART 실행 시험 [보고서](evals/v2-tests-20261119/report-docs-joeflow.md), 세 도구 연동 시험 [보고서](evals/v2-tests-20261119/report-integration.md))에서 나온 JOEFLOW 결함을 고친 후보입니다. 태그·Release·개인 설치는 아직 없습니다. 준비 기록은 [report-201.md](evals/v2-tests-20261119/report-201.md)입니다.

**바뀐 것**

- `open_revision.py`(`revision_v2.py`): `--status READY_FOR_REVIEW` 개정에서 `discovery_baseline`이 `CURRENT`가 아니면 그 자리에서 세웁니다(`build_discovery_baseline.py`가 출력하는 것과 같은 객체, 보고에 `"discovery_baseline": "ESTABLISHED"`). 빈 템플릿에서 시작한 새 프로젝트가 `discovery_baseline_gaps`·`discovery_procedure_gaps`(pointer `null`)에 막혀 state.json을 손으로 고쳐야 하던 문제(연동 D2)를 고칩니다. `OPEN`·`BLOCKED` 개정과 이미 `CURRENT`인 baseline의 동작은 그대로입니다.
- `new_records.py question`·`user-decision`: `--evidence`가 선택이 됐습니다. 사용자 의도만 근거인 질문을 `--reason`으로만 기록할 수 있습니다. 전에는 `--evidence`가 필수여서 의도 근거를 넣으면 질문이 `EVIDENCE_RESOLVABLE`이 되어 검증에 걸렸습니다(연동 D10, 재현함).
- `references/first-plan-guide.md`: baseline이 언제 세워지는지, 의도 근거를 어느 플래그에 넣는지.
- `docs/QUICKSTART.md`·README 설치 블록: 문서 결함 D1~D8. README 블록은 태그 `v2.0.1`을 `./JOEFLOW`로 받고, 블록 전체를 `& { … }`로 감싸 clone이 실패하면 아무것도 복사하지 않고 멈춥니다.
- 테스트 환경 정리(스킬 변경 없음, 2026-11-20 부모 세션 추가 요청): `pwsh`가 없으면 `test_discovery_baseline_v020`·`test_reverse_bootstrap_v020`의 스키마 서브테스트 4건을 skip. `test_migration_v020_apply`의 스키마 테스트는 `Test-Json`이 없으면(Windows PowerShell 5.1) skip. `.gitattributes`에 `/evals/joeflow-f03-f04/fixtures/** text eol=lf`(index는 이미 LF라 커밋 바이트는 그대로, CRLF 체크아웃만 막음). M6 재생 테스트는 원래 계획이 "조용히 건너뛰지 말라"고 정했으므로 바꾸지 않았습니다. `docs/regression-environment.md`의 방법(로컬 커밋 `d38b0ca`의 detached clone을 `JOEWRKS_M6_PHASE_B_WORKTREE`로 지정)으로 증거를 주면 통과합니다. 그 설정으로 전체 1,267개: 실패 0·오류 0·건너뜀 6.
- 버전 2.0.1, 개인 오버레이 설치기 [`install_2_0_1.py`](evals/v2-tests-20261119/install_2_0_1.py)(BASE `89cb012`, 실행하지 않음).

**확인된 것**

- 새 테스트 `tests/test_first_plan_201.py`(3건)는 고치기 전 2건 실패, 고친 뒤 통과. 빈 템플릿 → rev2 OPEN → rev3 READY_FOR_REVIEW → `validate_state` 통과 → Approval Manifest 생성까지 스크립트만으로 갑니다.
- README 새 블록을 PowerShell 5.1에서 stdin으로 두 번 실행: 첫 번째 설치, 같은 폴더 두 번째는 clone 실패로 멈추고 설치하지 않음(URL은 로컬 저장소, 태그는 v2.0.0으로 바꿔 시험).
- `[Console]::OutputEncoding = [Text.Encoding]::UTF8`: 콘솔 인코딩 cp949에서 깨지던 변수 캡처가 정상이 됨(PowerShell 5.1.19041).
- 전체 테스트 결과는 준비 기록에 있습니다.

**확인되지 않은 것**

- 행동 시험 없음. 바뀐 것은 스크립트 동작과 참조 문서이며 SKILL.md와 `workflow-v0.2.0.md` 본문은 그대로입니다.
- 대화형 PowerShell 콘솔에 사람이 블록을 붙여 넣는 경우, Codex가 `skills\` 안의 백업 폴더를 중복 스킬로 읽는지, `install_2_0_1.py` 실제 실행.

**세션이 대신 내린 결정**

- D2는 (a) `open_revision`이 baseline을 세우는 방식 + (c) first-plan-guide 안내를 골랐습니다. READY_FOR_REVIEW 요청 자체가 "발견 절차를 마쳤다"는 작성자의 주장이고, 기존 `build_discovery_baseline.py`도 같은 주장(`procedure_complete: true`)을 조건 없이 적기 때문입니다. (b) finding pointer 보강은 (a) 뒤에 이 경로에서 그 finding이 나오지 않으므로 하지 않았습니다.
- D10은 guide 문장이 아니라 CLI를 고쳤습니다. guide와 예시(`discover-one-question`의 `evidence_refs: []`)가 맞고 필수 플래그가 틀렸기 때문입니다.

## 2.0.0 — 2026-11-19

게시: 사용자 승인("게시 ㄱㄱ", 2026-11-19, 부모 세션이 직접 받음) 뒤 태그 v2.0.0, GitHub Release, 개인 설치 overlay 갱신([install_2_0_0.py](evals/v2-release-20261119/install_2_0_0.py), 기록 [PERSONAL_INSTALL_RECORD.md](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)). 릴리스 노트 [release-notes-v2.0.0.md](evals/v2-release-20261119/release-notes-v2.0.0.md). 스킬 폴더는 `skills/joewrks-product-definition/VERSION` 한 파일만 1.7.3과 다르고 나머지 200개 파일은 바이트가 같습니다. 행동을 바꾸는 문장 변경이 없으므로 행동 시험은 하지 않았습니다. 기록은 [보고서](evals/v2-release-20261119/report.md)에 있습니다.

- (A) 저장소 정리: 참조 0건인 `.superpowers/…/continuation-task-a-report.md` 1개 삭제. 참조 0건인 `docs/superpowers/plans/*` 13개와 `evals/v0.1.*-results.md` 3개를 `evals/archive/2026-11-19-unreferenced/`로 이동(상대 경로 유지). 테스트가 고정하지 않은 7개 파일에서 홈 경로 9곳을 `~`로 가림. 테스트·`.gitattributes`가 바이트를 고정한 3개 파일의 4곳은 그대로 둠.
- (B) [`SECURITY.md`](SECURITY.md): 점검 항목과 수치, 남은 식별자(고정 파일, 이력, 커밋 메타데이터), 스크립트 신뢰 경계, 의존성, 보고 방법.
- (C) [`docs/QUICKSTART.md`](docs/QUICKSTART.md): Codex 일반 복사, 개인용 오버레이 설치기, Claude Code(clone + junction), 첫 실행, 검증, 투영 갱신·검사, 버전 고정, 설치 경로별 업그레이드, 제거. README를 350줄에서 147줄로 줄이고 "전용 설치기 없음" 문장을 고침. `PROGRAM_ARCHITECTURE.md`의 Repository mapping을 지금 트리에 맞춤.
- 개인 오버레이 설치기 [`install_2_0_0.py`](evals/v2-release-20261119/install_2_0_0.py)(BASE `ddf5c7e`; 게시 커밋을 TIP으로 실행).
- 게이트: 스킬 폴더 diff는 `VERSION` 1개 파일입니다. 전체 테스트는 1,264개 중 실패 3·오류 5·건너뜀 1이고, `v1.7.3` 태그를 다시 돌린 결과와 목록이 줄 단위로 같습니다(환경 원인 8건). `test_skill_package`·`test_friction_170`은 통과합니다.

## 1.7.3 — 2026-11-18

게시: 사용자 승인("게시(보정 포함)", 2026-11-18, 부모 세션이 직접 받음) 뒤 VERSION 1.7.3, 태그 v1.7.3, GitHub Release, 개인 설치 overlay 갱신([install_1_7_3.py](evals/2026-11-17-safety-sentence-172/install_1_7_3.py), 기록 [PERSONAL_INSTALL_RECORD.md](PERSONAL_INSTALL_RECORD.md)). 변경·재검사·한계는 [보고서](evals/2026-11-17-safety-sentence-172/report-173.md), 릴리스 노트 [release-notes-v1.7.3.md](evals/2026-11-17-safety-sentence-172/release-notes-v1.7.3.md).

- `projection_check.py`: 머리 영역의 꾸밈말 없는 승인 표기(`` > 승인: revision 1 (`dd1e837b…`) ``)를, 숫자가 state의 마지막 승인 revision과 같고 같은 줄(HTML은 같은 블록 요소)에 그 승인의 `approval_history[].manifest_digest` 앞 8자 이상이 함께 적혀 있을 때 더는 `stale_*_title_revision`으로 잡지 않습니다. digest가 없거나 다른 것이거나 7자 이하이면, 숫자가 마지막 승인과 다르면, 같은 줄에 현재 revision도 적혀 있으면 지금처럼 검출합니다. 보정(게시 전, 부모 세션): `<title>`·`<h1>`·Markdown `# ` 이름 줄은 digest가 있어도 문서 이름으로 읽어 지적을 유지합니다(흉내 위험 축소, 테스트 3건). 2026-11-17 안전 문장 시험 고정물의 5행 오탐이 사라지고 다른 결과는 같습니다. `next_action` 문구는 그대로입니다. 행동 효과는 아래 시험에서 따로 봤습니다.
- 사실 줄 보존 행동 시험(2026-11-18, Opus 4회 + 블라인드 채점 1회, 버전 누출 0/4, [보고서](evals/2026-11-18-fact-line-173/behavior-ab/report.md)): 지적이 사라진 1.7.3에서 5행 `` > 승인: revision 1 (`dd1e837b…`) ``을 원문 그대로 둔 run은 3/4입니다. 대조군인 11-17의 1.7.2 4회(재사용, 재실행 없음)는 1/4였습니다. 사전 기준상 "효과 있음"입니다. 2로 고친 run과 삭제한 run은 0/8입니다. 1/4는 지적이 없는데도 사실을 남긴 채 다시 썼습니다. 한계: 대조군이 다른 날 실행한 기록입니다. workflow 설명 변경과 검사 결과 변경의 몫을 나누지 못했습니다.

## 1.7.2 — 2026-11-15

게시: 사용자 승인("게시", 2026-11-15)으로 태그 `v1.7.2`(커밋 `6a74446a4e55d265cb385b4a25b6e617c13eadce`)과 [GitHub Release](https://github.com/JOEWRKS/JOEFLOW/releases/tag/v1.7.2)를 만들었습니다(Latest). 이후 커밋은 문서 기록뿐이며 태그 대상은 그대로 둡니다. 개인 설치본에는 같은 날 1.7.2를 반영했습니다(experience pass는 여전히 제외, `install_1_7_2.py`, [설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)); Claude Code용 클론도 같은 커밋으로 올렸습니다. 재현·범위·한계는 [보고서](evals/2026-11-15-stale-title-172/report.md), 릴리스 노트는 [release-notes-v1.7.2.md](evals/2026-11-15-stale-title-172/release-notes-v1.7.2.md).

- `projection_check.py`: 머리 영역에서 마지막 승인 revision을 사실대로 적은 문장("마지막 승인은 revision 1입니다", "마지막으로 승인된 것은 revision 1이다", "revision 1만 승인됨", "last approved: rev 1" 등)을 더는 `stale_*_title_revision`으로 잡지 않습니다. 숫자가 state의 마지막 승인 revision과 같을 때만 건너뛰고, 꾸밈말 없는 "승인 revision 1"·"Approved: rev 1"·"revision 1 (approved)"는 낡은 제목일 수 있어 그대로 검출합니다. 1.7.1 행동 시험의 오탐 2건(r1·r6)이 사라졌습니다.
- finding의 `next_action`에 "그 줄이 다른 revision(이전·마지막 승인)을 사실대로 적은 문장이면 고치지 말고 검사기 오탐으로 보고하라"는 문장을 더했습니다. 기존 "change revision X to Y by hand"는 그대로 있습니다.
- 행동 시험(2026-11-15, Opus 16회 + 블라인드 채점 2회, 저장소 밖 작업 폴더, 버전 누출 0/16, [보고서](evals/2026-11-15-stale-title-172/behavior-ab/report.md)): 낡은 손제목은 1.7.0 4/4(스스로)와 1.7.2 4/4(finding대로)가 고쳤습니다. 머리말 "승인 revision 1 기준…"을 숫자만 2로 바꿔 틀리게 만든 run은 1.7.1·1.7.2 모두 0/4였습니다. 1.7.2는 4/4가 "마지막 승인은 revision 1" 사실을 남겼고, 1.7.1은 4/4가 그 사실을 뺐습니다(3/4은 남겼다가 다시 걸린 뒤). 8/8이 그 문장을 낡은 문장으로 읽어 next_action 안전 문장은 시험되지 않았습니다(추가 필요).
- 안전 문장 행동 시험(2026-11-17, Opus 8회 + 블라인드 채점 1회, 버전 누출 0/8, [보고서](evals/2026-11-17-safety-sentence-172/behavior-ab/report.md)): 두 판 모두 지적하는 사실 머리말 `> 승인: revision 1 (dd1e837b…)`을 그대로 두고 오탐으로 보고한 run은 1.7.2 1/4, 1.7.1 0/4로 사전 기준상 "차이 없음"입니다. 숫자를 2로 바꾼 run은 0/8입니다. 1.7.2 3/4는 "마지막 승인은 revision 1"로 다시 써 사실을 남겼고, 1.7.1 4/4는 사실을 빼고 identity 블록 참조로 돌렸습니다. next_action과 workflow 설명이 함께 바뀌어 있어 둘의 몫은 나누지 못했습니다.

## 1.7.1 — 2026-11-15

게시: 사용자 승인("게시", 2026-11-15)으로 태그 `v1.7.1`(커밋 `f071560e563413468a4b6fbea7297f956521331c`)과 [GitHub Release](https://github.com/JOEWRKS/JOEFLOW/releases/tag/v1.7.1)를 만들었습니다(Latest). 이후 커밋은 문서 기록뿐이며 태그 대상은 그대로 둡니다. 개인 설치본에는 같은 날 1.7.1을 반영했습니다(experience pass는 여전히 제외, `install_1_7_1.py`, [설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)); Claude Code용 클론도 같은 커밋으로 올렸습니다. 재현·검출 범위는 [보고서](evals/2026-11-13-stale-title-171/report.md), 릴리스 노트는 [release-notes-v1.7.1.md](evals/2026-11-13-stale-title-171/release-notes-v1.7.1.md).

- `projection_check.py`: 투영 문서의 제목·머리 영역(HTML `<title>`와 첫 섹션 앞 header, Markdown 첫 `## ` 앞)에 적힌 revision(`revision N`, `rev N`, `Rev. N`, `개정 N`, `리비전 N` 등)이 `definition_revision`과 다르면 `stale_review_title_revision`·`stale_spec_title_revision`(줄·기대값·실제값·다음 행동)을 내고 ok false. 식별 블록이 현재여도 손제목의 낡은 "revision 0"이 통과하던 1.7.0 결함을 고쳤습니다. 본문 변경 이력, 주석, `rev 1→2` 범위, "이전 승인 rev N"은 읽지 않습니다. 기존 키는 그대로이고 `stale_title_revision` 목록만 더했습니다.
- 행동 시험(2026-11-15, Opus 8회 + 블라인드 채점 1회, [보고서](evals/2026-11-13-stale-title-171/behavior-ab/report.md)): 손제목을 고친 run은 B(1.7.1) 4/4가 finding대로, A(1.7.0) 4/4가 스스로였습니다. 이 장면에서는 차이가 없었습니다. 템플릿 본문이 비어 있었고 1.7.1 지식이 새어 들어가 장면이 오염됐기 때문입니다. 잘못 고친 경우는 0/8입니다. 머리말의 "마지막 승인은 revision 1"을 잡는 오탐 1종을 새로 찾았습니다(미수정).

## 1.7.0 — 2026-11-12

게시: 태그 `v1.7.0`(커밋 `ba15afe06c9338f2d240eb7d64a34a46925e91ad`)과 [GitHub Release](https://github.com/JOEWRKS/JOEFLOW/releases/tag/v1.7.0)를 2026-11-12에 만들었습니다(Latest). 이후 커밋은 문서 기록뿐이며 태그 대상은 그대로 둡니다. 개인 설치본에는 2026-11-12에 1.7.0을 반영했습니다(experience pass는 여전히 제외, `install_1_7_0.py`, [설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)).

오목 실사용 마찰(2026-11-11)과 세 도구 통합 시험. 재현·확인은 [보고서](evals/2026-11-12-friction-170/report.md). State 0.2.0, 고정 검증 모듈, 바인딩 계약은 바뀌지 않았습니다.

- 선택지·추천 검증 오류가 칸·값·이유를 말합니다(예: `options[1].id 'NONE' is a reserved non-answer word`). 예약어(`none, false, n/a, na, later, tbd`)는 `new_records.py`가 만들 때 거절하고 도움말·workflow에 적었습니다.
- `new_records.py`: `--recommend`는 `--reason`·`--tradeoff`가 필수, `--accepted`는 `--recommend`가 필수. `relayed --asked|--asked-summary`로 답한 질문을 남깁니다.
- 승인: 읽기 전용 `check_approval.py`. `record_approval.py --quote`·`--relayed-from`이 원문·전달 경로를 `joeflow-project.json`(state.json 옆)에 남기고 `approval_status.py`가 보여 줍니다. 전달 승인은 원문을 받은 세션이 기록하는 절차를 SKILL·workflow에 적었습니다.
- 판 고정: `joeflow_version.py [--pin]`, 새 `skills/joewrks-product-definition/VERSION`. 고정이 없거나 다르면 주요 명령이 `version_notice`로 알립니다. 스키마 거절 메시지가 찾은 판과 할 일을 말합니다.
- 통합 시험에서 찾은 것: `open_revision.py`가 READY_FOR_REVIEW에서 semantic readiness 실패 시 쓰지 않고 레코드를 이름으로 알립니다. `build_approval_manifest.py` 실패 출력에 `findings`. `update_projection.py`가 빈 블록·CRLF 블록을 알아봅니다. JOENESS·JOEDESIGN과 ID로 인계하는 문장을 더했습니다.

## 1.6.0 — 2026-11-01

개인 설치본에는 2026-11-01에 U2-8을 반영했습니다(experience pass는 여전히 제외, [설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)).

- U2-8(마무리): 전달된 사용자 의도의 근거 종류 `RELAYED_USER_INTENT`. `confidence` `DIRECT`(사용자 원문 그대로)만 직접 확인과 같고, 전달자의 요약은 material 질문을 닫거나 사용자 결정을 뒷받침하거나 모순 권위가 될 수 없습니다(`relayed_intent_cannot_close`). `new_records.py relayed --quote|--summary`. 전달 근거를 인용한 질문은 담당자 기본값으로도 닫을 수 없습니다(`relayed_intent_needs_user`). 고정 모듈 `state_validation_v2.py`와 스키마 enum 갱신, 기존 기록 영향 없음. 에이전트 A/B 12회: 규칙 없이는 요약을 사용자 결정으로 닫았고(2/2), 두 규칙 뒤에는 4/4가 질문을 사용자 답 대기로 남겼습니다([결과](evals/joeflow-u2-8-relayed-intent-ab/README.md)). 설계는 [U2-8](docs/u2-8-relayed-intent-design.md).

## 1.5.0 — 2026-10-31

개인 설치본에는 2026-10-31에 U2-10·U2-11을 반영했습니다(experience pass는 여전히 제외, [설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)).

- U2-10: 기존 제품에 기능을 더하는 절차 `references/feature-extension.md`와 `new_records.py baseline`. NEW_PRODUCT를 변경 범위로 한정하고, 유지할 기존 동작을 관찰 근거 + 기준선 요구사항(REQ·RULE·AC·SURF·Core 행, `default_authority`로 손글 3칸) 하나로 둡니다. 새 bootstrap 모드·표면 필드는 없습니다(스키마 버전이 바뀌면 승인이 모두 낡음). 측정은 [오목 rev 39](evals/joeflow-u2-10-feature-extension/README.md).
- U2-11: `surface_manifest.grill_profile.ASYNC.execution` = `LOCAL`·`LOCAL_PURE`(`references/grill-profile-inheritance-v1.json`)가 ASYNC 행의 polling·reconciliation(·idempotency·duplicate_execution) 축을 N/A로 암시해 생략할 수 있습니다. 오목의 손글 N/A 4축과 정확히 같고 승인본 digest는 그대로입니다([측정](evals/joeflow-u2-11-async-profile/README.md)). 고정 모듈 `authority_binding_v2.py`·`approval_v2.py` 해시 갱신. 설계는 [U2-10·U2-11](docs/u2-10-u2-11-design.md).

## 1.4.0 — 2026-10-31

개인 설치본에는 2026-10-31에 U2 전체를 반영했습니다(experience pass는 여전히 제외, [설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)).

U2 1·2·3단계와 U2-12. 계획은 [U2 계획](docs/u2-planning-gaps.md)과 [ROADMAP U2](ROADMAP.md)에 있습니다. 바인딩 계약 identity와 State 0.2.0은 바뀌지 않았습니다.

- U2-1: `update_projection.py`가 기획서·검토 화면의 식별 블록(revision·digest·변경 수·이전 승인)과 출처 블록을 다시 만들고, 바뀐 레코드를 적은 손글 줄을 알려 줍니다. 템플릿에 두 블록 표시를 넣었습니다.
- U2-2: 검토 화면 다이어그램이 작은 화면에서 글자를 줄이지 않고 가로로 스크롤됩니다.
- U2-3: DISCOVER·CLOSED 예제 state와 첫 기획 안내를 추가했습니다. `new_records.py user-decision|authoring --address CELL`이 답한 질문이 붙잡던 coverage 칸을 같은 패치에서 닫습니다.
- U2-4: 첫 기획 안내에 근거별 위치 표를 넣었습니다.
- U2-5·U2-7: native 정의가 OPEN인 동안 요구사항·화면을 coverage 행보다 먼저 둘 수 있습니다. READY_FOR_REVIEW부터는 빠진 행이 다시 오류입니다. 보호된 `authority_binding_v2.py`의 고정 해시를 갱신했습니다.
- U2-6: 담당자 기본값 결정(AGENT)을 그 질문과 함께 대체할 수 있습니다.
- U2-8: 관찰 사실(FACTUAL·BEHAVIORAL·CONSTRAINT)을 추천 근거로 쓸 수 있습니다.
- U2-12: 확정 칸 상속. 행동 행의 `shape`(`navigate`·`local_choice`·`toggle`·`submit`·`destructive`)가 해당 없는 축을, 요구사항·화면·행동 행의 `default_authority`가 적지 않은 축을 채웁니다. 적은 칸이 이깁니다. 검증·digest·다운스트림은 펼친 보기를 읽어 압축 상태와 펼친 상태의 digest가 같고, 두 필드가 없는 0.2.0 기록은 그대로 유효합니다. `compact_coverage.py`가 기존 행을 손실 없이 압축합니다(오목 38/202, WebAppDev 209/1,320). 고정 모듈 `authority_binding_v2.py`·`approval_v2.py` 해시 갱신. 설명 `references/coverage-inheritance.md`. 에이전트 A/B(12회)에서 `open_revision.py`의 `rows` 패치가 `shape`·`default_authority`를 버리던 결함을 찾아 고쳤고, `draft_freeze.py`가 모든 행동에 `shape: DECIDE`를 둡니다. 고친 뒤 4/4가 모양을 선언했으나 줄어든 칸은 6/113이고 `default_authority`는 쓰이지 않았습니다([A/B](evals/joeflow-u2-12-coverage-inheritance/agent-ab/README.md)). 모양 표를 실측으로 다시 정한 v2(`references/ux-action-shapes-v2.json`: `navigate` 7축, 신설 `browse`·`discard`, undo 제외)와 `draft_freeze.py --shape KEY=SHAPE`로 검증 4회에서 4/4가 같은 모양을 골라 손글 칸 113 → 96([측정](evals/joeflow-u2-12-coverage-inheritance/shapes-v2/README.md)).
- U2-9: `draft_freeze.py`가 빠진 coverage 행을 정확한 칸 목록으로 패치에 쓰고, 기록 그래프로 정해지는 칸(완료 기준·사용자·목표·흐름)만 채우며 나머지는 후보와 함께 `DECIDE`로 둡니다. 패치에 `rows`로 새 coverage 행을 넣을 수 있습니다. 오목 측정에서는 212칸 중 11칸만 정해져 효과가 작습니다([측정](docs/u2-9-light-freeze-design.md)).

## 1.3.0 — 2026-10-31

- U1-7: 계정 없는 앱의 UX 축 상속. `surface_manifest.grill_profile`의 `AUTH`·`PERMISSION`이 근거 있는 `N/A`이면 화면마다 계정·권한·세션 축(`unauthenticated`·`expired`·`session_expiration`·`permission_denied`·`permission`)을 생략할 수 있습니다. 적힌 칸은 그대로 검증하고, 바인딩 계약 파일과 state 스키마 0.2.0은 바뀌지 않았습니다. 고정 모듈 `authority_binding_v2.py`의 고정 해시를 사용자 승인으로 갱신했습니다. 설계는 [U1-7 설계](docs/u1-7-local-profile-design.md), 측정은 [오목 사본 측정](evals/joeflow-u1-7-ux-inheritance/gomoku-result.json)에 있습니다.

개인 설치본에는 2026-10-31에 U1-7을 반영했습니다(experience pass는 여전히 제외, [U1 설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)).

게시: 태그 `v1.3.0`(커밋 `016a60645d37b1381f9b8d9e7ad7bab82c0e6497`)과 [GitHub Release](https://github.com/JOEWRKS/JOEFLOW/releases/tag/v1.3.0)를 2026-10-31에 만들었습니다(Latest). 이후 커밋은 문서 기록뿐이며 태그 대상은 그대로 둡니다.

## 1.2.0 — 2026-10-30

오목(AI-Gomoku) 실사용 마찰 보강. 계획과 판정은 [ROADMAP U1](ROADMAP.md)에, 에이전트 행동 비교는 [승인 규칙 A/B](evals/joeflow-u1-approval-ab/REPORT.md)에 있습니다. State 0.2.0, 고정 검증 모듈, downstream 2.1 계약은 바뀌지 않았습니다.

- 2026-10-23: 기획 FREEZE 단계에 experience pass(여정·조작·작은 화면 정보 예산)를 추가했습니다. 개인 설치본에는 넣지 않았습니다.
- U1-1: 사람이 읽는 CLI 4개(`next_product_question`, `authority_binding_value`, `build_discovery_baseline`, `migrate_state`)의 출력을 UTF-8로 고정해 Windows cp949 파이프에서 생기던 `UnicodeEncodeError`와 글자 깨짐을 없앴습니다.
- U1-2: `record_approval.py`가 사용자가 승인한 revision·Manifest digest를 현재 state와 대조한 뒤 승인 기록, `approval_history`, `CLOSED`를 한 번에 씁니다.
- U1-3: `approval_status.py`가 승인된 revision, 승인 대기 revision, 따로 승인되지 않고 묶인 revision을 읽기 전용으로 보여 줍니다. SKILL·workflow의 APPROVE 단계가 두 명령을 쓰도록 바뀌었습니다.
- U1-4: `grill_v2.py` 오류(unknown 필드·형태, 추천 근거, 추천 수락, grill profile, EVIDENCE_RESOLVABLE 판정)가 틀린 조건과 허용·기대 값을 알려 줍니다. 고정된 검증 모듈의 오류에는 `explain_state_errors.py`가 힌트를 붙입니다.
- U1-5: `open_revision.py`가 작성자 패치로 다음 revision을 한 번에 열고, 패치한 레코드의 바인딩만 다시 해시하며, 검증을 통과할 때만 씁니다. `refresh_bindings.py`는 깨진 바인딩을 보여 주고 지정한 레코드만 갱신합니다.
- U1-6: `new_records.py`가 근거·질문·사용자 결정·작성 작업 레코드를 패치 파일에 만들어 넣습니다.
- U1-9: `supersede_records.py`가 레코드 대체를 패치에 넣으며, 현재 레코드의 참조와 커버리지 바인딩을 새 레코드로 옮깁니다.
- U1-2 보강: 사용자가 "승인"처럼 짧게 답하면 바로 앞에 보여 준 Manifest의 revision·digest로 승인을 기록합니다(`record_approval.py`가 다시 계산해 맞을 때만). 개정 패치 파일을 `state.json` 옆에 남기도록 권장합니다.
- U1-10: `projection_check.py`가 기획서·검토 화면이 현재 승인 revision·digest와 이번 개정의 새 레코드를 담고 있는지 읽기 전용으로 점검하고, `--draft`로 갱신 초안을 냅니다.

개인 설치본은 v1.1.0 위에 U1 변경만 반영했고 experience pass는 넣지 않았습니다(사용자 결정). 파일별 출처와 해시는 [U1 설치 기록](evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md)에 있습니다.

게시: 태그 `v1.2.0`(커밋 `62eb5418b84386f1e5fc5f6b6eeb48b08c4c6f59`)과 [GitHub Release](https://github.com/JOEWRKS/JOEFLOW/releases/tag/v1.2.0)를 2026-10-30에 만들었습니다(Latest). 이후 커밋은 문서 기록뿐이며 태그 대상은 그대로 둡니다.

## 1.1.0 — 2026-10-13

- 처음 사용하는 사람이 바로 설치하고 요청할 수 있도록 README를 여섯 개 핵심 절로 정리했습니다.
- JOENESS·JOEFLOW·JOEDESIGN의 역할과 실제 인계 순서를 같은 표현으로 연결했습니다.
- Product Definition 후보 사전검사와 사람이 읽는 planning projection 검사를 추가했습니다.
- 공통 구현 인계와 선택적 Figma 안내를 분리하고, 조건부 성공·실패·복구 의미 보존을 강화했습니다.
- Approval Manifest와 관련 CLI의 UTF-8 출력 경계를 보강했습니다.
- Windows checkout의 raw-byte 검사와 M6 역사적 replay를 재현하는 회귀 환경을 문서화했습니다.

검증 범위와 남은 경계는 [v1.1.0 검증 기록](evals/joeflow-v1.1.0/VERIFICATION.md)에 정리했습니다. 이후 승인된 개인 설치 결과는 [개인 설치 검증 기록](evals/joeflow-v1.1.0/PERSONAL_INSTALL_VERIFICATION.md)과 [전체 manifest receipt](evals/joeflow-v1.1.0/personal-install-receipt.json)에서 확인할 수 있습니다.

유지되는 경계:

- Runtime skill/package ID: `joewrks-product-definition`
- Native state contract: `0.2.0`
- Current downstream contract: `joewrks.action-conformance/2.1`
- Semantic review reliability: `NOT_MEASURED`
- Historical frozen contracts and evidence are unchanged.

## 1.0.0 — 2026-09-27

- `JOEFLOW` 프로그램 이름과 `joewrks-product-definition` runtime skill ID를 분리했습니다.
- Native State 0.2.0 lifecycle과 downstream 2.1 handoff를 기본 설치 경로로 연결했습니다.
- `MASTER_PLANNING_SPEC.md`와 `planning-review-core.html`을 기본 사람용 전달 산출물로 추가했습니다.
- Legacy 0.1.2.1과 historical 1.0/2.0 contract compatibility를 보존했습니다.
