"""Read-only capability disposition for the semantic-review runner."""

from __future__ import annotations

import sys


_previous_dont_write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    import argparse
    import importlib
    import importlib.abc
    import importlib.machinery
    import importlib.util
    import json
    import os
    from pathlib import Path, PurePosixPath
    import stat
    import subprocess
    from typing import Iterable
finally:
    sys.dont_write_bytecode = _previous_dont_write_bytecode
    del _previous_dont_write_bytecode


_SKILL_ROOT = Path(__file__).resolve().parents[1]


AUDIT_SCHEMA_VERSION = "joewrks.reviewer-runner-capability-audit/1.0"
IMPLEMENTATION_BASE_REVISION = "71ffc0a66618c11e2fe08a442df5fd2d67718f7b"
BACKEND_KIND = "STATELESS_TOOLLESS_EXTERNAL_INFERENCE"
REGISTERED_PRODUCTION_ADAPTERS: tuple[object, ...] = ()
RUNNER_SOURCE_PATH = "skills/joewrks-product-definition/reviewer_runner"
_PUBLIC_RUNNER_PACKAGE_NAME = "reviewer_runner"

_SNAPSHOT_MODULE_SOURCES = {
    "": f"{RUNNER_SOURCE_PATH}/__init__.py",
    ".identity": f"{RUNNER_SOURCE_PATH}/identity.py",
    ".backend": f"{RUNNER_SOURCE_PATH}/backend.py",
    ".request": f"{RUNNER_SOURCE_PATH}/request.py",
    ".providers": f"{RUNNER_SOURCE_PATH}/providers/__init__.py",
    ".providers.anthropic": f"{RUNNER_SOURCE_PATH}/providers/anthropic.py",
    ".providers.anthropic_admission": (
        f"{RUNNER_SOURCE_PATH}/providers/anthropic_admission.py"
    ),
}

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
        ["git", "--no-optional-locks", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=not binary,
    )
    return result.stdout


def _git_blob_id(repository: Path, content: bytes) -> str:
    result = subprocess.run(
        [
            "git",
            "--no-optional-locks",
            "-C",
            str(repository),
            "hash-object",
            "--stdin",
        ],
        check=True,
        capture_output=True,
        input=content,
    )
    return result.stdout.decode("ascii").strip()


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


def _runner_revision_blob_map(repository: Path, revision: str) -> dict[str, str]:
    raw = _git(
        repository,
        "ls-tree",
        "-r",
        "-z",
        revision,
        "--",
        RUNNER_SOURCE_PATH,
        binary=True,
    )
    records: dict[str, str] = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        metadata, path_bytes = entry.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split(" ")
        if object_type != "blob":
            raise RuntimeError("runner source inventory contains a non-blob object")
        records[path_bytes.decode("utf-8")] = f"{mode}:{object_id}"
    return dict(sorted(records.items()))


def _runner_index_blob_map(repository: Path) -> dict[str, str]:
    raw = _git(
        repository,
        "ls-files",
        "--stage",
        "-z",
        "--",
        RUNNER_SOURCE_PATH,
        binary=True,
    )
    records: dict[str, str] = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        metadata, path_bytes = entry.split(b"\t", 1)
        mode, object_id, stage = metadata.decode("ascii").split(" ")
        if stage != "0":
            raise RuntimeError("runner source inventory contains an unmerged entry")
        path = path_bytes.decode("utf-8")
        if path in records:
            raise RuntimeError("runner source inventory contains a duplicate path")
        records[path] = f"{mode}:{object_id}"
    return dict(sorted(records.items()))


def _read_bound_regular_file(path: Path) -> tuple[str, bytes]:
    path_stat = path.lstat()
    if not stat.S_ISREG(path_stat.st_mode):
        raise RuntimeError("live runner source is not a regular file")
    with path.open("rb") as source_file:
        opened_before = os.fstat(source_file.fileno())
        content = source_file.read()
        opened_after = os.fstat(source_file.fileno())
    path_after = path.lstat()
    identity_fields = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns")
    identities = [
        tuple(getattr(value, field) for field in identity_fields)
        for value in (path_stat, opened_before, opened_after, path_after)
    ]
    if any(identity != identities[0] for identity in identities[1:]):
        raise RuntimeError("live runner source changed while it was read")
    live_mode = "100755" if path_stat.st_mode & 0o111 else "100644"
    return live_mode, content


def _verify_runner_source_binding(
    repository: Path,
    revision: str,
) -> dict[str, bytes]:
    repository_root = repository.resolve(strict=True)
    audit_repository_root = _SKILL_ROOT.parents[1].resolve(strict=True)
    if repository_root != audit_repository_root:
        raise RuntimeError("runner source repository does not match the audit module")

    runner_root = repository_root / RUNNER_SOURCE_PATH
    if runner_root.resolve(strict=True) != runner_root:
        raise RuntimeError("runner source path does not resolve to its tracked location")

    status = _git(
        repository_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--",
        RUNNER_SOURCE_PATH,
        binary=True,
    )
    if status:
        raise RuntimeError("live runner source is modified or contains untracked files")

    revision_inventory = _runner_revision_blob_map(repository_root, revision)
    current_inventory = _runner_index_blob_map(repository_root)
    required_core_sources = {
        _SNAPSHOT_MODULE_SOURCES[""],
        _SNAPSHOT_MODULE_SOURCES[".identity"],
        _SNAPSHOT_MODULE_SOURCES[".backend"],
    }
    if (
        not revision_inventory
        or not required_core_sources.issubset(revision_inventory)
        or any(
            current_inventory.get(path) != commitment
            for path, commitment in revision_inventory.items()
        )
    ):
        raise RuntimeError(
            "runner source inventory is absent, incomplete, or differs from loaded source"
        )

    snapshot: dict[str, bytes] = {}
    runner_prefix = f"{RUNNER_SOURCE_PATH}/"
    for path, commitment in revision_inventory.items():
        relative_path = PurePosixPath(path)
        if (
            relative_path.is_absolute()
            or ".." in relative_path.parts
            or not path.startswith(runner_prefix)
        ):
            raise RuntimeError("runner source inventory contains an invalid path")
        live_path = repository_root.joinpath(*relative_path.parts)
        if live_path.resolve(strict=True) != live_path:
            raise RuntimeError("live runner source path does not resolve to its tracked location")

        expected_mode, expected_blob_id = commitment.split(":", 1)
        live_mode, content = _read_bound_regular_file(live_path)
        live_blob_id = _git_blob_id(repository_root, content)
        if live_mode != expected_mode or live_blob_id != expected_blob_id:
            raise RuntimeError("live runner source bytes or mode differ from revision")
        snapshot[path] = content
    return snapshot


class _SnapshotSourceLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname: str, source: bytes, filename: Path):
        super().__init__(fullname, str(filename))
        self._source = source
        self._filename = filename

    def exec_module(self, module) -> None:
        module.__file__ = str(self._filename)
        code = compile(self._source, str(self._filename), "exec", dont_inherit=True)
        exec(code, module.__dict__)


class _SnapshotSourceFinder(importlib.abc.MetaPathFinder):
    def __init__(
        self,
        package_name: str,
        repository: Path,
        snapshot: dict[str, bytes],
    ):
        self._package_name = package_name
        self._repository = repository
        self._snapshot = snapshot

    def find_spec(self, fullname, path=None, target=None):
        if (
            fullname == _PUBLIC_RUNNER_PACKAGE_NAME
            or fullname.startswith(f"{_PUBLIC_RUNNER_PACKAGE_NAME}.")
        ):
            raise RuntimeError("verified runner attempted an absolute public import")
        if fullname == self._package_name:
            suffix = ""
        elif fullname.startswith(f"{self._package_name}."):
            suffix = fullname[len(self._package_name):]
        else:
            return None
        relative_source = _SNAPSHOT_MODULE_SOURCES.get(suffix)
        if relative_source is None:
            raise RuntimeError("verified runner attempted an unexpected module import")
        source = self._snapshot.get(relative_source)
        if source is None:
            raise RuntimeError("verified runner source snapshot is incomplete")
        filename = self._repository.joinpath(*PurePosixPath(relative_source).parts)
        loader = _SnapshotSourceLoader(fullname, source, filename)
        return importlib.util.spec_from_loader(
            fullname,
            loader,
            origin=str(filename),
            is_package=suffix in ("", ".providers"),
        )


def _private_runner_module_names(package_name: str) -> tuple[str, ...]:
    return tuple(
        name
        for name in sys.modules
        if name == package_name or name.startswith(f"{package_name}.")
    )


def _remove_private_runner_modules(package_name: str) -> None:
    for name in _private_runner_module_names(package_name):
        sys.modules.pop(name, None)


def _stash_public_runner_modules() -> dict[str, object]:
    """Remove public runner modules so snapshot imports cannot reuse them."""

    names = tuple(
        name
        for name in sys.modules
        if (
            name == _PUBLIC_RUNNER_PACKAGE_NAME
            or name.startswith(f"{_PUBLIC_RUNNER_PACKAGE_NAME}.")
        )
    )
    return {name: sys.modules.pop(name) for name in names}


def _restore_public_runner_modules(stashed_modules: dict[str, object]) -> None:
    """Discard public modules introduced during loading and restore caller state."""

    for name in tuple(sys.modules):
        if (
            name == _PUBLIC_RUNNER_PACKAGE_NAME
            or name.startswith(f"{_PUBLIC_RUNNER_PACKAGE_NAME}.")
        ):
            sys.modules.pop(name, None)
    sys.modules.update(stashed_modules)


def _verify_snapshot_module(
    module,
    *,
    fullname: str,
    filename: Path,
    source: bytes,
) -> None:
    spec = getattr(module, "__spec__", None)
    loader = getattr(module, "__loader__", None)
    if (
        module.__name__ != fullname
        or module.__file__ != str(filename)
        or spec is None
        or spec.name != fullname
        or spec.origin != str(filename)
        or type(spec.loader) is not _SnapshotSourceLoader
        or loader is not spec.loader
        or loader._filename != filename
        or loader._source != source
    ):
        raise RuntimeError("verified runner module binding is invalid")


def _load_verified_runner_api(
    repository: Path,
    revision: str,
    snapshot: dict[str, bytes],
):
    package_name = f"_audit_verified_reviewer_runner_{revision}"
    finder = None
    stashed_public_modules = _stash_public_runner_modules()
    try:
        if _private_runner_module_names(package_name):
            raise RuntimeError("verified runner module namespace collision")
        finder = _SnapshotSourceFinder(package_name, repository, snapshot)
        sys.meta_path.insert(0, finder)
        package_module = importlib.import_module(package_name)
        identity_module = importlib.import_module(f"{package_name}.identity")
        backend_module = importlib.import_module(f"{package_name}.backend")
        expected_modules = {
            package_name: f"{RUNNER_SOURCE_PATH}/__init__.py",
            f"{package_name}.identity": f"{RUNNER_SOURCE_PATH}/identity.py",
            f"{package_name}.backend": f"{RUNNER_SOURCE_PATH}/backend.py",
        }
        loaded_names = set(_private_runner_module_names(package_name))
        if loaded_names != set(expected_modules):
            raise RuntimeError("verified runner loaded an unexpected module")
        for module, fullname in (
            (package_module, package_name),
            (identity_module, f"{package_name}.identity"),
            (backend_module, f"{package_name}.backend"),
        ):
            relative_source = expected_modules[fullname]
            filename = repository.joinpath(*PurePosixPath(relative_source).parts)
            _verify_snapshot_module(
                module,
                fullname=fullname,
                filename=filename,
                source=snapshot[relative_source],
            )
        return identity_module, backend_module
    finally:
        if finder is not None and finder in sys.meta_path:
            sys.meta_path.remove(finder)
        _remove_private_runner_modules(package_name)
        _restore_public_runner_modules(stashed_public_modules)


def _load_verified_snapshot_registration(
    repository: Path,
    revision: str,
    snapshot: dict[str, bytes],
) -> tuple[object, ...]:
    """Load only the revision-bound provider registration for audit tests."""

    registration_source = _SNAPSHOT_MODULE_SOURCES[".providers"]
    revision_inventory = _runner_revision_blob_map(repository, revision)
    registration_commitment = revision_inventory.get(registration_source)
    registration_bytes = snapshot.get(registration_source)
    if registration_commitment is None:
        if registration_bytes is not None:
            raise RuntimeError("verified provider source snapshot disagrees with revision")
        return ()
    if registration_bytes is None:
        raise RuntimeError("verified provider source snapshot is incomplete")

    required_sources = (
        _SNAPSHOT_MODULE_SOURCES[""],
        _SNAPSHOT_MODULE_SOURCES[".identity"],
        _SNAPSHOT_MODULE_SOURCES[".backend"],
        _SNAPSHOT_MODULE_SOURCES[".request"],
        registration_source,
        _SNAPSHOT_MODULE_SOURCES[".providers.anthropic"],
        _SNAPSHOT_MODULE_SOURCES[".providers.anthropic_admission"],
    )
    for relative_source in required_sources:
        source = snapshot.get(relative_source)
        commitment = revision_inventory.get(relative_source)
        if source is None or commitment is None:
            raise RuntimeError("verified provider source snapshot is incomplete")
        _, expected_blob_id = commitment.split(":", 1)
        if _git_blob_id(repository, source) != expected_blob_id:
            raise RuntimeError("verified provider source bytes differ from revision")

    package_name = f"_audit_verified_reviewer_runner_{revision}"
    finder = None
    stashed_public_modules = _stash_public_runner_modules()
    try:
        if _private_runner_module_names(package_name):
            raise RuntimeError("verified runner module namespace collision")
        finder = _SnapshotSourceFinder(package_name, repository, snapshot)
        sys.meta_path.insert(0, finder)
        providers_module = importlib.import_module(f"{package_name}.providers")
        expected_modules = {
            f"{package_name}{suffix}": relative_source
            for suffix, relative_source in _SNAPSHOT_MODULE_SOURCES.items()
        }
        loaded_names = set(_private_runner_module_names(package_name))
        if loaded_names != set(expected_modules):
            raise RuntimeError("verified runner loaded an unexpected module")
        for fullname, relative_source in expected_modules.items():
            module = sys.modules.get(fullname)
            if module is None:
                raise RuntimeError("verified runner source snapshot is incomplete")
            filename = repository.joinpath(*PurePosixPath(relative_source).parts)
            _verify_snapshot_module(
                module,
                fullname=fullname,
                filename=filename,
                source=snapshot[relative_source],
            )
        registered = getattr(providers_module, "REGISTERED_PRODUCTION_ADAPTERS", None)
        if type(registered) is not tuple:
            raise RuntimeError("verified provider registration is not an immutable tuple")
        return registered
    finally:
        if finder is not None and finder in sys.meta_path:
            sys.meta_path.remove(finder)
        _remove_private_runner_modules(package_name)
        _restore_public_runner_modules(stashed_public_modules)


def _rehydrate_backend_descriptor(descriptor, identity_module, backend_module):
    try:
        if (
            type(descriptor).__module__ != "reviewer_runner.backend"
            or type(descriptor).__qualname__ != "BackendDescriptor"
        ):
            raise ValueError("backend descriptor must be an exact BackendDescriptor")
        identity = descriptor.identity
        if (
            type(identity).__module__ != "reviewer_runner.identity"
            or type(identity).__qualname__ != "BackendIdentity"
        ):
            raise ValueError("backend identity must be an exact BackendIdentity")
        trusted_identity = identity_module.BackendIdentity(
            backend_kind=identity.backend_kind,
            adapter_id=identity.adapter_id,
            adapter_version=identity.adapter_version,
            endpoint_identity=identity.endpoint_identity,
            deployment_identity=identity.deployment_identity,
            model_revision_identity=identity.model_revision_identity,
            model_identity_stability=identity.model_identity_stability,
            inference_settings_sha256=identity.inference_settings_sha256,
            retention_policy_identity=identity.retention_policy_identity,
            privacy_policy_identity=identity.privacy_policy_identity,
            is_test_double=identity.is_test_double,
        )
        trusted_observations = []
        for observation in descriptor.observations:
            if (
                type(observation).__module__ != "reviewer_runner.backend"
                or type(observation).__qualname__ != "CapabilityObservation"
            ):
                raise ValueError(
                    "observations must be exact CapabilityObservation values"
                )
            trusted_observations.append(
                backend_module.CapabilityObservation(
                    capability=observation.capability,
                    classification=identity_module.CapabilityClass(
                        observation.classification.value
                    ),
                    method=observation.method,
                    evidence_sha256=observation.evidence_sha256,
                )
            )
        return backend_module.BackendDescriptor(
            identity=trusted_identity,
            max_request_bytes=descriptor.max_request_bytes,
            observations=tuple(trusted_observations),
        )
    except (AttributeError, TypeError, ValueError) as error:
        raise ValueError("registered adapter returned an invalid descriptor") from error


def _real_adapter_count(
    registered_adapters: Iterable[object],
    identity_module,
    backend_module,
) -> int:
    count = 0
    for adapter in registered_adapters:
        describe = getattr(adapter, "describe", None)
        if not callable(describe):
            raise ValueError("registered adapter must expose describe()")
        descriptor = _rehydrate_backend_descriptor(
            describe(),
            identity_module,
            backend_module,
        )
        backend_module.validate_backend_descriptor(descriptor)
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
    runner_snapshot = _verify_runner_source_binding(repository, commit)
    identity_module, backend_module = _load_verified_runner_api(
        repository.resolve(strict=True),
        commit,
        runner_snapshot,
    )
    baseline = frozen_blob_map(repository, IMPLEMENTATION_BASE_REVISION)
    observed = frozen_blob_map(repository, commit)
    if not baseline or observed != baseline:
        raise RuntimeError("frozen Product Definition, semantic-review, or M6 paths changed")

    real_adapter_count = _real_adapter_count(
        tuple(registered_adapters),
        identity_module,
        backend_module,
    )
    if real_adapter_count == 0:
        capability = "UNAVAILABLE"
        runner_state = "ISOLATION_CAPABILITY_UNAVAILABLE"
    else:
        capability = "UNTESTED"
        runner_state = "CALIBRATION_NOT_RUN"

    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "runner_contract_version": identity_module.RUNNER_CONTRACT_VERSION,
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
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
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
        sys.stdout.buffer.write(canonical_audit_json(document).encode("utf-8"))
        sys.stdout.buffer.flush()
        return 0
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode


if __name__ == "__main__":
    raise SystemExit(main())
