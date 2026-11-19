# JOEFLOW 2.0 사전 조사 — 목록, 참조 그래프, 보안 점검 (읽기 전용)

조사일 2026-11-19 · 기준 커밋 `8bcc9b4` (main, 태그 `v1.7.3` 이후 문서·평가 커밋 5개) · 이 파일 외 변경 없음.
표기: 홈 경로 → `~`, Windows 사용자 이름 → `<user>`, gmail 주소 → `<email>`.

## 결론

1. **버전 올리기와 출판 게이트가 충돌한다.** 스킬 폴더 안의 `skills/joewrks-product-definition/VERSION`(값 `1.7.3`)은 스킬 해시에 포함되고, `tests/test_friction_170.py`가 이 값과 루트 `VERSION`이 같아야 한다고 검사한다. "스킬 해시 1.x와 동일 + 전체 테스트 통과"와 "2.0 표기"는 동시에 만족할 수 없으므로, 게이트에서 `VERSION` 한 파일을 빼거나 2.0을 저장소 버전으로만 둘지 먼저 정해야 한다. 기준 해시: `98e2b5ea15c876ef5716da57ea30db2e1a56ec28`(파일 201개, `v1.7.3`과 HEAD에서 같음).
2. **정리 작업은 테스트와 스킬 코드가 고정해 둔 경로에 막힌다.** `evals/semantic-review-v0.4.3`은 테스트 2개가 git tree 해시로 고정하고 있다. 여기에 `evals/core-semantic-closure-v2-m6`, `product-definition/`까지 3개는 스킬 내부 `scripts/audit_reviewer_runner.py`의 `FROZEN_PATHS`에도 들어 있다. 이 경로들을 옮기면 스킬을 고치지 않는 한 깨진다. 따라서 평가 기록 보관 이동은 "무참조 폴더만 이동"으로 범위를 좁혀야 한다.
3. **README 축약은 테스트가 잡고 있다.** `tests/test_skill_package.py`가 README에 들어가야 할 6개 영문 절, 6개 한글 절, 언어 링크, 역할 문구 6개, 링크 2개를, `test_semantic_v012.py`가 `validate_state.py`·`validate_closure.py` 문자열을 요구한다. 축약하려면 테스트도 함께 고쳐야 한다(테스트는 스킬 밖이므로 범위 안이다).
4. **보안:** 작업 트리와 이력 전체(커밋 399개)에서 실제 비밀 값은 찾지 못했다(`sk-ant-test-*` 같은 테스트용 가짜 표식만 있다). 개인 식별자는 작업 트리 10개 파일에 13회, 이력에서는 삭제된 원시 로그를 포함해 4,348줄, 커밋 20개에 남아 있다. 모든 커밋의 작성자 메타데이터에 `<email>`이 들어 있고, 일부 커밋은 실명 작성자 이름을 쓴다. 스크립트에서 `shell=True`, `eval`/`exec`, 다운로드 경로는 발견되지 않았다.
5. **엄격한 의미의 제거 후보는 1개**(`.superpowers/…/continuation-task-a-report.md`)뿐이다. 추적 중인 캐시나 추적되지 않은 파일은 0개다. 아무 데서도 참조하지 않는 과거 기록 21개는 삭제가 아니라 보관 이동 대상이다. Claude Code 설치 경로(clone + `git pull --ff-only`), 업데이트, 제거 방법은 저장소 어디에도 문서가 없다.

---

## 1. 목록 (`git ls-files` 958개)

### 1-요약

| 분류 | 경로 | 파일 수 | 바이트 |
|---|---|---:|---:|
| (a) 에이전트가 실행 중 읽음 | `skills/joewrks-product-definition/**` | 201 | 1,916,162 |
| (a′) 스킬 코드가 경로로 읽는 저장소 파일 | `product-definition/`, `evals/semantic-review-v0.4.3`, `evals/core-semantic-closure-v2-m6` (`scripts/audit_reviewer_runner.py` FROZEN_PATHS) | 아래 (d) 참조 | — |
| (b) 사람이 읽음 | `README.md`, `PROGRAM_ARCHITECTURE.md`, `CHANGELOG.md`, `ROADMAP.md`, `VERSION`, `docs/**`(41), `evals/joeflow-u1-personal-install/PERSONAL_INSTALL_RECORD.md` | 46 | 약 0.8 MB |
| (c) 테스트 | `tests/**`(지원 모듈과 `tests/fixtures/` 16개 포함) | 121 | 2,865,359 |
| (d) 기록 | `evals/**` | 579 | 약 6.6 MB |
| (d) 기록(도그푸드 산출물) | `product-definition/client-feedback-portal-dogfood/` | 8 | 295,736 |
| (e) 무참조이며 기록·테스트 아님 | `.superpowers/sdd/2026-08-30-…/continuation-task-a-report.md` | 1 | 4,569 |
| 설정 | `.gitattributes`, `.gitignore` | 2 | — |

- 저장소 최상위에 `scripts/` 폴더는 없다(과제 설명과 다름). 저장소 수준 스크립트는 모두 `evals/**` 아래에 있다.
- `AGENTS.md`, `.github/`(CI), 의존성 매니페스트는 없다.
- 추적되지 않은 파일과 무시된 파일은 0개다(`git status --porcelain --ignored` 출력 없음). `__pycache__`도 추적되지 않는다.
- `.gitignore` 내용: `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.DS_Store`.
- `.gitattributes`는 `evals/semantic-review-v0.4.3/calibration/**`, `evals/post-m6-…/RUNNER_CAPABILITY_EVIDENCE.json`, `evals/joeflow-regression-environment-20261013/*.log`의 바이트(eol=lf)를 고정한다. 이 폴더들을 옮기면 `.gitattributes`도 함께 고쳐야 한다.

### 1-(c) 테스트가 의존하는 스킬 밖 경로 (옮기면 테스트가 깨짐)

| 경로 | 의존하는 테스트 | 비고 |
|---|---|---|
| `evals/semantic-review-v0.4.3` | `test_downstream_v2_frozen_boundaries`, `test_downstream_v21_frozen_boundaries`(tree 해시 `a2dc7ee…`), `test_semantic_review_calibration_*`, `test_official_calibration_controller`, `test_semantic_review_human_packet` | 스킬 audit FROZEN_PATHS, .gitattributes |
| `evals/core-semantic-closure-v2-m6` | `test_core_semantic_closure_v2_m6_dogfood_phase_a/b`, `test_m6_*`, `test_v2_installed_workflow`, `test_downstream_v21_dogfood_replay` | 스킬 audit FROZEN_PATHS |
| `evals/downstream-conformance-v0.4.1/evidence/…` | `test_downstream_handoff` | |
| `evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json` | `test_reviewer_runner_audit` | .gitattributes |
| `evals/joeflow-f03-f04/fixtures` | `test_candidate_preflight_projection_audit` | |
| `product-definition/client-feedback-portal-dogfood/state.json` | `test_downstream_product_bundles`, `test_core_semantic_closure_v2_m6_dogfood_phase_a` | 스킬 audit FROZEN_PATHS(`product-definition`) |
| `README.md`, `PROGRAM_ARCHITECTURE.md`, `CHANGELOG.md`, `VERSION`, `docs/regression-environment.md` | `test_skill_package`, `test_semantic_v012`, `test_v2_installed_workflow`, `test_friction_170` | 문구를 검사함(4절 참조) |

### 1-(d) 기록: `evals/` 하위 폴더별

| 폴더 | 파일 | 바이트 | 테스트/스킬 고정 |
|---|---:|---:|---|
| 2026-10-23-ux-planning-ab | 20 | 217,176 | |
| 2026-11-12-classifier-check-170 | 2 | 3,606 | |
| 2026-11-12-friction-170 | 11 | 35,348 | (docstring에서 언급만) |
| 2026-11-13-stale-title-171 | 60 | 447,345 | |
| 2026-11-15-stale-title-172 | 127 | 500,641 | |
| 2026-11-17-safety-sentence-172 | 70 | 339,757 | 현재 설치기 `install_1_7_3.py` 위치 |
| 2026-11-18-fact-line-173 | 36 | 117,482 | |
| behavioral-v0.2 | 67 | 285,881 | |
| core-semantic-closure-v2-m5-1 | 3 | 21,130 | |
| **core-semantic-closure-v2-m6** | 22 | 1,907,676 | **고정** |
| **downstream-conformance-v0.4.1** | 14 | 761,192 | **고정** |
| end-to-end-v0.3 | 14 | 44,763 | |
| end-to-end-v0.3.1 | 9 | 10,101 | |
| **joeflow-f03-f04** | 15 | 66,676 | **고정** |
| joeflow-f06-manifest-encoding | 1 | 5,699 | |
| joeflow-regression-environment-20261013 | 9 | 245,228 | .gitattributes, docs |
| joeflow-u1-7-ux-inheritance | 2 | 4,421 | |
| joeflow-u1-approval-ab | 2 | 6,099 | |
| joeflow-u1-personal-install | 9 | 143,880 | 설치 영수증 경로(설치기가 씀) |
| joeflow-u2-10-feature-extension | 3 | 7,081 | |
| joeflow-u2-11-async-profile | 3 | 3,361 | |
| joeflow-u2-12-coverage-inheritance | 19 | 95,331 | |
| joeflow-u2-8-relayed-intent-ab | 6 | 21,233 | |
| joeflow-u2-9-draft-freeze | 2 | 3,582 | |
| joeflow-v1.1.0 | 3 | 101,440 | |
| **post-m6-semantic-review-reliability-enablement** | 3 | 37,893 | **고정** |
| **semantic-review-v0.4.3** | 41 | 695,059 | **고정(tree 해시)** |
| 최상위 md 7개 (`baseline-results.md` 등) | 7 | 13,357 | |

### 1-(e) 제거 후보와 보관 이동 후보 (근거 포함)

판정 방법: 각 파일의 경로와 파일 이름을 추적 중인 다른 모든 파일에서 문자열로 검색했다.

| 후보 | 근거 | 권고 |
|---|---|---|
| `.superpowers/sdd/2026-08-30-core-semantic-closure-v2-m6-integration-adoption/continuation-task-a-report.md` | 파일 이름과 `.superpowers` 모두 참조 0건. 도구 작업용 숨김 폴더에 남은 중간 보고서다 | **제거 후보(1)**. 기록으로 남기려면 docs 보관 폴더로 이동 |
| `docs/superpowers/plans/*` 중 참조 0건인 13개: behavioral-evaluation-v0.2, end-to-end-dogfood-v0.3, joewrks-product-definition, end-to-end-make-dogfood-v0.3.1, downstream-conformance-v0.4.1, downstream-contract-authority-v0.4.1.1, m1-state-foundation, m2/m3/m4/m5/m6 `-self-review`(5), post-m6-…-enablement | 참조 0건. 과거 설계 기록이다 | 보관 이동(13) |
| `evals/v0.1.1-…-results.md`, `evals/v0.1.2-…-results.md`, `evals/v0.1.2.1-…-results.md` | 참조 0건 | 보관 이동(3) |
| `evals/2026-10-23-ux-planning-ab/score.py`, `evals/joeflow-u2-12-coverage-inheritance/{cobind,groups,mechanisms}.py`, `evals/semantic-review-v0.4.3/calibration/diagnose_run_01.py` | 참조 0건. 기록 폴더에 들어 있는 분석 스크립트다(마지막 파일은 고정 폴더 안이라 이동 불가) | 소속 폴더와 함께 보관(4), 고정 폴더 안의 1개는 유지 |
| 같은 내용의 blob 중복: `post-check-17x.json` 40개 동일, `planning-review-core.html` 9개, `diff.txt`/`diff-stat.txt` 7·7·6·5개, fixture `state.json` 4개 | `git ls-files -s` 해시가 같다. 실행별 증거로 각각 기록돼 있다 | **유지**: git은 같은 blob을 한 번만 저장하므로 저장 공간 이득이 없고, 지우면 실행 기록이 끊긴다 |
| `skills/…/downstream/semantic_review/artifacts/{reviewer-brief-v1.md,responsibility-profile-v1.json}`, `…/schemas/semantic-review-output.schema.json` ↔ `evals/semantic-review-v0.4.3/calibration/…/reviewer-package/` | 같은 blob이지만 양쪽 다 고정돼 있다 | 유지 |
| 지난 설치기 7개 (`install_u1_7`, `u2`, `u2_8`, `u2_10_11`, `1_7_0`, `1_7_1`, `1_7_2`) | CHANGELOG, ROADMAP, 영수증 기록이 참조한다. 각각 특정 BASE→TIP 쌍에만 쓰는 일회용이다 | 기록으로 유지. 2.0 설치기 설계 때 하나로 합칠 후보 |

합계: 엄격한 제거 후보 **1개**, 무참조 보관 이동 후보 **21개**(13 + 3 + 이동 가능한 스크립트 4 + .superpowers 1). 그 외 기록 폴더 전체의 이동 여부는 위 "고정" 표시를 피해서 정하면 된다.

---

## 2. 참조 그래프

### 2-1. 스킬 내부 엣지 (파일 이름이나 상대 링크로 언급한 것)

| 출발 | 대상 수 | 대상 |
|---|---:|---|
| `SKILL.md` | 31 | references: workflow-v0.2.0, reentry-workflow-v0.2.0, figma-make-handoff, state-contract-v0.2.0, first-plan-guide, state-contract, ux-state-taxonomy, coverage-inheritance, feature-extension · schemas: state-v0.2.0, state · templates: figma-make-handoff.md, master-planning-spec.md, planning-review-core.html, state-v0.2.0.example.json, state.example.json · scripts: validate_state, migrate_state, record_approval, check_approval, compile_downstream_v2, audit_downstream_v2, build_semantic_review_v2, verify_runtime_v21, verify_runtime_v2, new_records, open_revision, joeflow_version, update_projection, projection_check, approval_status |
| `references/workflow-v0.2.0.md` | 31 | references: coverage-inheritance, feature-extension, first-plan-guide, reentry-workflow-v0.2.0, ux-state-taxonomy, ux-profile-inheritance-v1.json · templates: planning-review-core.html, state-v0.2.0.example.json · scripts 23개(approval_status, audit_downstream_v2, audit_planning_projections, build_approval_manifest, build_semantic_review_v2, check_approval, compact_coverage, compile_downstream_v2, draft_freeze, explain_state_errors, joeflow_version, migrate_state, new_records, open_revision, preflight_state_candidate, projection_check, record_approval, refresh_bindings, supersede_records, update_projection, validate_closure, validate_state, verify_runtime_v21) |
| `references/first-plan-guide.md` | 14 | coverage-inheritance, feature-extension, workflow-v0.2.0; templates/examples 2개, state-v0.2.0.example.json; scripts: draft_freeze, explain_state_errors, new_records, next_product_question, open_revision, supersede_records, update_projection, validate_state |
| `references/coverage-inheritance.md` | 6 | grill-profile-inheritance-v1.json, ux-action-shapes-v2.json; scripts: compact_coverage, draft_freeze, open_revision, refresh_bindings |
| `references/figma-make-handoff.md` | 5 | downstream-v2-contract, downstream-v2.1-contract, workflow-v0.2.0, templates/planning-review-core.html, `../downstream/README.md`, `../downstream_v2/README.md` |
| `references/state-contract-v0.2.0.md` | 5 | discovery-contract, grill-contract, migration, semantic-freeze-contract, scripts/migrate_state |
| `references/feature-extension.md` | 3 | scripts: audit_downstream_v2, new_records, open_revision |
| `references/downstream-v2.1-contract.md` | 2 | downstream_v21/schemas: action-contract-v21, handoff-definition-v21 |
| `references/semantic-review-v2.1-contract.md` | 2 | downstream_v21/schemas: semantic-review-input/output-v21 |
| `references/state-contract.md` | 2 | schemas/state.schema.json, templates/state.example.json |
| discovery→grill, grill→semantic-freeze, migration→migrate_state, reentry-workflow→state-v0.2.0 schema, runtime-conformance-v0.2.0→verify_runtime_v2 | 각 1 | |
| artifact-dependency-graph, closure-gate, downstream-v2-contract, failure-recovery-taxonomy, implementation-reentry-contract, interrogation-engine, product-coverage-matrix, requirement-taxonomy, runtime-conformance-plan-contract, semantic-freeze-contract, unknown-taxonomy, ux-state-taxonomy | 0 (나가는 엣지 없음) | |

**SKILL.md나 다른 reference가 이름으로 부르지 않는 reference 11개:** artifact-dependency-graph, closure-gate, failure-recovery-taxonomy, implementation-reentry-contract, interrogation-engine, product-coverage-matrix, requirement-taxonomy, runtime-conformance-plan-contract, runtime-conformance-v0.2.0, semantic-review-v2.1-contract, unknown-taxonomy. 이 가운데 9개는 `test_skill_package.py`의 필수 파일 목록에 있다. 스킬 폴더 밖 범위이므로 2.0에서는 손대지 않고 기록만 해 둔다.

### 2-2. 스킬이 가리키는 저장소 수준 파일

| 스킬 파일 | 가리키는 대상 | 2.0 영향 |
|---|---|---|
| `scripts/audit_reviewer_runner.py` | `product-definition`, `evals/semantic-review-v0.4.3`, `evals/core-semantic-closure-v2-m6` (FROZEN_PATHS, git으로 검사) | 이 세 경로는 이동이나 이름 변경 금지 |
| `downstream/README.md` | `evals/semantic-review-v0.4.3/RELIABILITY_GATE_SPEC.md` (본문 인용) | 이동 금지 |
| `downstream/run_frozen_regressions.py` | `evals/cross-domain-v0.4/…` (**다른 저장소의 고정 커밋** 안 경로. 이 저장소에는 없음) | 영향 없음 |
| `SKILL.md`, `workflow-v0.2.0.md` | "ROADMAP item", "DESIGN.md" | 사용자 프로젝트(JOENESS/JOEDESIGN)의 파일이며 이 저장소의 ROADMAP.md가 아님 |
| 여러 파일의 `product-definition/<slug>/state.json` | 사용자 프로젝트 경로 | 영향 없음 |

**README와 PROGRAM_ARCHITECTURE 가운데 에이전트가 읽는 파일이 가리키는 부분: 없음.** 스킬 폴더의 어떤 파일도 `README.md`(루트), `PROGRAM_ARCHITECTURE.md`, `CHANGELOG.md`를 언급하지 않는다. README를 줄일 때 지켜야 할 것은 테스트가 요구하는 문구뿐이다(4절).

### 2-3. 사람용 문서 사이의 중복

| 중복 | 위치 |
|---|---|
| README 영문과 한글 본문 전체 | 350줄 중 각 반씩 같은 내용이다. 테스트가 두 언어 모두를 요구한다 |
| 6개 절 골격("1. 핵심 요약" … "6. 한계") | README, PROGRAM_ARCHITECTURE, docs/regression-environment 3개 문서에 같은 형태로 있다(테스트가 강제) |
| 설치 안내 | PROGRAM_ARCHITECTURE "설치·시작"이 README 사용 방법을 링크로 넘긴다(중복 아님, 정상) |
| 저장소 구조도 | PROGRAM_ARCHITECTURE "Repository mapping"이 실제와 어긋난다(`reviewer_runner/`, `downstream_v21` 현행 표기, evals 최신 폴더가 빠짐). 오래돼 낡은 정보다 |
| 상태 표식(`PRODUCT_DEFINITION_STATE_V2_DEFAULT` 등) | SKILL.md와 PROGRAM_ARCHITECTURE에 모두 있다. 테스트가 PROGRAM_ARCHITECTURE 쪽을 요구한다 |
| SKILL.md와 workflow-v0.2.0.md | 그대로 같은 문장(70자 이상)은 0개다. 승인 기록 절차 같은 내용은 바꿔 쓴 형태로 겹친다(스킬 범위라 2.0에서 손대지 않음) |

### 2-4. Codex 오버레이 설치기가 다루는 범위 (`evals/2026-11-17-safety-sentence-172/install_1_7_3.py`)

| 항목 | 내용 |
|---|---|
| 읽는 것 | git 객체 `BASE=6a74446`, 인자 `<TIP>`, `V110=e3be5d1…`; `~/.codex/skills/joewrks-product-definition/**`; 영수증 `evals/joeflow-u1-personal-install/personal-install-overlay-receipt.json` |
| 그대로 복사 | `git diff --name-status BASE TIP -- skills/joewrks-product-definition` 결과 가운데 합성 대상이 아닌 파일. 설치본이 BASE와 같은지 sha256으로 확인한 뒤 TIP blob을 쓴다 |
| 합성(hunk 적용) | `SKILL.md`, `references/workflow-v0.2.0.md`. 임시 폴더에서 `patch -p0 -F3`로 적용하고, 추가·삭제된 줄을 모두 다시 확인한다 |
| 과거에 합성됨(origin 표시) | `templates/master-planning-spec.md` |
| 로컬 오버레이 보존(2개) | `references/figma-make-handoff.md`, `templates/figma-make-handoff.md` (영수증의 `preserved_local_overlay`) |
| 영수증 현황 | 설치 파일 274개 = 저장소 추적 201개 기준 `branch_tip` 46 + `v1.1.0_and_branch_tip` 149 + 합성 3 + 로컬 오버레이 2 + `v1.1.0_only` 1 + `__pycache__` 73 |
| 쓰는 위치 | `~/.codex/skills/joewrks-product-definition/**`, `~/.codex/skills-backups/joewrks-product-definition-before-1-7-3-<tip>-<날짜>/`, 저장소 안 영수증 JSON |

**의미:** 개인 Codex 설치본은 저장소 스킬 폴더와 바이트 단위로 같지 않다(합성 3개, 오버레이 2개). 따라서 "스킬 해시 동일" 게이트는 저장소 기준으로만 성립하고, 설치본 해시와는 원래부터 다르다. 2.0 설치기 계획은 이 5개 파일을 명시적으로 다뤄야 한다.

---

## 3. 보안 점검 (보고만 하고 고치지 않음)

### 3-(i) 비밀 값

| 검사 | 작업 트리 | 이력(전체 ref, 커밋 399개) |
|---|---|---|
| AWS `AKIA…`, GitHub `ghp_`/`github_pat_`, `sk-…`/`sk-ant-…`, Slack `xox?-`, Google `AIza…`, `BEGIN … PRIVATE KEY`, DB 접속 문자열 `scheme://user@`, `password=`/`api_key=`/`secret=` 값 할당, `Bearer` 토큰 | 실제 값 0건. 테스트 상수 1건(`tests/test_reviewer_runner_identity.py:137`의 `"controller-only-oracle-material"`, 가짜 값) | 실제 키 형태(`sk-ant-api03-…`, `ghp_` 36자, `AKIA` 16자) 0건. `sk-ant-` 접두 문자열 6종은 모두 테스트용 가짜 표식(`sk-ant-test-secret`, `-test-marker`, `-secret`, `-task-4-secret`, `-reader-exception`, `-transport-exception`)이며, 커밋 `fda3932`에서 삭제됐다 |
| `.env`, `*.pem`, `*.key`, `id_rsa`, `*.p12/pfx` 파일 | 0개 | 0개 |
| API 키 환경 변수 | `OPENAI_API_KEY`는 `tests/test_reviewer_runner_audit.py`에서 sentinel 값으로 쓰는 것뿐이다. `ANTHROPIC_API_KEY` 참조 0건 | — |

### 3-(ii) 개인 식별자

| 식별자 | 작업 트리 파일 / 횟수 | 이력: 변경 줄 / 관련 커밋 | 이미 `~`로 가림? |
|---|---|---|---|
| `<user>` (Windows 사용자 이름) | 10 / 13 | 4,348줄 / 20 커밋 | 아니오 |
| `<email>` (본문) | 0 / 0 | 0 / 0 | 해당 없음 |
| `<email>` (**커밋 작성자 메타데이터**) | — | 커밋 399개 전부(작성자 이름 2종, 그중 1종은 실명 포함) | 아니오. 이력을 다시 쓰지 않고는 가릴 수 없다 |
| `C:/Users` | 3 / 3 | 22줄 / 7 커밋 | 아니오 |
| `C:\Users` (JSON의 `C:\\Users` 포함) | 5 / 7 | 8줄 / 4 커밋 | 아니오 |
| `AppData` | 7 / 10 (그중 4회는 `…\AppData\Local\Temp\tmp…` 앞부분이 잘린 테스트 로그, 1회는 가림용 정규식) | 10줄 / 5 커밋 | 일부 |
| `~/.codex` (이미 가린 형태) | 7 / 22 | 41줄 / 9 커밋 | **예**(f01cb0c에서 정리) |

작업 트리에서 `<user>`가 나오는 곳:

| 파일 | 내용 형태 | 고정 여부 |
|---|---|---|
| `docs/superpowers/plans/2026-08-20-behavioral-evaluation-v0.2.md:11`, `…end-to-end-dogfood-v0.3.md:11`, `2026-08-21-…make-dogfood-v0.3.1.md:11` | `C:/Users/<user>/.codex/attachments/<uuid>/pasted-text.txt` | 자유(가릴 수 있음) |
| `evals/behavioral-v0.2/transcripts/eval-0{1,2,3}-control.md` (5회) | `C:\Users\<user>\.codex\plugins\cache\…`, `C:\Users\<user>\.agents\skills\…` | 자유 |
| `evals/post-m6-semantic-review-reliability-enablement/ISOLATION_CAPABILITY_AUDIT.md:97` | `C:\Users\<user>\AppData\Local\Temp` | 폴더는 테스트가 고정하지만 이 파일은 아님. 가릴 수 있음 |
| `evals/semantic-review-v0.4.3/evidence/calibration-disposition/MANIFEST_ONLY_ISOLATION_CAPABILITY_EVIDENCE.json:31`, `…/V043_CALIBRATION_ENVIRONMENT_BLOCKED_DISPOSITION.md:64` | 같은 Temp 경로 | **tree 해시 고정. 가리면 테스트 2개가 실패한다** |
| `evals/joeflow-regression-environment-20261013/focused-red.log` (2회) | 같은 줄 안의 경로 | .gitattributes가 바이트 고정(가릴 수는 있음) |

이력에서 나온 4,348줄은 대부분 지금은 지워진 `evals/semantic-review-v0.4.3/calibration/run-01/raw-outputs/*/codex-events.jsonl`(Codex 원시 이벤트 로그)에서 나온다. GitHub에 push된 브랜치(원격 브랜치 9개 확인)에 남아 있을 수 있다. 원격 공개 여부는 이 세션에서 확인하지 않았다.

### 3-(iii) 스크립트의 외부 입력과 쓰기 위치

| 스크립트 | 외부 입력 | 쓰는 위치 | subprocess / 위험 호출 |
|---|---|---|---|
| `skills/…/scripts/projection_check.py` | 인자: state.json 경로, `--spec` MD, `--review` HTML, `--require-types`, `--draft`. JSON은 `json.loads`로 읽음 | **쓰지 않음**(stdout만 출력) | 없음. **신뢰할 수 없는 HTML/Markdown은 `re`와 문자열 함수로만 다룬다**. HTML 파서, `eval`, 파일 쓰기, 네트워크가 없다. 사용자 정규식은 받지 않고 `re.escape`를 쓴다. 잠재 위험은 큰 입력에서 `<!--.*?-->`(re.S) 같은 비탐욕 패턴의 처리 시간 정도이며, 측정하지 않았다 |
| `scripts/update_projection.py` | state, `--spec`, `--review`, `--write`, `--adopt` | `--write`일 때 `--spec`/`--review`로 받은 경로(사용자 프로젝트) | 없음 |
| `scripts/open_revision.py`, `record_approval.py`, `refresh_bindings.py`, `project_pin.py`, `migrate_state.py` | state.json, patch JSON, 인자 | 대상 state.json 또는 `joeflow-project.json` 옆 임시 파일 → `os.replace`(원자적 교체) | 없음 |
| `scripts/new_records.py`, `supersede_records.py`, `draft_freeze.py`, `compact_coverage.py` | state, 인자 | 인자로 받은 patch 또는 state 경로 | 없음 |
| `scripts/audit_reviewer_runner.py` | 저장소 경로 | 없음 | `subprocess.run(["git", …])` 리스트 인자, shell 미사용 |
| `reviewer_runner/evidence.py` | 저장소 루트 | 자기가 만든 증거 디렉터리(`mkdir`, `unlink`) | `git` 리스트 인자, `shell=False` 명시 |
| `downstream/adapter_runtime.py` | **계약에 정의된 어댑터 명령(argv 리스트)**, env | `tempfile.TemporaryDirectory` 안의 requests/responses JSONL | `subprocess.run(list(command), timeout=60)`, shell 미사용. 명령 자체는 호출자가 정하므로 신뢰 경계는 호출자에게 있다 |
| `downstream/run_frozen_regressions.py` | 외부 저장소 경로, 고정 커밋 | 인자로 받은 출력 경로 | `git -C` 리스트 인자 |
| `integration_v2/dogfood_v21.py`, `downstream/semantic_review/goldens.py` | 픽스처 | 호출자가 준 루트 아래 | 없음 |
| `downstream/adapters/*.mjs`, `vitest*.ts` | `JOEWRKS_REQUEST_JSONL`/`RESPONSE_JSONL` 환경 변수 | 응답 JSONL | `child_process` 미사용 |
| `evals/…/install_1_7_3.py` (그리고 같은 형태의 `install_1_7_0/1/2.py`) | 인자 `<TIP>`(`git rev-parse --verify`로 확인), git 객체, 설치본, 영수증 JSON | `~/.codex/skills/joewrks-product-definition/**`, `~/.codex/skills-backups/…`, 저장소 영수증 | `git`·`patch` 리스트 인자, shell 미사용. **`patch -p0 -F3`는 임시 폴더의 `target` 1개 파일에만 적용**한다(`SKILL.md`, `workflow-v0.2.0.md`의 BASE..TIP diff). 다운로드 없음. 재개할 때 백업과 다른 설치본 파일을 덮어쓰고 지운다(설치 폴더 안에 한정) |
| `install_u1_7.py`, `install_u2.py`, `install_u2_8.py`, `install_u2_10_11.py` | 같은 방식(BASE/TIP 하드코딩) | 같은 위치. `install_u2`는 `master-planning-spec.md`도 합성했다. `-F3` 없이 엄격한 patch를 쓴다 | 같음 |
| `evals/*/collect.py`, `measure.py` 등 | 실행 기록 폴더 | 기록 폴더 | `os.environ` 복사 후 PYTHONIOENCODING만 설정 |

저장소 전체(`tests/` 제외)에서 `shell=True`, `os.system`, `os.popen`, `eval(`, `exec(`, `pickle`, `yaml.load`, `requests`/`http.client`/`socket`, XML/HTML 파서는 0건이다. `urllib`은 `downstream_v21/field_refs.py`의 `urllib.parse.quote/unquote_to_bytes` 하나뿐이다(네트워크 아님). 쓰기 위치는 모두 사용자 프로젝트(인자로 받은 경로), 임시 폴더, `~/.codex` 셋 중 하나다.

### 3-(iv) 의존성 매니페스트

없다(`requirements*.txt`, `pyproject.toml`, `setup.*`, `Pipfile`, `package.json`, lock 파일 모두 없음). `pip audit`과 `npm audit`은 매니페스트도 없고 도구 설치도 필요해서 **실행하지 않았다**. 대신 `test_skill_package.py`가 `scripts/*.py`의 import가 표준 라이브러리와 형제 모듈뿐인지 AST로 강제한다. `downstream/adapters/vitest*`는 vitest를 쓰지만 버전을 고정한 매니페스트가 없다(외부 고정 저장소에서만 실행됨).

### 3-(v) CI

`.github/workflows`가 없다. 권한이나 secrets 사용도 해당 없음.

---

## 4. 사용 문서

### 4-1. README 측정

- 350줄, 공백 기준 1,394단어(영문 + 한글). 비교: PROGRAM_ARCHITECTURE 302줄, CHANGELOG 120줄, ROADMAP 71줄, docs/regression-environment 174줄.
- 절(두 언어 동일): 1 Summary/핵심 요약 · 2 Design Purpose/설계 목적(Objectives, Replacement scope, Non-replacement scope) · 3 Key Features/주요 기능 · 4 Usage/사용 방법(When to use, Installation requirements, Example request, Primary validation) · 5 Tool Integration/도구 간 연결 · 6 Limitations/한계.
- **테스트가 요구하는 README 문구(축약해도 남겨야 하고, 아니면 테스트를 고쳐야 함):** `v1.7.3`, 12개 절 제목, `[English](#english) | [한국어](#korean)`, `<a name="english"></a>`/`<a name="korean"></a>`, `Program version: **\`v1.7.3\`**`, `Runtime skill/package ID: …`, `Authoritative source: …`, workflow와 reentry 링크 2개, `# JOEFLOW`가 정확히 1번, 역할 문구 6개(영·한), `skills/joewrks-product-definition`, `validate_state.py`, `validate_closure.py`.

### 4-2. 두 설치 경로가 문서에 있는가

| 경로 | README | PROGRAM_ARCHITECTURE / docs | 실제 |
|---|---|---|---|
| Codex 일반 복사 | 있음(PowerShell 블록. 기존 설치가 있으면 `throw`) | README로 넘김 | 동작함. 다만 **업데이트 경로가 없다**(이미 설치돼 있으면 거부) |
| Codex 오버레이(`install_<ver>.py`) | **없음**. README는 "No dedicated installer … is currently provided"라고 해서 **사실과 어긋난다** | 없음(CHANGELOG와 PERSONAL_INSTALL_RECORD에만 있음) | 개인 전용이다. 영수증이 직전 버전 상태여야 실행된다 |
| Claude Code(clean clone + `git pull --ff-only`) | **없음** | **없음**(저장소 전체에서 `pull --ff-only`, `.claude/skills` 0건) | 이 세션은 연결 방식(복사, 링크, 경로 설정)을 확인하지 않았다 |
| 제거 | 없음 | 없음 | — |

### 4-3. 한 쪽짜리 Quickstart 초안 (오늘 존재하는 명령만 사용)

| 단계 | 명령(현재 있는 것) | 문서 상태 |
|---|---|---|
| 1a. 설치: Codex 일반 복사 | README의 PowerShell 블록(`git clone https://github.com/JOEWRKS/JOEFLOW.git` → `Copy-Item … $env:CODEX_HOME\skills\joewrks-product-definition`) | 있음 |
| 1b. 설치: Codex 오버레이(개인) | `python -B evals/2026-11-17-safety-sentence-172/install_1_7_3.py <1.7.3 릴리스 커밋>` | **README에 없고 README와 모순.** 일반 사용자용이 아님 |
| 1c. 설치: Claude Code | `git clone https://github.com/JOEWRKS/JOEFLOW.git` 후 스킬 폴더 연결 | **문서 없음, 연결 방법 미확인** |
| 2. 첫 실행 | 새 대화에서 README의 Example request(`Use $joewrks-product-definition for this project. …`) | 있음(Codex `$` 호출 표기만 있고 Claude Code 호출법은 없음) |
| 2′. 검증 | `python <skill>/scripts/validate_state.py path/to/state.json` · `python <skill>/scripts/validate_closure.py path/to/state.json` | 있음 |
| 3. 투영 갱신과 검사 | `python <skill>/scripts/update_projection.py STATE_JSON --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html --write` → `python <skill>/scripts/projection_check.py STATE_JSON --spec MASTER_PLANNING_SPEC.md --review planning-review-core.html` | SKILL.md와 workflow에만 있음. **README에 없음** |
| 3′. 프로젝트 버전 고정 | `python <skill>/scripts/joeflow_version.py STATE_JSON --pin` | SKILL.md에만 있음 |
| 4. 새 버전으로 업데이트 | Codex 일반: **없음**(README 블록은 기존 설치를 거부) · 오버레이: 버전마다 새 `install_<ver>.py` · Claude Code: `git pull --ff-only` | **문서 없음 또는 모순** |
| 5. 제거 | 명령 없음 | **문서 없음** |

---

## 5. D 후보 (조치하지 않음)

### 5-1. 2.0에서 낡게 될 문장 (스킬 폴더 안이라 게이트상 수정 불가, 기록만)

| 파일:줄 | 내용 | 비고 |
|---|---|---|
| `SKILL.md:12` | `JOEFLOW_V1_RELEASE` 상태 표식 | 2.0과 이름이 맞지 않는다. 바꾸면 스킬 해시가 달라진다 |
| `references/coverage-inheritance.md:16,48` | "(1.3.0)", "Measured on real definitions (2026-10-31)" | 날짜·버전이 박힌 문장 |
| `references/feature-extension.md:22` | 예시 locator `app v1.3 (2026-10-31)` | 예시 값이라 영향 적음 |
| `scripts/projection_check.py:68,71,140` | 주석 `1.7.2:`, `(1.7.3)`, `1.7.3:` | 주석일 뿐 동작과 무관 |
| `scripts/project_pin.py:10,14` | docstring 예시 `"joeflow_version": "1.7.0"` | 예시 |
| 스킬 폴더 안 문장 중복 | 그대로 같은 문장(70자 이상) 0개 | — |

저장소 문서 쪽: README의 "No dedicated installer" 문장(사실과 다름), PROGRAM_ARCHITECTURE "Repository mapping"(낡음), CHANGELOG와 ROADMAP의 날짜가 박힌 게시 기록(기록이라 그대로 둠).

### 5-2. `1.7.3` 또는 `1.7.x`를 담은 파일 (평가 기록 제외)

| 파일 | `1.7.3` | `1.7.x` 전체 | 2.0 bump 대상? |
|---|---:|---:|---|
| `VERSION` | 1 | 1 | 예 |
| `skills/joewrks-product-definition/VERSION` | 1 | 1 | **게이트와 충돌**(결론 1) |
| `README.md` | 4 | 4 | 예(테스트 문구와 같이) |
| `PROGRAM_ARCHITECTURE.md` | 3 | 6 | 예(테스트 문구 2개) |
| `CHANGELOG.md` | 3 | 14 | 새 절 `## 2.0.0` 추가 |
| `tests/test_skill_package.py` | 2 | 2 | 예 |
| `tests/test_projection_check_v020.py` | 2 | 5 | 아니오(docstring·주석) |
| `tests/test_friction_170.py` | 0 | 1 | 아니오(docstring) |
| `skills/…/scripts/projection_check.py` | 2 | 3 | 아니오(주석, 스킬) |
| `skills/…/scripts/project_pin.py` | 0 | 2 | 아니오(예시, 스킬) |

평가 기록 안에서 `1.7.3`을 담은 파일은 14개다(install_1_7_3.py, release-notes-v1.7.3.md, report-173.md, fact-line-173 하위 9개, PERSONAL_INSTALL_RECORD.md, 영수증 JSON). 모두 기록이라 bump 대상이 아니다.

### 5-3. 버전 문자열을 검사하는 테스트

| 테스트 | 검사 |
|---|---|
| `tests/test_skill_package.py:24` | `VERSION == "1.7.3"` (하드코딩) |
| `tests/test_skill_package.py:25-30,46` | README에 `v{version}`, PROGRAM_ARCHITECTURE에 `\| 프로그램 릴리스 \| \`v{version}\` \|`와 `이 기준선의 전체 프로그램 릴리스: \`v{version}\``, CHANGELOG에 `## {version}`, README에 `Program version: **\`v1.7.3\`**`(하드코딩) |
| `tests/test_friction_170.py:209` | 스킬 `VERSION`과 루트 `VERSION`이 같아야 함 |
| `tests/test_friction_170.py:221-223` | 고정 픽스처 `"1.2.0"`(bump와 무관) |
| 그 밖의 `"version": "1.0"` 단언 (grill packs, binding contracts) | 계약 버전이라 bump와 무관 |

---

## 확인된 것

- 추적 파일 958개. 추적되지 않은 파일과 무시된 파일 0개. 추적 캐시 0개. 매니페스트·CI·`AGENTS.md`·루트 `scripts/` 없음.
- 스킬 폴더 tree 해시 `98e2b5ea15c876ef5716da57ea30db2e1a56ec28`이 `v1.7.3` 태그와 HEAD에서 같다(파일 201개).
- 스킬 `VERSION` 파일이 `1.7.3`을 담고 있고, 테스트가 이를 루트 `VERSION`과 비교한다.
- `evals/semantic-review-v0.4.3`(tree 해시 테스트), `evals/core-semantic-closure-v2-m6`, `product-definition`(스킬 audit FROZEN_PATHS) 외 테스트 고정 경로 4곳(1-(c) 표).
- 스킬이 루트 README, PROGRAM_ARCHITECTURE, CHANGELOG를 참조하지 않는다. README 축약을 막는 것은 테스트 문구뿐이다.
- 비밀 값은 트리와 이력 모두 0건이다(테스트용 가짜 표식만 있음).
- 개인 식별자 수치(3-(ii) 표). `<email>`은 본문 0건, 커밋 메타데이터에는 전부 있다.
- 스크립트 전체에 shell 문자열 실행, eval/exec, 다운로드가 없다. projection_check는 정규식과 문자열 처리만 하는 읽기 전용이다.
- 오버레이 설치본은 저장소와 다르다(합성 3 + 로컬 오버레이 2 + `v1.1.0_only` 1, 영수증 기준).
- README에는 오버레이·Claude Code·업데이트·제거 설명이 없고, "전용 설치기 없음" 문장은 사실과 어긋난다.

## 확인되지 않은 것

- 테스트 실행 결과(이 세션에서는 돌리지 않았다. 환경 요인 실패 8건은 이전 세션 보고를 따른다).
- GitHub 원격 저장소의 공개 여부, 원격 브랜치 9개에 남은 식별자 수(로컬 `--all` 기준으로만 셌다).
- 실제 `~/.codex` 설치본의 현재 상태(영수증만 읽었고 설치 폴더는 열지 않았다).
- Claude Code 쪽 설치가 어떤 방식으로 스킬 폴더를 연결하는지.
- projection_check 정규식의 큰 입력 처리 시간(ReDoS) 측정.
- vitest 어댑터의 의존성 취약점(매니페스트가 없어 audit 불가).

## 세션이 대신 내린 결정

- (e) 분류는 엄격하게 잡았다. 과거 계획·설계 문서와 무참조 평가 스크립트는 "기록"으로 보고 제거가 아니라 보관 이동 후보로 분류했다.
- 같은 내용의 blob이 여러 경로에 있는 실행 증거 파일은 git이 한 번만 저장하므로 "유지"를 권했다.
- 참조 판정은 파일 이름과 경로의 문자열 일치로 했다. `README.md`, `state.json`, `__init__.py` 같은 흔한 이름은 그래프에서 따로 다루었다.
- `<user>` 수를 셀 때는 대소문자를 무시했다. 이력 수치는 `git log --all -p`의 변경 줄(+/−) 기준이다.
- 이 보고서에 실명 작성자 이름과 이메일은 적지 않았다.
