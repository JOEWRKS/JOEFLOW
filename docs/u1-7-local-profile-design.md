# U1-7 설계: 계정 없는 앱의 UX 축 상속 (초안, 2026-10-31)

상태: 2026-10-31 사용자 승인, 구현 완료. 구현하며 범위가 줄었다: `state_validation*.py`는 지표를 `authority_binding_v2`에서 받으므로 고치지 않았고, downstream_v2 seeds·reentry는 COVERED 칸만 읽어 생략된 N/A 칸의 영향이 없으므로 펼친 보기(`expand_inherited_ux`)는 만들지 않았다. 고정 blob은 `authority_binding_v2.py` 하나만 바뀌었다.

## 1. 문제

로컬·무계정 앱도 화면마다 계정·권한·세션 UX 칸을 모두 채워야 한다(F7). 오목 rev 36 기준 UX 칸 142개 중 61개가 N/A이고, 그중 15개는 "계정·권한이 없다"류를 칸마다 반복한다.

| 축 | 종류 | 오목 N/A 칸 |
|---|---|---|
| `permission`, `session_expiration` | 동작 | 5 + 5 |
| `permission_denied`, `unauthenticated`, `expired` | 상태 | 2 + 2 + 1 |

이 사실은 이미 한 곳에 근거와 함께 기록되어 있다. `surface_manifest.grill_profile`의 `AUTH`·`PERMISSION` 칸이 `N/A`이고 `basis_refs`·`rationale`을 가진다. 그 결정이 화면 칸으로 내려가지 않을 뿐이다.

## 2. 제안: 프로필 N/A 상속

새 사용자 선언 필드는 만들지 않는다. 이미 승인 대상인 grill_profile을 근거로 쓴다.

| 프로필 칸 | 상속되는 UX 축 |
|---|---|
| `AUTH` = N/A | 상태 `unauthenticated`·`expired`, 동작 `session_expiration` |
| `PERMISSION` = N/A | 상태 `permission_denied`, 동작 `permission` |

규칙:
1. 해당 프로필 칸이 근거가 검증된 `N/A`일 때만, 상속 축의 UX 칸을 **생략할 수 있다**. 생략된 칸은 "프로필에서 상속된 N/A"로 본다.
2. 칸을 그대로 적어도 된다. 적힌 칸은 지금과 똑같이 검증한다(기존 state 전부 그대로 유효).
3. 프로필 칸이 `ACTIVE`·`OPEN`이거나 근거가 깨지면 상속이 없다. 생략된 칸은 지금처럼 누락 오류다.
4. 나머지 축(`notification`, `undo`, `back` 등)은 상속하지 않는다. 그 축의 N/A는 화면마다 사정이 달라 칸별 근거가 맞다.

## 3. 바뀌는 것

| 대상 | 변경 | 비고 |
|---|---|---|
| `scripts/authority_binding_v2.py` (고정) | `_ux_binding_analysis`의 축 집합 비교를 "필수 축 = 전체 − 상속 가능 축"으로 | 고정 blob 갱신 필요 |
| `scripts/state_validation.py`·`state_validation_v2.py` | 누락 칸 지표가 상속 축을 세지 않게 | v2는 고정 blob |
| 새 `references/ux-profile-inheritance-v1.json` | 위 대응표 | 바인딩 계약 JSON은 **바꾸지 않음** |
| 새 `expand_inherited_ux(state)` | 생략 칸을 펼친 전체 축 보기를 만듦 | downstream_v2 seeds·reentry, 기획서 점검이 이 보기를 받음 |
| `tests/test_downstream_v2_frozen_boundaries.py` | 고정 blob 해시 갱신 | 사용자 승인 사항 |
| SKILL·workflow | 무계정 앱은 상속 축을 생략해도 된다는 한 줄 | |

바꾸지 않는 것:
- `ux-coverage-binding-v1.json`: 승인 기록의 `closure_contract.ux_binding_contract`가 이 파일의 digest를 담는다. 바꾸면 기존 승인이 모두 낡은 것이 된다.
- state 스키마 0.2.0: 칸 생략은 이미 스키마상 허용된다(`states`는 additionalProperties 객체). 버전을 올리지 않는다.
- 고정 downstream(v1) 트리, semantic-review 0.4.3, downstream 2.1 계약.

## 4. 위험과 확인

| 위험 | 확인 방법 |
|---|---|
| 기존 결과가 바뀜 | 모든 기존 fixture·오목 rev 36 원본의 검증 결과·approval digest·discovery digest가 바이트 단위로 같음 |
| 상속이 근거 없이 일어남 | AUTH가 ACTIVE·OPEN이거나 basis가 깨진 사본에서 생략 칸이 누락 오류로 나옴 |
| downstream이 빠진 칸을 오해 | 펼친 보기와 원래 칸 보기로 seeds·reentry 결과가 같음 |
| Manifest digest가 의도치 않게 바뀜 | 생략 전후 사본 각각에서 Manifest를 만들어 차이가 칸 데이터뿐인지 확인 |

측정: 오목 rev 36 사본에서 상속 축 15칸을 지우고 검증 통과, N/A 칸 61 → 46, 반복 근거 문장 수 감소를 기록.

## 5. 범위 밖 (이번에 하지 않음)

- **ASYNC 경량 축:** 오목은 Worker 계산 때문에 ASYNC가 ACTIVE이고, 10축 중 4축(polling·idempotency·duplicate_execution·reconciliation)이 N/A다. 줄이려면 표면에 "로컬 실행" 같은 새 속성이 필요해 스키마가 바뀐다. 효과(4칸, 한 표면)에 비해 비용이 커서 따로 판단한다.
- `notification` 등 다른 축의 일괄 N/A.

## 6. 순서

1. 이 설계 승인
2. 대응표·펼친 보기·검증 변경 구현, 고정 blob 해시 갱신
3. 기존 결과 불변 시험 → 오목 사본 측정 → 전체 회귀
4. 커밋 → ROADMAP·CHANGELOG 기록 (버전·게시·설치는 각각 따로 승인)
