# JOEFLOW 빠른 시작

설치 단위는 언제나 `skills/joewrks-product-definition/` 폴더 전체입니다. 아래 명령은 Windows PowerShell 기준이고, 저장소에 있는 스크립트만 씁니다. `<skill>`은 설치된 스킬 폴더, `STATE_JSON`은 사용자 프로젝트의 `product-definition/<project-slug>/state.json`입니다.

## 1. 설치

**Codex — 일반 복사.** README의 [설치 블록](../README.md#4-usage)을 그대로 실행합니다. 이미 설치돼 있으면 덮어쓰지 않고 멈춥니다.

**Codex — 오버레이 설치(개인용).** 저장소 관리자의 Codex 설치본을 버전마다 갱신하는 스크립트입니다. 직전 버전의 설치 영수증(`evals/joeflow-u1-personal-install/personal-install-overlay-receipt.json`)이 있어야 하고, 영수증이 직전 버전 상태가 아니면 아무것도 쓰지 않고 멈춥니다. 다른 사람의 설치에는 쓰지 마세요.

```powershell
python -B evals/v2-release-20261119/install_2_0_0.py <2.0.0 릴리스 커밋>
```

**Claude Code.** 이 일을 하는 스크립트는 없습니다. 깨끗한 clone을 하나 두고, Claude Code 스킬 폴더에서 저장소의 스킬 폴더로 junction(링크)을 만듭니다.

```powershell
git clone https://github.com/JOEWRKS/JOEFLOW.git $HOME\src\JOEFLOW
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

## 4. 읽기용 문서 갱신과 검사

```powershell
python <skill>/scripts/update_projection.py STATE_JSON --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html --write
python <skill>/scripts/projection_check.py STATE_JSON --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html
```

`projection_check.py`는 읽기만 하며, 낡은 revision이나 빠진 내용을 찾으면 `ok: false`와 다음 행동을 출력합니다.

## 5. 프로젝트에 버전 고정

```powershell
python <skill>/scripts/joeflow_version.py STATE_JSON --pin
```

`state.json` 밖의 `joeflow-project.json`에 이 프로젝트를 만든 JOEFLOW 버전을 적습니다.

## 6. 업그레이드

| 설치 경로 | 방법 |
| --- | --- |
| Codex 일반 복사 | 업그레이드 스크립트는 없습니다. 기존 `…\.codex\skills\joewrks-product-definition` 폴더를 다른 이름으로 옮겨 백업하고, 새로 clone한 저장소에서 1절의 일반 복사를 다시 실행합니다 |
| Codex 오버레이(개인용) | 새 버전의 `install_<ver>.py <릴리스 커밋>`을 실행합니다. 버전마다 새 스크립트가 있습니다 |
| Claude Code | clone 폴더에서 `git pull --ff-only`. junction이라 다시 연결할 필요가 없습니다 |

## 7. 제거

제거 스크립트는 없습니다. 스킬 폴더를 지우면 됩니다.

- Codex: `…\.codex\skills\joewrks-product-definition` 폴더를 지웁니다.
- Claude Code: `cmd /c rmdir $HOME\.claude\skills\joewrks-product-definition`로 **junction만** 지웁니다(`Remove-Item -Recurse`를 junction에 쓰면 clone 안의 파일까지 지워질 수 있습니다). 필요하면 clone 폴더도 지웁니다.

사용자 프로젝트의 `product-definition/` 폴더와 `joeflow-project.json`은 그대로 남습니다.
