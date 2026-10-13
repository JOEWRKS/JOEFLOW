# Regression environment and frozen-core closure

Date: 2026-10-13. Implementation and execution: QA Manager. Independent
read-only source review: JOEFLOW owner, final review PASS. No full product
release or semantic-review reliability certification is implied.

## Findings and fixes

1. The original 18 focused tests reproduced 5 failures and 7 errors. Eleven
   shared a runner raw-byte mismatch caused by Windows CRLF checkout; one
   lacked the required historical M6 input. The runner integrity checks,
   revision commitments, evidence and mandatory replay assertions were kept.
2. Attributes now force LF only for runner Python/JSON and canonical evidence.
   Existing checkout refresh verifies all 11 paths against the same HEAD,
   refuses substantive/staged edits, then restores exact bytes and refreshes
   index metadata. The first attempt without index refresh failed; this was
   retained in QA evidence and corrected in the documented procedure.
3. The historical M6 input was reconstructed from local Git commit
   `d38b0ca04768888c47e658c79f41e1cec0a7a1ce`, tree
   `40749d900b98936cf694b0c96db7897011cddae8`, in a detached local clone.
   The advanced M6 development checkout was not reset. Existing identity,
   artifact, approval, and before/after tracked-byte checks passed unchanged.
4. A full run at `bd4d4696950bf89aabde41bdd46d772feee7030d` ran 1,128 tests
   and exposed one additional F03 regression: the diagnostic implementation
   had modified the frozen authority core. This was distinct from the twelve
   environment failures. The earlier whole-suite run occurred before F03/F04.
5. The authority core was restored to exact blob
   `03704ea991aa72d20c2dd8c251ea22cbda8640ce`. Detailed offender diagnostics
   moved into the candidate preflight adapter, using the same frozen graph
   and predicates. Existing approval/closure metrics and frozen expected
   hashes were not changed. A regression checks four gap categories, exact
   offender IDs, count parity, and input preservation.

## Final verification

Source commit: `bfd07459c985d58079c43ee5d235562ec0aad85f`.

- [Full regression](full-result.json): **1,129 run, zero failures/errors,
  one existing skip**, exit 0, Python 3.14.5. [Complete log](full-suite.log).
- Source tracked bytes/HEAD/tree/status, historical snapshot, and all three
  personal skills plus global protected settings were unchanged during the run.
- F03/F04 focused tests: 24 passed. Separate F03 counterexamples: 6/6.
- Fresh Windows clone with `core.autocrlf=true`: all 11 exact-byte paths match
  committed bytes without manual conversion; a future binary path is not
  forced to text. [Receipt](final-checkout.json).
- Documented checkout refresh: CRLF-only input succeeds; substantive and
  staged edits are rejected with files/index preserved. [Receipt](checkout-recipe.json).
- Isolated candidate to installed JOENESS: 9/9 expected outcomes.
- Managed personal install: exact 201-file backup, two-file replacement,
  201-file post-manifest match, then actual installed JOEFLOW to JOENESS
  11/11 expected outcomes. No new/deleted files. [Receipt](managed-receipt.json).
- [Independent final source review](owner-final-review.json) accepted the
  narrowed attributes, reproducible refresh, and preserved frozen core.

The full regression was rerun because F03 code changed. This evidence-only
follow-up and the LF attribute for these log files do not alter runtime code
or tests; their validation reuses that exact source result.

## Remaining boundary

The pre-existing frozen A/B runtime test is skipped because
`JOEWRKS_FROZEN_A_ROOT` and `JOEWRKS_FROZEN_B_WORKTREE` were not supplied.
That scenario remains unverified. M6 replay is mandatory and was **not**
skipped. No test was removed or newly skipped. No main merge, release tag,
live service call, or user product acceptance was performed.

Repository logs use LF; the original raw captures and their SHA-256 are
retained in JOEQASAM T038. See [the reproducible environment instructions](../../docs/regression-environment.md).
