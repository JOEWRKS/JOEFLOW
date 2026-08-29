"""Public API and read-only CLI for semantic-review/2.0 package construction."""

import json
import sys
from pathlib import Path

from ..authority import canonical_json
from .package import build_semantic_review_package


__all__ = ["build_semantic_review_package"]

USAGE = "python -m downstream_v2.semantic_review.build_package CONTRACT_JSON"


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
    if len(arguments) != 1:
        _emit(_error("USAGE_ERROR", {"usage": USAGE}))
        return 2
    try:
        contract = _read_json(arguments[0])
    except _CliInputError as error:
        _emit(_error(error.code, error.detail))
        return 2
    try:
        package = build_semantic_review_package(contract)
    except RecursionError:
        _emit(
            _error(
                "INVALID_ACTION_CONTRACT_V2",
                "maximum semantic input nesting depth exceeded",
            )
        )
        return 1
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        _emit(_error("INVALID_ACTION_CONTRACT_V2", str(error)))
        return 1
    _emit({"review_required": package is not None, "package": package})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
