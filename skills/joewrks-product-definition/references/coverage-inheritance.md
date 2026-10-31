# Compact coverage rows

State 0.2.0 stays the canonical form: every requirement row has its 20 Core cells, every
screen its 16 state cells and 22 cells per major action. Writing them is where most of a
FREEZE goes, and on real projects many of those cells carry the same answer. A row may
therefore declare that answer once and omit the cells it implies. The declarations are
authoring conveniences inside 0.2.0, not a new schema version: `expand_coverage` writes
the omitted cells out, and every digest, validator and downstream reader sees that
explicit form, so a compact state and its explicit twin have the same definition digest and
Approval Manifest digest.

## What a row may declare

| Declaration | Where | Omitted cell becomes |
|---|---|---|
| `surface_manifest.grill_profile.AUTH` / `PERMISSION` = `N/A` | the profile (1.3.0) | `N/A` on the account, permission and session UX axes of every screen |
| `shape` | an action row | `N/A` on the axes listed for that shape in `ux-action-shapes-v2.json`: `navigate` (leave at once), `browse` (change what the screen shows), `local_choice`, `discard` (confirm, throw away, leave), `toggle`, `submit`, `destructive` |
| `default_authority` | a requirement, screen or action row | `COVERED` with those bindings |
| `execution` = `LOCAL` or `LOCAL_PURE` | `surface_manifest.grill_profile.ASYNC` (ACTIVE) | `N/A` on the ASYNC pack axes listed in `grill-profile-inheritance-v1.json`: `polling`, `reconciliation` for LOCAL; also `idempotency`, `duplicate_execution` for LOCAL_PURE |

A written cell always wins. An omitted axis that no declaration covers is still an
inventory error. A `default_authority` record whose type is not allowed on some axis
fails on that axis with a message naming the default; write that cell yourself or mark it
`N/A`. An unknown shape is an error. In the expanded view each implied cell carries
`inherited_from` (`profile`, `profile:ASYNC.LOCAL_PURE`, `shape:<name>` or `row`), so an audit
can tell a declared answer from a hand-written one; the digest projection strips the tag and
the declarations.

## Writing and converting

- New rows: declare first, then write only the cells that differ. In a `rows` patch an
  action carries `"shape": "navigate"` next to its `key`, and a requirement, screen or
  action row carries `"default_authority": [{"record_id": "FLOW-005", "pointer": "/paths"}]`;
  `open_revision.py` hashes the default like any binding. `draft_freeze.py` marks every
  action's `shape` `DECIDE`; rerun it with `--shape KEY=SHAPE` for each action and the
  draft declares the shape and leaves out the cells it implies. Delete yourself the cells
  a default implies.
- Existing rows: `python <skill-directory>/scripts/compact_coverage.py STATE_JSON --write`
  turns the most reused COVERED binding set of each row into its `default_authority` and
  drops the cells it reproduces. It writes only when the result expands back to the
  original byte for byte and keeps both digests, so an approved definition stays approved.
  Hand-written `N/A` cells are kept: an inherited `N/A` has no basis or rationale, so
  replacing one would change the record. Declaring a shape on an approved definition is
  therefore a semantic change that needs a new revision and approval.
- `open_revision.py` re-hashes a `default_authority` like any binding when its record is
  patched; `refresh_bindings.py` lists it under the row path (`coverage[0].default_authority`).

## Measured on real definitions (2026-10-31)

Lossless compaction of existing rows: AI-Gomoku rev 38 removed 38 of 202 cells, the
curated-lifestyle-store definition 209 of 1,320. Shapes apply to new rows. The v2 table
keeps, per shape, only the axes every measured action of that shape answered N/A
(AI-Gomoku and 48 agent-written actions); hand-written N/A sets otherwise varied from
author to author for the same action, which is what a declared shape removes.
