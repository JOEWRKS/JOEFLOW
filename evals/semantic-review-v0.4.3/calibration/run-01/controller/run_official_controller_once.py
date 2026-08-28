from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_ROOT = RUN_ROOT.parent
CONTROLLER_PATH = CALIBRATION_ROOT / "official_calibration_controller.py"
LOCK_PATH = RUN_ROOT / "CALIBRATION_RUN_LOCK.json"
EVIDENCE_PATH = RUN_ROOT / "OFFICIAL_CALIBRATION_EVIDENCE.json"
RAW_MANIFEST_PATH = RUN_ROOT / "RAW_OUTPUT_MANIFEST.json"
RECEIPT_PATH = RUN_ROOT / "OFFICIAL_CONTROLLER_INVOCATION.json"
RESULT_PATH = RUN_ROOT / "OFFICIAL_CALIBRATION_RESULT.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_ready(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"denominator": value.denominator, "numerator": value.numerator}
    if isinstance(value, dict):
        return {key: json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [json_ready(child) for child in value]
    return value


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            json_ready(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    if RECEIPT_PATH.exists() or RESULT_PATH.exists():
        raise RuntimeError("official controller invocation/result already exists")

    lock = load_json(LOCK_PATH)
    evidence = load_json(EVIDENCE_PATH)
    raw_manifest = load_json(RAW_MANIFEST_PATH)
    expected_controller_hash = lock["frozen_bindings"][
        "official_controller_file_sha256"
    ]
    controller_hash = file_sha256(CONTROLLER_PATH)
    if controller_hash != expected_controller_hash:
        raise RuntimeError("official controller hash drift")
    if raw_manifest["raw_outputs_frozen_before_oracle_scoring"] is not True:
        raise RuntimeError("raw outputs were not frozen before scoring")
    if raw_manifest["actual_attempt_count"] != 48 or raw_manifest["retry_count"] != 0:
        raise RuntimeError("raw execution population drift")

    spec = importlib.util.spec_from_file_location(
        "v043_frozen_official_calibration_controller", CONTROLLER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen official controller")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    started = utc_now()
    receipt: dict[str, Any] = {
        "attempt_count": 1,
        "completed_at_utc": None,
        "controller_file_sha256": controller_hash,
        "evidence_file_sha256": file_sha256(EVIDENCE_PATH),
        "official_function": "evaluate_official_calibration",
        "real_mode": True,
        "result_status": "RUNNING",
        "schema_version": "joewrks.semantic-review-official-controller-invocation/1.0",
        "started_at_utc": started,
    }
    RECEIPT_PATH.write_bytes(canonical_bytes(receipt))

    try:
        result = module.evaluate_official_calibration(evidence, real_mode=True)
    except module.CalibrationControllerError as error:
        completed = utc_now()
        error_result = {
            "controller_error": {
                "code": error.code,
                "detail": error.detail,
                "message": str(error),
            },
            "gate_report": None,
            "official_controller_completed": False,
            "schema_version": "joewrks.semantic-review-official-calibration-result/1.0",
        }
        RESULT_PATH.write_bytes(canonical_bytes(error_result))
        receipt.update(
            {
                "completed_at_utc": completed,
                "result_file_sha256": file_sha256(RESULT_PATH),
                "result_status": "CONTROLLER_ERROR",
            }
        )
        RECEIPT_PATH.write_bytes(canonical_bytes(receipt))
        print(f"OFFICIAL_CONTROLLER_ERROR={error.code}")
        print(f"OFFICIAL_CONTROLLER_DETAIL={error.detail}")
        return 2

    RESULT_PATH.write_bytes(canonical_bytes(result))
    receipt.update(
        {
            "completed_at_utc": utc_now(),
            "result_file_sha256": file_sha256(RESULT_PATH),
            "result_status": "COMPLETED",
        }
    )
    RECEIPT_PATH.write_bytes(canonical_bytes(receipt))
    gate_passed = bool(result.get("gate_report", {}).get("passed"))
    print("OFFICIAL_CONTROLLER_COMPLETED=TRUE")
    print(f"GATE_REPORT_PASSED={str(gate_passed).upper()}")
    print(f"RESULT_SHA256={file_sha256(RESULT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
