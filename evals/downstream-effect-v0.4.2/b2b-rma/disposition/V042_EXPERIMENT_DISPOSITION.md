# v0.4.2 Experiment Disposition

## Official classification

`STOPPED — TREATMENT_INTERVENTION_CONSTRUCTION_FAILED`

## Paired efficacy result

`NOT RUN`

Reason: Treatment intervention failed pre-freeze semantic review before S1 creation.

No implementation arm started. Therefore this is not a Treatment implementation failure, Control win, Treatment loss, or evidence that the downstream contract was ineffective.

## Frozen boundaries

- S1: absent
- Control: NOT STARTED
- Treatment: NOT STARTED
- C0/T0: absent
- main: unchanged
- Product Definition: unchanged
- Generic downstream subsystem: unchanged

## Diagnostic conclusion

The two reviews used the same 665 identities but materially different review-brief wording. The only four semantic edits did not produce verdict flips; all 176 flips occurred on unchanged fields. Isolated adjudication found the shared field-completeness rule underspecified and classified all 176 flips as rubric ambiguity. This is a pre-experiment review-reliability failure, not an efficacy result.

## Recommendation

Keep v0.4.2 stopped and immutable. Open a separate post-v0.4.2 review-calibration/hardening workstream before attempting a new paired efficacy version. That workstream should version and freeze one reviewer brief, define whether semantic obligations compose across sibling fields, supply adjudicated golden cases, and demonstrate repeatable verdicts. It must not retroactively create S1 or reinterpret v0.4.2 as an implementation result.
