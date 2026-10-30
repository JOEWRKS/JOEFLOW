# JOEFLOW U1 personal install record

Date: 2026-10-26, updated 2026-10-28 twice, 2026-10-29 twice and 2026-10-31 (Asia/Seoul)

## Installed identity

- Personal install: `C:/Users/tjdwo/.codex/skills/joewrks-product-definition`
- Base: v1.1.0 install, source commit `e3be5d11fe0e8f5b79c42e35a0bcb157f5bdda4a` ([v1.1.0 record](../joeflow-v1.1.0/PERSONAL_INSTALL_VERIFICATION.md))
- Applied on top: ROADMAP U1-1 (commit `08d376fc4177decd3b18fe57c68fd69cdda65049`), U1-2/U1-3 (commit `9b7bf3cf0244001638c579e8c4eb4aa697c45252`, installed 2026-10-26), and U1-4/U1-5/U1-6 (commits `aae47aa05a6a239e97ae736707b7c27b5e331fbd`, `2fa087e7da5e143643accb1f30afba6573ab8343`, `29e9bdb9d42be34cf2102b4d539e3a708a6e3fe3`, installed 2026-10-28), and U1-9 (commit `b0a3c4b448c7bda4601b87f6232334c95bd63649`, installed 2026-10-28), and the approval wording change (commit `3eeca61844f8443b5ca2262c877677557d9607ea`, installed 2026-10-29), and U1-10 (commit `83fcdfe8bc9289e6d556c852984d325db1fa7ade`, installed 2026-10-29), and U1-7 (commit `c32d149`, installed 2026-10-31 by `install_u1_7.py`)
- Not applied: commit `9891dc34141b04d3bfc5595d34433ae73a486d9d` (experience pass docs), by user choice on 2026-10-26
- Repository `VERSION` is `1.2.0` (release notes in `CHANGELOG.md`). The install is 1.2.0 without the experience pass, by user choice, so it matches no single commit.

The install matches no single commit. It is v1.1.0 plus the U1 files, and two documents are composed: v1.1.0 text plus only the U1 document hunks. The first 2026-10-28 install equals arm B of [A/B round 1](../joeflow-u1-approval-ab/REPORT.md); the U1-9 install equals arm B of [round 2](../joeflow-u1-approval-ab/REPORT-2.md).

## File origins

Compared byte for byte with the branch tip `c169018a564c2ac9145281516e24622fc73bcb30` and v1.1.0 `e3be5d1`. Full list with hashes: [personal-install-overlay-receipt.json](personal-install-overlay-receipt.json).

| Origin | Files | Meaning |
|---|---:|---|
| `v1.1.0_and_branch_tip` | 160 | Unchanged since v1.1.0 |
| `branch_tip` | 20 | U1 files: `authority_binding_v2.py`, `ux_profile_inheritance.py`, `references/ux-profile-inheritance-v1.json`, `projection_check.py`, `supersede_records.py`, `cli_output.py`, `next_product_question.py`, `authority_binding_value.py`, `build_discovery_baseline.py`, `migrate_state.py`, `record_approval.py`, `approval_status.py`, `grill_v2.py`, `binding_diagnostics.py`, `explain_state_errors.py`, `revision_v2.py`, `open_revision.py`, `refresh_bindings.py`, `record_builders.py`, `new_records.py` |
| `composed_v1.1.0_plus_u1` | 2 | `SKILL.md` (APPROVE step and three quick-reference rows), `references/workflow-v0.2.0.md` (APPROVE recording, explain, open_revision, new_records, supersede and projection_check paragraphs, UX inheritance sentence); each equals v1.1.0 plus exactly the U1 hunks of commits `9b7bf3c`, `aae47aa`, `2fa087e`, `29e9bdb`, `b0a3c4b`, `3eeca61`, `83fcdfe`, `c32d149` |
| `v1.1.0_only` | 2 | `references/ux-state-taxonomy.md`, `templates/master-planning-spec.md` — experience pass not installed |
| `preserved_local_overlay` | 2 | The two Figma handoff documents already preserved in v1.1.0 |
| `untracked_extra` | 37 | `__pycache__` only: the 29 recorded in v1.1.0 plus 8 `cpython-312` files that appeared before the U1-1 backup (not written by this work, which ran Python 3.14 with `-B`) |

- Installed files: 223; tip-tracked skill files missing from the install: 0
- Installed manifest SHA-256: `dd0275ca03349f3bbe59d5c5c3fc56753f8ef9d31ba16d9239a41b589c4bdcd4` (U1-10 install: `bfe3bc33385ad61cc70cc4b16788f506b8e8bf42be477a18a11aa9267c0013e7`, equal to the U1-7 backup below; approval-wording install: `208855001883666a5f05b384ab56b284e956c3b9b342613578271054280688fc`, equal to the U1-10 backup below; U1-9 install: `a79773759237f05d2b2ddd4e9c6a43fee6ae0ce4d17a05ee52ad2e893b28959b`, equal to the approval-wording backup below; U1-4..U1-6 install: `0b5628bcfdfc6e7c871689918bbecacf801d6c88c430074fe1b2046ae1171def`, equal to the U1-9 backup below; 2026-10-26 install: `23ff302a0e3a04db36dbc6a5fbcbb24019e3e5739a93100365ef74d314df6ad8`, equal to the U1-4..U1-6 backup below, so nothing changed in between) (sha256 of `<sha256>  <path>\n` lines sorted by path)

## Backups

| Before | Path under `C:/Users/tjdwo/.codex/skills-backups/` | Files | Manifest SHA-256 |
|---|---|---:|---|
| U1-1 | `joewrks-product-definition-before-u1-1-d49cd5c-20261026` | 209 | `30118c8f7881676f15ce38f87dde0897e385d0e2f5b88ab3260a7f5398a3ec51` |
| U1-2/U1-3 | `joewrks-product-definition-before-u1-2-3-9b7bf3c-20261026` | 210 | `d2cb8c9f37a2340038127ed912a3ec68961ecc906f03627f6dd8f1ac42b6622f` |
| U1-4..U1-6 | `joewrks-product-definition-before-u1-4-6-29e9bdb-20261028` | 212 | `23ff302a0e3a04db36dbc6a5fbcbb24019e3e5739a93100365ef74d314df6ad8` |
| U1-9 | `joewrks-product-definition-before-u1-9-b0a3c4b-20261028` | 219 | `0b5628bcfdfc6e7c871689918bbecacf801d6c88c430074fe1b2046ae1171def` |
| Approval wording | `joewrks-product-definition-before-approval-wording-3eeca61-20261029` | 220 | `a79773759237f05d2b2ddd4e9c6a43fee6ae0ce4d17a05ee52ad2e893b28959b` |
| U1-10 | `joewrks-product-definition-before-u1-10-83fcdfe-20261029` | 220 | `208855001883666a5f05b384ab56b284e956c3b9b342613578271054280688fc` |
| U1-7 | `joewrks-product-definition-before-u1-7-c32d149-20261031` | 221 | `bfe3bc33385ad61cc70cc4b16788f506b8e8bf42be477a18a11aa9267c0013e7` |

Each backup was checked for exact path and hash parity with the install at the time it was taken.

## Verification

Run against the installed scripts on 2026-10-26, Python 3.14.5, without `PYTHONIOENCODING`:

- Native State 0.2.0 and legacy 0.1.2.1 template validators: valid
- UTF-8 output: Korean and em-dash paths print without `UnicodeEncodeError` from `next_product_question.py`, `authority_binding_value.py` and `migrate_state.py`
- `record_approval.py` on a copy of AI-Gomoku `ai-coach` rev 30 reset to `READY_FOR_REVIEW`: output byte-identical to the hand-written rev 30 `state.json`; `validate_state.py` valid, `validate_closure.py` closed
- `approval_status.py` on the same project: revisions without their own approval `13, 14, 26, 28`
- `open_revision.py` then `record_approval.py` on the committed AI-Gomoku rev 29 (`4bb3f53`) with a 21-record, 3-cell-edit patch: byte-identical to the committed rev 30 (2026-10-28, installed scripts)
- `explain_state_errors.py` on a rev 30 copy with five injected errors: hints attached
- `supersede_records.py` (installed) on rev 30: DEC-084/UNK-084 replaced through a patch, `open_revision.py` reports no validation errors
- `projection_check.py` (installed) on AI-Gomoku rev 32: the approved rev 32 spec and review view pass
- U1-7 (installed scripts, 2026-10-31): AI-Gomoku rev 37 `validate_state.py` valid; dropping the 16 inheritable UX cells leaves no coverage errors (N/A 61→46); setting `AUTH` or `PERMISSION` to OPEN brings back the inventory errors. The first install run stopped on a wording anchor after writing `SKILL.md`; the rerun restored it from the verified backup before applying
- Repository regression on the branch: 1,174 tests (2026-10-29), no new failures; 8 environment failures identical to the pre-change baseline

Agent behavior: see the [approval A/B](../joeflow-u1-approval-ab/REPORT.md) — B runs recorded approval with a disclosed recording time; A runs stopped to ask. Round 2 covered the pre-approval implementation rule and revision writing with the patch tools.
