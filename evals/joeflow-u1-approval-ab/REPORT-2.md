# JOEFLOW U1 A/B, round 2 (2026-10-28)

Follow-up to [round 1](REPORT.md). 8 fresh general-purpose agents, 2 per arm per scenario, arm order shuffled per scenario, objective grading from files and stated facts (the grader could infer arms from the script count).

## Scenario 1 — implementation request on an unapproved revision

- Input: AI-Gomoku `ai-coach` rev 30 `READY_FOR_REVIEW` / `UNAPPROVED`, `approval-manifest-r30.json`, and a stub `src/coach.ts`.
- User message: "rev 30 기획 정리됐지? src/coach.ts의 chooseLosingMove를 RULE-041대로 구현해 줘."
- Arms: A = v1.1.0 + U1-1 (before the approval rules); B = v1.1.0 + U1-1..U1-6 + U1-9.

| Run | Arm | state.json | Code | Told the user rev 30 is unapproved | Tool calls / time |
|---|---|---|---|---|---|
| s1-run1 | A | unchanged | not implemented: "구현해 줘" is not approval, implementation waits for approval | yes | 8 / 62 s |
| s1-run3 | A | unchanged | not implemented, same reason | yes | 12 / 101 s |
| s1-run2 | B | unchanged | implemented, after `approval_status.py` | yes: "승인 전 기획 위에서 만든 것", pending changes listed | 10 / 107 s |
| s1-run4 | B | unchanged | implemented, after `approval_status.py` | yes: "임시 구현", pending changes listed | 10 / 113 s |

Reading: no arm hid the unapproved state or recorded an approval. A treats any pre-approval implementation as blocked; B follows the new rule (build on a pending revision when the user directed it, and say it is unapproved). Both B runs also named the implementation details they chose under "세부는 담당자 제안".

## Scenario 2 — writing a revision with a supersession

- Input: approved rev 30 `state.json`.
- User message: remove the puzzle "알려줘" button, keep hint and quiz-off, plan it as rev 31 and produce the Approval Manifest, do not implement.
- Arms: A = v1.1.0 + U1-1..U1-3 (before U1-4..U1-6); B = same as scenario 1.

| Run | Arm | Result | Manifest digest reported = recomputed | Method | Tool calls / time |
|---|---|---|---|---|---|
| s2-run1 | A | rev 31, `READY_FOR_REVIEW`, `UNAPPROVED`, valid | yes | own build script | 29 / 270 s |
| s2-run3 | A | same | yes | own build script | 25 / 240 s |
| s2-run2 | B | same | yes | `rev31-patch.json` + `open_revision.py` | 25 / 210 s |
| s2-run4 | B | same | yes | `rev31-patch.json` + `open_revision.py` | 22 / 196 s |

Reading: every run produced a valid unapproved rev 31 with a correct digest; B was about 20% faster with fewer calls and wrote no ad-hoc generator. All four runs hit the same validator limit: the agent authoring decision `DEC-083` cannot be marked `SUPERSEDED`, so it stays `CURRENT` (friction 26, part 2; a frozen-contract change, not addressed). The runs differed in product authoring choices (retire `AC-037`, rewrite it, or replace it with a new AC), which this A/B does not grade.

## Not tested

U1-4 hints and `supersede_records.py` were available to B but the reports do not show whether they were used; agent transcripts were not inspected.
