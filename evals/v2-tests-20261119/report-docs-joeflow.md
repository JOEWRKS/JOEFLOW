# JOEFLOW 2.0.0 `docs/QUICKSTART.md` 문서 시험 보고서

시험일 2026-11-19 · 대상 `JOEWRKS/JOEFLOW` 태그 `v2.0.0`(89cb012) · Windows 10, Windows PowerShell 5.1(콘솔 코드페이지 cp949), Python 3.14.5, Git for Windows

## 결론

- **문서에 적힌 명령은 모두 적힌 순서대로 돌아갔다.** 설치, 검증, 투영 갱신, 검사, 버전 고정, 업그레이드, 제거 절 모두에서 스크립트가 죽거나 종료 코드가 틀리는 일은 없었다. Python에서 인코딩 예외도 나지 않았다(`PYTHONIOENCODING` 없이도). 스크립트가 직접 stdout을 UTF-8로 바꾸기 때문이다(`scripts/cli_output.py`).
- **새 사용자가 문서만 보고는 막히는 곳이 두 군데 있다.**
  1. **4절(투영 갱신):** `update_projection.py`는 `MASTER_PLANNING_SPEC.md`와 `planning-review-core.html`이 이미 있어야 돈다. 문서는 그 파일들을 어디서 만드는지(`templates/`), 상대 경로가 어느 폴더 기준인지 말하지 않는다. 처음 실행은 `exit=2`로 끝났다.
  2. **6절(Codex 업그레이드):** "새로 clone한 저장소에서 1절을 다시 실행"을 같은 폴더에서 하면 `git clone`만 실패한다. 블록의 나머지는 **예전 clone에서 그대로 설치하고 exit=0**으로 끝난다. 사용자는 업그레이드가 됐다고 믿게 된다.
- **2절(첫 실행)은 실제로 돌려 보지 않았다.** 새 대화를 열지 않았다. SKILL.md의 지시대로 에이전트 역할을 최소한으로 흉내 냈을 뿐이다.
- **인코딩 결과:** `PYTHONIOENCODING`은 QUICKSTART와 README 어디에도 나오지 않는다. 그래도 필요하지 않았다. 다만 PowerShell 5.1이 스크립트 출력을 받아 `$out = python …`이나 `Out-File`로 넘기면 한국어와 `·`, `→`가 깨진다. 이건 `PYTHONIOENCODING=utf-8`을 넣어도 똑같이 깨진다(아래 D7). 스크립트가 쓰는 파일 자체는 UTF-8로 정상이다.
- **오버레이 설치기 문단은 다른 사람이 잘못 돌리지 않게 막기에 전제가 부족하다**(D8). 실행하지는 않았다.

## 절별 판정

| 절 | 판정 | 근거(QUICKSTART 줄 번호 · 실제 출력) |
|---|---|---|
| 1. 설치 — Codex 일반 복사(L7 → README L42-53) | **통과** | 1회차: 복사 완료, exit=0(`log/03-…run1`). 2회차: `throw "기존 설치를 덮어쓰지 마세요…"`, exit=1, 파일 그대로(`log/03-…run2`). stdin 붙여넣기 방식으로도 멈추고 그 뒤 줄은 실행되지 않았다(`log/04`). L7의 "덮어쓰지 않고 멈춘다"는 확인됨. 설치본은 저장소의 스킬 폴더와 바이트까지 같다(`diff -r`). |
| 1. 설치 — 오버레이(L9-13) | **미실행 / 문서 결함** | 지시에 따라 실행하지 않았다. 문단만 읽고 판정했다. D8 참고. |
| 1. 설치 — Claude Code(L15-21) | **통과**(경미한 관찰 있음) | clone, 폴더 만들기, junction 모두 exit=0(`log/05-…run1`). 2회차는 `git clone` fatal과 `New-Item` DirectoryNotEmpty 오류가 나지만 **스크립트 종료 코드는 0**이고 손상은 없었다(`log/05-…run2`). 이 절은 "멈춘다"고 약속하지 않으므로 결함은 아니다. D5 참고. |
| 2. 첫 실행(L23-25) | **미실행**(에이전트 대행만) | 실제 Codex나 Claude Code 대화는 열지 않았다. SKILL.md L36에 따라 `templates/state-v0.2.0.example.json`을 `proj/product-definition/demo/state.json`으로 복사하는 데까지만 했다. |
| 3. 검증(L27-32) | **문서 결함**(경미) | `validate_state.py`: `valid:true`, exit=0. `validate_closure.py`: 빈 상태는 `closed:false`, **exit=1**(`log/10`, `log/11`). 승인된 예시는 `closed:true`, exit=0(`log/12`, `log/13`). 명령은 통한다. 하지만 문서에 기대 결과가 없어서, 처음 쓰는 사람은 exit=1이 고장인지 정상인지 알 수 없다(D3). |
| 4. 투영 갱신과 검사(L34-41) | **문서 결함** | 문서대로 실행하니 `{"ok": false, "error": "[Errno 2] No such file or directory: 'MASTER_PLANNING_SPEC.md'"}`, exit=2(`log/14`). `--help`를 보고 템플릿을 state.json 옆에 복사한 뒤 **그 폴더에서** 실행하니 `ok:true`, exit=0(`log/17`). 이어서 `projection_check.py`도 `ok:true`, exit=0(`log/18`). 이 절에서 두 번째 시도에 통과했다. D1, D2 참고. |
| 5. 버전 고정(L43-49) | **통과**(문서 표현 경미 결함) | `--pin`: `pinned:true`, `pinned_version:"2.0.0"`, exit=0. 다시 돌리면 `previous_pin:"2.0.0"`(`log/19`~`21`). 파일 위치는 `product-definition/<slug>/joeflow-project.json`이다. D4 참고. |
| 6. 업그레이드 — Codex 일반 복사(L55) | **문서 결함** | 백업 이름 바꾸기는 exit=True(`log/30`). 같은 폴더에서 1절 블록을 다시 실행하니 `fatal: destination path 'JOEFLOW' already exists` 다음에 `after-copy reached`, exit=0(`log/31`). **예전 clone에서 다시 설치된 것이다.** 이번에는 같은 버전이라 피해가 없었다. D6 참고. |
| 6. 업그레이드 — 오버레이(L56) | **미실행** | 지시에 따라 실행하지 않았다. |
| 6. 업그레이드 — Claude Code(L57) | **통과** | `git pull --ff-only` → `Already up to date.`, exit=0. junction을 통한 VERSION은 2.0.0(`log/32`). 새 커밋을 받는 실제 업그레이드는 확인하지 못했다. |
| 7. 제거 — Codex(L63) | **통과**(문서 표현 경미 결함) | 폴더를 지웠고 exit=True(`log/40`). 문서에 명령이 없어 `Remove-Item -Recurse -Force`를 내가 골랐다. 6절에서 만든 백업 폴더가 같은 `skills\`에 남는다는 말이 없다(D6). |
| 7. 제거 — Claude Code(L64) | **통과** | `cmd /c rmdir` 결과 exit=0, junction만 사라졌다. clone의 스킬 폴더(12개 항목)는 남았고 `git status`도 깨끗하다(`log/41`). L66의 "사용자 프로젝트는 그대로"도 확인했다(`proj/product-definition/minimal/*` 그대로). |
| 문서 전반: Windows 인코딩 | **문서 결함**(경미) | D7 참고. |

## 결함 목록

**D1 (4절, 문서 결함, 막힘).** 문서는 L37에서 `update_projection.py … --write`로 "읽기용 문서를 갱신"하라고만 한다. 실제로는 대상 파일이 이미 있어야 한다. 없으면 exit=2 `No such file or directory`로 끝난다. 처음 한 번은 `templates/master-planning-spec.md`와 `templates/planning-review-core.html`을 복사해야 한다는 사실을 QUICKSTART에서 알 수 없다. `--help`나 SKILL.md L115까지 가야 나온다. 템플릿에 IDENTITY/SOURCE-MAP 블록이 이미 있어 `--adopt` 없이 돌아간다는 점도 문서에 없다.

**D2 (4절, 문서 결함, 멈칫).** `--spec MASTER_PLANNING_SPEC.md`와 `--review planning-review-core.html`은 **현재 작업 폴더 기준** 경로다. README L27-30의 트리는 이 파일들이 `state.json` 옆에 있다고 보여 준다. 그런데 문서에는 "그 폴더에서 실행하라"거나 "경로를 state.json 옆으로 주라"는 말이 없다. 프로젝트 루트에서 그대로 치면 루트의 파일을 찾는다. 나는 `product-definition/minimal/`에서 실행하고 `STATE_JSON=state.json`으로 두었다.

**D3 (3절, 문서 결함, 경미).** `validate_closure.py`는 승인 전에 `closed:false`와 exit=1을 내는 것이 정상이다. 문서는 기대 결과도, 무엇이 통과인지도 말하지 않는다. 2절에서 "승인 전에는 구현을 시작하지 않습니다"라고만 한다.

**D4 (5·7절, 문서 결함, 경미).** L49는 "`state.json` 밖의 `joeflow-project.json`", L66은 "`product-definition/` 폴더와 `joeflow-project.json`은 그대로 남습니다"라고 쓴다. 이 표현은 파일이 `product-definition/` 바깥(프로젝트 루트)에 있는 것처럼 읽힌다. 실제 위치는 `product-definition/<slug>/joeflow-project.json`, 즉 state.json과 같은 폴더다(`log/19`의 `project_file`).

**D5 (1절 Claude Code, 관찰).** L18의 clone은 기본 브랜치를 받는다. 시험 시점의 main은 `v2.0.0-1-g6692f4d`였다. 스킬 폴더는 태그와 같았고, 바뀐 건 evals 영수증 두 파일뿐이다. 문서는 버전(태그)을 고르는 방법을 말하지 않는다. README의 Codex 블록도 마찬가지다. 지금은 피해가 없지만, main이 앞서 나가면 "2.0.0 빠른 시작"으로 다른 버전이 깔린다.

**D6 (6절 Codex 업그레이드, 문서 결함, 실제 위험).** 문서 L55는 "새로 clone한 저장소에서 1절의 일반 복사를 다시 실행"이라고 한다. 그런데 1절 블록은 `git clone`을 현재 폴더에 하고 곧바로 `Set-Location JOEFLOW`를 한다. 처음 설치한 폴더에서 다시 붙여 넣으면 이렇게 된다(`log/31`).
- clone만 실패한다.
- **예전 clone에서 다시 복사한다.**
- 경고 없이 exit=0으로 끝난다.

문서는 "빈 폴더에서", "기존 clone을 지우거나 `git pull` 후에" 같은 전제를 말하지 않는다. "다른 이름으로 옮겨 백업"도 어디로 옮길지 말하지 않는다. 같은 `…\.codex\skills\` 안에 두면 `name: joewrks-product-definition`인 SKILL.md가 둘이 된다. Codex가 이걸 중복 스킬로 읽는지는 확인하지 않았다(Codex를 실행하지 않음). 7절 제거도 이 백업을 언급하지 않는다.

**D7 (문서 전반, 문서 결함, 경미).** QUICKSTART와 README 모두 `PYTHONIOENCODING`도, 콘솔 인코딩도 언급하지 않는다. 관찰한 결과는 다음과 같다.
- (a) Git Bash에서 그대로 실행하면 정상이다. 파일 리디렉션도 UTF-8로 정상이다.
- (b) PowerShell 5.1이 출력을 받는 경우(`$out = python …update_projection.py …` 다음 `Out-File`)에는 `·`가 `쨌`로, `승인됨`이 `?뱀씤??`로, `→`가 `??`로 깨진다(`log/24`). 스크립트는 UTF-8로 내보내는데 PowerShell은 `[Console]::OutputEncoding`(ks_c_5601-1987)으로 읽기 때문이다.
- (c) `PYTHONIOENCODING=utf-8`을 넣고 다시 돌려도 **똑같이 깨진다**(`log/25`). 그러니 그 변수는 해결책이 아니다. PowerShell 쪽에서 `[Console]::OutputEncoding = [Text.Encoding]::UTF8`을 해야 할 것으로 추정하지만 시험하지 않았다.

JSON 키와 숫자는 ASCII라서 `ok`, `exit` 판정에는 영향이 없다. 한국어 diff와 메시지를 읽을 때만 문제가 된다. 실제 대화형 콘솔에 바로 찍히는 경우는 확인하지 않았다.

보조 관찰: README 블록을 BOM 없는 UTF-8 `.ps1`로 저장해 `powershell -File`로 돌리면, `throw` 메시지의 한국어가 깨져서 나온다(`log/03-…run2`). 이건 내 실행 방식에서 생긴 일이다. 문서는 붙여 넣기를 전제한다. BOM을 붙인 스크립트(`log/05`)에서는 Python 쪽 문제가 없었다.

**D8 (1절 오버레이, 문서 결함, 미실행 판정).** L9가 적은 안전장치는 "직전 버전 영수증이 있어야 하고, 아니면 멈춘다", "다른 사람의 설치에는 쓰지 마세요"다. 다른 사람이 실수로 돌리는 것을 막기에는 다음이 빠졌다.
- (a) 영수증 `evals/joeflow-u1-personal-install/personal-install-overlay-receipt.json`은 **공개 저장소에 커밋돼 있다.** 그래서 누가 clone하든 "영수증이 있다"는 조건이 채워진다. 파일이 있다는 것만 확인했고 내용은 읽지 않았다. 게다가 태그 `v2.0.0`의 영수증은 1.7.3 상태이고, main에서는 6692f4d가 2.0.0 상태로 갱신했다. 그래서 같은 명령이라도 체크아웃한 위치에 따라 "멈춤 조건"이 달라진다.
- (b) 스크립트가 **어디에 쓰는지**(`~\.codex\skills\…`인지, `CODEX_HOME`을 따르는지) 적혀 있지 않다.
- (c) 영수증이 직전 버전 상태일 때, 자기 `~\.codex`에 다른 설치본이 있는 사람에게 무슨 일이 생기는지 적혀 있지 않다. 덮어쓰는지, 해시를 대조하는지 알 수 없다.
- (d) `<2.0.0 릴리스 커밋>` 자리에 무엇을 넣는지(태그 커밋 89cb012인지) 문서만으로는 정하기 어렵다.

그래서 "영수증이 맞지 않으면 쓰지 않는다"는 말이 다른 사람에게도 보호가 되는지는 **문서로 판단할 수 없다.**

## 확인된 것

- README Codex 블록은 `CODEX_HOME`이 있으면 그것을 따른다. 그래서 문서 명령을 고치지 않고 대체 경로에 설치할 수 있었다. 두 번째 실행은 덮어쓰지 않고 exit=1로 멈췄다.
- Claude Code의 junction 방식 설치, `git pull --ff-only`, `cmd /c rmdir`(junction만 지우고 clone은 남음)이 모두 문서대로 동작했다.
- `validate_state`, `validate_closure`, `update_projection --write`, `projection_check`, `joeflow_version --pin`이 junction 경로와 복사 경로 모두에서 exit 코드대로 동작했다. `PYTHONIOENCODING` 없이 Python 인코딩 예외는 없었다. 스크립트가 쓴 HTML과 MD는 UTF-8로 정상이고 한국어 `승인됨`이 보존됐다.
- `--pin`을 두 번 실행해도 안전했다(`previous_pin`이 보고됨).

## 확인되지 않은 것

- 2절 첫 실행 대화(Codex나 Claude Code에서 스킬이 실제로 불리고 질문하는지). 대화를 열지 않았다.
- 실제 DISCOVER→APPROVE 흐름으로 만든 state. 4·5절은 저장소 예시 `templates/examples/closed-minimal.state.json`(이미 승인 기록이 있음)으로 대신했다.
- 오버레이 설치기의 실제 동작(지시에 따라 실행하지 않음).
- 새 커밋이 있을 때의 업그레이드(`git pull`이 실제로 받아 오는 경우).
- 대화형 PowerShell 콘솔에 사람이 직접 붙여 넣는 경우의 동작(`throw` 뒤 줄이 실행되는지, 화면 출력 인코딩). 나는 `-File`과 `-Command -`(stdin)로만 흉내 냈다.
- Codex가 `skills\` 안의 백업 폴더를 중복 스킬로 읽는지.
- `[Console]::OutputEncoding = UTF8`로 D7이 해결되는지.

## 내가 대신 내린 결정

- **Codex 설치 대상:** `~\.codex\skills\` 대신 `<cwd>\codex-home\skills\joewrks-product-definition\`을 썼다. README 블록을 고치지 않고 **프로세스 범위에서만** `$env:CODEX_HOME`을 설정했다. 전역 설정은 바꾸지 않았다.
- **Codex 첫 설치 clone 위치와 버전:** `<cwd>\work-codex\`에서 실행했다. README에는 없는 `git checkout v2.0.0`을 첫 실행 스크립트(`runner/codex-install.ps1`)에 내가 넣었다. stdin 방식 재실행(`runner/codex-install-paste.txt`)에는 넣지 않았다.
- **Claude Code:** `$HOME\src\JOEFLOW` 대신 `<cwd>\src\JOEFLOW`, `$HOME\.claude\skills` 대신 `<cwd>\claude-skills`를 썼다. junction은 지시에 적힌 `cmd /c mklink /J` 대신 **문서 L20의 `New-Item -ItemType Junction`을 경로만 바꿔** 썼다. 문서 명령 자체를 시험하려는 것이었다. 결과는 같은 junction이다(`dir`에 `<JUNCTION>`으로 표시됨).
- **2절 에이전트 역할:** SKILL.md L36에 따라 빈 템플릿 state를 만들었다(`proj/product-definition/demo`). 승인된 상태가 필요한 4·5절은 저장소의 `closed-minimal` 예시를 `proj/product-definition/minimal/state.json`으로 복사해 썼다. **사용자 역할로 승인을 따로 주거나 기록하지 않았다.** 예시에 들어 있던 승인 기록을 그대로 썼을 뿐이다.
- **4절 재시도:** 템플릿 두 파일을 state.json 옆에 복사했다. 실행 폴더는 `product-definition/minimal`, `STATE_JSON=state.json`으로 두어 `--spec`, `--review` 인수를 문서 글자 그대로 유지했다.
- **6절 백업 위치:** 문서에 없어서 같은 `skills\` 안에 `joewrks-product-definition.bak-2.0.0`이라는 이름으로 두었다(새 사용자가 가장 흔히 할 선택으로 보고 고름).
- **7절 Codex 제거 명령:** 문서에 없어서 `Remove-Item -Recurse -Force`(junction이 아닌 진짜 폴더)를 썼다. 백업 폴더는 문서가 언급하지 않으므로 지우지 않았다.

## 사고 기록(규칙 관련)

정리 단계의 bash 명령 한 줄에 `cmd /c rmdir $HOME\.claude\skills\joewrks-product-definition`을 PowerShell로 부르는 **실수 줄**을 써 넣었다. **실제 전역 경로를 가리키는 줄이었다.** bash 구문 오류(`unexpected EOF while looking for matching backtick`)로 그 줄은 파싱 단계에서 실패해 **실행되지 않았다.** 앞줄만 실행된 것이 출력으로 확인된다. 그 뒤 `Test-Path "$HOME\.claude\skills\joewrks-product-definition"`로 존재 여부만 읽었고 결과는 `False`였다. 실행 전 상태를 몰라서 이 값만으로 "전에도 없었다"고 증명할 수는 없다. 다만 명령이 실행되지 않았다는 근거는 셸의 파싱 오류다. 금지 경로(`D:\JOEWRKS\.claude\skills` 등)는 읽지도 쓰지도 않았다.

## scratch(cwd) 안에 남긴 것

| 경로(cwd 기준) | 내용 |
|---|---|
| `report.md` | 이 보고서 |
| `log\` | 명령 로그 30개(종료 코드 포함): `01`~`05` 설치, `10`~`25` 3~5절과 인코딩(`22`·`23`은 테스트 설계 오류로 무효, `24`·`25`가 유효), `30`~`32` 업그레이드, `40`~`41` 제거, `50` 오버레이 파일 존재 확인 |
| `runner\` | 내가 쓴 실행 보조 파일: `run.sh`, `codex-install.ps1`, `codex-install-paste.txt`, `claude-install.ps1`, `ps-encoding.ps1`, `ps-enc2.ps1` |
| `JOEFLOW-clone\` | 1단계 clone(태그 v2.0.0 체크아웃, detached) |
| `work-codex\JOEFLOW\` | README 블록이 만든 clone(v2.0.0 체크아웃) |
| `src\JOEFLOW\` | Claude Code 절의 clone(main, 6692f4d) |
| `codex-home\skills\joewrks-product-definition.bak-2.0.0\` | 6절 백업(문서상 남는 것) |
| `claude-skills\` | 빈 폴더(junction 제거 후) |
| `proj\` | 임시 사용자 프로젝트(git init, 커밋 없음): `README.md`, `product-definition\{demo,minimal,enc-noenv,enc-env}\` |

**junction:** 내가 만든 junction은 `claude-skills\joewrks-product-definition` 하나뿐이다. `cmd /c rmdir`로 지웠다. `Get-ChildItem -Recurse -Attributes ReparsePoint` 결과 cwd 안에 reparse point는 0개다.

## 내가 쓴 경로(전부 cwd `D:\JOEWRKS\.local\v2-tests-20261119\docs-joeflow\` 안)

- `report.md`, `log\*`, `runner\*`
- `JOEFLOW-clone\`, `work-codex\`, `src\`
- `codex-home\`(설치, 백업, 제거), `claude-skills\`(junction 생성과 제거)
- `proj\`
- (지운 것) `codex-home.bak-before-paste\`(실수로 만든 사본, 바로 지움)

cwd 밖에 쓴 것은 없다. git push, GitHub 쓰기, pip install, PATH나 전역 설정 변경, 유료 외부 실행은 하지 않았다.
