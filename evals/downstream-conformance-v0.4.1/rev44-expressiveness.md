# Revision 44 Expressiveness Probe

## Authority

- product: `client-feedback-portal-dogfood`
- approved revision: `44`
- approved digest: `2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1`
- compiled contract: `ea31516b703aab17d471081acf6d49622e0825643c2c4460247396633aecffc2`

Compilation read the preserved `state.json` and wrote no canonical data. This is an expressiveness probe, not a new Figma Make run or verdict.

## Expressed semantics

- **Authority:** `RULE-001` pins designated reviewer email identity.
- **Exact Version:** `STATE-001`, `RULE-059`, and `RULE-060` pin exact Version ID and expected state revision.
- **Link lifecycle:** current state/lifecycle clauses are separated from inactive superseded `DEC-011` provenance.
- **Concurrency/idempotency:** stale is no-op/latest readback; `RULE-062` reuses prior exact-Version approval without a duplicate record.
- **Delivery separation:** approval state/history and the separate Designer email delivery event/status occupy distinct result components.
- **Append-only history:** `RULE-008` preserves approval actor, timestamp, and exact Version.

The action trace represents `approve_version` from canonical action/control through handler/command, exact Version mutation, approval history, Designer delivery, and visible authoritative readback. The lifecycle contract marks APPROVED terminal for the same immutable Version.

## Superseded sentinel

The compiled lifecycle carries `DEC-011` only as `active=false`, `source_status=SUPERSEDED`. A sentinel sequence deliberately observed `DEC-011` as current behavior; the lifecycle verifier returned NONCONFORMANT with matched source `DEC-011`. This proves the harness fails an implemented superseded rule.
