# Product Definition

> canonical state.json revision 62 projection

## REQ-001
- Status: CURRENT
- Behavior: 고객은 촬영 인원을 필수 입력하고 수용 가능한 공간 하나를 독점하며 호환되는 장비를 품목별 수량으로 선택한다. 공간 수용 인원 초과는 선택과 확정에서 차단한다. 고객이 최종 확인을 누르면 선택 공간과 장비 수량 전체의 해당 시간 가용성을 하나의 원자적 작업으로 확인하고, 모두 가용할 때만 예약을 즉시 확정한다. 공간이 점유됐거나 전체 동시 예약의 장비 수량 합이 품목 가용 수량을 넘으면 예약을 생성하지 않고 최신 가용 시간을 다시 표시한다.
- Actor: USR-001
- Screens: SCR-001, SCR-004
- Rules: RULE-001, RULE-007, RULE-008, RULE-009, RULE-010, RULE-011, RULE-019, RULE-021
- Acceptance: AC-001, AC-002, AC-003, AC-013, AC-014, AC-015, AC-016, AC-017, AC-018, AC-019, AC-044, AC-045, AC-046, AC-050, AC-051, AC-052, AC-053, AC-054, AC-055

## REQ-002
- Status: CURRENT
- Behavior: 고객은 회원가입 없이 이메일로 받은 일회용 관리 링크를 사용해 자신의 예약 관리 화면에 접근한다. 새 링크 요청 시 새 토큰을 발급하고 이전 미사용 토큰을 폐기하며, 토큰은 한 번 사용된 뒤 짧은 관리 세션으로 전환된다.
- Actor: USR-001
- Screens: SCR-002, SCR-003
- Rules: RULE-002, RULE-003, RULE-004, RULE-005, RULE-006, RULE-013
- Acceptance: AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-012

## REQ-003
- Status: CURRENT
- Behavior: 운영자는 스튜디오 공통 요일별 반복 영업시간과 반복 일정보다 우선하는 날짜별 완전 휴무·연장·단축 예외를 설정한다. 변경안이 기존 확정 예약과 충돌하면 자동 취소하지 않고 충돌 목록을 보여주며 모든 충돌을 별도 처리하기 전까지 변경 확정을 막는다.
- Actor: USR-002
- Screens: SCR-005
- Rules: RULE-011, RULE-012
- Acceptance: AC-020, AC-021, AC-022, AC-023, AC-024, AC-025

## REQ-004
- Status: CURRENT
- Behavior: v1 고객 알림은 이메일만 사용한다. 예약 확정·변경·취소·운영자 조치와 관리 링크 이메일 각각을 업무 상태와 분리된 delivery record로 추적하며 발송 실패는 원래 업무 transaction을 롤백하지 않는다.
- Actor: USR-001
- Screens: SCR-006
- Rules: RULE-012, RULE-013
- Acceptance: AC-026, AC-027, AC-028

## REQ-005
- Status: CURRENT
- Behavior: 고객은 촬영 시작 정확히 48시간 전까지 온라인으로 예약을 취소할 수 있다. 그 이후에는 mutation 없이 운영자 문의를 안내한다. 운영자는 마감 이후에도 필수 사유를 기록해 취소할 수 있으며, 취소 상태 commit과 공간·장비 점유 해제는 원자적으로 완료된다.
- Actor: USR-001
- Screens: SCR-003, SCR-007
- Rules: RULE-014
- Acceptance: AC-029, AC-030, AC-031, AC-032

## REQ-006
- Status: CURRENT
- Behavior: 고객은 촬영 시작 정확히 48시간 전까지 횟수 제한 없이 예약의 촬영 인원·시간·공간·장비를 온라인 변경할 수 있다. 이후 Owner 또는 Staff는 필수 사유를 기록하고 고객이 해당 변경안의 이메일 동의 링크로 동의한 경우에만 변경할 수 있다. 동의 링크는 발급 후 24시간과 촬영 시작 중 먼저 오는 시점까지 유효하다. 모든 변경은 새 구성 전체를 commit 시 재검증하고 새 점유 확보와 기존 점유 해제를 원자적으로 처리하며 실패하면 기존 예약과 점유를 보존한다.
- Actor: USR-001
- Screens: SCR-003, SCR-004, SCR-008
- Rules: RULE-001, RULE-007, RULE-008, RULE-009, RULE-010, RULE-015, RULE-016
- Acceptance: AC-033, AC-034, AC-035, AC-036, AC-040, AC-041

## REQ-007
- Status: CURRENT
- Behavior: 고객에게 공간 시간당 요금과 장비 품목별 시간당 요금×수량을 30분 단위로 비례 계산한 금액을 표시한다. 버퍼는 과금하지 않는다. 예약 확정 시 구성요소와 총액을 가격 snapshot으로 고정하고 운영자 요금 변경은 기존 snapshot에 영향을 주지 않는다. 고객 예약 변경 시 기존 snapshot과 새 구성 총액의 차이를 확인시킨 뒤 새 snapshot을 확정한다. v1은 정가 KRW snapshot만 다루며 결제·환불 transaction, 결제사·수단, 할인 코드·패키지·회원 요금을 지원하지 않는다.
- Actor: USR-001
- Screens: SCR-001, SCR-008, SCR-009
- Rules: RULE-010, RULE-016, RULE-017, RULE-018, RULE-058
- Acceptance: AC-037, AC-038, AC-039, AC-040, AC-041, AC-042, AC-043, AC-226, AC-227, AC-228, AC-229

## REQ-008
- Status: CURRENT
- Behavior: v1의 예약·영업시간·48시간 변경·취소 마감·90일 한도·이메일 시간 표시는 모두 Asia/Seoul 기준으로 계산한다. 저장 시 절대 시각과 timezone 정보를 함께 보존하며 v1에는 timezone 변경 기능이 없다.
- Actor: USR-002
- Screens: 
- Rules: RULE-020
- Acceptance: AC-047, AC-048, AC-049

## REQ-009
- Status: CURRENT
- Behavior: 예약 종료 또는 취소 후 1년이 지나면 이름·이메일·전화번호·촬영 메모를 비가역 익명화한다. 예약 시간·공간·장비·가격 snapshot·상태·비식별 운영 통계는 유지한다. legal hold가 있는 예약은 해제 전까지 익명화를 보류한다.
- Actor: USR-002
- Screens: SCR-010
- Rules: RULE-023, RULE-024, RULE-025
- Acceptance: AC-056, AC-057, AC-058, AC-059, AC-060, AC-061

## REQ-010
- Status: CURRENT
- Behavior: 운영자는 Owner와 Staff 역할로 분리한다. Owner만 운영자 초대·비활성화·역할 변경, legal hold와 전체 감사 기록 조회를 수행한다. Staff는 예약과 공간·장비·영업시간·요금을 운영하지만 운영자 계정·legal hold는 다룰 수 없다. 두 역할의 개인정보 화면 조회는 업무상 필요한 예약에 한정되고 모두 append-only 감사 기록에 남는다. v1은 고객 개인정보 다운로드·CSV export·직접 파일 생성 API를 제공하지 않는다. Owner와 Staff는 Asia/Seoul 기준 핵심 운영 지표를 화면 조회하고 개인정보·예약 단위 행이 없는 최대 10,000행의 집계 CSV로 내보낼 수 있다.
- Actor: USR-003
- Screens: SCR-011, SCR-012, SCR-013, SCR-014
- Rules: RULE-024, RULE-025, RULE-026, RULE-027, RULE-028, RULE-029, RULE-030, RULE-031
- Acceptance: AC-062, AC-063, AC-064, AC-065, AC-066, AC-067, AC-068, AC-069, AC-070, AC-071, AC-072, AC-073, AC-074, AC-075, AC-076, AC-077, AC-078, AC-079, AC-080, AC-081, AC-082, AC-083, AC-084, AC-085, AC-086, AC-087, AC-088, AC-089, AC-090, AC-091, AC-092, AC-093, AC-094, AC-095

## REQ-011
- Status: CURRENT
- Behavior: Owner와 Staff는 공간·장비의 이름, 설명, 사진, 활성 상태, 공간 수용 인원, 장비 총수량, 2원 단위 시간당 요금과 공간-장비 호환성을 생성·수정·비활성화한다. 삭제는 제공하지 않고 기존 예약 snapshot과 점유를 유지한다. 확정 예약과 충돌하는 공간 수용 인원 하향, 장비 수량 감소 또는 자원 비활성화는 충돌 목록의 예약을 별도 처리하기 전까지 적용하지 않으며 모든 설정 변경을 감사한다.
- Actor: USR-002
- Screens: SCR-015
- Rules: RULE-008, RULE-018, RULE-032
- Acceptance: AC-096, AC-097, AC-098, AC-099, AC-100

## REQ-012
- Status: CURRENT
- Behavior: 촬영 시작 48시간 이후 고객 취소 요청은 mutation 없이 차단하고, 인증된 예약 관리 화면에서 예약 ID와 마감 사유가 자동 연결된 인앱 문의를 제공한다. 고객은 문의 내용을 필수 입력하며 앱에 양방향 상태형 thread를 생성한다. Owner·Staff는 답변하고 고객 답변 대기 또는 해결로 전환하며, 고객은 인증 화면에서 답변하고 해결 후 답변으로 다시 연다. 메시지·상태 전이를 감사하고 상대 이메일·운영자 앱 알림을 delivery record로 추적한다. thread 동작은 예약을 변경·취소하지 않는다.
- Actor: USR-001
- Screens: SCR-003, SCR-017
- Rules: RULE-014, RULE-036, RULE-037
- Acceptance: AC-115, AC-116, AC-117, AC-118, AC-119, AC-120, AC-121, AC-122, AC-123, AC-124

## REQ-013
- Status: CURRENT
- Behavior: 예약 확정 전에 이용약관, 48시간 취소·변경 정책, 안전수칙, 촬영 제한, 개인정보 수집 안내를 각각 표시하고 필수 동의를 받는다. Owner·Staff가 초안을 작성하되 Owner만 새 version을 발행·철회한다. 발행본은 즉시 신규 예약에 적용하고 이전 version은 불변 보존한다. 필수 문서 중 현재 발행본이 하나라도 없으면 신규 예약 확정을 차단하며 철회 시 이전 version으로 자동 복귀하지 않는다. 예약 snapshot에 각 문서 ID·version과 동의 시각을 저장한다.
- Actor: USR-001
- Screens: SCR-001, SCR-018, SCR-019
- Rules: RULE-038, RULE-039
- Acceptance: AC-125, AC-126, AC-127, AC-128, AC-129, AC-130, AC-131, AC-132, AC-133

## REQ-014
- Status: CURRENT
- Behavior: Owner·Staff는 필수 고객 이름·이메일·촬영 인원과 선택 전화번호·메모, 필수 등록 사유로 대리 예약안을 만든다. 온라인과 동일한 시간·수용 인원·공간·장비·가격·현재 정책 version을 검증해 자원을 15분 임시 hold하고 24시간 고객 확인 링크를 보낸다. 운영자는 정책 동의를 대신할 수 없으며 고객이 직접 필수 정책에 동의해야 최종 확정된다. 미동의·만료 시 hold를 해제하고 등록자·사유·상태 전이를 감사한다.
- Actor: USR-002
- Screens: SCR-020, SCR-018
- Rules: RULE-041
- Acceptance: AC-135, AC-136, AC-137, AC-138, AC-139, AC-140, AC-141, AC-142, AC-143, AC-144

## REQ-015
- Status: CURRENT
- Behavior: Owner·Staff가 장비를 고장·점검 불가로 전환하면 즉시 신규 예약 선택에서 제외하고 기존 확정 예약 충돌 목록을 생성한다. 운영자는 동급 대체 장비 또는 장비 제외 변경안을 기존 24시간 고객 동의 lifecycle로 제안하고 동의 후 전체 구성을 원자적으로 변경한다. 합의 실패 시 필수 사유로 운영자 취소한다. 자동 취소와 고객 동의 없는 교체는 금지하며 모든 전이·알림을 감사한다.
- Actor: USR-002
- Screens: SCR-021, SCR-016
- Rules: RULE-034, RULE-035, RULE-043
- Acceptance: AC-148, AC-149, AC-150, AC-151, AC-152, AC-153

## REQ-016
- Status: CURRENT
- Behavior: Owner·Staff는 필수 사유와 30분 경계로 전체 스튜디오, 특정 공간, 특정 장비 수량의 임시 차단을 생성·변경·해제한다. 차단은 예약 전후 버퍼와 함께 가용성에 반영한다. 기존 확정 예약과 충돌하면 즉시 적용하지 않고 각 예약에 예외 유지·24시간 고객 동의 변경·필수 사유 운영자 취소 중 하나를 처리한 뒤 확정한다. 모든 차단 lifecycle을 감사한다.
- Actor: USR-002
- Screens: SCR-022, SCR-016
- Rules: RULE-044
- Acceptance: AC-154, AC-155, AC-156, AC-157, AC-158, AC-159

## REQ-017
- Status: CURRENT
- Behavior: 모든 이메일 delivery는 최초 실패 후 1분·5분·30분에 최대 3회 자동 재시도한다. 계속 실패하면 운영자 앱 알림과 실패 큐에 표시하며 Owner·Staff가 원인을 확인한 뒤 수동 재발송할 수 있다. delivery event 고유키와 attempt 기록으로 중복 발송을 방지하고 delivery 실패는 예약·문의·변경 상태를 롤백하지 않는다.
- Actor: USR-002
- Screens: SCR-023
- Rules: RULE-045
- Acceptance: AC-160, AC-161, AC-162, AC-163, AC-164, AC-165

## REQ-018
- Status: CURRENT
- Behavior: v1 고객·운영자 화면, 정책 문서, 이메일은 한국어만 제공하고 WCAG 2.2 AA를 기준으로 한다. 모든 interactive workflow는 키보드 조작, 가시적 포커스, 스크린리더 이름, 오류-필드 연결, 충분한 대비, 동작 감소 선호, 200% 확대와 모바일 reflow를 지원한다.
- Actor: USR-001
- Screens: SCR-001, SCR-002, SCR-003, SCR-004, SCR-005, SCR-006, SCR-007, SCR-008, SCR-009, SCR-010, SCR-011, SCR-012, SCR-013, SCR-014, SCR-015, SCR-016, SCR-017, SCR-018, SCR-019, SCR-020, SCR-021, SCR-022, SCR-023
- Rules: RULE-047
- Acceptance: AC-170, AC-171, AC-172, AC-173, AC-174, AC-175, AC-176, AC-177

## REQ-019
- Status: CURRENT
- Behavior: 고객 관리 세션 만료 시 예약 변경안과 문의 작성 내용을 예약·고객 세션에 묶인 서버 암호화 draft로 2시간 보관한다. 새 관리 링크로 같은 예약을 재인증한 뒤에만 latest draft version을 복구하며 인증 비밀·토큰은 저장하지 않는다. 복구 후 성공 mutation, 고객 명시 폐기, 또는 2시간 만료 시 draft를 삭제한다.
- Actor: USR-001
- Screens: SCR-003, SCR-008, SCR-017, SCR-024
- Rules: RULE-004, RULE-048
- Acceptance: AC-178, AC-179, AC-180, AC-181, AC-182, AC-183

## REQ-020
- Status: CURRENT
- Behavior: 예약 종료·취소 후 1년에 delivery 수신 주소와 개인화 메시지 데이터를 비가역 익명화한다. event 유형·attempt·상태·시각·정제된 실패 원인 같은 비식별 delivery 기록은 3년 보관 후 삭제한다. 예약 legal hold는 두 기한을 모두 보류하며 provider payload·token은 장기 보관하지 않는다.
- Actor: USR-002
- Screens: SCR-010, SCR-023
- Rules: RULE-050
- Acceptance: AC-188, AC-189, AC-190, AC-191, AC-192

## REQ-021
- Status: CURRENT
- Behavior: append-only 운영·보안·개인정보 접근 감사 기록은 사건 시점부터 5년 보관 후 삭제한다. 포함된 고객 식별 필드는 해당 예약의 종료·취소 후 1년 익명화 시 함께 비식별화하되 행위 종류·운영자 역할·시각·대상 비식별 ID는 남긴다. 관련 legal hold는 삭제와 비식별화를 모두 보류한다.
- Actor: USR-003
- Screens: SCR-010, SCR-012
- Rules: RULE-051
- Acceptance: AC-193, AC-194, AC-195, AC-196, AC-197

## REQ-022
- Status: CURRENT
- Behavior: 고객은 새 관리 링크로 예약을 인증해 개인정보 삭제를 요청할 수 있다. 미래·진행 예약 요청은 완료 또는 취소까지 보류하고, 종료·취소 예약은 요청 후 30일 안에 고객 개인정보와 관련 delivery 식별 필드를 익명화한다. legal hold는 해제까지 처리를 보류한다. 비식별 예약·가격·자원·감사 기록은 유지하고 요청·보류·완료를 감사한다.
- Actor: USR-001
- Screens: SCR-003, SCR-025, SCR-010
- Rules: RULE-052
- Acceptance: AC-198, AC-199, AC-200, AC-201, AC-202, AC-203

## REQ-023
- Status: CURRENT
- Behavior: Owner·Staff는 예약에 연결된 파손·분실 사건의 설명, 사진, 금액 참고치, 처리 상태와 append-only 이력을 기록하고 고객에게 이메일로 안내한다. 고객 공유 내용과 고객에게 보이지 않는 Owner·Staff 전용 내부 메모는 권한·데이터 필드로 분리한다. 보증금 결제와 배상금 청구 transaction은 v1 범위 밖이다.
- Actor: USR-002
- Screens: SCR-026
- Rules: RULE-056
- Acceptance: AC-213, AC-214, AC-215, AC-216, AC-217, AC-218

## REQ-024
- Status: CURRENT
- Behavior: 촬영 시작 30분 후에도 도착하지 않으면 Owner·Staff가 필수 사유로 수동 노쇼 처리한다. 자동 전환은 없고 지각 도착도 원래 종료 시각을 연장하지 않으며 전후 버퍼 포함 자원 점유는 유지한다. 결제·위약금 없이 노쇼·지각 상태, 메모, 고객 이메일, 감사를 기록하고 잘못된 노쇼는 운영자가 필수 사유로 되돌릴 수 있다.
- Actor: USR-002
- Screens: SCR-027
- Rules: RULE-057
- Acceptance: AC-219, AC-220, AC-221, AC-222, AC-223, AC-224, AC-225

