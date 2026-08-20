# Figma and Figma Make Handoff

When Figma is available, generate editable low-fi frames from screen and flow specifications. Recommended pages: `00_PRODUCT_MAP`, `01_USER_FLOWS`, `02_WIREFRAMES`, `03_SCREEN_STATES`, `99_HANDOFF`. Name frames `SCR-001__LOGIN` and variants `SCR-001__DEFAULT`, `SCR-001__ERROR`; preserve IDs exactly.

Do not invent brand style, decorative imagery, color identity, complex animation, or high-fidelity styling before the user decides them. Low-fi work validates hierarchy, layout, content, interaction, navigation, state, and flow.

Without Figma, produce Markdown wireframes, Mermaid flows, screen specifications, build instructions, and `FIGMA_MAKE_HANDOFF.md`; record `Figma visualization: NOT VERIFIED`.

After Figma Make output, create `MAKE_REVIEW.md` covering missing/extra screens and flows, invented branches, missing states, rule/permission/data/navigation drift, scope expansion, and acceptance violations. Link each drift to expected IDs and severity.

