# UX State Taxonomy

For every interactive screen or component, record applicability and behavior for: Default, Loading, Empty, Partial, Success, Error, Disabled, Permission denied, Unauthenticated, Offline, Timeout, Retrying, Submitting, Completed, Cancelled, and Expired.

For every major action inspect: entry, precondition, input, validation, submit, success, failure, retry, cancel, back, refresh, duplicate/concurrent action, timeout, offline, permission, session expiration, data mutation, side effect, notification, persistence, undo, and destructive confirmation.

Record every state axis in `ux_coverage[].states` using the structured coverage-cell form. Declare the authoritative action inventory in `screens[].major_actions`; `ux_coverage[].actions` is an array of `{ "key": ..., "cells": ... }` rows whose unique key set must match it exactly. Use `N/A` with rationale when an axis does not apply. Missing keys, blanks, duplicate rows/actions, and missing or extra actions block closure. A genuinely actionless interactive screen records `screens[].no_major_actions_reason`.
