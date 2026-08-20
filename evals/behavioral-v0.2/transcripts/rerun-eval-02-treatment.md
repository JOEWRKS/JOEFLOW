# RERUN-EVAL-02-TREATMENT

## Execution/runtime

- Run slug: `rerun-eval-02-treatment`
- Executed at: `2026-08-20T21:08:24.9508113+09:00`
- Workspace: `D:\JOEWRKS\JOEWRKS-Product`
- Skill explicitly used: `joewrks-product-definition`
- Canonical state: `D:\JOEWRKS\JOEWRKS-Product\evals\behavioral-v0.2\run-state\rerun-eval-02-treatment\product-definition\rerun-eval-02-treatment\state.json`
- Evidence boundary: only `evals/behavioral-v0.2/fixtures/team-invitation`
- Implementation performed: no

## Prompt

> 우리 SaaS에 팀원 초대 기능 넣어줘.

## Evidence

1. `fixtures/team-invitation/README.md`: requests use session authentication and `request.user_id` is the authenticated user. Workspace roles are `OWNER`, `ADMIN`, and `MEMBER`. The plan limit is 25 accepted members. Whether pending invitations consume the limit is explicitly undocumented. No invitation feature exists.
2. `fixtures/team-invitation/src/repository.md`: accepted membership is unique on `(workspace_id, user_id)`; workspace active/deleted status, membership lookup, accepted-member count, and verified normalized-email lookup are available. No invitation table or token contract exists.
3. `fixtures/team-invitation/src/email-service.md`: transactional email queueing returns a provider message ID, but queue acceptance does not guarantee delivery. Delivered, bounced, and complained webhooks exist; their product behavior is undefined.

## Full response

아직 구현은 시작하지 않았습니다. 현재 증거에는 `OWNER`·`ADMIN`·`MEMBER` 역할이 있다는 사실만 있고, 누가 초대할 수 있는지는 정의돼 있지 않습니다. 이 선택은 API 권한, 화면 노출, 감사 기록, 테스트 전반에 영향을 줍니다.

누가 팀원을 초대할 수 있어야 하나요?

1. `OWNER + ADMIN` — 추천. 일반적인 팀 운영 권한과 보안의 균형이 좋습니다.
2. `OWNER만` — 가장 엄격하지만 운영 병목이 생길 수 있습니다.
3. `OWNER + ADMIN + MEMBER` — 협업은 빠르지만 오초대·남용 방지와 감사 요구가 커집니다.

선택해 주시면 그 결정을 상태에 기록한 뒤, 다음으로 파급력이 큰 미결정 사항을 하나씩 확인하겠습니다.

## Ordered questions

1. `UNK-001`: Which workspace roles may invite teammates? Recommendation: `OWNER + ADMIN`.
2. `UNK-002`: May invitations target any email address or only an existing verified user?
3. `UNK-003`: Do pending invitations consume the 25-member plan limit?
4. `UNK-004`: What role does an invite grant, and may the inviter choose it?
5. `UNK-005`: How long is an invitation valid?
6. `UNK-006`: Are tokens single-use, and how are they stored and validated?
7. `UNK-007`: What happens for duplicate invitations or an already accepted member?
8. `UNK-008`: May a pending invitation be revoked, and by whom?
9. `UNK-009`: May an invitation be resent, and what throttling applies?
10. `UNK-010`: Must the recipient sign in or create an account with the invited email before acceptance?
11. `UNK-011`: What happens if the workspace is deleted before acceptance?
12. `UNK-012`: Is the 25-member limit rechecked atomically at acceptance?
13. `UNK-013`: How do delivered, bounced, and complained webhooks affect state or UI?
14. `UNK-014`: What does the inviter see when queueing succeeds but delivery later fails?
15. `UNK-015`: Which invitation events require audit records and who may view them?
16. `UNK-016`: Where should invitation management live, and what UI surfaces are required?
17. `UNK-017`: What email-address exposure and retention policy applies across invitation states?

## Unknowns and assumptions

- All 17 independently answerable unknowns above are material and remain `OPEN`.
- No missing policy was converted into an assumption.
- The only recommendation is `OWNER + ADMIN` for `UNK-001`; it is not treated as accepted.
- Known evidence was recorded without extending it: session authentication, three existing roles, 25 accepted-member limit, repository capabilities, and email delivery signals.
- No screen, route, token format, invitation schema, expiration period, role default, quota behavior, retry policy, or webhook behavior was assumed.

## Writes

- Created only the canonical state file listed above.
- Created only this transcript.
- No fixture, source, shared product file, schema, or implementation file was changed.

## Validation/closure

- Structure validator: passed (`valid: true`, `errors: []`).
- Closure validator: correctly did not close (`closed: false`, digest `0948fc8725883035aa444e08a29219ef9f66a68f4dece3209fa1c20f75677189`). It reported 17 blocking unknowns, 19 coverage gaps, 1 orphan requirement, missing/stale approval metrics, and no structural errors.
- Closure is not eligible because material unknowns remain open and explicit user approval has not been given.

## Final status

`BLOCKED` — product definition requires the user's answer to `UNK-001`; implementation was intentionally not started.
