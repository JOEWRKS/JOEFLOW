# Full regression environment

Run from a clean, committed JOEFLOW checkout. The suite runs local synthetic
checks and reads historical fixtures; it does not require a live reviewer
service. Do not run concurrently with editing: one runner integrity test
temporarily changes a source file and restores its original bytes and mtime
in `finally`.

## Windows checkout bytes

`.gitattributes` fixes LF for `reviewer_runner/**` and its canonical capability
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
global Git configuration.

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
