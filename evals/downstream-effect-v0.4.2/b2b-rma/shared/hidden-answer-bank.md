# Controller-only hidden answer bank

Created after the Product Agent finished. The Product Agent did not read this file or its source instruction.

## Source identity

- Controller instruction attachment: `C:\Users\tjdwo\.codex\attachments\8c2c03a3-0a04-4da2-a306-7d4748822ad9\pasted-text.txt`
- SHA-256: `999E9A9CEA698E5BA335B49F66E99B0E9066A93FBDF1998A659FC6D4E7CCA0AB`
- Exact Product Agent prompt: `도매·납품업체가 거래처의 반품, 불량, 오배송 요청을 받고, 반품 승인부터 입고 검수, 교환·환불·거절까지 관리할 수 있는 웹앱 만들어줘.`

## Hidden product truth supplied to the controller

- One supplier workspace serves multiple customer organizations. Marketplace, new-order purchasing, and checkout are out of scope. RMA applies to delivered Order Lines.
- Conceptual roles are Customer Requester, RMA Agent, Warehouse Inspector, and Finance Operator. Internal users may hold multiple roles; current permission and least privilege govern every protected request.
- A customer user can access only its own organization’s cases, history, and attachments, even if another Case ID is known.
- Every Return Line binds to one exact delivered Order Line and preserves Order ID, Order Line ID, SKU/product identity, and required immutable commercial snapshots.
- Requested quantity is capped by delivered quantity minus finalized prior returns for that exact Order Line.
- Serial-managed units require exact serials; incompatible duplicate serial ownership is a hard block. Lot identity and quantity are recorded where applicable.
- One case can contain multiple Return Lines and mixed line outcomes.
- Drafts can be created, edited, and deleted. Submit creates an immutable historical snapshot.
- Reasons include defective, wrong item, shipping damage, quantity issue, and other; other requires explanation.
- Evidence accepts JPG, PNG, and PDF, at 20 MB per file. Upload failure must preserve otherwise valid Draft input.
- Submit binds to exact revision and operation identity; same-operation retry cannot duplicate state, history, or notification.
- RMA review is per line: approve, reject, or request more information. Only approved quantities become authorized.
- Authorization expires if shipment does not begin within 14 days; expired authority cannot silently reactivate.
- Customer cancellation is allowed before shipment begins and closes at IN_TRANSIT or an equivalent committed transit state.
- Carrier behavior may be deterministic simulation. Carrier or notification failure cannot roll back committed business truth.
- Warehouse receipt keeps authorized quantity and actual received quantity separate; short and excess receipt remain observable. Unauthorized excess never becomes automatically creditable or replaceable.
- Inspection binds to exact received scope and records quantity, serial/lot, condition, state, notes, and evidence. Finalized inspection cannot be silently edited by an ordinary Warehouse Inspector.
- Per-scope resolutions are REFUND, REPLACEMENT, RETURN_TO_CUSTOMER, and NO_CREDIT.
- Refund basis is immutable original net unit price times finalized eligible credit quantity.
- Replacement quantity and dispatch lifecycle remain separate from original RMA history.
- Finance handles refund-eligible resolutions only and binds mutations to exact resolution, case/line revision, and current authority.
- No real bank, carrier, payment-provider, production email, or other production integration is required; simulation must be labeled.
- Material mutation uses expected version semantics. Stale, permission, and validation rejection are canonical no-ops except an explicitly allowed denial audit.
- Material operations require idempotency, including Submit, final Resolution, refund commit, and replacement dispatch.
- Role removal and reassignment take effect on the next protected request; an already-open browser grants no continuing authority.
- Customer and internal notifications are event-scoped; notification failure remains separate from business-state success.
- History is append-only event-time truth and preserves actor, time, exact object/revision, event-time state, and immutable event meaning.
- No hard-delete UI exists in v1. Exact retention may be explicitly deferred.
- Customer UX supports desktop and mobile; warehouse inspection is mobile-priority; RMA and Finance are desktop-first with tablet usability.
- Design is low-fi, neutral, and operational; final branding must not be invented.

## Mandatory reversal truth

Initial answer after the Product Agent asked about final-resolution reversibility: `RMA Agent가 final resolution을 확정하면 되돌릴 수 없다.`

After that decision materially propagated, the controller injected: `생각해보니 최종 처리 저장했다고 무조건 못 바꾸는 건 너무 빡세네. 실제 환불 지급이나 교환 출고가 커밋되기 전까진 RMA 담당자가 사유 남기고 resolution을 다시 열 수 있게 하자.`

The active replacement truth allows the currently authorized RMA Agent to reopen the same resolved Return Line with a reason only before the applicable downstream commit. Previous resolution history remains append-only. Committed payment, dispatch, return-to-customer handoff, or disposal execution cannot reopen and instead uses linked correction handling.

## Firewall result

- `REQUESTED_ONLY_CHECK` executions: `79`
- Hidden-truth leak detected: `0`
- Product Agent access to this bank before completion: `0`
- Emergent evaluator decisions were allowed only when the requested dimension was absent from this bank and the answer was kept consistent with already approved truth.

The chronological disclosure index is in `interrogation-transcript.md`; canonical question, answer, source, decision, and affected-ID detail is in the approved `DECISION_LEDGER.md`, `UNKNOWN_LEDGER.md`, and `state.json`.

