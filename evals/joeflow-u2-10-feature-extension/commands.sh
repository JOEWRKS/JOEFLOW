# Run from the repository root against a copy of AI-Gomoku rev 39 state.json (STATE).
S=skills/joewrks-product-definition/scripts
python -B $S/new_records.py --patch patch.json evidence --id EVD-041 --source-kind OBSERVED_RUNTIME --class BEHAVIORAL \
  --locator "omok-gosu rev 39 게시본(2026-10-31), tests/e2e·work/release" \
  --claim "되돌리기·새 게임·시작 화면·판 위 표시는 e2e·release 검사가 단정하는 대로 동작한다"
python -B $S/new_records.py --patch patch.json baseline --requirement REQ-006 --rule RULE-047 --acceptance AC-046 \
  --surface SURF-005 --goal GOAL-001 --evidence EVD-041 --task TASK-004 \
  --check "기존 e2e·release 검사(RPL1~3, REL-08 포함)가 수정 없이 통과한다" \
  --behavior "되돌리기는 직전 국면으로 돌아간다" --behavior "새 게임은 확인 창 뒤에 시작 화면 선택으로 돌아간다" \
  --behavior "시작 화면의 모드·색·강도 선택과 승률 막대는 그대로다" --behavior "대국 화면의 점선 후보·금수 표시·말풍선은 그대로다"
python -B $S/open_revision.py STATE --patch patch.json --status READY_FOR_REVIEW --write
python -B $S/build_approval_manifest.py STATE
