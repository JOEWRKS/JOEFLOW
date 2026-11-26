# JOEFLOW

[English](#english) | [한국어](#korean)

<a name="english"></a>
**English**

## 1. Summary

- Program version: **`v2.0.2`**
- Runtime skill/package ID: **`joewrks-product-definition`**
- Authoritative source: **`product-definition/<project-slug>/state.json`**
- Mission: product planning tool that defines what to build before implementation (websites, apps, games, workflows, redesigns)
- Principle: inspect evidence first, ask only about material unresolved decisions, persist approved outcomes as file-based authority

## 2. Design Purpose

- Objectives: define product meaning before implementation; check implementation against approved requirements; separate code defects from unresolved product decisions
- Replaces: product authority held only in chat memory, arbitrary policy decisions by implementers, fragmented requirement delivery
- Does not replace: product code, final art direction, deployment operations, professional legal/security/accounting approval

## 3. Key Features

Evidence discovery, ambiguity resolution, product meaning closure, acceptance boundaries, readable projections, implementation handoff bound to stable IDs, and re-entry routing for implementation mismatches. Revision and approval tools: `open_revision.py`, `new_records.py`, `supersede_records.py`, `record_approval.py`, `approval_status.py`, `explain_state_errors.py`.

```text
product-definition/my-product/
├─ state.json                 # Approved meaning and authority
├─ MASTER_PLANNING_SPEC.md    # Planning specification for implementers
└─ planning-review-core.html  # Compact review view for users
```

The Markdown and HTML files are projections; `state.json` stays authoritative. HTML colors and layout are not design approval.

## 4. Usage

Use it for a new product, a change to an existing product, or a mismatch between approved meaning and implementation. Requires Git and Python 3 (examples use Windows PowerShell). Install the entire `skills/joewrks-product-definition/` directory; never copy only `SKILL.md` or overwrite an existing install without inspection.

Codex plain copy of release `v2.0.2`. Run it in an empty folder; it stops without copying if the clone fails (for example, a `JOEFLOW` folder is already there) or an install already exists:

```powershell
& {
  git clone --branch v2.0.2 https://github.com/JOEWRKS/JOEFLOW.git JOEFLOW
  if ($LASTEXITCODE -ne 0) { throw "git clone이 실패했습니다. 빈 폴더에서 다시 실행하세요(이미 JOEFLOW 폴더가 있으면 clone하지 않습니다)." }

  $joeflowSource = (Resolve-Path '.\JOEFLOW\skills\joewrks-product-definition').Path
  $joeflowCodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
  $joeflowTarget = Join-Path $joeflowCodexHome 'skills\joewrks-product-definition'

  if (Test-Path -LiteralPath $joeflowTarget) {
    throw "기존 설치를 덮어쓰지 마세요. 먼저 백업하고 변경 내용을 확인하세요: $joeflowTarget"
  }
  New-Item -ItemType Directory -Force (Split-Path $joeflowTarget) | Out-Null
  Copy-Item -LiteralPath $joeflowSource -Destination $joeflowTarget -Recurse
}
```

There is no package-manager command. Claude Code (clone + junction), the maintainer's personal Codex overlay installer (`evals/<release-folder>/install_<ver>.py`), upgrades, and removal are in the [Quickstart (Korean)](docs/QUICKSTART.md).

### Example request

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

Resolve script paths from the installed skill directory. Product Definition approval needs the user's approval of the exact revision, digest, and Approval Manifest.

## 5. Tool Integration

| Tool | Role |
| --- | --- |
| [JOENESS](https://github.com/JOEWRKS/JOENESS) | **Task sequence, progress, and completion evidence** |
| [JOEFLOW](https://github.com/JOEWRKS/JOEFLOW) | **Requirements, rules, exceptions, and acceptance criteria** |
| [JOEDESIGN](https://github.com/JOEWRKS/JOEDESIGN) | **UI creation, visual standards, and design review** |

Sequence: JOENESS organizes work → JOEFLOW defines the product → JOEDESIGN creates and reviews the UI → implement → verify → JOENESS records completion. Each tool works alone; connecting them never implies automatic execution, approval, or completion.

## 6. Limitations

- Never replaces user approval; AI-generated approvals or approval timestamps are prohibited
- Material ambiguity found during implementation re-enters the affected Product Definition scope; clear code defects stay code defects
- Unobserved results stay `NOT VERIFIED`; semantic review repeatability stays `NOT_MEASURED` and cannot approve new decisions
- Program version `2.0.2` is independent of state and contract versions; frozen historical contracts keep their meaning

References: [Program architecture (Korean)](PROGRAM_ARCHITECTURE.md) · [Current V2 workflow](skills/joewrks-product-definition/references/workflow-v0.2.0.md) · [Implementation mismatch re-entry procedure](skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md) · [Regression environment (Korean)](docs/regression-environment.md) · [Quickstart (Korean)](docs/QUICKSTART.md) · [Security (Korean)](SECURITY.md) · [Changelog](CHANGELOG.md)

---

<a name="korean"></a>
**한국어**

- 프로그램 버전: **`v2.0.2`**
- 런타임 skill/package ID: **`joewrks-product-definition`**
- 제품 기준 원본: **`product-definition/<project-slug>/state.json`**

## 1. 핵심 요약

- 임무: 구현 전에 무엇을 만들지 확정하는 제품 기획 도구(웹사이트, 앱, 게임, 업무 흐름, 기존 제품 개편)
- 원칙: 근거 먼저 확인, 중요한 미결정만 질문, 승인 결과는 파일로 기준화

## 2. 설계 목적

- 목적: 구현 전 제품 의미 확정, 승인 기준과 구현의 일치 확인, 코드 결함과 제품 미결정 분리
- 대체: 채팅 기억에만 있는 기준, 구현 담당의 임의 정책 결정, 흩어진 요구사항 전달
- 비대체: 제품 코드 작성, 최종 아트디렉션, 배포 운영, 법률·보안·회계 전문 승인

## 3. 주요 기능

근거 조사, 회색지대 정리, 의미 확정, 완료 기준 고정, 읽기용 문서(`MASTER_PLANNING_SPEC.md`, `planning-review-core.html`), 고정 ID 기반 구현 인계, 구현 불일치 재진입 판정. 승인 기준은 항상 `state.json`이며 HTML의 색·배치는 디자인 승인이 아닙니다.

## 4. 사용 방법

설치는 `skills/joewrks-product-definition/` 폴더 전체 단위입니다. Codex 일반 복사는 위 영어 절의 PowerShell 블록, Claude Code 연결·개인용 오버레이 설치기·업그레이드·제거는 [빠른 시작](docs/QUICKSTART.md)에 있습니다. 실행 요청은 위 Example request를 새 채팅에 붙여 넣으면 됩니다. 대표 검증은 `validate_state.py`와 `validate_closure.py`입니다(경로는 설치된 skill 폴더 기준).

## 5. 도구 간 연결

| 도구 | 역할 |
| --- | --- |
| [JOENESS](https://github.com/JOEWRKS/JOENESS) | **작업 순서·진행 상태·완료 근거 관리** |
| [JOEFLOW](https://github.com/JOEWRKS/JOEFLOW) | **요구사항·규칙·예외·완료 기준 확정** |
| [JOEDESIGN](https://github.com/JOEWRKS/JOEDESIGN) | **화면 제작·시각 기준 수립·디자인 검수** |

각 도구는 단독으로도 쓰며, 연결만으로 자동 실행·승인·완료 처리를 하지 않습니다.

## 6. 한계

- 사용자 승인 대체 불가, AI의 승인·승인 시각 생성 금지
- 구현 중 중요 미결정은 해당 범위 재진입, 명확한 코드 결함은 제품 결정으로 바꾸지 않음
- 미확인 결과는 `NOT VERIFIED`, 의미 검토 반복 신뢰도는 `NOT_MEASURED`
- 프로그램 버전 `2.0.2`는 내부 상태·계약 버전과 독립

상세: [프로그램 구조](PROGRAM_ARCHITECTURE.md) · [빠른 시작](docs/QUICKSTART.md) · [보안](SECURITY.md) · [회귀 환경](docs/regression-environment.md) · [변경 기록](CHANGELOG.md)
