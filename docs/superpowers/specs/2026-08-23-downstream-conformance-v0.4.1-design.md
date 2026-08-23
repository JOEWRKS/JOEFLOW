# Downstream Conformance v0.4.1 Design

## Outcome

Add a reusable downstream subsystem that compiles an approved Product Definition into executable implementation obligations and evaluates real runtime sequences without changing canonical product truth. The acceptance signal is semantic detection: the harness must expose the known frozen Replication A and B failures, including B030 partial mutation and B031 actual non-finite numeric submission.

## Authority and isolation

- Source authority is `main` commit `16fc6edc362321ea03613339e224472b98bc1a04`.
- Canonical `state.json`, schema, validators, taxonomy, stable IDs, interrogation, and Closure semantics are read-only.
- The subsystem lives under `skills/joewrks-product-definition/downstream/`; evaluation evidence lives under `evals/downstream-conformance-v0.4.1/`.
- Derived bundles identify product slug, approved revision/digest, compiler identity/version, source file/hash, and provenance for every material semantic clause.
- A provenance source is a current stable object ID plus an exact JSON Pointer and SHA-256 of the canonical JSON value at that pointer. Compilation rejects missing pointers, hash mismatches, non-current sources, and active references to superseded objects.
- Product adapters may select and map canonical clauses into executable fields. They may not invent product semantics. The generic core contains only cross-product execution and verification rules.

## Components

### Python standard-library core

The core contains:

- a deterministic canonical JSON/hash utility;
- JSON Pointer resolution and provenance verification;
- action and lifecycle contract validation/compilation;
- a versioned JSONL protocol codec;
- subprocess adapter invocation;
- sequence execution and evidence recording;
- deep component-by-component no-op and mutation verification;
- generic invariant hooks with product-specific hook registration;
- UI-to-domain trace evaluation.

The compiler emits deterministic bundles. Runtime evidence may carry an observed timestamp, but timestamps are excluded from executable contract hashing.

### Action Conformance Contract

Each action declares a stable `action_id`, canonical sources, actor/auth/ownership constraints, object and revision binding, preconditions and state boundaries, input invariants, command, required and forbidden mutations, version/history/business/delivery effects, idempotency and rejection semantics, visible outcomes, superseded sentinels, trace obligations, and test obligations.

Fields that do not apply use explicit empty collections or a provenance-backed `not_applicable` declaration. Product-specific obligations cannot be inferred from labels, routes, or action names.

### Lifecycle/Reversal Contract

Lifecycle entries contain current states, allowed and forbidden transitions, boundary conditions, reversibility, timing window, object identity outcome, reason/confirmation/evidence requirements, authority, history preservation, and inactive superseded sentinels. Active transitions cannot cite a superseded source.

### JSONL runtime protocol

Protocol identity is `joewrks.downstream.execution/1.0`. Each request and evidence response identifies:

- protocol version and record kind;
- sequence/test ID and product slug;
- approved revision and digest;
- executable contract SHA-256;
- adapter name/version;
- frozen source commit/tree;
- command and typed input;
- before snapshot, command result, after snapshot;
- audit/history, business-side-effect, and delivery deltas.

Non-finite numbers are recursively represented as typed sentinels:

- `{"$number":"NaN"}`
- `{"$number":"+Infinity"}`
- `{"$number":"-Infinity"}`

An object containing `$number` may contain no other key. Adapters decode sentinels to the runtime's real numeric values immediately before invocation and re-encode runtime snapshots before JSON serialization. B031 therefore exercises real JavaScript `NaN` and `Infinity`, never JSON `null` substitutes.

### Runtime adapters

An adapter only performs:

`versioned protocol request -> actual frozen runtime invocation/readback -> versioned evidence response`

It does not decide whether the result is correct. The Python core compares observed evidence with the executable contract.

- Replication A adapter loads pinned frozen JavaScript in Node and invokes the actual public-action path.
- Replication B adapter lives outside the frozen implementation and uses the frozen toolchain to import and execute the actual TypeScript engine/selectors.
- Neither adapter patches, copies over, or instruments the frozen source tree.

### Deep verification

Rejected, stale, and unauthorized commands are evaluated independently across:

1. authoritative domain state;
2. version/revision;
3. audit/history;
4. business side effects;
5. notification/delivery effects.

The verdict retains every component result. Any allowed change must be declared by the canonical action contract; otherwise mutation is forbidden. This detects validation that occurs after partial mutation, including B030.

SUCCESS requires the declared authoritative mutation. IDEMPOTENT REPLAY requires no duplicate mutation/event/delivery and preservation of the original operation identity. Delivery failure after a business commit is evaluated as two separate outcomes.

### Sequence and trace execution

Sequence definitions compose versioned commands and expected semantic verdicts. The runner records every before/result/after transition and applies action obligations plus sequence-specific invariants. Supported reusable classes include happy, role/ownership/authority loss, stale version, validation rejection, idempotent replay, reversal boundaries, superseded sentinels, delivery retry/separation, terminal stop, destructive confirmation, rejected-then-related command, and historical projection.

A UI-to-domain trace is conformant only when it connects the canonical action through public invocation, handler, domain command, authoritative state, audit/history, side effects/delivery, and visible result/recovery. Rendered controls, handler existence, helper tests, build success, and success messages are not substitutes for the transition.

## Frozen regression strategy

- Replication A commit `9408434e640b9cf0bf6afaadd8f9d1f5f52e8943`: execute its public JavaScript action path in Node and prove that a material UI action can report success/audit while omitting the canonical domain mutation.
- Replication B source commit `eecebc28701006dd2c7be4045a22542e34719705`: execute the actual TypeScript engine/selectors from an external runner. B030 must show mutation in a REJECTED result. B031 must submit decoded real `NaN` and `Infinity` and detect acceptance/submission.
- Additional actual sequences cover stale/latest-value behavior, historical projection, terminal retry/worker behavior, authority loss, replay, delivery separation, and current-only transition sentinels as the frozen products support them.
- Revision 44 client feedback is an expressiveness probe only; it compiles preserved authority, exact-version, link lifecycle, concurrency/idempotency, delivery separation, and append-only history semantics without a new Make generation or verdict.

## Handoff and audit integration

Human-readable implementation/Figma Make handoff remains intact and gains a downstream bundle section naming the executable action contract, lifecycle contract, contract hash, runner command, and required sequences. A reusable blind-audit procedure requires evidence for precondition, public action, handler, state, provenance/side effects, and visible recovery. Implementation self-report and green test counts are non-authoritative.

## Exclusions

- responsive behavior;
- new product decisions or state fields;
- database/vendor implementation requirements;
- patching frozen A/B source;
- rerunning Figma Make;
- merging evaluation branches or changing `main`.

## Verification boundary

Completion requires the original 43 tests, new unit/integration tests, actual frozen runtime executions, exact protected-blob comparison with `16fc6ed…`, branch-only commit/push, and remote readback. A regression is reported as detected only when its sequence was executed and the Python authority evaluator produced the expected nonconformance.
