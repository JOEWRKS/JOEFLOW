# JOEFLOW 프로그램 구조

## 1. 핵심 요약

- 프로그램 이름: **JOEFLOW**
- 적용 범위: Product Definition, downstream conformance, semantic review, evaluation 도구의 통합 운영
- 런타임 skill/package ID: **`joewrks-product-definition`** 유지
- 런타임 ID rename: 미수행

| 항목 | 값 |
| --- | --- |
| 프로그램 이름 | `JOEFLOW` |
| 프로그램 릴리스 | `v1.5.0` |
| 저장소 | `JOEWRKS/JOEFLOW` |
| 런타임 skill/package ID | `joewrks-product-definition` |
| canonical Product Definition authority | `product-definition/<project-slug>/state.json` |
| 현재 Product Definition 상태 계약 | `0.2.0` |
| 현재 downstream authority 계약 | `joewrks.action-conformance/2.1` |
| 현재 semantic-review 경계 | `joewrks.semantic-review/2.1` / reliability `NOT_MEASURED` |
| repaired v0.4.3 calibration input | `748254d6def81080a2fd2736115a3ab5e0bde5a3` |
| v0.4.3 environment-blocked disposition | `6a0674c5d00a40790afef78cfa19494314b894e3` |

설치된 routing marker:

```text
PRODUCT_DEFINITION_STATE_V2_DEFAULT
LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED
DOWNSTREAM_V2_INSTALLED_ROUTING
SEMANTIC_REVIEW_V2_RELIABILITY_NOT_MEASURED
```

- 현재 Product Definition 상태 계약: `0.2.0`
- 현재 V2 downstream authority 계약: `joewrks.action-conformance/2.1`
- 현재 V2 semantic-review 경계: `joewrks.semantic-review/2.1` / reliability `NOT_MEASURED`
- 과거 호환성: 상태 `0.1.2.1`, `joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, v0.4.3 evidence
- 계약 버전: 상호 독립 관리
- 이 기준선의 전체 프로그램 릴리스: `v1.5.0`

## 2. 설계 목적

- 구현 전 중요한 제품·UX 모호성 해소
- 확정 결정을 명시적 authority로 보존
- 승인 내용을 downstream 구현 의무로 컴파일
- 구현 의미 drift 탐지
- semantic interpretation의 반복 신뢰 가능성 평가
- 운영 구조: 결정 확정·구현 인계·검증의 단계별 체계

비대체 범위:

- 사용자 승인
- 실제 제품 구현
- Product Definition authority를 대신하는 review 결과

## 3. 주요 기능

```text
JOEFLOW
│
├─ 1. Product Definition Core
│  ├─ state contract 0.2.0 (installed default)
│  ├─ evidence discovery
│  ├─ Product Surface + Evidence + Contradictions
│  ├─ unknown / Materiality / decision authority
│  ├─ canonical state.json authority
│  ├─ requirements / rules / data / flows / screens / states
│  ├─ Core + specialist Grill coverage bindings
│  ├─ Approval Manifest + definition digest
│  └─ deterministic Semantic Closure Gate
│
├─ 2. Downstream Conformance
│  ├─ joewrks.handoff-definition/2.1 → joewrks.action-conformance/2.1
│  ├─ exact M4 source seeds + scope commitments
│  ├─ DIRECT_AUTHORITY / MACHINE_DERIVED / REVIEW_REQUIRED
│  ├─ hard SEMANTIC_AUTHORITY_GAP re-entry
│  ├─ implementation / Figma handoff obligations
│  └─ dependency-scoped audit
│
├─ 3. Semantic Review
│  ├─ joewrks.semantic-review/2.1 only for REVIEW_REQUIRED obligations
│  ├─ only legitimate REVIEW_REQUIRED obligations
│  ├─ exact obligation/value binding
│  ├─ assurance, never Product Definition authority
│  └─ reliability NOT_MEASURED
│
└─ 4. Evaluation & Calibration Harness
   ├─ behavioral / dogfood evaluations
   ├─ official calibration controller
   ├─ calibration control plane
   ├─ frozen raw-output evidence
   ├─ disagreement / reliability metrics
   └─ isolated reviewer execution boundary
```

과거 State `0.1.2.1`, downstream v1, semantic-review/1.0, frozen execution transport, v0.4.3 evidence의 원래 identity 유지. 설치된 V2 기본값과 구분되는 compatibility boundary로 유지.

### Product Definition Core

- 불완전한 제품 요청을 검토 가능한 명시적 authority로 전환
- 중요한 제품 결정의 묵시적 생성 금지
- 미결정 사항의 unknown 등록
- 명시적 답변의 decision 기록
- 중요 변경의 requirement·flow·screen·state·rule·acceptance criterion·implementation mapping 전파
- canonical authority: `product-definition/<project-slug>/state.json`
- Markdown PRD·plan·wireflow·handoff·summary: state의 projection으로만 사용

현재 core lifecycle:

```text
DISCOVER
→ CLOSE
→ FREEZE
→ APPROVE
→ HANDOFF
→ VERIFY
```

Semantic Closure 필수 조건:

- deterministic validation
- 정확한 coverage-to-authority binding
- 일치하는 Approval Manifest와 definition digest
- 현재 definition revision에 대한 명시적 승인
- 구현 완료 주장 금지

### Downstream Conformance

- Product Definition Closure 이후 승인된 canonical clause를 실행 가능한 downstream obligation으로 컴파일
- 현재 V2 handoff contract: `joewrks.action-conformance/2.1`
- exact M4 coverage binding의 source seed 재사용
- consumed seed와 authority scope identity 고정
- semantic authority gap이 0인 handoff만 materialize
- Product authority와 implementation behavior 분리
- Direct authority와 closed deterministic derivation 분리
- Legitimate qualitative review와 upstream authority gap 분리
- Global definition state와 dependency-local contract validity 분리
- consumer working directory와 무관한 installed wrapper 실행
- persistent `PYTHONPATH` 요구 없음
- Product Definition authority에 대한 read-only 유지
- 과거 `joewrks.action-conformance/1.0`의 frozen·reproducible contract 유지

### Semantic Review

- Structured Product Definition authority 또는 closed derivation으로 안전하게 표현할 수 없는 downstream field만 대상
- Responsibility profile이 허용한 field만 `REVIEW_REQUIRED` 유지
- V2 sidecar: `joewrks.semantic-review/2.1`
- Exact action contract·source obligation·proposed value hash·responsibility rule binding
- Review output: assurance evidence 및 read-only affected-scope re-entry 가능
- Product Definition 또는 action contract 수정 금지
- semantic-review/2.1 reliability: `NOT_MEASURED`
- v0.4.3 calibration disposition 또는 semantic-review/1.0 reliability claim 상속 금지
- 과거 `joewrks.semantic-review/1.0`, **26 action + 12 lifecycle = 38** responsibility rule, v0.4.3 evidence의 frozen compatibility 유지

Terminal review outcome:

```text
APPROVED
REJECTED_CANDIDATE
RUBRIC_ERROR
INPUT_PACKAGE_ERROR
```

- Reliability gate: conjunctive
- Majority vote escape hatch: 없음

### Evaluation & Calibration Harness

- Fresh execution에서의 일관성 측정
- Deterministic unit test 통과와의 분리
- Behavioral A/B evaluation
- End-to-end dogfood
- Downstream-conformance experiment
- Semantic-review golden calibration
- Official calibration controller
- Raw-output freeze 및 evidence binding
- Reliability statistic 및 disagreement classification
- Valid real calibration: reviewer context가 assigned package·run envelope·invocation wrapper만 접근 가능한 환경 필요
- Isolation enforcement: reviewer instruction이 아닌 execution environment 책임

## 4. 사용 방법

### 설치·시작

- 설치 절차와 최초 요청: [README 사용 방법](README.md#4-사용-방법) 기준
- canonical authority 생성·재개: `product-definition/<project-slug>/state.json` 기준
- 적용 계약 선택: state version과 현재 lifecycle 기준
- 과거 계약의 자동 migration 금지

### End-to-end authority flow

```text
Vague idea / evidence
        ↓
Product Definition Core
        ↓
canonical state.json
        ↓
Semantic Closure + exact approval
        ↓
Downstream V2 compiler
        ↓
handoff-definition/2.1 → action-conformance/2.1 contract
        ↓
Implementation / Figma Make
        ↓
dependency audit + implementation evidence
        ↓
semantic-review/2.1 for legitimate REVIEW_REQUIRED fields
        ↓
re-entry for affected authority gaps or ambiguity
```

- 구현 중 발견된 중요 모호성: downstream 묵시 결정 금지, Product Definition 재진입

### Repository mapping

```text
skills/joewrks-product-definition/
├─ SKILL.md                         # Product Definition entrypoint
├─ references/                      # authority and workflow rules
├─ schemas/                         # canonical schemas
├─ templates/                       # generated projection templates
├─ scripts/                         # validators + installed V2 wrappers
├─ downstream_v2/                   # frozen action-conformance/2.0 authority
├─ downstream_v21/                  # frozen current 2.1 semantic/package authority
├─ integration_v2/                  # M6 runtime verifier/report outside frozen packages
└─ downstream/                      # historical v1 compatibility
   ├─ contracts.py                  # downstream contract compilation
   ├─ provenance.py                 # source binding
   ├─ verifier.py / invariants.py   # runtime conformance
   ├─ protocol.py                   # execution protocol
   ├─ adapters/                     # runtime adapters
   └─ semantic_review/              # v0.4.3 semantic-review core

evals/
├─ behavioral-v0.2/                 # behavioral evaluation
├─ downstream-conformance-v0.4*/    # downstream experiments/evidence
└─ semantic-review-v0.4.3/          # semantic-review spec/calibration/evidence

tests/
└─ fixtures/semantic-review-v1/     # frozen golden packages/oracle fixtures
```

## 5. 도구 간 연결

- JOENESS: 작업 순서·진행 상태·완료 근거 관리
- JOEFLOW: 요구사항·규칙·예외·완료 기준 확정
- JOEDESIGN: 화면 제작·시각 기준 수립·디자인 검수
- Implementation/Figma Make: 승인된 downstream obligation 소비
- Semantic Review: legitimate `REVIEW_REQUIRED` field의 assurance
- Evaluation Harness: fresh execution의 일관성·신뢰성 측정

버전 진행 기록:

- **v0.1.x** — deterministic Product Definition authority, state contract, Closure Gate
- **v0.2** — behavioral interrogation refinement와 A/B evaluation
- **v0.3.x** — end-to-end dogfood, Figma/Figma Make handoff, drift auditing
- **v0.4 / v0.4.1.x** — cross-domain downstream conformance와 executable action-contract authority
- **v0.4.2** — fresh downstream-contract efficacy experiment, review-construction instability로 paired result 전 중단
- **v0.4.3** — deterministic semantic-review contract, responsibility model, reliability gate, calibration controller, control-plane hardening
- **v1.0.0** — native State 0.2.0 lifecycle, downstream 2.1 handoff, dogfood-proven human delivery output, conditional-branch preservation rule
- **v1.1.0** — unified JOE tool handoff language, candidate/preflight 및 projection check, UTF-8 manifest output, reproducible Windows regression preparation; frozen contract identity 변경 없음
- **v1.2.0** — experience pass, UTF-8 CLI 출력, 승인 기록·승인 현황, 오류 허용 값 힌트, 패치 기반 revision 개정·대체 연쇄·레코드 작성 CLI; frozen contract identity 변경 없음
- **v1.3.0** — 계정 없는 앱의 UX 축 상속(grill profile `AUTH`·`PERMISSION` N/A이면 계정·권한·세션 UX 축 생략 가능); 바인딩 계약 identity·State 0.2.0 변경 없음, 보호된 `authority_binding_v2.py` 고정 해시 갱신
- **v1.4.0** — U2 기획 보강: 기획서·검토 화면 식별·출처 블록 갱신 도구, OPEN 동안 coverage 행 유예, 담당자 기본값 대체, 관찰 사실 추천 근거, 빠진 coverage 행 초안(`draft_freeze.py --shape`), 행동 `shape`(실측 모양 표 v2)·행 `default_authority`로 확정 칸 상속과 손실 없는 압축(`compact_coverage.py`); State 0.2.0·바인딩 계약 identity 변경 없음, 보호된 `authority_binding_v2.py`·`approval_v2.py` 고정 해시 갱신
- **v1.5.0** — 기존 제품에 기능 추가(`feature-extension.md`, `new_records.py baseline`: 유지할 기존 동작을 기준선 요구사항으로), ASYNC 로컬 실행 프로필(`grill_profile.ASYNC.execution`으로 ASYNC 행 축 생략); State 0.2.0·바인딩 계약 identity 변경 없음, 보호된 `authority_binding_v2.py`·`approval_v2.py` 고정 해시 갱신

## 6. 한계

### Historical v0.4.3 calibration boundary

| 경계 | 상태 |
| --- | --- |
| v0.4.3 specification | `VERIFIED` |
| semantic-review implementation | `VERIFIED` |
| calibration control plane | `VERIFIED_AFTER_RUN_01_REPAIR` |
| Run-01 | `INVALID / CONTROL_PLANE_DEFECT` |
| valid real calibration runs | `0` |
| real reviewer reliability | `NOT_MEASURED` |
| calibration PASS | `NOT_CLAIMED` |
| calibration FAIL | `NOT_CLAIMED` |
| current blocker | `MANIFEST_ONLY_ISOLATION_UNAVAILABLE` |
| v0.4.4 | `BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION` |

- Frozen historical status: calibration PASS보다 좁은 범위
- Current V2 contract identity의 정의로 사용 금지
- Capability probe 결과: 현재 collaboration/Codex 환경에서 repository-side Run-01 evidence 접근 가능
- Package-only reviewer isolation의 사실상 증명 불가
- 환경 제한으로부터 semantic defect 또는 rubric defect 추론 금지

### Historical calibration execution boundary

- 다음 valid real calibration의 선행 조건: isolated reviewer runner proof
- Fresh reviewer context 허용 범위: assigned package와 envelope
- Fresh reviewer context 금지 범위: repository, Run-01 evidence, golden answer, seed oracle, prior output, sibling package
- Isolation runner 역할: 시스템 외곽 infrastructure
- Product Definition authority 전환 금지
- 환경 충족 목적의 semantic-review core 수정 금지
