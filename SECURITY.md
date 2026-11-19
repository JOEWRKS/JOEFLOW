# JOEFLOW 보안 안내

JOEFLOW는 네트워크에 접속하지 않고, 표준 라이브러리만 쓰는 Python 스크립트와 에이전트가 읽는 문서로 이루어진 로컬 도구입니다. 2026-11-19 점검에서 비밀 값은 작업 트리와 이력 모두에서 0건이었습니다. 개인 식별자(Windows 사용자 이름이 든 경로)는 작업 트리에 4회 남아 있고, git 이력과 커밋 메타데이터에도 남아 있습니다. 이력은 다시 쓰지 않았습니다.

## 1. 점검한 것과 결과 (2026-11-19, 커밋 399개 기준)

| 점검 | 방법 | 결과 |
| --- | --- | --- |
| 비밀 값 | AWS `AKIA…`, GitHub `ghp_`/`github_pat_`, `sk-`/`sk-ant-`, Slack `xox?-`, Google `AIza…`, `BEGIN … PRIVATE KEY`, 접속 문자열, `password=`/`api_key=`/`secret=`, `Bearer` 패턴을 작업 트리와 `git log --all -p`에서 검색 | 실제 값 0건. `sk-ant-test-*` 같은 테스트용 가짜 표식만 있음 |
| 비밀 파일 | `.env`, `*.pem`, `*.key`, `id_rsa`, `*.p12`/`*.pfx` | 0개 |
| 위험 호출 | `shell=True`, `os.system`, `os.popen`, `eval(`, `exec(`, `pickle`, `yaml.load`, 네트워크 모듈, XML/HTML 파서 (`tests/` 제외) | 0건. `urllib`은 `urllib.parse`의 인코딩 함수 1곳뿐 |
| 개인 식별자(작업 트리) | Windows 사용자 이름, `C:/Users`, `C:\Users`, gmail 주소 | 2.0 정리 전 10개 파일 13회 → 정리 후 3개 파일 4회. 본문의 gmail 주소 0건 |
| 의존성 | 매니페스트 검색 | `requirements*.txt`, `pyproject.toml`, `package.json`, lock 파일 없음 |
| CI | `.github/workflows` | 없음 (권한·secrets 사용 없음) |

## 2. 남아 있는 것

가리지 않은 이유는 모두 같습니다. **git 이력을 다시 쓰지 않기로 했고**, 테스트가 바이트를 고정한 파일은 고치면 검사가 깨집니다.

- **작업 트리 3개 파일 4회**: `evals/semantic-review-v0.4.3/evidence/calibration-disposition/` 아래 2개 파일은 테스트가 폴더 tree 해시로 고정합니다. `evals/joeflow-regression-environment-20261013/focused-red.log`(2회)는 `.gitattributes`가 바이트를 고정한 실행 기록이라 그대로 두었습니다. 셋 다 임시 폴더 경로(`…\AppData\Local\Temp`) 안에 사용자 이름이 들어 있는 형태입니다.
- **git 이력**: 사용자 이름이 든 변경 줄 4,348줄(커밋 20개). 대부분은 지금은 지운 Codex 원시 이벤트 로그(`evals/semantic-review-v0.4.3/calibration/run-01/raw-outputs/*/codex-events.jsonl`)에서 나옵니다. 원격 브랜치에도 남아 있을 수 있습니다.
- **커밋 메타데이터**: 모든 커밋의 작성자 정보에 개인 이메일이 있고, 일부 커밋은 실명 작성자 이름을 씁니다.

## 3. 스크립트의 신뢰 경계

| 스크립트 | 다루는 입력 | 쓰는 곳 |
| --- | --- | --- |
| `scripts/projection_check.py` | 신뢰할 수 없는 HTML·Markdown 투영 문서와 `state.json` | **쓰지 않음**(stdout만). HTML 파서·`eval`·네트워크 없이 `re`와 문자열 함수로만 읽고, 사용자 정규식을 받지 않음. 아주 큰 입력에서 정규식 처리 시간은 측정하지 않음 |
| `open_revision.py`, `record_approval.py`, `refresh_bindings.py`, `project_pin.py` | 사용자 프로젝트의 `state.json`, patch JSON | 대상 파일 옆 임시 파일 → `os.replace`(원자적 교체). 쓰는 곳은 사용자 프로젝트뿐 |
| `migrate_state.py` | 기존 state | 새 출력 경로(임시 파일 → `os.link`, 기존 파일을 덮지 않음) |
| `update_projection.py`, `new_records.py`, `supersede_records.py`, `draft_freeze.py`, `compact_coverage.py` | state, 인자 | 인자로 받은 사용자 프로젝트 경로에 직접 씀 |
| `downstream/adapter_runtime.py` | **호출자가 계약에 정의한 어댑터 명령(argv 리스트)** | 임시 폴더 안 JSONL. `subprocess.run(list, timeout=60)`, shell 미사용. 무엇을 실행할지는 호출자가 정하므로 신뢰 경계는 호출자에게 있음 |
| `scripts/audit_reviewer_runner.py`, `reviewer_runner/evidence.py` | 저장소 경로 | `git`을 리스트 인자로 실행(shell 미사용) |
| `evals/**/install_*.py` (개인 Codex 오버레이 설치기) | 인자 `<TIP>`(`git rev-parse --verify`로 확인), git 객체 | `~/.codex/skills/joewrks-product-definition/`, `~/.codex/skills-backups/`, 저장소 안 영수증 JSON만. 다운로드 없음. `patch`는 임시 폴더의 파일 1개에만 적용. 영수증에는 홈 경로를 `~`로 적음 |

## 4. 의존성

외부 패키지를 쓰지 않습니다. `tests/test_skill_package.py`가 `skills/joewrks-product-definition/scripts/*.py`의 import를 AST로 읽어 표준 라이브러리와 형제 모듈만 허용하고, `__import__`로 숨긴 import도 막습니다. 이 검사는 `scripts/` 폴더만 봅니다. `downstream/adapters/vitest*`는 vitest를 쓰지만 버전 고정 매니페스트가 없고, 외부 고정 저장소에서만 실행됩니다. 매니페스트가 없어 `pip audit`·`npm audit`은 돌리지 않았습니다.

## 5. 보고 방법

GitHub 저장소 [JOEWRKS/JOEFLOW](https://github.com/JOEWRKS/JOEFLOW)의 Security 탭에서 비공개 보고(Private vulnerability reporting)를 이용해 주세요. 그 기능이 꺼져 있으면, 비밀 값이나 개인 정보를 적지 않은 Issue로 "보안 연락 요청"만 남겨 주시면 연락 경로를 안내합니다. 공개 Issue에 재현 코드나 민감한 값을 올리지 마세요.
