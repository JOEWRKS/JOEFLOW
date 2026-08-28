from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
INPUT_MANIFEST_PATH = RUN_ROOT / "INPUT_FREEZE_MANIFEST.json"
DESTINATION_ROOT = RUN_ROOT / "raw-outputs"
RAW_MANIFEST_PATH = RUN_ROOT / "RAW_OUTPUT_MANIFEST.json"
CONTEXT_FILES = (
    "raw-output.txt",
    "codex-events.jsonl",
    "codex-stderr.txt",
    "execution-receipt.json",
)
ROOT_FILES = ("execution-start.json", "execution-summary.json")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import frozen calibration bytes without interpreting reviewer semantics."
    )
    parser.add_argument("--capture-root", required=True, type=Path)
    args = parser.parse_args()
    capture_root = args.capture_root.resolve()

    require(capture_root.is_dir(), f"capture root missing: {capture_root}")
    require(not DESTINATION_ROOT.exists(), f"destination already exists: {DESTINATION_ROOT}")
    require(not RAW_MANIFEST_PATH.exists(), f"manifest already exists: {RAW_MANIFEST_PATH}")

    input_manifest = load_json(INPUT_MANIFEST_PATH)
    planned = input_manifest["contexts"]
    require(len(planned) == 48, "input manifest must contain exactly 48 contexts")
    planned_ids = [item["planned_context_id"] for item in planned]
    require(len(set(planned_ids)) == 48, "planned context IDs must be unique")

    execution_summary = load_json(capture_root / "execution-summary.json")
    receipts_by_id = {
        item["planned_context_id"]: item for item in execution_summary["receipts"]
    }
    require(set(receipts_by_id) == set(planned_ids), "summary context set mismatch")
    require(execution_summary["actual_attempt_count"] == 48, "attempt count mismatch")
    require(execution_summary["retry_count"] == 0, "retry count must be zero")
    require(execution_summary["raw_output_present_count"] == 48, "raw output count mismatch")
    require(execution_summary["unique_runtime_context_count"] == 48, "runtime IDs not unique")
    require(execution_summary["zero_exit_count"] == 48, "nonzero execution exit found")

    DESTINATION_ROOT.mkdir(parents=False)
    context_manifest: list[dict] = []
    try:
        for filename in ROOT_FILES:
            source = capture_root / filename
            require(source.is_file(), f"missing capture root file: {filename}")
            shutil.copyfile(source, DESTINATION_ROOT / filename)

        for planned_item in planned:
            context_id = planned_item["planned_context_id"]
            source_dir = capture_root / context_id
            destination_dir = DESTINATION_ROOT / context_id
            require(source_dir.is_dir(), f"missing context capture: {context_id}")
            destination_dir.mkdir()

            files: dict[str, dict[str, int | str]] = {}
            for filename in CONTEXT_FILES:
                source = source_dir / filename
                require(source.is_file(), f"missing {context_id}/{filename}")
                destination = destination_dir / filename
                shutil.copyfile(source, destination)
                require(source.read_bytes() == destination.read_bytes(), f"copy drift: {context_id}/{filename}")
                files[filename] = {"bytes": destination.stat().st_size, "sha256": sha256(destination)}

            receipt = load_json(destination_dir / "execution-receipt.json")
            expected = receipts_by_id[context_id]
            require(receipt == expected, f"receipt differs from summary: {context_id}")
            require(receipt["attempt_count"] == 1, f"attempt count is not one: {context_id}")
            require(receipt["retry_status"] == "NO_RETRY", f"retry found: {context_id}")
            require(receipt["process_exit_code"] == 0, f"nonzero exit: {context_id}")
            require(receipt["raw_output_present"] is True, f"raw output absent: {context_id}")
            require(receipt["input_bundle_sha256"] == planned_item["input_bundle_sha256"], f"input bundle mismatch: {context_id}")
            require(receipt["raw_output_sha256"] == files["raw-output.txt"]["sha256"], f"raw output hash mismatch: {context_id}")
            require(receipt["codex_events_sha256"] == files["codex-events.jsonl"]["sha256"], f"event hash mismatch: {context_id}")
            require(receipt["codex_stderr_sha256"] == files["codex-stderr.txt"]["sha256"], f"stderr hash mismatch: {context_id}")

            context_manifest.append(
                {
                    "actual_runtime_context_id": receipt["actual_runtime_context_id"],
                    "attempt_count": receipt["attempt_count"],
                    "case_id": receipt["case_id"],
                    "cohort_id": receipt["cohort_id"],
                    "files": files,
                    "input_bundle_sha256": receipt["input_bundle_sha256"],
                    "kind": receipt["kind"],
                    "planned_context_id": context_id,
                    "process_exit_code": receipt["process_exit_code"],
                    "raw_output_present": receipt["raw_output_present"],
                    "retry_status": receipt["retry_status"],
                    "review_run_id": receipt["review_run_id"],
                }
            )

        runtime_ids = [item["actual_runtime_context_id"] for item in context_manifest]
        require(len(set(runtime_ids)) == 48, "imported runtime context IDs not unique")
        manifest = {
            "actual_attempt_count": 48,
            "contexts": context_manifest,
            "full_context_count": 3,
            "golden_context_count": 45,
            "input_freeze_commit": execution_summary["input_freeze_commit"],
            "planned_context_count": 48,
            "raw_outputs_frozen_before_oracle_scoring": True,
            "retry_count": 0,
            "root_files": {
                filename: {
                    "bytes": (DESTINATION_ROOT / filename).stat().st_size,
                    "sha256": sha256(DESTINATION_ROOT / filename),
                }
                for filename in ROOT_FILES
            },
            "schema_version": "joewrks.semantic-review-raw-output-freeze/1.0",
            "unique_runtime_context_count": 48,
            "verdicts_interpreted": False,
        }
        RAW_MANIFEST_PATH.write_bytes(canonical_bytes(manifest))
    except BaseException:
        if DESTINATION_ROOT.exists():
            shutil.rmtree(DESTINATION_ROOT)
        if RAW_MANIFEST_PATH.exists():
            RAW_MANIFEST_PATH.unlink()
        raise

    print("RAW_OUTPUT_FREEZE=PASS")
    print("ACTUAL_ATTEMPTS=48")
    print("RAW_OUTPUTS_PRESENT=48")
    print("UNIQUE_RUNTIME_CONTEXTS=48")
    print("RETRIES=0")
    print(f"RAW_OUTPUT_MANIFEST_SHA256={sha256(RAW_MANIFEST_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
