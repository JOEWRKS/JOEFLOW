# Replay rev18: builder commands and their output

Base: revision 17 (committed). Target: revision 18 (committed).

### 1. exit 0

```
python new_records.py --state state.json --patch patch.json question --unknown UNK-060 --question '결제 실패 뒤 주문 상태는 무엇인가? 전이 표(STATE-007)의 '"'"'결제 실패'"'"' 상태와 DEC-021·FLOW-003·AC-006의 '"'"'결제 대기 유지'"'"'가 서로 다르다.' --why '표대로면 결제 실패 주문은 구매자 취소(RULE-016)도 24시간 자동 취소(결제 대기만)도 받지 못해 차감된 재고가 묶인다. Stage 2 결제·취소 구현과 AC-006·AC-008 판정이 어느 문장을 따르느냐에 따라 달라진다(ISSUES I-001, 구현 착수 중 발견).' --category STATE_RECOVERY --materiality HIGH,MULTI_FLOW,true,COSTLY_TO_REVERSE,money --option 'OPT-EVENT=결제 실패는 주문 상태가 아니라 이력 사건이다. 실패 콜백·상태 조회 실패·승인 뒤 저장 실패 보상 뒤에도 주문은 결제 대기로 남고(DEC-021), 취소·24시간 자동 취소·다시 결제(새 결제 키)가 모두 적용된다.|STATE-007에서 결제 실패 상태를 빼고 실패를 이력 사건으로 둔다. 사용자 결정 문구(DEC-021)는 그대로다.' --option 'OPT-STATE=결제 실패를 주문 상태로 유지하고 구매자 취소·24시간 자동 취소 범위에 넣는다. 다시 결제는 결제 실패→결제 대기 전이다.|DEC-021·FLOW-003·AC-006의 '"'"'결제 대기 유지'"'"' 문구를 '"'"'결제 실패 상태'"'"'로 바꿔야 하므로 사용자 결정 변경이 된다.' --affects SURF-011 --affects SURF-008 --affects SURF-010 --surface SURF-011 --recommend OPT-EVENT --confidence HIGH --reason EVD-001 --tradeoff '이력 사건으로 두면 상태가 하나 줄어 단순하지만 주문 목록에서 '"'"'실패했던 주문'"'"'을 상태만으로는 구분할 수 없고 이력으로 봐야 한다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "UNK-060"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-060": "USER_DECISION_REQUIRED"
  }
}
```

### 2. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-060 --option OPT-EVENT --summary '사용자 답(2026-11-23): "A 이력 사건" — OPT-EVENT 추천안 수락.' --statement '결제 실패는 주문 상태가 아니라 주문 이력의 사건이다. PG 실패 콜백, 확인 중 상태 조회의 실패 결과, 승인 뒤 주문 확정 저장 실패의 보상(환불 호출) 뒤에 주문은 결제 대기로 남거나 돌아오고 실패가 이력에 기록된다. 결제 대기 주문에는 다시 결제(새 결제 키), 구매자 취소(환불 없음), 24시간 자동 취소가 그대로 적용된다. 주문 상태 집합에서 '"'"'결제 실패'"'"'를 뺀다.' --decision DEC-060 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-060"
  ],
  "changed": [
    "SURF-008",
    "SURF-010",
    "SURF-011"
  ],
  "replaced": [
    "UNK-060"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-060",
      "option": "OPT-EVENT",
      "decision": "DEC-060",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: reversibility COSTLY_TO_REVERSE and risk flags ['money']"
    }
  ],
  "notes": []
}
```

### 3. exit 0

```
python new_records.py --state state.json --patch patch.json edit REQ-006 --replace-text '. 주문별 결제 키로 중복 승인을 막는다(DEC-022). 전액 환불은 어댑터 환불 호출(모의는 즉시 성공), 부분 환불 없음(DEC-023, DEC-024). 구매자는 배송 준비 전까지 취소할 수 있고 결제됐으면 환불 호출(DEC-025). 지급 거절은 분쟁 표시만, 정산은 범위 밖(DEC-026, DEC-027). 완료 뒤 주문 완료 화면과 주문번호 조회를 주고 영수증 메일은 이벤트로만 기록한다(DEC-028). 주문 상태: 결제 대기, 결제 확인 중, 결제 완료, 결제 실패, 배송 준비, 취소됨, 환불됨, 분쟁' '; 결제 실패는 상태가 아니라 이력 사건이다(DEC-060). 주문별 결제 키로 중복 승인을 막는다(DEC-022). 전액 환불은 어댑터 환불 호출(모의는 즉시 성공), 부분 환불 없음(DEC-023, DEC-024). 구매자는 배송 준비 전까지 취소할 수 있고 결제됐으면 환불 호출(DEC-025). 지급 거절은 분쟁 표시만, 정산은 범위 밖(DEC-026, DEC-027). 완료 뒤 주문 완료 화면과 주문번호 조회를 주고 영수증 메일은 이벤트로만 기록한다(DEC-028). 주문 상태: 결제 대기, 결제 확인 중, 결제 완료, 배송 준비, 취소됨, 환불됨, 분쟁(DEC-060)'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "REQ-006"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "REQ-006: changed ['/statement']"
  ]
}
```

### 4. exit 0

```
python new_records.py --state state.json --patch patch.json edit REQ-008 --replace-text '실패·확인 중 상태에서 사용자가 다시 결제한다(DEC-053, DEC-021). 멱등 권위는 주문별 결제 키이며 같은 키의 콜백은 첫 결과만 반영한다(DEC-054, DEC-022). 상태 전이는 허용 표(결제 대기→결제 완료/결제 실패/취소됨, 결제 대기→결제 확인 중→결제 완료/결제 실패, 결제 완료→배송 준비, 결제 완료→취소됨→환불됨, 결제 완료→분쟁)로만 일어나고 벗어난 콜백은 무시하고 이력에 기록한다(DEC-055). 확인 중 상태에 늦게 온 승인은 결제 완료로 반영하되 그 사이 취소했으면 환불을 호출한다(DEC-056). 부분 완료는 없으며 승인 뒤 주문 확정 저장이 실패하면 환불 호출 후 실패 처리한다(DEC-057' '결제 대기(실패 이력 포함)·확인 중 상태에서 사용자가 다시 결제한다(DEC-053, DEC-021). 결제 실패는 상태가 아니라 이력 사건이다(DEC-060). 멱등 권위는 주문별 결제 키이며 같은 키의 콜백은 첫 결과만 반영한다(DEC-054, DEC-022). 상태 전이는 허용 표(결제 대기→결제 완료/취소됨, 결제 대기→결제 확인 중→결제 완료/취소됨, 결제 완료→배송 준비, 결제 완료→취소됨→환불됨, 결제 완료→분쟁; 실패 콜백·조회 실패는 결제 대기 유지 + 이력)로만 일어나고 벗어난 콜백은 무시하고 이력에 기록한다(DEC-055). 확인 중 상태에 늦게 온 승인은 결제 완료로 반영하되 그 사이 취소했으면 환불을 호출한다(DEC-056). 부분 완료는 없으며 승인 뒤 주문 확정 저장이 실패하면 환불 호출 후 주문을 결제 대기로 되돌리고 실패를 이력에 남긴다(DEC-057, DEC-060'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "REQ-008"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "REQ-008: changed ['/statement']"
  ]
}
```

### 5. exit 0

```
python new_records.py --state state.json --patch patch.json edit RULE-012 --replace-text '·실패 주문에는 다시 결제 버튼' ' 주문(실패 이력이 있어도)에는 다시 결제 버튼과 최근 실패 안내'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "RULE-012"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "RULE-012: changed ['/statement']"
  ]
}
```

### 6. exit 0

```
python new_records.py --state state.json --patch patch.json edit RULE-013 --replace-text '결제 실패로 둔다(부분 완료 없음' '주문을 결제 대기로 되돌리고 실패를 이력에 남긴다(부분 완료 없음). 결제 실패는 상태가 아니라 이력 사건이며 실패 콜백·조회 실패 뒤에도 주문은 결제 대기다(DEC-060'
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

### 7. exit 0

```
python new_records.py --state state.json --patch patch.json edit STATE-007 --replace-text '실패, 결제 완료, 배송 준비, 취소됨, 환불됨, 분쟁 중 하나다' '완료, 배송 준비, 취소됨, 환불됨, 분쟁 중 하나다. 결제 실패는 상태가 아니라 이력 사건이다(DEC-060)' --replace-text '실패|결제 확인 중|취소됨; 결제 확인 중→결제 완료|결제 실패|취소됨; 결제 실패→결제 대기(다시 결제); 결제 완료→배송 준비|취소됨|분쟁; 취소됨→환불됨(결제됐던 경우); 배송 준비 이후 구매자 취소 없음' '확인 중|취소됨; 결제 확인 중→결제 완료|취소됨; 결제 완료→배송 준비|취소됨|분쟁; 취소됨→환불됨(결제됐던 경우); 배송 준비 이후 구매자 취소 없음. 실패 콜백·조회 실패·승인 뒤 저장 실패 보상은 결제 대기 유지(확인 중이면 결제 대기로 복귀) + 이력 기록이고, 다시 결제는 결제 대기에서 새 결제 키로 다시 승인 요청이다'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "STATE-007"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "STATE-007: changed ['/conditions/0', '/conditions/1']"
  ]
}
```

### 8. exit 0

```
python new_records.py --state state.json --patch patch.json edit FLOW-005 --replace-text '·결제 실패 주문' ' 주문(실패 이력 포함)'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "FLOW-005"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "FLOW-005: changed ['/paths/0']"
  ]
}
```

### 9. exit 0

```
python new_records.py --state state.json --patch patch.json edit AC-008 --replace-text '결제 실패가 된' '주문은 결제 대기로 남고 이력에 실패가 기록된다. 실패 콜백을 받은 주문도 상태는 결제 대기이고 이력에 실패가 있으며 취소와 다시 결제가 가능하'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "AC-008"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "AC-008: changed ['/assertion']"
  ]
}
```

### 10. exit 0

```
python new_records.py --state state.json --patch patch.json edit AC-006 --replace-text '은 결제 대기로 남고' ' 상태는 결제 대기로 남고(실패는 이력 사건)'
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

### 11. exit 0

```
python open_revision.py state.json --patch patch.json --status READY_FOR_REVIEW --write
```

```json
{
  "added": [
    "UNK-060",
    "DEC-060"
  ],
  "cells": [],
  "changed": [
    "REQ-006",
    "REQ-008",
    "RULE-012",
    "RULE-013",
    "STATE-007",
    "FLOW-005",
    "AC-008",
    "AC-006",
    "SURF-008",
    "SURF-010",
    "SURF-011"
  ],
  "from_revision": 17,
  "refreshed": [
    {
      "cell": "coverage[5].cells.error",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "coverage[5].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[5].cells.state",
      "pointer": "/conditions",
      "record_id": "STATE-007"
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
      "cell": "coverage[6].cells.happy_path",
      "pointer": "/paths",
      "record_id": "FLOW-005"
    },
    {
      "cell": "coverage[6].cells.alternative_path",
      "pointer": "/paths",
      "record_id": "FLOW-005"
    },
    {
      "cell": "coverage[6].cells.error",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "coverage[6].cells.state",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "coverage[6].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "coverage[7].cells.error",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "coverage[7].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[7].cells.state",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "coverage[7].cells.validation",
      "pointer": "/assertion",
      "record_id": "AC-008"
    },
    {
      "cell": "coverage[7].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[7].cells.acceptance",
      "pointer": "/assertion",
      "record_id": "AC-008"
    },
    {
      "cell": "ux_coverage[3].states.success",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "ux_coverage[3].states.error",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "ux_coverage[3].states.offline",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].states.cancelled",
      "pointer": "/conditions",
      "record_id": "STATE-007"
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
      "pointer": "/conditions",
      "record_id": "STATE-007"
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
      "cell": "ux_coverage[3].actions[2].cells.cancel",
      "pointer": "/conditions",
      "record_id": "STATE-007"
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
      "cell": "ux_coverage[4].states.empty",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].states.error",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].states.disabled",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "ux_coverage[4].states.submitting",
      "pointer": "/paths",
      "record_id": "FLOW-005"
    },
    {
      "cell": "ux_coverage[4].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[0].cells.input",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[0].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[0].cells.failure",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[0].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-005"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.precondition",
      "pointer": "/conditions",
      "record_id": "STATE-007"
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
      "cell": "ux_coverage[4].actions[1].cells.failure",
      "pointer": "/conditions",
      "record_id": "STATE-007"
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
      "cell": "ux_coverage[4].actions[1].cells.cancel",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[4].actions[1].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-005"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.precondition",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.failure",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.cancel",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.back",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.refresh",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.duplicate_concurrent_action",
      "pointer": "/statement",
      "record_id": "RULE-012"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.duplicate_concurrent_action",
      "pointer": "/conditions",
      "record_id": "STATE-007"
    },
    {
      "cell": "ux_coverage[4].actions[2].cells.undo",
      "pointer": "/paths",
      "record_id": "FLOW-005"
    },
    {
      "cell": "ux_coverage[4].actions[2].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-012"
    }
  ],
  "status": "READY_FOR_REVIEW",
  "to_revision": 18,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "written": true
}
```
