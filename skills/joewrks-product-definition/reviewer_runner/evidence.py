"""Immutable evidence, exact task cleanup, and repository no-mutation guards."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Sequence
import uuid

from .identity import (
    canonical_json_bytes,
    sha256_bytes,
    validate_receipt_document,
)


_RUNNER_DIRECTORY = "joewrks-reviewer-runner"
_RESERVATION_DIRECTORY = ".joewrks-run-reservations"
_OWNER_MARKER = ".joewrks-runner-owner.json"
_OWNED_DIRECTORIES = ("inputs", "response-working", "synthetic-canaries")
_RECEIPT_FILENAMES = frozenset(
    {"receipt.json", "runner-receipt.json", "reviewer-runner-receipt.json"}
)
_SAFE_PATH_COMPONENT = re.compile(r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?")
_MAX_PATH_COMPONENT_LENGTH = 128
_WINDOWS_RESERVED_PATH_STEMS = frozenset(
    {
        "aux",
        "con",
        "nul",
        "prn",
        *(f"com{number}" for number in range(1, 10)),
        *(f"lpt{number}" for number in range(1, 10)),
    }
)


class EvidenceLifecycleError(ValueError):
    """A terminal failure to preserve evidence or prove exact cleanup."""


@dataclass(frozen=True)
class SourceSnapshot:
    head_sha: str
    tree_sha: str
    status_sha256: str
    clean: bool


@dataclass(frozen=True)
class CleanupResult:
    removed_paths: tuple[str, ...]
    missing_after_cleanup: tuple[str, ...]
    sibling_paths_unchanged: tuple[str, ...]
    source_snapshot_unchanged: bool
    cleanup_sha256: str


@dataclass
class TaskWorkspace:
    transient_parent: Path
    review_run_id: str
    root: Path
    marker_path: Path
    inputs_path: Path
    response_working_path: Path
    synthetic_canaries_path: Path
    repository_root: Path
    source_snapshot: SourceSnapshot
    _terminal: bool = field(default=False, init=False, repr=False)

    @classmethod
    def create(cls, transient_parent: Path, review_run_id: str) -> "TaskWorkspace":
        """Create one new marker-owned workspace without reusing prior output."""

        parent = _require_existing_directory(transient_parent, "transient_parent")
        _require_safe_path_component(review_run_id, "review_run_id")
        runner_parent = parent / _RUNNER_DIRECTORY
        if os.path.lexists(runner_parent):
            _require_plain_directory(runner_parent, "runner workspace parent")
            if not _same_path(runner_parent.resolve(strict=True), runner_parent):
                raise EvidenceLifecycleError("runner workspace parent is path-aliased")
        else:
            runner_parent.mkdir()
        if not _is_strict_descendant(runner_parent.resolve(strict=True), parent):
            raise EvidenceLifecycleError("runner workspace parent escapes transient_parent")

        task_root = runner_parent / review_run_id
        if os.path.lexists(task_root):
            raise EvidenceLifecycleError(
                "review workspace already exists; prior execution state is ambiguous"
            )
        _create_run_reservation(runner_parent, task_root, review_run_id)
        task_root.mkdir()
        resolved_root = task_root.resolve(strict=True)
        if not _is_strict_descendant(resolved_root, parent):
            raise EvidenceLifecycleError("review workspace escapes transient_parent")
        marker_path = resolved_root / _OWNER_MARKER
        atomic_freeze_evidence(
            canonical_json_bytes(
                {
                    "resolved_root": str(resolved_root),
                    "review_run_id": review_run_id,
                }
            ),
            marker_path,
        )
        owned_paths = tuple(resolved_root / name for name in _OWNED_DIRECTORIES)
        for owned_path in owned_paths:
            owned_path.mkdir()

        repository_root = Path.cwd().resolve(strict=True)
        source_snapshot = _capture_source_snapshot(repository_root)
        return cls(
            transient_parent=parent,
            review_run_id=review_run_id,
            root=resolved_root,
            marker_path=marker_path,
            inputs_path=owned_paths[0],
            response_working_path=owned_paths[1],
            synthetic_canaries_path=owned_paths[2],
            repository_root=repository_root,
            source_snapshot=source_snapshot,
        )

    def cleanup(
        self,
        *,
        preserved_evidence_paths: Sequence[Path],
        sibling_paths: Sequence[Path],
    ) -> CleanupResult:
        """Remove only this marker-owned root after evidence and boundary checks."""

        if self._terminal:
            raise EvidenceLifecycleError("workspace lifecycle is terminal")
        self._terminal = True

        _verify_run_reservation(self.root.parent, self.root, self.review_run_id)
        _verify_workspace_identity(self)
        _verify_owned_tree(self.root)
        preserved = _capture_preserved_evidence(
            preserved_evidence_paths,
            task_root=self.root,
        )
        siblings_before = _capture_sibling_states(
            sibling_paths,
            task_root=self.root,
        )
        verify_source_unchanged(self.source_snapshot, self.repository_root)

        try:
            _remove_owned_tree(self.root)
        except OSError as error:
            raise EvidenceLifecycleError(
                f"exact task-root cleanup failed: {error}"
            ) from error
        if os.path.lexists(self.root):
            raise EvidenceLifecycleError("exact task root still exists after cleanup")

        _verify_path_states_unchanged(preserved, "preserved evidence")
        _verify_path_states_unchanged(siblings_before, "sibling")
        source_unchanged = verify_source_unchanged(
            self.source_snapshot,
            self.repository_root,
        )
        removed_paths = (str(self.root),)
        missing_after_cleanup = (str(self.root),)
        unchanged_siblings = tuple(sorted(siblings_before))
        result_content = {
            "missing_after_cleanup": list(missing_after_cleanup),
            "preserved_evidence": [
                {"path": path, "sha256": preserved[path]} for path in sorted(preserved)
            ],
            "removed_paths": list(removed_paths),
            "sibling_paths_unchanged": list(unchanged_siblings),
            "source_snapshot_unchanged": source_unchanged,
        }
        result = CleanupResult(
            removed_paths=removed_paths,
            missing_after_cleanup=missing_after_cleanup,
            sibling_paths_unchanged=unchanged_siblings,
            source_snapshot_unchanged=source_unchanged,
            cleanup_sha256=sha256_bytes(canonical_json_bytes(result_content)),
        )
        _clear_run_reservation(self.root.parent, self.root, self.review_run_id)
        return result


def capture_source_snapshot(
    repository_root: Path,
    *,
    execution_mode: str = "REAL_REVIEW",
) -> SourceSnapshot:
    """Capture exact Git identity and require a clean real-review source tree."""

    if not isinstance(execution_mode, str) or not execution_mode:
        raise EvidenceLifecycleError("execution_mode must be a non-empty string")
    snapshot = _capture_source_snapshot(repository_root)
    if execution_mode == "REAL_REVIEW" and not snapshot.clean:
        raise EvidenceLifecycleError("REAL_REVIEW requires a clean repository source snapshot")
    return snapshot


def verify_source_unchanged(
    before: SourceSnapshot,
    repository_root: Path,
) -> bool:
    """Require exact HEAD, tree, status-byte hash, and clean-flag equality."""

    if type(before) is not SourceSnapshot:
        raise EvidenceLifecycleError("before must be an exact SourceSnapshot")
    after = _capture_source_snapshot(repository_root)
    if after != before:
        raise EvidenceLifecycleError("repository source snapshot changed")
    return True


def atomic_freeze_evidence(content: bytes, target_path: Path) -> Path:
    """Persist immutable exact bytes with exclusive temp, fsync, replace, and readback."""

    if type(content) is not bytes:
        raise EvidenceLifecycleError("evidence content must be exact bytes")
    if not isinstance(target_path, Path):
        raise EvidenceLifecycleError("target_path must be a Path")
    if not target_path.name:
        raise EvidenceLifecycleError("target_path must name an evidence file")
    unresolved_target = Path(os.path.abspath(target_path))
    _reject_reparse_components(unresolved_target, "evidence target")
    target = unresolved_target.resolve(strict=False)
    if os.path.lexists(target):
        return _read_existing_immutable_evidence(target, content)

    target.parent.mkdir(parents=True, exist_ok=True)
    _reject_reparse_components(unresolved_target, "evidence target")
    _require_plain_directory(target.parent, "evidence parent")
    publication_lock = target.with_name(f".{target.name}.freeze.lock")
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    lock_identity = None
    target_claim_identity = None
    target_claim_bytes = None
    temporary_identity = None
    lock_created = False
    target_claimed = False
    created_temporary = False
    try:
        try:
            with publication_lock.open("xb") as stream:
                lock_created = True
                lock_bytes = uuid.uuid4().hex.encode("ascii")
                written = stream.write(lock_bytes)
                if written != len(lock_bytes):
                    raise EvidenceLifecycleError(
                        "evidence publication lock write was incomplete"
                    )
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError as error:
            raise EvidenceLifecycleError(
                "evidence publication is already reserved by another writer"
            ) from error
        lock_identity = _plain_file_identity(
            publication_lock,
            "evidence publication lock",
        )
        if os.path.lexists(target):
            return _read_existing_immutable_evidence(target, content)
        target_claim_bytes = (
            b"joewrks-evidence-destination-reservation\0"
            + uuid.uuid4().hex.encode("ascii")
        )
        try:
            with target.open("xb") as stream:
                target_claimed = True
                written = stream.write(target_claim_bytes)
                if written != len(target_claim_bytes):
                    raise EvidenceLifecycleError(
                        "evidence destination reservation write was incomplete"
                    )
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            return _read_existing_immutable_evidence(target, content)
        target_claim_identity = _plain_file_identity(
            target,
            "evidence destination reservation",
        )
        with temporary.open("xb") as stream:
            created_temporary = True
            written = stream.write(content)
            if written != len(content):
                raise EvidenceLifecycleError("evidence temporary write was incomplete")
            stream.flush()
            os.fsync(stream.fileno())
        temporary_identity = _plain_file_identity(temporary, "evidence temporary file")
        _verify_created_file(
            target,
            target_claim_identity,
            target_claim_bytes,
            "evidence destination reservation",
        )
        os.replace(temporary, target)
        created_temporary = False
        target_claimed = False
        observed = target.read_bytes()
        if observed != content or sha256_bytes(observed) != sha256_bytes(content):
            raise EvidenceLifecycleError(
                "frozen evidence readback does not match exact bytes"
            )
        return target
    finally:
        if created_temporary and os.path.lexists(temporary):
            _unlink_created_file(
                temporary,
                temporary_identity,
                "evidence temporary file",
            )
        if target_claimed:
            if not os.path.lexists(target):
                raise EvidenceLifecycleError(
                    "evidence destination reservation disappeared before cleanup"
                )
            _verify_created_file(
                target,
                target_claim_identity,
                target_claim_bytes,
                "evidence destination reservation",
            )
            _unlink_created_file(
                target,
                target_claim_identity,
                "evidence destination reservation",
            )
        if lock_created and os.path.lexists(publication_lock):
            _unlink_created_file(
                publication_lock,
                lock_identity,
                "evidence publication lock",
            )


def load_used_provider_request_ids(evidence_root: Path) -> frozenset[str]:
    """Load provider request identifiers only from valid frozen runner receipts."""

    if not isinstance(evidence_root, Path):
        raise EvidenceLifecycleError("evidence_root must be a Path")
    root = evidence_root.resolve(strict=False)
    if not os.path.lexists(root):
        return frozenset()
    _require_plain_directory(root, "evidence_root")
    identifiers: set[str] = set()
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        _require_resolved_descendant_or_same(current_path, root, "evidence directory")
        for name in tuple(directories) + tuple(files):
            candidate = current_path / name
            if _is_reparse_point(candidate):
                raise EvidenceLifecycleError("evidence index contains a symlink or junction")
            _require_resolved_descendant_or_same(candidate, root, "evidence path")
        for name in files:
            if name not in _RECEIPT_FILENAMES:
                continue
            receipt_path = current_path / name
            try:
                document = json.loads(
                    receipt_path.read_bytes().decode("utf-8", errors="strict"),
                    object_pairs_hook=_object_without_duplicate_keys,
                    parse_constant=_reject_non_json_number,
                )
                receipt = validate_receipt_document(document)
            except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
                raise EvidenceLifecycleError(
                    f"frozen runner receipt is invalid: {receipt_path}: {error}"
                ) from error
            identifiers.add(receipt.response_identity.provider_request_id)
    return frozenset(identifiers)


def _capture_source_snapshot(repository_root: Path) -> SourceSnapshot:
    root = _require_existing_directory(repository_root, "repository_root")
    head_bytes = _run_git(root, "rev-parse", "HEAD")
    tree_bytes = _run_git(root, "rev-parse", "HEAD^{tree}")
    status_bytes = _run_git(root, "status", "--porcelain=v1", "-z")
    head_sha = _decode_git_sha(head_bytes, "HEAD")
    tree_sha = _decode_git_sha(tree_bytes, "HEAD tree")
    return SourceSnapshot(
        head_sha=head_sha,
        tree_sha=tree_sha,
        status_sha256=sha256_bytes(status_bytes),
        clean=status_bytes == b"",
    )


def _run_git(repository_root: Path, *arguments: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repository_root,
            check=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceLifecycleError(
            f"git source snapshot command failed: {' '.join(arguments)}"
        ) from error
    return completed.stdout


def _decode_git_sha(value: bytes, label: str) -> str:
    try:
        decoded = value.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise EvidenceLifecycleError(f"git {label} was not ASCII") from error
    sha = decoded.removesuffix("\n").removesuffix("\r")
    if (
        not sha
        or len(sha) not in (40, 64)
        or any(character not in "0123456789abcdef" for character in sha)
    ):
        raise EvidenceLifecycleError(f"git {label} was not one exact object ID")
    return sha


def _read_existing_immutable_evidence(target: Path, expected: bytes) -> Path:
    if _is_reparse_point(target) or not target.is_file():
        raise EvidenceLifecycleError("immutable evidence target is not a plain file")
    try:
        observed = target.read_bytes()
    except OSError as error:
        raise EvidenceLifecycleError(f"immutable evidence cannot be read: {error}") from error
    if observed != expected:
        raise EvidenceLifecycleError("immutable evidence conflict at the same path")
    return target


def _plain_file_identity(path: Path, label: str) -> tuple[int, int]:
    if _is_reparse_point(path) or not path.is_file():
        raise EvidenceLifecycleError(f"{label} is not an owned plain file")
    try:
        observed = path.lstat()
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} cannot be inspected") from error
    return observed.st_dev, observed.st_ino


def _verify_created_file(
    path: Path,
    expected_identity: tuple[int, int] | None,
    expected_bytes: bytes | None,
    label: str,
) -> None:
    if expected_identity is None or _plain_file_identity(path, label) != expected_identity:
        raise EvidenceLifecycleError(f"{label} ownership changed")
    if expected_bytes is None or path.read_bytes() != expected_bytes:
        raise EvidenceLifecycleError(f"{label} bytes changed")


def _unlink_created_file(
    path: Path,
    expected_identity: tuple[int, int] | None,
    label: str,
) -> None:
    if expected_identity is None or _plain_file_identity(path, label) != expected_identity:
        raise EvidenceLifecycleError(f"{label} ownership changed before cleanup")
    try:
        path.unlink()
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} cleanup failed: {error}") from error
    if os.path.lexists(path):
        raise EvidenceLifecycleError(f"{label} still exists after cleanup")


def _create_run_reservation(
    runner_parent: Path,
    task_root: Path,
    review_run_id: str,
) -> None:
    reservation_directory = runner_parent / _RESERVATION_DIRECTORY
    if os.path.lexists(reservation_directory):
        _require_plain_directory(reservation_directory, "run reservation directory")
    else:
        reservation_directory.mkdir()
    _require_resolved_descendant_or_same(
        reservation_directory,
        runner_parent,
        "run reservation directory",
    )
    reservation_path = reservation_directory / f"{review_run_id}.json"
    if os.path.lexists(reservation_path):
        raise EvidenceLifecycleError(
            "review run is reserved by a prior or active execution"
        )
    content = _reservation_bytes(task_root, review_run_id)
    try:
        with reservation_path.open("xb") as stream:
            written = stream.write(content)
            if written != len(content):
                raise EvidenceLifecycleError("run reservation write was incomplete")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise EvidenceLifecycleError(
            "review run is reserved by a concurrent execution"
        ) from error
    if reservation_path.read_bytes() != content:
        raise EvidenceLifecycleError("run reservation readback changed")


def _verify_run_reservation(
    runner_parent: Path,
    task_root: Path,
    review_run_id: str,
) -> Path:
    reservation_directory = runner_parent / _RESERVATION_DIRECTORY
    _require_plain_directory(reservation_directory, "run reservation directory")
    reservation_path = reservation_directory / f"{review_run_id}.json"
    if _is_reparse_point(reservation_path) or not reservation_path.is_file():
        raise EvidenceLifecycleError("run reservation is missing or ambiguous")
    _require_resolved_descendant_or_same(
        reservation_path,
        reservation_directory,
        "run reservation",
    )
    if reservation_path.read_bytes() != _reservation_bytes(task_root, review_run_id):
        raise EvidenceLifecycleError("run reservation does not match the task")
    return reservation_path


def _clear_run_reservation(
    runner_parent: Path,
    task_root: Path,
    review_run_id: str,
) -> None:
    reservation_path = _verify_run_reservation(
        runner_parent,
        task_root,
        review_run_id,
    )
    try:
        reservation_path.unlink()
    except OSError as error:
        raise EvidenceLifecycleError(f"run reservation cleanup failed: {error}") from error
    if os.path.lexists(reservation_path):
        raise EvidenceLifecycleError("run reservation still exists after cleanup")


def _reservation_bytes(task_root: Path, review_run_id: str) -> bytes:
    return canonical_json_bytes(
        {
            "resolved_root": str(task_root),
            "review_run_id": review_run_id,
        }
    )


def _verify_workspace_identity(workspace: TaskWorkspace) -> None:
    if type(workspace) is not TaskWorkspace:
        raise EvidenceLifecycleError("cleanup requires an exact TaskWorkspace")
    parent = _require_existing_directory(workspace.transient_parent, "transient_parent")
    expected_root = parent / _RUNNER_DIRECTORY / workspace.review_run_id
    if not _same_path(workspace.root, expected_root):
        raise EvidenceLifecycleError("workspace root does not match its exact task path")
    _require_plain_directory(workspace.root, "task root")
    resolved_root = workspace.root.resolve(strict=True)
    if not _same_path(resolved_root, workspace.root):
        raise EvidenceLifecycleError("task root is path-aliased")
    if not _is_strict_descendant(resolved_root, parent):
        raise EvidenceLifecycleError("task root escapes transient_parent")

    expected_paths = (
        resolved_root / _OWNER_MARKER,
        *(resolved_root / name for name in _OWNED_DIRECTORIES),
    )
    actual_paths = (
        workspace.marker_path,
        workspace.inputs_path,
        workspace.response_working_path,
        workspace.synthetic_canaries_path,
    )
    if any(not _same_path(actual, expected) for actual, expected in zip(actual_paths, expected_paths)):
        raise EvidenceLifecycleError("workspace owned paths do not match the exact layout")
    if _is_reparse_point(workspace.marker_path) or not workspace.marker_path.is_file():
        raise EvidenceLifecycleError("workspace ownership marker is missing or ambiguous")
    try:
        marker_bytes = workspace.marker_path.read_bytes()
        marker = json.loads(
            marker_bytes.decode("utf-8", errors="strict"),
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_non_json_number,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise EvidenceLifecycleError("workspace ownership marker is invalid") from error
    expected_marker = {
        "resolved_root": str(resolved_root),
        "review_run_id": workspace.review_run_id,
    }
    if marker != expected_marker or marker_bytes != canonical_json_bytes(expected_marker):
        raise EvidenceLifecycleError("workspace ownership marker does not match the task")
    for directory in actual_paths[1:]:
        _require_plain_directory(directory, "owned workspace directory")


def _verify_owned_tree(root: Path) -> None:
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        _require_resolved_descendant_or_same(current_path, root, "removable directory")
        for name in tuple(directories) + tuple(files):
            candidate = current_path / name
            if _is_reparse_point(candidate):
                raise EvidenceLifecycleError(
                    "removable tree contains a symlink or junction"
                )
            _require_resolved_descendant_or_same(candidate, root, "removable path")


def _remove_owned_tree(root: Path) -> None:
    boundary = Path(os.path.abspath(root))
    _remove_owned_directory(boundary, boundary)


def _remove_owned_directory(directory: Path, boundary: Path) -> None:
    _require_lexical_descendant_or_same(directory, boundary, "removable directory")
    directory_identity = _plain_directory_identity(directory, "removable directory")
    with os.scandir(directory) as iterator:
        entries = sorted(iterator, key=lambda entry: entry.name)
    if _plain_directory_identity(directory, "removable directory") != directory_identity:
        raise EvidenceLifecycleError("removable directory changed while it was inspected")

    for entry in entries:
        if _plain_directory_identity(directory, "removable directory") != directory_identity:
            raise EvidenceLifecycleError("removable directory changed during cleanup")
        candidate = directory / entry.name
        if not _same_path(candidate.parent, directory):
            raise EvidenceLifecycleError("removable entry is not an exact child")
        _require_lexical_descendant_or_same(candidate, boundary, "removable entry")
        entry_identity = _entry_identity_no_follow(candidate)
        if stat.S_ISDIR(entry_identity[2]):
            if _plain_directory_identity(directory, "removable directory") != directory_identity:
                raise EvidenceLifecycleError(
                    "removable directory changed before child recursion"
                )
            if _entry_identity_no_follow(candidate) != entry_identity:
                raise EvidenceLifecycleError(
                    "removable child directory changed before recursion"
                )
            _remove_owned_directory(candidate, boundary)
            continue
        if not stat.S_ISREG(entry_identity[2]):
            raise EvidenceLifecycleError(
                "removable entry is not a plain file or directory"
            )
        if _plain_directory_identity(directory, "removable directory") != directory_identity:
            raise EvidenceLifecycleError("removable directory changed before file cleanup")
        if _entry_identity_no_follow(candidate) != entry_identity:
            raise EvidenceLifecycleError("removable file changed before cleanup")
        os.unlink(candidate)
        if os.path.lexists(candidate):
            raise EvidenceLifecycleError("removable file still exists after cleanup")

    if _plain_directory_identity(directory, "removable directory") != directory_identity:
        raise EvidenceLifecycleError("removable directory changed before final cleanup")
    with os.scandir(directory) as iterator:
        if next(iterator, None) is not None:
            raise EvidenceLifecycleError("removable directory changed before final cleanup")
    os.rmdir(directory)
    if os.path.lexists(directory):
        raise EvidenceLifecycleError("removable directory still exists after cleanup")


def _plain_directory_identity(path: Path, label: str) -> tuple[int, int, int]:
    identity = _entry_identity_no_follow(path)
    if not stat.S_ISDIR(identity[2]):
        raise EvidenceLifecycleError(f"{label} is not a plain directory")
    return identity


def _entry_identity_no_follow(path: Path) -> tuple[int, int, int]:
    try:
        observed = path.lstat()
    except OSError as error:
        raise EvidenceLifecycleError("owned path cannot be inspected without following") from error
    reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(observed, "st_file_attributes", 0)
    if stat.S_ISLNK(observed.st_mode) or bool(attributes & reparse_attribute):
        raise EvidenceLifecycleError("owned path became a symlink or junction")
    return observed.st_dev, observed.st_ino, observed.st_mode


def _require_lexical_descendant_or_same(path: Path, root: Path, label: str) -> None:
    if not _same_path(path, root):
        try:
            path.relative_to(root)
        except ValueError as error:
            raise EvidenceLifecycleError(f"{label} escapes the exact task root") from error


def _capture_preserved_evidence(
    paths: Sequence[Path],
    *,
    task_root: Path,
) -> dict[str, str]:
    normalized = _normalize_path_sequence(paths, "preserved_evidence_paths")
    if not normalized:
        raise EvidenceLifecycleError("preserved evidence must be frozen before cleanup")
    states: dict[str, str] = {}
    for path in normalized:
        if _paths_overlap(path, task_root):
            raise EvidenceLifecycleError("preserved evidence overlaps the removable task root")
        if _is_reparse_point(path) or not path.is_file():
            raise EvidenceLifecycleError("preserved evidence must be an existing plain file")
        states[str(path)] = _path_state_sha256(path)
    return states


def _capture_sibling_states(
    paths: Sequence[Path],
    *,
    task_root: Path,
) -> dict[str, str]:
    normalized = _normalize_path_sequence(paths, "sibling_paths")
    states: dict[str, str] = {}
    for path in normalized:
        if _paths_overlap(path, task_root):
            raise EvidenceLifecycleError("sibling path overlaps the removable task root")
        if not os.path.lexists(path):
            raise EvidenceLifecycleError("declared sibling path is missing")
        states[str(path)] = _path_state_sha256(path)
    return states


def _verify_path_states_unchanged(states: dict[str, str], label: str) -> None:
    for path_text, expected_sha256 in states.items():
        path = Path(path_text)
        if not os.path.lexists(path):
            raise EvidenceLifecycleError(f"{label} path disappeared during cleanup")
        if _path_state_sha256(path) != expected_sha256:
            raise EvidenceLifecycleError(f"{label} path changed during cleanup")


def _normalize_path_sequence(paths: Sequence[Path], label: str) -> tuple[Path, ...]:
    if isinstance(paths, (str, bytes)):
        raise EvidenceLifecycleError(f"{label} must be a sequence of Paths")
    try:
        values = tuple(paths)
    except TypeError as error:
        raise EvidenceLifecycleError(f"{label} must be iterable") from error
    normalized: dict[str, Path] = {}
    for value in values:
        if not isinstance(value, Path):
            raise EvidenceLifecycleError(f"{label} must contain only Paths")
        if _is_reparse_point(value):
            raise EvidenceLifecycleError(f"{label} contains a symlink or junction")
        try:
            resolved = value.resolve(strict=True)
        except OSError as error:
            raise EvidenceLifecycleError(f"{label} contains a missing path") from error
        normalized.setdefault(os.path.normcase(str(resolved)), resolved)
    return tuple(normalized[key] for key in sorted(normalized))


def _path_state_sha256(path: Path) -> str:
    if _is_reparse_point(path):
        raise EvidenceLifecycleError("cannot hash a symlink or junction as owned state")
    resolved = path.resolve(strict=True)
    digest = hashlib.sha256()
    if resolved.is_file():
        content_length, content_sha256 = _file_content_commitment(resolved)
        _hash_manifest_entry(
            digest,
            entry_type=b"F",
            relative_path=b"",
            content_length=content_length,
            content_sha256=content_sha256,
        )
        return digest.hexdigest()
    if not resolved.is_dir():
        raise EvidenceLifecycleError("declared path is not a regular file or directory")
    empty_sha256 = hashlib.sha256(b"").digest()
    _hash_manifest_entry(
        digest,
        entry_type=b"D",
        relative_path=b"",
        content_length=0,
        content_sha256=empty_sha256,
    )
    for current, directories, files in os.walk(resolved, topdown=True, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        _require_resolved_descendant_or_same(current_path, resolved, "hashed directory")
        for name in directories:
            candidate = current_path / name
            if _is_reparse_point(candidate):
                raise EvidenceLifecycleError("hashed tree contains a symlink or junction")
            _require_resolved_descendant_or_same(candidate, resolved, "hashed directory")
            relative = candidate.relative_to(resolved).as_posix().encode("utf-8")
            _hash_manifest_entry(
                digest,
                entry_type=b"D",
                relative_path=relative,
                content_length=0,
                content_sha256=empty_sha256,
            )
        for name in files:
            candidate = current_path / name
            if _is_reparse_point(candidate):
                raise EvidenceLifecycleError("hashed tree contains a symlink or junction")
            _require_resolved_descendant_or_same(candidate, resolved, "hashed file")
            relative = candidate.relative_to(resolved).as_posix().encode("utf-8")
            content_length, content_sha256 = _file_content_commitment(candidate)
            _hash_manifest_entry(
                digest,
                entry_type=b"F",
                relative_path=relative,
                content_length=content_length,
                content_sha256=content_sha256,
            )
    return digest.hexdigest()


def _file_content_commitment(path: Path) -> tuple[int, bytes]:
    digest = hashlib.sha256()
    length = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            length += len(chunk)
    return length, digest.digest()


def _hash_manifest_entry(
    digest,
    *,
    entry_type: bytes,
    relative_path: bytes,
    content_length: int,
    content_sha256: bytes,
) -> None:
    digest.update(entry_type)
    digest.update(len(relative_path).to_bytes(8, byteorder="big", signed=False))
    digest.update(relative_path)
    digest.update(content_length.to_bytes(8, byteorder="big", signed=False))
    digest.update(len(content_sha256).to_bytes(2, byteorder="big", signed=False))
    digest.update(content_sha256)


def _require_existing_directory(path: Path, label: str) -> Path:
    if not isinstance(path, Path):
        raise EvidenceLifecycleError(f"{label} must be a Path")
    if not os.path.lexists(path):
        raise EvidenceLifecycleError(f"{label} must already exist")
    _require_plain_directory(path, label)
    try:
        return path.resolve(strict=True)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} cannot be resolved") from error


def _require_plain_directory(path: Path, label: str) -> None:
    if _is_reparse_point(path) or not path.is_dir():
        raise EvidenceLifecycleError(f"{label} must be a plain directory")


def _require_resolved_descendant_or_same(path: Path, root: Path, label: str) -> None:
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} cannot be resolved") from error
    if not _same_path(resolved, root) and not _is_strict_descendant(resolved, root):
        raise EvidenceLifecycleError(f"{label} escapes its declared root")


def _require_safe_path_component(value: object, label: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) > _MAX_PATH_COMPONENT_LENGTH
        or _SAFE_PATH_COMPONENT.fullmatch(value) is None
        or value.split(".", 1)[0] in _WINDOWS_RESERVED_PATH_STEMS
    ):
        raise EvidenceLifecycleError(f"{label} is not a safe path component")


def _is_reparse_point(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except AttributeError:
        attributes = 0
    except OSError:
        return False
    reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & reparse_attribute)


def _reject_reparse_components(path: Path, label: str) -> None:
    for component in (*reversed(path.parents), path):
        if os.path.lexists(component) and _is_reparse_point(component):
            raise EvidenceLifecycleError(f"{label} contains a symlink or junction")


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _is_strict_descendant(path: Path, root: Path) -> bool:
    if _same_path(path, root):
        return False
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _paths_overlap(left: Path, right: Path) -> bool:
    return (
        _same_path(left, right)
        or _is_strict_descendant(left, right)
        or _is_strict_descendant(right, left)
    )


def _object_without_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceLifecycleError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_non_json_number(value: str) -> object:
    raise EvidenceLifecycleError(f"non-JSON numeric constant: {value}")
