# Figma and Figma Make Handoff

When Figma is available, generate editable low-fi frames from screen and flow specifications. Recommended pages: `00_PRODUCT_MAP`, `01_USER_FLOWS`, `02_WIREFRAMES`, `03_SCREEN_STATES`, `99_HANDOFF`. Name frames `SCR-001__LOGIN` and variants `SCR-001__DEFAULT`, `SCR-001__ERROR`; preserve IDs exactly.

Do not invent brand style, decorative imagery, color identity, complex animation, or high-fidelity styling before the user decides them. Low-fi work validates hierarchy, layout, content, interaction, navigation, state, and flow.

Without Figma, produce Markdown wireframes, Mermaid flows, screen specifications, build instructions, and `FIGMA_MAKE_HANDOFF.md`; record `Figma visualization: NOT VERIFIED`.

After Figma Make output, create `MAKE_REVIEW.md` covering missing/extra screens and flows, invented branches, missing states, rule/permission/data/navigation drift, scope expansion, and acceptance violations. Link each drift to expected IDs and severity.

## Executable downstream conformance

After Product Definition Closure, implementation handoff may bundle a derived executable contract by following [`downstream/README.md`](../downstream/README.md). Canonical Product Definition remains authority; the action/lifecycle bundle is a read-only, provenance-pinned projection and does not change Closure or `state.json`.

Keep the human-readable handoff. Add the compiled action contract path, lifecycle contract path, exact contract SHA-256, adapter identity/version, frozen source commit/tree, and sequence-runner command. Runtime evidence uses `joewrks.downstream.execution/1.0`; generator adapters only invoke/read back the implementation, while the Python core determines semantic conformance.

After implementation, use the downstream blind-audit procedure. Trace every material action from precondition through public action, handler, domain state, provenance/side effects, and visible result or recovery. A rendered label, handler existence, helper test, build result, visual similarity, implementation self-report, or green test count is not transition evidence.

