# Behavioral Evaluation v0.2

This directory contains isolated Control/Treatment behavioral evidence for EVAL-01 through EVAL-06. The deterministic baseline is commit `1121c9e33ef30335d9cb2af0b0c794621e33d6fd`, contract `0.1.2.1`.

Primary transcripts are immutable observations. Evaluator reports and comparisons are derived from them; hidden chain-of-thought is neither requested nor inferred. Figma-native generation and Figma Make execution are outside scope.

## Artifact index

- `methodology.md` and `rubric.md`: isolation and scoring contract.
- `transcripts/eval-XX-{control,treatment}.md`: 12 primary fresh runs.
- `eval-XX-{control,treatment}.md`: primary run evaluations.
- `eval-XX-comparison.md`: paired initial and final comparison.
- `transcripts/rerun-eval-XX-treatment.md`: six fresh post-refinement Treatment regressions.
- `rerun-eval-XX-treatment-evaluation.md`: rerun evaluations.
- `observed-rationalizations.md` and `refinement-log.md`: evidence-to-instruction traceability.
- `aggregate-results.md`: final verdict and score rollup.

Final result: **PASS**, final Treatment average **97.3/100**, average Control delta **+32.8**, UX burden **5.0/5**, critical failures **0**.
