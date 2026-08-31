# Continuation Task A report — frozen-boundary relocation and installed 2.1 routing

## Outcome

The M6 runtime verifier, report module, and report schema now live in
`skills/joewrks-product-definition/integration_v2/`, outside the frozen
`downstream_v2/` and `downstream_v21/` package trees. Installed compile, audit,
and conditional semantic-review wrappers now route the current State `0.2.0`
workflow through the frozen 2.1 implementations. The M6 runtime wrapper imports
the relocated verifier/report modules while retaining the 2.0 runtime contract
adapter it is designed to verify.

The sole Task A commit is `refactor: route M6 integration through downstream 2.1`.
This report is included with that bounded commit; obtain its exact SHA with
`git rev-parse HEAD` after checkout.

## Exact files changed

- Added `skills/joewrks-product-definition/integration_v2/__init__.py` and
  `installed_workflow.py`.
- Relocated, without behavior changes except the required contract-module import
  rebasing, `runtime.py`, `runtime_report.py`, and
  `schemas/runtime-conformance-report.schema.json` from `downstream_v2/` to
  `integration_v2/`.
- Redirected the installed compile, audit, review, and runtime wrappers.
- Updated `SKILL.md`, `references/workflow-v0.2.0.md`, `README.md`, and
  `PROGRAM_ARCHITECTURE.md` to name the current
  `joewrks.handoff-definition/2.1`, `joewrks.action-conformance/2.1`, and
  conditional `joewrks.semantic-review/2.1` route, with
  `NOT_MEASURED` reliability. The workflow also names
  `joewrks.runtime-conformance-plan/1.0`, frozen
  `joewrks.downstream.execution/1.0`,
  `joewrks.runtime-evidence-bundle/1.0`, and the M6
  `joewrks.runtime-conformance-report/1.0`.
- Updated the relocated-runtime and installed-workflow tests to import the new
  namespace and assert the current routing identities.

## RED → GREEN evidence

1. The pre-change installed-routing contract test ran 5 tests and failed on the
   missing current 2.1 authority and semantic-review markers (2 failures).
2. The amended routing test ran 5 tests and failed as expected on the missing
   2.1 workflow identities (9 failures total, including the two documentation
   markers).
3. After the smallest routing/documentation changes,
   `python -m unittest tests.test_v2_installed_workflow -v` passed all 13 tests.
   These include compile, audit, review, and runtime wrappers invoked from an
   external consumer CWD with `PYTHONPATH` cleared.
4. The first relocated-runtime run exposed the still-old test schema location;
   the test was updated to use `integration_v2/schemas/`. The relocation-focused
   runtime/report tests then passed. The frozen-tree test was intentionally run
   again after committing because it validates `HEAD`, not an uncommitted tree.
5. The current 2.1 compiler/audit/review/runtime-plan/runtime-evidence focused
   suite passed: 80 tests.
6. Post-commit, the relocated-runtime/report, frozen-boundary, and installed
   workflow suite passed: 71 tests. `git diff --check` passed and the worktree
   was clean.

## Boundary verification

At the committed Task A boundary, the required tree identities are:

```text
skills/joewrks-product-definition/downstream_v2
= 33fb2653531fa85dcc8fd8c94cbbb7cc5c41d41e
skills/joewrks-product-definition/downstream_v21
= d4f396103e44673cdbb10606b998304575aaaa4c
skills/joewrks-product-definition/downstream
= b63568d8c4632b14bc806e7bff1908e94dea9669
evals/semantic-review-v0.4.3
= a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
```

The retained historical Phase-B artifacts were read-only checked by SHA-256:

```text
dogfood product-definition state.json
= 728744301bc0ea2a1766852b7b46bab3c610215b31f63c0a784dd804fa3ce49d
dogfood approval-manifest.json
= f354e7baf1001bf1cd2a763569b310947ca2fd1ae4e6eb57c6f1573d9ec2eef1
dogfood handoff-definition.json
= 11fdce0fdce90d8c2f5e069cd766aa338e5f4efd7653d38e2d152509653fbaef
dogfood reentry-probe.json
= b6e0b4960211456a6dacf521a407667c0b838b5b1dee50db9ab02f2b9534e211
```

## Scope and concerns

- No dogfood compilation, runtime-plan materialization, runtime-evidence
  creation, Task 6 work, push, PR, or merge was performed.
- `semantic-review/2.1` reliability remains `NOT_MEASURED`.
- The M6 runtime verifier/report continues to verify its frozen 2.0 runtime
  contract shape; it was relocated for frozen-tree safety, not redesigned to
  reinterpret 2.1 runtime-plan or evidence-bundle semantics. Task B owns the
  approved-dogfood 2.1 runtime lineage.
