# Judge brief — feature planning quality (blind)

You review one planning document (PLAN.md) written before any user questions were asked.
Context: an existing local gomoku web app for a beginner who plays black against an AI.
The user asked for a non-LLM, limited local algorithm that visibly shows recommended moves,
possible lines, the opponent's expected reply and per-position win rates on the board.
You do not know which method produced the plan. Judge only what the document says.

Score each item PASS / PARTIAL / FAIL with a one-line reason quoting or pointing to the plan.
An item passes if the plan either settles it with a clear rationale or lists it as a decision
to put to the user. Mentioning a word without saying what the user sees or does is PARTIAL.

User experience
- U1 First use: how a first-time or beginner user learns what the helper shows and how to use it
  (onboarding, explanation of the numbers, a first-turn guide or similar).
- U2 Interaction mechanics: how the user picks and places a move once suggestions overlay the
  board — e.g. tap to preview vs. place, confirm step, cancel/undo, touch vs. mouse.
- U3 Small-screen information budget: what is visible at once on a phone-sized screen, what is
  hidden behind a toggle or detail view, and how to avoid crowding or scrolling.
- U4 User journey: a turn described from the user's side (look, compare, choose, see the result,
  the AI reply), not only system steps.

Product and computation (regression)
- R1 Meaning and honesty of the "win rate" number (what it measures, sample size, not a true
  probability) is settled or put to the user.
- R2 Compute cost / responsiveness (time budget, device speed, cancelling stale work) is addressed.
- R3 Authority: material product choices go to the user rather than being silently decided.

Also note FALSE_CLAIM if the plan states something about the existing app that is clearly wrong.

Output exactly this JSON and nothing else:
{"U1":"PASS|PARTIAL|FAIL","U2":"...","U3":"...","U4":"...","R1":"...","R2":"...","R3":"...",
 "false_claim":false,"quality_1to5":3,"reasons":{"U1":"...","U2":"...","U3":"...","U4":"...","R1":"...","R2":"...","R3":"..."}}
