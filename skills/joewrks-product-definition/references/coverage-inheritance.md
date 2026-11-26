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

## Record types each axis accepts

A `COVERED`/`ADDRESSED` cell (and a `default_authority`) may bind only records of the types
its axis allows; the lists below come from `references/binding-contracts/*.json`.
`open_revision.py` and `explain_state_errors.py` name the axis, the allowed types and the
bound record's actual type when a binding does not fit, for example
`axis back: allowed [FLOW, RULE, SCR], actual STATE (STATE-007 /conditions)`.

| Core axis (`coverage[REQ].cells`) | allowed record types |
|---|---|
| `actor` | USR, DEC, RULE |
| `goal` | GOAL, REQ |
| `entry_point` | FLOW, SCR, RULE |
| `precondition` | RULE, STATE, FLOW |
| `happy_path` | FLOW, REQ |
| `alternative_path` | FLOW, RULE |
| `error` | FLOW, STATE, RULE |
| `recovery` | FLOW, STATE, RULE |
| `permission` | RULE, DEC, USR |
| `state` | STATE, RULE |
| `data` | DATA, RULE |
| `side_effect` | RULE, DATA, INT |
| `notification` | RULE, FLOW, INT |
| `validation` | RULE, DATA, AC |
| `boundary` | RULE, DEC |
| `persistence` | DATA, RULE |
| `security` | RULE, DEC |
| `privacy` | RULE, DEC, DATA |
| `analytics` | RULE, DATA, INT |
| `acceptance` | AC |

| Specialist pack (`grill_coverage[PACK].axes`, every axis) | allowed record types |
|---|---|
| `GRILL-AUTH-1` | USR, DEC, RULE, FLOW, STATE, DATA, AC |
| `GRILL-MONEY-1` | DEC, RULE, FLOW, STATE, DATA, INT, AC |
| `GRILL-FILE-UPLOAD-1` | DEC, RULE, FLOW, STATE, DATA, INT, AC |
| `GRILL-ASYNC-1` | DEC, RULE, FLOW, STATE, DATA, INT, AC |
| `GRILL-PERMISSION-1` | USR, DEC, RULE, FLOW, STATE, DATA, AC |
| `GRILL-DESTRUCTIVE-ACTION-1` | DEC, RULE, FLOW, STATE, DATA, INT, AC |

| UX state axis (`ux_coverage[SCR].states`) | allowed record types |
|---|---|
| `default` | SCR, STATE, FLOW, RULE |
| `loading` | STATE, FLOW |
| `empty` | STATE, FLOW, RULE |
| `partial` | STATE, FLOW, RULE |
| `success` | STATE, FLOW, AC |
| `error` | STATE, FLOW, RULE, AC |
| `disabled` | STATE, RULE |
| `permission_denied` | STATE, RULE, DEC, USR |
| `unauthenticated` | STATE, RULE, FLOW |
| `offline` | STATE, FLOW, RULE |
| `timeout` | STATE, FLOW, RULE |
| `retrying` | STATE, FLOW, RULE |
| `submitting` | STATE, FLOW |
| `completed` | STATE, FLOW, AC |
| `cancelled` | STATE, FLOW, RULE |
| `expired` | STATE, RULE, FLOW |

| UX action axis (`ux_coverage[SCR].actions[KEY].cells`) | allowed record types |
|---|---|
| `entry` | FLOW, SCR, RULE |
| `precondition` | RULE, STATE, FLOW |
| `input` | DATA, SCR, RULE |
| `validation` | RULE, DATA, AC |
| `submit` | FLOW, SCR, RULE |
| `success` | FLOW, STATE, AC |
| `failure` | FLOW, STATE, RULE, AC |
| `retry` | FLOW, STATE, RULE |
| `cancel` | FLOW, STATE, RULE |
| `back` | FLOW, SCR, RULE |
| `refresh` | FLOW, STATE, RULE |
| `duplicate_concurrent_action` | RULE, STATE, FLOW |
| `timeout` | FLOW, STATE, RULE |
| `offline` | STATE, FLOW, RULE |
| `permission` | RULE, DEC, USR |
| `session_expiration` | STATE, RULE, FLOW |
| `data_mutation` | DATA, RULE, FLOW |
| `side_effect` | RULE, DATA, INT |
| `notification` | RULE, FLOW, INT |
| `persistence` | DATA, RULE |
| `undo` | FLOW, STATE, RULE |
| `destructive_confirmation` | RULE, DEC, FLOW |

`N/A` cells take basis bindings of these types: Core and specialist GOAL, USR, REQ, DEC, RULE, FLOW, SCR, STATE, DATA, INT, AC, SURF, EVD; UX GOAL, USR, REQ, DEC, RULE, FLOW, SCR, STATE, DATA, INT, AC, SURF, EVD.

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
