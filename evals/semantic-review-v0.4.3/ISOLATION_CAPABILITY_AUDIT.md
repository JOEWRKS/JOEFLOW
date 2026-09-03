# Semantic Review Isolation Capability Audit

Date: 2026-09-03

Audit kind: architecture-time capability inspection only

Result:

```text
CURRENT_RUNTIME_ISOLATION = UNAVAILABLE
REAL_CALIBRATION = NOT_RUN
semantic-review/2.1 reliability = NOT_MEASURED
```

This audit did not execute a semantic reviewer, a golden case, C1/C2/C3, or a
reliability score. It did not modify the v0.4.3 oracle, corpus, controller,
semantic-review implementation, Product Definition, or M6 evidence.

## 1. Authority and scope

Repository authority inspected at:

```text
main commit: cdc0eb4a972020666f73f7d267a70a1972675054
main tree:   6e28df29454a5b7475556a672ed9a2b33207736b
```

Current approved Product Definition identity:

```text
schema:                   0.2.0
revision:                 2
status:                   CLOSED
approval:                 APPROVED
definition digest:        81d3b7ff59dbce321dc27fab6b51f03db4201dc1f4a1ea3d6b202f3f76afddcf
Approval Manifest digest: 079ef1bb60ccc382a66c6c764519e67e606744a9d10425310cc1b868be490003
```

Historical reliability disposition remains:

```text
Run-01:                         INVALID / CONTROL_PLANE_DEFECT
Run-02 semantic execution:     NOT_STARTED
REAL_CALIBRATION_ATTEMPTS:     1
VALID_REAL_CALIBRATION_RUNS:   0
real reviewer reliability:    NOT_MEASURED
```

## 2. Classification vocabulary

- `OBSERVED`: directly read or executed in this Phase 0, or read from exact
  committed historical capability evidence.
- `INFERRED`: a conclusion derived from observed facts, clearly marked as such.
- `UNAVAILABLE`: the capability was absent, disabled, or failed its available
  invocation on this host.
- `UNTESTED`: the theoretical capability was not present or was not safely
  executable, so no support claim is made.

## 3. Current host and tool inventory

| Capability | Classification | Evidence | Consequence |
| --- | --- | --- | --- |
| OS | `OBSERVED` | Windows 10 Pro, build 19045, 64-bit | Windows-specific local isolation constraints apply |
| Hypervisor | `OBSERVED` / `UNAVAILABLE` | `HyperVisorPresent = False` | no active hypervisor boundary |
| Firmware virtualization | `OBSERVED` / `UNAVAILABLE` | `systeminfo`: `Virtualization Enabled In Firmware: No` | VM-backed local isolation cannot run as currently configured |
| Docker CLI | `UNAVAILABLE` | `where.exe docker.exe` found no executable | no Docker container runner |
| Podman CLI | `UNAVAILABLE` | `where.exe podman.exe` found no executable | no Podman container runner |
| nerdctl CLI | `UNAVAILABLE` | `where.exe nerdctl.exe` found no executable | no containerd CLI runner |
| WSL executable | `OBSERVED` | `C:\Windows\System32\wsl.exe` exists | executable presence alone is not a usable distro/boundary |
| WSL feature | `UNAVAILABLE` | `Win32_OptionalFeature.InstallState = 2` | feature disabled |
| VirtualMachinePlatform | `UNAVAILABLE` | `InstallState = 2` | feature disabled |
| Hyper-V | `UNAVAILABLE` | `InstallState = 2` | feature disabled |
| Windows Containers | `UNAVAILABLE` | `InstallState = 2` | feature disabled |
| Windows Sandbox | `UNAVAILABLE` | `Containers-DisposableClientVM InstallState = 2` | feature disabled |
| Hyper-V management commands/services | `UNAVAILABLE` | no relevant command/service returned | no usable current VM control path |
| Codex CLI | `OBSERVED` | `codex-cli 0.146.0` | local CLI exists, but existence is not isolation |
| Current Codex task filesystem | `OBSERVED` | current permission profile exposes the repository and other workspace roots | current task cannot attest package-only visibility |
| Collaboration agents | `OBSERVED` | runtime contract states agents share the same repository filesystem | not eligible reviewer isolation |
| External tool-free reviewer adapter | `UNAVAILABLE` | no such repository adapter or configured runtime was found | recommended architecture cannot run yet |
| External endpoint behavior | `UNTESTED` | no endpoint was selected or invoked | no package-only support claim |

`InstallState = 2` is recorded as the observed disabled state returned by
`Win32_OptionalFeature`. The elevation-required `Get-WindowsOptionalFeature`
query was not used to upgrade an unavailable result into a support claim.

## 4. Historical manifest-only capability evidence

Committed evidence:

```text
evals/semantic-review-v0.4.3/evidence/calibration-disposition/
  MANIFEST_ONLY_ISOLATION_CAPABILITY_EVIDENCE.json
  V043_CALIBRATION_ENVIRONMENT_BLOCKED_DISPOSITION.md
```

The historical ephemeral Codex capability probe ran from
`C:\Users\tjdwo\AppData\Local\Temp` in declared `read-only` mode. It could
enumerate the forbidden Run-01 path:

```text
D:\JOEWRKS\JOEWRKS-Product-v043-calibration-run-01\
  evals\semantic-review-v0.4.3\calibration\run-01
```

Observed result:

```text
RUN01_READABLE = YES
result = BLOCKED — MANIFEST_ONLY_ISOLATION_UNAVAILABLE
reviewer contexts spawned = 0
semantic outputs produced = 0
```

This is `OBSERVED` historical evidence that a dedicated working directory and
read-only write policy did not deny absolute-path reads.

## 5. Current Phase 0 restricted-token probe

The only current execution probe was capability-only and is classified:

```text
THROWAWAY_ISOLATION_PROBE
semantic content: none
reviewer context: none
semantic output: none
```

Invocation:

```text
codex sandbox -- powershell.exe -NoLogo -NoProfile -NonInteractive
  -Command "whoami; Test-Path -LiteralPath
  'D:\JOEWRKS\JOEWRKS-Product\.git'"
```

Observed fresh result:

```text
exit code: 1
windows sandbox failed: CreateProcessWithLogonW failed: 2
```

The child command did not start, so this probe proves current unavailability,
not successful denial of the repository. The same mechanism was not retried.
No canary file or persistent sandbox state was created.

## 6. Codex execution surfaces

| Surface | Classification | Evidence | Isolation assessment |
| --- | --- | --- | --- |
| `codex exec -C <temp> --ephemeral --sandbox read-only` family | `OBSERVED` historically unsafe | historical `RUN01_READABLE = YES` | insufficient |
| Codex Windows restricted-token sandbox | `UNAVAILABLE` | current invocation failed before child start | cannot be used now |
| Codex Desktop collaboration agent | `OBSERVED` shared | shared repository filesystem is part of runtime contract | insufficient |
| `codex cloud exec` | `OBSERVED` interface, package-only behavior `UNTESTED` | CLI requires an environment ID and accepts a Git branch | no package-only claim; repository-oriented surface is not selected |
| Codex output-schema option | `OBSERVED` | CLI exposes structured output | output shape does not remove shell/filesystem capabilities |

Changing the prompt, current directory, run ID, or output schema would not
repair the observed filesystem boundary.

## 7. Repository/runtime evidence identity

The frozen v0.4.3 full reviewer package currently occupies 319,066 bytes across
ten files including `manifest.json`. Its manifest declares nine files totaling
316,743 bytes. Readback identities:

```text
full reviewer package hash:
  ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603

reviewer brief hash:
  3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c

responsibility profile hash:
  f8010b9410bfb786cc3107e78a001e226bf30ce6cf8aafcfca303851dce56fc5

normative oracle file SHA-256:
  4126bb8d316291d8362f04fe1160f53ad86adc73ec358effad7a84d104d7a173
```

The package size is an observed input to future endpoint capability testing. It
does not prove any endpoint can admit it.

The current Revision-2 M6 dogfood output remains:

```text
action-conformance:             2.1
actions/lifecycles:             6 / 0
review-required fields:         0
semantic review package/output: NOT_REQUIRED
runtime coverage:               COMPLETE
runtime status:                 CONFORMANT
implementation status:          IMPLEMENTATION_CONFORMANT
semantic-review/2.1 reliability: NOT_MEASURED
```

## 8. Compatibility observation

This is an `OBSERVED` contract fact:

- v0.4.3 calibrates `joewrks.semantic-review/1.0` over
  `joewrks.action-conformance/1.0`;
- current M6 uses `joewrks.semantic-review/2.1` over
  `joewrks.action-conformance/2.1`;
- the 2.1 contract states that 2.0 and 2.1 package/output identities are
  mutually invalid and that v1/v2.0 reliability/calibration identity is not
  imported or inferred;
- 1.0 and 2.1 use different package identities, responsibility boundaries,
  output shapes, and verdict vocabularies.

Therefore it is `INFERRED` with direct contract support that an isolated PASS
of the unchanged v0.4.3 corpus would not alone measure semantic-review/2.1.
A separately frozen 2.1 calibration authority or an explicit new compatibility
decision is required before 2.1 reliability can change from `NOT_MEASURED`.

## 9. Approach capability conclusions

### 9.1 Process-only working directory

Classification: `OBSERVED` available, `OBSERVED` insufficient.

It is inexpensive and portable, but historical evidence proves it does not
deny absolute-path repository access. It cannot satisfy the reliability gate.

### 9.2 Local filesystem/container sandbox

Classification: `UNAVAILABLE` now; correctly provisioned behavior `UNTESTED`.

No current container engine, VM platform, WSL distribution, Hyper-V, or Windows
Sandbox boundary is usable. A future provisioned environment might satisfy the
contract, but would need fresh positive/negative proof including mounts,
network, credentials, temp, symlink/junction, and sibling isolation. No such
support is claimed here.

### 9.3 External package-only execution boundary

Classification: selected design, implementation `UNAVAILABLE`, endpoint
capability `UNTESTED`.

No current adapter was found that sends only serialized package bytes to a
stateless inference endpoint with tools, retrieval, memory, connectors, and
host files absent. Codex Cloud's repository/environment-oriented interface is
not proof of this property. This approach remains the recommendation because it
has the smallest required reviewer capability surface once provisioned and
proven.

## 10. Required future capability proof

Before real reviewer execution, a future audit must change every required item
below from `UNTESTED`/`UNAVAILABLE` to `OBSERVED PASS` for one exact immutable
runtime configuration:

- stateless fresh request and unique context identity;
- exact own package, brief, envelope, and schema readable;
- exact response channel usable;
- repository root/parent and `.git` unreachable;
- worktrees and Run-01 evidence unreachable;
- golden answers, expected labels, oracle, scoring truth, and evaluator notes
  unreachable;
- sibling packages/outputs and prior outputs unreachable;
- absolute, parent, UNC, symlink, junction, and common-temp escape unavailable;
- no inherited environment, cwd, Git metadata, or conversation state;
- no shell, filesystem, Git, web, browser, connector, MCP, retrieval, code
  execution, or remote-storage tool;
- exact immutable model/deployment/settings identity recorded;
- exact request and response commitments recorded;
- controller-only oracle load occurs after raw output freeze;
- cleanup and source repository no-change readback pass.

The future proof must use synthetic non-semantic canaries before any real
calibration context. An architecture description, tool name, reviewer promise,
or absence of a voluntary access attempt is insufficient.

## 11. Current disposition

The current runtime cannot truthfully attest the minimum isolation contract.
The correct outcome is:

```text
ISOLATION_CAPABILITY_UNAVAILABLE
CALIBRATION_NOT_RUN
semantic-review/2.1 reliability = NOT_MEASURED
v0.4.4 = BLOCKED
```

No semantic or rubric defect is established by this capability result. No
existing attempt/run counter changes. A later implementation task may begin
only after PM approval of the accompanying design. Real calibration requires a
separate explicit authorization after runner implementation, capability proof,
and exact semantic-review/2.1 calibration authority are all ready.
