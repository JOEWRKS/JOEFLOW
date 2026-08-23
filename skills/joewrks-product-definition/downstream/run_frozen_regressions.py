"""Execute pinned Replication A/B runtimes and evaluate them in the Python core."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .adapter_runtime import build_request, run_file_jsonl_adapter
from .contracts import compile_contract, is_full_handoff_contract, materialize_definition
from .product_adapters import replication_a_definition, replication_b_definition
from .verifier import verify_execution, verify_lifecycle_transition


A_COMMIT = "9408434e640b9cf0bf6afaadd8f9d1f5f52e8943"
B_COMMIT = "eecebc28701006dd2c7be4045a22542e34719705"
A_IMPLEMENTATION_PATH = "evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation"
B_IMPLEMENTATION_PATH = "codex-implementation"


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(arguments)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for record in records
        ),
        encoding="utf-8",
        newline="\n",
    )


def _request_factory(
    bundle: dict[str, Any], adapter: dict[str, str], frozen: dict[str, str]
):
    authority = {
        "approved_revision": bundle["source_authority"]["approved_revision"],
        "approved_digest": bundle["source_authority"]["approved_digest"],
    }

    def request(
        sequence_id: str,
        test_id: str,
        command: dict[str, Any],
        *,
        setup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return build_request(
            sequence_id=sequence_id,
            test_id=test_id,
            product_slug=bundle["source_authority"]["product_slug"],
            authority=authority,
            contract_hash=bundle["contract_hash"],
            adapter=adapter,
            frozen_source=frozen,
            command=command,
            setup=setup,
        )

    return request


def _command(
    command_type: str,
    actor_id: str,
    target_id: str,
    expected_version: int,
    idempotency_key: str,
    command_input: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": command_type,
        "actorId": actor_id,
        "targetId": target_id,
        "expectedVersion": expected_version,
        "idempotencyKey": idempotency_key,
        "input": command_input,
    }


def _actions(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {action["action_id"]: action for action in bundle["actions"]}


def _assert_frozen_sources(a_root: Path, b_worktree: Path) -> tuple[Path, Path, str, str]:
    if _git(a_root, "rev-parse", "HEAD") != A_COMMIT:
        raise RuntimeError("Replication A worktree is not at the pinned commit")
    a_source = a_root / Path(A_IMPLEMENTATION_PATH)
    b_source = b_worktree / B_IMPLEMENTATION_PATH
    a_tree = _git(a_root, "rev-parse", f"{A_COMMIT}:{A_IMPLEMENTATION_PATH}")
    b_tree = _git(b_worktree, "rev-parse", f"{B_COMMIT}:{B_IMPLEMENTATION_PATH}")
    current_b_tree = _git(b_worktree, "rev-parse", f"HEAD:{B_IMPLEMENTATION_PATH}")
    if b_tree != current_b_tree:
        raise RuntimeError("checked-out Replication B source differs from frozen eecebc tree")
    if _git(a_root, "status", "--short") or _git(b_worktree, "status", "--short"):
        raise RuntimeError("frozen runtime worktree must be clean")
    return a_source, b_source, a_tree, b_tree


def _evaluate(
    action_map: dict[str, dict[str, Any]],
    action_id: str,
    record: dict[str, Any],
    expected_result: str | None = None,
) -> dict[str, Any]:
    return verify_execution(
        action_map[action_id], record, expected_result=expected_result
    )

def execute_frozen_regressions(
    *, a_root: Path, b_worktree: Path, output_dir: Path
) -> dict[str, Any]:
    a_root = a_root.resolve()
    b_worktree = b_worktree.resolve()
    output_dir = output_dir.resolve()
    a_source, b_source, a_tree, b_tree = _assert_frozen_sources(a_root, b_worktree)
    a_state = _read_json(a_root / "product-definition" / "studio-booking-dogfood" / "state.json")
    b_state = _read_json(b_worktree / "product-definition" / "expense-reimbursement-dogfood" / "state.json")
    a_bundle = compile_contract(a_state, materialize_definition(a_state, replication_a_definition(a_state)))
    b_bundle = compile_contract(b_state, materialize_definition(b_state, replication_b_definition(b_state)))
    adapters_dir = Path(__file__).resolve().parent / "adapters"
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required for frozen runtime execution")

    a_adapter = {"name": "frozen-a-node-public-ui", "version": "1.0.0"}
    a_frozen = {"commit": A_COMMIT, "tree": a_tree}
    make_a_request = _request_factory(a_bundle, a_adapter, a_frozen)
    a_requests = [
        make_a_request(
            "SEQ-A-UI-DOMAIN",
            "A-PUBLIC-CONFIRM-BOOKING",
            {"type": "PUBLIC_ACTION", "input": {"action": "confirm_booking"}},
        )
    ]
    a_records = run_file_jsonl_adapter(
        [node, str(adapters_dir / "node_a_adapter.mjs")],
        a_requests,
        cwd=a_source,
        env={"JOEWRKS_FROZEN_SOURCE_ROOT": str(a_source)},
    )

    b_adapter = {"name": "frozen-b-vitest-engine-selectors", "version": "1.0.0"}
    b_frozen = {"commit": B_COMMIT, "tree": b_tree}
    make_b_request = _request_factory(b_bundle, b_adapter, b_frozen)
    reset = {"reset": True}
    b_requests = [
        make_b_request("SEQ-B030", "B030-CREATE", _command("CREATE_ADJUSTMENT", "usr-finance", "clm-completed", 4, "b030-create", {"kind": "Recovery", "amountKrw": 1000, "reason": "Correction"}), setup=reset),
        make_b_request("SEQ-B030", "B030-FAIL", _command("FAIL_ADJUSTMENT", "usr-finance", "clm-completed", 5, "b030-fail", {"adjustmentId": "adjustment-0001", "reason": "External failure"})),
        make_b_request("SEQ-B030", "B030-REJECTED-RESOLVE", _command("RESOLVE_ADJUSTMENT", "usr-finance", "clm-completed", 6, "b030-resolve", {"adjustmentId": "adjustment-0001", "result": "Executed", "note": "Bank trace found"})),
        make_b_request("SEQ-B030", "B030-SECOND-CREATE", _command("CREATE_ADJUSTMENT", "usr-finance", "clm-completed", 6, "b030-second", {"kind": "Additional payment", "amountKrw": 500, "reason": "Second correction"})),
        make_b_request("SEQ-B031-NAN", "B031-NAN-UPDATE", _command("UPDATE_DRAFT", "usr-employee", "clm-draft", 1, "b031-nan-update", {"originalAmount": {"$number": "NaN"}, "krwAmount": {"$number": "NaN"}}), setup=reset),
        make_b_request("SEQ-B031-NAN", "B031-NAN-SUBMIT", _command("SUBMIT_CLAIM", "usr-employee", "clm-draft", 2, "b031-nan-submit", {})),
        make_b_request("SEQ-B031-INFINITY", "B031-INFINITY-UPDATE", _command("UPDATE_DRAFT", "usr-employee", "clm-draft", 1, "b031-infinity-update", {"originalAmount": {"$number": "+Infinity"}, "krwAmount": {"$number": "+Infinity"}}), setup=reset),
        make_b_request("SEQ-B031-INFINITY", "B031-INFINITY-SUBMIT", _command("SUBMIT_CLAIM", "usr-employee", "clm-draft", 2, "b031-infinity-submit", {})),
        make_b_request("SEQ-B-STALE-LATEST", "B-ADMIN-STALE", _command("UPDATE_ACCOUNT", "usr-admin", "usr-employee", 0, "stale-admin", {"active": False, "roles": ["EMPLOYEE"]}), setup=reset),
        make_b_request("SEQ-B-HISTORY", "B-HISTORY-APPROVE", _command("APPROVE_CLAIM", "usr-manager", "clm-submitted", 1, "history-approve", {"revision": 1}), setup=reset),
        make_b_request("SEQ-B-HISTORY", "B-HISTORY-REVOKE", _command("REVOKE_APPROVAL", "usr-manager", "clm-submitted", 2, "history-revoke", {"revision": 1, "comment": "Receipt invalidated"})),
        make_b_request("SEQ-B-HISTORY", "B-HISTORY-QUERY", _command("HARNESS_QUERY_TIMELINE", "usr-manager", "clm-submitted", 3, "history-query", {"role": "MANAGER", "actorId": "usr-manager"})),
        make_b_request("SEQ-B-TERMINAL-PAYMENT", "B-TERMINAL-COMPLETE", _command("COMPLETE_PAYMENT", "usr-finance", "clm-scheduled", 2, "terminal-complete", {"actualDate": "2026-08-22", "method": "Bank transfer", "externalReference": "PAY-TERMINAL"}), setup={"reset": True, "patches": [{"pointer": "/claims/clm-scheduled/payment/overdue", "value": True}]}),
        make_b_request("SEQ-B-TERMINAL-RETRY", "B-TERMINAL-REMINDER-RETRY", _command("RUN_DELIVERY_RETRIES", "usr-admin", "worker-terminal", 0, "terminal-worker", {"failedDeliveryIds": ["delivery-stopped-reminder"]}), setup={"reset": True, "patches": [{"pointer": "/claims/clm-submitted/status", "value": "Payment pending"}, {"pointer": "/deliveries/-", "value": {"id": "delivery-stopped-reminder", "targetId": "clm-submitted", "channel": "EMAIL", "recipientId": "usr-manager", "template": "MANAGER_REVIEW_REMINDER", "status": "Queued", "attempts": 1, "manualRetryUsed": False, "version": 1}}]}),
        make_b_request("SEQ-B-AUTHORITY-LOSS", "B-AUTHORITY-GRANT", _command("ISSUE_FILE_ACCESS", "usr-manager", "file-clm-submitted-receipt", 0, "authority-grant", {}), setup=reset),
        make_b_request("SEQ-B-AUTHORITY-LOSS", "B-AUTHORITY-DOWNLOAD-DENIED", _command("DOWNLOAD_FILE", "usr-manager", "grant-0001", 1, "authority-download", {"rangeOrRetry": True}), setup={"patches": [{"pointer": "/users/usr-manager/active", "value": False}]}),
        make_b_request("SEQ-B-STALE-NOOP", "B-DRAFT-STALE-NOOP", _command("UPDATE_DRAFT", "usr-employee", "clm-draft", 0, "draft-stale", {"businessPurpose": "Preserved caller input"}), setup=reset),
        make_b_request("SEQ-B-REPLAY", "B-REPLAY-ORIGINAL", _command("UPDATE_DRAFT", "usr-employee", "clm-draft", 1, "draft-replay", {"businessPurpose": "Replay-safe"}), setup=reset),
        make_b_request("SEQ-B-REPLAY", "B-REPLAY-SAME-KEY", _command("UPDATE_DRAFT", "usr-employee", "clm-draft", 1, "draft-replay", {"businessPurpose": "Replay-safe"})),
        make_b_request("SEQ-B-DELIVERY-SEPARATION", "B-REASSIGN-COMMIT", _command("REASSIGN_MANAGER", "usr-admin", "clm-submitted", 1, "delivery-reassign", {"managerId": "usr-manager-other", "reason": "Manager left"}), setup={"reset": True, "patches": [{"pointer": "/users/usr-manager/active", "value": False}]}),
        make_b_request("SEQ-B-DELIVERY-SEPARATION", "B-DELIVERY-PERMANENT-FAILURE", _command("RUN_DELIVERY_RETRIES", "usr-admin", "worker-delivery", 0, "delivery-worker", {"failedDeliveryIds": ["delivery-0002"]}), setup={"patches": [{"pointer": "/deliveries/1/attempts", "value": 3}]}),
        make_b_request("SEQ-B-DELIVERY-SEPARATION", "B-DELIVERY-MANUAL-RETRY", _command("RETRY_DELIVERY", "usr-admin", "delivery-0002", 2, "delivery-manual", {})),
    ]
    vitest = b_source / "node_modules" / "vitest" / "vitest.mjs"
    if not vitest.is_file():
        raise RuntimeError(f"frozen B Vitest runtime is unavailable: {vitest}")
    b_records = run_file_jsonl_adapter(
        [
            node,
            str(vitest),
            "run",
            "--root",
            str(adapters_dir),
            "--config",
            str(adapters_dir / "vitest.config.mjs"),
            "--reporter=dot",
        ],
        b_requests,
        cwd=b_source,
        env={"JOEWRKS_FROZEN_SOURCE_ROOT": str(b_source)},
        timeout=120,
    )

    a_action_map = _actions(a_bundle)
    b_action_map = _actions(b_bundle)
    a_report = _evaluate(a_action_map, "confirm_booking", a_records[0], "SUCCESS")
    by_id = {record["test_id"]: record for record in b_records}
    b030_resolve = _evaluate(b_action_map, "resolve_adjustment_executed", by_id["B030-REJECTED-RESOLVE"])
    b030_second = _evaluate(b_action_map, "create_adjustment_after_rejection", by_id["B030-SECOND-CREATE"], "REJECTED")
    nan_update = _evaluate(b_action_map, "update_draft_money", by_id["B031-NAN-UPDATE"])
    nan_submit = _evaluate(b_action_map, "submit_invalid_money", by_id["B031-NAN-SUBMIT"])
    infinity_update = _evaluate(b_action_map, "update_draft_money", by_id["B031-INFINITY-UPDATE"])
    infinity_submit = _evaluate(b_action_map, "submit_invalid_money", by_id["B031-INFINITY-SUBMIT"])
    stale_latest = _evaluate(b_action_map, "admin_stale", by_id["B-ADMIN-STALE"], "STALE")
    history = _evaluate(b_action_map, "timeline_query", by_id["B-HISTORY-QUERY"], "SUCCESS")
    terminal_payment = _evaluate(b_action_map, "complete_payment_terminal", by_id["B-TERMINAL-COMPLETE"], "SUCCESS")
    terminal_retry = _evaluate(b_action_map, "terminal_reminder_retry", by_id["B-TERMINAL-REMINDER-RETRY"], "SUCCESS")
    authority_loss = _evaluate(b_action_map, "download_after_authority_loss", by_id["B-AUTHORITY-DOWNLOAD-DENIED"])
    stale_noop = _evaluate(b_action_map, "update_draft", by_id["B-DRAFT-STALE-NOOP"], "STALE")
    replay = _evaluate(b_action_map, "update_draft", by_id["B-REPLAY-SAME-KEY"], "IDEMPOTENT_REPLAY")
    reassign = _evaluate(b_action_map, "reassign_manager", by_id["B-REASSIGN-COMMIT"], "SUCCESS")
    delivery_failure = _evaluate(b_action_map, "delivery_failure_after_commit", by_id["B-DELIVERY-PERMANENT-FAILURE"], "SUCCESS")
    manual_retry = _evaluate(b_action_map, "manual_delivery_retry", by_id["B-DELIVERY-MANUAL-RETRY"], "SUCCESS")

    lifecycle_blueprint_path = Path(__file__).resolve().parent / "products" / "client-feedback-rev44.json"
    client_state = _read_json(a_root / "product-definition" / "client-feedback-portal-dogfood" / "state.json")
    client_bundle = compile_contract(
        client_state,
        materialize_definition(client_state, _read_json(lifecycle_blueprint_path)),
    )
    sentinel = verify_lifecycle_transition(
        client_bundle["lifecycles"][0],
        {"transition": "superseded-link-rule-as-current", "source_ids": ["DEC-011"]},
    )

    report = {
        "harness_version": "0.4.1.1",
        "frozen_sources": {
            "replication_a": {"commit": A_COMMIT, "tree": a_tree},
            "replication_b": {"commit": B_COMMIT, "tree": b_tree},
        },
        "contract_hashes": {
            "replication_a": a_bundle["contract_hash"],
            "replication_b": b_bundle["contract_hash"],
            "client_feedback_rev44": client_bundle["contract_hash"],
        },
        "contract_versions": {
            "replication_a": a_bundle["contract_schema_version"],
            "replication_b": b_bundle["contract_schema_version"],
            "client_feedback_rev44": client_bundle["contract_schema_version"],
        },
        "authority_assessments": {
            "replication_a": a_bundle["authority_assessment"],
            "replication_b": b_bundle["authority_assessment"],
            "client_feedback_rev44": client_bundle["authority_assessment"],
        },
        "production_handoff_eligible": {
            "replication_a": is_full_handoff_contract(a_bundle),
            "replication_b": is_full_handoff_contract(b_bundle),
            "client_feedback_rev44": is_full_handoff_contract(client_bundle),
        },
        "regressions": {
            "A_UI_DOMAIN_DISCONNECT": {"detected": not a_report["conformant"] and not a_report["components"]["authoritative_state"]["passed"], "verification": a_report},
            "B030_REJECTED_PARTIAL_MUTATION": {"detected": not b030_resolve["conformant"] and not b030_resolve["components"]["authoritative_state"]["passed"] and not b030_second["conformant"], "resolve_verification": b030_resolve, "second_command_verification": b030_second},
            "B031_NAN_SUBMISSION": {"detected": not nan_update["conformant"] and not nan_submit["conformant"], "runtime_non_finite_inputs": by_id["B031-NAN-UPDATE"]["result"]["runtime_non_finite_inputs"], "update_verification": nan_update, "submit_verification": nan_submit},
            "B031_POSITIVE_INFINITY_SUBMISSION": {"detected": not infinity_update["conformant"] and not infinity_submit["conformant"], "runtime_non_finite_inputs": by_id["B031-INFINITY-UPDATE"]["result"]["runtime_non_finite_inputs"], "update_verification": infinity_update, "submit_verification": infinity_submit},
            "B_STALE_LATEST_VALUE": {"detected": not stale_latest["conformant"], "verification": stale_latest},
            "B_HISTORICAL_STATUS_PROJECTION": {"detected": not history["conformant"], "verification": history},
            "B_TERMINAL_RETRY_STOP": {"detected": not terminal_payment["conformant"] and not terminal_retry["conformant"], "payment_verification": terminal_payment, "retry_verification": terminal_retry},
        },
        "coverage": {
            "authority_loss": authority_loss,
            "stale_no_op": stale_noop,
            "idempotent_replay": replay,
            "delivery_business_separation": {"conformant": reassign["conformant"] and delivery_failure["conformant"], "business_commit": reassign, "delivery_failure": delivery_failure},
            "manual_delivery_retry": manual_retry,
            "superseded_transition_sentinel": sentinel,
        },
    }
    _write_jsonl(output_dir / "frozen-a-evidence.jsonl", a_records)
    _write_jsonl(output_dir / "frozen-b-evidence.jsonl", b_records)
    _write_json(output_dir / "replication-a-contract.json", a_bundle)
    _write_json(output_dir / "replication-b-contract.json", b_bundle)
    _write_json(output_dir / "client-feedback-rev44-contract.json", client_bundle)
    _write_json(output_dir / "harness-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a-root", type=Path, required=True)
    parser.add_argument("--b-worktree", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args()
    report = execute_frozen_regressions(
        a_root=arguments.a_root,
        b_worktree=arguments.b_worktree,
        output_dir=arguments.output_dir,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
