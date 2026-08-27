# v0.4.3 Deterministic Semantic Review Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `joewrks.semantic-review/1.0` as a mandatory hash-bound reliability sidecar over unchanged `joewrks.action-conformance/1.0`.

**Architecture:** Add a focused stdlib-only `downstream.semantic_review` package that validates exact input packages, responsibility/obligation ownership, review outputs, golden calibration, and repeated-review statistics. Keep contract compilation and runtime verification unchanged; the new gate consumes their frozen output by contract hash.

**Tech Stack:** Python 3 standard library, JSON Schema files restricted to and validated by the existing repository schema subset, `unittest`, canonical UTF-8 JSON/SHA-256. Cross-record uniqueness, exact-set, ordering, verdict/rationale, and arithmetic invariants are enforced in Python.

**Spec:** `evals/semantic-review-v0.4.3/V043_REVIEW_CONTRACT_SPEC.md`

## Global Constraints

- Review schema identity is exactly `joewrks.semantic-review/1.0`.
- Action contract remains exactly `joewrks.action-conformance/1.0`.
- Product Definition is read-only and canonical; supporting projections cannot extend it.
- Reviewer package and brief bytes must be identical across comparable runs.
- Failure precedence is package error, rubric error, candidate rejection, approval.
- No majority-vote or manual-waiver escape hatch exists.
- Every failed calibration increments `rubric_calibration_revision`, changes the responsibility-profile/rubric hash, and requires a complete rerun.
- Calibration uses exactly 15 frozen golden cases and at least 3 independent full reviews.
- All PM-approved thresholds in `RELIABILITY_GATE_SPEC.md` are conjunctive.
- The implementation uses only Python's standard library and existing repository schema validation.
- v0.4.2 RMA artifacts are not runtime dependencies or generic semantic authority.

---

### Task 1: Canonical review hashing primitives

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/__init__.py`
- Create: `skills/joewrks-product-definition/downstream/semantic_review/hashing.py`
- Test: `tests/test_semantic_review_hashing.py`

**Interfaces:**
- Produces: `canonical_json_bytes(value: Any) -> bytes`
- Produces: `sha256_bytes(data: bytes) -> str`
- Produces: `sha256_file(path: Path) -> tuple[str, int]`
- Produces: `manifest_hash(manifest: dict[str, Any]) -> str`
- Produces: `package_hash(manifest_hash_value: str, files: list[dict[str, Any]]) -> str`

- [ ] **Step 1: Write deterministic hash tests**

```python
def test_manifest_hash_ignores_declared_self_hash_but_not_other_bytes():
    base = {"schema_version": "joewrks.semantic-review-input/1.0", "files": []}
    with_self = {**base, "reviewer_input_manifest_hash": "0" * 64}
    assert manifest_hash(base) == manifest_hash(with_self)
    assert manifest_hash({**base, "files": [{"path": "a", "sha256": "1" * 64}]}) != manifest_hash(base)

def test_package_hash_sorts_by_logical_role_and_path():
    files = [
        {"logical_role": "reviewer_brief", "path": "z", "sha256": "2" * 64, "bytes": 2},
        {"logical_role": "action_contract", "path": "a", "sha256": "1" * 64, "bytes": 1},
    ]
    assert package_hash("3" * 64, files) == package_hash("3" * 64, list(reversed(files)))
```

- [ ] **Step 2: Run the hashing test and observe the missing module failure**

Run: `python -m unittest tests.test_semantic_review_hashing -v`

Expected: `ModuleNotFoundError` for `downstream.semantic_review`.

- [ ] **Step 3: Implement canonical byte and package hashing**

```python
def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def manifest_hash(manifest: dict[str, Any]) -> str:
    unhashed = dict(manifest)
    unhashed.pop("reviewer_input_manifest_hash", None)
    return sha256_bytes(canonical_json_bytes(unhashed))

def package_hash(manifest_hash_value: str, files: list[dict[str, Any]]) -> str:
    ordered = sorted(files, key=lambda item: (item["logical_role"], item["path"]))
    return sha256_bytes(canonical_json_bytes({"manifest_hash": manifest_hash_value, "ordered_files": ordered}))
```

- [ ] **Step 4: Run hashing tests**

Run: `python -m unittest tests.test_semantic_review_hashing -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the hashing unit**

```text
git add skills/joewrks-product-definition/downstream/semantic_review tests/test_semantic_review_hashing.py
git commit -m "feat: add deterministic semantic review hashing"
```

### Task 2: Hash-bound reviewer input package

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/package.py`
- Create: `skills/joewrks-product-definition/downstream/schemas/semantic-review-input-manifest.schema.json`
- Test: `tests/test_semantic_review_package.py`

**Interfaces:**
- Consumes: hashing functions from Task 1
- Produces: `PackageError(code: str, message: str)`
- Produces: `load_and_verify_package(root: Path) -> dict[str, Any]`
- Produces: `verify_exclusions(root: Path, manifest: dict[str, Any]) -> None`
- Produces: `verify_run_envelope(envelope: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]`

- [ ] **Step 1: Write package identity and exclusion tests**

```python
def test_package_rejects_prior_verdict_exposure(package_root):
    (package_root / "prior-review.json").write_text('{"verdict":"APPROVED"}', encoding="utf-8")
    with self.assertRaisesRegex(PackageError, "PREVIOUS_VERDICT_EXPOSURE"):
        load_and_verify_package(package_root)

def test_package_rejects_path_escape(package_root):
    manifest = load_manifest(package_root)
    manifest["files"][0]["path"] = "../outside.json"
    write_manifest(package_root, manifest)
    with self.assertRaisesRegex(PackageError, "INVALID_PACKAGE_PATH"):
        load_and_verify_package(package_root)
```

- [ ] **Step 2: Run the package tests and observe missing API failures**

Run: `python -m unittest tests.test_semantic_review_package -v`

Expected: import failures for `PackageError` and `load_and_verify_package`.

- [ ] **Step 3: Implement manifest/schema/hash/path/exclusion validation**

```python
REQUIRED_ROLES = {
    "canonical_authority", "action_contract", "provenance_inventory",
    "responsibility_profile", "semantic_obligation_index", "reviewer_brief",
    "review_output_schema", "review_identity_inventory", "exclusion_manifest",
}

class PackageError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code

def _safe_path(root: Path, relative: str) -> Path:
    if "\\" in relative or relative.startswith("/") or ".." in PurePosixPath(relative).parts:
        raise PackageError("INVALID_PACKAGE_PATH", relative)
    resolved = (root / relative).resolve()
    if root.resolve() not in (resolved, *resolved.parents):
        raise PackageError("INVALID_PACKAGE_PATH", relative)
    return resolved
```

Verify every declared byte size/hash, exact required role count, manifest hash, package hash, declared `previous_reviewer_verdicts_present: false`, and forbidden file scan before parsing semantic content.

- [ ] **Step 4: Run package and hashing tests**

Run: `python -m unittest tests.test_semantic_review_hashing tests.test_semantic_review_package -v`

Expected: all tests pass.

- [ ] **Step 5: Commit package validation**

```text
git add skills/joewrks-product-definition/downstream/semantic_review/package.py skills/joewrks-product-definition/downstream/schemas/semantic-review-input-manifest.schema.json tests/test_semantic_review_package.py
git commit -m "feat: validate hash-bound semantic review packages"
```

### Task 3: Responsibility profile and obligation index

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/responsibility.py`
- Create: `skills/joewrks-product-definition/downstream/semantic_review/artifacts/responsibility-profile-v1.json`
- Test: `tests/test_semantic_review_responsibility.py`

**Interfaces:**
- Produces: `ResponsibilityError(code: str, message: str)`
- Produces: `load_responsibility_profile(path: Path) -> dict[str, dict[str, Any]]`
- Produces: `validate_obligation_index(contract: dict[str, Any], profile: dict[str, Any], index: dict[str, Any]) -> None`
- Produces: `expected_responsibility(owner_kind: str, semantic_field: str) -> tuple[str, str]`

- [ ] **Step 1: Write complete-profile and unique-owner tests**

```python
def test_profile_assigns_all_current_action_and_lifecycle_fields_once():
    profile = load_responsibility_profile(PROFILE_PATH)
    assert set(profile["action"]) == EXPECTED_ACTION_FIELDS
    assert set(profile["lifecycle"]) == EXPECTED_LIFECYCLE_FIELDS

def test_obligation_cannot_have_two_owners(valid_contract, profile, valid_index):
    duplicate = copy.deepcopy(valid_index["obligations"][0])
    duplicate["owning_field"] = "visible_error"
    valid_index["obligations"].append(duplicate)
    with self.assertRaisesRegex(ResponsibilityError, "MULTIPLE_OWNERS"):
        validate_obligation_index(valid_contract, profile, valid_index)
```

- [ ] **Step 2: Run responsibility tests and observe missing implementation failures**

Run: `python -m unittest tests.test_semantic_review_responsibility -v`

Expected: import/file failures.

- [ ] **Step 3: Implement the 26 action and 13 lifecycle responsibility rules**

```python
VALID_MODES = {"LOCAL", "COMPOSITIONAL", "REFERENCE_ONLY"}

def expected_responsibility(profile, owner_kind, semantic_field):
    try:
        rule = profile[owner_kind][semantic_field]
    except KeyError as error:
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", f"{owner_kind}:{semantic_field}") from error
    if rule["completeness_mode"] not in VALID_MODES:
        raise ResponsibilityError("COMPLETENESS_UNDEFINED", semantic_field)
    return rule["responsibility_rule_id"], rule["completeness_mode"]
```

The JSON artifact SHALL copy every `FR-A01`–`FR-A26` and `FR-L01`–`FR-L13` rule from `FIELD_RESPONSIBILITY_MATRIX.md`, include a `rubric_calibration_revision`, and include allowed sibling rules, omission codes, and overreach codes.

- [ ] **Step 4: Run responsibility tests**

Run: `python -m unittest tests.test_semantic_review_responsibility -v`

Expected: all tests pass.

- [ ] **Step 5: Commit responsibility rules**

```text
git add skills/joewrks-product-definition/downstream/semantic_review tests/test_semantic_review_responsibility.py
git commit -m "feat: define semantic field responsibility profile"
```

### Task 4: Semantic review output validation

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/output.py`
- Create: `skills/joewrks-product-definition/downstream/schemas/semantic-review-output.schema.json`
- Test: `tests/test_semantic_review_output.py`

**Interfaces:**
- Consumes: package and responsibility validation
- Produces: `OutputError(code: str, message: str)`
- Produces: `validate_review_output(package: dict[str, Any], run_envelope: dict[str, Any], output: dict[str, Any]) -> dict[str, int]`

- [ ] **Step 1: Write exact coverage, immutable hash, and verdict tests**

```python
def test_completed_output_requires_exact_identity_set(valid_package, valid_output):
    valid_output["records"].pop()
    with self.assertRaisesRegex(OutputError, "IDENTITY_SET_MISMATCH"):
        validate_review_output(valid_package, valid_run_envelope, valid_output)

def test_rubric_error_is_not_candidate_rejection(valid_package, valid_output):
    valid_output["records"] = []
    valid_output["preflight_errors"] = [{
        "verdict": "RUBRIC_ERROR",
        "rationale_code": "RESPONSIBILITY_UNDEFINED",
        "scope": "responsibility-profile",
        "canonical_evidence_refs": [],
        "reviewer_explanation": "The frozen taxonomy has no unique owner for the fixture obligation.",
    }]
    valid_output["summary"].update({
        "record_count": 0,
        "unique_identity_count": 0,
        "pending_count": 0,
        "verdict_counts": {
            "APPROVED": 0,
            "REJECTED_CANDIDATE": 0,
            "RUBRIC_ERROR": 1,
            "INPUT_PACKAGE_ERROR": 0,
        },
        "complete": False,
    })
    summary = validate_review_output(valid_package, valid_run_envelope, valid_output)
    self.assertEqual(1, summary["RUBRIC_ERROR"])
```

- [ ] **Step 2: Run output tests and observe missing API failure**

Run: `python -m unittest tests.test_semantic_review_output -v`

Expected: import failure for `validate_review_output`.

- [ ] **Step 3: Implement schema, hash, responsibility, and identity validation**

```python
VERDICTS = {"APPROVED", "REJECTED_CANDIDATE", "RUBRIC_ERROR", "INPUT_PACKAGE_ERROR"}

def _identity(record):
    return f"{record['owner_kind']}:{record['owner_id']}:{record['semantic_field']}"

def validate_review_output(package, run_envelope, output):
    validate_instance(output, package["review_output_schema"])
    verify_run_envelope(run_envelope, package)
    for key in ("review_run_id", "reviewer_context_id", "isolation_attestation_hash"):
        if output[key] != run_envelope[key]:
            raise OutputError("RUN_ENVELOPE_MISMATCH", key)
    top_level_hashes = (
        "reviewer_brief_hash", "reviewer_input_manifest_hash", "reviewer_input_package_hash",
        "contract_hash", "responsibility_profile_hash", "semantic_obligation_index_hash",
        "review_identity_inventory_hash",
    )
    for key in top_level_hashes:
        if output[key] != package[key]:
            raise OutputError("IMMUTABLE_HASH_MISMATCH", key)
    preflight = output["preflight_errors"]
    if preflight:
        validate_preflight_errors(preflight)
        if output["summary"]["complete"]:
            raise OutputError("INVALID_COMPLETION_STATE", "preflight failure cannot be complete")
        observed_counts = Counter(item["verdict"] for item in preflight + output["records"])
        validate_summary_arithmetic(output["summary"], output["records"], preflight, observed_counts)
        return dict(observed_counts)
    records = output["records"]
    observed = [_identity(record) for record in records]
    if len(observed) != len(set(observed)) or set(observed) != set(package["expected_identities"]):
        raise OutputError("IDENTITY_SET_MISMATCH", "completed output must equal expected identities")
    if not output["summary"]["complete"] or output["summary"]["pending_count"] != 0:
        raise OutputError("INVALID_COMPLETION_STATE", "valid completed review must be complete with zero pending")
    immutable = {
        "reviewer_brief_hash": package["reviewer_brief_hash"],
        "reviewer_input_manifest_hash": package["reviewer_input_manifest_hash"],
        "contract_hash": package["contract_hash"],
    }
    for record in records:
        expected = package["identity_inventory"][_identity(record)]
        if any(record[key] != value for key, value in immutable.items()):
            raise OutputError("IMMUTABLE_HASH_MISMATCH", _identity(record))
        for key in ("semantic_value_hash", "provenance_set_hash", "responsibility_rule_id", "completeness_mode"):
            if record[key] != expected[key]:
                raise OutputError("IMMUTABLE_IDENTITY_MISMATCH", f"{_identity(record)}:{key}")
        if len(record["provenance_hashes"]) != len(set(record["provenance_hashes"])):
            raise OutputError("DUPLICATE_PROVENANCE", _identity(record))
        for key in ("sibling_review_identity_refs", "semantic_obligation_ids", "test_obligation_refs"):
            if record[key] != sorted(set(record[key])):
                raise OutputError("INVALID_REFERENCE_SET", f"{_identity(record)}:{key}")
        if record["rationale_code"] not in RATIONALES_BY_VERDICT[record["verdict"]]:
            raise OutputError("VERDICT_RATIONALE_MISMATCH", _identity(record))
    observed_counts = Counter(record["verdict"] for record in records)
    validate_summary_arithmetic(output["summary"], records, preflight, observed_counts)
    return dict(observed_counts)
```

- [ ] **Step 4: Run output, responsibility, package, and schema tests**

Run: `python -m unittest tests.test_semantic_review_output tests.test_semantic_review_responsibility tests.test_semantic_review_package tests.test_downstream_schema_validation -v`

Expected: all tests pass.

- [ ] **Step 5: Commit output contract**

```text
git add skills/joewrks-product-definition/downstream/semantic_review/output.py skills/joewrks-product-definition/downstream/schemas/semantic-review-output.schema.json tests/test_semantic_review_output.py
git commit -m "feat: validate semantic review outputs"
```

### Task 5: Canonical brief and 15 golden cases

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/artifacts/reviewer-brief-v1.md`
- Create: `tests/fixtures/semantic-review-v1/golden-cases.json`
- Create: `tests/fixtures/semantic-review-v1/golden-answers.json`
- Create: `tests/test_semantic_review_goldens.py`

**Interfaces:**
- Consumes: package/output validation
- Produces: `evaluate_goldens(outputs: list[dict[str, Any]], answers: dict[str, Any]) -> dict[str, Any]`

- [ ] **Step 1: Write frozen count and expected-answer tests**

```python
def test_golden_suite_has_exactly_fifteen_unique_cases():
    cases = json.loads(GOLDEN_CASES.read_text(encoding="utf-8"))
    assert len(cases) == 15
    assert {case["case_id"] for case in cases} == {f"G-{index:03d}" for index in range(1, 16)}

def test_golden_accuracy_requires_verdict_and_rationale_code():
    outputs = make_correct_golden_outputs()
    outputs[0]["rationale_code"] = "UNSUPPORTED_OVERREACH"
    report = evaluate_goldens(outputs, GOLDEN_ANSWERS)
    assert report["verdict_accuracy"] == 1.0
    assert report["rationale_code_accuracy"] < 1.0
```

- [ ] **Step 2: Run golden tests and observe missing fixtures/API failures**

Run: `python -m unittest tests.test_semantic_review_goldens -v`

Expected: fixture or import failure.

- [ ] **Step 3: Materialize exact brief and all specified golden cases**

The brief SHALL contain the complete normative body from `REVIEWER_BRIEF_SPEC.md`. The fixture files SHALL encode `G-001` through `G-015` with the exact expected verdict/rationale pairs in `GOLDEN_CASES_SPEC.md`. Keep `golden-answers.json` outside reviewer package manifests.

```python
def evaluate_goldens(outputs, answers):
    expected = {item["case_id"]: item for item in answers}
    observed = {item["case_id"]: item for item in outputs}
    if len(expected) != 15 or len(observed) != len(outputs) or set(observed) != set(expected):
        raise GoldenError("GOLDEN_IDENTITY_SET_MISMATCH")
    verdict_hits = sum(observed[key]["verdict"] == expected[key]["verdict"] for key in expected)
    rationale_hits = sum(observed[key]["rationale_code"] == expected[key]["rationale_code"] for key in expected)
    count = len(expected)
    return {"verdict_accuracy": verdict_hits / count, "rationale_code_accuracy": rationale_hits / count}
```

- [ ] **Step 4: Run golden tests**

Run: `python -m unittest tests.test_semantic_review_goldens -v`

Expected: all tests pass with count 15.

- [ ] **Step 5: Commit brief and goldens**

```text
git add skills/joewrks-product-definition/downstream/semantic_review/artifacts tests/fixtures/semantic-review-v1 tests/test_semantic_review_goldens.py
git commit -m "test: freeze semantic review golden calibration suite"
```

### Task 6: Reliability statistics with imbalance handling

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/statistics.py`
- Test: `tests/test_semantic_review_statistics.py`

**Interfaces:**
- Produces: `cohen_kappa(left: list[str], right: list[str]) -> float`
- Produces: `fleiss_kappa(runs: list[list[str]]) -> float`
- Produces: `gwet_ac1(runs: list[list[str]]) -> float`
- Produces: `minority_class_agreement(runs: list[list[str]]) -> float | None`
- Produces: `is_balanced(runs: list[list[str]], floor: float = 0.05) -> bool`

- [ ] **Step 1: Write statistic fixtures including the prevalence paradox**

```python
def test_imbalanced_population_uses_ac1_and_minority_agreement():
    runs = [
        ["APPROVED"] * 98 + ["REJECTED_CANDIDATE"] * 2,
        ["APPROVED"] * 98 + ["REJECTED_CANDIDATE"] * 2,
        ["APPROVED"] * 98 + ["REJECTED_CANDIDATE"] * 2,
    ]
    assert not is_balanced(runs)
    assert gwet_ac1(runs) == 1.0
    assert minority_class_agreement(runs) == 1.0
```

- [ ] **Step 2: Run statistics tests and observe missing API failure**

Run: `python -m unittest tests.test_semantic_review_statistics -v`

Expected: import failures for statistic functions.

- [ ] **Step 3: Implement pairwise, multi-rater, AC1, and minority formulas**

Use exact identity-aligned categorical counts and `fractions.Fraction` internally until the final float conversion. Reject unequal run lengths, unknown verdicts, fewer than three runs for multi-rater metrics, and empty populations.

```python
def minority_class_agreement(runs):
    candidate_classes = ("APPROVED", "REJECTED_CANDIDATE")
    pooled = Counter(value for run in runs for value in run if value in candidate_classes)
    minority = min(candidate_classes, key=lambda key: (pooled[key], key))
    if pooled[minority] == 0:
        return None
    any_minority = [index for index in range(len(runs[0])) if any(run[index] == minority for run in runs)]
    unanimous = sum(all(run[index] == minority for run in runs) for index in any_minority)
    return unanimous / len(any_minority)
```

- [ ] **Step 4: Run statistics tests**

Run: `python -m unittest tests.test_semantic_review_statistics -v`

Expected: all tests pass, including known perfect, chance, imbalanced, and disagreement matrices.

- [ ] **Step 5: Commit statistics**

```text
git add skills/joewrks-product-definition/downstream/semantic_review/statistics.py tests/test_semantic_review_statistics.py
git commit -m "feat: add semantic review reliability statistics"
```

### Task 7: Conjunctive reliability gate

**Files:**
- Create: `skills/joewrks-product-definition/downstream/semantic_review/gate.py`
- Create: `skills/joewrks-product-definition/downstream/semantic_review/disagreement.py`
- Test: `tests/test_semantic_review_gate.py`

**Interfaces:**
- Consumes: package, output, golden, and statistic APIs
- Produces: `evaluate_reliability_gate(run_packages: list[dict[str, Any]], run_envelopes: list[dict[str, Any]], outputs: list[dict[str, Any]], golden_report: dict[str, Any], classifications: list[dict[str, Any]]) -> dict[str, Any]`
- Produces: `validate_disagreement_classifications(outputs: list[dict[str, Any]], classifications: list[dict[str, Any]]) -> dict[str, Any]`

- [ ] **Step 1: Write balanced/imbalanced pass tests and no-majority failure test**

```python
def test_majority_agreement_cannot_override_same_rule_disagreement(valid_run_set):
    target_rule = valid_run_set.repeated_rule_id
    targets = [record for record in valid_run_set.outputs[2]["records"] if record["responsibility_rule_id"] == target_rule][:2]
    for record in targets:
        replace_verdict_and_recount(valid_run_set.outputs[2], record["review_identity"], "REJECTED_CANDIDATE", "MISSING_OWNED_SEMANTIC")
    report = evaluate_reliability_gate(*valid_run_set.args)
    assert not report["passed"]
    assert "FAIL/RESPONSIBILITY_RULE_INSTABILITY" in report["failures"]
```

- [ ] **Step 2: Run gate tests and observe missing API failure**

Run: `python -m unittest tests.test_semantic_review_gate -v`

Expected: import failure for `evaluate_reliability_gate`.

- [ ] **Step 3: Implement every threshold as a conjunctive gate**

```python
THRESHOLDS = {
    "minimum_runs": 3,
    "golden_verdict_accuracy": 1.0,
    "golden_rationale_code_accuracy": 1.0,
    "unanimity": 0.99,
    "balanced_kappa": 0.90,
    "imbalanced_ac1": 0.95,
    "minority_class_agreement": 0.95,
}

def evaluate_reliability_gate(run_packages, run_envelopes, outputs, golden_report, classifications):
    failures = []
    if len(outputs) < THRESHOLDS["minimum_runs"]:
        failures.append("FAIL/INSUFFICIENT_INDEPENDENT_RUNS")
    if not unique_verified_run_contexts(run_envelopes, outputs):
        failures.append("FAIL/REVIEWER_ISOLATION")
    if any(package["previous_reviewer_verdicts_present"] for package in run_packages):
        failures.append("FAIL/PREVIOUS_VERDICT_EXPOSURE")
    elif len({package["reviewer_brief_hash"] for package in run_packages}) != 1:
        failures.append("FAIL/BRIEF_IDENTITY_MISMATCH")
    elif len({package["reviewer_input_package_hash"] for package in run_packages}) != 1:
        failures.append("FAIL/PACKAGE_IDENTITY_MISMATCH")
    failures.extend(structural_failures(run_packages, outputs))
    if failures:
        return {"passed": False, "failures": list(dict.fromkeys(failures)), "metrics": {}, "thresholds": THRESHOLDS}
    failures.extend(golden_failures(golden_report, THRESHOLDS))
    metrics = reliability_metrics(outputs)
    disagreement_report = validate_disagreement_classifications(outputs, classifications)
    failures.extend(normative_disagreement_failures(metrics, disagreement_report))
    failures.extend(agreement_failures(metrics, THRESHOLDS))
    failures = list(dict.fromkeys(failures))
    return {"passed": not failures, "failures": failures, "metrics": metrics, "thresholds": THRESHOLDS}
```

Compute unchanged identities from exact semantic/provenance/rule/mode/obligation hashes. For more than three runs, compute three-review unanimity for every three-run combination and gate on the minimum. Compute pairwise Cohen kappa for every pair and Fleiss kappa/Gwet AC1 across all reviewers. Require one exact closed-code classification for every verdict or rationale disagreement; missing/uncertain classifications are `UNRESOLVED_NORMATIVE`, and adjudication never rewrites original metrics. Cluster disagreements by rule, field, mode, rationale, and obligation type; two identities under one rule fail automatically.

- [ ] **Step 4: Run the gate and all semantic-review unit tests**

Run: `python -m unittest discover -s tests -p "test_semantic_review_*.py" -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the gate**

```text
git add skills/joewrks-product-definition/downstream/semantic_review/gate.py skills/joewrks-product-definition/downstream/semantic_review/disagreement.py tests/test_semantic_review_gate.py
git commit -m "feat: enforce semantic review reliability gate"
```

### Task 8: Eight negative regressions and v0.4.2-shaped fixture

**Files:**
- Create: `tests/fixtures/semantic-review-v1/v042-instability-summary.json`
- Create: `tests/test_semantic_review_negative_regressions.py`

**Interfaces:**
- Consumes: all gate APIs
- Produces: one isolated fixture mutation per `NR-01` through `NR-08`

- [ ] **Step 1: Write eight named regression tests**

```python
EXPECTED = {
    "NR-01": {"FAIL/BRIEF_IDENTITY_MISMATCH"},
    "NR-02": {"FAIL/PACKAGE_IDENTITY_MISMATCH"},
    "NR-03": {"FAIL/RUBRIC_NORMATIVE_AMBIGUITY"},
    "NR-04": {"FAIL/IDENTITY_COVERAGE"},
    "NR-05": {"FAIL/PREVIOUS_VERDICT_EXPOSURE"},
    "NR-06": {"FAIL/PACKAGE_IDENTITY_MISMATCH"},
    "NR-07": {"FAIL/PACKAGE_IDENTITY_MISMATCH"},
    "NR-08": {"FAIL/GOLDEN_VERDICT", "FAIL/GOLDEN_RATIONALE"},
}

def test_v042_shaped_176_flip_fixture_fails_reliability(v042_run_set):
    report = evaluate_reliability_gate(*v042_run_set.args)
    assert not report["passed"]
    assert report["metrics"]["unchanged_disagreement_count"] == 176
```

- [ ] **Step 2: Run regressions against the unmutated good set and confirm fixture gaps fail**

Run: `python -m unittest tests.test_semantic_review_negative_regressions -v`

Expected: failures for missing eight mutation fixtures and v0.4.2 summary.

- [ ] **Step 3: Implement exactly eight single-variable mutations**

Create mutation helpers that deep-copy the known-good package/run set, change only the named input, and assert the source fixture hash is unchanged after evaluation. The v0.4.2 summary SHALL contain only counts and generic field families, never RMA canonical text or historical reviewer truth labels.

- [ ] **Step 4: Run negative regressions and complete semantic-review suite**

Run: `python -m unittest tests.test_semantic_review_negative_regressions -v`

Expected: exactly eight family tests plus the v0.4.2-shaped detection test pass.

Run: `python -m unittest discover -s tests -p "test_semantic_review_*.py" -v`

Expected: all semantic-review tests pass.

- [ ] **Step 5: Commit frozen regressions**

```text
git add tests/fixtures/semantic-review-v1 tests/test_semantic_review_negative_regressions.py
git commit -m "test: add semantic review reliability regressions"
```

### Task 9: Generic documentation, compatibility, and full regression verification

**Files:**
- Modify: `skills/joewrks-product-definition/downstream/README.md`
- Modify: `skills/joewrks-product-definition/downstream/references/drift-audit-procedure.md`
- Test: `tests/test_downstream_handoff.py`
- Test: all `tests/test_semantic_review_*.py`

**Interfaces:**
- Consumes: the complete semantic-review package/gate
- Produces: documented post-Closure review reliability workflow without changing runtime contract semantics

- [ ] **Step 1: Add failing documentation assertions**

```python
def test_downstream_reference_requires_semantic_review_sidecar_before_reliable_review():
    readme = (SKILL / "downstream" / "README.md").read_text(encoding="utf-8")
    assert "joewrks.semantic-review/1.0" in readme
    assert "No majority-vote escape hatch" in readme
    assert "joewrks.action-conformance/1.0 remains unchanged" in readme
```

- [ ] **Step 2: Run the documentation assertion and observe failure**

Run: `python -m unittest tests.test_downstream_handoff -v`

Expected: failure because v0.4.3 workflow text is absent.

- [ ] **Step 3: Document the sidecar authority and audit sequence**

Add a “Deterministic semantic review” section after current semantic derivation integrity. State exact package/brief hashes, field-responsibility composition, four verdicts, reliability thresholds by reference, failure preservation, and action-contract v1.0 compatibility. Extend the blind audit procedure to verify sidecar hashes and reliability-gate PASS before accepting a `REVIEW_REQUIRED` semantic review.

- [ ] **Step 4: Run full verification**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass; the existing frozen runtime regression may remain skipped only when its two documented environment variables are absent.

Run: `git diff --check`

Expected: no output and exit code 0.

Run: `git diff --exit-code efd96410f6401cbf9624328e94b795c315164b7f -- product-definition`

Expected: no output and exit code 0.

- [ ] **Step 5: Commit documentation and verification contract**

```text
git add skills/joewrks-product-definition/downstream/README.md skills/joewrks-product-definition/downstream/references/drift-audit-procedure.md tests/test_downstream_handoff.py
git commit -m "docs: define deterministic semantic review workflow"
```

## Implementation completion gate

The implementation workstream is complete only when:

- all nine tasks and their independent commits exist;
- action-contract v1.0 compiler/runtime behavior remains regression-green;
- all 15 golden cases pass at 100% verdict and rationale-code accuracy;
- all 8 negative regression families are detected;
- a real minimum-three-run calibration satisfies every threshold;
- failed calibrations remain preserved and cannot be majority-overridden;
- Product Definition and v0.4.2 evidence are unchanged;
- an independent implementation audit confirms no product-specific authority entered the generic subsystem.

This plan does not authorize implementation during the v0.4.3 specification phase.
