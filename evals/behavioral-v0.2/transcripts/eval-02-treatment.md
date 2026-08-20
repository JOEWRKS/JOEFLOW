# EVAL-02-TREATMENT Observable Record

- Execution ID: `eval-02-treatment`
- Runtime: not observable
- Prompt: `Use $joewrks-product-definition for “우리 SaaS에 팀원 초대 기능 넣어줘.”`

## Skill/evidence read

- `skills/joewrks-product-definition/SKILL.md`
- Routed references: `state-contract.md`, `interrogation-engine.md`, `unknown-taxonomy.md`, `requirement-taxonomy.md`, `artifact-dependency-graph.md`, `product-coverage-matrix.md`, `ux-state-taxonomy.md`, `failure-recovery-taxonomy.md`, `closure-gate.md`
- State template and schema: `templates/state.example.json`, `schemas/state.schema.json`
- Product evidence: `fixtures/team-invitation/README.md`, `src/repository.md`, `src/email-service.md`

## Full first response

기존 증거를 확인했습니다. 현재 세션 인증을 사용하고 역할은 `OWNER`/`ADMIN`/`MEMBER`이며, 정원은 수락된 멤버 25명입니다. 아직 초대 테이블·토큰 계약은 없고 이메일 큐 성공이 실제 배달을 보장하지도 않습니다.

첫 결정은 초대 권한입니다. **누가 팀원을 초대할 수 있어야 하나요?** 보안과 권한 모델, 화면 노출, API 검증에 모두 영향을 줍니다.

1. `OWNER + ADMIN` — 권한 위임과 안전성의 균형이 좋아 추천합니다.
2. `OWNER만` — 가장 보수적이지만 운영 병목이 생길 수 있습니다.
3. `모든 멤버` — 협업은 빠르지만 오초대·권한 남용 위험이 큽니다.

## Ordered questions

1. `UNK-001` — Which workspace roles may invite team members? (asked; awaiting answer)
2. `UNK-002` — Do pending invitations consume the 25-member plan limit?
3. `UNK-003` — Can invitations target any email or only an existing verified user?
4. `UNK-004` — Which role is assigned, and can the inviter choose it?
5. `UNK-005` — What are expiry, resend, revoke, duplicate, and delivery-failure behaviors?

## Unknowns/assumptions

- Five material unknowns are registered in authoritative state.
- No material product assumption was made.
- The recommendation `OWNER + ADMIN` is not accepted or recorded as a decision until the user explicitly chooses it.

## Writes

- Authoritative state: `evals/behavioral-v0.2/run-state/eval-02-treatment/product-definition/eval-02-treatment/state.json`
- Observable record: `evals/behavioral-v0.2/transcripts/eval-02-treatment.md`
- No shared product files or implementation files were edited.

## Validation/closure behavior

- Structural validation initially reported that descriptive impact-axis labels in `affects` were treated as broken object references. The state was corrected by keeping `affects` for stable object IDs and moving descriptive labels to `impact_axes`, then both validators were rerun once.
- Structural validator result after correction: `valid: true`, `errors: []`.
- Closure validator result after correction: `closed: false`, `errors: []`, with `blocking_unknowns: 5`, `minimum_definition_gaps: 3`, and approval-related gaps still present.
- Closure is not claimed: material unknowns remain and explicit approval has not been requested.
- Implementation is blocked until material ambiguity is resolved.

## Final status

`OPEN` — awaiting the answer to `UNK-001`; no implementation started.
