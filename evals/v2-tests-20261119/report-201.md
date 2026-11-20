# JOEFLOW 2.0.1 후보 준비 보고 (2026-11-20)

대상: 2026-11-19 2.0.0 시험 두 건에서 나온 JOEFLOW 결함. 원 보고서 사본은 [report-docs-joeflow.md](report-docs-joeflow.md)(QUICKSTART 실행 시험, D1~D8)와 [report-integration.md](report-integration.md)(세 도구 연동 시험, JOEFLOW 몫 D2·D10·D12)입니다. 보고서는 참고 자료로 읽었고, 결함마다 재현한 뒤 고쳤습니다. 로컬 커밋까지만 했습니다(push·태그·Release·개인 설치 없음).

## 결함별 처리

| 결함 | 재현 | 처리 |
|---|---|---|
| 연동 D2: 새 프로젝트가 READY_FOR_REVIEW에 못 감 | **재현됨.** 연동 시험의 `state-rev2-before-baseline.json` + `rev3-patch.json`으로 `open_revision.py --status READY_FOR_REVIEW` → `readiness_findings` `discovery_baseline_gaps`·`discovery_procedure_gaps`, `object_id: null`, `written: false` | `revision_v2.open_revision`: READY_FOR_REVIEW이고 baseline이 `CURRENT`가 아니면 `build_discovery_baseline(procedure_complete=True, applicable_surface_classes_complete=True)`로 세움, 보고에 `"discovery_baseline": "ESTABLISHED"`. first-plan-guide 2절 4단계에 안내 |
| 연동 D10: `--evidence` 필수 vs guide 3절 | **모순 재현됨.** `discover-one-question` 예시에 `question --evidence EVD-001`(USER_CONFIRMED_INTENT) → `open_revision --status OPEN`이 `invalid_decision_authority_derivation`(EVIDENCE_RESOLVABLE). 연동 시험에서 통과한 것은 `user-decision`(RESOLVED라 유도 검사 대상 아님)이었기 때문 | guide가 아니라 CLI를 고침: `--evidence`를 선택으로(`default=[]`), help에 의도는 `--reason`에 넣으라고 적음. guide 표에 플래그 이름 추가 |
| 연동 D12: downstream compile/verify 미실행 | 결함 아님(시험 범위 한정) | 처리 없음 |
| 문서 D1: 투영 템플릿 복사 | 문서 확인 + `closed-minimal`로 복사→`update_projection --write`→`projection_check` 모두 exit 0 확인 | QUICKSTART 4절 첫 단계로 복사, `--adopt` 불필요 이유 |
| 문서 D2: `--spec`·`--review` 기준 폴더 | 코드 확인(인자를 그대로 `Path`로 씀) | 4절에 "현재 폴더 기준, state.json 폴더에서 실행"과 `Set-Location` |
| 문서 D3: `validate_closure` exit 1 | 원 보고서 로그와 같음 | 3절에 기대 결과 |
| 문서 D4: `joeflow-project.json` 위치 | `project_pin.py`가 state.json 옆에 씀 | 5·7절 표현 수정 |
| 문서 D5: 버전 고정 | — | README 블록과 Claude Code clone에 `--branch v2.0.1` |
| 문서 D6: 업그레이드 재실행 위험 | 새 블록으로 재현 시험(아래) | README 블록을 `& { … }`로 감싸고 clone 실패 시 `throw`. 6절: 새 빈 폴더 또는 기존 clone에서 `git fetch --tags`·`git checkout <태그>` 뒤 복사 부분만, 백업은 `skills\` 밖. 7절: Codex 삭제 명령과 백업 |
| 문서 D7: PowerShell 5.1 캡처 인코딩 | **재현됨.** `[Console]::OutputEncoding`을 cp949로 두고 `$b = python …` → 깨짐(비교 False). UTF8로 바꾸면 비교 True | QUICKSTART 8절 한 단락 |
| 문서 D8: 오버레이 설치기 | 코드 확인: 쓰는 곳은 `Path.home()/'.codex'/'skills'/…`(CODEX_HOME 안 따름), 멈춤 근거는 `tip_compared` 접두사와 설치 소스 파일 해시 == 영수증 `installed_manifest`(쓰기 전 `assert`) | QUICKSTART 1절 문단을 사실대로. `assert`가 보호이므로 `python -O` 금지 문장, 2.0.1 설치기에 `-O` 차단 줄 |

## D2 수정 방향 선택 근거

- (a) `open_revision`이 baseline을 세움 / (b) finding에 pointer와 next_action / (c) guide 안내 중 **(a)+(c)**.
- READY_FOR_REVIEW 요청은 이미 작성자의 "발견을 마쳤다"는 주장입니다. 기존 `build_discovery_baseline.py`도 `procedure_complete: true`를 조건 없이 적습니다. 그래서 (a)는 지금 있는 수동 경로보다 약하지 않고, "state.json을 직접 고치지 말라"는 원칙과 충돌하던 손수정만 없앱니다. baseline의 나머지 필드(열린 material surface 수, 모순 수, grill pack 완결)는 상태에서 계산되고, readiness 지표가 따로 검사합니다.
- (b)는 (a) 뒤에 이 경로에서 그 finding이 나오지 않아 하지 않았습니다. 손으로 쓴 후보를 `preflight_state_candidate.py`로 검사할 때는 여전히 pointer가 `null`일 수 있습니다(아래 "고치지 않은 것").
- `OPEN`·`BLOCKED` 개정은 baseline을 `NOT_ESTABLISHED`로 둡니다(테스트로 고정). 이미 `CURRENT`인 baseline은 전처럼 재계산합니다.

## README 설치 블록 시험 (PowerShell 5.1.19041, `-Command -` stdin)

URL만 로컬 저장소로, 태그만 `v2.0.0`으로 바꾼 같은 블록, `CODEX_HOME`은 임시 폴더(프로세스 범위).

1. 빈 폴더: clone·복사, 설치본 VERSION 2.0.0.
2. 설치본을 옮긴 뒤 같은 폴더에서 다시: `fatal: destination path 'JOEFLOW' already exists` → 블록의 `throw`로 멈춤, 설치 폴더 생기지 않음.

README 4절 블록을 고정한 테스트는 없었습니다(grep: `test_skill_package`는 버전·제목만 봄).

## 게이트

- `python -B -m unittest tests.test_skill_package tests.test_friction_170 tests.test_first_plan_201`: 30개 통과.
- 고친 모듈 관련: `test_revision_v020`, `test_new_records_v020`, `test_draft_freeze_v020`, `test_discovery_baseline_v020`, `test_feature_extension_v020`, `test_supersede_records_v020`, `test_coverage_inheritance_v020` 포함 84개 중 오류 2(pwsh 없음, 기준선 항목) 외 통과.
- 새 테스트 `tests/test_first_plan_201.py`: 고치기 전 3개 중 2개 실패(D2 `readiness_findings`, D10 `--evidence` 필수), 고친 뒤 통과.
- 전체 `python -B -m unittest discover -s tests`: 1,267개(2.0.0의 1,264 + 새 3) 중 실패 3·오류 5·건너뜀 1. 실패·오류 8건 목록을 2.0.0 릴리스 보고서의 목록과 정렬 후 `diff`하면 **같다**(테스트 이름 기준). 8건: `test_digest_syntax_…`(A, Z)·`test_schema_and_runtime_reject_bootstrap_mode_…`(2건) pwsh 없음 4, `test_migrated_candidate_satisfies_the_json_structural_schema`(position 0, 1) PowerShell 5.1 `Test-Json` 없음 2, `test_f04_checked_in_pass_and_partial_inputs_are_executable` f04 픽스처 CRLF 1, `test_preserved_phase_b_replays_read_only_through_21` M6 재생 증거 미설정 1. 소요 797초.
- 스테이징 diff에 사용자 이름·메일·`C:\Users` 0건(커밋마다 grep).

## 버전·기록

- `VERSION`·스킬 `VERSION` 2.0.1, `tests/test_skill_package.py` 2곳, README 4곳, `PROGRAM_ARCHITECTURE.md` 표·기준선·이력·트리, `CHANGELOG.md` `## 2.0.1 — 후보 (미게시)`.
- [`install_2_0_1.py`](install_2_0_1.py): `install_2_0_0.py`를 본으로 BASE `89cb012`, TIP의 스킬 VERSION 2.0.1 확인, 영수증 `tip_compared`가 `89cb012`로 시작하는지 확인(현재 영수증은 `89cb012138eb…`로 일치). 바뀐 스킬 파일 4개(`VERSION`, `references/first-plan-guide.md`, `scripts/new_records.py`, `scripts/revision_v2.py`)는 합성 문서가 아니므로 patch 단계는 "unchanged since base"로 지나갑니다. 네 파일 모두 영수증에서 origin `branch_tip`이고 해시가 `89cb012`의 blob과 같습니다(확인함). **실행하지 않았습니다**(`-O` 차단 줄만 `python -O … x`로 확인, git·영수증 읽기 전에 끝남).

## 고치지 않은 것

- `preflight_state_candidate.py`로 손으로 쓴 후보를 검사할 때 `discovery_*` finding의 pointer가 `null`인 것((b)). 이 경로는 원래 손 편집 후보용이라 이번 결함의 길이 아닙니다.
- SKILL.md와 `workflow-v0.2.0.md` 본문(지시대로 손대지 않음). `build_discovery_baseline.py`는 여전히 SKILL.md에 나오지 않지만, 이제 첫 기획에 필요하지 않습니다.
- 연동 D1·D3~D9·D11·D13은 JOENESS·JOEDESIGN 몫이거나 환경 문제라 이 저장소에서 다루지 않았습니다.
- 대화형 콘솔 붙여 넣기 동작, Codex의 중복 스킬 판정, 실제 업그레이드(새 커밋을 받는 경우)는 시험하지 않았습니다.

## 커밋

- `3c81a47` fix: first plan reaches READY_FOR_REVIEW from the empty template (코드+테스트+guide)
- `db1f877` docs: QUICKSTART and README install fixes (문서)
- 이 보고를 담은 커밋: release-prep 2.0.1 candidate (버전·기록)

`git diff --stat v2.0.0 HEAD -- skills/joewrks-product-definition`: `VERSION`, `references/first-plan-guide.md`, `scripts/new_records.py`, `scripts/revision_v2.py` 4개 파일, 17줄 추가·4줄 삭제.
