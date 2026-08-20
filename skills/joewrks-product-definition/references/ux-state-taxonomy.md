# UX State Taxonomy

For every interactive screen or component, record applicability and behavior for: Default, Loading, Empty, Partial, Success, Error, Disabled, Permission denied, Unauthenticated, Offline, Timeout, Retrying, Submitting, Completed, Cancelled, and Expired.

For every major action inspect: entry, precondition, input, validation, submit, success, failure, retry, cancel, back, refresh, duplicate/concurrent action, timeout, offline, permission, session expiration, data mutation, side effect, notification, persistence, undo, and destructive confirmation.

Use `N/A` with rationale when a state or interaction axis does not apply. Never use a blank as implicit `N/A`.

