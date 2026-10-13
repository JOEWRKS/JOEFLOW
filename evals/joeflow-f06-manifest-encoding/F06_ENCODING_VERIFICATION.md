# F06 Approval Manifest CLI encoding verification

## Scope and baseline

- Source baseline: `origin/main` / `a1f7c2c44becd906774bc948d2e0ac6f6a65ed8a`
- Branch: `codex/joeflow-f06-manifest-encoding`
- Baseline CLI SHA-256: `ce818206a33e4a24d8937902d9b8280aa057d3155d21aa0a2623590896d7146b`
- Change boundary: ASCII-safe JSON emission and standard-stream write-failure containment only. No schema, Manifest meaning, digest, approval, Closure, state, file-output option, or product change.

## Permanent RED evidence

Command run before production changes:

```text
python -m unittest tests.test_approval_manifest_v020.ApprovalManifestV020Test.test_cli_success_is_ascii_safe_under_cp949_and_utf8_with_unicode_state_and_path tests.test_approval_manifest_v020.ApprovalManifestV020Test.test_output_write_failures_are_contained_and_partial_output_is_not_success
```

Result: exit `1`, 2 tests, 4 assertion failures.

- CP949 valid-success case returned `1`, stdout was empty, and stderr contained `UnicodeEncodeError: 'cp949' codec can't encode character '\u2014'` at the old `ensure_ascii=False` stdout write.
- UTF-8 succeeded but emitted non-ASCII bytes, violating the new locale-independent representation contract.
- `_emit_json` was absent, so BrokenPipe/OSError containment was not implemented.
- Independent real-OS pre-fix PIPE evidence later found a closed stdout pipe returned `120`: the structured `output_write_failed` stderr line was followed by Python's shutdown reflush error. Preserved external evidence: `D:/JOEWRKS/JOEQASAM/evidence/t035-joe-implementation/f06-io.json` and `review-f06-io.py`.

## Implemented representation contract

- Every success/error payload is serialized before writing as compact, sorted, `ensure_ascii=True`, `allow_nan=False` JSON plus one newline.
- Exit/channel meanings remain: success stdout/0; semantic or lifecycle rejection stdout/1; usage, read, or output failure stderr/2.
- BrokenPipe, OSError, Unicode, serialization, short-write, and flush failures return a controlled failure without traceback.
- A failed standard-stream descriptor is redirected to `os.devnull` so interpreter shutdown cannot reflush the already-failed pipe and replace exit `2` with `120`.
- A consumer must discard partial stdout when exit is `2`.
- The input state remains byte-identical; no `--output` or other file-writing path was added.

## GREEN evidence

```text
python -m unittest tests.test_approval_manifest_v020.ApprovalManifestV020Test.test_output_write_failures_are_contained_and_partial_output_is_not_success tests.test_approval_manifest_v020.ApprovalManifestV020Test.test_closed_stdout_pipe_returns_structured_exit_two_without_shutdown_reflush
```

Result: exit `0`, 2/2 passed. The real OS pipe begins with no reader, returns exact exit `2`, and emits only the ASCII-safe `{"error":"output_write_failed"}` JSON line on stderr.

```text
python -m unittest tests.test_approval_manifest_v020
```

Result: exit `0`, 28/28 passed. Coverage includes CP949/UTF-8, Korean/em dash/non-BMP data, Unicode paths, success, invalid/not-ready/malformed/read/usage paths, in-memory redirect, real closed PIPE, BrokenPipe, OSError, partial writes, parsed packet equality, digest/commitment equality, channel/exit behavior, and input immutability.

```text
python -m unittest tests.test_skill_package
```

Result: exit `0`, 6/6 passed.

```text
git diff --check
```

Result: exit `0`.

Independent Manager candidate checks also passed 10/10 success/error × CP949/UTF-8 cases and a CP949 file redirect with parsed packet identity preserved. External evidence: `D:/JOEWRKS/JOEQASAM/evidence/t035-joe-implementation/f06-candidate.json` and `f06-io.json`.

## Full-suite result and separated baseline limitations

```text
python -m unittest discover -s tests -p "test*.py"
```

Result: exit `1`; 1,104 tests ran in 469.914 seconds, with 5 failures, 7 errors, and 1 skip. No F06 test failed.

- Eleven findings are in `test_reviewer_runner_audit`. All reach the same frozen-source check or a dependent assertion. `core.autocrlf=true`; all 10 tracked `reviewer_runner` files have live-byte blob IDs different from their index blobs although `git diff origin/main` is empty for the runner, audit script, and tests. A representative file has 44 CRLF pairs in the live checkout and 0 in the `origin/main` blob. The isolated representative test reproduces `live runner source bytes or mode differ from revision`.
- One failure is `M6DogfoodReplayTests.test_preserved_phase_b_replays_read_only_through_21`; `JOEWRKS_M6_PHASE_B_WORKTREE` is absent and the test deliberately returns `M6_REPLAY_EVIDENCE_UNAVAILABLE`.

These are recorded as baseline/environment limitations, not as passing tests and not as F06 regressions. The relevant failure paths have no working-tree diff from `origin/main`.

## Candidate and unchanged authorities

- Candidate CLI SHA-256: `6bf4cc41f3df6939093b35455076afb0307104dd00e464f49eb901d031d32c14`
- Candidate test SHA-256: `3088c0e081fd69f9a281e62ed71776da4fd9dc2ef8bfc00877063acd8678534c`
- Candidate workflow SHA-256: `4946c080a0796c1b4af7b285eeac6558fc5e90109e9bf479622ddb2177f3e216`
- Installed personal CLI remains baseline SHA-256 `ce818206a33e4a24d8937902d9b8280aa057d3155d21aa0a2623590896d7146b`; managed installation was not changed before independent review.
- FnBShop canonical state remains SHA-256 `5cbb9d5a0bafc914dd4e6630f4f3ca6c30491d8f9fa43cf8647f86232c26d86f`; it was read only.
- The F02 draft fixture was not committed because the contract owner is correcting independently found counterexamples. No provisional product mapping was promoted as authority.
