# Downstream 2.1 package boundary

This package implements the semantic and runtime-planning boundary identified by:

- `ACTION_CONFORMANCE_2_1`
- `HANDOFF_DEFINITION_2_1`
- `RUNTIME_CONFORMANCE_PLAN_1_0`
- `RUNTIME_EVIDENCE_BUNDLE_1_0`

Runtime evidence remains an external, deterministic envelope over exact parsed `joewrks.downstream.execution/1.0` records. Every record is validated by the frozen transport validator before 2.1 admission. The envelope binds the semantic contract hash, runtime plan hash, approved definition digest, product slug, approved revision, and the plan's unique test IDs without adding fields to an execution record.

The runtime evidence inventory reports sorted required, observed, missing, and unexpected test IDs. It reports coverage only; it does not interpret a runtime result as semantic PASS or FAIL.

Boundary and status markers:

- `SEMANTIC_REVIEW_2_1_RELIABILITY_NOT_MEASURED`
- `SEMANTIC_AUTHORITY_GAP_REENTERS_PRODUCT_DEFINITION`
- `CONTRACT_EXPRESSIVENESS_GAP_DOES_NOT_REENTER_PRODUCT_DEFINITION`
- `RUNTIME_MAPPING_GAP_DOES_NOT_REENTER_PRODUCT_DEFINITION`
- `DOWNSTREAM_V2_0_FROZEN`
- `M6_NOT_COMPLETED_BY_M5_1`

The package does not read Product Definition authority to invent runtime behavior. It consumes validated 2.1 semantic contracts and runtime plans, and it does not provide templates, callbacks, executable expressions, `eval`, or natural-language parsing.
