# State 0.2.0 foundation boundary

state 0.2.0 is parallel to, not an in-place replacement for, legacy 0.1.2.1.
legacy 0.1.2.1 validation remains frozen. LEGACY_CLOSURE remains governed by the frozen legacy contract.

M1 validated V2 top-level shape, typed semantic minima, lifecycle, IDs, and migration planning.
At that historical milestone, M1 did not claim V2 Semantic Closure.
`SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1` records that explicit M1 boundary; it is
not the current M4 runtime behavior.

`migrate_state.py --plan` emits `FOUNDATION_PLAN_ONLY` and never manufactures V2 authority.
The M1 closure guard may be removed only by a later milestone that implements and verifies its frozen gate.

## M2 discovery authority boundary

M2 adds evidence, discovered surface, contradiction, reverse-bootstrap, and
deterministic discovery-baseline authority rules. The authoritative M2 detail
is the [M2 discovery authority contract](discovery-contract-v0.2.0.md).

When current semantic authority consumes repository-backed
`DOCUMENTED_INTENT` or `HISTORICAL_DECISION`, that evidence must carry both an
exact `observed_version` and `content_hash`. Accepted commitments are exact Git
commit/tree/blob identities (`git-commit:`, `git-tree:`, or `git-blob:` plus the
40-character object ID) or an exact SHA-256/source-byte commitment. A relative
repository locator with null or informal commitments is not closure-eligible.
Changing either commitment changes the consumed-evidence semantic projection,
so the definition/approval checkpoint must be rebuilt. Current
`USER_CONFIRMED_INTENT` remains user authority and does not receive fabricated
repository versions, hashes, or timestamps.

M2 did not remove the M1 Closure guard. `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M2`
records that historical milestone boundary. M4 now supersedes only that
temporary guard, not M2's evidence and discovery semantics.

## M3 Grill Engine boundary

M3 adds deterministic Materiality, unknown-resolution authority, selective
question projection, mandatory topology profiles, declarative Grill Packs, and
Grill-aware discovery baselines. The authoritative M3 detail is the
[M3 Grill Engine contract](grill-contract-v0.2.0.md).

M3 preserved the M1/M2 Closure guard. `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M3`
records that historical boundary; M3 did not itself claim closure.

## M4 Semantic Freeze boundary

M4 replaces the temporary guard with the actual state 0.2.0 Product Definition
Semantic Closure evaluator. Valid READY states expose their deterministic
definition digest, and only an exact approved CLOSED state with every frozen
M1–M4 blocker at zero returns `closed = true`.

The authoritative current detail is the
[M4 Semantic Freeze contract](semantic-freeze-contract-v0.2.0.md).
`SEMANTIC_CLOSURE_AVAILABLE_M4` means Product Definition closure is available;
it does not mean design, implementation, deployment, downstream 2.0, or M6
adoption is complete.

## M6 deterministic migration boundary

M6 adds an apply path beside the unchanged M1 plan path. A valid legacy
`0.1.2.1` state can be converted into a deterministic state `0.2.0`
reconciliation candidate by `migrate_state.py --apply SOURCE_JSON --output
DEST_JSON`. The exact migration and receipt contract is the
[M6 migration contract](migration-v0.2.0.md).

Migration does not transfer legacy closure or approval into current V2
authority. Every candidate begins `OPEN`, uses
`EXISTING_PRODUCT_RECONCILIATION`, increments the legacy definition revision,
remains `UNAPPROVED`, has no approval history, and has no established discovery
baseline. Incomplete legacy records remain exact historical source records
under `migration.legacy_records`; deterministic `migration.reconciliation_gaps`
describe missing V2 semantic authority without manufacturing typed semantic
objects or canonical unknowns.

Conflicting source aliases or any unconsumed semantic/custom source field also
force exact archival. Missing axes in otherwise valid legacy Core and UX rows
become deterministic cell-path gaps without fabricated cells or unknowns.
Extra legacy Core and UX axes remain non-authoritative OPEN cells with exact
axis-inventory gaps; inventory mismatch attribution requires complete gap
coverage for every missing and extra axis.
Candidate publication uses a uniquely owned sibling temporary artifact and a
non-overwriting destination operation; write, flush, and publish failures remove
the owned temporary artifact and never alter an existing destination.

`MIGRATION_RECONCILIATION_CANDIDATE_M6` means the state is structurally valid
and migration-integrity verified. It does not mean Semantic Closure, approval,
discovery completion, specialist topology classification, downstream adoption,
design, implementation, or deployment.

## Authoring builders (JOEFLOW 2.0.2)

The builders write records of this contract; they do not change it. State 0.2.0, the
schema and the binding contracts are unchanged.

- New projects start from a template whose six topology domains are `OPEN`, each holding
  one `GRILL_TOPOLOGY` question (`UNK-901`…`UNK-906`, `basis_refs []`). No evidence is
  pre-filled. A domain becomes `ACTIVE` or `N/A` only from its answer
  (`new_records.py topology-on|topology-off DEC`).
- `open_revision.py` accepts `grill_profile` in a patch: a map from domain to its complete
  profile cell, replacing that domain's cell.
- An `ACTIVE` specialist pack still needs its coverage row in the same revision
  (`missing_grill_coverage` is unchanged). `topology-on` writes it, with the checked-in
  pack version and digest and one `OPEN` axis cell per axis, each held by its own
  `GRILL_PACK_AXIS` question. While a domain is `OPEN` no row exists or is needed.
- Decision authority of an `OPEN` or `BLOCKED` unknown is the validator's
  `derive_decision_authority`; the builders call it (`scripts/decision_policy.py`). A
  `RESOLVED` unknown's authority follows its resolution mode. The builders record
  `USER_ACCEPTED_RECOMMENDATION` only when the `OPEN` question derives
  `USER_CONFIRMATION`; the validator does not re-derive resolved records, so states written
  by earlier versions stay valid.
- Coverage cell addresses in patches may name the target: `grill_coverage[PACK/TARGET]`.
