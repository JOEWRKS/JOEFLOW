# JOEFLOW 2.0.1

2.0.0 게시 뒤 돌린 두 시험(QUICKSTART 실행 시험, JOENESS·JOEFLOW·JOEDESIGN 연동 시험)이 찾은 결함을 고친 판입니다. State 0.2.0, 검증 모듈, 바인딩 계약, 기존 승인, 출력 JSON 모양은 그대로입니다. `SKILL.md`와 `references/workflow-v0.2.0.md` 본문은 바꾸지 않았습니다.

## 바뀐 것

- **새 프로젝트가 READY_FOR_REVIEW에 갑니다.** `open_revision --status READY_FOR_REVIEW`에서 `discovery_baseline`이 `CURRENT`가 아니면 그 자리에서 세웁니다(`build_discovery_baseline.py`와 같은 객체). 빈 템플릿에서 시작하면 `discovery_baseline_gaps`(pointer `null`)에 막혀 state.json을 손으로 고쳐야 하던 문제입니다. `references/first-plan-guide.md`에 그 절차를 적었습니다.
- `new_records.py question`·`user-decision`의 `--evidence`가 선택이 됐습니다. 사용자 의도만 근거인 질문을 `--reason`으로만 기록할 수 있습니다(전에는 필수여서 의도 근거를 넣으면 `EVIDENCE_RESOLVABLE`로 검증에 걸렸음).
- 문서(QUICKSTART·README): 투영 갱신 전에 템플릿 2개를 state.json 옆에 복사해야 함, `--spec`·`--review`는 실행 폴더 기준, 승인 전 `validate_closure` exit 1이 정상, `joeflow-project.json` 실제 위치, 설치·clone 시 버전(태그) 고정, Codex 업그레이드를 기존 clone에서 `fetch`+`checkout` 뒤 복사 부분만(같은 폴더에서 다시 붙여 넣으면 옛 clone으로 조용히 재설치되던 위험), 백업 폴더 위치, PowerShell 5.1 출력 인코딩, 오버레이 설치기 전제.
- 테스트 환경 정리(스킬 변경 없음): pwsh·`Test-Json`이 없는 기계에서 해당 테스트는 skip, f04 픽스처는 `.gitattributes`로 LF 고정. M6 재생 테스트는 계획대로 skip하지 않고 증거 변수가 있어야 통과합니다.

## 확인된 것

- 결함마다 고치기 전 재현했습니다. 새 테스트(`tests/test_first_plan_201.py`)가 빈 템플릿에서 승인 가능 상태까지 스크립트만으로 갑니다.
- `test_skill_package`·`test_friction_170` 통과. 전체 1,267개: M6 증거 변수 없이 실패 1·오류 0·skip 6(2.0.0은 실패 3·오류 5), 변수를 주면 0·0·6(준비 세션 확인).
- 스테이징한 줄에 사용자 이름·메일·`C:` 사용자 폴더 0건.

## 확인되지 않은 것

- 행동 시험 0회. 실제 새 대화(DISCOVER→APPROVE)에서의 첫 기획.
- Codex가 `skills\` 안의 백업 폴더를 중복 스킬로 읽는지.

## 세션이 대신 내린 결정

1. baseline 수립 위치를 `open_revision`(READY_FOR_REVIEW)로 잡았습니다(검수 요청이 "탐색이 끝났다"는 작성자의 주장이므로).
2. M6 재생 테스트는 M5.1 계획("조용히 건너뛰지 말라")을 존중해 skip으로 바꾸지 않았습니다.

기록: [report-201.md](report-201.md), 입력 시험 [report-docs-joeflow.md](report-docs-joeflow.md)·[report-integration.md](report-integration.md). 개인 설치: [install_2_0_1.py](install_2_0_1.py).
