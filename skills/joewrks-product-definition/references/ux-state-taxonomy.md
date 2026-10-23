# UX State Taxonomy

For every interactive screen or component, record applicability and behavior for: Default, Loading, Empty, Partial, Success, Error, Disabled, Permission denied, Unauthenticated, Offline, Timeout, Retrying, Submitting, Completed, Cancelled, and Expired.

For every major action inspect: entry, precondition, input, validation, submit, success, failure, retry, cancel, back, refresh, duplicate/concurrent action, timeout, offline, permission, session expiration, data mutation, side effect, notification, persistence, undo, and destructive confirmation.

Record every state axis in `ux_coverage[].states` using the structured coverage-cell form. Declare the authoritative action inventory in `screens[].major_actions`; `ux_coverage[].actions` is an array of `{ "key": ..., "cells": ... }` rows whose unique key set must match it exactly. Use `N/A` with rationale when an axis does not apply. Missing keys, blanks, duplicate rows/actions, and missing or extra actions block closure. A genuinely actionless interactive screen records `screens[].no_major_actions_reason`.

## Experience pass

State coverage shows the system handles every condition; it does not show that a person can use the surface. Before FREEZE, settle three items for each primary user and interactive surface, each as a decision (evidence, user answer or accepted recommendation) or a truthful unknown:

- **Journey.** Walk the user's own path: first contact (what they see and must understand the first time), the main task step by step from their side, likely mistakes and how they notice and recover, and the return visit. Write user actions and what they see, not system steps.
- **Interaction mechanics.** For each major action: input method per supported device (tap, click, keyboard, drag), any preview or confirm step, how to cancel or undo, and how new overlays, hints or modes change an existing input. "Keep the existing procedure" is a decision only after checking it against the new surface.
- **Information budget.** For the smallest supported viewport: what must be visible at once without scrolling, what sits behind disclosure, and what is dropped. Visual styling stays with design; what the user must see, and when, is planning.

Record the results in screen specifications and user flows. Put unresolved items in the question queue alongside data and computation questions. Delegating "placement" or "layout" to design settles none of these.
