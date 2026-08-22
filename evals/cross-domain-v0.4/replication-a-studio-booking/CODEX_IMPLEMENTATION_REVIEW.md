# Replication A — Codex Implementation Review

## Verdict

**FAIL — CODEX_DRIFT_UNRESOLVED**

The authorized three correction passes are exhausted with one current BLOCKING finding and eight current MAJOR findings. The implementation is not a verified substitute for the Figma Make stage. Replication B was not started in this implementation track.

## Authority and evaluation boundary

- Source commit: `16fc6edc362321ea03613339e224472b98bc1a04`
- Product: `studio-booking-dogfood`
- Approved Product Definition: revision `62`, status `CLOSED`
- Approved digest: `8ebb472aa66a5b680961e102db950214cea2d0be3b644164f23712030b9d8a7c`
- Audited Figma file: `fClM2GgNhwEDIiqZcIWhNZ`
- Audited native roots: desktop `4:2`, mobile `4:656`
- Historical Figma catalog root `1:4` was not used as implementation authority.
- `Open Design: UNAVAILABLE_IN_CURRENT_RUNTIME`
- Exact Open Design readback: `No MCP server named 'open-design' found.`
- The approved Product Definition, canonical state, uppercase projections, Closure approval, and Figma artifact were not revised by this track.
- `make-input-record.md` was preserved. Figma Make was not executed.

Authority order remained: approved Product Definition → `state.json` → uppercase projections → audited native Figma → `CODEX_IMPLEMENTATION_HANDOFF.md` → implementation.

## Required evidence inventory

- `product-definition/studio-booking-dogfood/CODEX_IMPLEMENTATION_HANDOFF.md`
- `codex-design-refinement-report.md`
- `codex-implementation-report.md`
- `codex-initial-audit.md`
- `codex-correction-pass-1.md`
- `codex-correction-pass-1-audit.md`
- `codex-correction-pass-2.md`
- `codex-correction-pass-2-audit.md`
- `codex-correction-pass-3.md`
- `codex-correction-pass-3-audit.md`
- `ACTION_DOMAIN_COVERAGE.md`
- `TEST_GAP_ANALYSIS.md`
- this `CODEX_IMPLEMENTATION_REVIEW.md`

The implementation is isolated under `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/` and uses dependency-free HTML, CSS, ES modules, a local static server, and Node's built-in test runner.

## PM evidence index

| Independent review question | Frozen evidence |
| --- | --- |
| Exact canonical requirement and expected transition | `ACTION_DOMAIN_COVERAGE.md` maps every one of the 78 visible actions to its `SCR`, `REQ`, and `RULE` authority and names the expected transition. |
| Exact source/UI action and actual behavior | The same matrix records the final `app.handle → executeAction` handler, mutation result, audit-only status, tests, and inherited severity for every action. |
| Why `A-CODEX-DRIFT-001` is BLOCKING | `TEST_GAP_ANALYSIS.md` records that the primary stateful Customer/Staff/Owner prototype objective is absent across the product, not at one secondary edge. |
| Why each of the eight findings is MAJOR | `TEST_GAP_ANALYSIS.md` gives an outcome-changing rationale for `002–009`: permissions, booking correctness, consent/price evidence, access/recovery, delivery operations, destructive/concurrency safety, accessible usability, and evidence integrity. |
| Findings before pass 1 | Initial set was `001` BLOCKING, `002–009` MAJOR, and `010` MINOR. |
| Findings fixed during passes 1–3 | Pass 1 closed `006`; pass 2 closed newly introduced `011`; partial code improvements did not close the other finding families. |
| Findings remaining after pass 3 | `001` BLOCKING; `002,003,004,005,006,007,008,009` MAJOR; `010` MINOR remains intentionally uncorrected. |
| New material regression | Pass 1 introduced `011`, fixed in pass 2. Pass 3 regressed/reopened `006` by replacing delivery UI branches with the generic dispatcher fallback. |
| Why 14/14 missed the disconnect | `TEST_GAP_ANALYSIS.md` traces all 14 tests and shows inventory/direct-helper/regex coverage without a rendered click-to-state assertion. |

These additions document the frozen failed state. They do not correct implementation behavior or revise any prior finding.

## Bounded design refinement result

The audited Figma was freshly read at roots `4:2` and `4:656`. The refinement retained its white/neutral surfaces, dark primary actions, restrained red recovery treatment, role labels, grouped fields/actions, 27 desktop screen identities, and three 360px role journeys. UI UX Pro Max guidance was used only for semantic status color, 4/8px spacing, focus, contrast, and responsive operational layout. Apple guidance was limited to predictable wayfinding, system-font legibility, immediate feedback, restraint, and reduced motion. Gradients, glass effects, floating actions, remote fonts, expressive motion, and new product semantics were rejected.

## Blind audit and correction history

| Stage | Fresh test result | Material audit state |
| --- | ---: | --- |
| Initial implementation | 10/10 pass | 1 BLOCKING, 8 MAJOR, 1 MINOR |
| Correction pass 1 | 11/11 pass | 1 BLOCKING, 8 MAJOR open; delivery finding closed; new resend crash finding opened |
| Correction pass 2 | 13/13 pass | 1 BLOCKING, 7 MAJOR open; resend crash closed |
| Correction pass 3 | 14/14 pass | 1 BLOCKING, 8 MAJOR open; delivery behavior regressed |

Only current BLOCKING/MAJOR findings were eligible for correction. The three-pass cap was respected. No controller-authored fourth correction was made.

## Final current findings

| ID | Severity | Final evidence |
| --- | --- | --- |
| `A-CODEX-DRIFT-001` | BLOCKING | Most canonical actions route to a generic audit append. Browser `confirm_booking` reported success while `bookings` remained empty; management-link and delivery actions likewise created no substantive state. |
| `A-CODEX-DRIFT-002` | MAJOR | Authorization remains incorrect: Staff onboarding/inquiry actions are denied, while a Customer can receive mutation authority from a synthetic `prebooking` context rather than an authenticated reservation/session. |
| `A-CODEX-DRIFT-003` | MAJOR | Booking validation ignores operating hours and equipment outage in the probed path; the SPA no longer invokes authoritative booking commit behavior. |
| `A-CODEX-DRIFT-004` | MAJOR | Price/policy snapshots omit required identity/time details and the browser does not render or execute publish, withdraw, old/new/delta, or booking-consent semantics. |
| `A-CODEX-DRIFT-005` | MAJOR | Management-link issuance is disconnected; expired-session draft capture/recovery and deletion transitions contradict the approved lifecycle. |
| `A-CODEX-DRIFT-006` | MAJOR | The domain helper models retry timing, but the browser delivery actions regressed to generic audit-only behavior in pass 3. |
| `A-CODEX-DRIFT-007` | MAJOR | Destructive confirmation is not wired, authority loss does not revoke the modeled operator session, and idempotent replay can return a stale pre-cancellation result. |
| `A-CODEX-DRIFT-008` | MAJOR | The 78 labels exist, but the 27 screen schemas are imported without being rendered; most screens lack action-specific controls/error association and one error path can dereference a missing field. |
| `A-CODEX-DRIFT-009` | MAJOR | The 14 tests verify helper behavior, counts, and source presence but do not detect the SPA's disconnected canonical transitions; they overstate end-to-end coverage. |

`A-CODEX-DRIFT-011`, the Boolean-shadow resend crash, remains fixed. `A-CODEX-DRIFT-010` remains an uncorrected MINOR metadata-pin observation because the correction contract allowed only current BLOCKING/MAJOR work.

## Native browser and visual review

The initial implementer browser result was contaminated by an unrelated stale browser/port binding and was correctly left unverified. The final review used a fresh in-app browser binding and a task-owned server at `http://127.0.0.1:43173/?artifact=studio-booking-rev62-pass3`.

| Check | Expected source | Observed result | Result |
| --- | --- | --- | --- |
| Artifact identity | Handoff / implementation | Title `스튜디오 예약 운영`; correct unique URL; 27 navigation buttons | PASS |
| Desktop layout | Figma root `4:2` | At 1280×900, `scrollWidth=1265` for `innerWidth=1280`; role/navigation, screen card, fields, action, status, and state readback were visible without horizontal overflow | PASS |
| Mobile reflow | Figma root `4:656` / refinement | At 375px, client/scroll width `360/360`; at 320px, `305/305`; sampled controls were at least 44px high | PASS |
| Keyboard focus | Accessibility contract | Selecting `SCR-007` moved focus to `#screen-heading` | PASS |
| Reduced motion | Refinement contract | Emulated `prefers-reduced-motion: reduce` matched; sampled controls computed animation/transition durations of `0.00001s`; media emulation was then reset | PASS |
| Booking journey | Approved scenario 1 | `확정 예약` produced generic status `confirm_booking 기록이 생성되었습니다.` but state stayed at version 2 with `bookings=[]` and all policies null | FAIL |
| Destructive cancellation | Approved scenario 8 | `SCR-007` exposed zero dialog elements; after entering a reason, `확정 cancellation` emitted generic audit status with no confirmation continuation | FAIL |

Visual screenshots at desktop, 375px, and 320px were inspected during the run. The visual shell is readable and responsive, but those presentation passes do not cure the substantive behavior drift. The isolated server process was matched by PID, start time, executable path, command line, and listener before shutdown; immediate cleanup readback confirmed both process and port absent. A later check found the numerical PID reused by Codex's unrelated `node_repl.exe` with a later start time and no port-43173 listener; it was correctly left untouched.

## Fresh final verification

| Command/readback | Exit / result |
| --- | --- |
| `npm test` | exit 0; 14 pass, 0 fail |
| `validate_state.py` on canonical A state | exit 0; `valid=true`, errors 0 |
| `validate_closure.py` on canonical A state | exit 0; `closed=true`, digest exact, all 19 metrics zero |
| Final browser server | exact artifact served; task-owned listener cleanup verified absent |
| Frozen Skill/validator/schema diff from source commit | empty |

Passing tests are not accepted as an end-to-end verdict because the blind audit and browser probes demonstrate that the tests do not exercise the disconnected SPA behavior.

Canonical source hashes remained equal to the pre-implementation baseline:

| File | SHA-256 |
| --- | --- |
| `state.json` | `c18c8b2593e0cafb8e41f37d94126fa7ed1e99f81fb58961d89765561b84e12c` |
| `PRODUCT_DEFINITION.md` | `d9d970573eea2ee88a835098eee6692759c4ce3eb65473cc946b394ec063642b` |
| `USER_FLOWS.md` | `715b41f74042f886ff0ca75f733f15cb21290320c0b85f0c3bc09abcd22a28a3` |
| `SCREEN_SPEC.md` | `0ea8ca4386607d2dad7f29f1efc92d0bd09635b78537c0d89cd130dd50b0cfb1` |
| `DECISION_LEDGER.md` | `49a489ff6f8de5344990e7c5a9f97fe8b98c6b8a1cf517379ed4fcd246a4f2bb` |
| `UNKNOWN_LEDGER.md` | `ca58638a36926efcb802cef8065706ed452f06e97b1fc3c481a4cdba6ff42137` |
| `IMPLEMENTATION_PLAN.md` | `5af767d27ecfcff8772692d2fea5f5a01570b5ba2e9bdee0a5417db5fd478d65` |
| `FIGMA_MAKE_HANDOFF.md` | `53397b626182a142f965b97072a9db906a57678e116335de89fc19fecd094919` |

The newly authorized handoff hash is `298379c0903a277a468906faca7dbd98acf5cee283c5f38bcaef517500bab680`. The preserved `make-input-record.md` hash is `f046ad52fed6596baf1fc2b56f46917ec93c466fcb6ca9c3f7aa83d3c040fb88`.

## Comparison with the historical v0.3.1 Make run

The historical Make run began with five BLOCKING and seven MAJOR findings, then reached zero material findings after three passes. Its recurrent families were authentication/session direction, exact-version or token ownership, lifecycle/link restoration, idempotency/concurrency, delivery separation, recovery/history, and mobile behavior.

The Codex track reproduces several of those families—permissions/session binding, lifecycle recovery, idempotency, and delivery wiring—but does not converge. Its dominant new failure is a catalog-shaped SPA whose visible actions are not connected to the tested domain transitions. Studio-specific hours/equipment conflicts, policy snapshots, management drafts, and destructive booking semantics are artifact-specific manifestations of the same integration gap.

Classification: `CODEX_IMPLEMENTATION_BEHAVIOR`. The failure does not revise the approved Product Definition, canonical Closure, audited Figma, Skill, schema, validator, or taxonomy.

## Evidence boundary

This result evaluates an isolated deterministic browser prototype. It does not claim production authentication, persistence, encryption, email delivery, immutable audit, provider integration, database concurrency, deployment, load, security, or Figma Make execution. Replication A stops here with unresolved material implementation drift.
