"""Read-only command line entry point for downstream V2 compilation."""

import json
import sys
from pathlib import Path

from .authority import DownstreamV2Error, canonical_json
from .compiler import compile_handoff_definition


USAGE = "python -m downstream_v2.compile STATE_JSON HANDOFF_DEFINITION_JSON"


class _CliInputError(ValueError):
    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(code)


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON constant: {value}")


def _read_json(path_text: str) -> object:
    path = Path(path_text)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise _CliInputError("READ_ERROR", {"path": path_text, "message": str(error)}) from error
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


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) != 2:
        _emit(_error("USAGE_ERROR", {"usage": USAGE}))
        return 2
    try:
        state = _read_json(arguments[0])
        definition = _read_json(arguments[1])
    except _CliInputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    try:
        result = compile_handoff_definition(state, definition)
    except DownstreamV2Error as error:
        _emit(_error(error.code, error.detail))
        return 1
    except RecursionError:
        _emit(_error("INVALID_SEMANTIC_INPUT", "maximum semantic input nesting depth exceeded"))
        return 1
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        _emit(_error("INVALID_SEMANTIC_INPUT", str(error)))
        return 1
    _emit(result)
    return 0 if result.get("contract") is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
