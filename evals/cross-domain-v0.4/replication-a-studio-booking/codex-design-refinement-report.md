# Codex Design Refinement Report — Replication A

## Authority and scope

- Canonical revision: 62 (`CLOSED`)
- Approved digest: `8ebb472aa66a5b680961e102db950214cea2d0be3b644164f23712030b9d8a7c`
- Figma file: `fClM2GgNhwEDIiqZcIWhNZ`
- Audited implementation root: `4:2`
- Audited mobile root: `4:656`
- Open Design: `UNAVAILABLE_IN_CURRENT_RUNTIME`
- Open Design evidence: `codex mcp get open-design --json` returned `No MCP server named 'open-design' found.` No installation or substitute tool was attempted.
- Product Definition, state, projections, Closure, and Figma were not changed by this refinement.

## Fresh Figma readback

`get_design_context` was invoked on `4:2`, then on bounded subtrees `4:5`, `4:202`, and `4:656` using the Figma design-to-code workflow. The root exposes the expected 27 separate `SCR-*` screen frames and the mobile root exposes Customer, Staff, and Owner 360px journeys. The bounded code readback confirms the visual grammar: white surfaces, `#D1D5DB` borders, `#111827` primary actions, pale-red recovery panels, role labels, grouped fields/actions/recovery/navigation, and Inter-like compact system typography.

The generated React/Tailwind reference was treated only as design context. The target has no existing frontend stack, so the implementation contract chooses dependency-free semantic HTML, CSS tokens, and ES modules. No Tailwind or other dependency may be installed.

## Bounded refinement decisions

The low-fi is structurally authoritative but intentionally schematic. The implementation refines presentation without changing semantics:

- use system UI typography with large-heading negative tracking only and readable 1.5 body leading;
- use a calm neutral surface system with accessible blue primary, green success, amber warning, and red destructive/recovery tokens;
- keep 4/8px spacing rhythm and increase touch targets to at least 44px;
- make role and state visibly redundant through text plus color, never color alone;
- preserve recovery next to the action/field that caused it;
- use a role-oriented compact side rail on wide screens and a wrapping/top navigation on small screens;
- show the common action first and disclose advanced operational controls within the selected screen;
- use 150–250ms opacity/transform feedback, visible `:focus-visible`, and a no-motion equivalent under `prefers-reduced-motion`;
- use native semantic controls and text labels; no emoji or guessed visual assets.

## UI/UX Pro Max evidence

The installed local design database was queried first with `creative studio booking scheduling operations calm trustworthy responsive dashboard` and then with UX validation and `html-tailwind` stack queries. It returned a photography-studio/operations pattern, a neutral data-dense layout, semantic status colors, 4/8px spacing, visible focus, loading/submit feedback, and managed z-index guidance. The recommended bright gradient, glass effects, floating action button, decorative pulse, Lora/Raleway font pairing, and landing-page conversion sections were rejected because they conflict with the audited operational low-fi, dependency-free boundary, and restrained product authority.

## Selective Apple design guidance

Apple guidance was used only for principles compatible with the approved product: immediate press feedback, predictable wayfinding, spatially consistent open/close behavior, system-font legibility, restraint, reduced motion/transparency, and reversible user control. Gesture physics, momentum projection, glass stacking, haptics, sound, and expressive spring choreography were not adopted because this prototype has no canonical gesture-driven interaction.

## Implementation-ready visual rules

- Primary text and controls must meet WCAG-oriented contrast; focus must remain visible in every theme used.
- Content widths use fluid grids; 320–375px reflow must not create page-level horizontal scrolling.
- Sticky navigation cannot cover scroll content. Dialogs require labeled headings, focus restoration, Escape close when safe, and explicit confirmation for destructive actions.
- Loading, success, warning, error, stale, expired, denied, and recovery states must be textually named in a live-status region.
- Role surfaces remain visually distinct but share one token system. Owner-only actions cannot merely be hidden; denied navigation/action must produce an auditable prototype response.
- Dark mode is not added because neither canonical Figma nor approved product requires it; adding an unverified theme would broaden design scope. High contrast and reduced motion are supported.

## Result

Design refinement is ready for implementation. It changed presentation guidance only and introduced no product behavior. Figma remains the visual authority; `CODEX_IMPLEMENTATION_HANDOFF.md` binds the approved semantic and visual boundary for the implementation agent.
