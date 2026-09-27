# JOEFLOW

> **AI가 중요한 걸 빠뜨리거나 제멋대로 결정하지 않게 해주는 제품 기획·검증 도구입니다.**
>
> **A product planning and verification tool that keeps AI from guessing important decisions.**

만들고 싶은 것을 AI에게 바로 구현시키기 전에, 먼저 **빠진 것과 애매한 것을 찾아 확실하게 정리**합니다.

자료를 보고 확인할 수 있는 것은 AI가 먼저 조사하고, **사람의 판단이 꼭 필요한 중요한 결정만 질문**합니다. 한번 정한 내용은 프로젝트의 기준으로 기록하고, 이후 Codex 같은 구현 AI가 그 기준대로 만들게 합니다. 마지막에는 실제 결과물이 처음 정한 내용과 달라지지 않았는지도 확인합니다.

핵심 원칙은 간단합니다.

> **AI가 알아서 만들게 하되, 중요한 건 멋대로 정하지 못하게 한다.**

현재 프로그램 릴리스는 **`v1.0.0`**입니다. 런타임 skill/package ID는 호환성을 위해 **`joewrks-product-definition`**을 유지합니다.

---

## 이 도구가 하는 일

전체 흐름은 네 단계로 이해하면 됩니다.

### 1. 빠진 걸 찾습니다

요청에 적혀 있지 않은 중요한 조건, 예외, 상태, 권한, 실패 상황, 복구 방법 등을 찾습니다.

예를 들어 사용자가 단순히 “회원가입 기능이 필요해”라고 말해도 내부적으로는 다음 같은 회색지대를 확인할 수 있습니다.

- 이메일 인증이 필요한가?
- 인증 전 로그인은 가능한가?
- 같은 이메일로 다시 가입할 수 있는가?
- 인증 메일이 실패하면 어떻게 복구하는가?
- 계정 삭제 후 데이터는 어떻게 처리하는가?

중요한 점은 **이 질문을 전부 사용자에게 한꺼번에 던지지 않는다는 것**입니다.

### 2. 애매한 걸 확실하게 합니다

AI가 먼저 코드, 문서, 테스트, API, 디자인, 기존 동작 같은 자료를 조사합니다.

- 자료에서 답을 확인할 수 있으면 사용자에게 묻지 않습니다.
- 사소하고 쉽게 되돌릴 수 있는 구현 세부사항은 허용된 범위 안에서 AI가 처리합니다.
- 제품 결과가 달라지는 중요한 결정만 사용자에게 가져옵니다.
- 한 번에 가장 중요한 질문 하나씩만 묻습니다.

즉 **내부적으로는 꼼꼼하게 파고들고, 사용자에게는 필요한 것만 보여주는 방식**입니다.

### 3. 정한 대로 만들게 합니다

결정된 내용은 채팅 기억이 아니라 다음 파일에 프로젝트 기준으로 저장합니다.

```text
product-definition/<project-slug>/state.json
```

이 파일이 Product Definition의 기준입니다.

Codex 같은 구현 AI는 이 기준을 따라 구현합니다. 구현 중 새로운 중요한 애매함을 발견하면 임의로 정하지 않고 Product Definition으로 다시 돌아옵니다.

### 4. 제대로 만들었는지 확인합니다

구현이 끝난 뒤에는 처음 정한 요구사항과 실제 결과를 비교합니다.

- 요구사항이 빠졌는가?
- 화면 상태가 빠졌는가?
- 권한이나 실패 처리가 달라졌는가?
- 구현 과정에서 제품 의미가 바뀌었는가?
- 승인한 디자인이나 동작과 실제 결과가 다른가?

필요한 부분은 downstream conformance와 drift audit으로 더 강하게 검증할 수 있습니다.

---

## 이 도구가 대신하지 않는 것

이 시스템은 모든 일을 혼자 하는 올인원 제작 도구가 아닙니다.

직접 대신하지 않는 영역:

- 실제 production 코드를 작성하는 구현 AI의 역할
- 디자이너의 최종 미감·아트디렉션 판단
- 배포 인프라 운영
- 법률·보안·회계 등 전문적인 최종 승인

역할을 단순하게 나누면:

```text
JOEFLOW
        ↓
무엇을 만들어야 하는지 확실하게 정함
        ↓
Codex / 구현 AI
        ↓
정해진 내용을 실제로 만듦
        ↓
JOEWRKS 검증
        ↓
처음 정한 내용과 달라지지 않았는지 확인
```

---

## 언제 쓰면 좋은가

다음과 같은 작업에 특히 적합합니다.

- 새 웹사이트나 웹앱 기획
- 기존 사이트 리뉴얼
- Codex가 이미 어느 정도 만든 프로젝트 정리
- 여러 화면과 상태가 연결되는 UX
- 로그인, 권한, 저장, 삭제, 제출 같은 상태 변화가 있는 기능
- 결제, 예약, 외부 API 같은 실수 비용이 큰 흐름
- Figma / Figma Make로 넘기기 전 제품 정의
- 구현 이후 요구사항과 실제 결과의 차이 확인

---

## 설치

현재 전용 installer, package manager 명령, 공개 plugin package는 없습니다.

저장소 안의 skill 디렉터리를 **통째로** 설치해서 사용합니다.

### 1. 저장소 받기

```bash
git clone https://github.com/JOEWRKS/JOEFLOW.git
cd JOEFLOW
```

특정 branch나 commit을 사용할 경우 먼저 checkout 합니다.

### 2. Skill 디렉터리 전체 설치

아래 디렉터리를 사용하는 Codex / Agent Skills 환경의 Skills 위치에 그대로 복사하거나 설치합니다.

```text
skills/joewrks-product-definition/
```

`SKILL.md`만 따로 복사하면 안 됩니다.

```text
skills/joewrks-product-definition/
├─ SKILL.md
├─ references/
├─ schemas/
├─ templates/
├─ scripts/
├─ downstream/       # historical 1.0 compatibility
├─ downstream_v2/    # historical 2.0 compatibility
└─ downstream_v21/   # current 2.1 downstream authority
```

정확한 설치 경로는 사용하는 Codex/Agent 환경의 Skills 설치 방식에 맞춥니다.

Skill entrypoint:

```text
skills/joewrks-product-definition/SKILL.md
```

Skill ID:

```text
joewrks-product-definition
```

---

## 빠른 시작 — 새 프로젝트

구현 전에 다음처럼 요청합니다.

```text
Use joewrks-product-definition for this project.

이 프로젝트를 구현하기 전에 Product Definition부터 진행해.
먼저 현재 사용할 수 있는 자료를 조사해.
빠지거나 애매한 중요한 부분은 unknown으로 등록하고,
자료로 해결할 수 있는 것은 먼저 직접 확인해.
사람의 결정이 필요한 중요한 문제만 한 번에 하나씩 물어봐.

product-definition/<project-slug>/state.json을 기준으로 만들고,
Product Definition Closure와 내 승인이 끝나기 전에는 구현을 시작하지 마.
```

흐름:

```text
아이디어
→ 자료 조사
→ 빠진 것 찾기
→ 중요한 결정 정리
→ 요구사항 / 흐름 / 화면 / 상태 확정
→ Closure
→ 사용자 승인
→ 구현 handoff
→ Codex 구현
→ 결과 검증
```

---

## 빠른 시작 — 이미 만들어진 사이트나 앱

기존 코드가 있다고 해서 현재 동작을 곧바로 “원래 의도”라고 간주하면 안 됩니다.

먼저 **reverse Product Definition**을 진행합니다.

```text
Use joewrks-product-definition for this existing project.

아직 코드는 수정하지 마.
현재 repository, 문서, 테스트, 화면, 동작을 evidence로 조사해.

현재 구현에서 발견한 내용을 다음처럼 구분해:
1. 원래 의도였다고 확인되는 것
2. 구현에는 있지만 의도인지 확인되지 않은 것
3. 문서/의도와 구현이 충돌하는 것
4. 이유를 알 수 없는 것

현재 구현이 존재한다는 이유만으로 Product Definition의 정답으로 만들지 마.
애매한 중요한 부분을 먼저 정리한 뒤 구현 작업으로 넘어가.
```

이 방식은 AI가 이전 구현 과정에서 임의로 추가한 결정을 찾아낼 때 특히 유용합니다.

---

## 중요한 회색지대를 다루는 방식

이 시스템의 핵심은 **질문을 많이 하는 것**이 아닙니다.

목표는:

> **중요한 회색지대를 최대한 찾아내되, 사용자가 직접 결정해야 하는 것만 물어보는 것.**

현재 Product Definition Core는 다음 원칙을 사용합니다.

- evidence를 먼저 조사합니다.
- independently answerable한 중요한 결정을 각각 별도 unknown으로 관리합니다.
- 여러 정책을 하나의 애매한 질문으로 뭉개지 않습니다.
- security / money / privacy / irreversible decision처럼 위험도가 큰 것을 우선합니다.
- 영향 범위가 큰 질문을 먼저 해결합니다.
- 답을 받으면 관련 항목을 다시 확인하고 새로운 unknown이 생겼는지 재탐색합니다.
- 하나의 중요한 질문만 사용자에게 보여줍니다.

---

## Canonical Product Definition

프로젝트의 Product Definition 기준은 항상:

```text
product-definition/<project-slug>/state.json
```

입니다.

Markdown PRD, wireflow, handoff, summary는 사람이 보기 쉬운 출력물일 뿐 `state.json`을 대체하지 않습니다.

예:

```text
my-site/
├─ src/
├─ public/
└─ product-definition/
   └─ my-site/
      ├─ state.json
      └─ generated projections...
```

---

## v1 기본 전달 산출물

승인이 끝난 Product Definition은 내부 상태 파일만 남기고 종료하지 않습니다. 후속 디자인·구현 에이전트와 사람이 각각 바로 소비할 수 있도록 두 개의 기본 전달물을 만듭니다.

- `MASTER_PLANNING_SPEC.md` — 승인된 제품 의미를 한 파일에서 끝까지 읽을 수 있는 완전한 사람용 기획 명세. 후속 디자인·구현 에이전트의 기본 읽기 문서입니다.
- `planning-review-core.html` — 제품 목표, 범위, IA, 주요 화면, 핵심 흐름·분기, 중요 제한, 승인 상태를 빠르게 검토하는 축약 시각본입니다.

두 파일은 승인된 `state.json`의 projection이며 독립 authority가 아닙니다. Core HTML의 색·배치·스타일도 후속 제품 디자인의 visual reference가 아닙니다.

요약 과정에서 조건을 잃으면 안 됩니다. 특히 조건부 성공·실패·복구를 하나의 보편 결과로 압축하지 않고, 정상/예외/복귀 분기를 승인된 stable ID와 연결해 보존합니다. HTML 렌더를 실제로 확인하지 못했으면 `NOT_VERIFIED`라고 기록합니다.

---

## 현재 설치된 계약 라우팅

새 프로젝트는 State `0.2.0` 네이티브 템플릿으로 시작합니다. 기존 `0.2.0` 프로젝트는 그대로 재개하고, 기존 `0.1.2.1` 프로젝트는 동결된 레거시 계약으로 먼저 검증합니다. 사용자가 V2 채택을 명시적으로 요청하지 않으면 자동 마이그레이션하지 않습니다.

```text
PRODUCT_DEFINITION_STATE_V2_DEFAULT
LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED
DOWNSTREAM_V2_INSTALLED_ROUTING
SEMANTIC_REVIEW_V2_RELIABILITY_NOT_MEASURED
```

Current Product Definition state contract: `0.2.0`

Current V2 downstream authority contract: `joewrks.action-conformance/2.1`

Current V2 semantic review boundary: `joewrks.semantic-review/2.1` / reliability `NOT_MEASURED`

Historical compatibility: state `0.1.2.1`, `joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, and v0.4.3 evidence

설치된 전체 V2 흐름과 명령은 [`workflow-v0.2.0.md`](skills/joewrks-product-definition/references/workflow-v0.2.0.md)에 정리되어 있습니다. 새 프로젝트 템플릿의 `migration.mode`는 `NATIVE`이며, 템플릿 자체는 Closure, 사용자 승인, 승인 시각, downstream authority를 주장하지 않습니다.

---

## 더 강한 동작 검증이 필요한 경우

Product Definition Closure 이후 중요한 상태 변화나 business behavior는 Downstream Conformance로 검증할 수 있습니다.

현재 V2 downstream authority contract:

```text
joewrks.action-conformance/2.1
```

설치된 skill 경로를 기준으로 다음 wrapper를 실행합니다. consumer 프로젝트의 현재 디렉터리나 영구 `PYTHONPATH` 설정에 의존하지 않습니다.

```text
python <skill-directory>/scripts/compile_downstream_v2.py STATE_JSON HANDOFF_DEFINITION_JSON
python <skill-directory>/scripts/audit_downstream_v2.py CONTRACT_JSON STATE_JSON
python <skill-directory>/scripts/build_semantic_review_v2.py CONTRACT_JSON
```

`build_semantic_review_v2.py`는 정당한 `REVIEW_REQUIRED` 의미가 있을 때만 `joewrks.semantic-review/2.1` 패키지를 만듭니다. 이 review 계약의 reliability는 `NOT_MEASURED`이며, review 결과는 Product Definition authority를 만들지 않습니다. 현재 2.1 흐름은 `joewrks.runtime-conformance-plan/1.0`과 frozen `joewrks.downstream.execution/1.0` evidence를 `joewrks.runtime-evidence-bundle/1.0`으로 묶고, `verify_runtime_v21.py`로 계획·번들·필요 시 검증된 review package/output을 함께 재검증하여 `joewrks.runtime-conformance-report/1.0` evidence를 만듭니다. `verify_runtime_v2.py`는 역사적 2.0 계약 전용입니다.

특히 다음 같은 영역에 적합합니다.

- 로그인 / 계정 / 권한
- 폼 제출과 validation
- 저장 / 삭제 / 상태 변경
- 결제 / 예약
- retry / failure recovery
- 외부 API side effect
- business state transition

단순한 hero, 이미지 갤러리, footer 같은 표현 중심 영역까지 무조건 적용할 필요는 없습니다.

V2 계약과 historical v1 호환성:

- [`skills/joewrks-product-definition/references/downstream-v2-contract.md`](skills/joewrks-product-definition/references/downstream-v2-contract.md)
- [`skills/joewrks-product-definition/downstream/README.md`](skills/joewrks-product-definition/downstream/README.md) — historical `joewrks.action-conformance/1.0`

---

## 디자인과 Figma

이 시스템은 다음 같은 디자인 요구사항을 정의하고 고정할 수 있습니다.

- 화면의 목적
- 정보 우선순위
- visual hierarchy
- responsive 동작
- component state
- interaction behavior
- accessibility requirement
- stable screen ID와 구현 mapping

다만 “어느 구도가 더 예쁜가”, “어떤 크롭이 더 감각적인가” 같은 순수 미감 판단을 deterministic하게 증명하는 도구는 아닙니다.

승인된 디자인이 있다면 그 디자인을 구현 기준으로 사용하고 이후 drift를 확인할 수 있습니다.

---

## Validation

Canonical state 검증:

```bash
python /absolute/path/to/joewrks-product-definition/scripts/validate_state.py path/to/state.json
```

Closure 검증:

```bash
python /absolute/path/to/joewrks-product-definition/scripts/validate_closure.py path/to/state.json
```

저장소 전체 테스트:

```bash
python -m unittest discover -s tests -v
```

Script 경로는 consumer project가 아니라 **설치된 skill 디렉터리**를 기준으로 잡습니다.

---

## Historical v0.4.3 calibration boundary

v0.4.3은 현재 V2 설치 라우팅의 전체 프로그램 릴리스 번호가 아니라, 동결된 historical semantic-review/1.0 calibration evidence 경계입니다.

| 항목 | 상태 |
| --- | --- |
| v0.4.3 specification | `VERIFIED` |
| semantic-review implementation | `VERIFIED` |
| repaired calibration control plane | `VERIFIED_AFTER_RUN_01_REPAIR` |
| Run-01 | `INVALID / CONTROL_PLANE_DEFECT` |
| valid real calibration runs | `0` |
| real reviewer reliability | `NOT_MEASURED` |
| calibration PASS | `NOT_CLAIMED` |
| calibration FAIL | `NOT_CLAIMED` |
| current blocker | `MANIFEST_ONLY_ISOLATION_UNAVAILABLE` |
| v0.4.4 | `BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION` |

따라서 현재 deterministic Product Definition / Closure / handoff / downstream-conformance / drift-audit 계층은 각 검증된 계약 범위에서 사용할 수 있습니다.

반면 real semantic-review reliability는 유효한 isolated calibration이 완료되기 전까지 production-calibrated evidence라고 주장하지 않습니다.

Program release tag:

```text
v1.0.0
```

Repaired calibration input:

```text
748254d6def81080a2fd2736115a3ab5e0bde5a3
```

Environment-blocked disposition:

```text
6a0674c5d00a40790afef78cfa19494314b894e3
```

---

## 현재 Core 계약 — Semantic Closure V2

State `0.2.0` Product Definition Core와 downstream V2 authority는 설치된 skill workflow에서 기본 경로로 연결됩니다. 현재 경로는 `joewrks.action-conformance/2.1` → `joewrks.runtime-conformance-plan/1.0` → frozen `joewrks.downstream.execution/1.0` evidence → `joewrks.runtime-conformance-report/1.0` 순서입니다. 승인된 bounded M6 dogfood는 이 경로에서 full-contract conformance를 기록했지만, full historical migration은 여전히 `OPEN`이고 semantic-review/2.1 reliability는 `NOT_MEASURED`입니다. 최종 repository regression/review와 merge/deployment 전에는 전체 M6 완료를 주장하지 않습니다.

목표는 단순합니다.

- `COVERED`라고 적는 것만으로는 완료되지 않게 만들기
- 어떤 제품 영역을 검토했는지 자체를 기록하기
- 코드에 존재한다는 사실과 원래 제품 의도를 구분하기
- AI가 결정해도 되는 것과 반드시 사람이 결정해야 하는 것을 명확히 나누기
- 승인할 때 실제 무엇이 바뀌었는지 보여주기
- downstream review로 넘기기 전에 upstream에서 닫을 수 있는 의미는 최대한 닫기

정식 설계 명세:

[`docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md`](docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md)

동결된 설계 authority는 [`2026-08-28-core-semantic-closure-v2-freeze.md`](docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md)입니다. State `0.1.2.1`, action-conformance/1.0, semantic-review/1.0, v0.4.3 evidence는 historical compatibility로 유지되며 V2 의미로 재정의되지 않습니다.

---

## 상세 아키텍처

기술적인 내부 구조, authority flow, repository mapping, version history가 필요하면 다음 문서를 봅니다.

[`PROGRAM_ARCHITECTURE.md`](PROGRAM_ARCHITECTURE.md)

내부적으로는 Product Definition Core, Downstream Conformance, Semantic Review, Evaluation & Calibration 계층으로 나뉘지만, 처음 사용하는 사람은 다음 네 단계만 기억하면 됩니다.

> **빠진 걸 찾고 → 애매한 걸 정하고 → 정한 대로 만들게 하고 → 제대로 만들었는지 확인한다.**
