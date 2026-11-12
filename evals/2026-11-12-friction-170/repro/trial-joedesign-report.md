- 작업: 요청 내용 칸 아래 오른쪽에 글자 수 '현재 / 200' 표시(JOEFLOW rev 2 DEC-002·RULE-002, TASK-002)
- 업데이트 파일: 요청 화면(src/index.html), 화면 스타일(src/style.css), 측정 스크립트(work/measure-counter.js), 디자인 규칙(DESIGN.md)
- 이슈: C1 간격 4px이 상자 기준 측정값이고, 캡처에서 보이는 글자 윗선까지는 약 9px
- 해결: 없음
- 남은 문제: C1 규칙 문장이 상자 간격인지 보이는 간격인지 정하기(검사와 관찰이 다름), C2 대조 안 함, 다크 모드·확대 200% 미측정, 사용자 화면 확인
- 다음 작업: C1 규칙 정의 결정 뒤 재측정, R1-2 완료 판정

design check results:
- C1 gap | 8/8 at 4px | 4 sizes x 2 states, light | rendered | 320x700 200자: check 4 / observed 9 (글자 윗선, 캡처)
- C1 right edge | 8/8 at 0 | 4 sizes x 2 states, light | rendered | not spot-checked
- C2 overflow | 0/8 overflow | 4 sizes x 2 states, light | rendered | not spot-checked
- AC-002 count text | 0 / 200, 200 / 200, 199 / 200 | 1 size x 3 states, light | rendered | not spot-checked

C1 간격은 상자 기준 8/8(4 sizes x 2 states, rendered; spot check differs: check 4 / observed 9)이라 R1-2는 verification pending으로 둔다. 측정은 미리보기 창이 연결 CSS를 읽지 못해 같은 파일 내용을 주입해 잰 값이다.
report-check: ok 972 chars 685aaf68
