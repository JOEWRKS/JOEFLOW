# DECISION LEDGER

> revision 44; CLOSED and explicitly approved. DEC-015 is active 30-day review expiry; DEC-011 is historical SUPERSEDED only.

| ID | Status | Decision |
|---|---|---|
| DEC-001 | ANSWERED | 클라이언트 접근은 계정 생성 없는 이메일 기반 project-scoped magic review link 방식으로 한다. |
| DEC-002 | ANSWERED | 승인 상태는 version 단위의 DRAFT, IN_REVIEW, CHANGES_REQUESTED, APPROVED 네 가지로 관리하며 APPROVED는 exact version에만 적용한다. |
| DEC-003 | ANSWERED | APPROVED exact version의 승인은 철회하지 않으며 이후 변경은 새 version의 새 검토 사이클로 처리하고 과거 승인 actor, timestamp, version 기록을 보존한다. |
| DEC-004 | ANSWERED | APPROVED exact version의 파일, version ID, approval actor, approval timestamp는 immutable이며 이후 변경은 반드시 새 version으로 처리한다. |
| DEC-005 | ANSWERED | v1은 project당 지정된 Client Reviewer 1명만 두고, 해당 이메일 신원으로 접근한 reviewer만 exact version을 APPROVED 또는 CHANGES_REQUESTED로 전환할 수 있다. 복수 reviewer와 승인자 교체 workflow는 v1 범위 밖이다. |
| DEC-006 | ANSWERED | v1 피드백은 exact Version에 고정된 지점 핀과 댓글로 제공한다. Image는 normalized x/y, PDF는 page number와 normalized x/y를 저장한다. 새 Version에 과거 핀을 자동 복사하지 않고 이전 Version에서 과거 comment를 열람할 수 있으며 모바일에서도 단순화된 핀 생성을 지원한다. |
| DEC-007 | ANSWERED | CHANGES_REQUESTED 전환에는 unresolved 핀 댓글이 하나 이상 있거나 전체 수정 요청 사유 텍스트가 있어야 하며 빈 근거 전환은 금지한다. |
| DEC-008 | ANSWERED | Client Reviewer만 새 pin comment를 생성하고 Designer와 Client Reviewer 모두 thread reply를 작성할 수 있다. Designer가 thread를 RESOLVED로 전환하며 Client Reviewer가 RESOLVED thread에 reply하면 자동 OPEN된다. comment와 thread history 삭제는 금지한다. |
| DEC-009 | ANSWERED | Designer는 RESOLVED thread에 보충 reply를 작성할 수 있으나 상태는 RESOLVED로 유지하며 Client Reviewer reply만 OPEN으로 재전환한다. |
| DEC-010 | ANSWERED | v1에서 comment와 reply는 편집하거나 삭제할 수 없고 정정은 새 reply로만 남긴다. |
| DEC-011 | SUPERSEDED | magic review link는 발급 시각으로부터 7일 후 만료된다. |
| DEC-012 | ANSWERED | magic review link 만료 시 새 read/write 요청을 즉시 차단하고 만료 화면을 표시한다. 작성 중 comment text는 best-effort로 로컬 보존하되 서버 제출을 금지하고 Designer가 새 link를 발급한 뒤 복구·재시도한다. |
| DEC-013 | ANSWERED | project당 active review link는 하나만 허용한다. 새 링크 발급 시 기존 active link를 즉시 revoke하고 열린 기존 세션도 다음 요청부터 차단한다. Designer는 active link를 수동 revoke할 수 있다. |
| DEC-014 | ANSWERED | link revoke 시에도 만료와 동일하게 서버 제출을 차단하고 작성 중 comment text를 best-effort로 로컬 보존하며 새 active link 재인증 후 복구·재시도한다. |
| DEC-015 | ANSWERED | magic review link는 발급 시각으로부터 30일 후 만료된다. |
| DEC-016 | ANSWERED | v1에서는 30일 expiry 사전 알림을 보내지 않으며 만료 후 Designer가 새 magic review link를 재발급할 수 있다. 다른 알림 유형은 별도 결정으로 닫는다. |
| DEC-017 | ANSWERED | Client Reviewer가 exact Version을 APPROVED 또는 CHANGES_REQUESTED로 전환하면 Designer에게 즉시 이메일을 보내고 행동한 reviewer에게는 보내지 않는다. v1에는 in-app realtime notification center를 제공하지 않는다. |
| DEC-018 | ANSWERED | Client Reviewer가 새 pin comment를 만들면 Designer에게 즉시 이메일을 보내고 행동한 Reviewer에게 self-notification은 보내지 않는다. |
| DEC-019 | ANSWERED | thread reply 작성 시 상대 참여자에게 즉시 이메일을 보내고 작성자 자신에게는 보내지 않는다. |
| DEC-020 | ANSWERED | DRAFT upload에는 알림하지 않는다. Designer의 명시적 review request가 Version을 IN_REVIEW로 전환하고 magic review link와 함께 Client Reviewer에게 즉시 이메일을 보내며 Designer self-notification은 없다. |
| DEC-021 | ANSWERED | 같은 Version ID 안에서 파일 교체를 금지하고 모든 새 파일은 새 immutable Version으로 만든다. 실패한 upload는 phantom Version을 만들지 않는다. |
| DEC-022 | ANSWERED | client-generated upload attempt ID로 upload를 idempotent하게 재개·조회하고 이미 성공한 Version이 있으면 같은 Version을 반환하며 중복 Version 생성을 금지한다. |
| DEC-023 | ANSWERED | 여러 exact Version은 동시에 독립적으로 IN_REVIEW일 수 있다. comment, approval, 상태는 exact Version에만 귀속하고 reviewer가 열어 본 Version만 승인한다. approval과 새 upload의 동시 발생은 서로 다른 exact Version에 독립 적용하며 project 전체 승인 상태는 두지 않는다. |
| DEC-024 | ANSWERED | 상태 전환 요청은 expected Version state revision을 포함하고 불일치하면 mutation을 거부해 최신 상태를 표시한다. 승인 성공 여부가 불명확하면 성공 UI를 표시하지 않으며 retry는 duplicate approval record를 만들지 않는다. |
| DEC-025 | ANSWERED | APPROVED exact Version은 comment와 reply mutation을 모두 금지하고 기존 thread와 approval history만 읽을 수 있다. 변경이 필요하면 새 Version에서 새 review cycle을 시작한다. |
| DEC-026 | ANSWERED | v1 시안 형식은 PNG, JPG/JPEG, PDF만 지원한다. Figma 원본 direct import와 video review는 비범위이며 unsupported type은 가능한 client-side 사전 차단과 별도 server rejection error로 처리한다. |
| DEC-027 | ANSWERED | 지원 파일 1개의 최대 크기는 100MB다. 가능한 client-side 사전 차단과 별도 server rejection error 및 recovery를 제공한다. |
| DEC-028 | ANSWERED | v1에서는 PDF page-count 제한을 두지 않고 100MB 파일 제한만 적용하며 page rendering은 lazy/on-demand로 제공한다. future page cap은 실제 성능 데이터에 의존한다. |
| DEC-029 | ANSWERED | v1은 Designer archive만 제공한다. archive 후 Client magic link 접근과 새 comment/review를 차단하고 Designer는 archive history를 볼 수 있다. Hard delete와 retention은 v1 implementation scope 밖의 future policy dependency다. |
| DEC-030 | ANSWERED | Designer는 ARCHIVED project를 ACTIVE로 되돌릴 수 있지만 기존 link는 절대 복구하지 않는다. Client 접근 재개에는 새 review request와 새 active magic review link 발급이 필요하다. |
| DEC-031 | ANSWERED | 동일 Client Reviewer 이메일 신원 확인 후 여러 브라우저·기기 세션을 허용한다. revoke, expiry, archive는 모든 세션의 다음 요청을 차단하고 concurrent mutation은 exact Version ID와 expected revision으로 보호한다. |
| DEC-032 | ANSWERED | magic review link lifecycle metadata만 보존하고 raw token과 요청별 IP/device access log는 저장하지 않는다. token은 원문 복구 불가능한 형태로 저장·검증한다. |
| DEC-033 | ANSWERED | 별도 통합 audit 화면 없이 각 객체 화면에 history를 내장한다. Designer는 모든 Version, thread, approval, link lifecycle, archive history를 보고 Client Reviewer는 접근 중인 project의 exact Version thread와 approval history만 본다. |
| DEC-034 | ANSWERED | comment/reply text를 best-effort로 로컬 보존하고 client-generated message attempt ID로 idempotent 조회·재시도한다. 이미 성공했다면 기존 record를 반환하고 duplicate submission을 금지한다. |
| DEC-035 | ANSWERED | CHANGES_REQUESTED는 transition attempt ID, exact Version ID, expected state revision으로 idempotent 처리한다. 이미 성공했다면 기존 결과를 반환하고 상태 이력과 Designer 이메일을 중복 생성하지 않는다. |
| DEC-036 | ANSWERED | v1은 이메일로 로그인하는 Workspace Owner / Designer 1명이 운영하고 내부 collaborator role은 제공하지 않는다. low-fi auth 표현은 provider-neutral로 유지한다. |
| DEC-037 | ANSWERED | Designer 로그인은 provider-neutral 이메일 magic link 방식으로 제공한다. 링크는 15분 후 만료되고 1회만 사용할 수 있으며, 새 링크 재발급 시 이전 미사용 링크를 무효화한다. email delivery 실패와 resend를 별도 결과로 처리하고 인증 성공 후 session 복구를 제공한다. |
| DEC-038 | ANSWERED | Designer session은 인증 성공 시점부터 절대 최대 30일이며 7일 연속 미사용 시 먼저 만료한다. 만료 후 새 email magic link 재인증이 필요하다. |
| DEC-039 | ANSWERED | v1은 과금 없는 핵심 review workflow 검증 범위로 운영하며 billing, subscription, payment, refund 기능을 제공하지 않는다. |
| DEC-040 | ANSWERED | v1은 workspace 전체 project 수와 총 저장 용량 hard cap 없이 운영하되 project당 active deliverable/version file을 최대 50개로 제한한다. 한도에서는 기존 version 열람·download·archive를 허용하고 새 deliverable/version upload만 차단하며 명확한 limit state를 표시한다. |
