# Methodology

## Isolation and authority

- Evaluated only Replication B after the product-agent run ended.
- Treated `state.json` as authority and Markdown as projections.
- Created the hidden bank only post-run. The product directory is untracked and the evidence directory did not exist at inspection time; there is no repository evidence that the product agent read an evaluator checklist or hidden bank.
- Compared the result to the v0.4 evaluator interests only after extracting canonical product truth.

## Checks

1. Read the frozen Skill and v0.4 contract.
2. Counted and classified canonical objects and statuses.
3. Audited stable references, active/superseded state, revision headers, approval digest, coverage, and reversal propagation.
4. Ran both frozen validators against the canonical state.
5. Attempted the repository suite with `python -m pytest -q`; it did not execute because this interpreter has no `pytest` module. This is an environment limitation, not a product-definition validator failure.

## Reconstruction boundary

No raw chat transcript or revision-by-revision snapshots were persisted. Question order is reconstructed from stable `UNK-001..054` order, sources, dependency wording, and final revision arithmetic. Answer substance is authoritative because it is copied or faithfully summarized from each unknown's final resolution. Exact user phrasing, option labels for every turn, timestamps within the day, and the exact closure-approval utterance are not recoverable. Claims about turn counts are therefore clearly marked reconstructed.
