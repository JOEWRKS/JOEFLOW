# Replay rev23: builder commands and their output

Base: revision 22 (committed). Target: revision 23 (committed).

### 1. exit 0

```
python new_records.py --state state.json --patch patch.json question --unknown UNK-072 --question '승인 콜백의 금액이 주문 합계와 달라 서버가 승인을 거부할 때(DEC-069), PG가 이미 승인한 금액은 어떻게 하는가? DEC-069는 거부와 실패 이력만 정하고 승인된 돈의 처리는 정하지 않는다.' --why '구매자 계좌에서 빠진 돈이 환불되지 않으면 실패 이력만 남은 결제 대기 주문에 돈이 묶인다(Stage 4 수정 묶음 T019가 환불 호출을 구현해 두었다).' --category CORE_FLOW --materiality HIGH,LOCAL,true,REVERSIBLE,money --option 'OPT-REFUND=불일치 거부 시 서버가 어댑터 환불을 호출해 승인된 금액을 전액 환불하고, 실패 이력에 금액 불일치와 환불을 함께 남긴다. 주문은 결제 대기로 남아 다시 결제·취소·24시간 자동 취소를 따른다.|구매자 돈이 묶이지 않는다. 환불 호출이 실패하면 이력에 남고 운영자가 처리한다(기존 환불 실패 규칙).' --option 'OPT-HOLD=환불하지 않고 주문을 결제 확인 중으로 두어 운영자가 금액을 확인한 뒤 처리한다.|구매자 돈이 운영자 처리까지 묶이고 확인 중 상태의 의미가 넓어진다.' --affects SURF-009 --affects SURF-011 --surface SURF-011 --recommend OPT-REFUND --confidence HIGH --reason EVD-001 --tradeoff '모의 어댑터에서는 환불이 즉시 성공하므로 실제 PG의 환불 지연은 관측되지 않는다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "UNK-072"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-072": "USER_DECISION_REQUIRED"
  }
}
```

### 2. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-072 --option OPT-REFUND --summary '사용자 답(2026-11-26): "둘 다 추천대로" — 추천안 수락.' --statement '승인 콜백 금액이 주문 합계와 달라 승인을 거부할 때 서버는 어댑터 환불을 호출해 승인된 금액을 전액 환불하고, 실패 이력에 금액 불일치와 환불을 함께 남긴다. 주문은 결제 대기로 남아 다시 결제·취소·24시간 자동 취소를 따른다. 환불 호출 실패는 기존 환불 실패 규칙대로 이력에 남긴다.' --decision DEC-072 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-072"
  ],
  "changed": [
    "SURF-009",
    "SURF-011"
  ],
  "replaced": [
    "UNK-072"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-072",
      "option": "OPT-REFUND",
      "decision": "DEC-072",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": []
}
```

### 3. exit 0

```
python new_records.py --state state.json --patch patch.json question --unknown UNK-073 --question '모의 결제창(DEC-069)은 어떤 항목을 보이는가? 정의는 승인·실패·닫기 버튼만 정하고, 구매자가 어느 가맹점에 얼마를 내는지 확인할 항목 목록이 없다.' --why '실제 PG 결제창은 가맹점명·금액·주문번호·결제수단을 보인다. 모의 결제창이 같은 항목을 보여야 데모가 실제 흐름을 대표하고 어댑터 교체 뒤 구매자 경험이 달라지지 않는다(T020 재비평 지적).' --category SECONDARY_BEHAVIOR --materiality LOW,LOCAL,true,REVERSIBLE --option 'OPT-MERCHANT=모의 결제창은 가맹점명(ATELIER), 결제 금액, 주문번호, 결제수단, 시연용 안내 문장과 승인·실패·닫기 동작을 보인다.|실제 결제창과 같은 확인 항목을 갖는다. 항목 배치는 JOEDESIGN(D17)이 정한다.' --option 'OPT-MINIMAL=금액·주문번호·결제수단과 버튼만 보이고 가맹점명은 없다.|구매자가 어느 가맹점 결제인지 창 안에서 확인할 수 없다.' --affects SURF-008 --surface SURF-008 --recommend OPT-MERCHANT --confidence HIGH --reason EVD-001 --tradeoff '가맹점명은 사이트 이름을 그대로 쓰므로 설정 항목이 늘지 않는다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "UNK-073"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-073": "USER_CONFIRMATION"
  }
}
```

### 4. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-073 --option OPT-MERCHANT --summary '사용자 답(2026-11-26): "둘 다 추천대로" — 추천안 수락.' --statement '모의 결제창은 가맹점명(ATELIER), 결제 금액, 주문번호, 결제수단, 시연용 안내 문장과 승인·실패·닫기 동작을 보인다. 항목 배치는 시각 규칙(JOEDESIGN)이 정한다.' --decision DEC-073 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-073"
  ],
  "changed": [
    "SURF-008"
  ],
  "replaced": [
    "UNK-073"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-073",
      "option": "OPT-MERCHANT",
      "decision": "DEC-073",
      "resolution_mode": "USER_ACCEPTED_RECOMMENDATION",
      "decision_authority": "USER_CONFIRMATION",
      "open_authority_was": "USER_CONFIRMATION",
      "why": "material, not high-risk, with a HIGH-confidence recommendation"
    }
  ],
  "notes": []
}
```

### 5. exit 0

```
python new_records.py --state state.json --patch patch.json edit RULE-013 --replace-text '긴다(DEC-069' '기며 이미 승인된 금액은 어댑터 환불로 전액 돌려준다(DEC-069, DEC-072'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "RULE-013"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "RULE-013: changed ['/statement']"
  ]
}
```

### 6. exit 0

```
python new_records.py --state state.json --patch patch.json edit SCR-004 --replace-text '안 모의 결제창)으로 보내고,' '안 모의 결제창: 가맹점명·금액·주문번호·결제수단과 승인·실패·닫기, DEC-073)으로 보내고,'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "SCR-004"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "SCR-004: changed ['/purpose']"
  ]
}
```

### 7. exit 0

```
python new_records.py --state state.json --patch patch.json edit INT-001 --replace-text '승인·실패·닫기' '가맹점명·금액·주문번호·결제수단 표시, 승인·실패·닫기, DEC-073'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "INT-001"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "INT-001: changed ['/purpose']"
  ]
}
```

### 8. exit 0

```
python new_records.py --state state.json --patch patch.json edit AC-006 --replace-text '승인·실패·닫기)이 열리고, 승인으로 복귀하면 처리 중 화면에서 버튼이 잠기고 서버가 금액 대조 뒤 승인을 확정해 주문은 결제 완료, 장바구니는 비워지고 주문 완료 화면에 주문번호·금액·배송지·조회 안내가 보인다. 결제창에서 실패나 닫기로 복귀하거나 승인 확정이 실패하면 주문 상태는 결제 대기로 남고(실패는 이력 사건) 실패 안내와 다시 결제가 보이며 다시 결제는 새 결제 키를 쓴다. 같은 결제 키의 중복 콜백은 무시되고 이력에 기록된다. 복귀 금액이 주문 합계와 다르면 승인이 거부되고 실패 이력' '가맹점명·금액·주문번호·결제수단 표시, 승인·실패·닫기)이 열리고, 승인으로 복귀하면 처리 중 화면에서 버튼이 잠기고 서버가 금액 대조 뒤 승인을 확정해 주문은 결제 완료, 장바구니는 비워지고 주문 완료 화면에 주문번호·금액·배송지·조회 안내가 보인다. 결제창에서 실패나 닫기로 복귀하거나 승인 확정이 실패하면 주문 상태는 결제 대기로 남고(실패는 이력 사건) 실패 안내와 다시 결제가 보이며 다시 결제는 새 결제 키를 쓴다. 같은 결제 키의 중복 콜백은 무시되고 이력에 기록된다. 복귀 금액이 주문 합계와 다르면 승인이 거부되고 승인된 금액이 환불되며 실패 이력에 불일치와 환불'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "AC-006"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "AC-006: changed ['/assertion']"
  ]
}
```

### 9. exit 0

```
python open_revision.py state.json --patch patch.json --status READY_FOR_REVIEW --write
```

```json
{
  "added": [
    "UNK-072",
    "UNK-073",
    "DEC-072",
    "DEC-073"
  ],
  "cells": [],
  "changed": [
    "RULE-013",
    "SCR-004",
    "INT-001",
    "AC-006",
    "SURF-009",
    "SURF-011",
    "SURF-008"
  ],
  "from_revision": 22,
  "refreshed": [
    {
      "cell": "coverage[5].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[5].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "coverage[5].cells.validation",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "coverage[5].cells.acceptance",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "coverage[6].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "coverage[7].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[7].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "coverage[7].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].states.success",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "ux_coverage[3].states.offline",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.success",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.submit",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.failure",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.retry",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.cancel",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.duplicate_concurrent_action",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.timeout",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.offline",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.failure",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.retry",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.duplicate_concurrent_action",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.cancel",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    }
  ],
  "status": "READY_FOR_REVIEW",
  "to_revision": 23,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "written": true
}
```
