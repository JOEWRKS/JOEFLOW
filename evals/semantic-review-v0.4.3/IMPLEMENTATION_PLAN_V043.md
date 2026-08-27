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
- The responsibility profile covers exactly 26 action plus 12 lifecycle `semanticField` properties (38 semantic rules). Lifecycle `superseded_sentinels` remains a raw provenance array under `PR-P01`; it never becomes a semantic identity or `FR-L*` rule.
- Reliability coefficients, prevalence classification, display values, and threshold comparisons use exact reduced rational arithmetic; binary floating point and pre-decision rounding are forbidden.
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

def test_package_rejects_active_superseded_lifecycle_sentinel(package_root):
    contract = load_contract(package_root)
    sentinel = contract["lifecycles"][0]["superseded_sentinels"][0]
    sentinel["source_status"] = "SUPERSEDED"
    sentinel["active"] = True
    write_contract_and_rehash(package_root, contract)
    with self.assertRaisesRegex(PackageError, "ACTIVE_SUPERSEDED_SOURCE"):
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

Verify every declared byte size/hash, exact required role count, manifest hash, package hash, declared `previous_reviewer_verdicts_present: false`, and forbidden file scan before parsing semantic content. Then apply provenance-only rule `PR-P01` to each raw lifecycle `superseded_sentinels` source record. An active record with `source_status: SUPERSEDED` raises `PackageError("ACTIVE_SUPERSEDED_SOURCE", ...)` before semantic review; no responsibility rule or review identity is created for that array.

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
    assert len(profile["action"]) == 26
    assert len(profile["lifecycle"]) == 12
    assert "superseded_sentinels" not in profile["lifecycle"]

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

- [ ] **Step 3: Implement the 26 action and 12 lifecycle responsibility rules**

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

The JSON artifact SHALL copy every `FR-A01`–`FR-A26` and `FR-L01`–`FR-L12` rule from `FIELD_RESPONSIBILITY_MATRIX.md`, include a `rubric_calibration_revision`, and include allowed sibling rules, omission codes, and overreach codes. It SHALL contain exactly 38 semantic responsibility rules. `PR-P01` belongs to package/provenance validation in Task 2 and SHALL NOT appear as a semantic-field owner.

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

def test_output_rejects_synthetic_lifecycle_sentinel_identity(valid_package, valid_output):
    synthetic = copy.deepcopy(valid_output["records"][0])
    synthetic.update({
        "owner_kind": "lifecycle",
        "semantic_field": "superseded_sentinels",
        "review_identity": f"lifecycle:{synthetic['owner_id']}:superseded_sentinels",
    })
    valid_output["records"].append(synthetic)
    with self.assertRaisesRegex(OutputError, "OUTPUT_SCHEMA_VIOLATION"):
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

The output schema SHALL enumerate exactly the 38 semantic field names and exactly `FR-A01`–`FR-A26` plus `FR-L01`–`FR-L12`. `superseded_sentinels`, `PR-P01`, and `FR-L13` are schema-ineligible; the Python validator additionally enforces the owner-kind/field/rule tuple against the hash-bound identity inventory.

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
    assert report["verdict_accuracy"] == Fraction(1, 1)
    assert report["rationale_code_accuracy"] < Fraction(1, 1)
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
    return {
        "verdict_accuracy": Fraction(verdict_hits, count),
        "rationale_code_accuracy": Fraction(rationale_hits, count),
    }
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
- Produces: `MetricResult(value: Fraction | None, null_reason: str | None)`
- Produces: `cohen_kappa(left: list[str], right: list[str]) -> MetricResult`
- Produces: `fleiss_kappa(runs: list[list[str]]) -> MetricResult`
- Produces: `gwet_ac1(runs: list[list[str]]) -> MetricResult`
- Produces: `minority_class_agreement(runs: list[list[str]]) -> MetricResult`
- Produces: `is_balanced(runs: list[list[str]], floor: Fraction = Fraction(1, 20)) -> bool`
- Produces: `format_metric(value: Fraction, places: int = 6) -> str`
- Produces: `serialize_metric(result: MetricResult) -> dict[str, Any]`

- [ ] **Step 1: Write hand-calculated deterministic statistic vectors**

```python
from fractions import Fraction

A, R = "APPROVED", "REJECTED_CANDIDATE"

def test_balanced_disagreement_vector_exact_readback():
    runs = [
        [A, A, R, R],
        [A, R, R, R],
        [A, A, R, R],
    ]
    assert is_balanced(runs)
    assert [item.value for item in pairwise_cohen_kappas(runs)] == [Fraction(1, 2), Fraction(1, 1), Fraction(1, 2)]
    assert fleiss_kappa(runs).value == Fraction(23, 35)
    assert gwet_ac1(runs).value == Fraction(25, 37)
    assert minority_class_agreement(runs).value == Fraction(1, 2)
    assert format_metric(Fraction(23, 35)) == "0.657143"
    assert format_metric(Fraction(25, 37)) == "0.675676"

def test_imbalanced_prevalence_vector_exact_readback():
    runs = [[A] * 20 + [R], [A] * 20 + [R], [A] * 21]
    assert not is_balanced(runs)
    assert [item.value for item in pairwise_cohen_kappas(runs)] == [Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)]
    assert fleiss_kappa(runs).value == Fraction(59, 122)
    assert gwet_ac1(runs).value == Fraction(3599, 3725)
    assert minority_class_agreement(runs).value == Fraction(0, 1)
    assert format_metric(Fraction(59, 122)) == "0.483607"
    assert format_metric(Fraction(3599, 3725)) == "0.966174"

def test_all_one_class_has_frozen_null_semantics():
    runs = [[A] * 4, [A] * 4, [A] * 4]
    assert not is_balanced(runs)
    pairs = pairwise_cohen_kappas(runs)
    assert [item.value for item in pairs] == [None, None, None]
    assert {item.null_reason for item in pairs} == {"ALL_ONE_CLASS_CHANCE_DENOMINATOR"}
    assert fleiss_kappa(runs) == MetricResult(None, "ALL_ONE_CLASS_CHANCE_DENOMINATOR")
    assert gwet_ac1(runs).value == Fraction(1, 1)
    assert minority_class_agreement(runs) == MetricResult(None, "MINORITY_CLASS_UNOBSERVED")

def test_perfect_balanced_vector_exposes_minority_tie_diagnostic():
    runs = [[A, A, R, R]] * 3
    assert is_balanced(runs)
    assert [item.value for item in pairwise_cohen_kappas(runs)] == [Fraction(1, 1)] * 3
    assert fleiss_kappa(runs).value == Fraction(1, 1)
    assert gwet_ac1(runs).value == Fraction(1, 1)
    assert minority_class_agreement(runs) == MetricResult(None, "NO_UNIQUE_MINORITY")
```

For the balanced disagreement vector, `P_bar = 5/6`, pooled category shares are `5/12` and `7/12`, Fleiss `P_e = 37/72`, and Fleiss kappa is `(5/6 - 37/72)/(1 - 37/72) = 23/35`. Gwet `P_e = 35/72`, so AC1 is `(5/6 - 35/72)/(1 - 35/72) = 25/37`. The pooled minority is `APPROVED`; it appears at two identities and is unanimous at one, so minority agreement is `1/2`.

For the imbalanced vector, `P_bar = 61/63`, pooled category shares are `61/63` and `2/63`, Fleiss `P_e = 3725/3969`, and Fleiss kappa is `59/122`. Gwet `P_e = 244/3969`, so AC1 is `3599/3725`. The pooled minority is `REJECTED_CANDIDATE`; it appears at one identity and is not unanimous, so minority agreement is `0`. The third review's minority share is `0 < 1/20`, making the vector imbalanced.

- [ ] **Step 2: Run statistics tests and observe missing API failure**

Run: `python -m unittest tests.test_semantic_review_statistics -v`

Expected: import failures for statistic functions.

- [ ] **Step 3: Implement the exact frozen pairwise, multi-rater, AC1, minority, balance, and display formulas**

Follow `RELIABILITY_GATE_SPEC.md` §§6–7 literally. First require exact identity-set equality, then sort and align that exact set before extracting the two verdict categories. Use `fractions.Fraction` for every intermediate and every non-null `MetricResult.value`; never convert to float. Reject missing/extra/duplicate identities, unknown verdicts, fewer than three runs for set-level metrics, and empty populations. A structural or review-error verdict makes the metric set null and fails the gate; it is never a third category.

```python
@dataclass(frozen=True)
class MetricResult:
    value: Fraction | None
    null_reason: str | None = None

    def __post_init__(self):
        if (self.value is None) == (self.null_reason is None):
            raise ValueError("exactly one of value or null_reason is required")

def minority_class_agreement(runs):
    candidate_classes = ("APPROVED", "REJECTED_CANDIDATE")
    pooled = Counter(value for run in runs for value in run)
    if pooled[candidate_classes[0]] == pooled[candidate_classes[1]]:
        return MetricResult(None, "NO_UNIQUE_MINORITY")
    minority = min(candidate_classes, key=lambda key: pooled[key])
    if pooled[minority] == 0:
        return MetricResult(None, "MINORITY_CLASS_UNOBSERVED")
    detected = [index for index in range(len(runs[0])) if any(run[index] == minority for run in runs)]
    if not detected:
        return MetricResult(None, "MINORITY_CLASS_UNOBSERVED")
    unanimous = sum(all(run[index] == minority for run in runs) for index in detected)
    return MetricResult(Fraction(unanimous, len(detected)), None)
```

Implement Cohen's kappa for every unordered reviewer pair with pair-specific marginals; a zero `1 - P_e` denominator yields `null/ALL_ONE_CLASS_CHANCE_DENOMINATOR`. Implement Fleiss' kappa with `P_i = sum_c n_ic(n_ic-1)/(m(m-1))`, `P_bar = sum_i P_i/N`, and pooled `P_e = sum_c p_c^2`; its zero denominator yields the same null reason. Implement the one required multi-rater unweighted nominal Gwet AC1 variant with the same `P_bar` and `P_e = sum_c p_c(1-p_c)/(K-1)` for frozen `K=2`; do not substitute another AC1/AC2 or weighted definition. If AC1's denominator is zero, return its named null reason, though the frozen all-one case has `P_e=0` and AC1 exactly `1`.

For balance, calculate every reviewer/category share exactly and classify balanced iff all shares are `>= Fraction(1, 20)`; equality is balanced. `serialize_metric` stores a non-null reduced numerator/denominator and the six-decimal string from `format_metric`, or stores JSON null plus the stable `null_reason`. Half-even display rounding is derived by integer quotient/remainder arithmetic and never feeds a gate decision.

Add edge tests for empty populations, fewer than three reviewers, mismatched identity sets, identity permutation/alignment, unexpected error verdicts, all-one categories, pooled ties, unobserved minority, equality at `1/20`, and one count below `1/20`. Every required null has a stable reason code and fails its selected gate branch.

- [ ] **Step 4: Run statistics tests**

Run: `python -m unittest tests.test_semantic_review_statistics -v`

Expected: all tests pass, including the exact fractions, null reason codes, alignment failures, edge classifications, and six-decimal displays above.

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
    assert len({record["review_identity"] for record in targets}) == 2
    for record in targets:
        replace_verdict_and_recount(valid_run_set.outputs[2], record["review_identity"], "REJECTED_CANDIDATE", "MISSING_OWNED_SEMANTIC")
    classifications = [
        reviewer_execution_error(
            record["review_identity"],
            target_rule,
            interpretation="incorrectly required sibling-owned semantics in this LOCAL field",
        )
        for record in targets
    ]
    report = evaluate_reliability_gate(*valid_run_set.args, classifications=classifications)
    assert not report["passed"]
    assert "FAIL/RESPONSIBILITY_RULE_INSTABILITY" in report["failures"]
    assert "FAIL/RUBRIC_NORMATIVE_AMBIGUITY" not in report["failures"]
```

- [ ] **Step 2: Run gate tests and observe missing API failure**

Run: `python -m unittest tests.test_semantic_review_gate -v`

Expected: import failure for `evaluate_reliability_gate`.

- [ ] **Step 3: Implement every threshold as a conjunctive gate**

```python
THRESHOLDS = {
    "minimum_runs": 3,
    "golden_verdict_accuracy": Fraction(1, 1),
    "golden_rationale_code_accuracy": Fraction(1, 1),
    "unanimity": Fraction(99, 100),
    "balanced_kappa": Fraction(9, 10),
    "imbalanced_ac1": Fraction(19, 20),
    "minority_class_agreement": Fraction(19, 20),
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

Compute unchanged identities from exact semantic/provenance/rule/mode/obligation hashes. For more than three runs, compute three-review unanimity for every three-run combination and gate on the minimum. Compute pairwise Cohen kappa for every pair and Fleiss kappa/Gwet AC1 across all reviewers using the exact `Fraction` values from Task 6. The balanced branch requires every pair and Fleiss to be non-null and `>= 9/10`; the imbalanced branch requires Gwet AC1 and minority agreement to be non-null and `>= 19/20`. A required null fails the selected branch, including all-one AC1 `1` with null minority agreement. Require one exact closed-code classification for every verdict or rationale disagreement; missing/uncertain classifications are `UNRESOLVED_NORMATIVE`, and adjudication never rewrites original metrics. A single sibling-duplication mistake that is mechanically resolved by an existing responsibility rule is `REVIEWER_EXECUTION_ERROR`, not normative ambiguity. Cluster disagreements by responsibility rule for the zero-repetition gate and additionally record the exact interpretation for diagnosis. Any two distinct disagreement identities under one rule fail `FAIL/RESPONSIBILITY_RULE_INSTABILITY`; `NR-03` freezes the determinate subcase in which both carry the same incorrect sibling-duplication interpretation.

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
    "NR-03": {"FAIL/RESPONSIBILITY_RULE_INSTABILITY"},
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

- [ ] **Step 3: Implement exactly eight controlled regression-family mutations**

Create mutation helpers that deep-copy the known-good package/run set, apply only the named regression-family stimulus, and assert the source fixture hash is unchanged after evaluation. `NR-03` is one controlled repeated-interpretation family: on a frozen balanced base with at least 200 unchanged identities and coefficient headroom, mutate exactly two distinct identities governed by the same responsibility rule in one review, attach the same incorrect sibling-duplication interpretation and a determinate `REVIEWER_EXECUTION_ERROR` classification to each, and prove the gate emits only `FAIL/RESPONSIBILITY_RULE_INSTABILITY` while unanimity remains `>= 99%`, balanced coefficients remain above threshold, and normative ambiguity remains absent. Preserve `G-003`, `G-005`, and `G-008` as the positive composition-sensitivity proof that a single correct sibling reference remains acceptable. The v0.4.2 summary SHALL contain only counts and generic field families, never RMA canonical text or historical reviewer truth labels.

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
