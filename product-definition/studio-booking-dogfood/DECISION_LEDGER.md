# Decision Ledger

> canonical state.json revision 62 projection

## DEC-001
- Status: ANSWERED
- Decision: 고객의 최종 확인 시점에 공간과 선택 장비 전체가 가용하면 예약을 즉시 확정한다.
- Reason: 사용자가 즉시 확정 모델과 원자적 가용성 조건을 선택했다.

## DEC-002
- Status: ANSWERED
- Decision: 결제는 v1 제품 범위에서 제외한다.
- Reason: 사용자가 결제의 v1 제외를 명시했다.

## DEC-003
- Status: ANSWERED
- Decision: 고객 예약 관리 인증은 회원가입 없이 이메일 일회용 링크로 한다. 새 요청은 이전 미사용 토큰을 폐기하고, 토큰 사용은 짧은 관리 세션을 만든다.
- Reason: 사용자가 비회원 이메일 일회용 링크 방식과 토큰 수명주기 동작을 선택했다.

## DEC-004
- Status: ANSWERED
- Decision: 이메일 일회용 관리 링크는 발급 후 15분간 유효하며, 만료·사용·폐기 사유를 구분하지 않는 중립 메시지로 새 링크 요청을 안내한다.
- Reason: 사용자가 토큰 만료 시간과 무효 링크 정보 비노출 동작을 명시했다.

## DEC-005
- Status: ANSWERED
- Decision: 관리 세션은 링크 사용 시점부터 30분간 유효하다. 변경·취소 mutation 제출 시 서버가 만료를 재검사하고, 만료된 경우 변경 없이 재인증과 직전 입력 복구를 제공한다.
- Reason: 사용자가 세션 만료 시간과 만료 경계의 무변경·복구 동작을 명시했다.

## DEC-006
- Status: ANSWERED
- Decision: 관리 링크 재발급은 이메일별 60초에 1회 및 시간당 5회로 제한한다. 초과 시 토큰·메일을 만들지 않고 중립 응답과 재시도 가능 시점을 표시하며, 새 토큰 발급 성공 시에만 이전 미사용 토큰을 폐기한다.
- Reason: 사용자가 재발급 한도, 초과 동작, 기존 토큰 폐기 순서를 명시했다.

## DEC-007
- Status: ANSWERED
- Decision: 관리 링크 요청은 명백한 이메일 형식 오류만 필드 수준에서 알리고, 유효한 형식에는 예약 존재 여부와 무관하게 같은 중립 응답을 표시한다. 예약이 없으면 토큰과 메일을 만들지 않는다.
- Reason: 사용자가 형식 검증과 존재 여부 비노출 경계를 명시했다.

## DEC-008
- Status: ANSWERED
- Decision: 한 예약은 공간 하나를 독점하고 장비는 품목별 요청 수량을 점유한다. 동시간대 장비 요청 합은 품목 가용 수량을 넘을 수 없으며 운영자 정의 공간·장비 호환성을 선택 단계에서 강제한다.
- Reason: 사용자가 공간·장비 점유 단위와 호환성 통제를 명시했다.

## DEC-009
- Status: ANSWERED
- Decision: 예약 시작과 종료는 30분 경계이고 예약 길이는 1시간 이상 8시간 이하다. 예약 구간과 준비·정리 버퍼 전체가 영업시간 안에 있어야 한다.
- Reason: 사용자가 시간 간격, 길이 경계 및 버퍼 포함 영업시간 조건을 명시했다.

## DEC-010
- Status: ANSWERED
- Decision: 예약 전 30분과 후 30분 버퍼가 공간과 선택 장비를 점유한다. 버퍼는 고객 촬영 시간과 별도로 안내하고 비용 계산에서는 제외한다.
- Reason: 사용자가 버퍼 길이, 점유 대상, 고객 표시와 비용 제외를 명시했다.

## DEC-011
- Status: ANSWERED
- Decision: 영업시간은 스튜디오 공통 요일별 반복 일정과 우선순위가 더 높은 날짜별 완전 휴무·연장·단축 예외로 관리한다. 기존 확정 예약 충돌 시 자동 취소하지 않고 충돌을 별도 처리하기 전까지 변경 확정을 막는다.
- Reason: 사용자가 영업시간 모델, 예외 우선순위와 충돌 안전장치를 명시했다.

## DEC-012
- Status: ANSWERED
- Decision: 영업시간 충돌 예약마다 예외 유지·고객 협의 후 변경·운영자 취소 중 하나와 사유를 기록해야 변경을 확정한다. 예외 유지는 해당 예약과 자원 점유에만 적용한다. 변경·취소 알림 실패는 상태 변경을 롤백하지 않는다.
- Reason: 사용자가 충돌 해소 방식, 예외 범위, 알림과 상태 변경의 경계를 명시했다.

## DEC-013
- Status: ANSWERED
- Decision: v1 고객 알림은 이메일만 사용하며 예약 확정·변경·취소·운영자 조치와 관리 링크마다 업무 상태와 분리된 delivery record를 만든다. 발송 실패는 예약 transaction을 롤백하지 않는다.
- Reason: 사용자가 알림 채널, 대상 이벤트, 전달 추적과 transaction 경계를 명시했다.

## DEC-014
- Status: SUPERSEDED
- Decision: 고객 온라인 취소는 촬영 시작 정확히 24시간 전까지 허용하고 이후에는 mutation 없이 운영자 문의를 안내한다. 운영자는 이후에도 필수 사유를 기록해 취소할 수 있으며 자원 해제는 취소 commit과 원자적이다.
- Reason: 사용자가 취소 마감 경계, 운영자 예외와 자원 해제 transaction을 명시했다.

## DEC-015
- Status: SUPERSEDED
- Decision: 고객 온라인 예약 변경은 촬영 시작 정확히 24시간 전까지 횟수 제한 없이 허용한다. 새 시간·공간·장비 전체를 재검증하고 새 점유 확보와 기존 점유 해제를 원자적으로 commit하며 실패하면 기존 예약을 보존한다.
- Reason: 사용자가 변경 경계, 횟수, 검증 범위와 transaction 실패 동작을 명시했다.

## DEC-016
- Status: ANSWERED
- Decision: 고객 온라인 취소는 촬영 시작 정확히 48시간 전까지 허용하고 이후에는 mutation 없이 운영자 문의를 안내한다. 운영자는 이후에도 필수 사유를 기록해 취소할 수 있으며 자원 해제는 취소 commit과 원자적이다.
- Reason: 사용자가 운영 보호를 위해 기존 24시간 취소 마감을 48시간으로 명시 변경했다.

## DEC-017
- Status: ANSWERED
- Decision: 고객 온라인 예약 변경은 촬영 시작 정확히 48시간 전까지 횟수 제한 없이 허용한다. 새 시간·공간·장비 전체를 재검증하고 새 점유 확보와 기존 점유 해제를 원자적으로 commit하며 실패하면 기존 예약을 보존한다.
- Reason: 사용자가 운영 보호를 위해 기존 24시간 변경 마감을 48시간으로 명시 변경했다.

## DEC-018
- Status: ANSWERED
- Decision: 공간 시간당 요금과 장비 품목별 시간당 요금에 장비 수량을 곱해 30분 단위로 비례 계산하고 버퍼는 과금하지 않는다. 예약 확정 시 구성요소와 총액을 snapshot으로 고정하며 변경 시 기존과 새 총액 차이를 확인한 뒤 새 snapshot을 확정한다.
- Reason: 사용자가 가격 공식, snapshot 불변성과 예약 변경 시 가격 갱신 절차를 명시했다.

## DEC-019
- Status: ANSWERED
- Decision: v1 가격 표시와 snapshot은 KRW만 사용하고 정수 원 단위로 저장하며 화면에는 ₩와 천 단위 구분을 표시한다.
- Reason: 사용자가 단일 통화, 저장 단위와 표시 형식을 명시했다.

## DEC-020
- Status: ANSWERED
- Decision: v1 가격은 입력 요금에 세금이 포함된 총액으로 취급하고 별도 부가세 계산·분리는 범위에서 제외한다.
- Reason: 사용자가 세금 포함 표시와 v1 제외 범위를 명시했다.

## DEC-021
- Status: ANSWERED
- Decision: 시간당 요금은 2원 단위 정수만 허용하며 홀수 원 입력을 거부하고 저장 실패 시 기존 유효 요금을 보존한다.
- Reason: 사용자가 30분 비례 금액의 정수 원 보장과 실패 시 보존 동작을 명시했다.

## DEC-022
- Status: ANSWERED
- Decision: 현재 스튜디오 현지 날짜의 오늘부터 포함 90일째 날짜까지 고객 예약 슬롯을 표시하고 확정할 수 있다. 범위 밖은 슬롯을 숨기되 이미 확정된 예약의 유지·관리는 허용한다.
- Reason: 사용자가 미래 예약 한도, 포함 경계와 기존 예약 예외를 명시했다.

## DEC-023
- Status: ANSWERED
- Decision: v1 timezone은 Asia/Seoul로 고정하고 모든 시간 계산·표시에 적용하며 절대 시각과 timezone 정보를 함께 저장한다. v1은 timezone 변경 기능을 제공하지 않는다.
- Reason: 사용자가 단일 timezone, 저장 표현과 변경 제외 범위를 명시했다.

## DEC-024
- Status: ANSWERED
- Decision: 새 예약은 촬영 시작 정확히 2시간 전까지 허용한다. 이후 슬롯과 확정을 막고 최종 확정 시 서버 시각 재검사에서 경계를 넘으면 선택을 보존한 채 가능한 다음 슬롯을 표시한다.
- Reason: 사용자가 최소 사전 예약 경계와 경계 초과 복구 동작을 명시했다.

## DEC-025
- Status: ANSWERED
- Decision: 예약 고객 이름·이메일은 필수이고 전화번호·촬영 메모는 선택이다. 이름은 운영 식별과 이메일 개인화에만 사용하고 전화번호는 SMS에 사용하지 않으며 최종 확인 전에 목적과 필수·선택을 표시한다.
- Reason: 사용자가 수집 필드, 필수성, 용도 제한과 고지 시점을 명시했다.

## DEC-026
- Status: ANSWERED
- Decision: 예약 종료 또는 취소 후 1년이 지나면 이름·이메일·전화번호·촬영 메모를 비가역 익명화하고 비식별 예약·가격·운영 데이터는 유지한다. legal hold가 있으면 해제 전까지 익명화를 보류한다.
- Reason: 사용자가 개인정보 보관 기간, 익명화 범위, 유지 데이터와 legal hold 예외를 명시했다.

## DEC-027
- Status: ANSWERED
- Decision: 최고 권한 운영자만 예약 단위 legal hold를 설정·해제할 수 있고 필수 사유·참조 및 append-only 전후 상태 감사를 남긴다. hold는 고객 개인정보와 관련 delivery·감사 기록에 함께 적용한다.
- Reason: 사용자가 legal hold 권한, 필수 증빙, 감사 불변성과 적용 범위를 명시했다.

## DEC-028
- Status: ANSWERED
- Decision: 운영자 역할은 Owner와 Staff다. Owner만 계정·역할, legal hold, 전체 감사를 관리하고 Staff는 예약·자원·영업시간·요금을 운영한다. 두 역할의 업무상 필요한 예약 개인정보 조회·다운로드는 모두 감사한다.
- Reason: 사용자가 역할, 전용 권한, Staff 운영 범위와 개인정보 접근 감사를 명시했다.

## DEC-029
- Status: ANSWERED
- Decision: Owner와 Staff는 이메일·비밀번호와 필수 TOTP MFA로 로그인한다. Owner 초대 후 초대 주소 확인·비밀번호 설정·TOTP 등록·복구 코드 발급을 모두 완료해야 활성화된다.
- Reason: 사용자가 운영자 인증 요소와 계정 활성화 게이트를 명시했다.

## DEC-030
- Status: ANSWERED
- Decision: 비밀번호·TOTP 연속 실패 합계 5회면 15분 잠그고 성공 시 초기화한다. Owner는 사유를 남겨 다른 Staff 잠금만 해제하며 실패·잠금·해제를 감사하고 존재하지 않는 계정 응답·지연을 동일하게 한다.
- Reason: 사용자가 잠금 임계값, 해제 권한, 감사와 계정 열거 방지를 명시했다.

## DEC-031
- Status: ANSWERED
- Decision: TOTP 복구 코드는 10개 일회용으로 한 번만 표시·다운로드하고 해시 저장한다. 사용 즉시 폐기하고 비밀번호 재인증 후 새 세트를 발급하면 기존 미사용 코드를 모두 폐기하며 사용·재발급을 감사한다.
- Reason: 사용자가 복구 코드 개수, 보관·사용·재발급과 감사 규칙을 명시했다.

## DEC-032
- Status: ANSWERED
- Decision: 운영자 비밀번호 재설정은 15분 이메일 링크와 TOTP 또는 미사용 복구 코드 확인을 모두 요구한다. 요청은 계정 존재를 숨기고 새 링크 발급 성공 시 이전 링크를 폐기하며 성공 시 모든 운영 세션을 폐기·감사한다.
- Reason: 사용자가 재설정 인증 요소, 링크 수명주기, 열거 방지와 세션 폐기를 명시했다.

## DEC-033
- Status: ANSWERED
- Decision: 운영자 초대 링크는 24시간 유효하다. 새 초대 발급 성공 시에만 이전 미사용 링크를 폐기하고 활성·비활성 계정에는 권한을 부여하지 않으며 수명주기 행위를 감사한다.
- Reason: 사용자가 초대 만료, 안전한 재발급, 계정 상태 제한과 감사를 명시했다.

## DEC-034
- Status: ANSWERED
- Decision: Staff 개인정보 접근은 미래·진행 및 종료·취소 후 90일까지다. 이후 익명화 전 예약은 Owner가 필수 사유로만 접근하며 legal hold는 Staff 범위를 넓히지 않고 모든 허용·거부를 감사한다.
- Reason: 사용자가 역할별 개인정보 접근 기간, Owner 예외와 legal hold 비확장을 명시했다.

## DEC-035
- Status: ANSWERED
- Decision: v1은 Owner·Staff 모두 고객 개인정보 다운로드·CSV export·브라우저 직접 파일 생성 API를 금지하고 권한 범위의 화면 조회만 허용한다. 비식별 집계 운영 지표 export만 별도 허용한다.
- Reason: 사용자가 개인정보 반출 금지와 비식별 집계 예외를 명시했다.

## DEC-036
- Status: ANSWERED
- Decision: v1 핵심 운영 지표는 예약 건수, 취소 건수·취소율, 예약 촬영시간, 공간·장비 가동률, 가격 snapshot 총액이다. Owner와 Staff는 이를 Asia/Seoul 기준 일·주·월 및 공간·장비별로 화면 조회하고, 개인정보와 예약 단위 행을 제외한 최대 10,000행의 집계 CSV로 내려받을 수 있다.
- Reason: 사용자가 핵심 운영 지표와 집계·권한·export 경계를 명시했다.

## DEC-037
- Status: ANSWERED
- Decision: Owner와 Staff는 공간·장비의 운영 필드를 생성·수정·비활성화할 수 있다. 물리 삭제는 제공하지 않고 기존 예약 snapshot·점유를 보존하며, 확정 예약과 충돌하는 장비 수량 감소나 자원 비활성화는 충돌 예약 처리 전 차단한다. 모든 설정 변경을 감사한다.
- Reason: 사용자가 전체 운영 관리 범위와 기존 예약 보호 경계를 명시했다.

## DEC-038
- Status: ANSWERED
- Decision: 촬영 인원은 예약 필수 입력이며 선택 공간 수용 인원을 넘을 수 없다. 신규 확정, 고객 변경, 운영자 변경에서 재검증하고 예약 snapshot에 보존한다. 기존 예약 인원보다 낮게 공간 수용 인원을 변경하는 설정은 충돌 처리 전 차단한다.
- Reason: 사용자가 수용 인원 강제 범위와 기존 예약 보호를 명시했다.

## DEC-039
- Status: ANSWERED
- Decision: 촬영 시작 48시간 이후 Owner·Staff 예약 변경은 필수 사유와 고객의 변경안별 이메일 동의가 필요하다. 링크는 발급 후 24시간 또는 촬영 시작 중 먼저 오는 시점까지 유효하며 commit 시 전체 구성을 재검증해 원자적으로 교체한다. 실패하면 기존 예약을 보존하고 모든 lifecycle 사건을 감사한다.
- Reason: 사용자가 마감 후 운영자 변경의 동의·만료·transaction·감사 경계를 명시했다.

## DEC-040
- Status: ANSWERED
- Decision: 예약당 활성 운영자 변경안은 하나다. 새 토큰 발급과 이메일 요청 성공 후에만 이전 미사용 링크를 폐기한다. 고객 거절은 기존 예약을 유지한 채 변경안을 종료하고 재제안을 허용한다. 동의·거절 시 latest proposal version이 아니면 mutation 없이 거부한다.
- Reason: 사용자가 변경안 재발급·거절·stale 링크의 transaction 경계를 명시했다.

## DEC-041
- Status: ANSWERED
- Decision: 48시간 이후 취소 차단 화면은 인증된 예약과 마감 사유가 연결된 필수 내용의 인앱 문의 thread를 생성한다. 운영자 이메일·앱 알림과 고객 접수 확인을 delivery record로 추적하며 문의만으로 예약 mutation을 수행하지 않는다.
- Reason: 사용자가 마감 후 문의 채널·데이터·알림·mutation 경계를 명시했다.

## DEC-042
- Status: ANSWERED
- Decision: 예약 문의는 Owner·Staff와 인증 고객의 양방향 상태형 thread다. 운영자는 고객 답변 대기 또는 해결로 전환하고, 해결 후 고객 답변은 다시 연다. 메시지·상태 전이를 감사하고 상대 이메일·운영자 앱 알림 delivery를 추적하며 예약 상태에는 영향을 주지 않는다.
- Reason: 사용자가 문의 대화·상태·재개·알림·예약 불변 경계를 명시했다.

## DEC-043
- Status: ANSWERED
- Decision: 예약 확정 전 다섯 정책 문서를 각각 표시하고 필수 동의하며 문서 ID·version·동의 시각을 예약 snapshot에 고정한다. 정책 변경은 기존 기록을 수정하지 않고 고객에게 불리한 핵심 의무는 재동의 없이 소급하지 않는다.
- Reason: 사용자가 정책별 동의와 version·비소급 경계를 명시했다.

## DEC-044
- Status: ANSWERED
- Decision: Owner·Staff는 정책 초안을 작성하고 Owner만 version을 발행·철회한다. 발행은 즉시 신규 예약에 적용하며 이전 version을 불변 보존한다. 현재 발행본 누락 시 신규 확정을 차단하고 철회는 이전 version을 자동 복구하지 않는다. 모든 lifecycle 행위를 감사한다.
- Reason: 사용자가 정책 권한·효력·철회·감사 경계를 명시했다.

## DEC-045
- Status: ANSWERED
- Decision: v1은 iCalendar 구독과 Google Calendar 양방향 동기화를 제공하지 않으며 앱이 예약·가용성의 유일한 authoritative source다.
- Reason: 사용자가 외부 캘린더 연동을 명시적 비목표로 정했다.

## DEC-046
- Status: ANSWERED
- Decision: Owner·Staff 대리 예약안은 온라인과 동일한 검증 후 15분 자원 hold와 24시간 고객 정책 동의 링크를 생성한다. 운영자는 동의를 대리할 수 없고 고객 동의 전에는 확정되지 않는다. 미동의·만료 시 hold를 해제하고 lifecycle을 감사한다.
- Reason: 사용자가 대리 예약의 입력·검증·hold·동의·감사 경계를 명시했다.

## DEC-047
- Status: ANSWERED
- Decision: 15분 hold 만료는 24시간 고객 확인 링크를 무효화하지 않는다. 이후 동의 시 최신 규칙과 자원을 재검증해 원자적으로 재확보하며, 실패하면 예약 없이 제안을 종료하고 양측에 충돌을 알린 뒤 새 구성 재제안을 요구한다.
- Reason: 사용자가 hold와 링크 만료의 독립성 및 재확보 실패 동작을 명시했다.

## DEC-048
- Status: ANSWERED
- Decision: 일반 온라인 예약 작성에는 임시 hold가 없고 최종 확인 commit에 먼저 성공한 요청만 확정한다. 운영자 대리 예약 15분 hold만 예외다.
- Reason: 사용자가 일반 예약과 대리 예약 hold 경계를 명시했다.

## DEC-049
- Status: ANSWERED
- Decision: 경쟁 commit 실패 시 고객 입력과 새 슬롯에도 호환 가능한 선택을 보존하고, 무효 선택은 제거한 뒤 최신 가용 대안을 표시한다.
- Reason: 사용자가 경쟁 충돌 복구 범위를 명시했다.

## DEC-050
- Status: ANSWERED
- Decision: 장비 고장·점검 불가는 신규 선택을 즉시 차단하고 충돌 예약을 목록화한다. 운영자는 동급 대체 또는 장비 제외안을 24시간 고객 동의 lifecycle로 처리하며 합의 실패 시 사유를 남겨 취소한다. 자동 취소·무단 교체를 금지한다.
- Reason: 사용자가 장비 장애 복구와 고객 동의 경계를 명시했다.

## DEC-051
- Status: ANSWERED
- Decision: Owner·Staff는 필수 사유와 30분 경계로 전체·공간·장비 수량 임시 차단을 관리한다. 기존 예약 충돌은 예약별 예외 유지·고객 동의 변경·운영자 취소 처리 후 확정하며 차단은 버퍼와 함께 가용성에 반영되고 lifecycle을 감사한다.
- Reason: 사용자가 임시 차단 범위·충돌·가용성·감사 규칙을 명시했다.

## DEC-052
- Status: ANSWERED
- Decision: 이메일 최초 실패 후 1·5·30분에 3회 자동 재시도하고 최종 실패를 앱 알림·실패 큐에 표시해 Owner·Staff 수동 재발송을 허용한다. 고유키·attempt로 중복을 막고 업무 상태를 롤백하지 않는다.
- Reason: 사용자가 이메일 복구·관측·멱등성 경계를 명시했다.

## DEC-053
- Status: ANSWERED
- Decision: 이메일은 제공자 교체형 adapter와 배포 환경 설정을 사용한다. 검증된 전용 하위 도메인·SPF/DKIM/DMARC·고정 From을 강제하고 문의 알림만 검증된 Reply-To를 허용하며 provider 비밀정보를 고객 화면·일반 로그에서 숨긴다.
- Reason: 사용자가 제공자 독립성과 발신·비밀정보 제약을 명시했다.

## DEC-054
- Status: ANSWERED
- Decision: v1 화면·정책·이메일은 한국어만 제공하고 WCAG 2.2 AA를 기준으로 키보드·포커스·스크린리더·오류 연결·대비·동작 감소·200% 확대·모바일 reflow를 지원한다.
- Reason: 사용자가 언어와 접근성 acceptance 범위를 명시했다.

## DEC-055
- Status: ANSWERED
- Decision: 예약 변경안·문의 작성 내용을 예약·고객 세션에 묶인 서버 암호화 latest-version draft로 2시간 보관하고 같은 예약 재인증 후만 복구한다. 인증 비밀은 제외하고 복구 후 성공 mutation·명시 폐기·만료 시 삭제한다.
- Reason: 사용자가 draft 범위·저장·접근·삭제 lifecycle을 명시했다.

## DEC-056
- Status: ANSWERED
- Decision: 장비 부족 시 같은 시간 최대 수량, 동급 호환 대체 장비, 원래 수량 가능 최신 시간을 순서대로 제시하고 선택 후 전체 규칙·가격을 재계산하며 commit 시 원자적으로 재검증한다.
- Reason: 사용자가 장비 부족 대안 종류·순서·재검증 범위를 명시했다.

## DEC-057
- Status: ANSWERED
- Decision: delivery 수신 주소·개인화 데이터는 예약 종료·취소 후 1년에 익명화하고 비식별 event·attempt 기록은 3년 후 삭제한다. legal hold는 모두 보류하며 provider payload·token은 장기 보관하지 않는다.
- Reason: 사용자가 delivery 개인정보와 비식별 기록의 차등 retention을 명시했다.

## DEC-058
- Status: ANSWERED
- Decision: append-only 운영·보안·개인정보 접근 감사는 사건 후 5년 보관하고 고객 식별 필드는 예약 기준 1년에 비식별화한다. 행위·역할·시각·대상 비식별 ID는 유지하며 legal hold는 비식별화·삭제를 보류한다.
- Reason: 사용자가 감사 데이터 retention과 식별정보 수명주기를 명시했다.

## DEC-059
- Status: ANSWERED
- Decision: 인증 고객 삭제 요청은 미래·진행 예약이면 완료·취소까지 보류하고 종료·취소 예약이면 30일 내 고객·delivery 식별 필드를 익명화한다. legal hold는 보류하며 비식별 기록을 유지하고 lifecycle을 감사한다.
- Reason: 사용자가 요청 인증·처리 기한·예외·보존 경계를 명시했다.

## DEC-060
- Status: ANSWERED
- Decision: v1은 Asia/Seoul 단일 스튜디오 지점이며 모든 공간·장비·영업시간·요금·정책·운영자가 그 지점에 속한다. 다지점과 지점 간 장비 이동은 비목표다.
- Reason: 사용자가 v1 지점·tenant 경계를 명시했다.

## DEC-061
- Status: ANSWERED
- Decision: v1은 예약당 하나의 날짜·시간·공간만 허용하고 반복·여러 날짜 일괄 예약을 제공하지 않는다. 날짜별 예약은 독립 lifecycle·가격 snapshot·관리 링크를 가진다.
- Reason: 사용자가 단일 occurrence 예약 경계를 명시했다.

## DEC-062
- Status: ANSWERED
- Decision: 운영자 취소는 필수 사유와 대체 변경안 고객 동의를 먼저 시도하고 합의 실패·운영 불가 시 예약 취소와 자원 해제를 원자적으로 수행한다. v1은 결제·환불·금전 보상·크레딧을 처리하지 않는다.
- Reason: 사용자가 운영자 취소의 대체 우선·비금전 복구 경계를 명시했다.

## DEC-063
- Status: ANSWERED
- Decision: v1은 보증금·배상금 transaction 없이 Owner·Staff가 예약 연결 파손·분실 사건과 append-only 이력을 기록하고 고객에게 알린다. 고객 공유 필드와 운영자 전용 내부 메모를 분리한다.
- Reason: 사용자가 사건 기록 범위와 비금전·권한 경계를 명시했다.

## DEC-064
- Status: ANSWERED
- Decision: 촬영 시작 30분 후 Owner·Staff가 사유로 수동 노쇼 처리하며 자동 전환은 없다. 지각·노쇼는 종료·버퍼 점유를 바꾸지 않고 비금전 상태·메모·이메일·감사를 기록하며 오처리는 사유로 되돌린다.
- Reason: 사용자가 노쇼·지각 경계와 정정 절차를 명시했다.

## DEC-065
- Status: ANSWERED
- Decision: 결제 transaction·결제사·결제수단은 v1 명시적 비목표이며 앱은 KRW 가격 구성과 불변 가격 snapshot만 표시·보존한다.
- Reason: 사용자가 결제 범위를 최종 명시했다.

## DEC-066
- Status: ANSWERED
- Decision: 환불 transaction은 v1 명시적 비목표이며 취소·변경·운영자 조치는 금전 transaction 없이 상태·자원·알림·감사만 처리한다.
- Reason: 사용자가 환불 범위를 최종 명시했다.

## DEC-067
- Status: ANSWERED
- Decision: 할인 코드·패키지·회원 요금은 v1 명시적 비목표이며 모든 snapshot은 현재 유효한 공간·장비 정가 규칙으로 계산한다.
- Reason: 사용자가 할인 범위를 최종 명시했다.

