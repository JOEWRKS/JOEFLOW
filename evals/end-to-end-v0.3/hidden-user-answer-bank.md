# Hidden User Answer Bank

Evaluator-only reproducibility summary. This file was not shown to the Product Agent.

- Topology: one freelancer/small studio workspace, many client projects; no marketplace, discovery, or v1 billing.
- Roles: one Workspace Owner/Designer and one accountless Client Reviewer; no internal collaborator in v1.
- Access: Designer email login, provider-neutral; project-scoped client magic link; no public anonymous link. Initial expiry 7 days, revocable/reissuable, one project only. Prescribed mid-run reversal changes expiry to 30 days.
- Assets: PNG/JPG/PDF, 100 MB each, 50 active deliverable/version files per project; no Figma import or video.
- Versions: DRAFT, IN_REVIEW, CHANGES_REQUESTED, APPROVED; feedback and approval bind to an exact Version; new uploads never inherit approval.
- Comments: normalized image coordinates or PDF page plus normalized coordinates; append-only history; both roles reply; Designer resolves; Client reply reopens.
- Approval: exact Version, actor/timestamp/version ID, immutable history.
- Notifications: review invitation, new version, comment, reply, approval, changes request; no self-notification or realtime center.
- Lifecycle: archive disables client access and mutation; no hard delete/retention policy in v1; retain as future policy dependency.
- Concurrency/recovery: independent comments; exact-version approval; idempotent upload/comment/approval; preserve recoverable drafts; separate invitation from delivery.
- Responsive/accessibility: Designer desktop-first/tablet usable; Client desktop/mobile with mobile pinning; keyboard/focus/names/non-color status/contrast/pin navigation.
- Visual: low-fi structure only; no brand, final color/type, illustration, or complex motion.
