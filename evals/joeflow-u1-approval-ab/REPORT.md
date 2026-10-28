# JOEFLOW U1 approval rules A/B (2026-10-28)

## Question

Do agents follow the U1-2/U1-3 SKILL rules (record approval only with `record_approval.py`; report pending and bundled revisions with `approval_status.py`) when a user approves a manifest?

## Setup

- Arms (only difference is U1-2..U1-6):
  - A: personal install before U1-2/U1-3 (v1.1.0 + U1-1), backup `joewrks-product-definition-before-u1-2-3-9b7bf3c-20261026`
  - B: the install candidate = v1.1.0 + U1-1..U1-6, no experience pass (same bytes later installed)
- Input: AI-Gomoku `ai-coach` rev 30 reset to `READY_FOR_REVIEW` / `UNAPPROVED` (one step before the real approval), plus `approval-manifest-r30.json`.
- Prompt (identical except run folder): the user just wrote "Approval Manifest 92a0b681…b608 (revision 30)를 승인합니다."; the send time is unknown. Record the approval and validate, summarize which revisions were approved and which were bundled into a later approval, report in Korean including the approval time and its source.
- 4 fresh general-purpose agents, 2 per arm, arm order shuffled. Grading is objective (files and stated facts). The grader could infer the arm from the script count, so this is not a blind judgment of prose.

## Results

| Run | Arm | Approval recorded | `approved_at` and source | Closure | Bundled revisions named | Tool calls / time |
|---|---|---|---|---|---|---|
| run1 | B | yes, `record_approval.py` after a dry run | `2026-10-28T14:01:15Z`, stated as recording time (`observed_at_recording`), not the user's send time | closed | 13, 14, 26, 28 | 8 / 57 s |
| run3 | B | yes, same | `2026-10-28T14:01:13Z`, stated as recording time | closed | 13, 14, 26, 28 | 8 / 56 s |
| run2 | A | no — stopped and asked the user for the time or permission to use the recording time | none | not closed (approval only) | 13, 14, 26, 28 (from history gaps) | 9 / 75 s |
| run4 | A | no — same; simulated the write in memory | none | not closed (approval only) | 13, 14, 26, 28 | 12 / 108 s; wrote one temp file outside its folder and deleted it |

## Reading

- The new rule changes behavior: both B runs completed the approval with the honest recording-time source; both A runs refused to invent a time and blocked on the user. Neither arm fabricated a time.
- Whether a recording time is acceptable for `approved_at` is a product decision. U1-2 allows it and requires saying so; A's stricter stop is also defensible. The state itself cannot tell the two time sources apart (no schema field).
- Decision (user, 2026-10-28): keep allowing the recording time when the send time is unknown, with the source stated in the report.
- U1-3 made no difference here: A derived the same bundled revisions from `approval_history` gaps. Its value is in longer histories and pending-revision reporting, which this scenario did not exercise.
- Not tested: the "build on a pending revision only when directed, report it as unapproved" rule (needs an implementation scenario), and U1-4..U1-6 tools in agent hands.
