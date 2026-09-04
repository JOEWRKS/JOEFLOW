"""Immutable evidence, exact task cleanup, and repository no-mutation guards."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
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
_WINDOWS_FILE_READ_ATTRIBUTES = 0x00000080
_WINDOWS_DELETE = 0x00010000
_WINDOWS_FILE_SHARE_READ = 0x00000001
_WINDOWS_FILE_SHARE_WRITE = 0x00000002
_WINDOWS_OPEN_EXISTING = 3
_WINDOWS_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
_WINDOWS_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_WINDOWS_FILE_DISPOSITION_INFO_CLASS = 4
_WINDOWS_FILE_ID_INFO_CLASS = 0x12
_WINDOWS_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
_WINDOWS_KERNEL32 = None
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


class EvidenceClaimConflict(EvidenceLifecycleError):
    """A one-shot durable evidence claim already exists or is in progress."""


@dataclass(frozen=True)
class _WindowsFileIdentity:
    volume_serial_number: int
    file_id: bytes


class _WindowsFileId128(ctypes.Structure):
    _fields_ = (("identifier", ctypes.c_ubyte * 16),)


class _WindowsFileIdInfo(ctypes.Structure):
    _fields_ = (
        ("volume_serial_number", ctypes.c_ulonglong),
        ("file_id", _WindowsFileId128),
    )


class _WindowsFileDispositionInfo(ctypes.Structure):
    _fields_ = (("delete_file", ctypes.c_ubyte),)


@dataclass(frozen=True)
class _RunReservation:
    path: Path
    path_identity: tuple[int, int, int]
    directory: Path
    directory_identity: tuple[int, int, int]
    directory_created: bool


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


@dataclass(frozen=True)
class ResolvedPathTopology:
    repository_root: Path
    evidence_root: Path
    transient_parent: Path


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
    def create(
        cls,
        transient_parent: Path,
        review_run_id: str,
        *,
        repository_root: Path,
        source_snapshot: SourceSnapshot | None = None,
    ) -> "TaskWorkspace":
        """Create one new marker-owned workspace without reusing prior output."""

        repository = _require_existing_directory(repository_root, "repository_root")
        if source_snapshot is None:
            source_snapshot = _capture_source_snapshot(repository)
        else:
            verify_source_unchanged(source_snapshot, repository)
        parent = _require_existing_directory(transient_parent, "transient_parent")
        _require_safe_path_component(review_run_id, "review_run_id")
        runner_parent = parent / _RUNNER_DIRECTORY
        runner_parent_created = False
        runner_parent_identity: tuple[int, int, int] | None = None
        task_root = runner_parent / review_run_id
        reservation: _RunReservation | None = None
        task_root_identity: tuple[int, int, int] | None = None
        try:
            if os.path.lexists(runner_parent):
                _require_plain_directory(runner_parent, "runner workspace parent")
                if not _same_path(runner_parent.resolve(strict=True), runner_parent):
                    raise EvidenceLifecycleError("runner workspace parent is path-aliased")
            else:
                runner_parent_identity = _create_plain_directory_transactionally(
                    runner_parent,
                    "new runner workspace parent",
                )
                runner_parent_created = True
            if not _is_strict_descendant(runner_parent.resolve(strict=True), parent):
                raise EvidenceLifecycleError(
                    "runner workspace parent escapes transient_parent"
                )
            if os.path.lexists(task_root):
                raise EvidenceLifecycleError(
                    "review workspace already exists; prior execution state is ambiguous"
                )
            reservation = _create_run_reservation(
                runner_parent,
                task_root,
                review_run_id,
            )
            task_root_identity = _create_plain_directory_transactionally(
                task_root,
                "new review workspace",
            )
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
        except Exception as setup_error:
            try:
                _rollback_workspace_setup(
                    runner_parent,
                    runner_parent_created=runner_parent_created,
                    runner_parent_identity=runner_parent_identity,
                    reservation=reservation,
                    task_root=task_root,
                    task_root_identity=task_root_identity,
                )
            except EvidenceLifecycleError as rollback_error:
                raise EvidenceLifecycleError(
                    f"workspace setup failed: {setup_error}; rollback failed: {rollback_error}"
                ) from setup_error
            raise

        return cls(
            transient_parent=parent,
            review_run_id=review_run_id,
            root=resolved_root,
            marker_path=marker_path,
            inputs_path=owned_paths[0],
            response_working_path=owned_paths[1],
            synthetic_canaries_path=owned_paths[2],
            repository_root=repository,
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
        _complete_run_reservation(self.root.parent, self.root, self.review_run_id)
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


def validate_runner_path_topology(
    repository_root: Path,
    evidence_root: Path,
    transient_parent: Path,
) -> ResolvedPathTopology:
    """Resolve the controller roots and reject every unsafe writable overlap."""

    repository = _resolve_topology_path(
        repository_root,
        "repository_root",
        must_exist=True,
    )
    evidence = _resolve_topology_path(evidence_root, "evidence_root")
    transient = _resolve_topology_path(transient_parent, "transient_parent")
    if _paths_overlap(repository, evidence):
        raise EvidenceLifecycleError("repository_root overlaps evidence_root")
    if _paths_overlap(repository, transient):
        raise EvidenceLifecycleError("repository_root overlaps transient_parent")
    if _paths_overlap(evidence, transient):
        raise EvidenceLifecycleError("evidence_root overlaps transient_parent")
    return ResolvedPathTopology(
        repository_root=repository,
        evidence_root=evidence,
        transient_parent=transient,
    )


def atomic_freeze_evidence(content: bytes, target_path: Path) -> Path:
    """Persist immutable bytes without overwriting an intervening publication."""

    return _atomic_publish_evidence(
        content,
        target_path,
        existing_is_conflict=False,
    )


def atomic_claim_evidence(content: bytes, target_path: Path) -> Path:
    """Acquire one permanent claim; an identical existing claim still conflicts."""

    return _atomic_publish_evidence(
        content,
        target_path,
        existing_is_conflict=True,
    )


def _atomic_publish_evidence(
    content: bytes,
    target_path: Path,
    *,
    existing_is_conflict: bool,
) -> Path:
    if type(content) is not bytes:
        raise EvidenceLifecycleError("evidence content must be exact bytes")
    if not isinstance(target_path, Path):
        raise EvidenceLifecycleError("target_path must be a Path")
    if not target_path.name:
        raise EvidenceLifecycleError("target_path must name an evidence file")
    target = Path(os.path.abspath(target_path))
    _reject_reparse_components(target, "evidence target")
    if os.path.lexists(target):
        return _resolve_existing_publication(
            target,
            content,
            existing_is_conflict=existing_is_conflict,
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    _reject_reparse_components(target, "evidence target")
    _require_plain_directory(target.parent, "evidence parent")
    parent_identity = _plain_directory_identity(target.parent, "evidence parent")
    publication_lock = target.with_name(f".{target.name}.freeze.lock")
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    lock_descriptor = None
    temporary_descriptor = None
    try:
        _require_directory_identity(
            target.parent,
            parent_identity,
            "evidence parent before publication lock",
        )
        try:
            lock_descriptor = _open_delete_on_close_file(
                publication_lock,
                "evidence publication lock",
            )
        except FileExistsError as error:
            if existing_is_conflict:
                raise EvidenceClaimConflict(
                    "one-shot evidence claim is already being acquired"
                ) from error
            raise EvidenceLifecycleError(
                "evidence publication is already reserved by another writer"
            ) from error
        lock_identity = _opened_plain_file_identity(
            lock_descriptor,
            "evidence publication lock",
        )
        _write_descriptor_exact(
            lock_descriptor,
            uuid.uuid4().hex.encode("ascii"),
            "evidence publication lock",
        )
        _verify_opened_file_path(
            publication_lock,
            lock_identity,
            "evidence publication lock",
        )
        _require_directory_identity(
            target.parent,
            parent_identity,
            "evidence parent after publication lock",
        )
        if os.path.lexists(target):
            return _resolve_existing_publication(
                target,
                content,
                existing_is_conflict=existing_is_conflict,
            )
        temporary_descriptor = _open_delete_on_close_file(
            temporary,
            "evidence temporary file",
        )
        temporary_identity = _opened_plain_file_identity(
            temporary_descriptor,
            "evidence temporary file",
        )
        _write_descriptor_exact(
            temporary_descriptor,
            content,
            "evidence temporary file",
        )
        _verify_opened_file_path(
            temporary,
            temporary_identity,
            "evidence temporary file",
        )
        _reject_reparse_components(target, "evidence target before publication")
        _require_directory_identity(
            target.parent,
            parent_identity,
            "evidence parent immediately before publication",
        )
        try:
            os.link(temporary, target)
        except FileExistsError:
            _require_directory_identity(
                target.parent,
                parent_identity,
                "evidence parent after publication conflict",
            )
            return _resolve_existing_publication(
                target,
                content,
                existing_is_conflict=existing_is_conflict,
            )
        except OSError as error:
            raise EvidenceLifecycleError(
                f"atomic no-clobber evidence publication failed: {error}"
            ) from error
        _require_directory_identity(
            target.parent,
            parent_identity,
            "evidence parent immediately after publication",
        )
        if _plain_file_identity(target, "frozen evidence") != temporary_identity[:2]:
            raise EvidenceLifecycleError("frozen evidence identity changed after publication")
        observed = target.read_bytes()
        if observed != content or sha256_bytes(observed) != sha256_bytes(content):
            raise EvidenceLifecycleError(
                "frozen evidence readback does not match exact bytes"
            )
        return target
    finally:
        _close_delete_on_close_file(temporary_descriptor, "evidence temporary file")
        _close_delete_on_close_file(lock_descriptor, "evidence publication lock")


def _resolve_existing_publication(
    target: Path,
    expected: bytes,
    *,
    existing_is_conflict: bool,
) -> Path:
    if existing_is_conflict:
        if _is_reparse_point(target) or not target.is_file():
            raise EvidenceLifecycleError(
                "one-shot evidence claim target is not a plain file"
            )
        raise EvidenceClaimConflict("one-shot evidence claim already exists")
    return _read_existing_immutable_evidence(target, expected)


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
            ["git", "--no-optional-locks", *arguments],
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


def _open_delete_on_close_file(path: Path, label: str) -> int:
    temporary_flag = getattr(os, "O_TEMPORARY", None)
    if temporary_flag is None:
        raise EvidenceLifecycleError(
            f"{label} requires platform delete-on-close support"
        )
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | temporary_flag
    flags |= getattr(os, "O_BINARY", 0)
    try:
        return os.open(path, flags, 0o600)
    except OSError as error:
        if isinstance(error, FileExistsError):
            raise
        raise EvidenceLifecycleError(f"{label} cannot be created exclusively: {error}") from error


def _open_existing_delete_on_close_file(path: Path, label: str) -> int:
    temporary_flag = getattr(os, "O_TEMPORARY", None)
    if temporary_flag is None:
        raise EvidenceLifecycleError(
            f"{label} requires platform delete-on-close support"
        )
    flags = os.O_RDONLY | temporary_flag | getattr(os, "O_BINARY", 0)
    try:
        return os.open(path, flags)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} cannot be opened safely: {error}") from error


def _opened_plain_file_identity(descriptor: int, label: str) -> tuple[int, int, int]:
    try:
        observed = os.fstat(descriptor)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} handle cannot be inspected") from error
    if not stat.S_ISREG(observed.st_mode):
        raise EvidenceLifecycleError(f"{label} handle is not a plain file")
    return observed.st_dev, observed.st_ino, observed.st_mode


def _write_descriptor_exact(descriptor: int, content: bytes, label: str) -> None:
    offset = 0
    while offset < len(content):
        try:
            written = os.write(descriptor, content[offset:])
        except OSError as error:
            raise EvidenceLifecycleError(f"{label} write failed: {error}") from error
        if written <= 0:
            raise EvidenceLifecycleError(f"{label} write was incomplete")
        offset += written
    try:
        os.fsync(descriptor)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} fsync failed: {error}") from error


def _verify_opened_file_path(
    path: Path,
    expected_identity: tuple[int, int, int],
    label: str,
) -> None:
    observed = _entry_identity_no_follow(path)
    if observed != expected_identity or not stat.S_ISREG(observed[2]):
        raise EvidenceLifecycleError(f"{label} path no longer names its opened file")


def _close_delete_on_close_file(descriptor: int | None, label: str) -> None:
    if descriptor is None:
        return
    try:
        os.close(descriptor)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} handle cleanup failed: {error}") from error


def _require_directory_identity(
    path: Path,
    expected_identity: tuple[int, int, int],
    label: str,
) -> None:
    if _plain_directory_identity(path, label) != expected_identity:
        raise EvidenceLifecycleError(f"{label} identity changed")


def _create_plain_directory_transactionally(
    path: Path,
    label: str,
) -> tuple[int, int, int]:
    if os.path.lexists(path):
        raise EvidenceLifecycleError(f"{label} already exists")
    path.mkdir()
    identity: tuple[int, int, int] | None = None
    try:
        identity = _entry_identity_no_follow(path)
        if not stat.S_ISDIR(identity[2]):
            raise EvidenceLifecycleError(f"{label} is not a plain directory")
        _require_directory_identity(path, identity, label)
        return identity
    except Exception as setup_error:
        try:
            if identity is None:
                identity = _entry_identity_no_follow(path)
            if not stat.S_ISDIR(identity[2]):
                raise EvidenceLifecycleError(
                    f"{label} rollback target is not a plain directory"
                )
            _remove_created_empty_directory(
                path,
                identity,
                f"incomplete {label}",
            )
        except EvidenceLifecycleError as cleanup_error:
            raise EvidenceLifecycleError(
                f"{label} setup failed: {setup_error}; "
                f"cleanup failed: {cleanup_error}"
            ) from setup_error
        if os.path.lexists(path):
            raise EvidenceLifecycleError(
                f"{label} setup failed: {setup_error}; cleanup left the path present"
            ) from setup_error
        raise


def _create_run_reservation(
    runner_parent: Path,
    task_root: Path,
    review_run_id: str,
) -> _RunReservation:
    reservation_directory = runner_parent / _RESERVATION_DIRECTORY
    directory_created = False
    if os.path.lexists(reservation_directory):
        _require_plain_directory(reservation_directory, "run reservation directory")
        directory_identity = _plain_directory_identity(
            reservation_directory,
            "run reservation directory",
        )
    else:
        directory_identity = _create_plain_directory_transactionally(
            reservation_directory,
            "run reservation directory",
        )
        directory_created = True
    reservation_path = reservation_directory / f"{review_run_id}.json"
    content = _reservation_bytes(task_root, review_run_id)
    reservation_created = False
    path_identity: tuple[int, int, int] | None = None
    try:
        _require_resolved_descendant_or_same(
            reservation_directory,
            runner_parent,
            "run reservation directory",
        )
        _require_directory_identity(
            reservation_directory,
            directory_identity,
            "run reservation directory",
        )
        if os.path.lexists(reservation_path):
            raise EvidenceLifecycleError(
                "review run is reserved by a prior or active execution"
            )
        try:
            with reservation_path.open("xb") as stream:
                reservation_created = True
                path_identity = _opened_plain_file_identity(
                    stream.fileno(),
                    "run reservation",
                )
                _verify_opened_file_path(
                    reservation_path,
                    path_identity,
                    "run reservation",
                )
                _write_descriptor_exact(
                    stream.fileno(),
                    content,
                    "run reservation",
                )
        except FileExistsError as error:
            raise EvidenceLifecycleError(
                "review run is reserved by a concurrent execution"
            ) from error
        if reservation_path.read_bytes() != content:
            raise EvidenceLifecycleError("run reservation readback changed")
        if path_identity is None:
            raise EvidenceLifecycleError("run reservation identity was not captured")
        _verify_opened_file_path(
            reservation_path,
            path_identity,
            "run reservation",
        )
    except Exception as setup_error:
        cleanup_failures: list[str] = []
        if reservation_created:
            try:
                if path_identity is None:
                    path_identity = _entry_identity_no_follow(reservation_path)
                if not stat.S_ISREG(path_identity[2]):
                    raise EvidenceLifecycleError(
                        "incomplete run reservation is not a plain file"
                    )
                _remove_created_file(
                    reservation_path,
                    path_identity,
                    reservation_directory,
                    directory_identity,
                    "incomplete run reservation",
                )
            except EvidenceLifecycleError as cleanup_error:
                cleanup_failures.append(str(cleanup_error))
        if directory_created:
            try:
                _remove_created_empty_directory(
                    reservation_directory,
                    directory_identity,
                    "incomplete run reservation directory",
                )
            except EvidenceLifecycleError as cleanup_error:
                cleanup_failures.append(str(cleanup_error))
        expected_absent = []
        if reservation_created:
            expected_absent.append(reservation_path)
        if directory_created:
            expected_absent.append(reservation_directory)
        for path in expected_absent:
            if os.path.lexists(path):
                cleanup_failures.append(
                    f"incomplete run reservation setup path still exists: {path}"
                )
        if cleanup_failures:
            raise EvidenceLifecycleError(
                f"run reservation setup failed: {setup_error}; cleanup failed: "
                + "; ".join(cleanup_failures)
            ) from setup_error
        raise
    return _RunReservation(
        path=reservation_path,
        path_identity=path_identity,
        directory=reservation_directory,
        directory_identity=directory_identity,
        directory_created=directory_created,
    )


def _rollback_workspace_setup(
    runner_parent: Path,
    *,
    runner_parent_created: bool,
    runner_parent_identity: tuple[int, int, int] | None,
    reservation: _RunReservation | None,
    task_root: Path,
    task_root_identity: tuple[int, int, int] | None,
) -> None:
    failures: list[str] = []
    if task_root_identity is not None:
        try:
            _remove_owned_directory(
                task_root,
                task_root,
                expected_identity=task_root_identity,
            )
        except EvidenceLifecycleError as error:
            failures.append(str(error))
    if reservation is not None:
        try:
            _remove_created_file(
                reservation.path,
                reservation.path_identity,
                reservation.directory,
                reservation.directory_identity,
                "failed workspace run reservation",
            )
        except EvidenceLifecycleError as error:
            failures.append(str(error))
        if reservation.directory_created:
            try:
                _remove_created_empty_directory(
                    reservation.directory,
                    reservation.directory_identity,
                    "failed workspace reservation directory",
                )
            except EvidenceLifecycleError as error:
                failures.append(str(error))
    if runner_parent_created and runner_parent_identity is not None:
        try:
            _remove_created_empty_directory(
                runner_parent,
                runner_parent_identity,
                "failed workspace runner parent",
            )
        except EvidenceLifecycleError as error:
            failures.append(str(error))
    expected_absent = [task_root]
    if reservation is not None:
        expected_absent.append(reservation.path)
        if reservation.directory_created:
            expected_absent.append(reservation.directory)
    if runner_parent_created:
        expected_absent.append(runner_parent)
    for path in expected_absent:
        if os.path.lexists(path):
            failures.append(f"failed workspace setup path still exists: {path}")
    if failures:
        raise EvidenceLifecycleError("; ".join(failures))


def _remove_created_file(
    path: Path,
    expected_identity: tuple[int, int, int],
    parent: Path,
    parent_identity: tuple[int, int, int],
    label: str,
) -> None:
    _require_directory_identity(parent, parent_identity, f"{label} parent")
    if _entry_identity_no_follow(path) != expected_identity:
        raise EvidenceLifecycleError(f"{label} identity changed")
    quarantined = _quarantine_owned_entry(
        path,
        parent,
        parent_identity,
        expected_identity,
        label,
    )
    _unlink_quarantined_file(
        quarantined,
        expected_identity,
        parent,
        parent_identity,
    )
    if os.path.lexists(path) or os.path.lexists(quarantined):
        raise EvidenceLifecycleError(f"{label} still exists after rollback")


def _remove_created_empty_directory(
    path: Path,
    expected_identity: tuple[int, int, int],
    label: str,
) -> None:
    _require_directory_identity(path, expected_identity, label)
    with os.scandir(path) as iterator:
        if next(iterator, None) is not None:
            raise EvidenceLifecycleError(f"{label} is not empty")
    windows_identity = _capture_windows_directory_identity(path)
    _remove_empty_windows_directory_by_handle(
        path,
        expected_identity,
        windows_identity,
    )


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


def _complete_run_reservation(
    runner_parent: Path,
    task_root: Path,
    review_run_id: str,
) -> None:
    """Freeze completion while retaining the canonical no-clobber blocker."""

    reservation_path = _verify_run_reservation(
        runner_parent,
        task_root,
        review_run_id,
    )
    reservation_directory = reservation_path.parent
    directory_identity = _plain_directory_identity(
        reservation_directory,
        "run reservation directory",
    )
    reservation_identity = _plain_file_identity(
        reservation_path,
        "run reservation",
    )
    content = _reservation_bytes(task_root, review_run_id)
    _require_directory_identity(
        reservation_directory,
        directory_identity,
        "run reservation directory before completion",
    )
    completion_path = reservation_path.with_name(
        f"{reservation_path.stem}.completed.json"
    )
    atomic_freeze_evidence(
        canonical_json_bytes(
            {
                "reservation_sha256": sha256_bytes(content),
                "review_run_id": review_run_id,
                "status": "COMPLETED",
            }
        ),
        completion_path,
    )
    _require_directory_identity(
        reservation_directory,
        directory_identity,
        "run reservation directory after completion",
    )
    if _plain_file_identity(reservation_path, "run reservation") != reservation_identity:
        raise EvidenceLifecycleError("canonical run reservation identity changed")
    if reservation_path.read_bytes() != content:
        raise EvidenceLifecycleError("canonical run reservation bytes changed")


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


def _windows_kernel32():
    global _WINDOWS_KERNEL32
    if os.name != "nt":
        raise EvidenceLifecycleError(
            "identity-conditional directory deletion requires Windows"
        )
    if _WINDOWS_KERNEL32 is None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.argtypes = (
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        )
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.GetFileInformationByHandleEx.argtypes = (
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
        )
        kernel32.GetFileInformationByHandleEx.restype = wintypes.BOOL
        kernel32.SetFileInformationByHandle.argtypes = (
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
        )
        kernel32.SetFileInformationByHandle.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL
        _WINDOWS_KERNEL32 = kernel32
    return _WINDOWS_KERNEL32


def _win32_lifecycle_error(operation: str) -> EvidenceLifecycleError:
    return EvidenceLifecycleError(
        f"{operation} failed with Win32 error {ctypes.get_last_error()}"
    )


def _open_windows_directory_delete_handle(directory: Path) -> int:
    kernel32 = _windows_kernel32()
    handle = kernel32.CreateFileW(
        str(directory),
        _WINDOWS_FILE_READ_ATTRIBUTES | _WINDOWS_DELETE,
        _WINDOWS_FILE_SHARE_READ | _WINDOWS_FILE_SHARE_WRITE,
        None,
        _WINDOWS_OPEN_EXISTING,
        (
            _WINDOWS_FILE_FLAG_BACKUP_SEMANTICS
            | _WINDOWS_FILE_FLAG_OPEN_REPARSE_POINT
        ),
        None,
    )
    if handle in (None, _WINDOWS_INVALID_HANDLE_VALUE):
        raise _win32_lifecycle_error("opening exact removable directory handle")
    return handle


def _windows_directory_identity_from_handle(handle: int) -> _WindowsFileIdentity:
    information = _WindowsFileIdInfo()
    kernel32 = _windows_kernel32()
    if not kernel32.GetFileInformationByHandleEx(
        handle,
        _WINDOWS_FILE_ID_INFO_CLASS,
        ctypes.byref(information),
        ctypes.sizeof(information),
    ):
        raise _win32_lifecycle_error("reading removable directory handle identity")
    return _WindowsFileIdentity(
        volume_serial_number=information.volume_serial_number,
        file_id=bytes(information.file_id.identifier),
    )


def _close_windows_handle(handle: int, label: str) -> None:
    if not _windows_kernel32().CloseHandle(handle):
        raise _win32_lifecycle_error(f"closing {label}")


def _capture_windows_directory_identity(directory: Path) -> _WindowsFileIdentity:
    handle = _open_windows_directory_delete_handle(directory)
    try:
        return _windows_directory_identity_from_handle(handle)
    finally:
        _close_windows_handle(handle, "removable directory identity handle")


def _remove_empty_windows_directory_by_handle(
    directory: Path,
    expected_path_identity: tuple[int, int, int],
    expected_windows_identity: _WindowsFileIdentity,
) -> None:
    handle = _open_windows_directory_delete_handle(directory)
    try:
        observed_windows_identity = _windows_directory_identity_from_handle(handle)
        if observed_windows_identity != expected_windows_identity:
            raise EvidenceLifecycleError(
                "removable directory object changed before handle-pinned deletion"
            )
        if _plain_directory_identity(
            directory,
            "handle-pinned removable directory",
        ) != expected_path_identity:
            raise EvidenceLifecycleError(
                "removable directory path changed before handle-pinned deletion"
            )
        with os.scandir(directory) as iterator:
            if next(iterator, None) is not None:
                raise EvidenceLifecycleError(
                    "handle-pinned removable directory is not empty"
                )
        disposition = _WindowsFileDispositionInfo(delete_file=1)
        if not _windows_kernel32().SetFileInformationByHandle(
            handle,
            _WINDOWS_FILE_DISPOSITION_INFO_CLASS,
            ctypes.byref(disposition),
            ctypes.sizeof(disposition),
        ):
            raise _win32_lifecycle_error(
                "marking exact removable directory handle for deletion"
            )
    finally:
        _close_windows_handle(handle, "exact removable directory delete handle")
    if os.path.lexists(directory):
        raise EvidenceLifecycleError(
            "handle-pinned removable directory still exists after cleanup"
        )


def _remove_owned_tree(root: Path) -> None:
    boundary = Path(os.path.abspath(root))
    root_identity = _plain_directory_identity(boundary, "removable task root")
    _remove_owned_directory(boundary, boundary, expected_identity=root_identity)


def _remove_owned_directory(
    directory: Path,
    boundary: Path,
    *,
    expected_identity: tuple[int, int, int] | None = None,
) -> None:
    _require_lexical_descendant_or_same(directory, boundary, "removable directory")
    directory_identity = _plain_directory_identity(directory, "removable directory")
    if expected_identity is not None and directory_identity != expected_identity:
        raise EvidenceLifecycleError("removable directory ownership changed before recursion")
    windows_identity = _capture_windows_directory_identity(directory)
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
            quarantined = _quarantine_owned_entry(
                candidate,
                directory,
                directory_identity,
                entry_identity,
                "removable child directory",
            )
            _remove_owned_directory(
                quarantined,
                boundary,
                expected_identity=entry_identity,
            )
            continue
        if not stat.S_ISREG(entry_identity[2]):
            raise EvidenceLifecycleError(
                "removable entry is not a plain file or directory"
            )
        if _plain_directory_identity(directory, "removable directory") != directory_identity:
            raise EvidenceLifecycleError("removable directory changed before file cleanup")
        if _entry_identity_no_follow(candidate) != entry_identity:
            raise EvidenceLifecycleError("removable file changed before cleanup")
        quarantined = _quarantine_owned_entry(
            candidate,
            directory,
            directory_identity,
            entry_identity,
            "removable file",
        )
        _unlink_quarantined_file(
            quarantined,
            entry_identity,
            directory,
            directory_identity,
        )

    if _plain_directory_identity(directory, "removable directory") != directory_identity:
        raise EvidenceLifecycleError("removable directory changed before final cleanup")
    with os.scandir(directory) as iterator:
        if next(iterator, None) is not None:
            raise EvidenceLifecycleError("removable directory changed before final cleanup")
    _remove_empty_windows_directory_by_handle(
        directory,
        directory_identity,
        windows_identity,
    )


def _quarantine_owned_entry(
    candidate: Path,
    parent: Path,
    parent_identity: tuple[int, int, int],
    expected_identity: tuple[int, int, int],
    label: str,
) -> Path:
    _require_directory_identity(parent, parent_identity, f"{label} parent")
    if _entry_identity_no_follow(candidate) != expected_identity:
        raise EvidenceLifecycleError(f"{label} changed before quarantine")
    quarantine = candidate.with_name(
        f".{candidate.name}.{uuid.uuid4().hex}.cleanup"
    )
    if os.path.lexists(quarantine):
        raise EvidenceLifecycleError(f"{label} quarantine path already exists")
    try:
        os.rename(candidate, quarantine)
    except OSError as error:
        raise EvidenceLifecycleError(f"{label} quarantine move failed: {error}") from error
    _require_directory_identity(parent, parent_identity, f"{label} parent after quarantine")
    if _entry_identity_no_follow(quarantine) != expected_identity:
        raise EvidenceLifecycleError(f"{label} quarantine ownership is ambiguous")
    if os.path.lexists(candidate):
        raise EvidenceLifecycleError(f"{label} source reappeared after quarantine")
    return quarantine


def _unlink_quarantined_file(
    path: Path,
    expected_identity: tuple[int, int, int],
    parent: Path,
    parent_identity: tuple[int, int, int],
) -> None:
    guard_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.delete-guard")
    if os.path.lexists(guard_path):
        raise EvidenceLifecycleError("removable file delete guard already exists")
    try:
        os.link(path, guard_path)
    except OSError as error:
        raise EvidenceLifecycleError(f"removable file guard creation failed: {error}") from error
    guard_descriptor = None
    try:
        guard_descriptor = _open_existing_delete_on_close_file(
            guard_path,
            "removable file delete guard",
        )
        guard_before = os.fstat(guard_descriptor)
        guard_identity = (guard_before.st_dev, guard_before.st_ino, guard_before.st_mode)
        if guard_identity != expected_identity:
            raise EvidenceLifecycleError("removable file changed before guarded cleanup")
        _require_directory_identity(parent, parent_identity, "removable file parent")
        if _entry_identity_no_follow(path) != expected_identity:
            raise EvidenceLifecycleError("removable file changed before guarded unlink")
        try:
            os.unlink(path)
        except OSError as error:
            raise EvidenceLifecycleError(f"removable file unlink failed: {error}") from error
        guard_after = os.fstat(guard_descriptor)
        if guard_after.st_nlink != guard_before.st_nlink - 1:
            raise EvidenceLifecycleError("removable file substitution detected during unlink")
        if os.path.lexists(path):
            raise EvidenceLifecycleError("removable file still exists after cleanup")
    finally:
        _close_delete_on_close_file(
            guard_descriptor,
            "removable file delete guard",
        )


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


def _resolve_topology_path(
    path: Path,
    label: str,
    *,
    must_exist: bool = False,
) -> Path:
    if not isinstance(path, Path):
        raise EvidenceLifecycleError(f"{label} must be a Path")
    if not path.is_absolute():
        raise EvidenceLifecycleError(f"{label} must be absolute")
    try:
        absolute = Path(os.path.abspath(path))
    except (OSError, ValueError) as error:
        raise EvidenceLifecycleError(f"{label} cannot be normalized") from error
    _reject_reparse_components(absolute, label)

    existing_ancestor = absolute
    missing_components: list[str] = []
    while not os.path.lexists(existing_ancestor):
        parent = existing_ancestor.parent
        if _same_path(parent, existing_ancestor) or not existing_ancestor.name:
            raise EvidenceLifecycleError(
                f"{label} has no safely resolvable existing ancestor"
            )
        missing_components.append(existing_ancestor.name)
        existing_ancestor = parent
    _require_plain_directory(existing_ancestor, f"{label} existing ancestor")
    try:
        resolved_ancestor = existing_ancestor.resolve(strict=True)
    except OSError as error:
        raise EvidenceLifecycleError(
            f"{label} existing ancestor cannot be resolved"
        ) from error
    if must_exist and missing_components:
        raise EvidenceLifecycleError(f"{label} must already exist")

    resolved = resolved_ancestor.joinpath(*reversed(missing_components))
    return Path(os.path.normpath(resolved))


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
