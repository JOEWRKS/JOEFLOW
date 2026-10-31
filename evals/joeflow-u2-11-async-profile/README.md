# U2-11 ASYNC 로컬 실행 프로필 — 오목 rev 39 측정 (2026-10-31)

`python -B measure.py D:/JOEWRKS/.claude-worktrees/AI-Gomoku/product-definition/ai-coach/state.json` (rev 39, 승인본, 커밋 `9c403e1`). 결과는 `result.txt`.

- 오목이 손으로 N/A로 둔 ASYNC 축 4개(duplicate_execution·idempotency·polling·reconciliation)는 `ASYNC.execution = LOCAL_PURE`가 암시하는 4축과 정확히 같다.
- 승인본에 선언만 더하면 검증 오류 0, definition digest·Manifest digest 그대로(승인 유효).
- 선언 뒤 4칸을 빼면 커버리지 오류 없음(남는 오류는 revision을 열지 않고 상태를 바꾼 데서 오는 `semantic_change_without_revision_increment`·승인 관련뿐). 펼친 보기에는 `inherited_from: profile:ASYNC.LOCAL_PURE` 꼬리표 4개.
- 효과: ASYNC 표면당 4칸(근거·사유 포함). 계획대로 작다.
