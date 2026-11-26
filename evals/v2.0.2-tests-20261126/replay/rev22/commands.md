# Replay rev22: builder commands and their output

Base: revision 21 (committed). Target: revision 22 (committed).

### 1. exit 0

```
python new_records.py --state state.json --patch patch.json question --unknown UNK-069 --question '결제하기 뒤 구매자가 PG 결제창에서 인증하는 단계가 있는가? rev21은 서버 단독 승인 요청만 정의하고, 국내 PG 대부분은 구매자 결제창과 복귀 단계를 요구한다.' --why '결제창 단계가 없으면 어댑터 교체만으로 실제 PG를 붙일 수 없다(Stage 4 PG 접점 점검). 결제 흐름의 화면·상태·이력이 달라진다.' --category CORE_FLOW --materiality HIGH,MULTI_FLOW,true,COSTLY_TO_REVERSE,money --option 'OPT-WINDOW=결제하기 뒤 서버가 결제 대기 주문·재고 차감·결제 키를 만들고 구매자는 PG 결제창으로 간다(모의 어댑터는 사이트 안 모의 결제창 화면에 승인·실패·닫기 버튼, 시험 모드는 자동 진행). 성공 복귀 시 서버가 PG 금액과 주문 합계를 대조해 승인을 확정하고 결제 완료가 된다. 실패·닫기 복귀는 결제 대기 유지 + 실패 이력 + 다시 결제. 복귀 없이 떠나면 결제 대기(24시간 자동 취소). 금액 불일치는 승인 거부 + 실패 이력.|화면 하나(모의 결제창)와 단계 하나가 는다. 어댑터 교체만으로 실제 PG가 붙는다.' --option 'OPT-SERVER=현행 서버 단독 승인 요청을 유지하고 PG 연결 때 다시 정의한다.|PG 연결 때 결제 흐름을 다시 정의·구현해야 한다.' --affects SURF-008 --affects SURF-009 --affects SURF-011 --surface SURF-008 --recommend OPT-WINDOW --confidence HIGH --reason EVD-001 --tradeoff '모의 결제창은 데모에서 구매자가 한 번 더 누르는 단계가 된다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "UNK-069"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-069": "USER_DECISION_REQUIRED"
  }
}
```

### 2. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-069 --option OPT-WINDOW --summary '사용자 답(2026-11-25): "전부 추천대로" — 추천안 수락.' --statement '결제하기 뒤 서버는 가격 재계산 주문을 결제 대기로 만들고 재고를 차감하고 결제 키를 만든 뒤 구매자를 PG 결제창으로 보낸다(모의 어댑터는 사이트 안 모의 결제창 화면: 승인·실패·닫기 버튼, 시험 모드는 자동 진행). 성공 복귀 시 서버가 PG 금액과 주문 합계를 대조해 승인을 확정하고 결제 완료가 된다(확정을 기다리는 동안 처리 중 규칙 그대로). 실패·닫기 복귀는 결제 대기 유지 + 실패 이력 + 다시 결제(새 결제 키). 복귀 없이 떠난 주문은 결제 대기로 남아 24시간 자동 취소를 따른다. 금액 불일치는 승인 거부 + 실패 이력이다.' --decision DEC-069 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-069"
  ],
  "changed": [
    "SURF-008",
    "SURF-009",
    "SURF-011"
  ],
  "replaced": [
    "UNK-069"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-069",
      "option": "OPT-WINDOW",
      "decision": "DEC-069",
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
python new_records.py --state state.json --patch patch.json question --unknown UNK-070 --question 'PG 어댑터 경계(INT-001)는 어댑터 교체만으로 실제 PG가 붙을 만큼 완전한가? 현재 콜백 라우트가 모의 전용 메서드를 부르고, 승인 금액 대조와 지급 거절 인바운드 수신이 없으며, 시험 플래그가 운영 모드와 무관하게 켜진다.' --why '프로젝트 목표가 '"'"'PG만 붙이면 바로 쓸 수 있는'"'"' 수준이다. 경계가 불완전하면 교체 시 라우트·검증 코드를 새로 짜야 하고, 시험 플래그는 실제 결제를 환불할 위험이 있다(Stage 4 PG 접점 점검).' --category SCOPE_BOUNDARY --materiality MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money --option 'OPT-COMPLETE=인터페이스에 결제창 진입 정보 발급, 콜백·복귀 수신과 서명 검증, 승인 금액 대조, 지급 거절 인바운드 수신을 넣고, 시험 플래그는 시험 모드에서만 켜진다.|어댑터 교체만으로 PG가 붙는다. 모의 어댑터가 그 메서드를 모두 구현한다.' --option 'OPT-DEFER=현행 경계를 유지하고 PG 연결 때 처리한다.|교체 시 라우트·검증을 새로 짜야 하고 시험 플래그 위험이 남는다.' --affects SURF-009 --affects SURF-008 --surface SURF-009 --recommend OPT-COMPLETE --confidence HIGH --reason EVD-001 --tradeoff '모의 어댑터 코드가 늘고 콜백 서명 형식은 모의 기준으로 정해진다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "UNK-070"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-070": "USER_DECISION_REQUIRED"
  }
}
```

### 4. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-070 --option OPT-COMPLETE --summary '사용자 답(2026-11-25): "전부 추천대로" — 추천안 수락.' --statement 'PG 어댑터 경계(INT-001)는 결제창 진입 정보 발급, 콜백·복귀 수신과 서명 검증, 승인 금액과 주문 합계 대조, 지급 거절 인바운드 수신을 포함한다. 시험용 플래그(저장 실패 흉내 등)는 시험 모드에서만 켜지고 운영 모드에서는 무시된다. 어댑터 교체만으로 실제 PG가 붙어야 한다.' --decision DEC-070 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-070"
  ],
  "changed": [],
  "replaced": [
    "UNK-070",
    "SURF-008",
    "SURF-009"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-070",
      "option": "OPT-COMPLETE",
      "decision": "DEC-070",
      "resolution_mode": "USER_DECISION",
      "decision_authority": "USER_DECISION_REQUIRED",
      "open_authority_was": "USER_DECISION_REQUIRED",
      "why": "high risk: risk flags ['money']"
    }
  ],
  "notes": []
}
```

### 5. exit 0

```
python new_records.py --state state.json --patch patch.json question --unknown UNK-071 --question '1024px 이상 상품 상세에서 소재 설명·사이즈 표·배송 안내 접힘 영역은 어느 열에 두는가? RULE-009는 접힘 뒤에 둔다고만 하고 열은 정하지 않아, 정보 열이 담기에서 끝나고 그 아래가 비어 있다.' --why '첫 화면 오른쪽 절반이 비어 보인다(Stage 4 독립 비평). 내용 순서는 RULE-009 소관이다.' --category SECONDARY_BEHAVIOR --materiality LOW,LOCAL,true,REVERSIBLE --option 'OPT-INFO-COLUMN=1024 이상에서는 접힘 영역을 정보 열의 담기 아래에 둔다(내용 순서는 그대로). 그보다 좁으면 스테이지 아래 그대로.|정보 열이 담기 뒤로 이어지고 오른쪽 빈 열이 없어진다.' --option 'OPT-KEEP=접힘 영역을 스테이지 아래에 두고 오른쪽 열은 비워 둔다.|첫 화면 오른쪽 절반이 빈다.' --affects SURF-004 --surface SURF-004 --recommend OPT-INFO-COLUMN --confidence HIGH --reason EVD-001 --tradeoff '넓은 화면에서 접힘 영역이 스테이지보다 먼저 스크롤 밖으로 나가지 않도록 정보 열 고정 여부는 JOEDESIGN이 정한다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "UNK-071"
  ],
  "cells": [],
  "rows": [],
  "decision_authority": {
    "UNK-071": "USER_CONFIRMATION"
  }
}
```

### 6. exit 0

```
python new_records.py --state state.json --patch patch.json resolve UNK-071 --option OPT-INFO-COLUMN --summary '사용자 답(2026-11-25): "전부 추천대로" — 추천안 수락.' --statement '1024px 이상 상품 상세에서 소재 설명·사이즈 표·배송 안내 접힘 영역은 정보 열의 담기 아래에 둔다(내용 순서 그대로). 그보다 좁은 화면에서는 스테이지 아래에 둔다.' --decision DEC-071 --decision-type PRODUCT_BEHAVIOR
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [
    "DEC-071"
  ],
  "changed": [
    "SURF-004"
  ],
  "replaced": [
    "UNK-071"
  ],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [
    {
      "unknown": "UNK-071",
      "option": "OPT-INFO-COLUMN",
      "decision": "DEC-071",
      "resolution_mode": "USER_ACCEPTED_RECOMMENDATION",
      "decision_authority": "USER_CONFIRMATION",
      "open_authority_was": "USER_CONFIRMATION",
      "why": "material, not high-risk, with a HIGH-confidence recommendation"
    }
  ],
  "notes": []
}
```

### 7. exit 0

```
python new_records.py --state state.json --patch patch.json edit REQ-006 --replace-text '(승인/실패/취소 콜백)를 호출하며 기본 구현은 모의 승인 어댑터다(DEC-001' '에서 결제창 진입 정보를 받아 구매자를 PG 결제창으로 보내고, 성공 복귀 시 서버가 금액 대조 뒤 승인을 확정한다(DEC-069); 기본 구현은 모의 어댑터(사이트 안 모의 결제창)다(DEC-001). 어댑터 경계는 교체만으로 실제 PG가 붙도록 콜백 검증·금액 대조·지급 거절 수신을 포함한다(DEC-070'
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

### 8. exit 0

```
python new_records.py --state state.json --patch patch.json edit REQ-008 --replace-text '승인 요청 직후 주문은 결제 대기가 되고' '결제하기 직후 주문은 결제 대기가 되고 구매자는 PG 결제창으로 간다(DEC-069); 성공 복귀 뒤 서버가 금액 대조로 승인을 확정하는 동안'
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

### 9. exit 0

```
python new_records.py --state state.json --patch patch.json edit RULE-009 --replace-text ' 뒤에 둔다. 사이즈 표는 선' ' 뒤에 둔다. 1024px 이상에서는 접힘 영역이 정보 열의 담기 아래에 오고, 그보다 좁으면 스테이지 아래에 온다(DEC-071). 사이즈 표는 선'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "RULE-009"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "RULE-009: changed ['/statement']"
  ]
}
```

### 10. exit 0

```
python new_records.py --state state.json --patch patch.json edit RULE-011 --replace-text 'STATE-005(처리 중, 잠금, 폴링), 30초 뒤 STATE-006(확인 중, 주문 상세로 가기). 실패하면' '구매자는 PG 결제창으로 간다(모의 어댑터는 사이트 안 모의 결제창: 승인·실패·닫기, DEC-069). 성공 복귀 뒤 STATE-005(처리 중, 잠금, 폴링), 30초 뒤 STATE-006(확인 중, 주문 상세로 가기). 실패·닫기 복귀나 승인 실패는'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "RULE-011"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "RULE-011: changed ['/statement']"
  ]
}
```

### 11. exit 0

```
python new_records.py --state state.json --patch patch.json edit RULE-013 --replace-text '어댑터 승인을 요청한다. 같은 키의 콜백은 첫 결과만 반영하고 중복은 이력에 기록한다. 상태 전이는 STATE-007 허용 표로만 한다. 처리 중은 2초 폴링 최대 30초, 초과 시 결제 확인 중. 자동 재시도 없음, 사용자가 다시 결제한다(새 결제 키). 확인 중 주문에 늦게 온 승인은 결제 완료로 반영하되 이미 취소됐으면 즉시 환불 호출한다. 승인 뒤 주문 확정 저장이 실패하면 환불 호출 후 주문을 결제 대기로 되돌리고 실패를 이력에 남긴다(부분 완료 없음). 결제 실패는 상태가 아니라 이력 사건이며 실패 콜백·조회 실패 뒤에도 주문은 결제 대기다(DEC-060). 결제 대기·확인 중 주문은 사용자가 취소할 수 있고 승인 전이면 환불 없이 취소된다. 확인 중 주문의 권위는 어댑터 상태 조회이며 모의 어댑터는 즉시 응답한다' '결제창 진입 정보를 받아 구매자를 PG 결제창으로 보낸다. 성공 복귀 시 서버가 PG 금액과 주문 합계를 대조해 승인을 확정하고, 불일치면 거부하고 실패를 이력에 남긴다(DEC-069). 실패·닫기 복귀와 복귀 없는 이탈은 결제 대기 유지다. 같은 키의 콜백은 첫 결과만 반영하고 중복은 이력에 기록한다. 상태 전이는 STATE-007 허용 표로만 한다. 처리 중(승인 확정 대기)은 2초 폴링 최대 30초, 초과 시 결제 확인 중. 자동 재시도 없음, 사용자가 다시 결제한다(새 결제 키). 확인 중 주문에 늦게 온 승인은 결제 완료로 반영하되 이미 취소됐으면 즉시 환불 호출한다. 승인 뒤 주문 확정 저장이 실패하면 환불 호출 후 주문을 결제 대기로 되돌리고 실패를 이력에 남긴다(부분 완료 없음). 결제 실패는 상태가 아니라 이력 사건이며 실패 콜백·조회 실패 뒤에도 주문은 결제 대기다(DEC-060). 결제 대기·확인 중 주문은 사용자가 취소할 수 있고 승인 전이면 환불 없이 취소된다. 확인 중 주문의 권위는 어댑터 상태 조회이며 모의 어댑터는 즉시 응답한다. 어댑터 경계는 콜백·복귀 서명 검증, 금액 대조, 지급 거절 인바운드 수신을 포함하고 시험용 플래그는 시험 모드에서만 켜진다(DEC-070)'
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

### 12. exit 0

```
python new_records.py --state state.json --patch patch.json edit STATE-005 --replace-text '승인 요청을 보냈고 결과가 아직 없다. 주문 상태는 결제 대기다' '결제창에서 성공 복귀했고 서버의 승인 확정 결과가 아직 없다. 주문 상태는 결제 대기다(DEC-069)'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "STATE-005"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "STATE-005: changed ['/conditions/0']"
  ]
}
```

### 13. exit 0

```
python new_records.py --state state.json --patch patch.json edit FLOW-003 --replace-text ' 승인을 요청한다. 장바구니 표시가와 재계산 금액이 다르면 승인' '에서 결제창 진입 정보를 받아 구매자를 PG 결제창으로 보낸다(모의 어댑터는 사이트 안 모의 결제창, DEC-069). 장바구니 표시가와 재계산 금액이 다르면 결제창' --replace-text '결과를 기다리는 ' '결제창에서 성공 복귀하면 서버가 PG 금액과 주문 합계를 대조해 승인을 확정한다(불일치는 거부 + 실패 이력). 확정 결과를 기다리는 ' --replace-text '실패하면 주문은 결제 대기로 남고 주문서에 실패 안내와 다시 결제 버튼이 나온' '결제창에서 실패·닫기로 복귀하거나 승인이 실패하면 주문은 결제 대기로 남고 주문서에 실패 안내와 다시 결제 버튼이 나온다. 복귀 없이 떠난 주문도 결제 대기로 남는'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "FLOW-003"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "FLOW-003: changed ['/paths/3', '/paths/4', '/paths/6']"
  ]
}
```

### 14. exit 0

```
python new_records.py --state state.json --patch patch.json edit SCR-004 --replace-text '결제를 요청하고,' '구매자를 PG 결제창(모의는 사이트 안 모의 결제창)으로 보내고, 복귀 뒤'
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

### 15. exit 0

```
python new_records.py --state state.json --patch patch.json edit DATA-006 --replace-text ' 기록: 종류(승인 요청, 승인·' ' 기록: 종류(결제창 진입 정보 발급, 결제창 복귀, 승인 확정 요청, 승인·'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "DATA-006"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "DATA-006: changed ['/purpose']"
  ]
}
```

### 16. exit 0

```
python new_records.py --state state.json --patch patch.json edit INT-001 --replace-text '승인 요청(주문별 결제 키와 결제수단 이름 포함, DEC-065), 승인·실패·취소 콜백, 환불 호출, 상태 조회, 지급 거절 이벤트, 메일 발송 이벤트 기록(DEC-001, DEC-017, DEC-022, DEC-023, DEC-026, DEC-028). 기본 구현은 모의 어댑터로 승인·환불 즉시 성공과 실패·지연을 시험용으로 흉내 낼 수 있어야 한다. PG를 붙이는 일은 이 인터페이스의 구현 교체다' '결제창 진입 정보 발급(주문별 결제 키와 결제수단 이름 포함, DEC-065, DEC-069), 결제창 복귀와 승인·실패·취소 콜백의 수신과 서명 검증, 승인 금액과 주문 합계 대조, 승인 확정 요청, 환불 호출, 상태 조회, 지급 거절 인바운드 수신, 메일 발송 이벤트 기록(DEC-070)(DEC-001, DEC-017, DEC-022, DEC-023, DEC-026, DEC-028). 기본 구현은 모의 어댑터로, 사이트 안 모의 결제창(승인·실패·닫기)과 승인·환불 즉시 성공, 실패·지연을 시험용으로 흉내 낼 수 있어야 한다. 시험용 플래그는 시험 모드에서만 켜진다(DEC-070). PG를 붙이는 일은 이 인터페이스의 구현 교체이며 라우트·검증 코드를 새로 짜지 않는다(DEC-070)'
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

### 17. exit 0

```
python new_records.py --state state.json --patch patch.json edit AC-002 --replace-text ' 없이 보인다.' ' 없이 보인다. 1024px 이상에서 접힘 영역은 정보 열의 담기 아래에 있다.'
```

```json
{
  "written": true,
  "patch": "patch.json",
  "added": [],
  "changed": [
    "AC-002"
  ],
  "replaced": [],
  "cells": [],
  "rows": [],
  "grill_profile": [],
  "derived": [],
  "notes": [
    "AC-002: changed ['/assertion']"
  ]
}
```

### 18. exit 0

```
python new_records.py --state state.json --patch patch.json edit AC-006 --replace-text '처리 중 화면에서 버튼이 잠기고 모의 승인 어댑터가 승인하면 주문은 결제 완료, 장바구니는 비워지고 주문 완료 화면에 주문번호·금액·배송지·조회 안내가 보인다. 어댑터가 실패를 돌려주면 주문 상태는 결제 대기로 남고(실패는 이력 사건) 실패 안내와 다시 결제가 보이며 다시 결제는 새 결제 키를 쓴다. 같은 결제 키의 중복 콜백은 무시되고 이력에 기록된' '모의 결제창(승인·실패·닫기)이 열리고, 승인으로 복귀하면 처리 중 화면에서 버튼이 잠기고 서버가 금액 대조 뒤 승인을 확정해 주문은 결제 완료, 장바구니는 비워지고 주문 완료 화면에 주문번호·금액·배송지·조회 안내가 보인다. 결제창에서 실패나 닫기로 복귀하거나 승인 확정이 실패하면 주문 상태는 결제 대기로 남고(실패는 이력 사건) 실패 안내와 다시 결제가 보이며 다시 결제는 새 결제 키를 쓴다. 같은 결제 키의 중복 콜백은 무시되고 이력에 기록된다. 복귀 금액이 주문 합계와 다르면 승인이 거부되고 실패 이력이 남는다. 시험용 플래그는 시험 모드에서만 작동한'
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

### 19. exit 0

```
python open_revision.py state.json --patch patch.json --status READY_FOR_REVIEW --write
```

```json
{
  "added": [
    "UNK-069",
    "UNK-070",
    "UNK-071",
    "DEC-069",
    "DEC-070",
    "DEC-071"
  ],
  "cells": [],
  "changed": [
    "REQ-006",
    "REQ-008",
    "RULE-009",
    "RULE-011",
    "RULE-013",
    "STATE-005",
    "FLOW-003",
    "SCR-004",
    "DATA-006",
    "INT-001",
    "AC-002",
    "AC-006",
    "SURF-008",
    "SURF-009",
    "SURF-011",
    "SURF-004"
  ],
  "from_revision": 21,
  "refreshed": [
    {
      "cell": "coverage[1].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "coverage[1].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "coverage[1].cells.acceptance",
      "pointer": "/assertion",
      "record_id": "AC-002"
    },
    {
      "cell": "coverage[3].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "coverage[4].cells.happy_path",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "coverage[4].cells.alternative_path",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "coverage[5].cells.happy_path",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "coverage[5].cells.alternative_path",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "coverage[5].cells.error",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "coverage[5].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[5].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "coverage[5].cells.state",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "coverage[5].cells.data",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "coverage[5].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "coverage[5].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-011"
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
      "cell": "coverage[6].cells.data",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "coverage[6].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "coverage[7].cells.happy_path",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "coverage[7].cells.alternative_path",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "coverage[7].cells.recovery",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "coverage[7].cells.state",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "coverage[7].cells.data",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "coverage[7].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "INT-001"
    },
    {
      "cell": "coverage[7].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "coverage[7].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[1].states.empty",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].states.cancelled",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[0].cells.offline",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[0].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[1].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[2].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[3].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[3].cells.offline",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[3].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[4].cells.cancel",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[4].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[1].actions[4].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-009"
    },
    {
      "cell": "ux_coverage[2].states.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[2].states.submitting",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[2].states.completed",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[2].actions[0].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[2].actions[1].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[2].actions[2].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[2].actions[2].cells.undo",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].states.partial",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].states.success",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "ux_coverage[3].states.disabled",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "ux_coverage[3].states.unauthenticated",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[3].states.offline",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].states.retrying",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "ux_coverage[3].states.submitting",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "ux_coverage[3].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[0].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[3].actions[0].cells.input",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[0].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[0].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[1].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[3].actions[1].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.success",
      "pointer": "/assertion",
      "record_id": "AC-006"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.validation",
      "pointer": "/statement",
      "record_id": "RULE-011"
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
      "cell": "ux_coverage[3].actions[2].cells.submit",
      "pointer": "/paths",
      "record_id": "FLOW-003"
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
      "cell": "ux_coverage[3].actions[2].cells.back",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.back",
      "pointer": "/paths",
      "record_id": "FLOW-003"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.refresh",
      "pointer": "/conditions",
      "record_id": "STATE-005"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.duplicate_concurrent_action",
      "pointer": "/statement",
      "record_id": "RULE-013"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.duplicate_concurrent_action",
      "pointer": "/conditions",
      "record_id": "STATE-005"
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
      "cell": "ux_coverage[3].actions[2].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "ux_coverage[3].actions[2].cells.destructive_confirmation",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[3].actions[2].default_authority",
      "pointer": "/statement",
      "record_id": "RULE-011"
    },
    {
      "cell": "ux_coverage[4].actions[1].cells.success",
      "pointer": "/paths",
      "record_id": "FLOW-003"
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
    },
    {
      "cell": "ux_coverage[5].actions[0].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    },
    {
      "cell": "ux_coverage[5].actions[2].cells.side_effect",
      "pointer": "/purpose",
      "record_id": "DATA-006"
    }
  ],
  "status": "READY_FOR_REVIEW",
  "to_revision": 22,
  "unresolved": [],
  "validation_errors": [],
  "version_notice": "this project does not record which JOEFLOW version it uses; running 2.0.2. Record it once with joeflow_version.py STATE_JSON --pin (writes joeflow-project.json next to state.json) and use the scripts of that version",
  "written": true
}
```
