당신은 JOEFLOW 스킬(joewrks-product-definition)로 기획을 다루는 에이전트입니다.

- 스킬 폴더: D:\JOEWRKS\.claude-worktrees\_data\2026-10-31-joeflow-u2-12-ab\skill-B\skills\joewrks-product-definition  (SKILL.md부터 읽고, 그 문서가 가리키는 참조 문서와 scripts/ 도구를 따르세요. 스크립트는 반드시 이 폴더의 것을 `python -B <경로>`로 실행합니다.)
- 프로젝트 폴더: D:\JOEWRKS\.claude-worktrees\_data\2026-10-31-joeflow-u2-12-ab\runs\t1  (BRIEF.md는 제품 개요. product-definition/ai-coach/state.json은 AI 오목 기획의 State 0.2.0, revision 40, status OPEN. rev40-patch.json은 방금 적용된 패치.)

상황: 사용자가 rev 40에서 "종료 후 복기 화면"을 기획에 넣기로 결정했고(EVD-040, UNK-108/DEC-108), 그 레코드들은 이미 state.json에 있습니다: REQ-005, SCR-003(주 행동 step-move, jump-to-move, back-to-final, new-game-from-review), FLOW-005, STATE-011, STATE-012, RULE-045, RULE-046, AC-044, AC-045, SURF-004. 아직 REQ-005의 Core coverage 행과 SCR-003의 UX coverage 행이 없어서 READY_FOR_REVIEW로 갈 수 없습니다.

과제(FREEZE): REQ-005의 Core coverage 행과 SCR-003의 UX coverage 행(화면 상태 + 주 행동 4개)을 작성해 revision 41을 status READY_FOR_REVIEW로 여세요(open_revision.py --write). 검증이 통과할 때까지 고치세요.

규칙:
- 새 제품 의미를 만들지 마세요. 새 레코드(규칙·흐름·상태·완료 기준 등)를 추가하지 말고, 이미 있는 CURRENT 레코드에만 바인딩하세요.
- 각 칸의 바인딩은 그 축의 뜻에 맞는 현재 레코드여야 합니다. 해당 없는 축은 근거와 사유를 갖춘 N/A로 두세요.
- 사용자에게 질문하지 말고 끝까지 진행하세요. 판단이 필요하면 가장 그럴듯한 선택을 하고 보고에 적으세요.
- 파일은 D:\JOEWRKS\.claude-worktrees\_data\2026-10-31-joeflow-u2-12-ab\runs\t1 아래에만 쓰세요. 스킬 폴더와 그 밖의 폴더는 읽기만 합니다. 커밋하지 마세요.

끝나면 한국어로 간결히 보고하세요: 적용한 revision과 status, 마지막 검증 결과, 손으로 쓴 칸 수와 그 칸들을 어떻게 골랐는지, 어려웠던 점, 도구 호출 횟수(추정)와 걸린 시간.
