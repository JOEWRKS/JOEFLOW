# State 0.2.0 deterministic migration contract

This contract defines M6 raw migration from a valid legacy state `0.1.2.1` to
a state `0.2.0` reconciliation candidate. Raw migration preserves evidence; it
does not manufacture V2 intent, authority, topology classification, closure,
approval, or downstream authority.

## Commands and exit behavior

The historical plan command remains:

```text
python migrate_state.py --plan SOURCE_JSON
```

It emits the unchanged canonical `FOUNDATION_PLAN_ONLY` plan and never writes a
V2 state.

Apply is:

```text
python migrate_state.py --apply SOURCE_JSON --output DEST_JSON
```

The source is read-only. The destination must not exist. Only after
`verify_migration_result()` returns no migration integrity errors, apply writes,
flushes, and synchronizes a uniquely owned sibling temporary artifact, then
publishes it with a non-overwriting same-filesystem link operation. The owned
temporary artifact is removed after write, flush, synchronization, or publish
failure. A destination created by another process is never altered. Success
writes one canonical candidate JSON document and prints one canonical receipt
JSON document. Expected reconciliation and semantic gaps exit `0` because they
are represented in migration metadata. Invalid legacy input exits `1` with
structured canonical JSON. Usage, read, JSON, destination, and write errors exit
`2` without a traceback.

## Candidate invariants

Every apply result has:

```text
schema_version = 0.2.0
project.definition_status = OPEN
project.definition_revision = legacy project.definition_revision + 1
project.bootstrap_mode = EXISTING_PRODUCT_RECONCILIATION
approval = {"status":"UNAPPROVED"}
approval_history = []
discovery_baseline = {"status":"NOT_ESTABLISHED"}
```

`project.closure_contract` contains the exact current Product and UX binding
contract identities returned by `binding_contract_identity()`. The legacy
approval is hashed as historical provenance only. Its fields and timestamp are
not copied to current approval or approval history. Migration creates no wall
clock field, including `migrated_at`, and the candidate contains no digest of
itself.

The migrated metadata object has exactly these fields:

```text
mode
from_schema
to_schema
migration_version
source_digest
source_revision
source_legacy_status
source_legacy_approval_digest
plan_digest
preserved_ids
promoted_ids
generated_ids
legacy_records
reconciliation_gaps
reconciliation_gap_count
```

The exact constants are `mode=MIGRATED`, `from_schema=0.1.2.1`,
`to_schema=0.2.0`, and `migration_version=0.2.0-m6.1`. Source, approval, plan,
archive-record, and candidate receipt digests are lowercase SHA-256 over
canonical JSON: UTF-8, Unicode preserved, object keys sorted, and separators
`,` and `:` without extra whitespace.

The separate receipt has exactly:

```text
schema_version = joewrks.state-migration-receipt/1.0
migration_version
source_digest
plan_digest
candidate_state_sha256
preserved_ids
promoted_ids
generated_ids
archived_ids
reconciliation_gap_count
```

`candidate_state_sha256` is computed only after the candidate is complete.

## Promotion and archive rules

A source record is promoted to its normal `objects.<group>` only when every
required V2 semantic minimum is losslessly constructible from explicit legacy
fields. The stable source ID is retained. Mapping is explicit per type:

| V2 type | Explicit source mapping |
| --- | --- |
| GOAL | `text` to `statement` |
| USR | `role` to `actor_kind`; `description` assembled from present `role`, `cardinality`, and `identity` fields with those labels preserved |
| REQ | `text` to `statement`; exact `scope`, `ui_required`, and full V2 `materiality` |
| UNK | exact complete V2 semantic fields; supported legacy lifecycle normalized without adding meaning |
| DEC | explicit `decision` or `answer` to `statement`; every other V2 minimum must already be explicit |
| RULE | explicit `statement` or `text`; exact `applies_to` |
| FLOW | exact `goal_refs`, `entry`, `preconditions`, `paths`, and `outcomes` |
| SCR | exact `purpose`, requirement references, `interaction_mode`, and `major_actions` |
| STATE | `name` to `state_name`; exact `owner_refs` and `conditions` |
| DATA | exact `name`, `purpose`, and `ownership` |
| INT | exact `name` and `purpose` |
| AC | exact `assertion` or `text` and requirement references |
| TASK | exact `implements` and acceptance references |

A legacy `material: true` or `material: false` never becomes a V2 Materiality
Assessment. A REQ, DEC, or UNK without a complete, internally consistent V2
Materiality object is not promoted.

Promotion also requires lossless source-field accounting. The exact consumed
field inventory is defined per source group. Any other semantic or custom source
field archives the whole record rather than silently dropping that field. For
the supported alias groups (`decision`/`answer`, `statement`/`text`,
`requirement_refs`/`requirements`, `assertion`/`text`, and
`acceptance_refs`/`acceptance`), multiple present aliases are accepted only when
their normalized text or string-list values are identical. Conflicting aliases
archive the exact record and identify the affected V2 field in its gap.

If any required meaning is absent, migration creates no statement, scope,
Materiality, lifecycle placeholder, fake stale object, or canonical unknown.
Instead it stores an exact deep copy under `migration.legacy_records`. Every
archive entry contains exactly `source_id`, `source_group`, `source_record`, and
`source_record_sha256`.

`preserved_ids` is the sorted exact union of promoted IDs and archived stable
source IDs. `generated_ids` lists only truthfully complete canonical records
created by migration; raw migration normally leaves it empty.

Ordinary state `0.2.0` validation rechecks these migration commitments even
outside `verify_migration_result()`. It recomputes every archived
`source_record_sha256`, the deterministic archive ordering, every gap key and
the gap-key order, and the preserved/promoted/generated/archive ID inventory
relationships. Editing an archived source record without its matching hash, or
rewriting an inventory while retaining a structurally valid shape, invalidates
the migrated state. These checks do not make migration metadata semantic
authority: the complete migration section remains excluded from the definition
digest and Approval Manifest projection.

## Reconciliation gaps

`migration.reconciliation_gaps` is an object keyed by
`gap:<24 lowercase hex>`. The suffix is the first 24 hexadecimal characters of
the canonical SHA-256 of the gap metadata. Each value contains exactly:

```text
source_id
source_path
missing_v2_fields
reason_code = MISSING_V2_SEMANTIC_AUTHORITY
```

`source_path` is an exact JSON Pointer with `~` and `/` escaped as `~0` and
`~1`. `missing_v2_fields` is sorted and unique. A gap key is metadata, not a
Product Definition stable ID, and never enters semantic authority.

Every legacy Core or UX coverage cell is retained as a V2 `OPEN` reconciliation
site with empty authority, unknown, and basis bindings. Legacy `COVERED` records
a missing exact `authority_bindings` selection; legacy `N/A` records missing
`basis_bindings`; legacy `OPEN` records missing `unknown_refs`. Old coverage is
never promoted directly to V2 `COVERED` or `N/A`.

Valid legacy rows may omit axes. For each absent axis from the frozen V2 Core,
UX state, or UX action inventory, migration records an exact deterministic gap
at the would-be cell path with all five V2 cell fields missing. It does not add
the absent cell or create an unknown. The resulting V2 inventory validation
error is accepted only when every absent axis has its exact derived gap.

Valid legacy rows may also contain axes outside the frozen V2 inventory. Each
extra source cell remains present as a non-authoritative V2 `OPEN` reconciliation
site; its legacy status selects the missing binding field, while
`axis_inventory` records that no current V2 axis owns that meaning. Migration
does not discard the cell or create a canonical unknown. An inventory mismatch
is attributable only when every missing required axis and every extra legacy
axis has its one exact deterministic derived gap.

When an explicitly promoted current material requirement or screen has no
legacy coverage row, raw migration still creates no fake row. It records a
deterministic absence gap at `/coverage/<REQ-ID>` or
`/ux_coverage/<SCR-ID>` so the validator's missing Core, Core Grill, or UX row
failure remains attributable.

Raw migration does not create six fake OPEN specialist topology cells or
canonical topology unknowns. The migrated structural schema permits an empty
Grill Topology Profile only for `mode=MIGRATED`, and the six missing domains are
represented by distinct reconciliation gaps. The semantic validator remains
unchanged: it reports the missing topology and other expected reconciliation
failures, all of which must be attributable to recorded gaps.

## Authority exclusion and closure boundary

Migration metadata is excluded from the semantic definition projection,
definition digest, Approval Manifest semantic projection, positive binding
seeds, and downstream authority. Migration scaffolding is never current
semantic authority because raw migration creates no such scaffolding.

`verify_migration_result()` checks the frozen candidate invariants, exact
metadata and gap reconstruction, receipt candidate digest, structural errors,
and unexpected semantic errors. Expected gap-attributed semantic failures do
not make migration integrity fail. The candidate nevertheless remains `OPEN`,
`UNAPPROVED`, has no approval timestamp, and Product Definition Closure is
false.
