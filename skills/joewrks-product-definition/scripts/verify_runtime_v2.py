"""Installed V2 runtime verifier; callable from any consumer working directory."""

from __future__ import annotations

import json
import sys
from pathlib import Path


_SKILL_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_ROOT = _SKILL_ROOT / "scripts"
for _root in (_SKILL_ROOT, _SCRIPTS_ROOT):
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from downstream_v2.authority import canonical_json  # noqa: E402
from downstream_v2.reentry import audit_contract_against_state  # noqa: E402
from downstream_v2.runtime import (  # noqa: E402
    RuntimeVerificationError,
    contained_runtime_error_result,
    verify_action_execution,
    verify_lifecycle_execution,
)
from downstream_v2.runtime_report import (  # noqa: E402
    build_runtime_conformance_report,
    validate_runtime_conformance_report,
)
from downstream_v2.semantic_review.output import semantic_assurance_result  # noqa: E402


USAGE = (
    "python verify_runtime_v2.py CONTRACT_JSON CURRENT_STATE_JSON EXECUTION_JSONL "
    "[REVIEW_PACKAGE_JSON REVIEW_OUTPUT_JSON]"
)
_MAX_JSON_DEPTH = 100
_MAX_JSON_NODES = 100_000
_OUTPUT_CANONICALIZATION_ERROR = (
    b'{"error":{"code":"OUTPUT_CANONICALIZATION_ERROR","detail":'
    b'"runtime report could not be canonicalized"},"status":"ERROR"}\n'
)


class _InputError(ValueError):
    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(code)


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON constant: {value}")


def _read_text(path_text: str) -> str:
    try:
        return Path(path_text).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise _InputError("READ_ERROR", {"path": path_text, "message": str(error)}) from error


def _decode_json(text: str, *, path_text: str, line_number: int | None = None) -> object:
    try:
        value = json.loads(text, parse_constant=_reject_constant)
    except RecursionError as error:
        detail = {"path": path_text, "message": "maximum JSON nesting depth exceeded"}
        if line_number is not None:
            detail["line"] = line_number
        raise _InputError("JSON_PARSE_ERROR", detail) from error
    except (json.JSONDecodeError, ValueError) as error:
        detail = {"path": path_text, "message": str(error)}
        if isinstance(error, json.JSONDecodeError):
            detail.update({"line": error.lineno, "column": error.colno})
        if line_number is not None:
            detail["jsonl_record"] = line_number
        raise _InputError("JSON_PARSE_ERROR", detail) from error
    stack = [(value, 0)]
    nodes = 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        if depth > _MAX_JSON_DEPTH or nodes > _MAX_JSON_NODES:
            detail = {"path": path_text, "message": "JSON input exceeds structural limits"}
            if line_number is not None:
                detail["jsonl_record"] = line_number
            raise _InputError("JSON_PARSE_ERROR", detail)
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                detail = {"path": path_text, "message": "JSON object keys must be strings"}
                if line_number is not None:
                    detail["jsonl_record"] = line_number
                raise _InputError("JSON_PARSE_ERROR", detail)
            stack.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            stack.extend((child, depth + 1) for child in item)
        elif item is not None and not isinstance(item, (str, int, float, bool)):
            detail = {"path": path_text, "message": "JSON value is not canonicalizable"}
            if line_number is not None:
                detail["jsonl_record"] = line_number
            raise _InputError("JSON_PARSE_ERROR", detail)
    try:
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError, RecursionError) as error:
        detail = {"path": path_text, "message": "JSON value is not canonicalizable"}
        if line_number is not None:
            detail["jsonl_record"] = line_number
        raise _InputError("JSON_PARSE_ERROR", detail) from error
    return value


def _read_json(path_text: str) -> object:
    return _decode_json(_read_text(path_text), path_text=path_text)


def _read_jsonl(path_text: str) -> list[object]:
    records = []
    for line_number, line in enumerate(_read_text(path_text).splitlines(), start=1):
        if not line.strip():
            continue
        records.append(_decode_json(line, path_text=path_text, line_number=line_number))
    return records


def _emit(payload: object) -> None:
    sys.stdout.buffer.write(canonical_json(payload).encode("utf-8") + b"\n")


def _error(code: str, detail: object) -> dict[str, object]:
    return {"status": "ERROR", "error": {"code": code, "detail": detail}}


def _verify_records(
    contract: dict[str, object], records: list[object],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    action_results = []
    lifecycle_results = []
    for record in records:
        mapping = record if isinstance(record, dict) else {}
        command = mapping.get("command") if isinstance(mapping.get("command"), dict) else {}
        is_lifecycle = "lifecycle_id" in command or mapping.get("record_kind") == "lifecycle_observation"
        try:
            if is_lifecycle:
                lifecycle_results.append(verify_lifecycle_execution(contract, record))
            else:
                action_results.append(verify_action_execution(contract, record))
        except RuntimeVerificationError as error:
            target = lifecycle_results if is_lifecycle else action_results
            target.append(contained_runtime_error_result(
                contract,
                record,
                error,
                lifecycle=is_lifecycle,
            ))
        except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
            contained = RuntimeVerificationError("RUNTIME_EVIDENCE_INVALID", str(error))
            target = lifecycle_results if is_lifecycle else action_results
            target.append(contained_runtime_error_result(
                contract,
                record,
                contained,
                lifecycle=is_lifecycle,
            ))
    return action_results, lifecycle_results


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) not in {3, 5}:
        _emit(_error("USAGE_ERROR", {"usage": USAGE}))
        return 2
    try:
        contract = _read_json(arguments[0])
        state = _read_json(arguments[1])
        records = _read_jsonl(arguments[2])
        review_package = _read_json(arguments[3]) if len(arguments) == 5 else None
        review_output = _read_json(arguments[4]) if len(arguments) == 5 else None
    except _InputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    contract_object = contract if isinstance(contract, dict) else {}
    state_object = state if isinstance(state, dict) else {}
    try:
        audit_result = audit_contract_against_state(contract_object, state_object)
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        audit_result = {
            "status": "DEFINITION_NOT_READY",
            "global_definition_closed": False,
            "authority_revision_relation": "SAME_APPROVED_REVISION",
            "reentry_events": [],
            "audit_error": str(error),
        }
    try:
        assurance = semantic_assurance_result(
            contract_object,
            review_package if isinstance(review_package, dict) else None,
            review_output if isinstance(review_output, dict) else None,
        )
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError):
        assurance = {"review_completion": "PENDING", "reliability_status": "NOT_MEASURED"}
    assurance = {**assurance, "verification_scope": "FULL_CONTRACT"}
    try:
        action_results, lifecycle_results = _verify_records(contract_object, records)
    except _InputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError):
        _emit(_error("JSON_PARSE_ERROR", {"message": "runtime evidence could not be canonicalized"}))
        return 2
    try:
        report = build_runtime_conformance_report(
            contract_object,
            audit_result,
            action_results,
            lifecycle_results,
            assurance,
        )
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        _emit(_error("INVALID_RUNTIME_INPUT", str(error)))
        return 1
    try:
        validate_runtime_conformance_report(report, contract_object)
    except RuntimeVerificationError as error:
        _emit(_error(error.code, error.detail))
        return 1
    try:
        _emit(report)
    except (TypeError, ValueError, AttributeError, RecursionError):
        sys.stdout.buffer.write(_OUTPUT_CANONICALIZATION_ERROR)
        return 2
    return 0 if report.get("implementation_status") == "IMPLEMENTATION_CONFORMANT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
