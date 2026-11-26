#!/usr/bin/env python3
"""JOEFLOW 2.0.2 fresh-project walk-through, every command and its output saved.

new state from the 2.0.2 template -> topology questions answered (MONEY on, the rest off)
-> topology-on for MONEY -> axis questions rewritten -> grouped questions -> resolve
--accept-recommended -> requirement --from-decisions -> FREEZE (Core row) ->
READY_FOR_REVIEW -> Approval Manifest.

Usage: python run_walkthrough.py SKILL_DIR OUT_DIR   (writes OUT_DIR/walkthrough.md and the files)
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

SKILL, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SCRIPTS = SKILL / "scripts"
OUT.mkdir(parents=True, exist_ok=True)
for name in ("state.json", "rev2-patch.json", "rev3-patch.json", "rev4-patch.json"):
    (OUT / name).unlink(missing_ok=True)
LOG = (OUT / "walkthrough.md").open("w", encoding="utf-8", newline="\n")
STEP = [0]


def run(script, *args, note=""):
    STEP[0] += 1
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args)], cwd=OUT,
                            capture_output=True, stdin=subprocess.DEVNULL, env=env)
    out = result.stdout.decode("utf-8").strip()
    LOG.write(f"\n### {STEP[0]}. {note}\n\n```\npython {script} {' '.join(shlex.quote(str(a)) for a in args)}\n```\n\n"
              f"exit {result.returncode}\n\n```\n{out}\n```\n")
    if result.returncode != 0:
        LOG.write(f"\nstderr:\n```\n{result.stderr.decode('utf-8')}\n```\n")
        LOG.close()
        raise SystemExit(f"step {STEP[0]} failed: {script} {args}\n{out}")
    return out


def nr(patch, *args, note=""):
    return run("new_records.py", "--state", "state.json", "--patch", patch, *args, note=note)


LOG.write("# JOEFLOW 2.0.2 walk-through: a fresh project\n\nEvery command runs from this folder; outputs are verbatim.\n")
shutil.copyfile(SKILL / "templates" / "state-v0.2.0.example.json", OUT / "state.json")
run("validate_state.py", "state.json", note="the 2.0.2 template validates: six domains OPEN, one classification question each")
run("next_product_question.py", "state.json", "--grouped", "--markdown", note="the template's topology questions, grouped")

WORDS = "결제는 받는다. 계정, 파일 올리기, 역할 구분, 되돌리기 어려운 삭제, 나중에 오는 결과는 없다."
nr("rev2-patch.json", "evidence", "--id", "EVD-001", "--source-kind", "USER_CONFIRMED_INTENT", "--class", "INTENT",
   "--locator", "chat (walk-through brief)", "--claim", "비회원 한 명이 한 품목을 바로 결제하는 단일 상품 판매 페이지.",
   note="the brief as evidence")
answers = {"UNK-902": "OPT-MONEY-ON", "UNK-901": "OPT-AUTH-OFF", "UNK-903": "OPT-UPLOAD-OFF",
           "UNK-904": "OPT-ASYNC-OFF", "UNK-905": "OPT-PERM-OFF", "UNK-906": "OPT-DESTR-OFF"}
for unknown, option in answers.items():
    nr("rev2-patch.json", "resolve", unknown, "--option", option, "--words", WORDS,
       note=f"resolve the topology question {unknown} = {option} (mode derived)")
nr("rev2-patch.json", "topology-on", "DEC-001", "--new-surface", "SURF-001", "--name", "결제",
   note="MONEY on: MONEY_FLOW surface, GRILL-MONEY-1 row with digest, 12 OPEN axis questions")
for decision, domain in (("DEC-002", "AUTH"), ("DEC-003", "FILE_UPLOAD"), ("DEC-004", "ASYNC"),
                         ("DEC-005", "PERMISSION"), ("DEC-006", "DESTRUCTIVE_ACTION")):
    nr("rev2-patch.json", "topology-off", decision, "--rationale", f"사용자 답(DEC-001~006): 이 제품에는 {domain} 동작이 없다.",
       note=f"{domain} off")
run("open_revision.py", "state.json", "--patch", "rev2-patch.json", "--status", "OPEN", "--write", note="rev2 (OPEN)")
run("next_product_question.py", "state.json", "--grouped", "--markdown", note="12 skeleton axis questions, one group")

AXES = {
    "currency": ("KRW 단일 통화", "다른 통화 표시 전환"), "price_authority": ("서버가 주문 시 가격을 다시 계산", "화면 가격을 그대로 사용"),
    "tax": ("부가세 포함가 표시", "부가세 별도 표시"), "discount": ("할인 없음", "쿠폰 입력란"),
    "payment_failure": ("실패 안내와 다시 결제", "주문 자동 취소"), "duplicate_payment": ("주문별 결제 키로 한 번만 승인", "검사 없음"),
    "refund": ("운영자가 전액 환불", "환불 없음"), "partial_refund": ("부분 환불 없음", "품목 단위 부분 환불"),
    "cancellation": ("결제 전에만 취소", "언제든 취소"), "chargeback": ("지급 거절은 이력에 기록", "무시"),
    "settlement": ("정산은 PG 화면에서 확인", "사이트 안 정산 화면"), "receipt": ("영수증 메일", "영수증 없음"),
}
unknowns = {u["origin"]["axis_id"]: u["id"] for u in json.loads((OUT / "state.json").read_text(encoding="utf-8"))["objects"]["unknowns"]
            if u["origin"]["kind"] == "GRILL_PACK_AXIS"}
for axis, (yes, no) in AXES.items():
    run("new_records.py", "--state", "state.json", "--patch", "rev3-patch.json", "--replace", "question", "--unknown", unknowns[axis], "--pack", "GRILL-MONEY-1", "--axis", axis, "--surface", "SURF-001",
       "--question", f"{axis}: {yes}인가, {no}인가?", "--why", f"결제 화면과 주문 기록의 {axis} 동작이 정해진다.",
       "--category", "SECONDARY_BEHAVIOR", "--affects", "SURF-001",
       "--option", f"OPT-A={yes}|{yes}로 구현한다.", "--option", f"OPT-B={no}|{no}로 구현한다.",
       "--materiality", "MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money", "--recommend", "OPT-A", "--reason", "EVD-001",
       "--tradeoff", f"{no}는 이번 범위에서 빠진다.", note=f"rewrite the {axis} skeleton in product terms (same ID)")
run("open_revision.py", "state.json", "--patch", "rev3-patch.json", "--status", "OPEN", "--write", note="rev3 (OPEN): questions ready to ask")
run("next_product_question.py", "state.json", "--grouped", "--markdown", note="the recommendation table shown to the user")
run("next_product_question.py", "state.json", "--grouped", note="the same groups as JSON")

nr("rev4-patch.json", "resolve", "--accept-recommended", "--pack", "GRILL-MONEY-1", "--surface", "SURF-001",
   "--words", "전부 추천대로", note="the user answers the table: all as recommended")
nr("rev4-patch.json", "requirement", "--from-decisions", ",".join(f"DEC-{n:03d}" for n in range(7, 19)), "--surface", "SURF-001",
   "--requirement", "REQ-001", "--ui-required", "false", note="the surface has no open question left: requirement from its decisions")
nr("rev4-patch.json", "edit", "REQ-001", "--set", "/statement",
   "구매자는 KRW 포함가로 한 품목을 결제하고, 서버 재계산 가격과 주문별 결제 키로 한 번만 승인되며, 실패하면 다시 결제한다"
   "(DEC-007~DEC-018).", note="the drafted statement edited into one requirement")
# FREEZE records: 2.0.2 has no RULE/AC/TASK builder (bundle E/F are 2.0.3), so this fragment is authored here.
freeze = json.loads((OUT / "rev4-patch.json").read_text(encoding="utf-8"))
freeze["objects"].update({
    "goals": [{"id": "GOAL-001", "status": "CURRENT", "statement": "구매자가 한 품목을 한 번에 결제한다."}],
    "users": [{"id": "USR-001", "status": "CURRENT", "description": "비회원 구매자.", "actor_kind": "BUYER"}],
    "rules": [{"id": "RULE-001", "status": "CURRENT", "applies_to": ["REQ-001"],
               "statement": "결제 규칙: KRW 포함가, 서버 재계산, 주문별 결제 키 한 번 승인, 실패 시 다시 결제, 결제 전 취소, 운영자 전액 환불, 영수증 메일."}],
    "acceptance_criteria": [{"id": "AC-001", "status": "CURRENT", "requirement_refs": ["REQ-001"],
                             "assertion": "같은 결제 키의 두 번째 승인은 무시되고 주문은 한 번만 결제 완료가 된다."}],
    "tasks": [{"id": "TASK-001", "status": "CURRENT", "implements": ["REQ-001"], "acceptance_refs": ["AC-001"]}],
})
bind = lambda record_id, pointer: {"record_id": record_id, "pointer": pointer}
freeze.setdefault("rows", []).append({"coverage": {"feature_id": "REQ-001", "default_authority": [bind("RULE-001", "/statement")], "cells": {
    "goal": {"status": "COVERED", "bind": [bind("GOAL-001", "/statement"), bind("REQ-001", "/statement")]},
    "happy_path": {"status": "COVERED", "bind": [bind("REQ-001", "/statement")]},
    # the topology answers are the product's boundary (DEC is allowed on the Core boundary axis)
    "boundary": {"status": "COVERED", "bind": [bind("RULE-001", "/statement")] + [bind(f"DEC-00{n}", "/statement") for n in range(1, 7)]},
    "acceptance": {"status": "COVERED", "bind": [bind("AC-001", "/assertion")]}}}})
(OUT / "rev4-patch.json").write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
LOG.write("\n### FREEZE fragment\n\nGOAL-001, USR-001, RULE-001, AC-001, TASK-001 and the REQ-001 Core row (its boundary cell binds the six topology decisions) are added to rev4-patch.json "
          "by hand (no 2.0.2 builder writes RULE/AC/TASK records).\n")
run("open_revision.py", "state.json", "--patch", "rev4-patch.json", "--status", "READY_FOR_REVIEW", "--write", note="rev4 READY_FOR_REVIEW")
run("validate_state.py", "state.json", note="valid")
run("build_approval_manifest.py", "state.json", note="the Approval Manifest to show the user")
LOG.close()
print(json.dumps({"ok": True, "steps": STEP[0]}))
