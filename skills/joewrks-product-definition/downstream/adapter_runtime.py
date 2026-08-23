"""Subprocess boundary for versioned JSONL runtime adapters."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Sequence

from .protocol import PROTOCOL_VERSION, encode_typed_numbers, loads_record


class AdapterError(RuntimeError):
    """An external adapter failed or returned identity-invalid evidence."""


def build_request(
    *,
    sequence_id: str,
    test_id: str,
    product_slug: str,
    authority: dict[str, Any],
    contract_hash: str,
    adapter: dict[str, str],
    frozen_source: dict[str, str],
    command: dict[str, Any],
    setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = {
        "protocol_version": PROTOCOL_VERSION,
        "record_kind": "execution_request",
        "sequence_id": sequence_id,
        "test_id": test_id,
        "product_slug": product_slug,
        "authority": authority,
        "contract_hash": contract_hash,
        "adapter": adapter,
        "frozen_source": frozen_source,
        "command": command,
    }
    if setup:
        request["setup"] = setup
    return request


def _write_requests(path: Path, requests: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        for request in requests:
            output.write(
                json.dumps(
                    encode_typed_numbers(request),
                    ensure_ascii=False,
                    allow_nan=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )


def _assert_identity(request: dict[str, Any], response: dict[str, Any]) -> None:
    for field in (
        "protocol_version",
        "sequence_id",
        "test_id",
        "product_slug",
        "authority",
        "contract_hash",
        "adapter",
        "frozen_source",
        "command",
    ):
        expected = encode_typed_numbers(request.get(field))
        if response.get(field) != expected:
            raise AdapterError(f"adapter response identity drift: {field}")


def run_file_jsonl_adapter(
    command: Sequence[str],
    requests: list[dict[str, Any]],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 60,
) -> list[dict[str, Any]]:
    if not requests:
        return []
    with tempfile.TemporaryDirectory(prefix="joewrks-downstream-") as directory:
        request_path = Path(directory) / "requests.jsonl"
        response_path = Path(directory) / "responses.jsonl"
        _write_requests(request_path, requests)
        process_env = os.environ.copy()
        process_env.update(env or {})
        process_env["JOEWRKS_REQUEST_JSONL"] = str(request_path)
        process_env["JOEWRKS_RESPONSE_JSONL"] = str(response_path)
        try:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                env=process_env,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise AdapterError(f"adapter invocation failed: {error}") from error
        if completed.returncode != 0:
            raise AdapterError(
                f"adapter exited {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )
        if not response_path.is_file():
            raise AdapterError("adapter did not create response JSONL")
        lines = [line for line in response_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) != len(requests):
            raise AdapterError(
                f"adapter response count mismatch: expected {len(requests)}, observed {len(lines)}"
            )
        responses = [loads_record(line) for line in lines]
        for request, response in zip(requests, responses, strict=True):
            _assert_identity(request, response)
            if "conformant" in response.get("result", {}):
                raise AdapterError("adapter may not provide the semantic conformance verdict")
        return responses
