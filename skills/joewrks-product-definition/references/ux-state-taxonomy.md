# UX State Taxonomy

For every interactive screen or component, record applicability and behavior for: Default, Loading, Empty, Partial, Success, Error, Disabled, Permission denied, Unauthenticated, Offline, Timeout, Retrying, Submitting, Completed, Cancelled, and Expired.

For every major action inspect: entry, precondition, input, validation, submit, success, failure, retry, cancel, back, refresh, duplicate/concurrent action, timeout, offline, permission, session expiration, data mutation, side effect, notification, persistence, undo, and destructive confirmation.

Record every axis in `screen_coverage[].states` and `screen_coverage[].actions` using the structured coverage-cell form. Use `N/A` with rationale when an axis does not apply. Missing keys and blanks block closure.
