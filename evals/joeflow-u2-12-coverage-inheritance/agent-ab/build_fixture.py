# Builds the A/B fixture: AI-Gomoku rev 39 + a user decision to bring the post-game review
# screen into the definition (rev 40, OPEN, records only, no coverage rows for REQ-005/SCR-003).
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skill-B/skills/joewrks-product-definition"
FX = ROOT / "fixture/product-definition/ai-coach"
STATE = FX / "state.json"
PATCH = FX / "rev40-patch.json"
mat = {"outcome_divergence": "HIGH", "fan_out": "MULTI_FLOW", "user_visible": True, "reversibility": "REVERSIBLE",
       "risk_flags": {k: False for k in ("security","privacy","money","legal_or_policy","destructive","data_loss","external_commitment")},
       "classification": "MATERIAL"}
cur = lambda **kw: {"status": "CURRENT", **kw}
patch = {
 "evidence": [{"id": "EVD-040", "status": "CURRENT", "source_kind": "USER_CONFIRMED_INTENT",
   "locator": "이 세션 사용자 채팅(2026-10-31, rev 39 게시 뒤)",
   "claim": "종료 후 복기를 기획에 넣자. 복기 화면에서 이전 수·다음 수로 국면을 옮기고 수순 목록에서 아무 수로 바로 가며, 각 국면마다 그때의 엔진 추정 승률과 추천 자리(최대 10곳 점선)를 다시 계산해 보인다. 복기 중에는 착수할 수 없고, '종료 판으로'로 끝난 판에 돌아오거나 '새 게임'으로 확인 뒤 시작 화면에 간다. 저장·내보내기·분기 대국은 넣지 않는다.",
   "confidence": "DIRECT", "authority_classes": ["INTENT"], "observed_version": None, "content_hash": None}],
 "objects": {
  "requirements": [cur(id="REQ-005", statement="대국이 끝나면 '대국 복기'로 복기 화면에 들어가 0수(빈 판)부터 마지막 수까지 국면을 이전 수·다음 수 버튼(키보드 ←·→ 동일)으로 옮기거나 수순 목록에서 아무 수를 눌러 바로 간다. 국면마다 그때의 사람 차례 기준 엔진 추정 승률과 추천 자리(최대 10곳 점선, 강제패 자리 제외)를 다시 계산해 보이고, 계산이 끝날 때까지 '계산 중'을 보인다. 실제 대국 결과(승·패·무, 총 수)는 표시 중인 수와 구별해 늘 보인다. 복기 중에는 착수할 수 없다. '종료 판으로'를 누르면 끝난 판으로 돌아가고, '새 게임'은 확인 뒤 시작 화면 선택으로 돌아간다. 저장·내보내기·분기 대국은 없다.",
                       scope="종료 후 복기 화면", ui_required=True, materiality=mat)],
  "screens": [cur(id="SCR-003", purpose="복기 화면: 끝난 대국의 수순을 앞뒤로 옮기며 각 국면의 엔진 추정 승률·추천 자리를 다시 본다",
                  requirement_refs=["REQ-005", "REQ-003"],
                  interaction_mode="이전 수·다음 수 버튼(키보드 ←·→ 동일), 수순 목록에서 수 누르기=그 국면으로, 판 누름=무시(착수 없음), '종료 판으로'·'새 게임'(확인 창) 버튼",
                  major_actions=["step-move", "jump-to-move", "back-to-final", "new-game-from-review"])],
  "flows": [cur(id="FLOW-005", goal_refs=["GOAL-001"], entry="대국이 끝난 뒤 결과 배너에서 '대국 복기'를 고른다",
                preconditions=["대국이 끝났다(승·패·무)", "엔진을 불러왔다"],
                paths=["0수(빈 판)에서 시작하고 수순 목록과 실제 결과(승·패·무, 총 수)를 보인다",
                       "이전 수·다음 수(키보드 ←·→)로 한 수씩 옮기고, 수순 목록에서 수를 누르면 그 국면으로 바로 간다",
                       "국면이 바뀌면 그때의 사람 차례 기준 엔진 계산(0.3초)이 끝날 때까지 '계산 중'을 보이고, 끝나면 승률과 추천 자리 최대 10곳을 점선으로 보인다",
                       "계산 중 국면을 다시 옮기면 앞 계산을 버리고 새 국면만 계산한다",
                       "판을 눌러도 돌을 놓지 않는다"],
                outcomes=["'종료 판으로'를 누르면 마지막 국면과 결과 배너로 돌아간다",
                          "'새 게임'을 누르면 확인 뒤 복기와 대국 이력을 버리고 시작 화면 선택으로 돌아간다"])],
  "states": [cur(id="STATE-011", owner_refs=["REQ-005", "REQ-003"], state_name="복기 국면 계산 중",
                 conditions=["복기 화면에서 국면을 옮긴 뒤 엔진 계산(0.3초)이 끝날 때까지", "승률과 추천 자리를 숨기고 '계산 중'을 보인다"]),
             cur(id="STATE-012", owner_refs=["REQ-005"], state_name="복기 0수",
                 conditions=["복기 화면에 들어간 직후", "빈 판·수순 목록·실제 결과만 보이고 승률·추천은 첫 수를 둘 사람 차례 기준으로 계산한다"])],
  "rules": [cur(id="RULE-045", statement="복기 화면은 표시 전용이다: 판을 눌러도 착수하지 않고, 실제 대국 상태(종료, 결과, 총 수)는 바뀌지 않는다. 국면을 옮길 때마다 그 국면의 사람 차례 기준으로 엔진이 승률과 추천 자리를 다시 계산하며(0.3초), 계산 중 국면이 또 바뀌면 앞 결과는 버린다. 저장·내보내기·분기 대국은 없다.", applies_to=["REQ-005"]),
            cur(id="RULE-046", statement="복기 이동 조작: 이전 수·다음 수 버튼과 키보드 ←·→는 같고, 0수에서 이전 수·마지막 수에서 다음 수는 눌리지 않는다. 수순 목록의 수를 누르면 그 국면으로 바로 간다. 표시 중인 수 번호와 실제 결과(승·패·무, 총 수)는 늘 함께 보인다. '종료 판으로'는 마지막 국면과 결과 배너로 돌아가고, '새 게임'은 RULE-042의 확인 창을 거쳐 시작 화면 선택으로 돌아간다.", applies_to=["REQ-005"])],
  "acceptance_criteria": [cur(id="AC-044", requirement_refs=["REQ-005"], assertion="끝난 46수 대국에서 '대국 복기'를 누르면 0수 빈 판과 수순 목록 46개, 결과 '흑 승 · 46수'가 보이고, 다음 수를 23번 누르면 23수 국면과 그때 사람 차례 기준 승률·추천 점선(최대 10곳)이 '계산 중' 뒤에 보이며, 수순 목록 40수를 누르면 바로 40수 국면이 보이고, 판을 눌러도 돌이 늘지 않는다."),
                          cur(id="AC-045", requirement_refs=["REQ-005"], assertion="복기 중 '종료 판으로'를 누르면 46수 국면과 결과 배너가 다시 보이고 되돌리기가 전과 같이 동작하며, '새 게임'을 누르면 확인 창이 뜨고 확인하면 시작 화면 선택(이전 선택 미표시)으로 간다. 0수에서 이전 수, 46수에서 다음 수 버튼은 눌리지 않는다.")],
 },
 "surfaces": [{"id": "SURF-004", "kind": "FEATURE_AREA", "name": "종료 후 복기 화면: 수순 이동과 국면별 승률·추천 재표시", "status": "IN_SCOPE",
               "materiality": mat, "evidence_refs": ["EVD-040"], "authority_refs": ["REQ-005"], "unknown_refs": [], "decision_refs": ["DEC-108"],
               "contradiction_refs": [], "rationale": "사용자 지시(EVD-040)로 범위에 넣었다. REQ-005가 권위다.", "intent_classification": None}],
}
PATCH.write_text(json.dumps(patch, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
def run(*args):
    r = subprocess.run([sys.executable, "-B", *args], capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-3000:], r.stderr[-3000:]); return r.returncode
run(SKILL / "scripts/new_records.py", "--patch", PATCH, "user-decision", "--unknown", "UNK-108",
    "--question", "종료 후 복기를 기획에 넣고, 복기 중 각 국면의 엔진 추정 승률·추천 자리를 다시 보일까요?",
    "--why", "복기는 구현돼 있지만 기획 밖이고(기존 기능), 국면별 승률·추천 재표시는 새 동작이다.",
    "--category", "CORE_FLOW", "--option", "A=복기 화면을 기획에 넣고 국면마다 승률·추천을 다시 계산해 보인다|복기 중 엔진 계산이 돈다(0.3초)",
    "--option", "B=복기는 기획 밖 기존 기능으로 둔다|승률·추천 재표시는 없다",
    "--affects", "SURF-004", "--evidence", "EVD-040", "--surface", "SURF-004",
    "--decision", "DEC-108", "--statement", "종료 후 복기 화면을 기획에 넣는다(REQ-005). 이전 수·다음 수·수순 목록 이동, 국면마다 엔진 추정 승률·추천 자리 재계산 표시, 표시 전용(착수 없음), '종료 판으로'와 '새 게임'(확인). 저장·내보내기·분기 대국은 없다.",
    "--summary", "사용자 지시 \"종료 후 복기를 기획에 넣자 … 각 국면마다 그때의 엔진 추정 승률과 추천 자리를 다시 계산해 보인다 … 저장·내보내기·분기 대국은 넣지 않는다\".",
    "--decision-affects", "REQ-005")
print("== open_revision OPEN")
rc = run(SKILL / "scripts/open_revision.py", STATE, "--patch", PATCH, "--status", "OPEN", "--write")
print("rc", rc)
