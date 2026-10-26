# JOEFLOW U1 personal install record

Date: 2026-10-26 (Asia/Seoul)

## Installed identity

- Personal install: `C:/Users/tjdwo/.codex/skills/joewrks-product-definition`
- Base: v1.1.0 install, source commit `e3be5d11fe0e8f5b79c42e35a0bcb157f5bdda4a` ([v1.1.0 record](../joeflow-v1.1.0/PERSONAL_INSTALL_VERIFICATION.md))
- Applied on top: ROADMAP U1-1 (commit `08d376fc4177decd3b18fe57c68fd69cdda65049`) and U1-2/U1-3 (commit `9b7bf3cf0244001638c579e8c4eb4aa697c45252`)
- Not applied: commit `9891dc34141b04d3bfc5595d34433ae73a486d9d` (experience pass docs), by user choice on 2026-10-26
- Root `VERSION` stays `1.1.0`; these changes are unreleased (see `CHANGELOG.md`).

The install matches no single commit. It is v1.1.0 plus the U1 files, and two documents are composed: v1.1.0 text plus only the U1-2/U1-3 insertions.

## File origins

Compared byte for byte with the branch tip `ee595285da4d47ffe8275e7412b7ef04efd15ce9` and v1.1.0 `e3be5d1`. Full list with hashes: [personal-install-overlay-receipt.json](personal-install-overlay-receipt.json).

| Origin | Files | Meaning |
|---|---:|---|
| `v1.1.0_and_branch_tip` | 162 | Unchanged since v1.1.0 |
| `branch_tip` | 7 | U1 scripts: `cli_output.py`, `record_approval.py`, `approval_status.py`, `next_product_question.py`, `authority_binding_value.py`, `build_discovery_baseline.py`, `migrate_state.py` |
| `composed_v1.1.0_plus_u1_2_3` | 2 | `SKILL.md` (APPROVE step and one quick-reference row), `references/workflow-v0.2.0.md` (APPROVE recording paragraphs); each equals v1.1.0 plus exactly those insertions |
| `v1.1.0_only` | 2 | `references/ux-state-taxonomy.md`, `templates/master-planning-spec.md` — experience pass not installed |
| `preserved_local_overlay` | 2 | The two Figma handoff documents already preserved in v1.1.0 |
| `untracked_extra` | 37 | `__pycache__` only: the 29 recorded in v1.1.0 plus 8 `cpython-312` files that appeared before the U1-1 backup (not written by this work, which ran Python 3.14 with `-B`) |

- Installed files: 212; tip-tracked skill files missing from the install: 0
- Installed manifest SHA-256: `23ff302a0e3a04db36dbc6a5fbcbb24019e3e5739a93100365ef74d314df6ad8` (sha256 of `<sha256>  <path>\n` lines sorted by path)

## Backups

| Before | Path under `C:/Users/tjdwo/.codex/skills-backups/` | Files | Manifest SHA-256 |
|---|---|---:|---|
| U1-1 | `joewrks-product-definition-before-u1-1-d49cd5c-20261026` | 209 | `30118c8f7881676f15ce38f87dde0897e385d0e2f5b88ab3260a7f5398a3ec51` |
| U1-2/U1-3 | `joewrks-product-definition-before-u1-2-3-9b7bf3c-20261026` | 210 | `d2cb8c9f37a2340038127ed912a3ec68961ecc906f03627f6dd8f1ac42b6622f` |

Each backup was checked for exact path and hash parity with the install at the time it was taken.

## Verification

Run against the installed scripts on 2026-10-26, Python 3.14.5, without `PYTHONIOENCODING`:

- Native State 0.2.0 and legacy 0.1.2.1 template validators: valid
- UTF-8 output: Korean and em-dash paths print without `UnicodeEncodeError` from `next_product_question.py`, `authority_binding_value.py` and `migrate_state.py`
- `record_approval.py` on a copy of AI-Gomoku `ai-coach` rev 30 reset to `READY_FOR_REVIEW`: output byte-identical to the hand-written rev 30 `state.json`; `validate_state.py` valid, `validate_closure.py` closed
- `approval_status.py` on the same project: revisions without their own approval `13, 14, 26, 28`
- Repository regression on the branch: 1,144 tests, no new failures; 8 environment failures identical to the pre-change baseline

Not verified: whether agents follow the new SKILL approval rules (no A/B run).
