# JOEFLOW Product-to-visual handoff delta validation

Date: 2026-10-08 KST
Verdict: PASS for the narrow exact-installed-base patch

## Scope

This record validates a two-file documentation delta against the exact current
installed `joewrks-product-definition` baseline. It does not synchronize the
older repository skill source and does not claim automatic inclusion in a
general repository installation path.

The delta clarifies:

- Product information priority and required exposure versus visual
  implementation responsibility;
- binding Product values versus approved visual-authority values versus
  proposed/DRAFT visual starting points;
- the exact source identity and affected scope actually consumed;
- Product conformance, visual conformance, and user visual acceptance as
  separate verdicts; and
- reuse of existing acceptance/review material without a new schema, enum,
  mandatory document, table, agent, or token system.

## Patch and installed identity

Patch:

`docs/superpowers/specs/2026-10-08-joeflow-product-visual-handoff-installed-delta.patch`

Patch SHA-256:

`f41764b51e80d114cbc3a9bdc39512550cce2720edc606d3dfd7b708642b3498`

| File relative to installed skill root | Required base SHA-256 | Expected installed SHA-256 |
| --- | --- | --- |
| `references/figma-make-handoff.md` | `4e379ae6ce575eb61ad519827412a7ebfb1aa593864ce6b364bd121e399aff7a` | `1269ef1e462ab86413c1e2d7df13bd4e8325eedf529c167946c60574f65e83e3` |
| `templates/figma-make-handoff.md` | `f27c31b594e988bd23520feab3933db548e9dbbcc15ad991dce8bd3761108ab7` | `2cc1d92ae88322198bab96a1bbe1b75d8287b44748e7c17dd068106d2f932361` |

The pre-install bytes are preserved outside Git at:

`C:/Users/tjdwo/.codex/skills/.backups/joewrks-product-definition/20261008-joeflow-visual-handoff-preinstall/`

For byte-reproducible Windows application, verify the two required base hashes
and run from the target skill root:

```text
git -c core.autocrlf=false apply --unidiff-zero <path-to-patch>
```

## Verification performed

- Clean replay from the two saved base files reproduced both expected installed
  SHA-256 values.
- `skill-creator/scripts/quick_validate.py` returned `Skill is valid!` for the
  installed skill and the replayed copy.
- Ten scoped semantic guards passed: one reference section; exact approved
  Product-value protection; consumed-source recording; no new schema/enum;
  three template placeholders; verdict separation; existing V2 Manifest guard;
  and existing `NOT USED` / `NOT VERIFIED` distinctions.
- Patch and installed-file whitespace checks passed. Git emitted only the
  expected Windows line-ending advisory; the patch records the deterministic
  `core.autocrlf=false` application command.

## FnBShop read-only applicability check

Authority read from `D:/JOEWRKS/GEOTest/FnBShop`:

- state SHA-256:
  `70bcb39aa71e0dcca40dce93242400c9782cb7c165bec3a36db0ebb8a52403cd`;
- definition digest:
  `6db14700d5de4e5edeea04701d7f41e987113ad37b8cd2cbd2e5f8075a332249`;
- state validator: PASS; and
- Closure: `closed=true`, every metric `0`.

The mapping was checked against `RULE-020`, `RULE-038`, `AC-031`, `AC-032`,
`DESIGN.md`, and the current wireframe evidence. Exact values approved in
`RULE-020` remain binding Product constraints. DS-01 remains a DRAFT visual
proposal where Product does not already bind a value. Product approval does not
become user visual acceptance.

Application evidence read back without copying it into this repository:

| Evidence | SHA-256 | Relevant result |
| --- | --- | --- |
| `D:/JOEWRKS/GEOTest/FnBShop/examples/geo-fresh-market/wireframes/REVIEW.md` | `3acd91221baf22fdcd8daeea3cd29848793f0d9c2bfcb8ea5ad696f28bcc4e65` | Contains the scoped installed-guidance readback and Product/DRAFT/acceptance separation. |
| `D:/JOEWRKS/GEOTest/FnBShop/examples/geo-fresh-market/wireframes/evidence/final-evidence-r19.json` | `82c78f9cd515c4ef9c3c17157f64ab7c3eb82c1408c0352cac2e95efc4db928f` | `updatedGuidanceReview.newImplementationDefects = 0`; 229 recorded file hashes; documentation falsifier gap closed. |

The evidence explicitly leaves `userVisualAcceptance = PENDING` and
`causalToolEffect = NOT_CLAIMED`.

## Boundaries retained

- No FnBShop Product Definition, DESIGN, implementation, or evidence file was
  changed by this JOEFLOW delta.
- No Product/UX decision, schema, compiler, runtime, or downstream contract was
  changed.
- The repository's older skill source is still distinct from the installed
  baseline. This exact-base patch is not a source synchronization or a claim
  that future installations automatically include the delta.
- User visual acceptance, full accessibility certification, and causal tool
  effectiveness remain outside this verification.
