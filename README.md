# JOEFLOW

[English](#english) | [한국어](#korean)

<a name="english"></a>
**English**

## 1. Summary

- Program version: **`v1.2.0`**
- Runtime skill/package ID: **`joewrks-product-definition`**
- Authoritative source: **`product-definition/<project-slug>/state.json`**
- Mission: **Product planning tool for defining what to build before implementation**
- Scope: Websites, apps, games, workflows, and existing product redesigns
- Focus: Requirements, rules, exceptions, and acceptance criteria
- Operating principle: Inspect evidence first, ask the user only about material unresolved decisions, and persist approved outcomes as file-based authority
- Objective: Prevent implementation teams from guessing material product decisions

## 2. Design Purpose

### Objectives

- Define product meaning before implementation
- Verify alignment between approved requirements and implementation behavior
- Separate code defects from unresolved product decisions discovered during implementation

### Replacement scope

- Replace product authority held only in chat memory with canonical `state.json`
- Replace arbitrary implementation policy decisions with evidence inspection and user approval
- Replace fragmented requirement delivery with planning specifications and implementation handoffs linked to stable source IDs

### Non-replacement scope

- Product code implementation
- Final aesthetic or art-direction decisions
- Deployment infrastructure operations
- Professional legal, security, or accounting approval

## 3. Key Features

| Feature | Purpose | Primary output |
| --- | --- | --- |
| Evidence discovery | Check repositories, documents, tests, and existing screens before asking questions | Evidence and source bindings |
| Ambiguity resolution | Identify omissions, conflicts, and exceptions that change outcomes | Material unknowns and user questions |
| Product meaning closure | Define requirements, rules, states, permissions, failures, and recovery | Approvable `state.json` |
| Acceptance boundary | Separate product completion from implementation completion | Approval Manifest and acceptance criteria |
| Human-readable delivery | Project approved meaning into readable documents | `MASTER_PLANNING_SPEC.md`, `planning-review-core.html` |
| Implementation handoff | Bind approved meaning and implementation obligations to stable IDs | Machine-readable handoff files and verification evidence when required |
| Re-entry routing | Classify implementation mismatches | Code correction or affected Product Definition review |
| Revision and approval tools | Open the next revision from a record patch, cascade supersessions, record the user's approval, and report pending or bundled revisions | `open_revision.py`, `new_records.py`, `supersede_records.py`, `record_approval.py`, `approval_status.py`, `explain_state_errors.py` |

Default outputs:

```text
product-definition/my-product/
├─ state.json                 # Approved meaning and authority
├─ MASTER_PLANNING_SPEC.md    # Planning specification for implementers
└─ planning-review-core.html  # Compact review view for users
```

`MASTER_PLANNING_SPEC.md` and the HTML file are readable projections generated from the source. `state.json` remains authoritative. HTML colors and layout do not constitute product design approval.

## 4. Usage

### When to use

1. **New product** — Define users, states, permissions, failure paths, and recovery before implementation
2. **Existing product change** — Separate current code from original intent and identify unresolved decisions within the redesign scope
3. **Implementation meaning mismatch** — Compare approved authority with observed behavior and determine whether code correction or Product Definition re-entry is required

Minor and reversible internal implementation choices do not require user questions.

### Installation requirements

- Required tools: Codex, Git, Python 3
- Example environment: Windows PowerShell
- Installation unit: Entire `skills/joewrks-product-definition/` directory
- Prohibited: Copying only `SKILL.md` or overwriting an existing personal installation without inspection

No dedicated installer or package-manager command is currently provided.

```powershell
git clone https://github.com/JOEWRKS/JOEFLOW.git
Set-Location JOEFLOW

$joeflowSource = (Resolve-Path '.\skills\joewrks-product-definition').Path
$joeflowCodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$joeflowTarget = Join-Path $joeflowCodexHome 'skills\joewrks-product-definition'

if (Test-Path -LiteralPath $joeflowTarget) {
  throw "기존 설치를 덮어쓰지 마세요. 먼저 백업하고 변경 내용을 확인하세요: $joeflowTarget"
}
New-Item -ItemType Directory -Force (Split-Path $joeflowTarget) | Out-Null
Copy-Item -LiteralPath $joeflowSource -Destination $joeflowTarget -Recurse
```

### Example request

Use the following request in a new chat.

```text
Use $joewrks-product-definition for this project.

Before implementation, use JOEFLOW to define exactly what should be built.
First inspect the repository, documents, tests, and existing screens for available evidence.
Identify material gaps in requirements, rules, exceptions, and acceptance criteria.
Ask one question at a time only for material decisions that cannot be resolved from evidence.

Use product-definition/<project-slug>/state.json as the authority.
Do not begin implementation before validation and my approval are complete.
After approval, create MASTER_PLANNING_SPEC.md and planning-review-core.html,
then hand off the approved meaning so the implementation team does not need to guess.
```

### Primary validation

```text
python <installed-skill-directory>/scripts/validate_state.py path/to/state.json
python <installed-skill-directory>/scripts/validate_closure.py path/to/state.json
```

Validation boundaries:

- Script path: Resolve from the installed skill directory, not the consumer project
- Product Definition approval: Requires user approval of the exact revision, digest, and Approval Manifest
- Implementation verification: Compare actual results with approved requirements, roles, states, failures, recovery, and acceptance criteria

## 5. Tool Integration

| Tool | Role | Handoff focus |
| --- | --- | --- |
| [JOENESS](https://github.com/JOEWRKS/JOENESS) | **Task sequence, progress, and completion evidence** | Task order, records, resumption, and completion evidence |
| [JOEFLOW](https://github.com/JOEWRKS/JOEFLOW) | **Requirements, rules, exceptions, and acceptance criteria** | Product requirements, rules, exceptions, and acceptance boundaries |
| [JOEDESIGN](https://github.com/JOEWRKS/JOEDESIGN) | **UI creation, visual standards, and design review** | Screens, visual standards, and design verification |

Recommended sequence:

```text
Organize work with JOENESS
→ Define the product with JOEFLOW
→ Create and review the UI with JOEDESIGN
→ Implement the product
→ Verify the result
→ Record completion and remaining work in JOENESS
```

Integration boundaries:

- JOENESS: Connect progress state with completion evidence across the work
- JOEFLOW: Hand approved `state.json` and planning specifications to design and implementation consumers
- JOEDESIGN: Hand off visual standards and review results without changing approved product meaning
- Independent use of each tool supported
- Tool connection does not imply automatic execution, approval, or completion

## 6. Limitations

- No replacement for user approval; AI-generated approval or approval timestamps prohibited
- Material ambiguity discovered during implementation requires re-entry for the affected Product Definition scope
- Clear code defects must not be converted into new product decisions
- Common implementation handoff supported without optional tools such as Figma
- Requested results not observed remain `NOT VERIFIED`
- Semantic review repeatability remains `NOT_MEASURED` until measured in a valid execution environment
- Semantic review results cannot approve new product decisions
- Program version `1.2.0` remains independent from internal state and contract versions
- Frozen historical contract meaning remains unchanged

Detailed references:

- [Program structure and contract boundaries (Korean)](PROGRAM_ARCHITECTURE.md)
- [Current V2 workflow](skills/joewrks-product-definition/references/workflow-v0.2.0.md)
- [Implementation mismatch re-entry procedure](skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md)
- [Full regression environment and safe recovery procedure (Korean)](docs/regression-environment.md)
- [Version history](CHANGELOG.md)

[English ↑](#english) | [한국어](#korean)

---

<a name="korean"></a>
**한국어**

- 프로그램 버전: **`v1.2.0`**
- 런타임 skill/package ID: **`joewrks-product-definition`**
- 제품 기준 원본: **`product-definition/<project-slug>/state.json`**

## 1. 핵심 요약

- 임무: **무엇을 만들지 확실하게 정하는 제품 기획 도구**
- 대상: 웹사이트, 앱, 게임, 업무 흐름, 기존 제품 개편
- 집중 범위: 요구사항·규칙·예외·완료 기준
- 운영 원칙: 근거 우선 확인, 중요 미결정만 사용자 질문, 승인 결과의 파일 기준화
- 최종 목적: 구현 담당자의 중요 제품 결정 추측 방지

## 2. 설계 목적

### 목적

- 구현 착수 전 제품 의미 확정을 목적으로 설계
- 승인된 요구사항과 실제 구현의 의미 일치 확인을 목적으로 설계
- 구현 중 발견된 코드 결함과 제품 미결정의 분리를 목적으로 설계

### 대체 범위

- 채팅 기억에만 의존하는 제품 기준을 canonical `state.json`으로 대체
- 구현 담당자의 임의 정책 결정을 근거 확인과 사용자 승인 절차로 대체
- 흩어진 요구사항 전달을 원본 ID에 연결된 기획 명세와 구현 인계로 대체

### 비대체 범위

- 실제 제품 코드 작성
- 최종 미감·아트디렉션 판단
- 배포 인프라 운영
- 법률·보안·회계 전문 승인

## 3. 주요 기능

| 기능 | 목적 | 주요 결과 |
| --- | --- | --- |
| 근거 조사 | 저장소·문서·테스트·기존 화면에서 확인 가능한 답 우선 확인 | evidence 및 출처 연결 |
| 회색지대 정리 | 결과를 바꾸는 누락·충돌·예외 식별 | 중요 unknown과 사용자 질문 |
| 의미 확정 | 요구사항·규칙·상태·권한·실패·복구 결정 | 승인 가능한 `state.json` |
| 완료 기준 고정 | 제품 완료와 구현 완료의 구분 | Approval Manifest와 수용 기준 |
| 사람용 전달 | 승인 의미의 읽기용 문서화 | `MASTER_PLANNING_SPEC.md`, `planning-review-core.html` |
| 구현 인계 | 승인 의미와 구현 의무의 고정 ID 연결 | 필요 시 기계용 인계 파일과 검증 근거 |
| 재진입 판정 | 구현 불일치의 원인 분류 | 코드 수정 또는 해당 제품 범위 재검토 |
| 개정·승인 도구 | 레코드 패치로 다음 revision 열기, 대체 연쇄 처리, 사용자 승인 기록, 승인 대기·묶인 revision 확인 | `open_revision.py`, `new_records.py`, `supersede_records.py`, `record_approval.py`, `approval_status.py`, `explain_state_errors.py` |

기본 결과물:

```text
product-definition/my-product/
├─ state.json                 # 승인과 의미의 기준
├─ MASTER_PLANNING_SPEC.md    # 구현 담당용 기획 명세
└─ planning-review-core.html  # 사용자용 핵심 검토 화면
```

`MASTER_PLANNING_SPEC.md`와 HTML은 원본에서 만든 읽기용 문서. 승인 기준은 항상 `state.json`. HTML의 색·배치를 제품 디자인 승인으로 사용 금지.

## 4. 사용 방법

### 적용 시점

1. **새 제품 시작** — 사용자·상태·권한·실패·복구 조건의 구현 전 정리
2. **기존 제품 변경** — 현재 코드와 원래 의도의 분리, 개편 범위의 미결정 확인
3. **구현 의미 불일치** — 승인 기준과 실제 동작의 차이 및 재진입 필요 범위 확인

사소하고 되돌릴 수 있는 내부 구현 선택은 사용자 질문 대상에서 제외.

### 설치 준비

- 필수 도구: Codex, Git, Python 3
- 아래 예제 환경: Windows PowerShell
- 설치 단위: `skills/joewrks-product-definition/` 전체
- 금지: `SKILL.md` 단독 복사, 기존 개인 설치의 무검증 덮어쓰기

전용 installer 및 package-manager 명령은 현재 미제공.

```powershell
git clone https://github.com/JOEWRKS/JOEFLOW.git
Set-Location JOEFLOW

$joeflowSource = (Resolve-Path '.\skills\joewrks-product-definition').Path
$joeflowCodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$joeflowTarget = Join-Path $joeflowCodexHome 'skills\joewrks-product-definition'

if (Test-Path -LiteralPath $joeflowTarget) {
  throw "기존 설치를 덮어쓰지 마세요. 먼저 백업하고 변경 내용을 확인하세요: $joeflowTarget"
}
New-Item -ItemType Directory -Force (Split-Path $joeflowTarget) | Out-Null
Copy-Item -LiteralPath $joeflowSource -Destination $joeflowTarget -Recurse
```

### 실행 요청

새 채팅에서 아래 요청 사용.

```text
Use $joewrks-product-definition for this project.

구현하기 전에 JOEFLOW로 무엇을 만들지 확정해줘.
먼저 저장소·문서·테스트·기존 화면에서 확인 가능한 근거를 조사하고,
요구사항·규칙·예외·완료 기준에서 중요한 빈틈을 찾아줘.
근거로 해결할 수 없는 중요한 결정만 한 번에 하나씩 질문해.

product-definition/<project-slug>/state.json을 기준으로 기록하고,
검증과 내 승인이 끝나기 전에는 구현을 시작하지 마.
승인 뒤에는 MASTER_PLANNING_SPEC.md와 planning-review-core.html을 만들고,
구현 담당자가 추측하지 않도록 인계해줘.
```

### 대표 검증

```text
python <installed-skill-directory>/scripts/validate_state.py path/to/state.json
python <installed-skill-directory>/scripts/validate_closure.py path/to/state.json
```

검증 기준:

- Script 경로: consumer project가 아닌 설치된 skill 디렉터리 기준
- Product Definition 승인: 정확한 revision·digest·Approval Manifest에 대한 사용자 승인 필수
- 구현 검증: 승인된 요구사항·역할·상태·실패·복구·수용 기준과 실제 결과의 대조

## 5. 도구 간 연결

| 도구 | 역할 | 인계 기준 |
| --- | --- | --- |
| [JOENESS](https://github.com/JOEWRKS/JOENESS) | **작업 순서·진행 상태·완료 근거 관리** | 작업 순서·기록·재개·완료 근거 |
| [JOEFLOW](https://github.com/JOEWRKS/JOEFLOW) | **요구사항·규칙·예외·완료 기준 확정** | 요구사항·규칙·예외·완료 기준 |
| [JOEDESIGN](https://github.com/JOEWRKS/JOEDESIGN) | **화면 제작·시각 기준 수립·디자인 검수** | 화면·시각 기준·디자인 검수 |

권장 연결 순서:

```text
JOENESS로 작업 정리
→ JOEFLOW로 만들 것 확정
→ JOEDESIGN으로 화면 제작·검수
→ 구현 담당이 개발
→ 결과 검증
→ JOENESS에 완료·잔여 기록
```

연결 원칙:

- JOENESS: 전 과정의 진행 상태와 완료 근거 연결
- JOEFLOW: 승인된 `state.json`과 기획 명세를 디자인·구현 담당에게 인계
- JOEDESIGN: 승인된 제품 의미를 변경하지 않은 시각 기준과 검수 결과 인계
- 개별 도구의 단독 사용 지원
- 연결만으로 자동 실행·자동 승인·자동 완료 처리 금지

## 6. 한계

- 사용자 승인 대체 불가. AI의 승인·승인 시각 생성 금지
- 구현 중 중요 미결정 발견 시 해당 Product Definition 범위 재진입
- 명확한 코드 결함을 새 제품 결정으로 전환 금지
- Figma 등 선택 도구 없이 공통 구현 인계 가능
- 요청된 결과 미확인 시 `NOT VERIFIED` 유지
- 의미 검토의 반복 판단 신뢰도: 실제 환경 측정 전 상태인 `NOT_MEASURED`
- 의미 검토 결과만으로 새 제품 결정 승인 불가
- 프로그램 버전 `1.2.0`과 내부 상태·계약 버전의 독립 관리
- 과거 동결 계약의 의미 변경 없음

상세 기준:

- [프로그램 구조와 계약 경계](PROGRAM_ARCHITECTURE.md)
- [현재 V2 작업 흐름](skills/joewrks-product-definition/references/workflow-v0.2.0.md)
- [구현 불일치 재진입 절차](skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md)
- [전체 회귀 환경과 안전한 복구 절차](docs/regression-environment.md)
- [버전별 변경 기록](CHANGELOG.md)
