# JOEFLOW 빠른 시작

설치 단위는 언제나 `skills/joewrks-product-definition/` 폴더 전체입니다. 아래 명령은 Windows PowerShell 기준이고, 저장소에 있는 스크립트만 씁니다. `<skill>`은 설치된 스킬 폴더, `STATE_JSON`은 사용자 프로젝트의 `product-definition/<project-slug>/state.json`입니다.

## 1. 설치

**Codex — 일반 복사.** README의 [설치 블록](../README.md#4-usage)을 **빈 폴더에서** 그대로 실행합니다. 블록은 태그 `v2.0.1`을 받아 설치합니다(다른 버전은 태그만 바꿉니다). 이미 설치돼 있거나 `git clone`이 실패하면(예: 그 폴더에 `JOEFLOW`가 이미 있음) 아무것도 복사하지 않고 멈춥니다. 설치 위치는 `$env:CODEX_HOME`이 있으면 `$env:CODEX_HOME\skills\joewrks-product-definition`, 없으면 `~\.codex\skills\joewrks-product-definition`입니다.

**Codex — 오버레이 설치(개인용).** 저장소 관리자의 Codex 설치본을 버전마다 갱신하는 스크립트입니다. 다른 사람은 쓰지 마세요. 동작은 코드 기준으로 이렇습니다.

- 쓰는 곳: `~\.codex\skills\joewrks-product-definition`(고정 경로, `CODEX_HOME`을 따르지 **않습니다**)과 백업 `~\.codex\skills-backups\…`, 그리고 저장소의 영수증 파일.
- 영수증(`evals/joeflow-u1-personal-install/personal-install-overlay-receipt.json`)은 공개 저장소에 들어 있으므로 "영수증이 있다"는 것은 보호가 아닙니다. 멈추는 근거는 **해시 대조**입니다. 영수증의 `tip_compared`가 직전 릴리스 커밋이어야 하고, 설치 폴더의 소스 파일 해시가 영수증의 `installed_manifest`와 모두 같아야 합니다. 설치가 없거나 다르면 아무것도 쓰기 전에 `AssertionError`로 멈춥니다. 이 검사는 `assert`이므로 `python -O`로 돌리지 마세요.
- `<릴리스 커밋>`: 설치할 버전 태그의 커밋, 예를 들어 `git rev-parse v2.0.1^{commit}`의 출력.

```powershell
python -B evals/v2-tests-20261119/install_2_0_1.py <2.0.1 릴리스 커밋>
```

**Claude Code.** 이 일을 하는 스크립트는 없습니다. 깨끗한 clone을 하나 두고, Claude Code 스킬 폴더에서 저장소의 스킬 폴더로 junction(링크)을 만듭니다.

```powershell
git clone --branch v2.0.1 https://github.com/JOEWRKS/JOEFLOW.git $HOME\src\JOEFLOW
New-Item -ItemType Directory -Force $HOME\.claude\skills | Out-Null
New-Item -ItemType Junction -Path $HOME\.claude\skills\joewrks-product-definition -Target $HOME\src\JOEFLOW\skills\joewrks-product-definition
```

## 2. 첫 실행

새 대화에서 README의 [예시 요청](../README.md#example-request)을 붙여 넣습니다(Codex는 `$joewrks-product-definition`, Claude Code는 스킬 이름 `joewrks-product-definition`으로 부릅니다). JOEFLOW는 근거를 먼저 조사하고, 근거로 정할 수 없는 중요한 결정만 한 번에 하나씩 묻습니다. 승인 전에는 구현을 시작하지 않습니다.

## 3. 검증

```powershell
python <skill>/scripts/validate_state.py STATE_JSON
python <skill>/scripts/validate_closure.py STATE_JSON
```

`validate_state.py`는 `valid: true`와 exit 0이면 통과입니다. `validate_closure.py`는 사용자 승인 전에는 `closed: false`와 **exit 1이 정상**입니다(무엇이 남았는지 출력합니다). 승인을 기록한 뒤 `closed: true`, exit 0이 됩니다.

## 4. 읽기용 문서 갱신과 검사

`--spec`·`--review`는 **현재 폴더 기준** 경로입니다. 두 문서는 `state.json` 옆에 두므로, 그 폴더에서 실행합니다. 처음 한 번은 두 템플릿을 그 폴더에 복사합니다. 템플릿에는 IDENTITY·SOURCE-MAP 블록이 이미 있어 `--adopt`가 필요 없습니다(`--adopt`는 블록 없이 손으로 쓴 기존 문서용입니다).

```powershell
Set-Location product-definition\<project-slug>
Copy-Item <skill>\templates\master-planning-spec.md MASTER_PLANNING_SPEC.md      # 처음 한 번
Copy-Item <skill>\templates\planning-review-core.html planning-review-core.html  # 처음 한 번
python <skill>/scripts/update_projection.py state.json --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html --write
python <skill>/scripts/projection_check.py state.json --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html
```

`projection_check.py`는 읽기만 하며, 낡은 revision이나 빠진 내용을 찾으면 `ok: false`와 다음 행동을 출력합니다.

## 5. 프로젝트에 버전 고정

```powershell
python <skill>/scripts/joeflow_version.py STATE_JSON --pin
```

`state.json`과 같은 폴더(`product-definition/<project-slug>/joeflow-project.json`)의 별도 파일에 이 프로젝트를 만든 JOEFLOW 버전을 적습니다. `state.json`은 바뀌지 않습니다.

## 6. 업그레이드

| 설치 경로 | 방법 |
| --- | --- |
| Codex 일반 복사 | 업그레이드 스크립트는 없습니다. ① 기존 설치 폴더를 **`skills\` 밖**으로 옮겨 백업합니다(예: `Move-Item ~\.codex\skills\joewrks-product-definition ~\.codex\skills-backups\joewrks-product-definition-2.0.0`, 먼저 `skills-backups` 폴더를 만듭니다). `skills\` 안에 두면 같은 이름의 스킬이 둘이 됩니다. ② **새 빈 폴더에서** README 블록을 다시 실행합니다. 처음 설치한 폴더에서 다시 실행하면 clone이 실패해 멈춥니다. 기존 clone을 쓰려면 그 clone에서 `git fetch --tags`와 `git checkout <새 태그>`를 한 뒤, 블록에서 `git clone` 두 줄을 뺀 나머지만 clone의 상위 폴더에서 실행합니다 |
| Codex 오버레이(개인용) | 새 버전의 `install_<ver>.py <릴리스 커밋>`을 실행합니다. 버전마다 새 스크립트가 있습니다 |
| Claude Code | clone 폴더에서 `git fetch --tags`와 `git checkout <새 태그>`(태그를 쓰지 않으면 `git pull --ff-only`). junction이라 다시 연결할 필요가 없습니다 |

## 7. 제거

제거 스크립트는 없습니다. 스킬 폴더를 지우면 됩니다.

- Codex: `Remove-Item -Recurse -Force ~\.codex\skills\joewrks-product-definition`(`CODEX_HOME`을 쓰면 그 아래 `skills\joewrks-product-definition`). 이 폴더는 junction이 아닌 진짜 복사본입니다. 6절에서 만든 백업(`~\.codex\skills-backups\…`)과 오버레이 설치기의 백업도 필요 없으면 따로 지웁니다.
- Claude Code: `cmd /c rmdir $HOME\.claude\skills\joewrks-product-definition`로 **junction만** 지웁니다(`Remove-Item -Recurse`를 junction에 쓰면 clone 안의 파일까지 지워질 수 있습니다). 필요하면 clone 폴더도 지웁니다.

사용자 프로젝트의 `product-definition/<project-slug>/` 폴더(`state.json`, `joeflow-project.json`, 읽기용 문서)는 그대로 남습니다.

## 8. Windows PowerShell 5.1에서 한국어 출력

스크립트는 출력을 UTF-8로 내보내므로 화면 출력과 스크립트가 쓰는 파일은 정상입니다. 다만 PowerShell 5.1이 출력을 받아 변수나 파일로 넘기면(`$out = python …`, `python … | Out-File …`) 콘솔 인코딩(한국어 Windows는 보통 cp949)으로 읽어 한국어와 `·`, `→`가 깨집니다. `PYTHONIOENCODING=utf-8`로는 고쳐지지 않습니다. 그 세션에서 먼저 아래 줄을 실행하면 정상으로 받습니다(PowerShell 5.1.19041에서 콘솔 인코딩을 cp949로 두고 변수로 받아 확인). Git Bash에서 실행해도 됩니다. JSON의 키와 `ok`·`exit` 값은 ASCII라 판정에는 영향이 없습니다.

```powershell
[Console]::OutputEncoding = [Text.Encoding]::UTF8
```
