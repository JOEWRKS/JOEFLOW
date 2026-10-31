# U2-10 기능 추가 모드 · U2-11 ASYNC 로컬 실행 프로필 — 설계와 결과 (2026-10-31)

상태: 사용자 지시(2026-10-31 "U2-10 기능 추가 모드, U2-11 ASYNC 프로필")로 설계·구현. 측정은 `evals/joeflow-u2-10-feature-extension/`, `evals/joeflow-u2-11-async-profile/`.

## 1. 공통 제약

`definition_digest`가 `schema_version`을 포함하므로 State 0.3.0은 모든 승인을 낡게 만든다(U2-12 결정과 같음). 고정 스키마 파일의 enum(`bootstrap_mode`, `intent_classification`)도 바꾸지 않는다. 그래서 두 항목 모두 **0.2.0 안의 작성 형식과 관례**로 푼다. 고정 모듈 `authority_binding_v2.py`·`approval_v2.py`는 고쳤고 해시를 갱신했다(사용자 승인 범위: "U2-10·U2-11 진행").

## 2. U2-10 기능 추가 모드

### 문제 (마찰 5)
`EXISTING_PRODUCT_RECONCILIATION`은 이전(migration)된 레거시 정의용이라 모든 표면에 `intent_classification`을 요구하고, `NEW_PRODUCT`는 그것을 금지한다. 이미 돌아가는 제품에 기능을 더할 때 맞는 모드가 없어 오목은 NEW_PRODUCT로 범위를 새 기능에 한정하고 기존 앱은 근거로만 썼다(우회 비용은 기록 1건).

### 원안과 바꾼 이유
원안(U2-9 설계 C): 표면마다 `change_kind`(NEW·CHANGED·BASELINE), BASELINE은 관찰 근거만 두고 coverage 없음. 스키마 버전·이전·downstream 계약까지 바뀐다. 기능 추가 모드가 꼭 해야 할 일은 둘뿐이다 — (1) 바꾸면 안 되는 기존 동작을 근거와 함께 선언해 인계·재진입이 쓰게 하고, (2) 새로 만들거나 바꾸는 표면에만 coverage를 요구한다. (2)는 NEW_PRODUCT 범위 한정으로 이미 된다. (1)은 0.2.0의 보통 권위로 쓸 수 있다.

### 구현
- `references/feature-extension.md`: 기존 제품에 기능을 더하는 절차. NEW_PRODUCT를 변경 범위로 한정, 기존 동작은 관찰 근거(`OBSERVED_IMPLEMENTATION`·`OBSERVED_RUNTIME`·`TEST_ASSERTION`), 유지할 동작은 **기준선(baseline)** 요구사항 하나로.
- `new_records.py baseline`: 한 번에 REQ("기존 동작 유지"), RULE(동작 목록), AC(기존 검사 통과), 그것을 소유하는 SURF(FEATURE_AREA, IN_SCOPE), Core 행(`default_authority` = RULE, 손으로 쓰는 칸은 goal·happy_path·acceptance 3개), 선택적으로 TASK(Manifest의 전달 매핑)를 패치에 쓴다. U2-12 상속이 없었다면 20칸을 손으로 써야 했을 것이다.
- workflow·first-plan-guide·SKILL.md 연결.

### 측정 (오목 rev 39 사본)
근거 1건 + `baseline` 1회 → rev 41 READY_FOR_REVIEW, 검증 오류 0, Manifest 생성, 승인(사본) 뒤 closure `closed: true`, 손으로 쓴 칸 3/20. 시험 `tests/test_feature_extension_v020.py`(승인본 픽스처에 적용 → 유효, 상속 17칸, TASK 매핑).

### 하지 않은 것
새 bootstrap 모드와 표면 필드(`change_kind`). 2.1 계약의 `scope_commitments`는 REQ·SCR·SURF만 담으므로 RULE 자체는 거기 들어가지 않는다 — 기준선 규칙의 변경은 승인 digest(새 revision 필요)로 잡히고, 인계 정의가 REQ를 `authority_scope_refs`에 적으면 그 REQ 해시가 계약에 고정된다. 구현이 실제로 동작을 지켰는지는 AC(기존 검사)가 증명한다.

## 3. U2-11 ASYNC 로컬 실행 프로필

### 문제 (마찰 6)
오목의 ASYNC 표면(브라우저 Worker 계산)은 ASYNC 팩 10축 중 4축(polling·reconciliation: 외부 시스템 없음, idempotency·duplicate_execution: 표시 전용 순수 계산)이 N/A였고, 각각 근거·사유를 적어야 했다.

### 구현 (U1-7·U2-12와 같은 상속 규칙)
- `references/grill-profile-inheritance-v1.json`: `ASYNC.execution` = `LOCAL`(polling·reconciliation N/A) 또는 `LOCAL_PURE`(+ idempotency·duplicate_execution).
- `grill_profile.ASYNC`가 ACTIVE일 때만 `execution`을 선언할 수 있고(`invalid_grill_profile_declaration`), ASYNC 행은 그 축을 생략할 수 있다. 적은 칸이 이긴다. `expand_coverage`가 `inherited_from: "profile:ASYNC.LOCAL_PURE"`로 펼치고, digest 투영은 선언과 꼬리표를 벗긴다. `draft_freeze.py`는 그 축을 초안에서 뺀다.
- 고정 모듈: `authority_binding_v2.py`(상속 N/A 칸은 근거·사유 검사 생략), `approval_v2.py`(digest가 프로필 선언을 벗김).

### 측정 (오목 rev 39)
LOCAL_PURE가 암시하는 4축 = 오목이 손으로 N/A로 둔 4축(정확히 일치). 승인본에 선언만 더하면 definition·Manifest digest가 그대로다(승인 유효). 4칸을 빼면 검증 통과(펼친 보기에 꼬리표 4개). 효과는 ASYNC 표면당 4칸으로 작다(계획대로).

## 4. 남은 것
- U2-8의 전달된 사용자 의도 근거 종류(사용자 결정 대기).
- 기능 추가 모드의 실제 사용 측정은 다음 오목 기능 추가 때 `feature-extension.md` 절차로 한다.
