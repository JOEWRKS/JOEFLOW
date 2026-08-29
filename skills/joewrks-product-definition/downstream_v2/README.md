# Downstream V2 — M5 authority boundary

This package is the read-only M5 boundary for compiling an M4-closed Product Definition into `joewrks.action-conformance/2.0`, auditing an existing contract's declared dependencies, proposing Product Definition re-entry, and building structural `joewrks.semantic-review/2.0` input packages.

It is deliberately non-integrated. Use both package roots for each invocation; do not install the package or change persistent environment configuration. On Windows PowerShell:

```powershell
$env:PYTHONPATH = "<skill-root>;<skill-root>/scripts"
```

On platforms that use `:` as the path separator:

```sh
PYTHONPATH="<skill-root>:<skill-root>/scripts"
```

Here, `<skill-root>` is `skills/joewrks-product-definition`.

## Read-only commands

Compile only from a Product Definition whose actual M4 state is CLOSED:

```text
python -m downstream_v2.compile STATE_JSON HANDOFF_DEFINITION_JSON
```

Exit `0` materializes a contract. Exit `1` reports a non-closed definition, invalid semantic input, or semantic authority gaps and re-entry. Exit `2` reports usage, read, or JSON errors. Every expected result is one canonical JSON document on stdout with empty stderr.

Audit an existing contract against only the dependencies it committed:

```text
python -m downstream_v2.audit CONTRACT_JSON STATE_JSON
```

Exit `0` means `CONFORMANT`. Exit `1` means `DEFINITION_NOT_READY`, `REENTRY_REQUIRED`, or invalid contract. Exit `2` means a usage, read, or JSON error. This audit does not require the current whole Product Definition to remain CLOSED; it does require a safely inspectable state and exact local dependencies.

Build a review-only structural package:

```text
python -m downstream_v2.semantic_review.build_package CONTRACT_JSON
```

Exit `0` returns either `review_required: false` with `package: null`, or `review_required: true` with a deterministic `joewrks.semantic-review/2.0` package. Invalid contracts exit `1`; usage, read, and JSON errors exit `2`.

All three commands read their inputs without modifying them. They do not write Product Definition state, contracts, handoff definitions, re-entry state, runtime state, or environment configuration.

## M5 limit

M5 establishes downstream V2 authority, semantic-debt classification, read-only re-entry proposals, and the structural semantic-review/2.0 boundary. Reliability remains `NOT_MEASURED`. Installed routing, implementation/runtime verification, deployment, calibration, production adoption, and representative product dogfood belong to M6 or later work.

See `../references/downstream-v2-contract.md` and `../references/implementation-reentry-contract.md` for the normative contracts.
