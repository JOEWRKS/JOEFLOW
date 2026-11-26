# Replay rev15: builder commands and their output

Base: revision 14 (committed). Target: revision 15 (committed).

### 1. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-042 --option OPT-CONFIRM --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-CONFIRM 추천안 수락.' --statement '취소 버튼 → 주문번호·환불 금액을 보여 주는 확인 대화상자 → 확정. 한 단계가 늘지만 오취소를 막는다.' --decision DEC-042 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-042"
  ],
  "changed": [
    "UNK-042",
    "SURF-008",
    "SURF-010"
  ],
  "replaced": [],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.confirmation"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-042",
      "option": "OPT-CONFIRM",
      "decision": "DEC-042",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.confirmation: answered by DEC-042"
  ]
}
```

### 2. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-043 --option OPT-OPTIONAL --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-OPTIONAL 추천안 수락.' --statement '사유 선택은 선택 사항(단순 변심/주문 실수/기타), 주문 이력에 기록. 필수 입력 없음.' --decision DEC-043 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-043"
  ],
  "changed": [
    "UNK-043"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.reason"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-043",
      "option": "OPT-OPTIONAL",
      "decision": "DEC-043",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.reason: answered by DEC-043"
  ]
}
```

### 3. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-044 --option OPT-NO-UNDO --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-NO-UNDO 추천안 수락.' --statement '되돌리기 없음. 취소 완료 화면에서 다시 주문하기로 안내. 환불·재고 처리가 한 방향이다.' --decision DEC-044 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-044"
  ],
  "changed": [
    "UNK-044"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.undo"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-044",
      "option": "OPT-NO-UNDO",
      "decision": "DEC-044",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.undo: answered by DEC-044"
  ]
}
```

### 4. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-045 --option OPT-NO-GRACE --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-NO-GRACE 추천안 수락.' --statement '유예 없이 확정 즉시 처리(결제됐으면 환불 호출 즉시). 상태가 바로 취소됨이 된다.' --decision DEC-045 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-045"
  ],
  "changed": [
    "UNK-045"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.grace_period"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-045",
      "option": "OPT-NO-GRACE",
      "decision": "DEC-045",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.grace_period: answered by DEC-045"
  ]
}
```

### 5. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-046 --option OPT-RESTOCK --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-RESTOCK 추천안 수락.' --statement '변형 재고 복구 + 결제됐으면 어댑터 환불 호출 + 주문 상태 취소됨. 장바구니는 건드리지 않는다. 세 효과가 한 트랜잭션 의미로 묶인다.' --decision DEC-046 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-046"
  ],
  "changed": [
    "UNK-046"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.dependency_effects"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-046",
      "option": "OPT-RESTOCK",
      "decision": "DEC-046",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.dependency_effects: answered by DEC-046"
  ]
}
```

### 6. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-047 --option OPT-SHIP-PREP --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-SHIP-PREP 추천안 수락.' --statement '배송 준비 상태로 전환되는 순간. 그 뒤엔 취소 버튼 대신 문의 안내. DEC-025와 같은 경계.' --decision DEC-047 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-047"
  ],
  "changed": [
    "UNK-047"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.irreversible_boundary"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-047",
      "option": "OPT-SHIP-PREP",
      "decision": "DEC-047",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.irreversible_boundary: answered by DEC-047"
  ]
}
```

### 7. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-048 --option OPT-LOG --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-LOG 추천안 수락.' --statement '주문 이력에 취소·환불 이벤트(시각, 주체=구매자, 사유, 환불 결과)를 남긴다. 주문 데이터에 이력 배열이 생긴다.' --decision DEC-048 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-048"
  ],
  "changed": [
    "UNK-048"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.audit"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-048",
      "option": "OPT-LOG",
      "decision": "DEC-048",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.audit: answered by DEC-048"
  ]
}
```

### 8. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-049 --option OPT-SCREEN-EVENT --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-SCREEN-EVENT 추천안 수락.' --statement '취소 완료 화면 + 주문 조회에 반영. 알림 메일은 어댑터 이벤트로만 기록(실제 발송 범위 밖, DEC-028과 동일). 메일 서비스 없이 완성.' --decision DEC-049 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-049"
  ],
  "changed": [
    "UNK-049"
  ],
  "replaced": [
    "SURF-008",
    "SURF-010"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.notification"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-049",
      "option": "OPT-SCREEN-EVENT",
      "decision": "DEC-049",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['destructive', 'money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.notification: answered by DEC-049"
  ],
  "surfaces_left_without_open_question": [
    {
      "surface": "SURF-010",
      "decision_refs": [
        "DEC-016",
        "DEC-023",
        "DEC-025",
        "DEC-042",
        "DEC-043",
        "DEC-044",
        "DEC-045",
        "DEC-046",
        "DEC-047",
        "DEC-048",
        "DEC-049"
      ],
      "next": "new_records.py --state STATE --patch PATCH requirement --from-decisions DEC-016,DEC-023,DEC-025,DEC-042,DEC-043,DEC-044,DEC-045,DEC-046,DEC-047,DEC-048,DEC-049 --surface SURF-010 --requirement REQ-007",
      "why": "an OPEN material surface needs an OPEN question (OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN); with every question answered, a requirement drafted from its decisions is its authority and the surface becomes IN_SCOPE"
    }
  ]
}
```

### 9. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-050 --option OPT-PENDING-SCREEN --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-PENDING-SCREEN 추천안 수락.' --statement '승인 요청 직후 주문은 결제 대기, 주문서는 처리 중 화면(버튼 잠금). 중복 클릭 불가.' --decision DEC-050 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-050"
  ],
  "changed": [
    "UNK-050",
    "SURF-009",
    "SURF-011"
  ],
  "replaced": [
    "SURF-008"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.pending"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-050",
      "option": "OPT-PENDING-SCREEN",
      "decision": "DEC-050",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.pending: answered by DEC-050"
  ]
}
```

### 10. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-051 --option OPT-POLL-2S --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-POLL-2S 추천안 수락.' --statement '처리 중 화면이 2초 간격으로 주문 상태를 조회, 최대 30초. 서버에 상태 조회 API가 든다.' --decision DEC-051 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-051"
  ],
  "changed": [
    "UNK-051"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.polling"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-051",
      "option": "OPT-POLL-2S",
      "decision": "DEC-051",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.polling: answered by DEC-051"
  ]
}
```

### 11. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-052 --option OPT-TIMEOUT-PENDING --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-TIMEOUT-PENDING 추천안 수락.' --statement '30초 안에 결과가 없으면 주문을 결제 확인 중으로 두고 주문 조회로 안내. 결제 대기 주문은 유지. 확인 중 상태 화면 필요.' --decision DEC-052 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-052"
  ],
  "changed": [
    "UNK-052"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.timeout"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-052",
      "option": "OPT-TIMEOUT-PENDING",
      "decision": "DEC-052",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.timeout: answered by DEC-052"
  ]
}
```

### 12. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-053 --option OPT-RETRY-USER --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-RETRY-USER 추천안 수락.' --statement '자동 재시도 없음. 실패·확인 중 상태에서 사용자가 다시 결제(DEC-021). 단순하고 멱등 키와 맞물린다.' --decision DEC-053 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-053"
  ],
  "changed": [
    "UNK-053"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.retry"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-053",
      "option": "OPT-RETRY-USER",
      "decision": "DEC-053",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.retry: answered by DEC-053"
  ]
}
```

### 13. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-054 --option OPT-ORDER-KEY --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-ORDER-KEY 추천안 수락.' --statement 'DEC-022의 주문별 결제 키가 권위. 같은 키의 콜백은 첫 결과만 반영. 어댑터 인터페이스에 키가 든다.' --decision DEC-054 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-054"
  ],
  "changed": [
    "UNK-054"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.idempotency"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-054",
      "option": "OPT-ORDER-KEY",
      "decision": "DEC-054",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.idempotency: answered by DEC-054"
  ]
}
```

### 14. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-055 --option OPT-STATE-GUARD --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-STATE-GUARD 추천안 수락.' --statement '상태 전이는 허용 표(결제 대기→완료/실패/취소)로만. 이미 전이된 주문에 온 콜백은 무시하고 이력에 기록. 전이 표가 데이터로 든다.' --decision DEC-055 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-055"
  ],
  "changed": [
    "UNK-055"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.duplicate_execution"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-055",
      "option": "OPT-STATE-GUARD",
      "decision": "DEC-055",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.duplicate_execution: answered by DEC-055"
  ]
}
```

### 15. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-056 --option OPT-LATE-APPLY --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-LATE-APPLY 추천안 수락.' --statement '결제 완료로 반영. 사용자가 그 사이 취소했으면 환불 호출. 취소와 승인이 겹치는 경우를 정의.' --decision DEC-056 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-056"
  ],
  "changed": [
    "UNK-056"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.late_completion"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-056",
      "option": "OPT-LATE-APPLY",
      "decision": "DEC-056",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.late_completion: answered by DEC-056"
  ]
}
```

### 16. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-057 --option OPT-NO-PARTIAL --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-NO-PARTIAL 추천안 수락.' --statement '주문은 단일 결제라 부분 완료 없음. 승인됐는데 주문 확정 저장이 실패하면 환불 호출 후 실패 처리. 보상 호출 하나로 끝.' --decision DEC-057 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-057"
  ],
  "changed": [
    "UNK-057"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.partial_completion"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-057",
      "option": "OPT-NO-PARTIAL",
      "decision": "DEC-057",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.partial_completion: answered by DEC-057"
  ]
}
```

### 17. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-058 --option OPT-CANCEL-PENDING --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-CANCEL-PENDING 추천안 수락.' --statement '가능. 승인 전이면 환불 없이 취소, 그 뒤 늦은 승인이 오면 늦은 완료 규칙으로 환불. 결제 완료 뒤는 DEC-025. 대기 주문이 쌓이지 않는다.' --decision DEC-058 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-058"
  ],
  "changed": [
    "UNK-058"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.cancel"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-058",
      "option": "OPT-CANCEL-PENDING",
      "decision": "DEC-058",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.cancel: answered by DEC-058"
  ]
}
```

### 18. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-059 --option OPT-ADAPTER-QUERY --summary '사용자 답(2026-11-23): "전부 추천대로" — OPT-ADAPTER-QUERY 추천안 수락.' --statement '어댑터의 상태 조회 호출이 권위. 확인 중 주문은 조회 때마다 다시 묻고, 모의 어댑터는 즉시 응답. 운영자 화면 없음. 어댑터 인터페이스에 조회가 든다.' --decision DEC-059 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-059"
  ],
  "changed": [
    "UNK-059"
  ],
  "replaced": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "cells": [
    "grill_coverage[GRILL-ASYNC-1].axes.reconciliation"
  ],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-059",
      "option": "OPT-ADAPTER-QUERY",
      "decision": "DEC-059",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": [
    "grill_coverage[GRILL-ASYNC-1].axes.reconciliation: answered by DEC-059"
  ],
  "surfaces_left_without_open_question": [
    {
      "surface": "SURF-011",
      "decision_refs": [
        "DEC-017",
        "DEC-021",
        "DEC-022",
        "DEC-050",
        "DEC-051",
        "DEC-052",
        "DEC-053",
        "DEC-054",
        "DEC-055",
        "DEC-056",
        "DEC-057",
        "DEC-058",
        "DEC-059"
      ],
      "next": "new_records.py --state STATE --patch PATCH requirement --from-decisions DEC-017,DEC-021,DEC-022,DEC-050,DEC-051,DEC-052,DEC-053,DEC-054,DEC-055,DEC-056,DEC-057,DEC-058,DEC-059 --surface SURF-011 --requirement REQ-007",
      "why": "an OPEN material surface needs an OPEN question (OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN); with every question answered, a requirement drafted from its decisions is its authority and the surface becomes IN_SCOPE"
    }
  ]
}
```

### 19. exit 0

```
python new_records.py --state state.json --patch patch.json requirement --from-decisions DEC-025,DEC-047,DEC-042,DEC-043,DEC-044,DEC-045,DEC-046,DEC-048,DEC-049,DEC-023,DEC-024 --surface SURF-010 --requirement REQ-007 --statement '구매자는 배송 준비 전까지 주문을 취소할 수 있고, 배송 준비로 전환되는 순간부터 취소 버튼 대신 문의 안내를 본다(DEC-025, DEC-047). 취소는 주문번호와 환불 금액을 보여 주는 확인 대화상자에서 확정하며, 사유 선택은 선택 사항(단순 변심/주문 실수/기타)이다(DEC-042, DEC-043). 확정 즉시 유예 없이 처리되고 되돌리기는 없다(DEC-044, DEC-045). 효과는 변형 재고 복구, 결제됐으면 어댑터 환불 호출, 주문 상태 취소됨이며 장바구니는 건드리지 않는다(DEC-046). 취소·환불 이벤트(시각, 주체=구매자, 사유, 환불 결과)는 주문 이력에 남는다(DEC-048). 취소 완료 화면과 주문 조회에 반영하고 알림 메일은 어댑터 이벤트로만 기록한다(DEC-049). 환불은 전액 단위, 모의 어댑터는 즉시 성공(DEC-023, DEC-024).' --scope '주문 취소·환불' --ui-required true
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "REQ-007"
  ],
  "changed": [],
  "replaced": [
    "SURF-010"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "SURF-010: IN_SCOPE with REQ-007 as authority; the statement is a draft joined from ['DEC-025', 'DEC-047', 'DEC-042', 'DEC-043', 'DEC-044', 'DEC-045', 'DEC-046', 'DEC-048', 'DEC-049', 'DEC-023', 'DEC-024'] — edit it to read as one requirement (new_records.py edit REQ-007 --set /statement ...)"
  ],
  "next_steps": [
    "REQ-007 is MATERIAL: FREEZE needs its Core coverage row (draft_freeze.py)"
  ]
}
```

### 20. exit 0

```
python new_records.py --state state.json --patch patch.json requirement --from-decisions DEC-050,DEC-051,DEC-052,DEC-053,DEC-021,DEC-054,DEC-022,DEC-055,DEC-056,DEC-057,DEC-058,DEC-059 --surface SURF-011 --requirement REQ-008 --statement '승인 요청 직후 주문은 결제 대기가 되고 주문서는 처리 중 화면(버튼 잠금)을 보이며, 2초 간격으로 최대 30초 주문 상태를 조회한다(DEC-050, DEC-051). 30초 안에 결과가 없으면 주문은 결제 확인 중이 되고 주문 조회로 안내한다(DEC-052). 자동 재시도는 없고 실패·확인 중 상태에서 사용자가 다시 결제한다(DEC-053, DEC-021). 멱등 권위는 주문별 결제 키이며 같은 키의 콜백은 첫 결과만 반영한다(DEC-054, DEC-022). 상태 전이는 허용 표(결제 대기→결제 완료/결제 실패/취소됨, 결제 대기→결제 확인 중→결제 완료/결제 실패, 결제 완료→배송 준비, 결제 완료→취소됨→환불됨, 결제 완료→분쟁)로만 일어나고 벗어난 콜백은 무시하고 이력에 기록한다(DEC-055). 확인 중 상태에 늦게 온 승인은 결제 완료로 반영하되 그 사이 취소했으면 환불을 호출한다(DEC-056). 부분 완료는 없으며 승인 뒤 주문 확정 저장이 실패하면 환불 호출 후 실패 처리한다(DEC-057). 결제 대기·확인 중 상태에서 취소할 수 있고 승인 전이면 환불 없이 취소한다(DEC-058). 확인 중 주문의 최종 상태는 어댑터 상태 조회가 권위이며 모의 어댑터는 즉시 응답한다(DEC-059).' --scope '결제 승인·주문 상태 전이' --ui-required true
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "REQ-008"
  ],
  "changed": [],
  "replaced": [
    "SURF-011"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "SURF-011: IN_SCOPE with REQ-008 as authority; the statement is a draft joined from ['DEC-050', 'DEC-051', 'DEC-052', 'DEC-053', 'DEC-021', 'DEC-054', 'DEC-022', 'DEC-055', 'DEC-056', 'DEC-057', 'DEC-058', 'DEC-059'] — edit it to read as one requirement (new_records.py edit REQ-008 --set /statement ...)"
  ],
  "next_steps": [
    "REQ-008 is MATERIAL: FREEZE needs its Core coverage row (draft_freeze.py)"
  ]
}
```

### 21. exit 0

```
python new_records.py --state state.json --patch patch.json edit REQ-007 --replace-text COSTLY_TO_REVERS IRREVERSIBL
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [],
  "replaced": [
    "REQ-007"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "REQ-007: changed ['/materiality/reversibility']"
  ]
}
```

### 22. exit 0

```
python new_records.py --state state.json --patch patch.json edit REQ-008 --replace-text MULTI_FLOW SYSTEMIC
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [],
  "replaced": [
    "REQ-008"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "REQ-008: changed ['/materiality/fan_out']"
  ]
}
```

### 23. exit 0

```
python new_records.py --state state.json --patch patch.json edit SURF-010 --set-json /unknown_refs '[]' --set-json /decision_refs '["DEC-016", "DEC-023", "DEC-025", "DEC-042", "DEC-043", "DEC-044", "DEC-045", "DEC-046", "DEC-047", "DEC-048", "DEC-049"]'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [],
  "replaced": [
    "SURF-010"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "SURF-010: changed ['/unknown_refs', '/decision_refs']"
  ]
}
```

### 24. exit 0

```
python new_records.py --state state.json --patch patch.json edit SURF-011 --set-json /unknown_refs '[]'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [],
  "replaced": [
    "SURF-011"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "SURF-011: changed ['/unknown_refs']"
  ]
}
```

### 25. exit 0

```
python open_revision.py state.json --patch patch.json --status OPEN --write
```

```json
{
  "added": [
    "DEC-042",
    "DEC-043",
    "DEC-044",
    "DEC-045",
    "DEC-046",
    "DEC-047",
    "DEC-048",
    "DEC-049",
    "DEC-050",
    "DEC-051",
    "DEC-052",
    "DEC-053",
    "DEC-054",
    "DEC-055",
    "DEC-056",
    "DEC-057",
    "DEC-058",
    "DEC-059",
    "REQ-007",
    "REQ-008"
  ],
  "cells": [
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.confirmation",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.reason",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.undo",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.grace_period",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.dependency_effects",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.irreversible_boundary",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.audit",
    "grill_coverage[GRILL-DESTRUCTIVE-ACTION-1].axes.notification",
    "grill_coverage[GRILL-ASYNC-1].axes.pending",
    "grill_coverage[GRILL-ASYNC-1].axes.polling",
    "grill_coverage[GRILL-ASYNC-1].axes.timeout",
    "grill_coverage[GRILL-ASYNC-1].axes.retry",
    "grill_coverage[GRILL-ASYNC-1].axes.idempotency",
    "grill_coverage[GRILL-ASYNC-1].axes.duplicate_execution",
    "grill_coverage[GRILL-ASYNC-1].axes.late_completion",
    "grill_coverage[GRILL-ASYNC-1].axes.partial_completion",
    "grill_coverage[GRILL-ASYNC-1].axes.cancel",
    "grill_coverage[GRILL-ASYNC-1].axes.reconciliation"
  ],
  "changed": [
    "UNK-042",
    "UNK-043",
    "UNK-044",
    "UNK-045",
    "UNK-046",
    "UNK-047",
    "UNK-048",
    "UNK-049",
    "UNK-050",
    "UNK-051",
    "UNK-052",
    "UNK-053",
    "UNK-054",
    "UNK-055",
    "UNK-056",
    "UNK-057",
    "UNK-058",
    "UNK-059",
    "SURF-008",
    "SURF-010",
    "SURF-009",
    "SURF-011"
  ],
  "from_revision": 14,
  "refreshed": [],
  "status": "OPEN",
  "to_revision": 15,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "warning": "revision 14 was never approved; its changes will reach the user only inside the next Approval Manifest",
  "written": true
}
```
