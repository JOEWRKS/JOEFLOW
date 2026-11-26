# JOEFLOW 2.0.2 walk-through: a fresh project

Every command runs from this folder; outputs are verbatim.

### 1. the 2.0.2 template validates: six domains OPEN, one classification question each

```
python validate_state.py state.json
```

exit 0

```
{
  "errors": [],
  "valid": true,
  "validator": "state"
}
```

### 2. the template's topology questions, grouped

```
python next_product_question.py state.json --grouped --markdown
```

exit 0

```
### topology domains (6)

| ID | question | options | recommended | why it matters |
|---|---|---|---|---|
| UNK-901 | AUTH topology: Does the product have user accounts (sign-up, sign-in, sessions)? | OPT-AUTH-ON: Yes: the product has AUTH behaviour.<br>OPT-AUTH-OFF: No: the product has no AUTH behaviour. | — | Accounts bring registration, login, session expiry, recovery and revocation decisions (GRILL-AUTH-1). Replace this placeholder question with the product's own wording, or answer it from the brief. |
| UNK-902 | MONEY topology: Does the product take, hold, refund or display money (prices, payments, refunds)? | OPT-MONEY-ON: Yes: the product has MONEY behaviour.<br>OPT-MONEY-OFF: No: the product has no MONEY behaviour. | — | Money brings currency, price authority, tax, payment failure, refund and settlement decisions (GRILL-MONEY-1). Replace this placeholder question with the product's own wording, or answer it from the brief. |
| UNK-903 | FILE_UPLOAD topology: Can users upload files (images, documents, attachments)? | OPT-UPLOAD-ON: Yes: the product has FILE_UPLOAD behaviour.<br>OPT-UPLOAD-OFF: No: the product has no FILE_UPLOAD behaviour. | — | Uploads bring type, size, quota, malware, retention and ownership decisions (GRILL-FILE-UPLOAD-1). Replace this placeholder question with the product's own wording, or answer it from the brief. |
| UNK-904 | ASYNC topology: Does any result arrive later than the request (callbacks, background jobs, polling, queued work)? | OPT-ASYNC-ON: Yes: the product has ASYNC behaviour.<br>OPT-ASYNC-OFF: No: the product has no ASYNC behaviour. | — | Deferred results bring timeout, retry, idempotency, duplicate execution and reconciliation decisions (GRILL-ASYNC-1). Replace this placeholder question with the product's own wording, or answer it from the brief. |
| UNK-905 | PERMISSION topology: Do different roles or owners see or do different things? | OPT-PERM-ON: Yes: the product has PERMISSION behaviour.<br>OPT-PERM-OFF: No: the product has no PERMISSION behaviour. | — | Roles bring role, resource ownership, delegation and denial decisions (GRILL-PERMISSION-1). Replace this placeholder question with the product's own wording, or answer it from the brief. |
| UNK-906 | DESTRUCTIVE_ACTION topology: Can a user delete, cancel or overwrite something that is hard to undo? | OPT-DESTR-ON: Yes: the product has DESTRUCTIVE_ACTION behaviour.<br>OPT-DESTR-OFF: No: the product has no DESTRUCTIVE_ACTION behaviour. | — | Destructive actions bring confirmation, undo, cascade and audit decisions (GRILL-DESTRUCTIVE-ACTION-1). Replace this placeholder question with the product's own wording, or answer it from the brief. |
```

### 3. the brief as evidence

```
python new_records.py --state state.json --patch rev2-patch.json evidence --id EVD-001 --source-kind USER_CONFIRMED_INTENT --class INTENT --locator 'chat (walk-through brief)' --claim '비회원 한 명이 한 품목을 바로 결제하는 단일 상품 판매 페이지.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "EVD-001"
  ],
  "cells": [],
  "rows": []
}
```

### 4. resolve the topology question UNK-902 = OPT-MONEY-ON (mode derived)

```
python new_records.py --state state.json --patch rev2-patch.json resolve UNK-902 --option OPT-MONEY-ON --words '결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "DEC-001"
  ],
  "changed": [
    "UNK-902"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-902",
      "option": "OPT-MONEY-ON",
      "decision": "DEC-001",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE and risk flags ['money']"
    }
  ],
  "notes": []
}
```

### 5. resolve the topology question UNK-901 = OPT-AUTH-OFF (mode derived)

```
python new_records.py --state state.json --patch rev2-patch.json resolve UNK-901 --option OPT-AUTH-OFF --words '결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "DEC-002"
  ],
  "changed": [
    "UNK-901"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-901",
      "option": "OPT-AUTH-OFF",
      "decision": "DEC-002",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE and risk flags ['security']"
    }
  ],
  "notes": []
}
```

### 6. resolve the topology question UNK-903 = OPT-UPLOAD-OFF (mode derived)

```
python new_records.py --state state.json --patch rev2-patch.json resolve UNK-903 --option OPT-UPLOAD-OFF --words '결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "DEC-003"
  ],
  "changed": [
    "UNK-903"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-903",
      "option": "OPT-UPLOAD-OFF",
      "decision": "DEC-003",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE"
    }
  ],
  "notes": []
}
```

### 7. resolve the topology question UNK-904 = OPT-ASYNC-OFF (mode derived)

```
python new_records.py --state state.json --patch rev2-patch.json resolve UNK-904 --option OPT-ASYNC-OFF --words '결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "DEC-004"
  ],
  "changed": [
    "UNK-904"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-904",
      "option": "OPT-ASYNC-OFF",
      "decision": "DEC-004",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE"
    }
  ],
  "notes": []
}
```

### 8. resolve the topology question UNK-905 = OPT-PERM-OFF (mode derived)

```
python new_records.py --state state.json --patch rev2-patch.json resolve UNK-905 --option OPT-PERM-OFF --words '결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "DEC-005"
  ],
  "changed": [
    "UNK-905"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-905",
      "option": "OPT-PERM-OFF",
      "decision": "DEC-005",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE and risk flags ['security']"
    }
  ],
  "notes": []
}
```

### 9. resolve the topology question UNK-906 = OPT-DESTR-OFF (mode derived)

```
python new_records.py --state state.json --patch rev2-patch.json resolve UNK-906 --option OPT-DESTR-OFF --words '결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "DEC-006"
  ],
  "changed": [
    "UNK-906"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-906",
      "option": "OPT-DESTR-OFF",
      "decision": "DEC-006",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE and risk flags ['destructive']"
    }
  ],
  "notes": []
}
```

### 10. MONEY on: MONEY_FLOW surface, GRILL-MONEY-1 row with digest, 12 OPEN axis questions

```
python new_records.py --state state.json --patch rev2-patch.json topology-on DEC-001 --new-surface SURF-001 --name '결제'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [
    "SURF-001",
    "UNK-001",
    "UNK-002",
    "UNK-003",
    "UNK-004",
    "UNK-005",
    "UNK-006",
    "UNK-007",
    "UNK-008",
    "UNK-009",
    "UNK-010",
    "UNK-011",
    "UNK-012"
  ],
  "changed": [],
  "replaced": [],
  "cells": [],
  "rows": [
    "grill_coverage[SURF-001]"
  ],
  "grill_profile": [
    "MONEY"
  ],
  "derived": [],
  "notes": [
    "12 axis questions are skeletons (two generic options, no recommendation): rewrite each with new_records.py --replace question --unknown ID --pack GRILL-MONEY-1 --axis AXIS --surface TARGET … before asking; next_product_question.py --grouped lists them as one table"
  ],
  "next_steps": [
    "DEC-001 is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority"
  ]
}
```

### 11. AUTH off

```
python new_records.py --state state.json --patch rev2-patch.json topology-off DEC-002 --rationale '사용자 답(DEC-001~006): 이 제품에는 AUTH 동작이 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [],
  "changed": [],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [
    "AUTH"
  ],
  "derived": [],
  "notes": [],
  "next_steps": [
    "DEC-002 is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority"
  ]
}
```

### 12. FILE_UPLOAD off

```
python new_records.py --state state.json --patch rev2-patch.json topology-off DEC-003 --rationale '사용자 답(DEC-001~006): 이 제품에는 FILE_UPLOAD 동작이 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [],
  "changed": [],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [
    "FILE_UPLOAD"
  ],
  "derived": [],
  "notes": [],
  "next_steps": [
    "DEC-003 is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority"
  ]
}
```

### 13. ASYNC off

```
python new_records.py --state state.json --patch rev2-patch.json topology-off DEC-004 --rationale '사용자 답(DEC-001~006): 이 제품에는 ASYNC 동작이 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [],
  "changed": [],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [
    "ASYNC"
  ],
  "derived": [],
  "notes": [],
  "next_steps": [
    "DEC-004 is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority"
  ]
}
```

### 14. PERMISSION off

```
python new_records.py --state state.json --patch rev2-patch.json topology-off DEC-005 --rationale '사용자 답(DEC-001~006): 이 제품에는 PERMISSION 동작이 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [],
  "changed": [],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [
    "PERMISSION"
  ],
  "derived": [],
  "notes": [],
  "next_steps": [
    "DEC-005 is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority"
  ]
}
```

### 15. DESTRUCTIVE_ACTION off

```
python new_records.py --state state.json --patch rev2-patch.json topology-off DEC-006 --rationale '사용자 답(DEC-001~006): 이 제품에는 DESTRUCTIVE_ACTION 동작이 없다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev2-patch.json",
  "added": [],
  "changed": [],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [
    "DESTRUCTIVE_ACTION"
  ],
  "derived": [],
  "notes": [],
  "next_steps": [
    "DEC-006 is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority"
  ]
}
```

### 16. rev2 (OPEN)

```
python open_revision.py state.json --patch rev2-patch.json --status OPEN --write
```

exit 0

```
{
  "added": [
    "EVD-001",
    "UNK-001",
    "UNK-002",
    "UNK-003",
    "UNK-004",
    "UNK-005",
    "UNK-006",
    "UNK-007",
    "UNK-008",
    "UNK-009",
    "UNK-010",
    "UNK-011",
    "UNK-012",
    "DEC-001",
    "DEC-002",
    "DEC-003",
    "DEC-004",
    "DEC-005",
    "DEC-006",
    "SURF-001"
  ],
  "cells": [],
  "changed": [
    "UNK-902",
    "UNK-901",
    "UNK-903",
    "UNK-904",
    "UNK-905",
    "UNK-906"
  ],
  "from_revision": 1,
  "grill_profile": [
    "MONEY",
    "AUTH",
    "FILE_UPLOAD",
    "ASYNC",
    "PERMISSION",
    "DESTRUCTIVE_ACTION"
  ],
  "refreshed": [],
  "rows": [
    "grill_coverage[SURF-001]"
  ],
  "status": "OPEN",
  "to_revision": 2,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "warning": "revision 1 was never approved; its changes will reach the user only inside the next Approval Manifest",
  "written": true
}
```

### 17. 12 skeleton axis questions, one group

```
python next_product_question.py state.json --grouped --markdown
```

exit 0

```
### GRILL-MONEY-1 · SURF-001 (12)

| ID | question | options | recommended | why it matters |
|---|---|---|---|---|
| UNK-001 | MONEY · currency: Currency selection, display, and conversion policy — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 currency 동작을 정한다: Currency selection, display, and conversion policy.<br>OPT-NOT-APPLICABLE: 이 제품에는 currency 동작이 없다. | — | GRILL-MONEY-1 축 currency는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-002 | MONEY · price_authority: Canonical authority for prices and price changes — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 price_authority 동작을 정한다: Canonical authority for prices and price changes.<br>OPT-NOT-APPLICABLE: 이 제품에는 price_authority 동작이 없다. | — | GRILL-MONEY-1 축 price_authority는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-003 | MONEY · tax: Tax calculation and presentation policy — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 tax 동작을 정한다: Tax calculation and presentation policy.<br>OPT-NOT-APPLICABLE: 이 제품에는 tax 동작이 없다. | — | GRILL-MONEY-1 축 tax는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-004 | MONEY · discount: Discount eligibility and application behavior — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 discount 동작을 정한다: Discount eligibility and application behavior.<br>OPT-NOT-APPLICABLE: 이 제품에는 discount 동작이 없다. | — | GRILL-MONEY-1 축 discount는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-005 | MONEY · payment_failure: Payment failure behavior and recovery — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 payment_failure 동작을 정한다: Payment failure behavior and recovery.<br>OPT-NOT-APPLICABLE: 이 제품에는 payment_failure 동작이 없다. | — | GRILL-MONEY-1 축 payment_failure는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-006 | MONEY · duplicate_payment: Duplicate payment prevention and remediation — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 duplicate_payment 동작을 정한다: Duplicate payment prevention and remediation.<br>OPT-NOT-APPLICABLE: 이 제품에는 duplicate_payment 동작이 없다. | — | GRILL-MONEY-1 축 duplicate_payment는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-007 | MONEY · refund: Full refund eligibility and execution policy — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 refund 동작을 정한다: Full refund eligibility and execution policy.<br>OPT-NOT-APPLICABLE: 이 제품에는 refund 동작이 없다. | — | GRILL-MONEY-1 축 refund는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-008 | MONEY · partial_refund: Partial refund eligibility and allocation policy — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 partial_refund 동작을 정한다: Partial refund eligibility and allocation policy.<br>OPT-NOT-APPLICABLE: 이 제품에는 partial_refund 동작이 없다. | — | GRILL-MONEY-1 축 partial_refund는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-009 | MONEY · cancellation: Cancellation policy and monetary effects — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 cancellation 동작을 정한다: Cancellation policy and monetary effects.<br>OPT-NOT-APPLICABLE: 이 제품에는 cancellation 동작이 없다. | — | GRILL-MONEY-1 축 cancellation는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-010 | MONEY · chargeback: Chargeback handling and account effects — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 chargeback 동작을 정한다: Chargeback handling and account effects.<br>OPT-NOT-APPLICABLE: 이 제품에는 chargeback 동작이 없다. | — | GRILL-MONEY-1 축 chargeback는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-011 | MONEY · settlement: Settlement timing, status, and reconciliation policy — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 settlement 동작을 정한다: Settlement timing, status, and reconciliation policy.<br>OPT-NOT-APPLICABLE: 이 제품에는 settlement 동작이 없다. | — | GRILL-MONEY-1 축 settlement는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
| UNK-012 | MONEY · receipt: Receipt contents, delivery, and retention policy — 이 제품은 어떻게 하는가? | OPT-SPECIFY: 이 제품은 receipt 동작을 정한다: Receipt contents, delivery, and retention policy.<br>OPT-NOT-APPLICABLE: 이 제품에는 receipt 동작이 없다. | — | GRILL-MONEY-1 축 receipt는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다. |
```

### 18. rewrite the currency skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-001 --pack GRILL-MONEY-1 --axis currency --surface SURF-001 --question 'currency: KRW 단일 통화인가, 다른 통화 표시 전환인가?' --why '결제 화면과 주문 기록의 currency 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=KRW 단일 통화|KRW 단일 통화로 구현한다.' --option 'OPT-B=다른 통화 표시 전환|다른 통화 표시 전환로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '다른 통화 표시 전환는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-001"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-001": "USER_DECISION_REQUIRED"
  }
}
```

### 19. rewrite the price_authority skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-002 --pack GRILL-MONEY-1 --axis price_authority --surface SURF-001 --question 'price_authority: 서버가 주문 시 가격을 다시 계산인가, 화면 가격을 그대로 사용인가?' --why '결제 화면과 주문 기록의 price_authority 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=서버가 주문 시 가격을 다시 계산|서버가 주문 시 가격을 다시 계산로 구현한다.' --option 'OPT-B=화면 가격을 그대로 사용|화면 가격을 그대로 사용로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '화면 가격을 그대로 사용는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-002"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-002": "USER_DECISION_REQUIRED"
  }
}
```

### 20. rewrite the tax skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-003 --pack GRILL-MONEY-1 --axis tax --surface SURF-001 --question 'tax: 부가세 포함가 표시인가, 부가세 별도 표시인가?' --why '결제 화면과 주문 기록의 tax 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=부가세 포함가 표시|부가세 포함가 표시로 구현한다.' --option 'OPT-B=부가세 별도 표시|부가세 별도 표시로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '부가세 별도 표시는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-003"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-003": "USER_DECISION_REQUIRED"
  }
}
```

### 21. rewrite the discount skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-004 --pack GRILL-MONEY-1 --axis discount --surface SURF-001 --question 'discount: 할인 없음인가, 쿠폰 입력란인가?' --why '결제 화면과 주문 기록의 discount 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=할인 없음|할인 없음로 구현한다.' --option 'OPT-B=쿠폰 입력란|쿠폰 입력란로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '쿠폰 입력란는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-004"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-004": "USER_DECISION_REQUIRED"
  }
}
```

### 22. rewrite the payment_failure skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-005 --pack GRILL-MONEY-1 --axis payment_failure --surface SURF-001 --question 'payment_failure: 실패 안내와 다시 결제인가, 주문 자동 취소인가?' --why '결제 화면과 주문 기록의 payment_failure 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=실패 안내와 다시 결제|실패 안내와 다시 결제로 구현한다.' --option 'OPT-B=주문 자동 취소|주문 자동 취소로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '주문 자동 취소는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-005"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-005": "USER_DECISION_REQUIRED"
  }
}
```

### 23. rewrite the duplicate_payment skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-006 --pack GRILL-MONEY-1 --axis duplicate_payment --surface SURF-001 --question 'duplicate_payment: 주문별 결제 키로 한 번만 승인인가, 검사 없음인가?' --why '결제 화면과 주문 기록의 duplicate_payment 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=주문별 결제 키로 한 번만 승인|주문별 결제 키로 한 번만 승인로 구현한다.' --option 'OPT-B=검사 없음|검사 없음로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '검사 없음는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-006"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-006": "USER_DECISION_REQUIRED"
  }
}
```

### 24. rewrite the refund skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-007 --pack GRILL-MONEY-1 --axis refund --surface SURF-001 --question 'refund: 운영자가 전액 환불인가, 환불 없음인가?' --why '결제 화면과 주문 기록의 refund 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=운영자가 전액 환불|운영자가 전액 환불로 구현한다.' --option 'OPT-B=환불 없음|환불 없음로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '환불 없음는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-007"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-007": "USER_DECISION_REQUIRED"
  }
}
```

### 25. rewrite the partial_refund skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-008 --pack GRILL-MONEY-1 --axis partial_refund --surface SURF-001 --question 'partial_refund: 부분 환불 없음인가, 품목 단위 부분 환불인가?' --why '결제 화면과 주문 기록의 partial_refund 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=부분 환불 없음|부분 환불 없음로 구현한다.' --option 'OPT-B=품목 단위 부분 환불|품목 단위 부분 환불로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '품목 단위 부분 환불는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-008"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-008": "USER_DECISION_REQUIRED"
  }
}
```

### 26. rewrite the cancellation skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-009 --pack GRILL-MONEY-1 --axis cancellation --surface SURF-001 --question 'cancellation: 결제 전에만 취소인가, 언제든 취소인가?' --why '결제 화면과 주문 기록의 cancellation 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=결제 전에만 취소|결제 전에만 취소로 구현한다.' --option 'OPT-B=언제든 취소|언제든 취소로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '언제든 취소는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-009"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-009": "USER_DECISION_REQUIRED"
  }
}
```

### 27. rewrite the chargeback skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-010 --pack GRILL-MONEY-1 --axis chargeback --surface SURF-001 --question 'chargeback: 지급 거절은 이력에 기록인가, 무시인가?' --why '결제 화면과 주문 기록의 chargeback 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=지급 거절은 이력에 기록|지급 거절은 이력에 기록로 구현한다.' --option 'OPT-B=무시|무시로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '무시는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-010"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-010": "USER_DECISION_REQUIRED"
  }
}
```

### 28. rewrite the settlement skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-011 --pack GRILL-MONEY-1 --axis settlement --surface SURF-001 --question 'settlement: 정산은 PG 화면에서 확인인가, 사이트 안 정산 화면인가?' --why '결제 화면과 주문 기록의 settlement 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=정산은 PG 화면에서 확인|정산은 PG 화면에서 확인로 구현한다.' --option 'OPT-B=사이트 안 정산 화면|사이트 안 정산 화면로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '사이트 안 정산 화면는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-011"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-011": "USER_DECISION_REQUIRED"
  }
}
```

### 29. rewrite the receipt skeleton in product terms (same ID)

```
python new_records.py --state state.json --patch rev3-patch.json --replace question --unknown UNK-012 --pack GRILL-MONEY-1 --axis receipt --surface SURF-001 --question 'receipt: 영수증 메일인가, 영수증 없음인가?' --why '결제 화면과 주문 기록의 receipt 동작이 정해진다.' --category SECONDARY_BEHAVIOR --affects SURF-001 --option 'OPT-A=영수증 메일|영수증 메일로 구현한다.' --option 'OPT-B=영수증 없음|영수증 없음로 구현한다.' --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --recommend OPT-A --reason EVD-001 --tradeoff '영수증 없음는 이번 범위에서 빠진다.'
```

exit 0

```
{
  "written": true,
  "patch": "rev3-patch.json",
  "added": [
    "UNK-012"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-012": "USER_DECISION_REQUIRED"
  }
}
```

### 30. rev3 (OPEN): questions ready to ask

```
python open_revision.py state.json --patch rev3-patch.json --status OPEN --write
```

exit 0

```
{
  "added": [],
  "cells": [],
  "changed": [
    "UNK-001",
    "UNK-002",
    "UNK-003",
    "UNK-004",
    "UNK-005",
    "UNK-006",
    "UNK-007",
    "UNK-008",
    "UNK-009",
    "UNK-010",
    "UNK-011",
    "UNK-012"
  ],
  "from_revision": 2,
  "refreshed": [],
  "status": "OPEN",
  "to_revision": 3,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "warning": "revision 2 was never approved; its changes will reach the user only inside the next Approval Manifest",
  "written": true
}
```

### 31. the recommendation table shown to the user

```
python next_product_question.py state.json --grouped --markdown
```

exit 0

```
### GRILL-MONEY-1 · SURF-001 (12)

| ID | question | options | recommended | why it matters |
|---|---|---|---|---|
| UNK-001 | currency: KRW 단일 통화인가, 다른 통화 표시 전환인가? | OPT-A: KRW 단일 통화<br>OPT-B: 다른 통화 표시 전환 | OPT-A (HIGH; 다른 통화 표시 전환는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 currency 동작이 정해진다. |
| UNK-002 | price_authority: 서버가 주문 시 가격을 다시 계산인가, 화면 가격을 그대로 사용인가? | OPT-A: 서버가 주문 시 가격을 다시 계산<br>OPT-B: 화면 가격을 그대로 사용 | OPT-A (HIGH; 화면 가격을 그대로 사용는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 price_authority 동작이 정해진다. |
| UNK-003 | tax: 부가세 포함가 표시인가, 부가세 별도 표시인가? | OPT-A: 부가세 포함가 표시<br>OPT-B: 부가세 별도 표시 | OPT-A (HIGH; 부가세 별도 표시는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 tax 동작이 정해진다. |
| UNK-004 | discount: 할인 없음인가, 쿠폰 입력란인가? | OPT-A: 할인 없음<br>OPT-B: 쿠폰 입력란 | OPT-A (HIGH; 쿠폰 입력란는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 discount 동작이 정해진다. |
| UNK-005 | payment_failure: 실패 안내와 다시 결제인가, 주문 자동 취소인가? | OPT-A: 실패 안내와 다시 결제<br>OPT-B: 주문 자동 취소 | OPT-A (HIGH; 주문 자동 취소는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 payment_failure 동작이 정해진다. |
| UNK-006 | duplicate_payment: 주문별 결제 키로 한 번만 승인인가, 검사 없음인가? | OPT-A: 주문별 결제 키로 한 번만 승인<br>OPT-B: 검사 없음 | OPT-A (HIGH; 검사 없음는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 duplicate_payment 동작이 정해진다. |
| UNK-007 | refund: 운영자가 전액 환불인가, 환불 없음인가? | OPT-A: 운영자가 전액 환불<br>OPT-B: 환불 없음 | OPT-A (HIGH; 환불 없음는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 refund 동작이 정해진다. |
| UNK-008 | partial_refund: 부분 환불 없음인가, 품목 단위 부분 환불인가? | OPT-A: 부분 환불 없음<br>OPT-B: 품목 단위 부분 환불 | OPT-A (HIGH; 품목 단위 부분 환불는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 partial_refund 동작이 정해진다. |
| UNK-009 | cancellation: 결제 전에만 취소인가, 언제든 취소인가? | OPT-A: 결제 전에만 취소<br>OPT-B: 언제든 취소 | OPT-A (HIGH; 언제든 취소는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 cancellation 동작이 정해진다. |
| UNK-010 | chargeback: 지급 거절은 이력에 기록인가, 무시인가? | OPT-A: 지급 거절은 이력에 기록<br>OPT-B: 무시 | OPT-A (HIGH; 무시는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 chargeback 동작이 정해진다. |
| UNK-011 | settlement: 정산은 PG 화면에서 확인인가, 사이트 안 정산 화면인가? | OPT-A: 정산은 PG 화면에서 확인<br>OPT-B: 사이트 안 정산 화면 | OPT-A (HIGH; 사이트 안 정산 화면는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 settlement 동작이 정해진다. |
| UNK-012 | receipt: 영수증 메일인가, 영수증 없음인가? | OPT-A: 영수증 메일<br>OPT-B: 영수증 없음 | OPT-A (HIGH; 영수증 없음는 이번 범위에서 빠진다.) | 결제 화면과 주문 기록의 receipt 동작이 정해진다. |

All as recommended: `new_records.py --state STATE --patch PATCH resolve --accept-recommended --pack GRILL-MONEY-1 --surface SURF-001 --words "<the user's words>"`
```

### 32. the same groups as JSON

```
python next_product_question.py state.json --grouped
```

exit 0

```
{
  "groups": [
    {
      "all_recommended": true,
      "count": 12,
      "group": "pack",
      "pack_id": "GRILL-MONEY-1",
      "present_as_one_table": true,
      "questions": [
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "currency",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "KRW 단일 통화로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "KRW 단일 통화"
            },
            {
              "consequences": [
                "다른 통화 표시 전환로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "다른 통화 표시 전환"
            }
          ],
          "question": "currency: KRW 단일 통화인가, 다른 통화 표시 전환인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "다른 통화 표시 전환는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-001",
          "why_it_matters": "결제 화면과 주문 기록의 currency 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "price_authority",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "서버가 주문 시 가격을 다시 계산로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "서버가 주문 시 가격을 다시 계산"
            },
            {
              "consequences": [
                "화면 가격을 그대로 사용로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "화면 가격을 그대로 사용"
            }
          ],
          "question": "price_authority: 서버가 주문 시 가격을 다시 계산인가, 화면 가격을 그대로 사용인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "화면 가격을 그대로 사용는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-002",
          "why_it_matters": "결제 화면과 주문 기록의 price_authority 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "tax",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "부가세 포함가 표시로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "부가세 포함가 표시"
            },
            {
              "consequences": [
                "부가세 별도 표시로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "부가세 별도 표시"
            }
          ],
          "question": "tax: 부가세 포함가 표시인가, 부가세 별도 표시인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "부가세 별도 표시는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-003",
          "why_it_matters": "결제 화면과 주문 기록의 tax 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "discount",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "할인 없음로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "할인 없음"
            },
            {
              "consequences": [
                "쿠폰 입력란로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "쿠폰 입력란"
            }
          ],
          "question": "discount: 할인 없음인가, 쿠폰 입력란인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "쿠폰 입력란는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-004",
          "why_it_matters": "결제 화면과 주문 기록의 discount 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "payment_failure",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "실패 안내와 다시 결제로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "실패 안내와 다시 결제"
            },
            {
              "consequences": [
                "주문 자동 취소로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "주문 자동 취소"
            }
          ],
          "question": "payment_failure: 실패 안내와 다시 결제인가, 주문 자동 취소인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "주문 자동 취소는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-005",
          "why_it_matters": "결제 화면과 주문 기록의 payment_failure 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "duplicate_payment",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "주문별 결제 키로 한 번만 승인로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "주문별 결제 키로 한 번만 승인"
            },
            {
              "consequences": [
                "검사 없음로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "검사 없음"
            }
          ],
          "question": "duplicate_payment: 주문별 결제 키로 한 번만 승인인가, 검사 없음인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "검사 없음는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-006",
          "why_it_matters": "결제 화면과 주문 기록의 duplicate_payment 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "refund",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "운영자가 전액 환불로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "운영자가 전액 환불"
            },
            {
              "consequences": [
                "환불 없음로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "환불 없음"
            }
          ],
          "question": "refund: 운영자가 전액 환불인가, 환불 없음인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "환불 없음는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-007",
          "why_it_matters": "결제 화면과 주문 기록의 refund 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "partial_refund",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "부분 환불 없음로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "부분 환불 없음"
            },
            {
              "consequences": [
                "품목 단위 부분 환불로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "품목 단위 부분 환불"
            }
          ],
          "question": "partial_refund: 부분 환불 없음인가, 품목 단위 부분 환불인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "품목 단위 부분 환불는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-008",
          "why_it_matters": "결제 화면과 주문 기록의 partial_refund 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "cancellation",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "결제 전에만 취소로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "결제 전에만 취소"
            },
            {
              "consequences": [
                "언제든 취소로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "언제든 취소"
            }
          ],
          "question": "cancellation: 결제 전에만 취소인가, 언제든 취소인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "언제든 취소는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-009",
          "why_it_matters": "결제 화면과 주문 기록의 cancellation 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "chargeback",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "지급 거절은 이력에 기록로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "지급 거절은 이력에 기록"
            },
            {
              "consequences": [
                "무시로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "무시"
            }
          ],
          "question": "chargeback: 지급 거절은 이력에 기록인가, 무시인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "무시는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-010",
          "why_it_matters": "결제 화면과 주문 기록의 chargeback 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "settlement",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "정산은 PG 화면에서 확인로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "정산은 PG 화면에서 확인"
            },
            {
              "consequences": [
                "사이트 안 정산 화면로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "사이트 안 정산 화면"
            }
          ],
          "question": "settlement: 정산은 PG 화면에서 확인인가, 사이트 안 정산 화면인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "사이트 안 정산 화면는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-011",
          "why_it_matters": "결제 화면과 주문 기록의 settlement 동작이 정해진다."
        },
        {
          "affected_ids": [
            "SURF-001"
          ],
          "axis_id": "receipt",
          "blocked_by": [],
          "blocks": [],
          "confidence": "HIGH",
          "decision_authority": "USER_DECISION_REQUIRED",
          "evidence_refs": [],
          "options": [
            {
              "consequences": [
                "영수증 메일로 구현한다."
              ],
              "id": "OPT-A",
              "statement": "영수증 메일"
            },
            {
              "consequences": [
                "영수증 없음로 구현한다."
              ],
              "id": "OPT-B",
              "statement": "영수증 없음"
            }
          ],
          "question": "receipt: 영수증 메일인가, 영수증 없음인가?",
          "recommendation": {
            "confidence": "HIGH",
            "reasoning_refs": [
              "EVD-001"
            ],
            "recommended_option": "OPT-A",
            "tradeoffs": [
              "영수증 없음는 이번 범위에서 빠진다."
            ]
          },
          "recommended_option": "OPT-A",
          "response_mode": "MUTUALLY_EXCLUSIVE",
          "unknown_id": "UNK-012",
          "why_it_matters": "결제 화면과 주문 기록의 receipt 동작이 정해진다."
        }
      ],
      "record_all_as_recommended": "new_records.py --state STATE --patch PATCH resolve --accept-recommended --pack GRILL-MONEY-1 --surface SURF-001 --words \"<the user's words>\"",
      "surface": "SURF-001"
    }
  ],
  "open_questions": 12
}
```

### 33. the user answers the table: all as recommended

```
python new_records.py --state state.json --patch rev4-patch.json resolve --accept-recommended --pack GRILL-MONEY-1 --surface SURF-001 --words '전부 추천대로'
```

exit 0

```
{
  "written": true,
  "patch": "rev4-patch.json",
  "added": [
    "DEC-007",
    "DEC-008",
    "DEC-009",
    "DEC-010",
    "DEC-011",
    "DEC-012",
    "DEC-013",
    "DEC-014",
    "DEC-015",
    "DEC-016",
    "DEC-017",
    "DEC-018"
  ],
  "changed": [
    "UNK-001",
    "SURF-001",
    "UNK-002",
    "UNK-003",
    "UNK-004",
    "UNK-005",
    "UNK-006",
    "UNK-007",
    "UNK-008",
    "UNK-009",
    "UNK-010",
    "UNK-011",
    "UNK-012"
  ],
  "replaced": [],
  "cells": [
    "grill_coverage[GRILL-MONEY-1].axes.currency",
    "grill_coverage[GRILL-MONEY-1].axes.price_authority",
    "grill_coverage[GRILL-MONEY-1].axes.tax",
    "grill_coverage[GRILL-MONEY-1].axes.discount",
    "grill_coverage[GRILL-MONEY-1].axes.payment_failure",
    "grill_coverage[GRILL-MONEY-1].axes.duplicate_payment",
    "grill_coverage[GRILL-MONEY-1].axes.refund",
    "grill_coverage[GRILL-MONEY-1].axes.partial_refund",
    "grill_coverage[GRILL-MONEY-1].axes.cancellation",
    "grill_coverage[GRILL-MONEY-1].axes.chargeback",
    "grill_coverage[GRILL-MONEY-1].axes.settlement",
    "grill_coverage[GRILL-MONEY-1].axes.receipt"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-001",
      "option": "OPT-A",
      "decision": "DEC-007",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-002",
      "option": "OPT-A",
      "decision": "DEC-008",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-003",
      "option": "OPT-A",
      "decision": "DEC-009",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-004",
      "option": "OPT-A",
      "decision": "DEC-010",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-005",
      "option": "OPT-A",
      "decision": "DEC-011",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-006",
      "option": "OPT-A",
      "decision": "DEC-012",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-007",
      "option": "OPT-A",
      "decision": "DEC-013",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-008",
      "option": "OPT-A",
      "decision": "DEC-014",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-009",
      "option": "OPT-A",
      "decision": "DEC-015",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-010",
      "option": "OPT-A",
      "decision": "DEC-016",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-011",
      "option": "OPT-A",
      "decision": "DEC-017",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    },
    {
      "unknown": "UNK-012",
      "option": "OPT-A",
      "decision": "DEC-018",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-MONEY-1].axes.currency: answered by DEC-007",
    "grill_coverage[GRILL-MONEY-1].axes.price_authority: answered by DEC-008",
    "grill_coverage[GRILL-MONEY-1].axes.tax: answered by DEC-009",
    "grill_coverage[GRILL-MONEY-1].axes.discount: answered by DEC-010",
    "grill_coverage[GRILL-MONEY-1].axes.payment_failure: answered by DEC-011",
    "grill_coverage[GRILL-MONEY-1].axes.duplicate_payment: answered by DEC-012",
    "grill_coverage[GRILL-MONEY-1].axes.refund: answered by DEC-013",
    "grill_coverage[GRILL-MONEY-1].axes.partial_refund: answered by DEC-014",
    "grill_coverage[GRILL-MONEY-1].axes.cancellation: answered by DEC-015",
    "grill_coverage[GRILL-MONEY-1].axes.chargeback: answered by DEC-016",
    "grill_coverage[GRILL-MONEY-1].axes.settlement: answered by DEC-017",
    "grill_coverage[GRILL-MONEY-1].axes.receipt: answered by DEC-018"
  ],
  "surfaces_left_without_open_question": [
    {
      "surface": "SURF-001",
      "decision_refs": [
        "DEC-001",
        "DEC-007",
        "DEC-008",
        "DEC-009",
        "DEC-010",
        "DEC-011",
        "DEC-012",
        "DEC-013",
        "DEC-014",
        "DEC-015",
        "DEC-016",
        "DEC-017",
        "DEC-018"
      ],
      "next": "new_records.py --state STATE --patch PATCH requirement --from-decisions DEC-001,DEC-007,DEC-008,DEC-009,DEC-010,DEC-011,DEC-012,DEC-013,DEC-014,DEC-015,DEC-016,DEC-017,DEC-018 --surface SURF-001 --requirement REQ-001",
      "why": "an OPEN material surface needs an OPEN question (OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN); with every question answered, a requirement drafted from its decisions is its authority and the surface becomes IN_SCOPE"
    }
  ]
}
```

### 34. the surface has no open question left: requirement from its decisions

```
python new_records.py --state state.json --patch rev4-patch.json requirement --from-decisions DEC-007,DEC-008,DEC-009,DEC-010,DEC-011,DEC-012,DEC-013,DEC-014,DEC-015,DEC-016,DEC-017,DEC-018 --surface SURF-001 --requirement REQ-001 --ui-required false
```

exit 0

```
{
  "written": true,
  "patch": "rev4-patch.json",
  "added": [
    "REQ-001"
  ],
  "changed": [],
  "replaced": [
    "SURF-001"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "SURF-001: IN_SCOPE with REQ-001 as authority; the statement is a draft joined from ['DEC-007', 'DEC-008', 'DEC-009', 'DEC-010', 'DEC-011', 'DEC-012', 'DEC-013', 'DEC-014', 'DEC-015', 'DEC-016', 'DEC-017', 'DEC-018'] — edit it to read as one requirement (new_records.py edit REQ-001 --set /statement ...)"
  ],
  "next_steps": [
    "REQ-001 is MATERIAL: FREEZE needs its Core coverage row (draft_freeze.py)"
  ]
}
```

### 35. the drafted statement edited into one requirement

```
python new_records.py --state state.json --patch rev4-patch.json edit REQ-001 --set /statement '구매자는 KRW 포함가로 한 품목을 결제하고, 서버 재계산 가격과 주문별 결제 키로 한 번만 승인되며, 실패하면 다시 결제한다(DEC-007~DEC-018).'
```

exit 0

```
{
  "written": true,
  "patch": "rev4-patch.json",
  "added": [],
  "changed": [],
  "replaced": [
    "REQ-001"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "REQ-001: changed ['/statement']"
  ]
}
```

### FREEZE fragment

GOAL-001, USR-001, RULE-001, AC-001, TASK-001 and the REQ-001 Core row (its boundary cell binds the six topology decisions) are added to rev4-patch.json by hand (no 2.0.2 builder writes RULE/AC/TASK records).

### 36. rev4 READY_FOR_REVIEW

```
python open_revision.py state.json --patch rev4-patch.json --status READY_FOR_REVIEW --write
```

exit 0

```
{
  "added": [
    "DEC-007",
    "DEC-008",
    "DEC-009",
    "DEC-010",
    "DEC-011",
    "DEC-012",
    "DEC-013",
    "DEC-014",
    "DEC-015",
    "DEC-016",
    "DEC-017",
    "DEC-018",
    "REQ-001",
    "GOAL-001",
    "USR-001",
    "RULE-001",
    "AC-001",
    "TASK-001"
  ],
  "cells": [
    "grill_coverage[GRILL-MONEY-1].axes.currency",
    "grill_coverage[GRILL-MONEY-1].axes.price_authority",
    "grill_coverage[GRILL-MONEY-1].axes.tax",
    "grill_coverage[GRILL-MONEY-1].axes.discount",
    "grill_coverage[GRILL-MONEY-1].axes.payment_failure",
    "grill_coverage[GRILL-MONEY-1].axes.duplicate_payment",
    "grill_coverage[GRILL-MONEY-1].axes.refund",
    "grill_coverage[GRILL-MONEY-1].axes.partial_refund",
    "grill_coverage[GRILL-MONEY-1].axes.cancellation",
    "grill_coverage[GRILL-MONEY-1].axes.chargeback",
    "grill_coverage[GRILL-MONEY-1].axes.settlement",
    "grill_coverage[GRILL-MONEY-1].axes.receipt"
  ],
  "changed": [
    "UNK-001",
    "UNK-002",
    "UNK-003",
    "UNK-004",
    "UNK-005",
    "UNK-006",
    "UNK-007",
    "UNK-008",
    "UNK-009",
    "UNK-010",
    "UNK-011",
    "UNK-012",
    "SURF-001"
  ],
  "discovery_baseline": "ESTABLISHED",
  "from_revision": 3,
  "refreshed": [],
  "rows": [
    "coverage[REQ-001]"
  ],
  "status": "READY_FOR_REVIEW",
  "to_revision": 4,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "warning": "revision 3 was never approved; its changes will reach the user only inside the next Approval Manifest",
  "written": true
}
```

### 37. valid

```
python validate_state.py state.json
```

exit 0

```
{
  "errors": [],
  "valid": true,
  "validator": "state"
}
```

### 38. the Approval Manifest to show the user

```
python build_approval_manifest.py state.json
```

exit 0

```
{"approval_commitment":{"coverage_digest":"012dea4c5048f6fb824b0e95c2d3c62875a0ae7694f39be14c1bca534d68f08d","definition_digest":"0929a272dc897d81d68f2509c2cb26d14dcfa0973c01591f3c71cacfbfab3040","grill_pack_set_digest":"065490f56bf841c3c9412044b0237d762e511472b3dc600bad4fdb7d84641e41","manifest_digest":"9df0e5d21d1f4fdc5728580ad05da00035b91a729c6cc8cb5ee0c7a772c54d68","record_hashes":{"AC-001":"41ae9eea0e2e5a689b3959d3f7370a6f74dbc544febeab8d90e6e998308b744d","DEC-001":"73c18429488c16442d6697b2b2d5313e12e3597f011861e5ed2bb7d942c64b0c","DEC-002":"8146692347e68d39dd5d654ab087da19929155deb8f03a7e00a180377c4026a8","DEC-003":"19874ad018c21db0ecfc68b634692fdaa32f8953a9d3c17bf5b2267262e24c5a","DEC-004":"5f8376a3b089e3c510909ede08638a32d6a48ccd146156eab0c7f6357c99b7bb","DEC-005":"972b694606171f38f592e5bfa0c07f156d519edaff07682accdb4c27a679394d","DEC-006":"ca5e1720e9a22c7a653f657895f0a14856104dc38aea1c667212be2a44b6b244","DEC-007":"c912df6f33550d4021e8cd4b91a26a987d0b8c0dfb776d3333185fc0fadd550c","DEC-008":"900d8e1d56207ddb74d3b6b5ad690843052dcc3eedb9a14d3d3a8bbd65744ed5","DEC-009":"390fedac6fabb8bf24791ba6eca6d55fa80ea2ef3a21ba1cc4bd94f80c38bd51","DEC-010":"69700f53027e491d522d41853bd743e1063a05802b83b3421294c5ce2f39f3a0","DEC-011":"e3fccc198369a457f9201c356447b1e096d38576303dfb31cde2fe1e021238d5","DEC-012":"52f616d3b61f55dca72fcbd81d445637c008fc99098818e73f809a96b9ec6324","DEC-013":"dff3215fd1029a1df34a7df1c83f6078234931fa67693fc1418d9f3b69a6b83d","DEC-014":"1704e744c7727e98a73746e55623810a4e89c57e36857791283f9c4b71833ae1","DEC-015":"054ebbc2afc0c807682aa7b2fbfb7b38d96d1d9aa4b8aef0d2ab125f4ac069a1","DEC-016":"17652d673b66cf0803bf587374f60582b18d8aa2450b579103dc1f2d5160814d","DEC-017":"bd76fcfdf5def26f88630221b66c6b217f736bedb009007c0560054fe397f33a","DEC-018":"b36cbe23c774cef0ecd81c5bdddbc7fd105f1bb4c8a646e0cbb9a691517f8a0b","GOAL-001":"1afa1f2992ccb5485ab8de6243b596e0dd5dd0becdad34faa6215f808ef57b0a","REQ-001":"fe583e5fbcde8af09b7228e51c1edfc94d3f74325e4afa30090a25629ec7ccbc","RULE-001":"20b9b47417a19e95163430bd8f6d0e3ddca291948ba1f82512e1535329198d92","SURF-001":"7da218d99fba765456d14fb60688e60de5f63a4cfe5a17875deb34266ceaea3f","TASK-001":"1132f754b922908a81cdfb1fe0763b69b177a769301a77d80b9ba5aec523ddde","UNK-001":"21ce4525904a4c66aa785f7774196b2db836ba17cafb4cf3bcff457722247f00","UNK-002":"a54eb44183eee3b51a315b645c962eeb355000a04b42eed2cd3b0148f668efb1","UNK-003":"d82e65fc5adffe343dac2f57af5795764ccd06ec9853276603d4c35d5ac405f9","UNK-004":"f03ff6568de5ef02faac6830c10a3e404b6ed8da3372889159ebd6d7527b09f6","UNK-005":"c75be45dcc834f029487ffb5dca19399153d9cd3b670fc2d9c2351a69d3f4b12","UNK-006":"37ef6aaa596740292abb9c45581c696113ff6473dc59d72576d3d22e169e2681","UNK-007":"a760c5a138b7a8fee6c80ad0c7855efccf739bc02b7974568926971352f8fa75","UNK-008":"8c9880ff220af30422f849bebdf245554818dd8d6e7b976be04093a2b273d503","UNK-009":"43400b6922052a1226b463ef9b79f79261b616316f7d2e1bf7c3ad2947c6c07f","UNK-010":"9fc78a4f686c18694e5139eac01ffe11896b8f8a68639d355ddcfb7040723fdc","UNK-011":"63a22b35cda5d955d2b50de66044f831e47bf5df97d7aa7b82e845ceba667d0c","UNK-012":"fc8316e67224ee4e21d797f035ca8f4865fb72cbe2a188ed660f0bc68cb13f8c","UNK-901":"33278e5d0a6081b4a98270bc1083f87682245eb93a9fb08bc09e6590d16dc893","UNK-902":"cf1a660b3a9381009e185e4910cbbbdb49eefb02ae79b5598b0d38ab57df243c","UNK-903":"6a6517b70f128887da1fd788c2bcb4d12a21567c25120dbd941556bc56e84719","UNK-904":"1d42d831e739fa2996c50631fbe90bc978af775e90175c6e5a60b7f2174b6bae","UNK-905":"e7cd22e44184712b46e4702dbd049ad8bef1010aac7be44cc73c17eab49978e2","UNK-906":"7ff447921507364e2bf2091f9297039e2406fbcc5aee96ff6a63c4cad7c47831","USR-001":"637fa2499a2099b87bc8ef092f4c492b030c80d33d4d83c47ccf3e875e6a385a"},"revision":4,"surface_digest":"6ea36f8d6435c7f1217d8551940fcaa900c0c62c520cd9d712e00032a8ed68ca"},"manifest":{"active_grill_packs":[{"digest":"45b87b1d77916ae5a6e0d624b3a8452f787a7754daf18635157157c4497b951e","pack_id":"GRILL-CORE-1","target_refs":["REQ-001"],"version":"1.0"},{"digest":"ecca8f8bb878d00715f1e064e82fdf1dba3056160740160f0bd7f28834ed15b0","pack_id":"GRILL-MONEY-1","target_refs":["SURF-001"],"version":"1.0"}],"added":[{"id":"AC-001","summary":"\uac19\uc740 \uacb0\uc81c \ud0a4\uc758 \ub450 \ubc88\uc9f8 \uc2b9\uc778\uc740 \ubb34\uc2dc\ub418\uace0 \uc8fc\ubb38\uc740 \ud55c \ubc88\ub9cc \uacb0\uc81c \uc644\ub8cc\uac00 \ub41c\ub2e4.","type":"AC"},{"id":"DEC-001","summary":"Yes: the product has MONEY behaviour.","type":"DEC"},{"id":"DEC-002","summary":"No: the product has no AUTH behaviour.","type":"DEC"},{"id":"DEC-003","summary":"No: the product has no FILE_UPLOAD behaviour.","type":"DEC"},{"id":"DEC-004","summary":"No: the product has no ASYNC behaviour.","type":"DEC"},{"id":"DEC-005","summary":"No: the product has no PERMISSION behaviour.","type":"DEC"},{"id":"DEC-006","summary":"No: the product has no DESTRUCTIVE_ACTION behaviour.","type":"DEC"},{"id":"DEC-007","summary":"KRW \ub2e8\uc77c \ud1b5\ud654","type":"DEC"},{"id":"DEC-008","summary":"\uc11c\ubc84\uac00 \uc8fc\ubb38 \uc2dc \uac00\uaca9\uc744 \ub2e4\uc2dc \uacc4\uc0b0","type":"DEC"},{"id":"DEC-009","summary":"\ubd80\uac00\uc138 \ud3ec\ud568\uac00 \ud45c\uc2dc","type":"DEC"},{"id":"DEC-010","summary":"\ud560\uc778 \uc5c6\uc74c","type":"DEC"},{"id":"DEC-011","summary":"\uc2e4\ud328 \uc548\ub0b4\uc640 \ub2e4\uc2dc \uacb0\uc81c","type":"DEC"},{"id":"DEC-012","summary":"\uc8fc\ubb38\ubcc4 \uacb0\uc81c \ud0a4\ub85c \ud55c \ubc88\ub9cc \uc2b9\uc778","type":"DEC"},{"id":"DEC-013","summary":"\uc6b4\uc601\uc790\uac00 \uc804\uc561 \ud658\ubd88","type":"DEC"},{"id":"DEC-014","summary":"\ubd80\ubd84 \ud658\ubd88 \uc5c6\uc74c","type":"DEC"},{"id":"DEC-015","summary":"\uacb0\uc81c \uc804\uc5d0\ub9cc \ucde8\uc18c","type":"DEC"},{"id":"DEC-016","summary":"\uc9c0\uae09 \uac70\uc808\uc740 \uc774\ub825\uc5d0 \uae30\ub85d","type":"DEC"},{"id":"DEC-017","summary":"\uc815\uc0b0\uc740 PG \ud654\uba74\uc5d0\uc11c \ud655\uc778","type":"DEC"},{"id":"DEC-018","summary":"\uc601\uc218\uc99d \uba54\uc77c","type":"DEC"},{"id":"GOAL-001","summary":"\uad6c\ub9e4\uc790\uac00 \ud55c \ud488\ubaa9\uc744 \ud55c \ubc88\uc5d0 \uacb0\uc81c\ud55c\ub2e4.","type":"GOAL"},{"id":"REQ-001","summary":"\uad6c\ub9e4\uc790\ub294 KRW \ud3ec\ud568\uac00\ub85c \ud55c \ud488\ubaa9\uc744 \uacb0\uc81c\ud558\uace0, \uc11c\ubc84 \uc7ac\uacc4\uc0b0 \uac00\uaca9\uacfc \uc8fc\ubb38\ubcc4 \uacb0\uc81c \ud0a4\ub85c \ud55c \ubc88\ub9cc \uc2b9\uc778\ub418\uba70, \uc2e4\ud328\ud558\uba74 \ub2e4\uc2dc \uacb0\uc81c\ud55c\ub2e4(DEC-007~DEC-018).","type":"REQ"},{"id":"RULE-001","summary":"\uacb0\uc81c \uaddc\uce59: KRW \ud3ec\ud568\uac00, \uc11c\ubc84 \uc7ac\uacc4\uc0b0, \uc8fc\ubb38\ubcc4 \uacb0\uc81c \ud0a4 \ud55c \ubc88 \uc2b9\uc778, \uc2e4\ud328 \uc2dc \ub2e4\uc2dc \uacb0\uc81c, \uacb0\uc81c \uc804 \ucde8\uc18c, \uc6b4\uc601\uc790 \uc804\uc561 \ud658\ubd88, \uc601\uc218\uc99d \uba54\uc77c.","type":"RULE"},{"id":"SURF-001","summary":"\uacb0\uc81c","type":"SURF"},{"id":"TASK-001","summary":"Implements REQ-001","type":"TASK"},{"id":"UNK-001","summary":"currency: KRW \ub2e8\uc77c \ud1b5\ud654\uc778\uac00, \ub2e4\ub978 \ud1b5\ud654 \ud45c\uc2dc \uc804\ud658\uc778\uac00?","type":"UNK"},{"id":"UNK-002","summary":"price_authority: \uc11c\ubc84\uac00 \uc8fc\ubb38 \uc2dc \uac00\uaca9\uc744 \ub2e4\uc2dc \uacc4\uc0b0\uc778\uac00, \ud654\uba74 \uac00\uaca9\uc744 \uadf8\ub300\ub85c \uc0ac\uc6a9\uc778\uac00?","type":"UNK"},{"id":"UNK-003","summary":"tax: \ubd80\uac00\uc138 \ud3ec\ud568\uac00 \ud45c\uc2dc\uc778\uac00, \ubd80\uac00\uc138 \ubcc4\ub3c4 \ud45c\uc2dc\uc778\uac00?","type":"UNK"},{"id":"UNK-004","summary":"discount: \ud560\uc778 \uc5c6\uc74c\uc778\uac00, \ucfe0\ud3f0 \uc785\ub825\ub780\uc778\uac00?","type":"UNK"},{"id":"UNK-005","summary":"payment_failure: \uc2e4\ud328 \uc548\ub0b4\uc640 \ub2e4\uc2dc \uacb0\uc81c\uc778\uac00, \uc8fc\ubb38 \uc790\ub3d9 \ucde8\uc18c\uc778\uac00?","type":"UNK"},{"id":"UNK-006","summary":"duplicate_payment: \uc8fc\ubb38\ubcc4 \uacb0\uc81c \ud0a4\ub85c \ud55c \ubc88\ub9cc \uc2b9\uc778\uc778\uac00, \uac80\uc0ac \uc5c6\uc74c\uc778\uac00?","type":"UNK"},{"id":"UNK-007","summary":"refund: \uc6b4\uc601\uc790\uac00 \uc804\uc561 \ud658\ubd88\uc778\uac00, \ud658\ubd88 \uc5c6\uc74c\uc778\uac00?","type":"UNK"},{"id":"UNK-008","summary":"partial_refund: \ubd80\ubd84 \ud658\ubd88 \uc5c6\uc74c\uc778\uac00, \ud488\ubaa9 \ub2e8\uc704 \ubd80\ubd84 \ud658\ubd88\uc778\uac00?","type":"UNK"},{"id":"UNK-009","summary":"cancellation: \uacb0\uc81c \uc804\uc5d0\ub9cc \ucde8\uc18c\uc778\uac00, \uc5b8\uc81c\ub4e0 \ucde8\uc18c\uc778\uac00?","type":"UNK"},{"id":"UNK-010","summary":"chargeback: \uc9c0\uae09 \uac70\uc808\uc740 \uc774\ub825\uc5d0 \uae30\ub85d\uc778\uac00, \ubb34\uc2dc\uc778\uac00?","type":"UNK"},{"id":"UNK-011","summary":"settlement: \uc815\uc0b0\uc740 PG \ud654\uba74\uc5d0\uc11c \ud655\uc778\uc778\uac00, \uc0ac\uc774\ud2b8 \uc548 \uc815\uc0b0 \ud654\uba74\uc778\uac00?","type":"UNK"},{"id":"UNK-012","summary":"receipt: \uc601\uc218\uc99d \uba54\uc77c\uc778\uac00, \uc601\uc218\uc99d \uc5c6\uc74c\uc778\uac00?","type":"UNK"},{"id":"UNK-901","summary":"AUTH topology: Does the product have user accounts (sign-up, sign-in, sessions)?","type":"UNK"},{"id":"UNK-902","summary":"MONEY topology: Does the product take, hold, refund or display money (prices, payments, refunds)?","type":"UNK"},{"id":"UNK-903","summary":"FILE_UPLOAD topology: Can users upload files (images, documents, attachments)?","type":"UNK"},{"id":"UNK-904","summary":"ASYNC topology: Does any result arrive later than the request (callbacks, background jobs, polling, queued work)?","type":"UNK"},{"id":"UNK-905","summary":"PERMISSION topology: Do different roles or owners see or do different things?","type":"UNK"},{"id":"UNK-906","summary":"DESTRUCTIVE_ACTION topology: Can a user delete, cancel or overwrite something that is hard to undo?","type":"UNK"},{"id":"USR-001","summary":"\ube44\ud68c\uc6d0 \uad6c\ub9e4\uc790.","type":"USR"}],"binding_contracts":{"product_binding_contract":{"contract_id":"joewrks.product-coverage-binding","digest":"b57459533247de52038aacb158e785c2184edcdd2fa6831f0edc3db713775f3c","version":"1.0"},"ux_binding_contract":{"contract_id":"joewrks.ux-coverage-binding","digest":"8fc84057a4a6f0f0ce329a58d11b8e208989800147d703665cea52088de0be0d","version":"1.0"}},"changed":[],"deferred_non_blocking":[],"definition_digest":"0929a272dc897d81d68f2509c2cb26d14dcfa0973c01591f3c71cacfbfab3040","from_revision":null,"high_risk_decisions":[{"id":"DEC-001","reversibility":"COSTLY_TO_REVERSE","risk_flags":["money"],"statement":"Yes: the product has MONEY behaviour."},{"id":"DEC-002","reversibility":"COSTLY_TO_REVERSE","risk_flags":["security"],"statement":"No: the product has no AUTH behaviour."},{"id":"DEC-003","reversibility":"COSTLY_TO_REVERSE","risk_flags":[],"statement":"No: the product has no FILE_UPLOAD behaviour."},{"id":"DEC-004","reversibility":"COSTLY_TO_REVERSE","risk_flags":[],"statement":"No: the product has no ASYNC behaviour."},{"id":"DEC-005","reversibility":"COSTLY_TO_REVERSE","risk_flags":["security"],"statement":"No: the product has no PERMISSION behaviour."},{"id":"DEC-006","reversibility":"COSTLY_TO_REVERSE","risk_flags":["destructive"],"statement":"No: the product has no DESTRUCTIVE_ACTION behaviour."},{"id":"DEC-007","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"KRW \ub2e8\uc77c \ud1b5\ud654"},{"id":"DEC-008","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc11c\ubc84\uac00 \uc8fc\ubb38 \uc2dc \uac00\uaca9\uc744 \ub2e4\uc2dc \uacc4\uc0b0"},{"id":"DEC-009","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\ubd80\uac00\uc138 \ud3ec\ud568\uac00 \ud45c\uc2dc"},{"id":"DEC-010","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\ud560\uc778 \uc5c6\uc74c"},{"id":"DEC-011","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc2e4\ud328 \uc548\ub0b4\uc640 \ub2e4\uc2dc \uacb0\uc81c"},{"id":"DEC-012","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc8fc\ubb38\ubcc4 \uacb0\uc81c \ud0a4\ub85c \ud55c \ubc88\ub9cc \uc2b9\uc778"},{"id":"DEC-013","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc6b4\uc601\uc790\uac00 \uc804\uc561 \ud658\ubd88"},{"id":"DEC-014","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\ubd80\ubd84 \ud658\ubd88 \uc5c6\uc74c"},{"id":"DEC-015","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uacb0\uc81c \uc804\uc5d0\ub9cc \ucde8\uc18c"},{"id":"DEC-016","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc9c0\uae09 \uac70\uc808\uc740 \uc774\ub825\uc5d0 \uae30\ub85d"},{"id":"DEC-017","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc815\uc0b0\uc740 PG \ud654\uba74\uc5d0\uc11c \ud655\uc778"},{"id":"DEC-018","reversibility":"REVERSIBLE","risk_flags":["money"],"statement":"\uc601\uc218\uc99d \uba54\uc77c"}],"retired":[],"schema_version":"joewrks.approval-manifest/1.0","semantic_closure_summary":{"active_grill_pack_gaps":0,"blocked_material_unknowns":0,"core_coverage_gaps":0,"coverage_without_authority":0,"discovery_baseline_gaps":0,"discovery_procedure_gaps":0,"invalid_authority_binding":0,"invalid_authority_graph_reference":0,"invalid_coverage_authority_type":0,"invalid_resolution_authority":0,"minimum_definition_gaps":0,"missing_required_user_decisions":0,"open_coverage_without_unknown":0,"open_material_surfaces":0,"open_material_unknowns":0,"orphan_material_authority":0,"pack_materiality_floor_violations":0,"requirement_acceptance_gaps":0,"screen_action_inventory_gaps":0,"screen_state_gaps":0,"semantic_readiness_blockers":0,"specialist_binding_gaps":0,"stale_authority_binding":0,"stale_consumed_evidence":0,"stale_selected_authority":0,"task_mapping_gaps":0,"umbrella_unknown_compression":0,"unassessed_materiality":0,"unauthorized_agent_decisions":0,"unbound_material_surfaces":0,"unconsumed_material_decision":0,"unjustified_na_without_basis":0,"unresolved_material_contradictions":0,"unresolved_pack_axes":0,"unresolved_unknown_provenance":0,"ux_coverage_gaps":0,"ux_invalid_authority_binding":0,"ux_open_without_unknown":0,"ux_stale_authority_binding":0,"ux_unjustified_na":0},"superseded":[],"to_revision":4},"manifest_digest":"9df0e5d21d1f4fdc5728580ad05da00035b91a729c6cc8cb5ee0c7a772c54d68"}
```
