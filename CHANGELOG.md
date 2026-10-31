# JOEFLOW 변경 기록

프로그램 릴리스 기록입니다. State, schema, action contract, semantic-review 같은 런타임 identity는 프로그램 버전과 별도로 호환성을 관리합니다.

## 1.4.0 — 2026-10-31

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
