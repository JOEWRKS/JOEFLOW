"""Execute each frozen run-01 input once in a projectless isolated Codex context."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parents[1]
INPUTS_ROOT = RUN_ROOT / "inputs"
INPUT_MANIFEST_PATH = RUN_ROOT / "INPUT_FREEZE_MANIFEST.json"
INVOCATION_PATH = RUN_ROOT / "REVIEWER_INVOCATION.txt"
EXPECTED_CONTEXTS = 48
_print_lock = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _file_inventory(root: Path) -> list[dict[str, Any]]:
    inventory = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        data = path.read_bytes()
        inventory.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
        )
    return inventory


def _bundle_hash(root: Path) -> str:
    return hashlib.sha256(_canonical_bytes(_file_inventory(root))).hexdigest()


def _extract_runtime_context_id(stdout: bytes) -> str | None:
    for raw_line in stdout.splitlines():
        try:
            event = json.loads(raw_line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        for key in ("thread_id", "session_id", "conversation_id"):
            value = event.get(key)
            if isinstance(value, str) and value:
                return value
        if event.get("type") in {"thread.started", "session.started"}:
            nested = event.get("thread") or event.get("session") or {}
            if isinstance(nested, dict):
                for key in ("id", "thread_id", "session_id"):
                    value = nested.get(key)
                    if isinstance(value, str) and value:
                        return value
    return None


def _execute_one(
    *,
    codex_path: str,
    context: dict[str, Any],
    wrapper_text: str,
    staging_root: Path,
    capture_root: Path,
    model: str,
    reasoning_effort: str,
) -> dict[str, Any]:
    context_id = context["planned_context_id"]
    context_root = staging_root / context_id
    capture = capture_root / context_id
    capture.mkdir(parents=True, exist_ok=False)
    raw_output_path = capture / "raw-output.txt"
    stdout_path = capture / "codex-events.jsonl"
    stderr_path = capture / "codex-stderr.txt"
    command = [
        codex_path,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--model",
        model,
        "--config",
        f'model_reasoning_effort="{reasoning_effort}"',
        "--cd",
        str(context_root),
        "--output-last-message",
        str(raw_output_path),
        "--json",
        "--color",
        "never",
        wrapper_text,
    ]
    started = _utc_now()
    process = subprocess.Popen(
        command,
        cwd=context_root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    ended = _utc_now()
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    raw_output_present = raw_output_path.is_file()
    raw_output = raw_output_path.read_bytes() if raw_output_present else b""
    receipt = {
        "schema_version": "joewrks.semantic-review-context-execution-receipt/1.0",
        "planned_context_id": context_id,
        "review_run_id": context["review_run_id"],
        "cohort_id": context["cohort_id"],
        "kind": context["kind"],
        "case_id": context["case_id"],
        "actual_runtime_context_id": _extract_runtime_context_id(stdout),
        "input_bundle_sha256": _bundle_hash(context_root),
        "reviewer_input_package_hash": context["reviewer_input_package_hash"],
        "reviewer_brief_hash": context["reviewer_brief_hash"],
        "start_time_utc": started,
        "end_time_utc": ended,
        "process_id": process.pid,
        "process_exit_code": process.returncode,
        "raw_output_present": raw_output_present,
        "raw_output_sha256": hashlib.sha256(raw_output).hexdigest()
        if raw_output_present
        else None,
        "raw_output_bytes": len(raw_output) if raw_output_present else 0,
        "codex_events_sha256": hashlib.sha256(stdout).hexdigest(),
        "codex_stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "attempt_count": 1,
        "retry_status": "NO_RETRY",
        "isolation": {
            "fresh_context": True,
            "ephemeral": True,
            "sandbox": "read-only",
            "projectless_execution_root": True,
            "previous_verdict_access": False,
            "manifest_only_evidence": True,
        },
    }
    (capture / "execution-receipt.json").write_bytes(
        _canonical_bytes(receipt) + b"\n"
    )
    with _print_lock:
        print(
            f"CONTEXT_FINISHED={context_id} EXIT={process.returncode} "
            f"OUTPUT={str(raw_output_present).upper()} "
            f"RUNTIME_ID={receipt['actual_runtime_context_id'] or 'ABSENT'}",
            flush=True,
        )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex", required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--input-freeze-commit", required=True)
    args = parser.parse_args()

    if args.staging_root.exists() or args.capture_root.exists():
        raise RuntimeError("staging and capture roots must be absent before execution")
    manifest = json.loads(INPUT_MANIFEST_PATH.read_text(encoding="utf-8"))
    contexts = manifest["contexts"]
    if len(contexts) != EXPECTED_CONTEXTS:
        raise RuntimeError("frozen context count mismatch")
    if manifest.get("reviewer_outputs") != "ABSENT":
        raise RuntimeError("reviewer outputs were not absent at execution start")
    wrapper = INVOCATION_PATH.read_bytes()
    if hashlib.sha256(wrapper).hexdigest() != manifest["invocation_wrapper_sha256"]:
        raise RuntimeError("invocation wrapper hash drift")

    args.staging_root.mkdir(parents=True, exist_ok=False)
    args.capture_root.mkdir(parents=True, exist_ok=False)
    for context in contexts:
        context_id = context["planned_context_id"]
        source = INPUTS_ROOT / context_id
        destination = args.staging_root / context_id
        shutil.copytree(source, destination)
        if _bundle_hash(destination) != context["input_bundle_sha256"]:
            raise RuntimeError(f"staged input drift: {context_id}")

    start_record = {
        "schema_version": "joewrks.semantic-review-execution-start/1.0",
        "input_freeze_commit": args.input_freeze_commit,
        "planned_context_count": EXPECTED_CONTEXTS,
        "started_at_utc": _utc_now(),
        "invocation_wrapper_sha256": manifest["invocation_wrapper_sha256"],
        "model": manifest["execution_parameters"]["model"],
        "reasoning_effort": manifest["execution_parameters"]["reasoning_effort"],
        "max_concurrency": manifest["execution_parameters"]["max_concurrency"],
        "no_retry": True,
    }
    (args.capture_root / "execution-start.json").write_bytes(
        _canonical_bytes(start_record) + b"\n"
    )

    receipts: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=manifest["execution_parameters"]["max_concurrency"]
    ) as executor:
        futures = [
            executor.submit(
                _execute_one,
                codex_path=args.codex,
                context=context,
                wrapper_text=wrapper.decode("utf-8"),
                staging_root=args.staging_root,
                capture_root=args.capture_root,
                model=manifest["execution_parameters"]["model"],
                reasoning_effort=manifest["execution_parameters"]["reasoning_effort"],
            )
            for context in contexts
        ]
        for future in concurrent.futures.as_completed(futures):
            receipts.append(future.result())

    receipts.sort(key=lambda item: item["planned_context_id"])
    summary = {
        "schema_version": "joewrks.semantic-review-execution-summary/1.0",
        "input_freeze_commit": args.input_freeze_commit,
        "planned_context_count": EXPECTED_CONTEXTS,
        "actual_attempt_count": len(receipts),
        "unique_planned_context_count": len(
            {item["planned_context_id"] for item in receipts}
        ),
        "unique_runtime_context_count": len(
            {
                item["actual_runtime_context_id"]
                for item in receipts
                if item["actual_runtime_context_id"]
            }
        ),
        "raw_output_present_count": sum(
            bool(item["raw_output_present"]) for item in receipts
        ),
        "zero_exit_count": sum(item["process_exit_code"] == 0 for item in receipts),
        "retry_count": 0,
        "completed_at_utc": _utc_now(),
        "receipts": receipts,
    }
    (args.capture_root / "execution-summary.json").write_bytes(
        _canonical_bytes(summary) + b"\n"
    )
    print(f"ACTUAL_ATTEMPTS={len(receipts)}", flush=True)
    print(
        f"RAW_OUTPUTS_PRESENT={summary['raw_output_present_count']}", flush=True
    )
    print(f"UNIQUE_RUNTIME_CONTEXTS={summary['unique_runtime_context_count']}", flush=True)
    print("RETRIES=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
