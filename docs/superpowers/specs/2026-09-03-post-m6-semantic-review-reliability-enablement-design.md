# Post-M6 Semantic Review Reliability Enablement Design

Date: 2026-09-03

Status: design candidate for PM review

Working name: `Post-M6 Semantic Review Reliability Enablement`

This work is not assigned an `M7` identity.

## 1. Context

The authoritative repository baseline for this design is:

```text
main commit: cdc0eb4a972020666f73f7d267a70a1972675054
main tree:   6e28df29454a5b7475556a672ed9a2b33207736b
```

The current Product Definition authority is schema `0.2.0`, revision `2`,
`CLOSED / APPROVED`, with definition digest
`81d3b7ff59dbce321dc27fab6b51f03db4201dc1f4a1ea3d6b202f3f76afddcf`
and Approval Manifest digest
`079ef1bb60ccc382a66c6c764519e67e606744a9d10425310cc1b868be490003`.
The DEC-042 provenance-only correction and its M6 downstream/runtime
regeneration are complete authority. This design does not reopen them.

The current M6 dogfood chain is conformant:

```text
state 0.2.0 CLOSED/APPROVED
→ joewrks.handoff-definition/2.1
→ joewrks.action-conformance/2.1
→ dependency audit
→ joewrks.semantic-review/2.1 only when REVIEW_REQUIRED
→ joewrks.runtime-conformance-plan/1.0
→ joewrks.downstream.execution/1.0 evidence
→ joewrks.runtime-evidence-bundle/1.0
→ joewrks.runtime-conformance-report/1.0
```

The current dogfood contract has six actions, zero lifecycles, 131
direct-authority fields, seven machine-derived fields, zero review-required
fields, zero semantic authority gaps, and zero contract expressiveness gaps.
Its runtime coverage is complete and the implementation result is
`IMPLEMENTATION_CONFORMANT`. Semantic review was correctly `NOT_REQUIRED` for
that contract, while the independent assurance property remains:

```text
semantic-review/2.1 reliability = NOT_MEASURED
```

## 2. Current reliability blocker

The semantic-review implementations and deterministic validators exist. The
missing evidence is that a semantic reviewer produces repeatable results while
receiving only its exact approved inputs.

Already verified by existing committed evidence:

- the v0.4.3 `joewrks.semantic-review/1.0` implementation and deterministic
  reliability gate exist;
- the v0.4.3 control-plane defects discovered in Run-01 were repaired and the
  repaired path passed its recorded regression audit;
- Run-01 is `INVALID / CALIBRATION_CONTROL_PLANE_DEFECT`, not a semantic
  reliability result;
- the v0.4.3 normative oracle has status
  `PM_APPROVED_NORMATIVE_ORACLE` and remains controller-only;
- M6 action-conformance/2.1, runtime planning, runtime evidence admission, and
  runtime verification are conformant;
- semantic-review/2.1 valid completion is assurance evidence only and never
  creates Product Definition authority.

Not verified:

- manifest-only reviewer execution under an enforced isolation boundary;
- reviewer independence from repository, oracle, prior outputs, sibling
  packages, sibling outputs, and hidden evaluator material;
- real reviewer repeatability for `joewrks.semantic-review/2.1`.

The historical capability probe found `RUN01_READABLE = YES` from an ephemeral
Codex context whose working directory was outside the repository. A separate
working directory therefore did not create a filesystem security boundary.
The frozen accounting remains:

```text
REAL_CALIBRATION_ATTEMPTS = 1
VALID_REAL_CALIBRATION_RUNS = 0
real reviewer reliability = NOT_MEASURED
```

This Phase 0 capability work is not a semantic reviewer execution and does not
change those counters.

## 3. Goals

1. Define a minimal execution boundary in which a reviewer can receive only
   its immutable package, immutable brief/instruction, run envelope, and output
   schema.
2. Make isolation a controller-observed property, not a reviewer-authored
   Boolean assertion.
3. Define positive and negative capability evidence that must pass before any
   real calibration context starts.
4. Bind every request and response to an exact review contract, package,
   reviewer, run, model, and runtime configuration.
5. Preserve the existing semantic-review and action-conformance meanings.
6. Keep invalid infrastructure runs distinct from semantic calibration
   failures.
7. Keep v0.4.4 blocked until valid semantic-review/2.1 reliability evidence
   exists.

## 4. Non-goals

This design does not:

- implement a reviewer runner;
- execute C1, C2, C3, a golden case, or a production semantic review;
- change Product Definition schema, records, approval, Closure, or coverage;
- change action-conformance/2.1, runtime-conformance, or execution semantics;
- change semantic-review/1.0 or semantic-review/2.1 package/output semantics;
- alter any v0.4.3 golden answer, threshold, rationale, negative regression, or
  historical result;
- promote v0.4.4;
- build a general sandbox service, job queue, Kubernetes layer, dashboard,
  plugin runtime, persistent database, or multi-user review service;
- define an implementation plan.

## 5. Existing semantic-review architecture

### 5.1 Historical v0.4.3 reliability harness

`joewrks.semantic-review/1.0` is a hash-bound sidecar over
`joewrks.action-conformance/1.0`. Its package validator binds a canonical
authority, action contract, provenance inventory, responsibility profile,
semantic obligation index, reviewer brief, output schema, identity inventory,
and exclusion manifest. Its reliability gate requires at least three fresh
reviews, exact package/brief identity, exact review identity coverage, zero
pending records, perfect frozen-golden verdict and rationale accuracy, zero
unexpected rubric/package errors, no unresolved normative disagreement, no
same-rule repeated disagreement, and the frozen agreement thresholds. There is
no majority-vote escape hatch.

The current v0.4.3 controller freezes raw outputs before loading the normative
oracle and scores each of three 15-case golden cohorts through production
`evaluate_goldens(...)`. It expects three full reviews plus 45 single-golden
reviews, for 48 unique contexts.

The controller's current isolation evidence is declarative. Its run envelope
hash-binds:

```json
{
  "fresh_context": true,
  "previous_verdict_access": false,
  "manifest_only_evidence": true
}
```

Hashing that object proves its bytes did not change; it does not prove an
operating-system or service boundary denied access. The new runner must supply
independent capability evidence before that declaration can be truthful.

### 5.2 Current semantic-review/2.1 boundary

`joewrks.semantic-review/2.1` is the assurance-only sibling for
`joewrks.action-conformance/2.1`. It packages only legitimate
`REVIEW_REQUIRED` obligations and binds the exact semantic contract, approved
definition digest, responsibility-profile identity, proposed values, current
source seed snapshots, obligation IDs, and package hash. Its current verdicts
are:

```text
CONFIRMED_INTERPRETATION
REJECTED_INTERPRETATION
UPSTREAM_AUTHORITY_GAP
```

Its completion status is structural and does not establish reliability.

### 5.3 Mandatory compatibility finding

The frozen semantic-review/2.1 contract explicitly states that v2.0 and v2.1
package/output identities are mutually invalid and that v2.1 does not import or
infer any v2.0 or v1 reliability/calibration identity. The v0.4.3 harness uses
`joewrks.semantic-review/1.0`, a different responsibility model, output schema,
identity model, and verdict vocabulary.

Therefore:

- a future PASS from the unchanged v0.4.3 C1/C2/C3 corpus cannot, by itself,
  change semantic-review/2.1 reliability;
- runner isolation can be transport-generic, but reliability evidence must be
  bound to the exact semantic-review contract version;
- before a real 2.1 calibration, a separate PM-frozen 2.1 calibration authority
  must exist, or a separately approved normative compatibility decision must
  explicitly authorize another mapping;
- this design chooses no inheritance shortcut and does not create that missing
  calibration authority.

This is a pre-calibration compatibility gate, not a Product Definition blocker
and not permission to modify either semantic-review contract.

## 6. Threat model

The reviewer is not treated as a malicious person. The threat is accidental or
model-initiated information access that invalidates reliability evidence.

### 6.1 Filesystem leakage

Forbidden sources include the repository root and parent, `.git`, Git
worktrees, evaluator/controller files, golden truth, previous outputs, sibling
reviewer inputs/outputs, common temporary directories, inherited working
directories, absolute paths, `..` traversal, symlinks, junctions, UNC paths,
and host-mounted storage.

### 6.2 Process and environment leakage

Forbidden sources include inherited environment variables, command-line
secrets, parent process metadata carrying paths, shared process memory, shared
agent context, saved conversation state, response continuation IDs, common
scratch locations, shell history, provider retrieval state, and cached prior
review content.

### 6.3 Package and cohort leakage

One reviewer must not receive another reviewer's package or output. A golden
reviewer must receive one case package, never the golden answer bank or another
case package. A full reviewer must not receive golden packages. No reviewer
receives scoring truth, confusion matrices, disagreement analysis, correction
hints, prior verdicts, or seed oracles.

### 6.4 Network and tool leakage

The reviewer must have no arbitrary filesystem, shell, Git, GitHub, web search,
browser, connector, retrieval, MCP, remote storage, or code-execution tool. A
prompt saying not to use those tools is not a control. The execution interface
must omit the capabilities.

### 6.5 Controller compromise boundary

The trusted controller necessarily knows package identities, raw outputs,
scoring rules, and oracle data. This design does not defend against a malicious
controller or compromised host administrator. It does prevent the reviewer
execution interface from receiving controller-only material and makes the
controller's request/output commitments auditable.

## 7. Minimum isolation contract

For every reviewer run, the allowed input set is exactly:

1. one immutable reviewer instruction/brief;
2. one exact immutable review package;
3. one non-normative run envelope;
4. one exact output schema or equivalent structured-output constraint.

The reviewer has exactly one logical output channel: the structured response
returned to the controller. The reviewer has no filesystem write capability;
the controller alone writes the returned bytes to that run's output root. This
is stronger than permitting a reviewer-writable directory.

The runtime contract requires:

- a fresh, stateless request for every context;
- no previous response/conversation identifier;
- no stored memory or retrieval index;
- no tools or connectors;
- no host file paths resolved by the endpoint;
- no sibling or prior run content in the request;
- no oracle bytes or expected label/rationale pair in the request;
- one immutable model/deployment identity for all comparable runs;
- one exact inference-settings identity for all comparable runs;
- controller-side request and response byte commitments;
- fail-closed behavior when any property cannot be evidenced.

The contract is not satisfied by `cwd` separation, read-only write policy,
container naming, a reviewer assertion, a unique prompt, or different run IDs
alone.

## 8. Reviewer/controller trust boundary

The controller may:

- read repository authority and prepare packages;
- validate and hash the package, brief, schema, and run envelope;
- retain the oracle and scoring implementation;
- create unique reviewer/run/context identities;
- invoke the approved external inference endpoint;
- freeze and validate raw output;
- load the oracle only after raw output freeze;
- assemble cohorts, classify disagreements, and calculate the gate;
- preserve evidence and clean task-owned temporary state.

The reviewer may:

- interpret only the request bytes;
- return one schema-constrained response.

The reviewer may not inspect the controller, filesystem, process, environment,
network, other contexts, scoring, oracle, or future prompts. Reviewer output is
evidence, never authority, and cannot modify its package or oracle.

Conceptually:

```text
trusted controller
  ├─ freeze package/brief/envelope/schema identities
  ├─ prove endpoint capability with synthetic canaries
  ├─ send exact tool-free stateless request
  ├─ freeze exact raw response
  ├─ validate response identity/schema
  └─ only then load oracle and score

external reviewer inference
  ├─ sees only the request payload
  ├─ has no tools, retrieval, memory, or host filesystem
  └─ returns one structured response
```

## 9. Input/output identity model

The future runner receipt must commit to at least:

- `runner_contract_version`;
- `backend_kind = STATELESS_TOOLLESS_EXTERNAL_INFERENCE`;
- exact endpoint/deployment and immutable model revision identities;
- inference-settings canonical hash;
- semantic-review contract version;
- package schema/version and package digest;
- reviewer brief/instruction hash;
- output schema hash;
- source action/semantic contract hash;
- source definition digest when present in the package;
- cohort ID and case ID when applicable;
- reviewer ID, review run ID, and context ID;
- sorted permitted input inventory with logical role, byte count, and SHA-256;
- canonical request payload SHA-256;
- capability-preflight evidence SHA-256;
- isolation receipt SHA-256;
- raw response byte count and SHA-256;
- parsed output canonical SHA-256.

The request inventory must equal the contract-defined allowed set. A missing or
extra field/file is a package binding failure. The output must satisfy every
identity field already required by its frozen version-specific schema. The
controller-owned wrapper/receipt binds the exact contract, package, run,
context, and reviewer identities that are not fields of that schema. In
particular, this design does not add run/context fields to the frozen
semantic-review/2.1 output. Output replay against another package or run is
rejected even if the semantic content is identical.

Hashes provide deterministic identity inside the trusted controller boundary;
this design does not add a public-key signing service or secret manager.

## 10. Isolation proof protocol

Isolation has a capability phase and a per-run binding phase.

### 10.1 Synthetic capability phase

Before any real semantic package is submitted, the controller creates a
`THROWAWAY_ISOLATION_PROBE` containing no product or golden semantics.

The controller generates independent high-entropy canaries for:

- allowed package content;
- repository-only content;
- `.git`/history content;
- golden-answer content;
- evaluator-only content;
- sibling package and output content;
- previous-run output content;
- parent/common-temp content;
- environment-only content.

Only the allowed canary is serialized into the reviewer request. Forbidden
canaries remain outside the request boundary. The exact request configuration
must prove that tools, connectors, retrieval, browsing, file attachment by
reference, previous-response continuation, and provider memory are absent. A
random forbidden canary appearing in output is an immediate failure.

The synthetic request also contains inert strings shaped as Windows absolute,
UNC, Unix absolute, parent-traversal, symlink, junction, repository, `.git`,
golden, sibling, and prior-output paths. The endpoint must expose no resolver or
tool capable of dereferencing them. Request/response event logs must contain no
tool-call or retrieval event.

Positive requirements:

- exact allowed payload and brief are readable by the reviewer;
- the allowed canary is returned in the required synthetic schema;
- exactly one response is accepted;
- the controller can freeze that response to the permitted per-run output root.

Negative requirements:

- all forbidden canaries remain absent;
- all forbidden path classes are structurally unreachable;
- no external tool event exists;
- no prior context/session identifier exists;
- no unexpected outbound channel or reviewer-side write exists.

The proof passes only when architecture evidence and observed probe evidence
agree. Reviewer cooperation or silence is not proof.

### 10.2 Per-run phase

Every real run revalidates the approved backend configuration, model/deployment
identity, no-tool request shape, permitted input inventory, unique run/context
identity, package digest, brief hash, output schema hash, and fresh-context
settings. Any drift stops before sending semantic bytes.

After receipt, the controller freezes raw bytes before parsing, verifies the
response identity and schema, and records the isolation receipt hash. Oracle
loading and scoring occur only after those steps.

### 10.3 Proof freshness

The full synthetic capability proof must be rerun whenever the endpoint,
deployment, model revision, inference settings, runner code, request schema,
tool policy, memory/retention policy, or operating environment changes. A
successful proof for one configuration cannot authorize another.

## 11. Approaches considered

| Approach | Isolation strength | Evidence quality | Complexity and dependencies | Portability | Major failures | Gate suitability |
| --- | --- | --- | --- | --- | --- | --- |
| A. Process-only temporary working directory | Low | Low; proves location, not denial | Low; available now | High | Absolute paths, parent paths, repo/worktree, environment, sibling temp, and shared context remain readable | Rejected |
| B. Filesystem/container/OS sandbox | High when correctly configured | High if mounts, namespaces, network, secrets, and canaries are independently verified | High in the current Windows host; needs a functioning engine or sandbox, credential separation, and possibly virtualization/admin changes | Medium | Host mounts, container socket, broad read-only mount, DNS/egress, credential file, symlink/junction, or shared output leakage | Conditional fallback only |
| C. Stateless tool-free external inference request | High for host-data isolation | High when exact request bytes and endpoint capability are recorded and the endpoint has no tools, retrieval, memory, or host mounts | Medium; requires one narrow adapter and provisioned endpoint access | High at the controller contract level | Floating model, hidden tools/retrieval, provider memory, payload limit, retention, or absent immutable deployment identity | Recommended, capability currently unproven |

Approach A is explicitly insufficient. Approach B is valid only after a new
environment demonstrates the boundary; a container label or read-only mount is
not enough. Approach C creates the smallest relevant attack surface because the
reviewer is an inference call rather than a shell-capable agent.

## 12. Recommended architecture

Use Approach C as the primary architecture: one stateless, tool-free external
inference request per reviewer context. Use Approach B only as a separately
approved fallback if a tool-free endpoint cannot be provisioned and the local
or remote sandbox independently passes the same isolation contract.

The implementation should contain one narrow backend adapter, not a plugin
framework. The adapter accepts canonical request bytes and returns raw response
bytes plus provider metadata. It must not accept arbitrary tools, repository
paths, environment passthrough, previous response IDs, or uncommitted content.

Required external endpoint properties:

- an immutable model/deployment identity can be recorded;
- requests are stateless and omit continuation identifiers;
- tools, web, retrieval, code execution, connectors, and file-by-reference are
  absent, not merely discouraged;
- storage/memory is disabled for reviewer state where the endpoint exposes that
  control;
- structured output can express the exact frozen review output schema;
- the historical full package size is accepted without semantic splitting (the
  current v0.4.3 full package is 319,066 bytes across ten files);
- exact request and response commitments can be preserved;
- provider retention/privacy terms are acceptable for the approved package.

If any property is unavailable or only inferred, the backend is not eligible
for real calibration.

The conditional sandbox fallback requires an immutable root filesystem, one
read-only package mount, one controller-owned output channel, no repository or
host filesystem mounts, no host/container-management socket, no shared temp,
no inherited environment, no sibling mounts, and no reviewer-accessible
network. A shell-capable Codex process that needs broad network or host
credentials inside the same sandbox does not satisfy this fallback.

## 13. Runtime capability requirements

The approved implementation environment must provide:

1. one tool-free stateless inference endpoint matching Section 12, or a
   separately approved sandbox fallback;
2. an exact immutable model/deployment identifier;
3. controller-only authentication that is never serialized into reviewer
   input or output;
4. a context/payload limit that admits the exact package bytes;
5. structured-output support or exact raw JSON return;
6. request metadata sufficient to prove no tools/retrieval/continuation;
7. controller access to cryptographic hashing and atomic local evidence freeze;
8. per-run unique IDs and independent output roots;
9. a source repository clean-tree check before and after execution;
10. a full synthetic positive/negative preflight.

The present host does not meet requirement 1. That is an implementation
prerequisite, not a reason to weaken isolation.

## 14. Failure states

The runner/controller state machine is fail-closed:

| State | Meaning | Reliability consequence |
| --- | --- | --- |
| `CALIBRATION_NOT_RUN` | Initial state; no real reviewer request sent | `NOT_MEASURED` |
| `ISOLATION_CAPABILITY_UNAVAILABLE` | No approved backend can provide the required boundary | `NOT_MEASURED`; stop |
| `ISOLATION_PREFLIGHT_FAILED` | Synthetic or per-run positive/negative proof failed | `NOT_MEASURED`; stop before real run |
| `PACKAGE_BINDING_MISMATCH` | Request inventory/digest/version/run binding differs | no score; affected attempt invalid |
| `REVIEWER_EXECUTION_FAILED` | Transport, timeout, provider, or process failure | no score; affected attempt invalid |
| `REVIEW_OUTPUT_INVALID` | Response bytes cannot satisfy exact schema/binding | no score; affected attempt invalid |
| `REVIEW_COMPLETED` | One reviewer output is frozen and valid | no cohort score by itself |
| `CALIBRATION_FAIL` | A complete valid isolated cohort set fails a frozen semantic/statistical gate | reliability not established; apply frozen rubric-revision/rerun policy |
| `CALIBRATION_PASS` | All isolation, identity, output, golden, disagreement, and statistical gates pass | reliability measured only for the exact bound contract/model/runner identities |

Infrastructure failure must not be translated into `INPUT_PACKAGE_ERROR`,
`RUBRIC_ERROR`, `REJECTED_INTERPRETATION`, or any other semantic verdict. No
partial output set may be scored. No automatic same-run retry may reuse a
reviewer context; after a cause fix, any new attempt uses a completely new set
of context/run IDs and follows the frozen full-rerun rule applicable to its
failure class.

## 15. Cleanup guarantees

The controller records the exact pre-state of every task-owned temporary root.
Each run uses a unique input staging root and output staging root. The reviewer
never receives either host path under the recommended external architecture.

On success or failure:

- raw response and controller receipts required as evidence are atomically
  copied to the designated evidence root before cleanup;
- temporary package copies, transient responses, and synthetic canaries are
  removed by exact resolved path, never a broad root or glob;
- deletion is followed by readback proving the task-owned paths are absent;
- the repository status/tree is read back and must be unchanged;
- no sibling run root is removed or reused;
- ambiguous ownership or cleanup failure is reported and stops further runs.

Provider-side retention is not treated as local cleanup. It must be disabled or
accepted explicitly as part of endpoint eligibility and recorded in the
capability evidence.

## 16. Calibration execution boundary

No real calibration starts until all of these gates pass:

1. the runner implementation has its own focused and adversarial tests;
2. the exact backend/model/settings identity is frozen;
3. the full synthetic isolation preflight passes;
4. the exact real reviewer packages, briefs, schemas, and run envelopes are
   frozen before execution;
5. the controller-only oracle predates outputs and is absent from every request;
6. the version-specific calibration authority matches the semantic-review
   contract being measured;
7. an independent read-only audit confirms the above.

For a v0.4.3 `semantic-review/1.0` rerun, the existing repaired controller keeps
its exact three-cohort/48-context protocol and frozen oracle. Such a rerun can
measure only the exact v0.4.3 contract/model/runner binding.

For semantic-review/2.1, the existing contract forbids inherited v1/v2.0
calibration claims. A separate PM-frozen 2.1 calibration authority is required
before execution. At minimum it must bind a 2.1 reviewer brief, 2.1 package and
output identities, a 2.1 normative oracle/golden corpus, the exact existing
2.1 verdict vocabulary and responsibility profile, reliability thresholds,
and a controller that derives scores from frozen raw outputs. Creating or
approving that authority is outside this Phase 0 design write and must not
change product semantics.

Oracle access remains controller-only and occurs after each raw reviewer output
is frozen. A reviewer result can never mutate the oracle. No majority vote,
manual waiver, prompt-only isolation, or cross-version inheritance may satisfy
the gate.

## 17. v0.4.4 re-entry gate

`V0.4.4` remains:

```text
BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION
```

The historical label is preserved, but current M6 authority adds a necessary
identity check: v0.4.3 `semantic-review/1.0` evidence alone cannot establish
semantic-review/2.1 reliability.

Before PM may decide to resume v0.4.4, evidence must show:

1. an approved runner implementation;
2. a successful synthetic isolation capability proof for the exact runtime;
3. an approved, exact semantic-review/2.1 calibration authority or an explicit
   new compatibility decision authorizing a different binding;
4. a complete real calibration using fresh isolated contexts;
5. independently frozen and schema/binding-valid raw outputs;
6. controller-side oracle scoring after output freeze;
7. every applicable reliability gate passing;
8. an independent final audit with no unresolved material finding.

Until then, semantic-review/2.1 reliability remains `NOT_MEASURED` and v0.4.4
does not start.

## 18. Test strategy

Future implementation tests must use synthetic material unless a separately
authorized real calibration task is active.

### 18.1 Isolation tests

- own package and brief readable;
- one valid structured response collectible;
- repository root and `.git` unreadable/unmounted;
- golden truth, evaluator notes, sibling input/output, and prior output absent;
- parent traversal, Windows/Unix absolute paths, UNC paths, symlink, and
  junction escape unable to resolve;
- no environment value except an explicit empty/allowlisted set reaches input;
- no inherited repository cwd or Git metadata;
- no web, shell, Git, browser, connector, retrieval, MCP, or filesystem tool;
- no prior response/conversation state;
- forbidden high-entropy canaries absent from response and event logs.

### 18.2 Identity tests

- wrong package, brief, schema, source-contract, model, settings, run, context,
  reviewer, cohort, or case digest rejected;
- modified package bytes rejected;
- missing/extra inventory entries rejected;
- output replay across run/package/contract versions rejected;
- floating or changed model identity stops before execution.

### 18.3 Execution tests

- malformed, truncated, duplicate, or extra output rejected;
- provider error, timeout, cancellation, and unexpected tool event create no
  score;
- partial reviewer/cohort population cannot satisfy calibration;
- oracle cannot load before raw-output freeze;
- infrastructure errors cannot become semantic verdicts;
- one failed context cannot be silently retried or substituted.

### 18.4 Cleanup tests

- task-owned temporary roots removed and read back absent;
- evidence required for diagnosis preserved before cleanup;
- sibling roots and outputs remain isolated;
- no output from an earlier run appears in a later request;
- repository tree and status remain unchanged;
- cleanup ambiguity blocks additional execution.

## 19. Negative and adversarial isolation tests

The future test suite must include at least:

1. an absolute repository path embedded in synthetic input;
2. `.git/HEAD`, worktree metadata, and parent-repository path probes;
3. `../`, encoded traversal, symlink, junction, and UNC probes;
4. a sibling package containing a withheld random nonce;
5. a prior output containing a withheld random nonce;
6. a golden/evaluator-only file containing a withheld random nonce;
7. an environment-only withheld random nonce;
8. an inert prompt-injection string asking for shell, Git, web, connector, or
   filesystem access;
9. a forged response that reuses another run/package identity;
10. a provider event stream containing any tool/retrieval event;
11. a request containing a previous-response or conversation identifier;
12. a request whose model/deployment identity changed after preflight;
13. an over-limit package that would otherwise invite silent semantic
    truncation or splitting;
14. a cleanup failure leaving a prior output where a later run could receive it.

Every case fails closed. Absence of a voluntarily attempted read is never used
as the sole proof.

## 20. Migration and compatibility impact

The runner is orchestration/evidence infrastructure. It consumes exact existing
packages and emits bytes for exact existing output validators. It does not
change:

- Product Definition state `0.2.0`, coverage, Closure, approval, or manifests;
- action-conformance/2.1 or runtime-conformance semantics;
- semantic-review/1.0 or semantic-review/2.1 schema/verdict semantics;
- the frozen v0.4.3 oracle, golden pairs, thresholds, responsibility rules,
  negative regressions, attempts, or disposition;
- existing M6 dogfood outputs.

The new receipt and isolation evidence are controller-side calibration
metadata, not fields added to a Product Definition, action contract, semantic
review output, or runtime report. Version-specific adapters may translate the
controller's immutable run identity into fields already required by a frozen
review schema, but may not translate verdict meanings or claim cross-version
reliability.

## 21. Security and privacy considerations

- Authentication remains controller-only and is excluded from request,
  response, logs, receipts, and reviewer-visible environment.
- Packages may contain proprietary product semantics. Endpoint retention,
  training-use, region, and access-control terms must be accepted before the
  backend is eligible.
- Raw requests/responses and evidence are stored only in explicitly approved
  evidence locations; logs redact credentials but do not rewrite semantic
  output.
- Hashes detect drift but do not make sensitive plaintext safe to publish.
- The controller must avoid sending local absolute paths, usernames, unrelated
  environment values, repository history, or evaluator notes.
- Model/provider drift invalidates the capability proof and comparable-run
  identity even when package bytes are unchanged.
- No endpoint availability or convenience permits fallback to a shell-capable,
  prompt-restricted reviewer.

## 22. Open questions and resolved prerequisites

No architectural choice remains open in this candidate: the selected primary
boundary is a stateless tool-free external inference endpoint, with a sandbox
as a conditional separately proven fallback.

The following are unresolved capabilities, not design omissions:

- no eligible external tool-free endpoint adapter is currently present or
  proven in this repository/runtime;
- no local sandbox/container capability currently passes the isolation
  contract;
- no PM-frozen semantic-review/2.1 calibration authority currently exists, and
  the frozen 2.1 contract forbids inheriting v1/v2.0 calibration claims.

These conditions must be satisfied in later, explicitly authorized work. The
implementation plan must not be written until this design is approved. The
real calibration task must not begin until both runtime isolation and exact
2.1 calibration authority are approved and proven.

## 23. Future implementation decomposition

To keep subsequent work bounded, a future implementation plan should separate:

1. runner receipt/identity and tool-free endpoint adapter;
2. synthetic capability and adversarial preflight;
3. controller integration and fail-closed evidence lifecycle;
4. independent implementation/capability audit;
5. separately approved semantic-review/2.1 calibration-authority preparation;
6. separately authorized real calibration execution and scoring.

Units 5 and 6 must not be hidden inside runner implementation. A passed runner
preflight is not a reliability result.

## 24. Design self-review criteria

Before this design is considered ready for PM review, verify:

- every required section is present and no unresolved marker remains;
- the threat model and selected architecture agree;
- no isolation claim depends on reviewer instructions alone;
- no path exposes oracle or prior/sibling results;
- no path relies on repository cwd or shared agent context;
- no real calibration precedes a successful capability proof;
- v0.4.3/1.0 evidence is not inherited by semantic-review/2.1;
- Product Definition and downstream/runtime semantics remain unchanged;
- v0.4.4 remains blocked;
- the scope can be implemented through the bounded units above.

## 25. Self-review result

Verdict: `PASS`

Material findings: `0`

| Check | Result |
| --- | --- |
| Required design and audit scope is complete | `PASS` |
| No unresolved marker or unexplained open architecture choice | `PASS` |
| Threat model and selected tool-free boundary agree | `PASS` |
| Isolation does not depend on reviewer instructions | `PASS` |
| Oracle, prior output, and sibling material remain controller-only | `PASS` |
| No repository-cwd or shared-context dependency | `PASS` |
| Positive and negative capability proof precedes real calibration | `PASS` |
| v0.4.3/1.0 reliability is not inherited by 2.1 | `PASS` |
| Product Definition, downstream, runtime, and verdict semantics unchanged | `PASS` |
| v0.4.4 remains blocked | `PASS` |
| Implementation scope is bounded and no implementation plan is included | `PASS` |
