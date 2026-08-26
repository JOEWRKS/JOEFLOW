# Implementation Plan Traceability Audit — B2B RMA rev79

## Verdict

**FAIL.** The two failures recorded for revision 78 were retested against the current uncommitted revision 79. The two lifecycle states are no longer orphaned, and the formerly unowned acceptance-strengthening subsection now contains active `AC-*` anchors. However, one substantive AC owner is still missing from that subsection, and one of the seven projections still contains a stale `CLOSED` assertion that contradicts the unapproved `READY_FOR_REVIEW` canonical state.

No canonical file was changed by this audit. No approval or commit was performed.

## Audited authority

- Canonical authority: `product-definition/b2b-rma-dogfood/state.json`
- Canonical definition revision: `79`
- Canonical definition digest: `1f329295fa2f11bda80709a63c5f6005d0bf47f9549b8978c712059230780a9a`
- Canonical status: `READY_FOR_REVIEW`
- Approval: `user_approved = false`; approved revision, digest, and timestamp are all `null`
- Canonical file SHA-256: `b310b718ddc38735b29446b9c40f6e278dbe58fee29b1eae47ef141aaa656147`
- Audited implementation-plan SHA-256: `ee384ccdc5a75a01e94f442aeee41b762a62fa6f7fa29c9e81edcff3594fe416`

Canonical evidence is at `state.json` lines 6-12. The digest above is the fresh official closure-validator result; it is distinct from the whole-file SHA-256.

## Before/after results

| Check | Revision 78 audit | Revision 79 retest | Result |
|---|---:|---:|---|
| Active implementation-trace objects reachable | 120/122 | 122/122 | PASS |
| Active lifecycle states reachable | 6/8 | 8/8 | PASS |
| Plan level-2/level-3 sections with an active canonical anchor | 56/56 | 57/57 | PASS |
| Acceptance-strengthening subsections with an explicit active `AC-*` anchor | 26/27 | 27/27 | PASS |
| Four policy bullets in `DEC-046`·`DEC-057` subsection with complete substantive AC ownership | not previously measured | 3/4 | FAIL |
| Seven projections wholly consistent with revision/digest/status/approval | 7/7 | 6/7 | FAIL |

Revision 79 active trace totals are `REQ 7/7`, `RULE 76/76`, `FLOW 1/1`, `SCR 4/4`, `STATE 8/8`, `DATA 13/13`, `INT 6/6`, and `AC 7/7`, for `122/122` reachable and gap `0`.

## Retest of the two recorded failures

### 1. `STATE-001` and `STATE-002`: repaired

- `DEC-014.affects` contains `STATE-001` (`state.json` lines 5173-5192), while `STATE-001.depends_on` contains `DEC-014` (`state.json` lines 9846-9854). Both objects are active. The new implementation guidance at `IMPLEMENTATION_PLAN.md` line 29 explicitly describes case creation into request receipt and anchors `DEC-014`, `STATE-001`, `FLOW-001`, `SCR-002`, and `SCR-004`.
- `DEC-018.affects` contains `STATE-002` (`state.json` lines 5287-5315), while `STATE-002.depends_on` contains `DEC-018` (`state.json` lines 9857-9866). Both objects are active. The new guidance at `IMPLEMENTATION_PLAN.md` line 30 explicitly describes entry into approval waiting and preserves the already-approved out-of-policy and additional-information branches through `STATE-006` and `STATE-007`.
- The added graph edges do not create a new role, decision, state, or branch. They bind the pre-existing `DEC-014` intake semantics to the pre-existing request-receipt state and the pre-existing `DEC-018` owner-decision semantics to the pre-existing approval-wait state. The additional state dependencies on `DEC-013`, `DEC-015`, and `DEC-016` are also existing role and eligibility boundaries, not new product semantics.

The exact required reciprocal links therefore pass, and neither lifecycle state is orphaned from implementation guidance or the active canonical graph.

### 2. `DEC-046`·`DEC-057` acceptance ownership: explicit anchors added, substantive gap remains

`IMPLEMENTATION_PLAN.md` lines 435-440 now contain active `AC-*` IDs on all four policy bullets. Every AC that is actually listed has substantive canonical support; no listed AC is overbroad:

| Plan policy bullet | Listed active AC owners | Canonical support | Result |
|---|---|---|---|
| Evidence type, 20 MB, validation, failure preservation | `AC-001`, `AC-003`, `AC-004`, `AC-006`, `AC-007` | Direct upload acceptance at state lines 11271, 11377, 11436, and 11730; audit reconstruction at line 11630 | PASS |
| Internal/external package permissions and out-of-assignment bulk-download denial | `AC-002`, `AC-004`, `AC-005`, `AC-006`, `AC-007` | Listed ACs cover owner/non-owner access, settlement scope, package-content separation, and customer external access at lines 11333, 11448, 11552, 11642, and 11738 | **FAIL: missing `AC-003`** |
| Draft deletion boundary and no post-submission hard-delete UI | `AC-001` through `AC-007` | Every mapped AC has an explicit hard-delete or draft-delete acceptance statement at lines 11275, 11333, 11381, 11448, 11552, 11642, and 11738 | PASS |
| Retention period, automatic deletion, and deletion-proof values remain deferred | `AC-002`, `AC-006` | Direct exclusion/no-function acceptance at lines 11333 and 11642 | PASS |

The missing mapping is exact: the package-permission bullet at `IMPLEMENTATION_PLAN.md` line 438 says warehouse personnel must be denied out-of-assignment bulk download, while canonical `AC-003.record_lifecycle_acceptance` at `state.json` line 11381 explicitly owns that observable denial. `AC-003` is active but is absent from the line-438 owner list. The other listed owners do not erase that requirement-level ownership. Missing mappings: `1`; unsupported or overbroad listed mappings: `0`.

## Stable IDs and active/superseded guidance

- Canonical object IDs: `283`; duplicates: `0`; invalid group-prefix/three-digit forms: `0`.
- Compared with the revision 78 Git base, IDs added: `0`; IDs removed: `0`. The repair changed references without renumbering, reusing, or deleting stable IDs.
- Historical objects are `UNK-018 → UNK-061`, `DEC-033 → DEC-034`, and `RULE-042 → RULE-043`. `IMPLEMENTATION_PLAN.md` mentions only `DEC-033` and `RULE-042`, at line 5, explicitly as superseded history. They were excluded from active reachability and did not satisfy any active guidance section.
- All 57 level-2/level-3 plan sections contain at least one active canonical anchor; no section depends only on superseded guidance.

## Projection consistency

All seven projections were read. Each carries revision `79`, digest `1f329295fa2f11bda80709a63c5f6005d0bf47f9549b8978c712059230780a9a`, `READY_FOR_REVIEW`, and empty approval in its primary snapshot. Six are wholly consistent: `PRODUCT_DEFINITION.md`, `UNKNOWN_LEDGER.md`, `DECISION_LEDGER.md`, `USER_FLOWS.md`, `SCREEN_SPEC.md`, and `IMPLEMENTATION_PLAN.md`.

`FIGMA_MAKE_HANDOFF.md` fails whole-document consistency. Line 7 correctly says revision 79 is awaiting approval and is `READY_FOR_REVIEW`, but line 421 still says, “제품정의는 `CLOSED`”. That is a direct contradiction of canonical lines 6-12 and of the projection's own line 7. This is not merely future-tense guidance; it asserts the present product-definition state and refers to an “approval record” that revision 79 does not have.

No old revision-78 digest remains in the seven projections.

## Official validators and implementation boundary

- `python skills/joewrks-product-definition/scripts/validate_state.py product-definition/b2b-rma-dogfood/state.json`: exit `0`; `valid: true`; errors `[]`.
- `python skills/joewrks-product-definition/scripts/validate_closure.py product-definition/b2b-rma-dogfood/state.json`: exit `1`; `closed: false`; digest exact match; errors `[]`. All semantic, coverage, UX, orphan, stale-artifact, and task metrics are `0`. The nonzero metrics are `invalid_closed_status = 1`, `missing_user_approval = 1`, `stale_approval = 1`, and `stale_user_approval = 1`, which reflect the intentional unapproved `READY_FOR_REVIEW` state. This audit does not approve revision 79 and therefore does not treat it as closed.
- `project.implementation_started` is `false` (`state.json` line 103), and `objects.tasks` is empty (`state.json` line 11808). The working-tree changes are confined to the eight canonical/projection files and evaluation reports; no implementation source change is present.

The official validators do not check subsection-level AC ownership or contradictory prose elsewhere in a projection, so their results do not clear the two failures above.
