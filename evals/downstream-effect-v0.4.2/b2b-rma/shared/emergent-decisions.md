# Emergent evaluator decisions

The controller made a consistent evaluator decision only when the Product Agent explicitly requested a material dimension not fixed by the hidden bank. The resulting answer was recorded through the normal unknown/decision/rule chain and approved as part of revision 78.

Material emergent categories included:

- one original order per case while allowing multiple lines, partial quantities, and mixed outcomes;
- product-master authority and case-time snapshotting for traceability mode;
- trim-only serial and lot normalization, organization-wide serial uniqueness, and audited correction;
- contract-over-SKU eligibility precedence with exception review when both are absent;
- reason-based inbound shipping responsibility and tracking requirements;
- detailed inspection axes and reason-specific evidence requirements;
- supplier-controlled RETURN_TO_CUSTOMER logistics with customer-paid collect-on-delivery handling;
- NO_CREDIT quarantine, notice, dispute, fee, settlement-exception, restricted-item, incident, and disposal-recovery policy;
- deterministic local fixture/simulation boundaries for external systems;
- per-allocation and partial-quantity commit boundaries, cleanup holds, and linked post-commit corrections;
- server-checkpoint/current-tab recovery without durable offline storage;
- operational workspace information architecture, authentication simulation, accessibility, service recovery, performance, dashboard, and export constraints;
- detailed confirmation/no-undo contracts for destructive and irreversible actions;
- case-completion and linked-correction compensation lineage.

No emergent evaluator decision was added outside a Product Agent-requested dimension. Exact decisions, reasons, sources, dependencies, and affected stable IDs are authoritative in `product-definition/b2b-rma-dogfood/state.json` and projected in `DECISION_LEDGER.md`.

