# JOEFLOW 1.7.0 후보 — 오목 마찰 4건과 세 도구 통합 점검 (2026-11-12)

결론: 마찰 A·B·D는 도구에서 해결, C는 절차·기록 자리·검사 전용 명령으로 해결했으나 자동 권한 분류기 쪽 동작은 재현·확인하지 못했다. 세 도구를 한 바퀴 돌린 통합 시험에서 JOEFLOW 결함 3건을 더 찾아 고쳤고, JOENESS·JOEDESIGN 쪽 사항은 고치지 않고 아래 목록으로 남긴다. 유료 모델 실행 0회.

- 기준: JOEFLOW v1.6.0(`43fb1fe`), JOENESS `7daed3c`(1.4.0 + 문서 1커밋), JOEDESIGN `3a19237`(1.3.0 + 문서 1커밋). 시험 폴더 `D:\JOEWRKS\.local\joeflow-170-trial-20261112`(저장소 밖, 정션 없음).
- 오목 원문은 `AI-Gomoku/TASK.md#tool-friction`(2026-11-11 항목)·`#rev43-approval`·`#rev43-open`·`#two-deploy`. 오목 폴더는 읽기만 했다.

## 마찰별 재현 → 수정 → 확인

### A. 선택지 ID `NONE` 거절, 오류가 ID를 말하지 않음 — 해결

- 원인: `grill_v2.py`의 `MEANINGLESS`(`none, false, n/a, na, later, tbd`, 대소문자 무시)에 걸려 선택지가 "의미 없는 글자"로 처리된다. 1.6.0 메시지는 고정 문장 하나뿐이다.
- 재현(오목 rev 43 사본 + 질문 하나): [a-out-160](repro/a-out-160.json) "options must match response_mode (each option needs id, …)".
- 수정: `grill_v2.options_problems`·`recommendation_problems`가 거절 이유를 칸·값으로 말한다(판정 함수는 그대로라 유효/무효 결과는 같다). `new_records.py`가 선택지 ID·문장·결과와 `--tradeoff`의 예약어를 만들 때 거절한다. 예약어 목록은 `new_records.py --help`와 `workflow-v0.2.0.md`에 적었다.
- 확인: [a-out-170](repro/a-out-170.json) "…: options[1].id 'NONE' is a reserved non-answer word (false, later, n/a, na, none, tbd); rename it". 생성 단계는 `argument --option: option ID 'NONE' is a reserved non-answer word …`로 종료 2, 패치 파일을 만들지 않는다. 테스트 `OptionDiagnosticsTest`·`NewRecordsGuardsTest`.

### B. `user-decision --accepted`가 `--reason`·`--tradeoff` 없이 패치를 만듦 — 해결

- 재현: [b-out-160](repro/b-out-160.json) 생성은 종료 0, 적용 때 "recommendation must match the canonical M3 structure".
- 수정: `--recommend`는 `--reason`·`--tradeoff`를 하나 이상 요구하고 선택지 ID 중 하나여야 하며, `--accepted`는 `--recommend`를 요구한다. 어기면 패치를 쓰지 않고 이유를 말한다. 도움말에 "required (at least one) with --recommend"를 적었다. 적용 단계 메시지도 [b-out-170](repro/b-out-170.json)처럼 빠진 칸과 넣을 인자를 말한다.
- 확인: 테스트 4건(`test_recommend_without_reason_or_tradeoff_is_refused` 등).

### C. 전달된 승인 기록 — 절차·기록 자리 해결, 분류기 동작은 확인 못 함

- 정한 절차(SKILL.md 4단계·Quick reference, `workflow-v0.2.0.md` APPROVE): 승인은 사용자 원문을 직접 받은 세션이 `record_approval.py … --quote "원문" --write`로 기록한다. 전달만 받은 세션은 기록하지 않고 원문·전달 세션 ID·revision·digest·시각을 프로젝트 기록(TASK)에 남기고, `check_approval.py`로 검사한 뒤 원문 세션에 기록을 요청한다.
- 기록 자리: state 0.2.0 스키마는 닫혀 있고 고정 모듈이라(바꾸면 기존 승인이 모두 낡음) state 밖 `joeflow-project.json`(state.json 옆)을 두었다. `record_approval.py --quote`·`--relayed-from`이 `--write` 때 `approvals`에 revision·두 digest·시각·시각 출처·원문·전달 경로·기록한 판을 붙인다. `--relayed-from`은 `--quote` 없이 거절(`relayed_approval_needs_quote`, 요약은 질문을 닫을 수 없다는 1.6.0 규칙과 같은 원칙). `--quote` 없이 기록하면 이 파일을 만들지 않는다(기존 동작과 같음). `approval_status.py`가 승인된 revision의 기록을 `approval_provenance`로 보인다.
- `relayed --quote`의 질문 원문: `--asked "보인 질문 원문"` 또는 원문이 없을 때 `--asked-summary "전달자 설명"`. 근거 claim에 `— 답한 질문 원문: "…"` / `— 답한 질문(전달자 요약, 원문 없음): …`로 붙는다. 질문을 닫을 수 있는 것은 여전히 답의 원문뿐이다.
- 승인 전 검사: 쓰기 옵션이 아예 없는 `check_approval.py`(같은 검사 함수 `prepare_approval` 공유). 결론: 분류기가 무엇을 보고 막았는지 도구에서 알 수 없으므로 "이름과 인자에 기록·쓰기가 없는 읽기 전용 명령"이 할 수 있는 최선이다. 이 세션에서는 `check_approval.py`와 `record_approval.py --write`가 둘 다 막히지 않았다(전달 승인 상황이 아님). 오목에서 막힌 상황의 재현은 하지 않았다.
- 확인: `ApprovalProvenanceTest` 4건, 통합 시험의 모의 승인 기록(아래).

### D. 설치 판 혼동 — 해결

- 기록 자리: `joeflow-project.json`의 `joeflow_version`. `joeflow_version.py STATE_JSON`이 실행 중인 판·고정한 판·state 스키마를 보이고 `--pin [X.Y.Z]`로 기록한다. 실행 판은 새 파일 `skills/joewrks-product-definition/VERSION`에서 읽는다(설치본에는 저장소 루트 VERSION이 없으므로). 테스트가 루트 VERSION과 같은지 확인한다 — 버전을 올릴 때 둘을 함께 올려야 한다.
- 알림: `approval_status.py`(`joeflow_version` 블록), `open_revision.py`·`record_approval.py`·`check_approval.py`(`version_notice`)가 고정이 없거나 판이 다를 때 한 문장으로 알린다(막지 않음). 스키마가 다르면 찾은 `schema_version`과 할 일(0.1.2.1은 legacy, migrate는 사용자 요청 때만)을 말한다.
- 판 차이의 뜻: 1.x는 모두 state 0.2.0을 읽는다. 새 판은 옛 판이 거절하는 레코드를 받거나 만들 수 있다. 오목 메모리가 가리킨 JOEFLOW-ux 1.2.0과 설치본 1.6.0의 차이는 이 문장 이상으로 분석하지 않았다.
- 확인: `VersionPinTest` 3건, 샘플 프로젝트 고정(`1.6.0`) 뒤 알림 없음.

## 통합 점검 (JOENESS 1.4.0 → JOEFLOW → JOEDESIGN 1.3.0 → JOENESS stamp)

샘플: 새 git 저장소 `sample/`(요청 폼, 실제 프로젝트 복사 아님). JOEFLOW는 `templates/examples/closed-minimal.state.json`(rev 1 승인)에서 시작해 기능 하나(요청 내용 글자 수 표시)를 rev 2로 정의했다. 사용자 승인은 모의(`--quote "(모의 시험, 실제 사용자 아님) 이대로 승인"`)다.

| 단계 | 한 일 | 결과 |
|---|---|---|
| JOEFLOW 판 | `joeflow_version.py --pin` | 1.6.0 고정, 이후 알림 없음 |
| 근거·결정 | `new_records.py relayed --asked`, `evidence`, `user-decision --accepted --recommend --reason --tradeoff` | 한 번에 통과 |
| rev 2 열기 | RULE-002·AC-002·TASK-002 + acceptance 칸 | **결함 F1**: 1.6.0 `open_revision.py`가 READY_FOR_REVIEW로 썼으나 `build_approval_manifest.py`가 `orphan_material_authority: 1`(레코드 이름 없음, **F2**)로 거절. RULE-002를 `boundary` 칸에 묶고 다시 열어 통과 |
| Manifest·승인 | `check_approval.py` → `record_approval.py --quote --relayed-from --write` | digest `6b50eb33…`, `joeflow-project.json`에 기록, `next`가 투영 갱신을 안내 |
| 투영 | `update_projection.py --write`, `projection_check.py` | **결함 F3**: 빈 식별 블록(BEGIN 바로 다음 END)을 못 알아봄. 고친 뒤 ok true |
| JOENESS 연결 | `project-setup.ps1 -Check` → `-Apply` | `current`, ROADMAP·TASK·ISSUES 작성 |
| JOEDESIGN | 구현, DESIGN.md Rule Coverage C1·C2, 4 sizes × 2 states 측정, 보고서 | 도장 `report-check: ok 972 chars 685aaf68`, `--verify` 종료 0(CRLF 사본도 일치) |
| JOENESS 소비 | TASK `Report stamp:`, ROADMAP R1-1 complete, R1-2 verification pending | C1 spot check가 어긋나(check 4 / observed 9) 완료로 넘기지 않음 — 의도대로 막힘 |

인계: JOEFLOW ID(rev 2, TASK-002, AC-002, RULE-002)는 ROADMAP Check·DESIGN Product Authority·JOEDESIGN 보고·TASK에 이어졌다. 다만 이어 붙인 것은 시험자이고, 세 도구 어느 문서도 "ROADMAP Check에 JOEFLOW AC/TASK ID를 적는다"를 말하지 않았다 → JOEFLOW 쪽 문장을 더했다(SKILL.md Quick reference, workflow HANDOFF).

### JOEFLOW에서 고친 것 (이번 후보에 포함)

- F1 `open_revision.py`: `--status READY_FOR_REVIEW`(기본값)에서 semantic readiness가 실패하면 쓰지 않고 `readiness_findings`(코드·레코드·원인·다음 행동)와 `--status OPEN` 안내를 낸다. 1.6.0은 써 놓고 Manifest 단계에서야 실패했다([r2-block](repro/r2-block.json)).
- F2 `build_approval_manifest.py`: readiness 실패 출력에 `findings`(레코드 이름)를 더했다. 기존 키는 그대로.
- F3 `update_projection.py`: 빈 블록과 CRLF 줄끝 블록을 알아본다.
- 테스트 `IntegrationTrialFixesTest` 2건.

### JOEFLOW에서 고치지 않은 것

- `projection_check.py`는 손으로 만든 검토 화면 제목의 낡은 "revision 0"을 잡지 못한다(`REVIEW VIEW … revision N` 형식만 갱신·대조). 템플릿을 쓰면 생기지 않는다.
- HANDOFF의 downstream 2.1 컴파일·검증 경로는 시험하지 않았다(작은 기능에서는 쓰지 않음).

### JOENESS 이슈 목록 (고치지 않음)

1. 연결 본문(`assets/AGENTS.md`)의 `<joedesign>` 자리: 설치 경로가 기계마다 달라 프로젝트 AGENTS.md에 절대 경로가 커밋된다. 경로를 정하는 안내가 없다.
2. DESIGN 템플릿이 두 개다: JOENESS `assets/DESIGN.md`(6줄)와 JOEDESIGN `templates/DESIGN.md`(Rule Coverage·Report Form). JOENESS 연결 본문은 "DESIGN rule table 행"을 Check로 요구하지만 자기 템플릿에는 그 표가 없다. 둘 다 쓸 때 어느 것을 쓰는지 지침이 없다.
3. ROADMAP 템플릿 `Product authority`에 revision·승인 상태를 적는 칸이 없다(JOEFLOW 프로젝트면 `approval_status.py` 결과가 들어갈 자리).

### JOEDESIGN 이슈 목록 (고치지 않음)

1. 보고서의 여섯 줄(JOENESS)과 결과 목록(JOEDESIGN) 순서·위치가 어느 문서에도 없어 시험자가 정했다. `report-check.mjs`는 통과시켰다.
2. 측정 환경: 앱 내 미리보기 창이 `file://` 페이지의 연결 CSS를 읽지 못해 같은 CSS를 주입해 쟀다. 도구 결함이 아니라 환경 한계지만, 렌더 측정의 "rendered" 표기가 이런 주입을 구별하지 않는다.

## 회귀

- 테스트: 1.6.0 기준 1,224개 중 실패 8(환경 원인, 1.2.0 때부터 같은 8건: projection audit fixture 해시·schema 런타임 등). 1.7.0 후보 1,244개(새 20개) 중 실패 8, 실패 목록이 1.6.0과 같다. 첫 실행에서 새 실패 1건(`recommendation_problems`가 목록인 `confidence`를 집합에서 찾다 TypeError, `test_unknown_resolution_v020`)을 찾아 고친 뒤 다시 돌린 결과다.
- 오목 rev 43 사본(`state.json` 원본 복사): `validate_state`·`validate_closure`·`projection_check` 출력이 1.6.0과 같다. `approval_status`는 새 키 `joeflow_version`만 늘고 나머지가 같다.
- 고정 모듈(`authority_binding_v2.py`, `approval_v2.py`, `state_validation_v2.py`, state 스키마, semantic-freeze 계약)은 바꾸지 않았다. `grill_v2.py`는 고정 목록 밖이다.

## 확인된 것 / 확인되지 않은 것

확인된 것
- A·B: 오목 사례 그대로 재현, 수정 뒤 메시지가 칸·값·인자를 말하고 생성 단계에서 막힘.
- C: 원문 기록·전달 경로 기록·`--relayed-from` 단독 거절·읽기 전용 검사 명령이 테스트와 시험에서 동작.
- D: 판 고정·불일치 알림·스키마 안내가 테스트와 시험에서 동작.
- 세 도구 한 바퀴: JOEFLOW ID가 ROADMAP·DESIGN·보고·TASK로 이어짐(시험자가 이어 붙임), 도장 `--verify` 일치, spot check 불일치가 완료를 막음.

확인되지 않은 것
- 자동 권한 분류기가 `check_approval.py`를 막지 않는지(오목과 같은 전달 승인 상황에서 재현하지 않음).
- 에이전트가 새 지침만 보고 전달 승인을 원문 세션에 넘기는지(행동 A/B 없음, 유료 실행 0회).
- 모의 승인이라 실제 사용자 승인 흐름의 시각(`--at` 메시지 시각) 사용.
- JOEFLOW-ux 1.2.0 → 1.6.0 사이 레코드 호환성 상세.
- 시험 측정은 미리보기 창 CSS 주입 렌더로 했다.

## 사용자 대신 정한 것

- 승인 원문·판 고정은 state가 아니라 `joeflow-project.json`에 둔다(스키마를 바꾸면 기존 승인이 낡기 때문).
- `--quote` 없이 승인하면 sidecar를 만들지 않는다.
- 판 불일치는 알리기만 하고 막지 않는다.
- READY_FOR_REVIEW 쓰기는 readiness 실패 때 막는다(1.6.0은 썼다). OPEN으로는 쓸 수 있다.
- 실행 판은 새 `skills/joewrks-product-definition/VERSION`(현재 1.6.0, 후보라 올리지 않음)에서 읽는다.
