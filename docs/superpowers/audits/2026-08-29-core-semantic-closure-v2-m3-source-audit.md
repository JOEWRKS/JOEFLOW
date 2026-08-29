# Core Semantic Closure V2 — M3 Remote Source Audit

**Audit status:** `REMOTE_SOURCE_VERIFIED / USER_EXECUTION_REPORTED`

**Audited branch:** `feat/core-semantic-closure-v2-m3-grill-engine`

**Audited HEAD:** `8786deb5749ba39e526d1707d63acc27f60b2b02`

**Tree:** `9f6fc04beb0dd35629c97fe155e4ff565a68f862`

**Planning base:** `f1ea8e10ad488b44458d5ad2b4704aa38e361d41`

## Verification boundary

This audit independently verifies the remote Git history, changed-file scope, and inspected M3 source contracts through the connected GitHub repository. It does **not** claim independent execution of the local test commands reported by the implementation agent.

GitHub exposes no combined status checks and no workflow runs for the audited HEAD. Reported targeted/focused/regression/full-suite results therefore remain `USER_EXECUTION_REPORTED`, not independently re-measured CI evidence.

## Remote history verification

Verified from GitHub:

- remote M3 branch HEAD is `8786deb5749ba39e526d1707d63acc27f60b2b02`;
- HEAD tree is `9f6fc04beb0dd35629c97fe155e4ff565a68f862`;
- HEAD parent is `ecdab73e98075f60546aa9f86c710eba32c1972a`;
- compare from planning base `f1ea8e10...` is `ahead_by: 14`, `behind_by: 0`;
- compare contains exactly 32 changed files;
- no compare entry exists under `skills/joewrks-product-definition/downstream/` or `evals/semantic-review-v0.4.3/`;
- the frozen legacy `state.schema.json`, `state_validation.py`, `state-contract.md`, and `state.example.json` are absent from the M3 diff;
- remote `main` remains `efd96410f6401cbf9624328e94b795c315164b7f`.

## Source-contract verification

### Deterministic Materiality

`materiality_v2.py` recomputes `NON_MATERIAL` only when outcome divergence is `NONE`/`LOW`, fan-out is `LOCAL`, reversibility is `TRIVIALLY_REVERSIBLE`, and every risk flag is false. All other valid shapes classify as `MATERIAL`. `user_visible` does not independently revoke the strict non-material autonomy boundary.

High risk is independently detected when reversibility is `COSTLY_TO_REVERSE`/`IRREVERSIBLE` or any risk flag is true.

### Unknown/Decision authority and selective questioning

`grill_v2.py` implements the frozen authority order:

1. qualifying evidence → `EVIDENCE_RESOLVABLE`;
2. missing factual/constraint/behavioral authority → `EXTERNAL_AUTHORITY_REQUIRED`;
3. strict `NON_MATERIAL` → `AGENT_AUTONOMOUS`;
4. material high risk → `USER_DECISION_REQUIRED`;
5. confirmation-ready high-confidence recommendation → `USER_CONFIRMATION`;
6. otherwise → `USER_DECISION_REQUIRED`.

Question selection validates the state, considers only OPEN `USER_CONFIRMATION` / `USER_DECISION_REQUIRED` unknowns, deterministically ranks unlock fan-out, risk, material fan-out, category and stable ID, and returns at most one projection of canonical unknown data.

Unknown origin includes `GRILL_TOPOLOGY`, `GRILL_PACK_AXIS`, and `MIGRATION_RECONCILIATION` with its canonical `source_path`. Unknown blocking references are validated and cycle-checked.

Decision provenance separates `decided_by`, recommendation acceptance, resolution mode, source unknowns and authority. Agent decisions are valid only as reciprocal `AGENT_NON_MATERIAL_DEFAULT` decisions over strictly non-material agent-autonomous source unknowns.

### Approved exception fix

The final commit `8786deb...` closes the specifically approved second final-fix finding. A CURRENT Decision using `EVIDENCE` or `MIGRATION_RECONCILIATION` now emits `invalid_unknown_resolution_authority` in addition to the provenance error, causing the affected Decision record to be counted by `invalid_resolution_authority`.

The same commit adds regression coverage for:

- CURRENT `EVIDENCE` → metric count `1`;
- CURRENT `MIGRATION_RECONCILIATION` → metric count `1`;
- linked invalid unknown + Decision → two affected records;
- permitted CURRENT modes `USER_DECISION`, `USER_ACCEPTED_RECOMMENDATION`, `AGENT_NON_MATERIAL_DEFAULT`, and `EXTERNAL_CONSTRAINT` → no authority-conflict false positive.

### Mandatory Grill topology and pack identity

M3 requires the six-domain `surface_manifest.grill_profile`:

```text
AUTH
MONEY
FILE_UPLOAD
ASYNC
PERMISSION
DESTRUCTIVE_ACTION
```

Each domain is explicitly `ACTIVE`, `N/A`, or `OPEN`; it cannot be silently omitted. Existing `MONEY_FLOW`, `ASYNC_PROCESS`, `PERMISSION`, and `DESTRUCTIVE_OPERATION` surfaces force corresponding ACTIVE profile truth. `N/A` requires current basis authority and meaningful rationale; `OPEN` requires an exact topology-origin unknown.

Core Grill is always compiled. ACTIVE specialist packs are compiled from the profile, not optional surface tags. Checked-in pack files are validated against frozen identities, version `1.0`, ordered axis inventory and materiality floors; pack digests are SHA-256 commitments of canonical parsed JSON.

Independent specialist OPEN axes require one unique exact-origin unknown. Reusing/mismatching an origin produces `umbrella_unknown_compression`; material-floor axes require a recomputed MATERIAL unknown.

### Grill-aware discovery baseline

`discovery_v2.py` commits deterministic active pack instances, including pack ID, version, digest and sorted target refs. `active_grill_packs_complete` is derived from topology/identity/row/inventory gaps and deliberately does not require every pack axis to be resolved; `unresolved_pack_axes` remains separate.

`unknown_unknown_exhaustiveness_claimed` remains hard-coded false.

### Semantic Closure boundary

`evaluate_closure_v2()` still returns:

```text
closed = false
definition_digest = null
semantic_closure_not_implemented = 1
```

It now exposes M1–M3 discovery/Grill metrics but does not claim exact Coverage Binding, informed approval, or Semantic Closure.

## Execution evidence boundary

The implementation report states:

```text
targeted exception regression: 3/3 PASS
M3 focused: 191/191 PASS
M2 regression: 59/59 PASS
legacy regression: 36/36 PASS
frozen legacy regression: 1/1 PASS
full suite: 425 tests PASS, 1 SKIP
git diff --check: PASS
final read-only review: Critical 0 / Important 0 / Minor 0
```

Those are preserved as implementation/user execution evidence. They were not independently rerun in this audit because the connected GitHub surface exposes no CI/status execution for this HEAD.

## Audit ruling

No source-level blocker was found against the frozen M3 scope in the inspected remote implementation.

Roadmap progression may treat M3 as:

```text
CORE_SEMANTIC_CLOSURE_V2_M3_IMPLEMENTED
— GRILL_ENGINE / NOT_INTEGRATED

remote source: VERIFIED
execution tests: USER_EXECUTION_REPORTED
independent execution remeasurement: NOT_PERFORMED
```

This ruling does not itself authorize a V2 Semantic Closure claim. M4 must implement exact authority binding, informed approval, semantic definition digest, and the actual Product Definition Semantic Closure gate before `closed = true` can ever be valid. M5–M6 remain unstarted by this audit.
