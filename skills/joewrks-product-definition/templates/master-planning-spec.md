# MASTER PLANNING SPEC — {{project_name}}

> Complete human-readable projection of the approved Product Definition.
> Canonical authority remains `{{CANONICAL_STATE_PATH}}`.

## Approved identity

- Revision: `{{APPROVED_DEFINITION_REVISION}}`
- Definition digest: `{{APPROVED_DEFINITION_DIGEST}}`
- Approval Manifest digest: `{{APPROVED_MANIFEST_DIGEST}}`
- Status: `{{APPROVAL_STATUS}}`

## 1. Product, users, goals, scope

Describe the user outcome, actors, goals, included scope, explicit exclusions,
external dependencies, and important product boundaries.

## 2. IA, navigation, and return relationships

Describe information hierarchy separately from screen-to-screen movement.
For every screen, include stable ID, purpose, entry, exit, and return behavior.

## 3. Shared behavior, data, and state contracts

Define shared rules once and link exact stable IDs/source pointers. A shared
clause may reduce duplication but must not erase when or where it applies.

## 4. Screen specifications

For each screen: purpose, information priority, major actions, applicable
states, inputs, reads/writes, persistence, failures/recovery, responsive and
accessibility requirements, and related acceptance IDs.

## 5. User flows

For every material flow: entry, preconditions, actor action, system decision,
happy path, alternatives, failures, recovery/retry, exit, postcondition, and
acceptance IDs.

## 6. Action contracts

For every major action: actor, target, input, preconditions, execution,
conditional success outcomes, rejection/failure, recovery, cancellation,
concurrency/idempotency where applicable, visible result, data effect, and
source binding.

### Projection-fidelity rule

- Preserve material conditions and branches from the approved source.
- Never turn an exceptional offline/stale/normalization/recovery path into the
  universal success/failure result.
- When text is deduplicated, retain exact stable-ID/source bindings and state
  on each action when the shared clause applies.
- If a displayed branch cannot be traced to approved authority, remove it or
  re-enter Product Definition; do not invent policy in this projection.

## 7. Acceptance criteria

Include the full assertion/expected-result meaning and requirement references.
Do not reduce acceptance to an ID list.

## 8. Responsive, accessibility, and downstream choice boundaries

Separate approved product requirements from later visual/technical choices.

## 9. Remaining unknowns, external verification, and approval state

List only real unresolved items. Distinguish product ambiguity from runtime,
provider, visual, or integration verification that has simply not run.

## 10. Source map

Provide exact canonical pointers/stable IDs so reviewers and downstream agents
can trace each material section without reconstructing product meaning from
many editable documents.
