# UNKNOWN LEDGER

> revision 44; CLOSED; explicitly approved; blocking unknowns 0.

| ID | Status | Question | Resolution |
|---|---|---|---|
| UNK-001 | ANSWERED | 클라이언트는 공유 시안에 어떤 방식으로 접근하고 신원을 확인해야 하는가? | 클라이언트는 계정을 만들지 않고 이메일로 받은 project-scoped magic review link로 접근한다. 링크 하나는 특정 project 하나에만 접근하며 public anonymous share link는 제공하지 않는다. |
| UNK-002 | ANSWERED | v1에서 한 project에 참여할 수 있는 디자이너 인원은 1명인가, 복수인가? | v1은 workspace owner/Designer 1명만 운영하고 내부 collaborator role은 제외한다. Designer는 이메일 로그인하며 low-fi는 auth provider-neutral로 유지한다. |
| UNK-003 | ANSWERED | v1에서 지원할 시안 파일 형식은 무엇인가? | v1 지원 형식은 PNG, JPG/JPEG, PDF만이다. Figma 원본 direct import와 video review는 비범위다. 가능한 경우 unsupported type을 client-side에서 사전 차단하고 server rejection error도 별도로 처리한다. |
| UNK-004 | ANSWERED | 시안 위 피드백은 핀 코멘트만 필요한가, 영역 표시나 드로잉도 필요한가? | v1 annotation은 지점 핀과 댓글 방식이다. Image는 normalized x/y, PDF는 page number와 normalized x/y를 저장한다. |
| UNK-005 | ANSWERED | 피드백 댓글에 답글 스레드를 지원할 것인가? | Designer와 Client Reviewer 모두 thread reply를 작성할 수 있다. |
| UNK-006 | ANSWERED | 수정본은 새 버전으로만 추가되는가, 기존 버전을 교체할 수도 있는가? | 같은 Version ID 안에서 파일 교체를 금지하고 모든 새 파일은 새 immutable Version으로 만든다. 실패한 upload는 phantom Version을 만들지 않는다. |
| UNK-007 | ANSWERED | 새 수정본이 올라오면 이전 버전의 미해결 피드백은 어떻게 이어지는가? | comment는 exact Version에 고정한다. 새 Version에 과거 핀을 자동 복사하지 않으며 이전 Version을 열면 과거 comment를 볼 수 있다. |
| UNK-008 | ANSWERED | 승인 상태의 단계와 가능한 전이는 무엇인가? | 각 version은 DRAFT, IN_REVIEW, CHANGES_REQUESTED, APPROVED 중 하나의 상태를 가진다. 리뷰 요청 시 IN_REVIEW, 수정 요청 시 CHANGES_REQUESTED, 승인 시 해당 exact version만 APPROVED가 된다. 새 version은 자동 승인되지 않으며 과거 승인 이력은 보존한다. |
| UNK-009 | ANSWERED | 한 project에 복수 클라이언트가 참여할 때 누가 exact version을 최종 APPROVED로 만들 수 있는가? | v1은 project당 지정된 Client Reviewer 1명만 두며 해당 이메일 신원으로 접근한 reviewer만 exact version을 APPROVED 또는 CHANGES_REQUESTED로 전환할 수 있다. 복수 reviewer와 승인자 교체 workflow는 v1 범위 밖이다. |
| UNK-010 | ANSWERED | APPROVED 상태인 exact version 자체에 새 피드백을 추가할 수 있는가? | APPROVED exact Version은 comment와 reply mutation을 모두 금지하고 기존 thread와 approval history만 읽을 수 있다. 변경이 필요하면 새 Version에서 새 review cycle을 시작한다. |
| UNK-011 | ANSWERED | 공유 링크는 만료되는가, 만료된다면 기준은 무엇인가? | magic review link는 발급 시각으로부터 30일 후 만료된다. 이전 만료 결정 DEC-011은 DEC-015로 supersede되었다. |
| UNK-012 | ANSWERED | exact Version의 APPROVED 또는 CHANGES_REQUESTED 전환을 누구에게 어떤 채널로 알릴 것인가? | Client Reviewer가 exact Version을 APPROVED 또는 CHANGES_REQUESTED로 전환하면 Designer에게 즉시 이메일을 보내고 행동한 Client Reviewer에게는 보내지 않는다. v1에는 in-app realtime notification center를 제공하지 않는다. |
| UNK-013 | ANSWERED | Designer가 project 삭제를 요청하면 v1에서 어떤 데이터를 실제 삭제하거나 보존할 것인가? | v1은 Designer archive만 제공한다. archive 후 Client magic link 접근과 새 comment/review를 차단하고 Designer는 archive history를 볼 수 있다. Hard delete와 retention은 v1 implementation scope 밖의 future policy dependency다. |
| UNK-014 | ANSWERED | v1에서 결제·구독을 제공할 것인가, 아니면 과금 없는 제품 검증 범위로 둘 것인가? | v1은 billing, subscription, payment, refund를 범위 밖으로 두고 핵심 review workflow 검증에 집중한다. |
| UNK-015 | ANSWERED | 모바일에서 시안 검토와 피드백 작성까지 지원해야 하는가, 열람만 지원해도 되는가? | 모바일에서도 핀 생성과 댓글 작성을 지원하되 정밀 UX는 단순화할 수 있다. |
| UNK-016 | ANSWERED | 감사 이력에서 누가 언제 어떤 피드백·버전·승인 변경을 했는지 보존하고 노출해야 하는가? | 별도 통합 audit 화면 없이 각 객체 화면에 history를 내장한다. Designer는 모든 Version, thread, approval, link lifecycle, archive history를 보고 Client Reviewer는 접근 중인 project의 exact Version thread와 approval history만 본다. |
| UNK-017 | ANSWERED | 동시 편집·중복 제출·오래된 화면에서의 상태 변경 충돌을 어떻게 처리할 것인가? | 상태 전환 요청은 expected Version state revision을 포함한다. 불일치하면 mutation을 거부하고 최신 상태를 표시한다. 승인 성공 여부가 불명확하면 성공 UI를 표시하지 않으며 retry는 duplicate approval record를 만들지 않는다. |
| UNK-018 | ANSWERED | 네트워크 실패로 comment 또는 reply 제출 결과가 불명확할 때 입력을 어떻게 보존하고 중복 없이 재시도할 것인가? | comment/reply text를 best-effort로 로컬 보존하고 client-generated message attempt ID로 idempotent 조회·재시도한다. 이미 성공했다면 기존 record를 반환하고 duplicate submission을 금지한다. |
| UNK-019 | ANSWERED | 피드백 comment와 reply를 작성 후 편집할 수 있는가? | v1에서 comment와 reply는 편집할 수 없으며 정정은 새 reply로 남긴다. |
| UNK-020 | ANSWERED | 피드백을 해결 처리하거나 다시 여는 주체와 조건은 무엇인가? | Designer가 thread를 RESOLVED로 전환하며, Client Reviewer가 RESOLVED thread에 reply하면 자동으로 OPEN 상태가 된다. |
| UNK-021 | ANSWERED | 디자이너는 이미 배포한 공유 링크를 폐기할 수 있는가? | Designer는 active review link를 별도로 수동 revoke할 수 있다. |
| UNK-022 | ANSWERED | 폐기·만료·교체된 magic review link의 이력과 접근 기록을 v1에서 무엇까지 보존할 것인가? | magic review link lifecycle metadata만 보존하고 raw token이나 요청별 IP/device access log는 저장하지 않는다. token은 원문 복구 불가능하게 저장·검증한다. |
| UNK-023 | ANSWERED | 지정된 동일 Client Reviewer가 하나의 active magic review link를 여러 브라우저·기기 세션에서 사용할 수 있는가? | 동일 Client Reviewer 이메일 신원을 확인한 뒤 여러 브라우저·기기 세션을 허용한다. revoke, expiry, archive는 모든 세션의 다음 요청을 차단하고 concurrent mutation은 exact Version ID와 expected revision으로 보호한다. |
| UNK-024 | ANSWERED | 이메일로 받은 magic review link를 다른 사람이 전달받았을 때도 접근 가능한 bearer link로 볼 것인가, 수신 이메일의 재인증을 요구할 것인가? | magic review link의 소지만으로는 충분하지 않으며, project에 지정된 Client Reviewer 이메일 신원으로 접근한 사용자만 reviewer 권한을 행사할 수 있다. |
| UNK-025 | ANSWERED | 새 link 발급 시 이전 active link를 어떻게 처리하는가? | project당 active review link는 하나만 허용하고 새 링크 발급 시 기존 active link를 즉시 revoke한다. 열린 기존 세션도 다음 요청부터 차단한다. |
| UNK-026 | ANSWERED | APPROVED가 된 exact version의 승인을 이후 철회하거나 되돌릴 수 있는가? | APPROVED는 철회하지 않는다. 승인 이후 변경은 새 version과 새 검토 사이클로 처리하며 과거 승인 actor, timestamp, version 기록을 보존한다. |
| UNK-027 | ANSWERED | 클라이언트가 CHANGES_REQUESTED로 전환할 때 최소 한 개의 미해결 피드백이나 수정 요청 사유를 필수로 요구할 것인가? | CHANGES_REQUESTED 전환에는 unresolved 핀 댓글이 하나 이상 있거나 전체 수정 요청 사유 텍스트가 있어야 하며 빈 근거 전환은 금지한다. |
| UNK-028 | ANSWERED | 새 version이 IN_REVIEW가 될 때 이전 version도 IN_REVIEW라면 이전 version의 상태와 리뷰 가능 여부는 어떻게 되는가? | 여러 exact Version이 동시에 독립적으로 IN_REVIEW일 수 있다. comment와 approval은 exact Version에만 귀속하며 reviewer가 열어 본 Version만 승인한다. approval과 새 upload가 동시에 발생해도 approval은 old exact Version에만 적용되고 새 Version은 별도 IN_REVIEW다. project 전체 승인 상태는 두지 않는다. |
| UNK-029 | ANSWERED | APPROVED 기록이 가리키는 exact version의 파일과 승인 관련 메타데이터를 이후 편집·교체할 수 있는가? | APPROVED exact version의 파일, version ID, approval actor, approval timestamp는 immutable이며 이후 변경은 반드시 새 version으로 올린다. |
| UNK-030 | ANSWERED | Designer가 RESOLVED thread에 reply할 때 thread 상태는 어떻게 되는가? | Designer는 RESOLVED thread에 보충 reply를 작성할 수 있지만 상태는 RESOLVED로 유지한다. Client Reviewer reply만 OPEN으로 재전환한다. |
| UNK-031 | ANSWERED | Client Reviewer가 이미 review 화면을 열어 둔 상태에서 magic review link가 30일 만료 시각을 지나면 현재 세션을 즉시 종료할 것인가? | 만료 시 즉시 새 read/write 요청을 차단하고 만료 화면을 표시한다. 작성 중 comment text는 가능한 한 로컬에 보존하지만 서버 제출은 금지하며 Designer가 새 link를 발급한 뒤 복구·재시도할 수 있다. |
| UNK-032 | ANSWERED | 열린 세션이 link revoke로 차단될 때 작성 중 comment text를 만료 때와 동일하게 로컬 보존·복구할 것인가? | revoke 시에도 서버 제출을 막고 초안을 best-effort로 로컬 보존하며 새 active link 재인증 후 복구·재시도한다. |
| UNK-033 | ANSWERED | 30일 만료 전에 Designer 또는 Client Reviewer에게 사전 알림을 보낼 것인가? | v1에서는 expiry 사전 알림을 보내지 않는다. 만료 후 Designer가 새 link를 재발급할 수 있다. |
| UNK-034 | ANSWERED | Client Reviewer가 새 pin comment를 만들면 Designer에게 어떤 채널로 알릴 것인가? | Client Reviewer가 새 pin comment를 만들면 Designer에게 즉시 이메일을 보내고 행동한 Reviewer에게 self-notification은 보내지 않는다. |
| UNK-035 | ANSWERED | Designer가 새 Version을 DRAFT로 업로드한 시점에도 Client Reviewer에게 이메일을 보낼 것인가, 명시적 리뷰 요청 때만 보낼 것인가? | DRAFT upload에는 알림하지 않는다. Designer가 명시적으로 review request를 보내면 Version을 IN_REVIEW로 전환하고 magic review link와 함께 Client Reviewer에게 즉시 이메일을 보내며 Designer 자기 알림은 없다. |
| UNK-036 | ANSWERED | thread reply가 작성되면 상대 참여자에게 어떤 채널로 알릴 것인가? | thread reply 작성 시 상대 참여자에게 즉시 이메일을 보내고 작성자 자신에게는 보내지 않는다. |
| UNK-037 | ANSWERED | upload 완료 응답이 timeout되어 성공 여부가 불명확한 상태에서 Designer가 재시도하면 중복 Version 생성을 어떻게 방지할 것인가? | client-generated upload attempt ID로 upload를 idempotent하게 재개·조회하고 이미 성공한 Version이 있으면 같은 Version을 반환하며 중복 Version 생성을 금지한다. |
| UNK-038 | ANSWERED | v1에서 단일 시안 파일의 최대 크기는 얼마인가? | 지원 파일 1개의 최대 크기는 100MB다. 가능한 경우 client-side에서 초과를 사전 차단하고 server는 별도 rejection error를 반환하며 recovery를 표시한다. |
| UNK-039 | ANSWERED | v1에서 PDF 한 파일의 최대 페이지 수는 얼마인가? | v1에서는 PDF page-count 제한을 두지 않고 100MB 파일 제한만 적용한다. PDF page rendering은 lazy/on-demand로 제공한다. |
| UNK-040 | DEFERRED_NON_BLOCKING | 실제 성능 데이터에 기반한 future PDF page cap은 얼마로 정할 것인가? | v1은 100MB 제한과 lazy/on-demand rendering으로 동작하며 page cap 수치는 실제 렌더링 성능 데이터가 있어야 근거 있게 정할 수 있다. |
| UNK-041 | DEFERRED_NON_BLOCKING | 삭제 요청이 없는 DRAFT, IN_REVIEW, CHANGES_REQUESTED Version과 thread를 얼마 동안 보존할 것인가? | v1은 archive 후 데이터를 보존하며 자동 retention expiration을 실행하지 않고 실제 보존 기간은 future policy에서 정한다. |
| UNK-042 | DEFERRED_NON_BLOCKING | 삭제 요청이 없는 APPROVED exact Version과 immutable approval history를 얼마 동안 보존할 것인가? | v1은 APPROVED exact Version과 approval history를 archive history로 보존하며 구체적 retention 기간은 future policy에서 정한다. |
| UNK-043 | DEFERRED_NON_BLOCKING | future hard delete는 어떤 주체·대상·대기 기간·복구 가능성으로 제공할 것인가? | v1은 reversible archive만 제공하고 irreversible hard delete의 권한·대상·대기·복구 정책은 future product and legal review가 필요하다. |
| UNK-044 | ANSWERED | Designer는 ARCHIVED project를 다시 활성화할 수 있는가? | Designer는 ARCHIVED project를 ACTIVE로 되돌릴 수 있지만 기존 link는 절대 복구하지 않는다. Client 접근을 다시 열려면 새 review request로 새 active link를 발급해야 한다. |
| UNK-045 | ANSWERED | CHANGES_REQUESTED 상태 전환의 서버 결과가 network timeout으로 불명확할 때 어떻게 조회·재시도할 것인가? | transition attempt ID, exact Version ID, expected state revision으로 idempotent 처리한다. 이미 성공했다면 기존 결과를 반환하고 상태 이력과 Designer 이메일을 중복 생성하지 않는다. |
| UNK-046 | ANSWERED | Workspace Owner / Designer의 이메일 로그인은 어떤 인증 방식으로 제공할 것인가? | Designer는 provider-neutral 이메일 magic link로 로그인한다. 로그인 링크는 15분 만료, 1회 사용이며 재발급 시 이전 미사용 링크를 무효화한다. email delivery 실패와 resend는 구분하고, 인증 성공 후 session 복구를 제공한다. |
| UNK-047 | ANSWERED | Designer 인증 성공 후 session의 지속 기간과 재인증 경계는 어떻게 정할 것인가? | Designer session은 인증 시점부터 절대 최대 30일이며 7일 연속 미사용 시 만료한다. 어느 경계든 만료 후에는 새 email magic link로 재인증해야 한다. |
| UNK-048 | ANSWERED | v1에서 Designer별 project 수, 저장 용량, Version 수에 어떤 사용 한도를 적용할 것인가? | workspace 전체 project 수와 총 저장 용량에는 hard cap을 두지 않는다. project당 active deliverable/version file은 최대 50개다. 한도 도달 시 기존 version 열람·download·archive는 허용하고 새 deliverable/version upload만 차단하며 명확한 limit state를 표시한다. |
