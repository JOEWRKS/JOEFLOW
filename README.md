# JOEFLOW

현재 프로그램 버전은 **`v1.1.0`**입니다. 런타임 skill/package ID는 호환성을 위해 **`joewrks-product-definition`**을 유지합니다.

## 1. 이게 뭐냐

**JOEFLOW는 구현 전에 요구사항·규칙·예외·완료 기준을 확인해, 무엇을 만들지 확실하게 정하는 제품 기획 도구입니다.**

AI가 코드부터 만들면서 중요한 결정을 추측하지 않도록 자료를 먼저 조사합니다. 자료만으로 정할 수 없는 중요한 문제는 사용자에게 묻고, 승인된 결과는 다음 파일에 기준으로 남깁니다.

```text
product-definition/<project-slug>/state.json
```

채팅 기록이나 요약 문서가 이 파일을 대신하지 않습니다.

## 2. 언제 쓰냐

대표적인 사용 상황은 세 가지입니다.

1. **새 제품을 시작할 때** — 웹사이트, 앱, 게임, 업무 흐름의 사용자·상태·권한·실패·복구 조건을 구현 전에 정리합니다.
2. **기존 제품을 고칠 때** — 현재 코드와 원래 의도를 구분하고, 리뉴얼이나 기능 변경에서 남은 중요한 미결정을 찾습니다.
3. **구현 중 뜻이 어긋났을 때** — 승인된 기준과 실제 동작의 차이를 확인하고, 코드 문제인지 제품 결정을 다시 열어야 하는지 구분합니다.

단순한 내부 구현 선택처럼 결과를 바꾸지 않고 쉽게 되돌릴 수 있는 일은 모두 사용자에게 묻지 않습니다.

## 3. 바로 시작하기

### 설치

준비물은 Codex, Git, Python 3이며 아래 설치 예시는 Windows PowerShell 기준입니다.

전용 installer나 package-manager 명령은 아직 없습니다. 저장소를 받은 뒤 skill 디렉터리 **전체**를 Codex의 skills 위치에 설치합니다. `SKILL.md`만 복사하면 동작하지 않습니다.

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

설치 후 새 채팅에서 아래 요청을 그대로 사용할 수 있습니다.

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

## 4. 무엇을 받게 되냐

기본 결과물은 다음과 같습니다.

```text
product-definition/my-product/
├─ state.json                 # 승인과 의미의 기준
├─ MASTER_PLANNING_SPEC.md    # 구현자가 처음부터 끝까지 읽는 기획 명세
└─ planning-review-core.html  # 사용자가 빠르게 보는 검토 화면
```

필요한 프로젝트에는 승인된 내용을 구현 작업으로 연결하는 기계용 인계 파일과 검증 근거가 추가될 수 있습니다. 이 파일은 요구사항, 역할, 상태 변화, 실패·복구, 수용 기준을 원본의 고정 ID에 연결합니다.

`MASTER_PLANNING_SPEC.md`와 HTML은 원본에서 만든 읽기용 문서입니다. 승인 기준은 항상 `state.json`이며, HTML의 색이나 배치는 제품 디자인 승인을 뜻하지 않습니다.

## 5. 다른 JOE 도구와 함께 쓰기

각 도구의 역할은 다음처럼 나뉩니다.

| 도구 | 역할 |
| --- | --- |
| [JOENESS](https://github.com/JOEWRKS/JOENESS) | **작업이 어디까지 됐고 무엇이 남았는지 관리한다.** 작업 순서·기록·재개·완료 근거를 맡습니다. |
| [JOEFLOW](https://github.com/JOEWRKS/JOEFLOW) | **무엇을 만들지 확실하게 정한다.** 요구사항·규칙·예외·완료 기준을 맡습니다. |
| [JOEDESIGN](https://github.com/JOEWRKS/JOEDESIGN) | **어떻게 보이고 사용될지 만들고 확인한다.** 화면·시각 기준·디자인 검수를 맡습니다. |

함께 사용할 때의 권장 흐름은 다음과 같습니다.

```text
JOENESS로 작업 정리
→ JOEFLOW로 만들 것 확정
→ JOEDESIGN으로 화면 제작·검수
→ 구현 담당이 개발
→ 결과 검증
→ JOENESS에 완료·잔여 기록
```

JOENESS는 전 과정에서 진행과 근거를 이어 줍니다. JOEFLOW는 승인된 `state.json`과 기획 명세를 JOEDESIGN·구현 담당에게 넘기고, JOEDESIGN은 승인된 제품 의미를 바꾸지 않은 시각 기준과 검수 결과를 넘깁니다. 세 도구는 각각 단독으로도 사용할 수 있으며, 연결됐다는 이유만으로 자동 실행·자동 승인·자동 완료되지는 않습니다.

## 6. 지원 범위·주의사항

- JOEFLOW는 제품 의미를 정하고 검증하지만 실제 제품 코드, 최종 미감 판단, 배포 운영, 법률·보안·회계의 전문 승인을 대신하지 않습니다.
- 중요한 제품 결정과 정확한 승인 목록(Approval Manifest)은 사용자가 승인해야 합니다. AI가 승인이나 승인 시각을 만들 수 없습니다.
- 구현에서 새로운 중요한 애매함이 나오면 해당 범위만 Product Definition으로 다시 돌아갑니다. 코드 버그를 새 제품 결정으로 꾸미지 않습니다.
- Figma 같은 선택 도구를 쓰지 않아도 공통 구현 인계는 가능합니다. 요청한 결과물을 확인하지 못했다면 `NOT VERIFIED`로 남깁니다.
- 의미 검토 기능이 반복해서 같은 판단을 내리는지는 아직 실제 환경에서 측정하지 않았습니다(`NOT_MEASURED`). 이 검토만으로 새 제품 결정을 승인할 수 없습니다.
- 프로그램 버전 `1.1.0`과 내부 상태·계약의 버전 표시는 서로 다른 체계입니다. 이번 릴리스가 과거 계약의 뜻을 바꾸지는 않습니다.

Canonical state 검증:

```text
python <installed-skill-directory>/scripts/validate_state.py path/to/state.json
python <installed-skill-directory>/scripts/validate_closure.py path/to/state.json
```

더 자세한 내용:

- [프로그램 구조와 계약 경계](PROGRAM_ARCHITECTURE.md)
- [현재 V2 작업 흐름](skills/joewrks-product-definition/references/workflow-v0.2.0.md)
- [구현 불일치가 생겼을 때의 재진입 절차](skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md)
- [전체 회귀 환경과 안전한 복구 절차](docs/regression-environment.md)
- [버전별 변경 기록](CHANGELOG.md)
