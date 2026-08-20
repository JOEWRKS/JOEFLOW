# Methodology

Each run uses a separate Codex subagent created with `fork_turns="none"`. This passes no root conversation history, prior EVAL transcript, paired result, or evaluator rubric. Every run receives a unique execution ID, the same user prompt and fixture path as its pair, and a unique writable output directory. Agents share the filesystem only for immutable fixtures; run output paths never overlap.

Control instructions prohibit loading `joewrks-product-definition` and supply no Skill text or path. Treatment explicitly requires loading `skills/joewrks-product-definition/SKILL.md` and following it. Model and runtime are inherited equally. The evaluator answer key is retained only by the root evaluator.

EVAL-04, EVAL-05, and EVAL-06 are scripted multi-stage runs. The same follow-up is included in the paired run protocol and delivered only after the initial behavior is recorded. Raw records contain observable responses, evidence reads, questions, assumptions, writes, closure attempts, and final status. They do not contain private reasoning.

The deterministic layer is frozen. Before evaluation, the baseline content of validators, schema, state contract, and coverage taxonomies is treated as immutable. Behavioral failure can change only `SKILL.md` and `references/interrogation-engine.md`, and only after all primary runs show a repeated transcript-supported pattern.
