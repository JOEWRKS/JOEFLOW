# EVAL-03 Comparison

## Outcome

| Run | Score | UX | Critical failure |
|---|---:|---:|---|
| Control | 59/100 | 5/5 | None |
| Initial Treatment | 93/100 | 5/5 | None |
| Final Treatment (rerun) | 100/100 | 5/5 | None |

Final Treatment delta versus Control: **+41**. Initial-to-final Treatment change: **+7**.

## Material Unknowns

Expected territories include selection/drag-drop, progress and lifecycle states, cancellation/retry, validation and rejection cases, multi-upload/concurrency/partial success, navigation/resume, permissions/quota/security, and post-upload processing.

Control discovered purpose plus a small deferred set: types/limits, multiplicity, processing, permissions, and success criteria. Treatment discovered job type, actor/access, formats/count/size/duplicates, destination/metadata/processing, security/privacy/retention, and a broad failure/recovery set.

Control missed nearly all concrete lifecycle, recovery, security, quota, concurrency, and post-transport failure territories. Initial Treatment still missed selection mechanics, progress/success presentation, concurrency, page-leave behavior, quota, explicit server rejection, and post-transport processing failure. Final Treatment separately registers all expected territories, including selection methods, transfer control, partial failure, server/network recovery, quota, and completion flow. Treatment-only legitimate discoveries include retention/deletion/privacy, expiry, accessibility, integration constraints, notifications, and audit/analytics.

## First Question

Control: “이 업로드 화면의 주 사용 목적은 무엇인가요?” This is a strong first question because purpose changes the whole interaction model.

Initial Treatment: “이 화면의 주된 업로드 업무 유형은 무엇인가?” This is equally well prioritized and slightly more diagnostic because its choices expose media-processing and tabular-import consequences.

Final Treatment: “어떤 용도의 파일 업로드인가요?” Its document submission, content registration, and large-file transfer choices efficiently expose validation/security, metadata, and resume/expiry consequences.

## Ordering

All three runs ask one high-fan-out purpose question before detailed constraints. Initial Treatment registers a later decision queue in six umbrella records. Final Treatment preserves the one-question dialogue while separating 24 independently answerable unknowns in state.

## Evidence First

Control did not inspect repository product evidence before asking. Initial Treatment searched for existing context and cited its absence. Final Treatment explicitly bounded its evidence to the user prompt because no product repository, documentation, API contract, design, or behavior was supplied.

## Silent Assumptions

No run silently selected material upload behavior. All recommendations remain explicitly unselected.

## Premature Build / Closure

No run built or claimed completion. Control says implementation is deferred. Both Treatment runs keep authoritative status `OPEN` and report closure blockers; the final run records 23 separate material blockers.

## State Discipline

Control created only its evaluation transcript; absence of the Treatment contract is not itself a failure, though no durable definition state exists. Initial Treatment persisted six unknowns. Final Treatment persists 24 separate unknowns, passes structural validation, and preserves a non-closed status.

## Rationalizations

No material rationalization is observable. Control’s “가장 단순하고 명확한 흐름” is presented as a recommendation, not an assumed answer. Both Treatment runs explain why implementation cannot proceed without choosing the upload purpose.

## Verdict

**PASS**. Final Treatment improves from 93 to 100 and leads Control by 41 points. It eliminates the initial umbrella-unknown coverage gaps without increasing UX burden, inventing behavior, or closing prematurely.
