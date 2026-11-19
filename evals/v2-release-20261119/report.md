# JOEFLOW 2.0.0 후보 — 준비 기록

작성 2026-11-19 · 기준 `v1.7.3`(`ddf5c7e`) · 입력 [사전 조사](../v2-survey-20261119/report.md) · push·태그·Release·설치 없음.

## 결론

1. **게이트 통과.** `git diff --stat v1.7.3 HEAD -- skills/joewrks-product-definition`은 `VERSION` 한 파일(`1.7.3` → `2.0.0`)뿐이다. 스킬의 나머지 200개 파일은 1.7.3과 바이트가 같다.
2. **테스트 실패 목록이 1.7.3과 같다.** 최종 트리 1,264개 중 실패 3·오류 5·건너뜀 1이고, `v1.7.3` 태그를 임시 worktree에서 같은 명령으로 돌린 결과(1,264개, 3·5·1)와 실패·오류 목록이 줄 단위로 같다(`diff` 일치). `test_skill_package`·`test_friction_170`은 통과한다.
3. 정리: 삭제 1, 보관 이동 16, 가림 9곳(7개 파일). 작업 트리의 사용자 이름은 13회(10개 파일) → 4회(3개 파일)로 줄었다. 남은 4회는 테스트·`.gitattributes`가 바이트를 고정한 파일 안에 있다.
4. 문서: `SECURITY.md`와 `docs/QUICKSTART.md`를 새로 썼다. README는 350줄에서 147줄로 줄였다(42%). 테스트 문구는 하나도 바꾸지 않았고 버전 숫자 2곳만 바꿨다.

## 게이트

| 검사 | 결과 |
| --- | --- |
| 스킬 폴더 diff (v1.7.3 → HEAD) | `VERSION` 1개 파일, 1줄 |
| `test_skill_package`, `test_friction_170` (+ `test_semantic_v012`, `test_v2_installed_workflow`) | 57/57 통과 |
| 전체 `python -B -m unittest discover -s tests` | 1,264개, 실패 3·오류 5·건너뜀 1 (977초). `v1.7.3` 태그: 1,264개, 3·5·1 (948초). 2.0 작업 전 HEAD: 1,264개, 3·5·1. 세 목록 `diff` 일치 |
| `git status` | 커밋 뒤 깨끗함 |

실패·오류 8건(1.7.3 보고서가 적은 환경 원인 8건과 같은 테스트):

```text
ERROR: test_f04_checked_in_pass_and_partial_inputs_are_executable
ERROR: test_digest_syntax_is_enforced_by_runtime_schema_and_regeneration_cli (invalid_digest='Z')
ERROR: test_digest_syntax_is_enforced_by_runtime_schema_and_regeneration_cli (invalid_digest='A')
ERROR: test_schema_and_runtime_reject_bootstrap_mode_classification_mismatches (bootstrap_mode='EXISTING_PRODUCT_RECONCILIATION')
ERROR: test_schema_and_runtime_reject_bootstrap_mode_classification_mismatches (bootstrap_mode='NEW_PRODUCT')
FAIL: test_preserved_phase_b_replays_read_only_through_21
FAIL: test_migrated_candidate_satisfies_the_json_structural_schema (position=0)
FAIL: test_migrated_candidate_satisfies_the_json_structural_schema (position=1)
```

## 정리 (A)

| 항목 | 수 | 내용 |
| --- | ---: | --- |
| 삭제 | 1 | `.superpowers/sdd/2026-08-30-core-semantic-closure-v2-m6-integration-adoption/continuation-task-a-report.md` |
| 보관 이동 | 16 | `docs/superpowers/plans/` 13개, `evals/v0.1.*-results.md` 3개 → `evals/archive/2026-11-19-unreferenced/` 아래 원래 상대 경로. 이동 전 파일 이름·확장자 뺀 이름으로 다시 검색해 참조 0건 확인 |
| 이동하지 않음 | — | 고정 경로 전부, 무참조 분석 스크립트 4개(실행 폴더와 함께 둠), 참조가 있는 plans 7개 |
| 가림 | 9곳 / 7개 파일 | plans 3개(이동한 위치에서), `behavioral-v0.2/transcripts/eval-0{1,2,3}-control.md` 5곳, `ISOLATION_CAPABILITY_AUDIT.md:97` 1곳. `C:/Users/<user>/` → `~/`, `C:\Users\<user>\` → `~\` |
| 가리지 않음 | 4곳 / 3개 파일 | `semantic-review-v0.4.3` tree 해시 고정 파일 2개, `focused-red.log` 2곳(`.gitattributes` 바이트 고정) |

이동한 self-review plan 5개의 "Applies to" 줄은 원래 자리에 남은 plan을 저장소 경로로 가리키므로 그대로 맞다.

## 문서 (B, C)

- `SECURITY.md`: 이 저장소에는 루트 파일 이름을 검사하는 테스트가 없다(`tests/`에서 `SECURITY`·`QUICKSTART` 0건).
- README 350줄 → 147줄. 12개 절 제목, 언어 링크·앵커, `Program version: **\`v2.0.0\`**`, 역할 문구 6개, workflow·reentry 링크, `# JOEFLOW` 1회, `validate_state.py`·`validate_closure.py`를 남겼다. "No dedicated installer …" 문장은 "package-manager 명령은 없고, Claude Code·개인 오버레이 설치기·업그레이드·제거는 Quickstart에"로 고쳤다. 한국어 절은 설치 블록과 예시 요청을 반복하지 않고 영어 절을 가리킨다.
- **테스트 문구 변경: 없음.** 바꾼 것은 `tests/test_skill_package.py`의 버전 하드코딩 2곳(`"1.7.3"` → `"2.0.0"`, `Program version: **\`v1.7.3\`**` → `v2.0.0`)뿐이다.
- `PROGRAM_ARCHITECTURE.md`: 릴리스 표·기준선 줄을 `v2.0.0`으로, 이력에 v2.0.0 줄 추가, Repository mapping을 지금 트리(`VERSION`, `agents/`, `reviewer_runner/`, `downstream_v21` 현행 표기, 고정 경로, `archive/`)에 맞췄다.

### Quickstart에 남은 빈틈

- Claude Code 연결(junction)은 이 세션에서 실행해 보지 않았다. 명령은 PowerShell 5.1 문법으로 썼다.
- Codex 일반 복사 설치에는 업그레이드 스크립트가 없다. 백업 후 다시 복사하라고만 적었다.
- 제거 스크립트는 없다. 폴더 삭제로 안내했다.
- Claude Code에서 스킬을 부르는 정확한 표기는 확인하지 않았다(스킬 이름으로 부른다고만 적음).

## 버전과 설치기

- `2.0.0`: 루트 `VERSION`, 스킬 `VERSION`, README(요약·한국어 머리·한계 2곳), PROGRAM_ARCHITECTURE(표·기준선·이력), `tests/test_skill_package.py` 2곳, CHANGELOG `## 2.0.0 — 후보 (미게시)`.
- `install_2_0_0.py`: `install_1_7_3.py`를 복사해 BASE `ddf5c7e`, 스킬 `VERSION == 2.0.0` 확인, 영수증이 1.7.3 설치 상태인지 확인, 백업 이름·영수증 키 `pycache_drift_before_2_0_0`만 바꿨다. 합성 대상(`SKILL.md`, `workflow-v0.2.0.md`)·합성 기록 3개·로컬 오버레이 2개 처리와 영수증의 `~` 표기는 그대로다. 예상 동작: 복사 1개(`VERSION`), 합성 문서는 "unchanged since base". **실행하지 않았다.** `py_compile`만 통과했다. 현재 영수증의 `tip_compared`는 `ddf5c7e…`(1.7.3)라 사전 조건은 맞는다.

## 커밋

- `0c20708` hygiene: 삭제 1, 보관 이동 16, 홈 경로 가림
- `585e0ba` docs: SECURITY.md
- (이 커밋) docs+version+installer: QUICKSTART, README 축약, PROGRAM_ARCHITECTURE, VERSION 2.0.0, 테스트 버전 2곳, CHANGELOG, install_2_0_0.py, 이 보고서

## 확인된 것

- 스킬 폴더 diff는 `VERSION` 한 파일이다.
- 전체 테스트의 실패·오류 목록이 `v1.7.3` 태그를 따로 돌린 결과와 같다(위 표).
- 무참조 판정을 이동 전에 다시 했다(전체 이름과 확장자 뺀 이름 모두 0건).
- 커밋마다 staged 텍스트에서 사용자 이름, gmail 주소, `C:/Users`, `C:\Users`, AppData를 검색했다. 걸린 것은 이미 가린 `~\AppData\Local\Temp`와 SECURITY.md의 검색어 이름뿐이다.

## 확인되지 않은 것

- `install_2_0_0.py`의 실제 동작(실행 금지). 개인 Codex 설치본의 현재 상태도 열어 보지 않았다.
- Quickstart의 Claude Code junction 명령, 업그레이드·제거 절차를 실제로 해 보지 않았다.
- GitHub의 비공개 취약점 보고 기능이 켜져 있는지. SECURITY.md는 꺼져 있을 때의 대안도 적었다.
- 원격 브랜치에 남은 식별자 수, 원격 저장소 공개 여부.

## 세션이 대신 내린 결정

- 1.7.3 보고서는 1,263개라고 적었지만(후보 커밋 기준), 태그에서 다시 돌리면 1,264개다. 비교 기준으로는 태그를 다시 돌린 결과를 썼다.
- 첫 커밋(정리) 전의 전체 테스트는 따로 돌리지 않았다. 정리 변경이 이미 작업 트리에 있는 상태에서 돌린 HEAD 기준 실행과, 마지막 전체 실행으로 갈음했다. 옮기거나 고친 파일은 어떤 테스트도 읽지 않는다.
- README 한국어 절은 설치 블록과 예시 요청을 두 번 싣지 않았다(테스트 요구 문구는 모두 남김).
- 이동한 self-review plan의 "Applies to" 경로는 고치지 않았다(가리킴 대상이 원래 자리에 있음).
- CHANGELOG 2.0.0 절에는 행동 시험을 하지 않은 이유(행동 문장 변경 없음)를 적었다.
