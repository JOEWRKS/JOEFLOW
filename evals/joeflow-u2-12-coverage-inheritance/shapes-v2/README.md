# 모양 표 v2 (2026-10-31)

A/B 1차([agent-ab](../agent-ab/README.md))에서 손으로 쓴 N/A가 실행마다 달랐고 v1 `navigate`가 두 축만 담아 선언의 효과가 6/113칸이었다. v2는 실측으로 정했다.

## 방법
- `axis_freq.py`: 메커니즘으로 모양이 분명한 행동(오목 rev 39의 5개 + A/B 12회의 SCR-003 행동 48개, 상속 칸을 펼친 뒤)에서 축마다 N/A 비율을 센다(`axis-freq-result.txt`). **모든 행동이 N/A로 답한 축만** 모양에 넣고, 메커니즘으로 설명되는지 확인했다. 갈린 축(navigate의 undo 6/12, browse의 undo 14/24, discard의 input 10/13)은 뺐다 — v1은 undo를 navigate에 넣었는데 작성자 절반이 undo를 "되돌아가기"로 읽어 COVERED로 썼다.
- `fit.py`: 97개 행동(오목 5, WebAppDev 44, A/B 48)마다 손글 N/A의 부분집합인 가장 큰 모양을 고르고 설명된 N/A 칸을 센다(`fit-result.txt`).

## 표
| 모양 | 뜻 | N/A 축 |
|---|---|---|
| `navigate` | 다른 화면·영역으로 바로 떠남 | cancel, destructive_confirmation, failure, notification, retry, timeout, validation |
| `browse` (신설) | 현재 화면이 보이는 것을 바꿈(단계·쪽·필터·위치), 계산·로드 가능, 바뀌는 것 없음 | destructive_confirmation, notification |
| `local_choice` | 화면 안에서 값 고르기 | v1과 같음(11축) |
| `discard` (신설) | 확인 뒤 로컬 상태를 버리고 떠남(새 게임·지우기·로그아웃) | failure, notification, retry, timeout, undo, validation |
| `toggle` | 되돌릴 수 있는 플래그 하나 | destructive_confirmation, undo (v1과 같음) |
| `submit` / `destructive` | 모든 축 적용 | — |

설명된 실측 N/A: v1 104/387 → v2 293/387. 맞는 모양이 없는 행동 54 → 13.

## 검증 실행 (B″, `../agent-ab/measure-result.json` t13~t16)
v2 + `draft_freeze.py --shape KEY=SHAPE`로 같은 과제 4회. **4/4가 같은 네 모양**(browse·browse·navigate·discard)을 골랐고 손으로 쓴 칸은 **113 → 96(−15%)**, 손글 N/A는 27 → 8. 검증 통과 4/4, 바인딩 집중도·인용 레코드 수는 이전 팔과 같음(도장 찍기 없음). 1/4(t16)는 TASK-004를 rev 42로 더했고 1/4(t13)는 rev 41 패치에 넣었다(과제 규칙 밖이지만 Manifest를 만들려면 필요한 전달 레코드).

B′ 실행(t9~t12)의 state는 v1 `navigate`가 암시한 undo·destructive_confirmation을 생략했으므로 v2 검증에서는 칸 누락이 된다(게시되지 않은 실험 데이터라 그대로 둠). 게시된 기록에는 모양 선언이 없다.
