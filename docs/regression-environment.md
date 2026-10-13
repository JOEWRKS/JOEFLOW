# 전체 회귀 환경

## 1. 핵심 요약

- 실행 위치: clean·committed JOEFLOW checkout
- 검사 구성: local synthetic check와 historical fixture
- Live reviewer service: 불필요
- 편집과 동시 실행: 금지
- 사유: runner integrity test 한 건이 source file을 임시 변경한 뒤 `finally`에서 원래 bytes와 mtime 복원

## 2. 설계 목적

- Canonical source byte와 executable mode의 Git 기준 검증
- CLI output byte와 preserved evidence의 일치 검증
- Historical M6 replay의 정확한 commit·tree·artifact identity 보존
- Focused regression과 full regression의 순차 실행
- 누락 fixture·skip·환경 제한의 명시적 보고

## 3. 주요 기능

### Windows checkout byte 보호

- `.gitattributes`: `reviewer_runner` Python/JSON file과 canonical capability evidence의 LF 고정
- Audit: raw source byte·executable mode를 Git과 비교
- CLI output byte: preserved evidence와 비교
- Audit check 변경 금지
- Evidence hash 갱신 또는 CRLF 적응 목적 assertion skip: 금지
- 신규 checkout: `core.autocrlf=true` 환경에서도 정책 적용
- 기존 checkout: refresh 전까지 과거 CRLF byte 잔존 가능

### Historical replay 보호

- M6 historical input의 exact commit·tree·artifact byte·approval·definition digest 검증
- 개발 checkout reset 금지
- 필요 시 exact commit 기반 separate detached local clone 재구성
- 재구성 snapshot에 대한 product runtime action·편집 금지

### 결과 보존

- Focused regression과 full regression의 동일 PowerShell process 순차 실행
- Source·snapshot identity의 실행 전후 대조
- Command·Python version·stdout/stderr·exit code·skip reason 보존

## 4. 사용 방법

### Windows checkout byte refresh

Refresh 전 필수 조건:

- 모든 사용자 변경 저장
- 대상 file의 committed blob 차이가 CRLF/LF 변환뿐인지 확인
- 같은 commit의 해당 file만 refresh
- 다른 차이 overwrite 금지
- 정확한 path만 `git add --renormalize -- <verified paths>` 적용
- Staged source/evidence blob change 없음 확인
- 미갱신 index metadata로 인한 audit read-only Git status의 modified 오판 방지
- Global Git configuration 변경 금지
- Checkout exclusive access 확보

아래 PowerShell recipe의 검사 범위: 11개 path. 쓰기 전 staged edit, non-line-ending change, symlink, changed HEAD 거부. 출력 범위: path/hash evidence. 출력의 regression log 보존.

```powershell
@'
from pathlib import Path
import hashlib, json, subprocess
root = Path.cwd().resolve()
def git(*args):
    return subprocess.check_output(['git', '-C', str(root), *args])
prefix = 'skills/joewrks-product-definition/reviewer_runner/'
paths = [prefix + p for p in [
    '__init__.py', 'backend.py', 'controller.py', 'evidence.py', 'identity.py',
    'preflight.py', 'request.py', 'response.py', 'semantic_review.py',
    'schemas/reviewer-runner-receipt-v1.schema.json',
]] + ['evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json']
head = git('rev-parse', 'HEAD').decode().strip()
git('diff', '--cached', '--exit-code', head, '--', *paths)
original, expected = {}, {}
for name in paths:
    path = root / name
    if not path.is_file() or path.resolve() != path:
        raise SystemExit('Not a regular tracked location: ' + name)
    original[name] = path.read_bytes()
    expected[name] = git('cat-file', 'blob', head + ':' + name)
    if b'\r\n' in expected[name] or original[name].replace(b'\r\n', b'\n') != expected[name]:
        raise SystemExit('Not an LF-only refresh; preserve changes: ' + name)
if git('rev-parse', 'HEAD').decode().strip() != head:
    raise SystemExit('HEAD changed; stop and inspect')
for name in paths:
    if (root / name).read_bytes() != original[name]:
        raise SystemExit('File changed; stop and inspect: ' + name)
for name in paths:
    (root / name).write_bytes(expected[name])
git('add', '--renormalize', '--', *paths)
git('diff', '--cached', '--exit-code', head, '--', *paths)
for name in paths:
    if (root / name).read_bytes() != expected[name]:
        raise SystemExit('Post-refresh byte mismatch: ' + name)
print(json.dumps([{
    'path': name,
    'beforeSha256': hashlib.sha256(original[name]).hexdigest(),
    'afterSha256': hashlib.sha256(expected[name]).hexdigest(),
} for name in paths], indent=2))
'@ | python -B -
if ($LASTEXITCODE -ne 0) { throw 'Checkout refresh failed; inspect before continuing' }
```

Refresh 결과:

- Checkout representation만 변경
- Guarded index refresh의 staged source/evidence change: 0 필수
- Recipe 중 I/O failure 발생 시 testing 중지 및 affected path 확인 후 재시도

### Required M6 historical replay

`JOEWRKS_M6_PHASE_B_WORKTREE` 필수 identity:

- commit `d38b0ca04768888c47e658c79f41e1cec0a7a1ce`
- tree `40749d900b98936cf694b0c96db7897011cddae8`
- unchanged committed dogfood artifact byte, approval digest, definition digest

현재 M6 development checkout: historical input 아님. Reset 금지. Original checkout 부재 및 exact commit의 local 존재 시 separate detached local clone 재구성 허용. Git 기반 재구성이며 과거 physical checkout 생존의 증명으로 사용 금지. 모든 active repository 밖의 새 absent destination 사용.

```powershell
$regressionSource = (Get-Location).Path
$regressionSnapshot = 'D:\QA-snapshots\joeflow-m6-phase-b'
if (Test-Path -LiteralPath $regressionSnapshot) { throw 'Use a new snapshot path' }
git clone --no-checkout --no-hardlinks -- $regressionSource $regressionSnapshot
if ($LASTEXITCODE -ne 0) { throw 'Snapshot clone failed' }
git -C $regressionSnapshot -c core.autocrlf=false checkout --detach d38b0ca04768888c47e658c79f41e1cec0a7a1ce
if ($LASTEXITCODE -ne 0) { throw 'Historical checkout failed' }
```

- Per-command checkout setting: current attribute 이전 historical artifact의 LF 보존
- Source checkout 또는 global configuration 변경 없음
- Replay test의 실행 전 검사: exact HEAD, tree, clean status, artifact hash, approval identity
- Replay test의 실행 후 검사: 모든 tracked-file hash와 checkout identity

### 회귀 실행 및 결과 보존

동일 PowerShell process에서 exact snapshot path 설정 후 JOEFLOW source checkout 기준 순차 실행:

```powershell
$env:JOEWRKS_M6_PHASE_B_WORKTREE = $regressionSnapshot
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m unittest tests.test_reviewer_runner_audit tests.test_downstream_v21_dogfood_replay -v
if ($LASTEXITCODE -ne 0) { throw 'Focused regression failed' }
python -B -m unittest discover -s tests -p 'test*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
```

- 환경 변수 적용 범위: 현재 shell과 child process
- 완료 후 기존 값 복원 또는 shell 종료
- 보존 항목: full command, Python version, source commit/tree, stdout/stderr, exit code, skip reason, source/snapshot identity before/after

## 5. 도구 간 연결

| 도구·입력 | 역할 | 필수 경계 |
| --- | --- | --- |
| Git | committed byte·tree·mode authority | global 설정 변경 금지 |
| Python `unittest` | focused/full regression 실행 | `-B`, 순차 실행 |
| `JOEWRKS_M6_PHASE_B_WORKTREE` | historical M6 replay input | exact detached snapshot |
| `JOEWRKS_FROZEN_A_ROOT` | frozen A runtime regression input | 미제공 시 기존 skip 보고 |
| `JOEWRKS_FROZEN_B_WORKTREE` | frozen B runtime regression input | 미제공 시 기존 skip 보고 |
| Regression log | 실행·환경·identity evidence | 명령과 skip reason 포함 |

## 6. 한계

- Missing M6 input: failure 유지
- Frozen A/B runtime regression: `JOEWRKS_FROZEN_A_ROOT`, `JOEWRKS_FROZEN_B_WORKTREE` 별도 필요
- Frozen A/B 입력 부재 시 existing skip 보고
- 해당 skip을 포함한 `OK`: frozen A/B runtime scenario 검증으로 사용 금지
- Checkout refresh: 실제 source/evidence 의미 변경 수단으로 사용 금지
- Historical clone: 과거 physical checkout 생존 증거로 사용 금지
- 동시 편집 또는 비독점 checkout에서 runner integrity test 실행 금지
