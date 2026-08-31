"""Read-only installed CLI routing for the current downstream 2.1 workflow."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from downstream_v2.authority import DownstreamV2Error, canonical_json
from downstream_v21.audit import audit_action_contract_v21_against_state
from downstream_v21.compiler import compile_handoff_definition_v21
from downstream_v21.semantic_review import build_semantic_review_package_v21


COMPILE_USAGE = "python compile_downstream_v2.py STATE_JSON HANDOFF_DEFINITION_JSON"
AUDIT_USAGE = "python audit_downstream_v2.py CONTRACT_JSON STATE_JSON"
REVIEW_USAGE = "python build_semantic_review_v2.py CONTRACT_JSON"


class _CliInputError(ValueError):
    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(code)


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON constant: {value}")


def _read_json(path_text: str) -> object:
    try:
        text = Path(path_text).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise _CliInputError(
            "READ_ERROR", {"path": path_text, "message": str(error)}
        ) from error
    try:
        return json.loads(text, parse_constant=_reject_constant)
    except RecursionError as error:
        raise _CliInputError(
            "JSON_PARSE_ERROR",
            {"path": path_text, "message": "maximum JSON nesting depth exceeded"},
        ) from error
    except (json.JSONDecodeError, ValueError) as error:
        detail = {"path": path_text, "message": str(error)}
        if isinstance(error, json.JSONDecodeError):
            detail.update({"line": error.lineno, "column": error.colno})
        raise _CliInputError("JSON_PARSE_ERROR", detail) from error


def _emit(payload: object) -> None:
    sys.stdout.buffer.write(canonical_json(payload).encode("utf-8") + b"\n")


def _error(code: str, detail: object) -> dict[str, object]:
    return {"status": "ERROR", "error": {"code": code, "detail": detail}}


def compile_main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) != 2:
        _emit(_error("USAGE_ERROR", {"usage": COMPILE_USAGE}))
        return 2
    try:
        state = _read_json(arguments[0])
        definition = _read_json(arguments[1])
    except _CliInputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    try:
        result = compile_handoff_definition_v21(state, definition)
    except DownstreamV2Error as error:
        _emit(_error(error.code, error.detail))
        return 1
    except RecursionError:
        _emit(
            _error(
                "INVALID_SEMANTIC_INPUT",
                "maximum semantic input nesting depth exceeded",
            )
        )
        return 1
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        _emit(_error("INVALID_SEMANTIC_INPUT", str(error)))
        return 1
    _emit(result)
    return 0 if result.get("contract") is not None else 1


def audit_main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) != 2:
        _emit(_error("USAGE_ERROR", {"usage": AUDIT_USAGE}))
        return 2
    try:
        contract = _read_json(arguments[0])
        state = _read_json(arguments[1])
    except _CliInputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    try:
        copy.deepcopy(contract)
        copy.deepcopy(state)
        result = audit_action_contract_v21_against_state(contract, state)
    except RecursionError:
        _emit(
            _error(
                "INVALID_AUDIT_INPUT",
                "maximum semantic input nesting depth exceeded",
            )
        )
        return 1
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        _emit(_error("INVALID_AUDIT_INPUT", str(error)))
        return 1
    _emit(result)
    return 0 if result.get("status") == "CONFORMANT" else 1


def review_main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) != 1:
        _emit(_error("USAGE_ERROR", {"usage": REVIEW_USAGE}))
        return 2
    try:
        contract = _read_json(arguments[0])
    except _CliInputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    try:
        package = build_semantic_review_package_v21(contract)
    except RecursionError:
        _emit(
            _error(
                "INVALID_ACTION_CONTRACT_V21",
                "maximum semantic input nesting depth exceeded",
            )
        )
        return 1
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        _emit(_error("INVALID_ACTION_CONTRACT_V21", str(error)))
        return 1
    _emit({"review_required": package is not None, "package": package})
    return 0


__all__ = ["audit_main", "compile_main", "review_main"]
