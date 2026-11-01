# U2-8 전달된 사용자 의도 — 설계와 결과 (2026-11-01)

상태: 사용자 결정(2026-11-01) "강하게 가자. 그래야 넘겨짚기가 없어진다". 구현 완료.

## 1. 문제 (마찰 9)
다른 세션이나 사람이 "사용자가 이렇게 말했다"고 전해 준 의도에 근거 종류가 없어 `USER_CONFIRMED_INTENT`로 적고 locator에 "전달받음"이라고 써 왔다. 기록상 직접 들은 것과 구분되지 않고, 전달 과정의 요약·해석이 그대로 material 결정이 될 수 있다.

## 2. 고려한 안
| 안 | 내용 | 문제 |
|---|---|---|
| 약한 안 | 새 종류를 두되 닫기 허용 | 기록만 달라지고 넘겨짚기는 그대로 |
| 중간안 | 닫되 Manifest에 "전달 근거로 닫힌 결정 N건" 표시 | 표시만으로는 못 막음("ㄱㄱ" 승인 흐름에서 직접 확인과 같아짐), 요약/원문 경계가 흐림 |
| **강한 안(채택)** | 전달 근거로는 material 질문을 못 닫음. 예외: 사용자 **원문 그대로**(요약 아님)이고 전달자가 적혀 있으면 직접 확인과 같음 | 부모→자식 세션 지시 흐름에서 질문마다 사용자 답이 필요. 원문 전달 예외로 대부분 흡수 |

## 3. 구현 (0.2.0 안, enum 확장)
- 근거 종류 `RELAYED_USER_INTENT`(INTENT·PREFERENCE). `confidence`가 그 뜻을 나른다: `DIRECT` = 사용자 원문 그대로(닫을 수 있음), 그 밖(`INFERRED`·`CORROBORATED`) = 전달자의 말(닫을 수 없음, 후보 전용 근거처럼 취급).
- 못 하는 것(요약일 때): EVIDENCE_RESOLVABLE로 질문 닫기, AUTHORITATIVE·OUT_OF_SCOPE 표면 근거, 모순의 선택 권위, Grill 축의 근거. 그리고 **사용자 결정(USER_DECISION·USER_ACCEPTED_RECOMMENDATION)이 요약 전달 근거만 인용하면 오류 `relayed_intent_cannot_close`** — 사용자 원문 근거(직접 또는 원문 전달)가 하나라도 있어야 한다.
- A/B 1차(8회, [결과](../evals/joeflow-u2-8-relayed-intent-ab/README.md)) 뒤 추가: 전달 근거(원문·요약 모두)를 인용한 질문을 **담당자 기본값으로 닫을 수 없다**(`relayed_intent_needs_user`, AUTHORING 결정은 예외). B·요약 실행 2/2가 질문을 비물질로 낮춰 AGENT 기본값으로 닫았기 때문이다.
- `new_records.py relayed --relayer WHO --quote "..."` / `--summary "..."`가 두 형식을 만든다(locator `relayed by WHO, said WHEN`).
- 고정 모듈 `state_validation_v2.py`와 스키마 `state-v0.2.0.schema.json`(source_kind enum)·해시 갱신. `grill_v2.py`의 표는 같은 규칙을 거울처럼 따른다. 기존 기록은 영향 없음(새 종류를 쓰기 전까지).
- 한계: "원문 그대로"는 작성자의 선언이다(검증기가 원문 여부를 알 수는 없다). 규칙의 값은 요약을 원문으로 적는 거짓을 **의식적인 행위**로 만드는 데 있다.

## 4. 측정 (오목 rev 41)
- `USER_CONFIRMED_INTENT` 근거 27건 중 전달 근거는 1건(EVD-002, 부모 세션 작업 지시, 원문 인용 없음). 현재 사용자 결정 51건 중 7건이 EVD-002를 인용하지만 EVD-002만 인용하는 결정은 0건 → 강한 규칙을 처음부터 적용했어도 오목에서 막혔을 결정은 없고, EVD-002는 요약형 `RELAYED_USER_INTENT`로 적혔을 것이다.
- 시험 `tests/test_relayed_intent_v020.py`: 요약 전달만 인용한 사용자 결정 → 오류, 원문 전달 → 통과, 직접 근거가 함께 있으면 통과, 요약 전달은 모순 선택 권위 불가, 도우미 두 형식.
