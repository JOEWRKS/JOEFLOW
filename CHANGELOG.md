# JOEFLOW 변경 기록

프로그램 릴리스 기록입니다. State, schema, action contract, semantic-review 같은 런타임 identity는 프로그램 버전과 별도로 호환성을 관리합니다.

## 1.1.0 — 2026-10-13

- 처음 사용하는 사람이 바로 설치하고 요청할 수 있도록 README를 여섯 개 핵심 절로 정리했습니다.
- JOENESS·JOEFLOW·JOEDESIGN의 역할과 실제 인계 순서를 같은 표현으로 연결했습니다.
- Product Definition 후보 사전검사와 사람이 읽는 planning projection 검사를 추가했습니다.
- 공통 구현 인계와 선택적 Figma 안내를 분리하고, 조건부 성공·실패·복구 의미 보존을 강화했습니다.
- Approval Manifest와 관련 CLI의 UTF-8 출력 경계를 보강했습니다.
- Windows checkout의 raw-byte 검사와 M6 역사적 replay를 재현하는 회귀 환경을 문서화했습니다.

검증 범위와 남은 경계는 [v1.1.0 검증 기록](evals/joeflow-v1.1.0/VERIFICATION.md)에 정리했습니다. 이후 승인된 개인 설치 결과는 [개인 설치 검증 기록](evals/joeflow-v1.1.0/PERSONAL_INSTALL_VERIFICATION.md)과 [전체 manifest receipt](evals/joeflow-v1.1.0/personal-install-receipt.json)에서 확인할 수 있습니다.

유지되는 경계:

- Runtime skill/package ID: `joewrks-product-definition`
- Native state contract: `0.2.0`
- Current downstream contract: `joewrks.action-conformance/2.1`
- Semantic review reliability: `NOT_MEASURED`
- Historical frozen contracts and evidence are unchanged.

## 1.0.0 — 2026-09-27

- `JOEFLOW` 프로그램 이름과 `joewrks-product-definition` runtime skill ID를 분리했습니다.
- Native State 0.2.0 lifecycle과 downstream 2.1 handoff를 기본 설치 경로로 연결했습니다.
- `MASTER_PLANNING_SPEC.md`와 `planning-review-core.html`을 기본 사람용 전달 산출물로 추가했습니다.
- Legacy 0.1.2.1과 historical 1.0/2.0 contract compatibility를 보존했습니다.
