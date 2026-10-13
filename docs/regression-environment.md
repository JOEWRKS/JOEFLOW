# Full regression environment

Run from a clean, committed JOEFLOW checkout. The suite runs local synthetic
checks and reads historical fixtures; it does not require a live reviewer
service. Do not run concurrently with editing: one runner integrity test
temporarily changes a source file and restores its original bytes and mtime
in `finally`.

## Windows checkout bytes

`.gitattributes` fixes LF for Python/JSON files in `reviewer_runner` and its canonical capability
evidence. The audit deliberately compares raw source bytes and executable mode
against Git, and compares CLI output bytes against the preserved evidence.
Keep those checks unchanged. Do not update evidence hashes or skip assertions
to accommodate CRLF conversion.

New checkouts apply this policy even when `core.autocrlf=true`. An existing
checkout may retain its old CRLF bytes until refreshed. Before refreshing, save
all user changes and verify that each affected file differs from its committed
blob only by CRLF/LF conversion. Refresh only those files from the same commit;
never overwrite other differences. Refresh Git's index metadata for those exact
paths with `git add --renormalize -- <verified paths>` and confirm there is no
staged source/evidence blob change. Otherwise the old index metadata can still
report modified files to the audit's read-only Git status call. Do not change
global Git configuration. With exclusive access to the checkout, this PowerShell
recipe checks all 11 paths before writing any of them. It rejects staged edits,
non-line-ending changes, symlinks, and a changed HEAD. It prints only path/hash
evidence; keep this output with the regression log.

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

This refresh changes checkout representation only. The guarded index refresh
must stage no source or evidence change. If an I/O failure interrupts the recipe,
stop testing and inspect the affected paths before retrying.

## Required M6 historical replay

`JOEWRKS_M6_PHASE_B_WORKTREE` must point to a clean checkout with:

- commit `d38b0ca04768888c47e658c79f41e1cec0a7a1ce`
- tree `40749d900b98936cf694b0c96db7897011cddae8`
- unchanged committed dogfood artifact bytes, approval and definition digests.

The current M6 development checkout has advanced and is not this historical
input. Do not reset it. If the original checkout is unavailable but the exact
commit is present locally, reconstruct a separate detached local clone. This
is a reconstruction from Git, not proof that the old physical checkout survives.
Use a new, absent destination outside every active repository. In PowerShell:

```powershell
$regressionSource = (Get-Location).Path
$regressionSnapshot = 'D:\QA-snapshots\joeflow-m6-phase-b'
if (Test-Path -LiteralPath $regressionSnapshot) { throw 'Use a new snapshot path' }
git clone --no-checkout --no-hardlinks -- $regressionSource $regressionSnapshot
if ($LASTEXITCODE -ne 0) { throw 'Snapshot clone failed' }
git -C $regressionSnapshot -c core.autocrlf=false checkout --detach d38b0ca04768888c47e658c79f41e1cec0a7a1ce
if ($LASTEXITCODE -ne 0) { throw 'Historical checkout failed' }
```

The per-command checkout setting preserves LF in historical artifact files
whose old revision predates the current attributes. It does not change the
source checkout or global configuration. The replay test checks exact HEAD,
tree, clean status, artifact hashes and approval identity before translation;
it checks all tracked-file hashes and checkout identity again after replay.
Do not run product runtime actions or edit the reconstructed snapshot.

## Execute and retain the result

In the same PowerShell process, set the exact snapshot path, then run focused
and full regression sequentially from the JOEFLOW source checkout:

```powershell
$env:JOEWRKS_M6_PHASE_B_WORKTREE = $regressionSnapshot
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m unittest tests.test_reviewer_runner_audit tests.test_downstream_v21_dogfood_replay -v
if ($LASTEXITCODE -ne 0) { throw 'Focused regression failed' }
python -B -m unittest discover -s tests -p 'test*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
```

These environment settings apply to this shell and its children only. Restore
prior values or close the shell afterward. Capture the full command, Python
version, source commit/tree, stdout/stderr, exit code, skip reasons, and source
and snapshot identities before/after. Missing M6 input must remain a failure.
The separate frozen A/B runtime regression requires `JOEWRKS_FROZEN_A_ROOT` and
`JOEWRKS_FROZEN_B_WORKTREE`; report its existing skip when these are unavailable.
An OK result with that skip does not verify the frozen A/B runtime scenario.
