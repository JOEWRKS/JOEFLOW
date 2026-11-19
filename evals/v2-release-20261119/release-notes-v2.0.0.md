# JOEFLOW 2.0.0

저장소 정리, 보안 검토 문서, 빠른 시작 문서를 더한 판입니다. **스킬 동작은 1.7.3과 같습니다.** `skills/joewrks-product-definition`에서 바뀐 파일은 `VERSION` 하나이고 나머지 200개 파일은 바이트가 같습니다. State 0.2.0, 검증 모듈, 바인딩 계약, 기존 승인, 출력 JSON 모양은 그대로입니다. 행동을 바꾸는 문장 변경이 없어 행동 시험은 하지 않았습니다.

## 바뀐 것

- **정리**: 참조 0건인 `.superpowers/…/continuation-task-a-report.md` 1개 삭제. 참조 0건인 `docs/superpowers/plans/*` 13개와 `evals/v0.1.*-results.md` 3개를 `evals/archive/2026-11-19-unreferenced/`로 이동. 테스트가 고정하지 않은 7개 파일에서 홈 경로 9곳을 `~`로 가림. git 이력은 다시 쓰지 않음.
- **[SECURITY.md](../../SECURITY.md)**: 점검 항목과 수치, 남은 식별자(테스트·`.gitattributes`가 바이트를 고정한 3개 파일의 4곳, 이력, 커밋 메타데이터), 스크립트 신뢰 경계, 의존성, 보고 방법.
- **[docs/QUICKSTART.md](../../docs/QUICKSTART.md)**: Codex 일반 복사, 개인용 오버레이 설치기, Claude Code(clone + junction), 첫 실행, 검증, 투영 갱신·검사, 버전 고정, 업그레이드, 제거.
- README 350줄 → 147줄. `PROGRAM_ARCHITECTURE.md` Repository mapping을 지금 트리에 맞춤. 루트·스킬 `VERSION` 2.0.0.

## 확인된 것

- `git diff --stat v1.7.3 -- skills/joewrks-product-definition` = `VERSION` 1개 파일.
- `test_skill_package`·`test_friction_170`·`test_semantic_v012`·`test_v2_installed_workflow` 57/57.
- 전체 스위트 1,264개 중 실패 3·오류 5·건너뜀 1. `v1.7.3` 태그를 같은 명령으로 다시 돌린 결과와 실패·오류 목록이 줄 단위로 같습니다. 8건은 모두 환경 원인입니다: PowerShell 7(`pwsh.exe`) 미설치 4, Windows PowerShell 5.1에 `Test-Json` 없음 2, f04 픽스처 CRLF 체크아웃 해시 불일치 1, M6 재생 증거 미설정 1.
- 스테이징한 줄에 사용자 이름·메일·`C:` 사용자 폴더 0건.

## 확인되지 않은 것

- Claude Code 쪽 설치(clone + junction)에서 스킬 발견·호출. 실제 Codex 실행.
- 마크다운 링크의 GitHub 렌더링(로컬에서 경로 존재만 확인).
- 남은 식별자 4곳과 git 이력(커밋 작성자 메일 포함)은 그대로입니다. 자세한 것은 SECURITY.md.

## 세션이 대신 내린 결정

1. 스킬 본문(SKILL.md·references·scripts·templates)은 한 글자도 바꾸지 않았습니다(성능 누락 위험 제거).
2. 테스트 문구는 바꾸지 않고 버전 숫자 2곳만 바꿨습니다.
3. f04 픽스처의 줄끝 고정(`.gitattributes`)은 그 파일이 테스트에 고정돼 있어 2.0 범위에서 뺐습니다.

기록: [evals/v2-release-20261119/report.md](report.md), [2.0 사전 조사](../v2-survey-20261119/report.md). 개인 설치: [install_2_0_0.py](install_2_0_0.py).
