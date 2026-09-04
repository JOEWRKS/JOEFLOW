"""Read-only capability disposition for the semantic-review runner."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


_SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))

from reviewer_runner import RUNNER_CONTRACT_VERSION  # noqa: E402
from reviewer_runner.backend import validate_backend_descriptor  # noqa: E402


AUDIT_SCHEMA_VERSION = "joewrks.reviewer-runner-capability-audit/1.0"
IMPLEMENTATION_BASE_REVISION = "71ffc0a66618c11e2fe08a442df5fd2d67718f7b"
BACKEND_KIND = "STATELESS_TOOLLESS_EXTERNAL_INFERENCE"
REGISTERED_PRODUCTION_ADAPTERS: tuple[object, ...] = ()

FROZEN_PATHS = (
    "product-definition",
    "skills/joewrks-product-definition/downstream/semantic_review",
    "skills/joewrks-product-definition/downstream_v21/semantic_review",
    "skills/joewrks-product-definition/downstream/schemas/semantic-review-input-manifest.schema.json",
    "skills/joewrks-product-definition/downstream/schemas/semantic-review-output.schema.json",
    "skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-input-v21.schema.json",
    "skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-output-v21.schema.json",
    "evals/semantic-review-v0.4.3",
    "evals/core-semantic-closure-v2-m6",
)


def _git(repository: Path, *arguments: str, binary: bool = False):
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=not binary,
    )
    return result.stdout


def _commit_and_tree(repository: Path, revision: str) -> tuple[str, str]:
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError("revision must be a non-empty Git revision")
    commit = _git(repository, "rev-parse", "--verify", f"{revision}^{{commit}}")
    tree = _git(repository, "rev-parse", "--verify", f"{commit.strip()}^{{tree}}")
    return commit.strip(), tree.strip()


def frozen_blob_map(repository: Path | str, revision: str) -> dict[str, str]:
    """Return exact mode/object commitments for every frozen path at revision."""

    repository = Path(repository)
    commit, _ = _commit_and_tree(repository, revision)
    raw = _git(
        repository,
        "ls-tree",
        "-r",
        "-z",
        commit,
        "--",
        *FROZEN_PATHS,
        binary=True,
    )
    records: dict[str, str] = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        metadata, path_bytes = entry.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split(" ")
        if object_type != "blob":
            raise RuntimeError("frozen path inventory contains a non-blob object")
        path = path_bytes.decode("utf-8")
        records[path] = f"{mode}:{object_id}"
    return dict(sorted(records.items()))


def _real_adapter_count(registered_adapters: Iterable[object]) -> int:
    count = 0
    for adapter in registered_adapters:
        describe = getattr(adapter, "describe", None)
        if not callable(describe):
            raise ValueError("registered adapter must expose describe()")
        descriptor = describe()
        validate_backend_descriptor(descriptor)
        if not descriptor.identity.is_test_double:
            count += 1
    return count


def build_capability_audit(
    repository: Path | str,
    revision: str,
    *,
    registered_adapters: Iterable[object] = REGISTERED_PRODUCTION_ADAPTERS,
) -> dict[str, object]:
    """Build the deterministic current-runtime disposition without executing inference."""

    repository = Path(repository)
    commit, tree = _commit_and_tree(repository, revision)
    baseline = frozen_blob_map(repository, IMPLEMENTATION_BASE_REVISION)
    observed = frozen_blob_map(repository, commit)
    if not baseline or observed != baseline:
        raise RuntimeError("frozen Product Definition, semantic-review, or M6 paths changed")

    real_adapter_count = _real_adapter_count(tuple(registered_adapters))
    if real_adapter_count == 0:
        capability = "UNAVAILABLE"
        runner_state = "ISOLATION_CAPABILITY_UNAVAILABLE"
    else:
        capability = "UNTESTED"
        runner_state = "CALIBRATION_NOT_RUN"

    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "runner_contract_version": RUNNER_CONTRACT_VERSION,
        "implementation_status": "RUNNER_IMPLEMENTED",
        "backend_kind": BACKEND_KIND,
        "registered_real_adapter_count": real_adapter_count,
        "real_backend_capability": capability,
        "runner_state": runner_state,
        "calibration_status": "CALIBRATION_NOT_RUN",
        "semantic_review_21_reliability": "NOT_MEASURED",
        "v044_status": "BLOCKED",
        "real_calibration_attempts": 1,
        "valid_real_calibration_runs": 0,
        "fake_backend_authoritative": False,
        "provider_selected": None,
        "implementation_code_commit": commit,
        "implementation_code_tree": tree,
    }


def canonical_audit_json(document: dict[str, object]) -> str:
    """Serialize capability evidence as canonical UTF-8 JSON text."""

    return json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    if not arguments.json:
        parser.error("--json is required")

    document = build_capability_audit(
        arguments.repository,
        arguments.revision,
        registered_adapters=REGISTERED_PRODUCTION_ADAPTERS,
    )
    sys.stdout.write(canonical_audit_json(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
