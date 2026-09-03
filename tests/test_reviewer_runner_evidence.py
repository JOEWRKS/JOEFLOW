import base64
import dataclasses
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.identity import (  # noqa: E402
    BackendIdentity,
    InputCommitment,
    RunIdentity,
    RunnerState,
    build_runner_receipt,
    canonical_json_bytes,
    receipt_document,
    sha256_bytes,
)
from reviewer_runner.request import (  # noqa: E402
    InputArtifact,
    build_canonical_request,
)

if importlib.util.find_spec("reviewer_runner.evidence") is None:
    _EVIDENCE_IMPORT_ERROR = ImportError("reviewer_runner.evidence is absent")
else:
    from reviewer_runner import evidence as evidence_module  # noqa: E402
    from reviewer_runner.evidence import (  # noqa: E402
        CleanupResult,
        SourceSnapshot,
        TaskWorkspace,
        atomic_freeze_evidence,
        capture_source_snapshot,
        load_used_provider_request_ids,
        verify_source_unchanged,
    )
    _EVIDENCE_IMPORT_ERROR = None


def _git(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _tree_bytes_sha256(path: Path) -> str:
    resolved = path.resolve(strict=True)
    manifest = []
    if resolved.is_file():
        content = resolved.read_bytes()
        manifest.append(
            {
                "byte_count": len(content),
                "content_sha256": hashlib.sha256(content).hexdigest(),
                "path": "",
                "type": "file",
            }
        )
        return hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
    manifest.append({"path": "", "type": "directory"})
    for current, directories, files in os.walk(resolved, topdown=True, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        for name in directories:
            relative = (current_path / name).relative_to(resolved).as_posix()
            manifest.append({"path": relative, "type": "directory"})
        for name in files:
            candidate = current_path / name
            relative = candidate.relative_to(resolved).as_posix()
            content = candidate.read_bytes()
            manifest.append(
                {
                    "byte_count": len(content),
                    "content_sha256": hashlib.sha256(content).hexdigest(),
                    "path": relative,
                    "type": "file",
                }
            )
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _receipt_bytes(provider_request_id: str, review_run_id: str) -> bytes:
    package_digest = sha256_bytes(b"package")
    run_identity = RunIdentity(
        semantic_review_contract_version="joewrks.semantic-review/1.0",
        package_schema_version="joewrks.semantic-review-input/1.0",
        package_digest=package_digest,
        source_action_contract_hash=sha256_bytes(b"action-contract"),
        source_definition_digest=sha256_bytes(b"definition"),
        reviewer_id="reviewer-001",
        review_run_id=review_run_id,
        context_id="context-001",
        cohort_id=None,
        case_id=None,
    )
    backend_identity = BackendIdentity(
        backend_kind="STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
        adapter_id="external-inference-adapter",
        adapter_version="1.0.0",
        endpoint_identity="https://inference.example.invalid/v1",
        deployment_identity="reviewer-production",
        model_revision_identity="example-model@2026-09-03",
        model_identity_stability="IMMUTABLE",
        inference_settings_sha256=sha256_bytes(b"settings"),
        retention_policy_identity="no-retention",
        privacy_policy_identity="privacy-v1",
        is_test_double=False,
    )
    inventory = (
        InputCommitment("reviewer_brief", "text/markdown", 5, sha256_bytes(b"brief")),
        InputCommitment("review_package", "application/json", 7, package_digest),
        InputCommitment("run_envelope", "application/json", 8, sha256_bytes(b"envelope")),
        InputCommitment("output_schema", "application/schema+json", 6, sha256_bytes(b"schema")),
    )
    request_sha256 = sha256_bytes(b"request")
    receipt = build_runner_receipt(
        state=RunnerState.REVIEW_COMPLETED,
        run_identity=run_identity,
        backend_identity=backend_identity,
        permitted_input_inventory=inventory,
        request_sha256=request_sha256,
        capability_preflight_sha256=sha256_bytes(b"preflight"),
        isolation_receipt_sha256=sha256_bytes(b"isolation"),
        response_identity={
            "provider_request_id": provider_request_id,
            "request_sha256": request_sha256,
            "reviewer_id": run_identity.reviewer_id,
            "review_run_id": run_identity.review_run_id,
            "context_id": run_identity.context_id,
            "backend_identity_sha256": sha256_bytes(
                canonical_json_bytes(dataclasses.asdict(backend_identity))
            ),
            "response_count": 1,
            "raw_response_byte_count": 8,
            "raw_response_sha256": sha256_bytes(b"response"),
            "parsed_output_sha256": sha256_bytes(b"output"),
        },
    )
    return canonical_json_bytes(receipt_document(receipt))


def _preserve(base: Path, label: str, content: bytes = b"diagnostic") -> Path:
    return atomic_freeze_evidence(content, base / "evidence" / label / "receipt.json")


class ReviewerRunnerEvidenceTests(unittest.TestCase):
    def setUp(self):
        if _EVIDENCE_IMPORT_ERROR is not None:
            self.fail(
                "reviewer_runner.evidence must implement the evidence lifecycle contract"
            )

    def test_task_workspace_has_unique_owned_marker_and_resolved_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            transient_parent = Path(directory).resolve() / "transient"
            transient_parent.mkdir()

            first = TaskWorkspace.create(transient_parent, "run-001")
            second = TaskWorkspace.create(transient_parent, "run-002")

            self.assertEqual(
                first.root,
                (transient_parent / "joewrks-reviewer-runner" / "run-001").resolve(),
            )
            self.assertEqual(first.marker_path, first.root / ".joewrks-runner-owner.json")
            self.assertEqual(first.inputs_path, first.root / "inputs")
            self.assertEqual(first.response_working_path, first.root / "response-working")
            self.assertEqual(first.synthetic_canaries_path, first.root / "synthetic-canaries")
            self.assertNotEqual(first.root, second.root)
            self.assertEqual(
                json.loads(first.marker_path.read_bytes()),
                {"resolved_root": str(first.root), "review_run_id": "run-001"},
            )
            self.assertEqual(
                sorted(path.name for path in first.root.iterdir()),
                [
                    ".joewrks-runner-owner.json",
                    "inputs",
                    "response-working",
                    "synthetic-canaries",
                ],
            )
            for path in (
                first.root,
                first.marker_path,
                first.inputs_path,
                first.response_working_path,
                first.synthetic_canaries_path,
            ):
                self.assertTrue(path.is_absolute())
                self.assertEqual(path, path.resolve(strict=True))

    def test_evidence_is_frozen_before_transient_package_response_and_canary_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-freeze")
            workspace.inputs_path.joinpath("package.json").write_bytes(b"transient-package")
            workspace.response_working_path.joinpath("response.json").write_bytes(
                b"transient-response"
            )
            workspace.synthetic_canaries_path.joinpath("canary.bin").write_bytes(
                b"transient-canary"
            )
            receipt_bytes = _receipt_bytes("provider-request-freeze", "run-freeze")
            receipt_path = base / "evidence" / "run-freeze" / "receipt.json"

            frozen_path = atomic_freeze_evidence(receipt_bytes, receipt_path)
            os.utime(frozen_path, ns=(1_000_000_000, 1_000_000_000))
            frozen_mtime = frozen_path.stat().st_mtime_ns
            self.assertEqual(atomic_freeze_evidence(receipt_bytes, receipt_path), frozen_path)
            self.assertEqual(frozen_path.stat().st_mtime_ns, frozen_mtime)
            with self.assertRaises(ValueError):
                atomic_freeze_evidence(b"conflicting-receipt", receipt_path)
            self.assertEqual(frozen_path.read_bytes(), receipt_bytes)

            workspace.cleanup(
                preserved_evidence_paths=(frozen_path,),
                sibling_paths=(),
            )

            self.assertFalse(workspace.root.exists())
            self.assertEqual(frozen_path.read_bytes(), receipt_bytes)
            self.assertEqual(
                load_used_provider_request_ids(base / "evidence"),
                frozenset({"provider-request-freeze"}),
            )

    def test_evidence_freeze_rejects_reparse_alias_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            real_evidence = base / "real-evidence"
            real_evidence.mkdir()
            alias = base / "evidence-alias"
            alias.symlink_to(real_evidence, target_is_directory=True)
            escaped_target = real_evidence / "receipt.json"

            with self.assertRaises(ValueError):
                atomic_freeze_evidence(
                    b"must-not-follow-reparse-alias",
                    alias / "receipt.json",
                )

            self.assertFalse(os.path.lexists(escaped_target))

    def test_evidence_freeze_serializes_intervening_writer_without_clobber(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            target = base / "evidence" / "receipt.json"
            original_replace = evidence_module.os.replace
            intervention_active = False
            competing_outcomes = []

            def replace_with_competing_writer(source, destination):
                nonlocal intervention_active
                resolved_destination = Path(destination).resolve(strict=False)
                self.assertEqual(resolved_destination, target.resolve(strict=False))
                self.assertTrue(resolved_destination.is_relative_to(base))
                if not intervention_active:
                    intervention_active = True
                    try:
                        try:
                            atomic_freeze_evidence(
                                b"competing-writer-bytes",
                                resolved_destination,
                            )
                        except ValueError:
                            competing_outcomes.append("rejected")
                        else:
                            competing_outcomes.append("published")
                    finally:
                        intervention_active = False
                original_replace(source, destination)

            with mock.patch.object(
                evidence_module.os,
                "replace",
                side_effect=replace_with_competing_writer,
            ):
                frozen = atomic_freeze_evidence(b"reserved-writer-bytes", target)

            self.assertEqual(competing_outcomes, ["rejected"])
            self.assertEqual(frozen.read_bytes(), b"reserved-writer-bytes")

    def test_evidence_freeze_reserves_destination_against_exclusive_creator(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            target = base / "evidence" / "receipt.json"
            original_replace = evidence_module.os.replace
            creator_outcomes = []

            def replace_after_exclusive_creator(source, destination):
                resolved_destination = Path(destination).resolve(strict=False)
                self.assertEqual(resolved_destination, target.resolve(strict=False))
                self.assertTrue(resolved_destination.is_relative_to(base))
                try:
                    with resolved_destination.open("xb") as stream:
                        stream.write(b"exclusive-intervening-writer")
                        stream.flush()
                        os.fsync(stream.fileno())
                except FileExistsError:
                    creator_outcomes.append("rejected")
                else:
                    creator_outcomes.append("published")
                original_replace(source, destination)

            with mock.patch.object(
                evidence_module.os,
                "replace",
                side_effect=replace_after_exclusive_creator,
            ):
                frozen = atomic_freeze_evidence(b"reserved-destination-bytes", target)

            self.assertEqual(creator_outcomes, ["rejected"])
            self.assertEqual(frozen.read_bytes(), b"reserved-destination-bytes")

    def test_cleanup_removes_only_exact_task_root_and_reads_back_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-cleanup")
            workspace.inputs_path.joinpath("input.bin").write_bytes(b"owned-input")
            preserved = _preserve(base, "run-cleanup")
            runner_parent = workspace.root.parent

            result = workspace.cleanup(
                preserved_evidence_paths=(preserved,),
                sibling_paths=(),
            )

            self.assertIsInstance(result, CleanupResult)
            self.assertEqual(result.removed_paths, (str(workspace.root),))
            self.assertEqual(result.missing_after_cleanup, (str(workspace.root),))
            self.assertEqual(result.sibling_paths_unchanged, ())
            self.assertTrue(result.source_snapshot_unchanged)
            self.assertRegex(result.cleanup_sha256, r"^[0-9a-f]{64}$")
            self.assertFalse(workspace.root.exists())
            self.assertTrue(transient_parent.is_dir())
            self.assertTrue(runner_parent.is_dir())
            self.assertTrue(preserved.is_file())
            recreated = TaskWorkspace.create(transient_parent, "run-cleanup")
            self.assertEqual(recreated.root, workspace.root)
            recreated.cleanup(
                preserved_evidence_paths=(preserved,),
                sibling_paths=(),
            )
            self.assertFalse(os.path.lexists(recreated.root))

    def test_sibling_root_and_sibling_output_remain_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            selected = TaskWorkspace.create(transient_parent, "run-selected")
            sibling = TaskWorkspace.create(transient_parent, "run-sibling")
            selected.inputs_path.joinpath("selected.bin").write_bytes(b"selected-only-bytes")
            sibling.inputs_path.joinpath("sibling.bin").write_bytes(b"sibling-root-bytes")
            sibling_output = sibling.response_working_path / "result.json"
            sibling_output.write_bytes(b'{"sibling":"byte-identical"}')
            preserved = _preserve(base, "run-selected")
            sibling_root_before = _tree_bytes_sha256(sibling.root)
            sibling_output_before = hashlib.sha256(sibling_output.read_bytes()).hexdigest()

            result = selected.cleanup(
                preserved_evidence_paths=(preserved,),
                sibling_paths=(sibling.root, sibling_output),
            )

            self.assertFalse(selected.root.exists())
            self.assertEqual(_tree_bytes_sha256(sibling.root), sibling_root_before)
            self.assertEqual(
                hashlib.sha256(sibling_output.read_bytes()).hexdigest(),
                sibling_output_before,
            )
            self.assertEqual(
                result.sibling_paths_unchanged,
                tuple(sorted((str(sibling.root), str(sibling_output)))),
            )

    def test_sibling_manifest_rejects_split_file_digest_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-framed-sibling")
            preserved = _preserve(base, "framed-sibling")
            sibling = base / "sibling-tree"
            sibling.mkdir()
            sibling.joinpath("a").write_bytes(b"Xfile\0b\0Y")
            original_remove_owned_tree = evidence_module._remove_owned_tree

            def delete_then_split_sibling_file(target):
                resolved_target = Path(target).resolve(strict=True)
                self.assertEqual(resolved_target, workspace.root)
                self.assertTrue(resolved_target.is_relative_to(base))
                original_remove_owned_tree(resolved_target)
                sibling.joinpath("a").unlink()
                sibling.joinpath("a").write_bytes(b"X")
                sibling.joinpath("b").write_bytes(b"Y")

            with mock.patch.object(
                evidence_module,
                "_remove_owned_tree",
                side_effect=delete_then_split_sibling_file,
            ):
                with self.assertRaises(ValueError):
                    workspace.cleanup(
                        preserved_evidence_paths=(preserved,),
                        sibling_paths=(sibling,),
                    )

            self.assertEqual(sibling.joinpath("a").read_bytes(), b"X")
            self.assertEqual(sibling.joinpath("b").read_bytes(), b"Y")

    def test_ambiguous_or_mismatched_ownership_blocks_cleanup_and_next_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            preserved = _preserve(base, "ownership")

            mismatched = TaskWorkspace.create(transient_parent, "run-mismatch")
            mismatched.marker_path.write_bytes(
                canonical_json_bytes(
                    {
                        "resolved_root": str(mismatched.root),
                        "review_run_id": "other-run",
                    }
                )
            )
            with self.assertRaises(ValueError):
                mismatched.cleanup(
                    preserved_evidence_paths=(preserved,),
                    sibling_paths=(),
                )
            self.assertTrue(mismatched.root.is_dir())
            with self.assertRaises(ValueError):
                TaskWorkspace.create(transient_parent, "run-mismatch")

            missing = TaskWorkspace.create(transient_parent, "run-missing-marker")
            missing.marker_path.unlink()
            with self.assertRaises(ValueError):
                missing.cleanup(
                    preserved_evidence_paths=(preserved,),
                    sibling_paths=(),
                )
            self.assertTrue(missing.root.is_dir())

            escaped = TaskWorkspace.create(transient_parent, "run-symlink")
            outside = base / "outside-owned-root"
            outside.mkdir()
            outside.joinpath("must-survive.bin").write_bytes(b"outside-survivor")
            link = escaped.inputs_path / "outside-link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                pass
            else:
                with self.assertRaises(ValueError):
                    escaped.cleanup(
                        preserved_evidence_paths=(preserved,),
                        sibling_paths=(),
                    )
                self.assertEqual(
                    outside.joinpath("must-survive.bin").read_bytes(),
                    b"outside-survivor",
                )

    def test_reparse_swap_after_partial_cleanup_is_terminal_and_never_traversed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-delete-race")
            removed_before_swap = workspace.inputs_path / "partial.bin"
            removed_before_swap.write_bytes(b"owned-partial-cleanup")
            outside = base / "outside-delete-boundary"
            outside.mkdir()
            outside_file = outside / "must-survive.bin"
            outside_file.write_bytes(b"external-target-bytes")
            preserved = _preserve(base, "delete-race")
            original_verify = evidence_module._verify_owned_tree

            def verify_then_partially_remove_and_swap(root):
                resolved_root = Path(root).resolve(strict=True)
                self.assertEqual(resolved_root, workspace.root)
                self.assertTrue(resolved_root.is_relative_to(base))
                original_verify(resolved_root)
                self.assertTrue(removed_before_swap.is_relative_to(resolved_root))
                removed_before_swap.unlink()
                workspace.synthetic_canaries_path.rmdir()
                workspace.synthetic_canaries_path.symlink_to(
                    outside,
                    target_is_directory=True,
                )

            with mock.patch.object(
                evidence_module,
                "_verify_owned_tree",
                side_effect=verify_then_partially_remove_and_swap,
            ):
                with self.assertRaises(ValueError):
                    workspace.cleanup(
                        preserved_evidence_paths=(preserved,),
                        sibling_paths=(),
                    )

            self.assertFalse(os.path.lexists(removed_before_swap))
            self.assertTrue(os.path.lexists(workspace.root))
            self.assertEqual(outside_file.read_bytes(), b"external-target-bytes")
            with self.assertRaises(ValueError):
                TaskWorkspace.create(transient_parent, "run-delete-race")

    def test_parent_reparse_swap_before_child_recursion_never_traverses_target(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-parent-swap")
            preserved = _preserve(base, "parent-swap")
            outside = base / "outside-parent-swap"
            outside_marker_directory = outside / ".joewrks-runner-owner.json"
            outside_marker_directory.mkdir(parents=True)
            outside_file = outside_marker_directory / "must-survive.bin"
            outside_file.write_bytes(b"external-parent-swap-bytes")
            parked_root = base / "parked-owned-root"
            original_plain_directory_identity = evidence_module._plain_directory_identity
            root_identity_checks = 0

            def identity_with_parent_swap(path, label):
                nonlocal root_identity_checks
                identity = original_plain_directory_identity(path, label)
                if Path(path) == workspace.root:
                    root_identity_checks += 1
                    if root_identity_checks == 3:
                        resolved_root = workspace.root.resolve(strict=True)
                        self.assertEqual(resolved_root, workspace.root)
                        self.assertTrue(resolved_root.is_relative_to(base))
                        os.replace(workspace.root, parked_root)
                        workspace.root.symlink_to(outside, target_is_directory=True)
                return identity

            with mock.patch.object(
                evidence_module,
                "_plain_directory_identity",
                side_effect=identity_with_parent_swap,
            ):
                with self.assertRaises(ValueError):
                    workspace.cleanup(
                        preserved_evidence_paths=(preserved,),
                        sibling_paths=(),
                    )

            self.assertTrue(outside_file.is_file())
            if outside_file.is_file():
                self.assertEqual(outside_file.read_bytes(), b"external-parent-swap-bytes")
            with self.assertRaises(ValueError):
                TaskWorkspace.create(transient_parent, "run-parent-swap")

    def test_repository_head_tree_and_clean_status_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory).resolve() / "repository"
            repository.mkdir()
            _git(repository, "init", "-q")
            _git(repository, "config", "user.email", "reviewer-runner@example.invalid")
            _git(repository, "config", "user.name", "Reviewer Runner Test")
            source = repository / "source.txt"
            source.write_bytes(b"immutable-source\n")
            _git(repository, "add", "source.txt")
            _git(repository, "commit", "-q", "-m", "fixture")

            before = capture_source_snapshot(repository)

            self.assertIsInstance(before, SourceSnapshot)
            self.assertEqual(before.head_sha, _git(repository, "rev-parse", "HEAD").decode().strip())
            self.assertEqual(
                before.tree_sha,
                _git(repository, "rev-parse", "HEAD^{tree}").decode().strip(),
            )
            self.assertEqual(before.status_sha256, hashlib.sha256(b"").hexdigest())
            self.assertTrue(before.clean)
            self.assertTrue(verify_source_unchanged(before, repository))

            source.write_bytes(b"mutated-source\n")
            with self.assertRaises(ValueError):
                capture_source_snapshot(repository)
            with self.assertRaises(ValueError):
                verify_source_unchanged(before, repository)
            source.write_bytes(b"immutable-source\n")
            self.assertTrue(verify_source_unchanged(before, repository))

    def test_cleanup_failure_is_terminal_and_preserves_diagnostic_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-cleanup-failure")
            transient_diagnostic = workspace.response_working_path / "failure.txt"
            transient_diagnostic.write_bytes(b"transient-failure-detail")
            preserved = _preserve(base, "cleanup-failure", b"preserved-failure-detail")

            with mock.patch.object(
                evidence_module,
                "_remove_owned_tree",
                side_effect=OSError("synthetic cleanup failure"),
            ):
                with self.assertRaises(ValueError):
                    workspace.cleanup(
                        preserved_evidence_paths=(preserved,),
                        sibling_paths=(),
                    )

            self.assertTrue(workspace.root.is_dir())
            self.assertEqual(transient_diagnostic.read_bytes(), b"transient-failure-detail")
            self.assertEqual(preserved.read_bytes(), b"preserved-failure-detail")
            with self.assertRaises(ValueError):
                workspace.cleanup(
                    preserved_evidence_paths=(preserved,),
                    sibling_paths=(),
                )
            with self.assertRaises(ValueError):
                TaskWorkspace.create(transient_parent, "run-cleanup-failure")

    def test_post_deletion_verification_failure_blocks_same_run_recreation(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            workspace = TaskWorkspace.create(transient_parent, "run-post-delete")
            preserved = _preserve(base, "post-delete", b"before-cleanup")
            original_remove_owned_tree = evidence_module._remove_owned_tree

            def delete_then_change_preserved_evidence(target):
                resolved_target = Path(target).resolve(strict=True)
                self.assertEqual(resolved_target, workspace.root)
                self.assertTrue(resolved_target.is_relative_to(base))
                original_remove_owned_tree(resolved_target)
                self.assertFalse(os.path.lexists(resolved_target))
                preserved.write_bytes(b"changed-after-delete")

            with mock.patch.object(
                evidence_module,
                "_remove_owned_tree",
                side_effect=delete_then_change_preserved_evidence,
            ):
                with self.assertRaises(ValueError):
                    workspace.cleanup(
                        preserved_evidence_paths=(preserved,),
                        sibling_paths=(),
                    )

            self.assertFalse(os.path.lexists(workspace.root))
            with self.assertRaises(ValueError):
                TaskWorkspace.create(transient_parent, "run-post-delete")

    def test_prior_output_bytes_do_not_enter_the_next_workspace_or_request(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            transient_parent = base / "transient"
            transient_parent.mkdir()
            prior = TaskWorkspace.create(transient_parent, "run-prior")
            next_workspace = TaskWorkspace.create(transient_parent, "run-next")
            prior_output = b"PRIOR-OUTPUT-SECRET-6eea37aa"
            prior.response_working_path.joinpath("review.json").write_bytes(prior_output)

            artifacts = (
                InputArtifact("reviewer_brief", "text/markdown", b"next brief"),
                InputArtifact("review_package", "application/json", b'{"next":true}'),
                InputArtifact("run_envelope", "application/json", b'{"run":"next"}'),
                InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
            )
            run = RunIdentity(
                semantic_review_contract_version="joewrks.semantic-review/1.0",
                package_schema_version="joewrks.semantic-review-input/1.0",
                package_digest=sha256_bytes(b'{"next":true}'),
                source_action_contract_hash=sha256_bytes(b"action-contract"),
                source_definition_digest=sha256_bytes(b"definition"),
                reviewer_id="reviewer-001",
                review_run_id="run-next",
                context_id="context-next",
                cohort_id=None,
                case_id=None,
            )
            request = build_canonical_request(run, artifacts, {})
            request_document = json.loads(request.content)
            decoded_inputs = tuple(
                base64.b64decode(item["content_base64"], validate=True)
                for item in request_document["inputs"]
            )
            next_workspace_bytes = []
            for current, directories, files in os.walk(
                next_workspace.root,
                topdown=True,
                followlinks=False,
            ):
                directories.sort()
                for name in sorted(files):
                    next_workspace_bytes.append((Path(current) / name).read_bytes())

            self.assertNotIn(prior_output, request.content)
            self.assertNotIn(prior_output, decoded_inputs)
            self.assertNotIn(prior_output, next_workspace_bytes)
            preserved = _preserve(base, "run-prior")
            prior.cleanup(
                preserved_evidence_paths=(preserved,),
                sibling_paths=(next_workspace.root,),
            )
            self.assertTrue(next_workspace.root.is_dir())
            next_workspace_bytes_after_cleanup = []
            for current, directories, files in os.walk(
                next_workspace.root,
                topdown=True,
                followlinks=False,
            ):
                directories.sort()
                for name in sorted(files):
                    next_workspace_bytes_after_cleanup.append(
                        (Path(current) / name).read_bytes()
                    )
            self.assertNotIn(prior_output, next_workspace_bytes_after_cleanup)


if __name__ == "__main__":
    unittest.main()
