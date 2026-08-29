import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
WORKFLOW_PATH = SKILL_ROOT / "references" / "workflow-v0.2.0.md"
REENTRY_WORKFLOW_PATH = SKILL_ROOT / "references" / "reentry-workflow-v0.2.0.md"
REENTRY_EVENT_SCHEMA_PATH = (
    SKILL_ROOT / "downstream_v2" / "schemas" / "reentry-event.schema.json"
)


def read_if_present(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = re.match(r"^(#+)\s", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end])


def normalized(text: str) -> str:
    return " ".join(text.split())


def appears_in_order(text: str, phrases: tuple[str, ...]) -> bool:
    cursor = -1
    for phrase in phrases:
        cursor = text.find(phrase, cursor + 1)
        if cursor < 0:
            return False
    return True


def fenced_inventory(section_text: str, label: str) -> list[str]:
    match = re.search(
        rf"{re.escape(label)}\s*\n\s*```text\s*\n(.*?)\n```",
        section_text,
        flags=re.DOTALL,
    )
    return [] if match is None else [line.strip() for line in match.group(1).splitlines()]


def append_to_section(markdown: str, heading: str, sentence: str) -> str:
    original = section(markdown, heading)
    if not original:
        return markdown
    return markdown.replace(original, f"{original}\n\n{sentence}", 1)


def semantic_fragments(text: str) -> list[str]:
    return [
        fragment.strip()
        for fragment in re.split(r"(?<=[.!?;:])\s+", normalized(text))
        if fragment.strip()
    ]


def action_is_denied(fragment: str, action_start: int) -> bool:
    prefix = fragment[:action_start]
    direct_denial = re.compile(
        r"(?:\b(?:do|does|must|may|can|should|will)\s+not\b|"
        r"\bcannot\b|\bcan't\b|\bnever\b)"
        r"(?:\s+(?:be|directly|ever|automatically|provisionally|temporarily)){0,3}\s*$|"
        r"\b(?:is|are)\s+not\s+(?:permitted|allowed)\s+to(?:\s+be)?\s*$",
        flags=re.IGNORECASE,
    )
    without_action = re.compile(
        r"\bwithout(?:\s+(?:directly|ever|first|also)){0,2}\s*$",
        flags=re.IGNORECASE,
    )
    return bool(direct_denial.search(prefix) or without_action.search(prefix))


def undenied_action_fragments(text: str, action_pattern: str) -> list[str]:
    results = []
    action = re.compile(action_pattern, flags=re.IGNORECASE)
    for fragment in semantic_fragments(text):
        for match in action.finditer(fragment):
            if not action_is_denied(fragment, match.start()):
                results.append(fragment)
                break
    return results


def contains_undenied_action(text: str, action_pattern: str) -> bool:
    return bool(undenied_action_fragments(text, action_pattern))


def clear_authority_contract(route: str) -> bool:
    prose = normalized(route)
    required = (
        "Product Definition already gives one clear meaning",
        "required outcome is an implementation correction",
        "does not require a Product Definition revision or approval change",
        "Do not create a new Product Definition decision or a canonical unknown",
        "rerun the affected verification against the unchanged approved authority",
    )
    forbidden_actions = (
        r"\b(?:create|open|register|allocate|add)\b.{0,80}"
        r"(?:\bcanonical\s+unknown\b|`unk-|\bcanonical\s+`unk-)",
        r"\bincrement\b.{0,50}\bdefinition_revision\b",
        r"\bset\b.{0,40}\bapproval\b.{0,40}\bunapproved\b",
        r"\bre-enter\b.{0,40}\bproduct definition\b",
    )
    return appears_in_order(prose, required) and not any(
        contains_undenied_action(route, action) for action in forbidden_actions
    )


def route_b_contract(route: str) -> bool:
    prose = normalized(route)
    required_order = (
        "inspect and resolve the exact affected authority and evidence",
        "truthfully assess Materiality and decision authority",
        "prepare a complete V2 unknown record off-state",
        "as one canonical mutation",
        "increment `definition_revision`",
        "set approval to `UNAPPROVED`",
        "stale only affected authority and downstream dependencies",
        "register the complete `UNK-*`",
    )
    fragments = semantic_fragments(route)
    registration_action = re.compile(
        r"\b(?:register|write|commit|create|open|add|allocate)\b.{0,80}"
        r"(?:`unk-|\b(?:canonical\s+)?unknown\b)",
        flags=re.IGNORECASE,
    )
    off_state_creation = re.compile(
        r"\bcreate\b.{0,60}\bcomplete\s+(?:v2\s+)?unknown\s+record\b"
        r".{0,40}\bonly\s+off-state\b",
        flags=re.IGNORECASE,
    )
    registrations = []
    for index, fragment in enumerate(fragments):
        off_state_spans = [match.span() for match in off_state_creation.finditer(fragment)]
        for match in registration_action.finditer(fragment):
            if action_is_denied(fragment, match.start()):
                continue
            if any(start <= match.start() < end for start, end in off_state_spans):
                continue
            registrations.append(index)
            break
    atomic_transition = next(
        (index for index, fragment in enumerate(fragments) if "as one canonical mutation" in fragment),
        -1,
    )
    resulting_state_validation = next(
        (
            index
            for index, fragment in enumerate(fragments)
            if "validate the complete resulting state" in fragment
        ),
        -1,
    )
    return (
        appears_in_order(prose, required_order)
        and len(registrations) == 1
        and atomic_transition < registrations[0] < resulting_state_validation
    )


def candidate_proposal_contract(candidate_section: str) -> bool:
    prose = normalized(candidate_section)
    required = (
        "suggestion text only",
        "must never be copied directly or verbatim",
        "independently authored from the inspected evidence and ordinary V2 semantics",
    )
    content_adoption = re.compile(
        r"\b(?:copy|copied|copying|reuse|reused|adopt|adopted|transfer|transferred)\b",
        flags=re.IGNORECASE,
    )
    metadata_location_only = re.compile(
        r"\bcandidate\s+proposal\s+metadata\b.{0,50}"
        r"\b(?:use|used|using|reuse|reused|reusing)\b.{0,30}\bonly\b"
        r".{0,30}\b(?:identify|locate)\b.{0,50}\bevidence\s+inspection\b",
        flags=re.IGNORECASE,
    )
    candidate_content = re.compile(
        r"\b(?:candidate|suggested|suggestion|wording|text|content|question)\b",
        flags=re.IGNORECASE,
    )
    affirmative_candidate_adoption = False
    for fragment in semantic_fragments(candidate_section):
        metadata_spans = [match.span() for match in metadata_location_only.finditer(fragment)]
        for match in content_adoption.finditer(fragment):
            if action_is_denied(fragment, match.start()):
                continue
            if any(start <= match.start() < end for start, end in metadata_spans):
                continue
            if candidate_content.search(fragment):
                affirmative_candidate_adoption = True
                break
        if affirmative_candidate_adoption:
            break
    candidate_content_use = (
        r"(?:\bdirect\s+use\b.{0,50}\b(?:candidate|suggested|suggestion)"
        r"(?:\s+(?:wording|text|content|question))?\b|"
        r"\b(?:candidate|suggested|suggestion)\s+"
        r"(?:wording|text|content|question)\b.{0,50}"
        r"\b(?:use|used|using)\b|"
        r"\b(?:use|used|using)\b.{0,40}\b(?:candidate|suggested|suggestion)\s+"
        r"(?:wording|text|content|question)\b)"
    )
    return all(requirement in prose for requirement in required) and not (
        affirmative_candidate_adoption
        or contains_undenied_action(candidate_section, candidate_content_use)
        or contains_undenied_action(candidate_section, r"\bdirect\s+copying\b")
    )


def non_null_contract_provenance_contract(non_null_section: str) -> bool:
    prose = normalized(non_null_section)
    required = (
        "source_contract_hash` is non-null",
        "resolve the exact `joewrks.action-conformance/2.0` contract",
        "semantic_contract_hash == source_contract_hash",
        "`source_seed_inventory` and `scope_commitments` from that contract",
        "A different contract is not evidence about this event",
    )
    fallback_selection = (
        r"\b(?:use|choose|select|take|fall\s+back\s+to)\b.{0,80}"
        r"\b(?:newest|latest|most\s+recent|closest|available|different|fallback)\b"
        r".{0,40}\bcontract\b"
    )
    return appears_in_order(prose, required) and not contains_undenied_action(
        non_null_section,
        fallback_selection,
    )


def out_of_scope_contract(route: str) -> bool:
    prose = normalized(route)
    required = (
        "does not become in scope",
        "Resolve Product Definition scope first",
        "do not implement the request as approved behavior",
        "If a real material scope question remains, use Route B",
        "only after the scope decision is canonical, approved, and reflected in a current downstream contract",
    )
    premature_fragments = undenied_action_fragments(
        route,
        r"\b(?:implement|implemented|proceed|continue|start|resume|treat|expand|expands|expansion)\b",
    )
    forbidden_timing = re.compile(
        r"\b(?:provisional|provisionally|temporary|temporarily|automatic|automatically|"
        r"before\b.{0,60}\bscope\b|while\b.{0,80}\b(?:scope|product definition)\b|"
        r"\bscope\b.{0,60}\bpending\b)",
        flags=re.IGNORECASE,
    )
    explicit_no_expansion = re.compile(
        r"\bthere is no\b.{0,80}\b(?:provisional|temporary|automatic)\b"
        r".{0,80}\bexpansion\b",
        flags=re.IGNORECASE,
    )
    return appears_in_order(prose, required) and not any(
        forbidden_timing.search(fragment) and not explicit_no_expansion.search(fragment)
        for fragment in premature_fragments
    )


class V2ReentryWorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = read_if_present(SKILL_PATH)
        cls.workflow = read_if_present(WORKFLOW_PATH)
        cls.reentry = read_if_present(REENTRY_WORKFLOW_PATH)
        cls.event_schema = json.loads(read_if_present(REENTRY_EVENT_SCHEMA_PATH))

    def assert_test_method_rejects_reentry_mutation(
        self,
        test_method: str,
        mutated_reentry: str,
    ) -> None:
        probe = type(self)(methodName=test_method)
        probe.skill = self.skill
        probe.workflow = self.workflow
        probe.reentry = mutated_reentry
        probe.event_schema = self.event_schema
        result = unittest.TestResult()
        probe.run(result)
        self.assertFalse(result.errors, result.errors)
        self.assertEqual(
            len(result.failures),
            1,
            f"{test_method} accepted a prohibited in-memory document mutation",
        )

    def test_skill_says_clear_authority_runtime_bug_requires_implementation_fix_not_new_decision(self):
        skill_route = section(self.skill, "## Implementation re-entry routing")
        workflow_route = section(self.workflow, "## Re-enter only the affected scope")
        route = section(self.reentry, "## Route A — clear authority, incorrect implementation")
        self.assertIn(
            "[reentry-workflow-v0.2.0.md](references/reentry-workflow-v0.2.0.md)",
            self.skill,
        )
        self.assertIn("implementation correction required", skill_route)
        self.assertIn("do not create a new Product Definition decision", skill_route)
        self.assertIn("runtime mismatch is an implementation bug", workflow_route)
        self.assertTrue(clear_authority_contract(route))

        contradictions = (
            "The team may create a canonical unknown for this code bug.",
            "The team must create a canonical unknown before fixing the runtime.",
            "Always increment `definition_revision` for the code bug.",
            "Always set approval to `UNAPPROVED` for the code bug.",
            "Always re-enter Product Definition even though authority is clear.",
        )
        for contradiction in contradictions:
            with self.subTest(contradiction=contradiction):
                self.assertFalse(clear_authority_contract(route + "\n" + contradiction))

    def test_skill_says_semantic_gap_reenters_product_definition(self):
        skill_route = section(self.skill, "## Implementation re-entry routing")
        workflow_route = section(self.workflow, "## Re-enter only the affected scope")
        route = section(
            self.reentry,
            "## Route B — downstream semantic authority gap or real ambiguity",
        )
        self.assertIn("[reentry workflow](reentry-workflow-v0.2.0.md)", workflow_route)
        self.assertTrue(route_b_contract(route))
        for routed_section in (skill_route, workflow_route):
            with self.subTest(document=routed_section[:60]):
                self.assertIn("assess Materiality and decision authority", routed_section)
                self.assertIn("prepare a complete V2 unknown record off-state", routed_section)
                self.assertIn("as one canonical mutation", routed_section)

        first = "truthfully assess Materiality and decision authority"
        second = "prepare a complete V2 unknown record off-state"
        reversed_route = route.replace(first, "ORDER-SWAP", 1).replace(second, first, 1).replace(
            "ORDER-SWAP", second, 1
        )
        self.assertFalse(route_b_contract(reversed_route))

    def test_candidate_unknown_is_never_described_as_canonical_authority(self):
        candidate = section(self.reentry, "## Candidate proposal boundary")
        skill_route = section(self.skill, "## Implementation re-entry routing")
        workflow_route = section(self.workflow, "## Re-enter only the affected scope")
        self.assertIn("CANDIDATE_UNKNOWN_IS_NOT_CANONICAL_AUTHORITY", self.reentry)
        self.assertTrue(candidate_proposal_contract(candidate))
        self.assertIn("must never be copied directly or verbatim", skill_route)
        self.assertIn("must never be copied directly or verbatim", workflow_route)
        self.assertIn("No general-purpose state mutator", self.reentry)

        conditional_escapes = (
            "The candidate wording may be copied after review.",
            "The candidate wording can be copied after review.",
            "The candidate wording may be copied after registration.",
            "Direct copying is allowed once evidence has been inspected.",
        )
        for escape in conditional_escapes:
            with self.subTest(escape=escape):
                self.assertFalse(candidate_proposal_contract(candidate + "\n" + escape))

    def test_reentry_event_schema_parity_routes_contract_and_precontract_provenance(self):
        inspect = section(self.reentry, "## Inspect before routing")
        declared_fields = fenced_inventory(inspect, "The event payload fields are exactly:")
        schema_fields = set(self.event_schema["properties"])
        self.assertEqual(len(declared_fields), len(set(declared_fields)))
        self.assertSetEqual(set(declared_fields), schema_fields)
        self.assertNotIn("source_seed_inventory", schema_fields)
        self.assertNotIn("scope_commitments", schema_fields)

        source_contract_schema = self.event_schema["properties"]["source_contract_hash"]
        self.assertTrue(any(branch.get("type") == "null" for branch in source_contract_schema["oneOf"]))

        with_contract_section = section(inspect, "### Non-null source contract")
        with_contract = normalized(with_contract_section)
        self.assertTrue(non_null_contract_provenance_contract(with_contract_section))
        self.assertIn("semantic_contract_hash == source_contract_hash", with_contract)
        self.assertIn("`source_seed_inventory` and `scope_commitments` from that contract", with_contract)

        without_contract = normalized(section(inspect, "### Null source contract"))
        self.assertIn("pre-contract event", without_contract)
        self.assertIn("exact handoff definition", without_contract)
        self.assertIn("current Product Definition state authority and evidence", without_contract)

    def test_out_of_scope_request_requires_scope_resolution(self):
        skill_route = section(self.skill, "## Implementation re-entry routing")
        workflow_route = section(self.workflow, "## Re-enter only the affected scope")
        route = section(self.reentry, "## Route C — `OUT_OF_SCOPE_REQUEST`")
        self.assertIn("resolve Product Definition scope first", skill_route)
        self.assertIn("scope resolution comes first", workflow_route)
        self.assertTrue(out_of_scope_contract(route))

        contradictions = (
            "The implementation request expands approved scope automatically.",
            "Treat the request as in scope while Product Definition catches up.",
            "Implementation may proceed before scope resolution.",
        )
        for contradiction in contradictions:
            with self.subTest(contradiction=contradiction):
                self.assertFalse(out_of_scope_contract(route + "\n" + contradiction))

    def test_clear_authority_test_rejects_inspection_conditioned_unknown_permission(self):
        mutated = append_to_section(
            self.reentry,
            "## Route A — clear authority, incorrect implementation",
            "After inspection, the team is permitted to open a canonical `UNK-*` "
            "for this otherwise clear runtime bug.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_skill_says_clear_authority_runtime_bug_requires_implementation_fix_not_new_decision",
            mutated,
        )

    def test_route_b_test_rejects_separate_early_canonical_unknown_update(self):
        mutated = append_to_section(
            self.reentry,
            "## Route B — downstream semantic authority gap or real ambiguity",
            "Register the complete `UNK-*` in a canonical update, then perform "
            "the revision and approval transition in a second mutation.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_skill_says_semantic_gap_reenters_product_definition",
            mutated,
        )

    def test_candidate_test_rejects_review_conditioned_wording_copy_permission(self):
        mutated = append_to_section(
            self.reentry,
            "## Candidate proposal boundary",
            "Once review establishes provenance, direct use of the candidate wording "
            "is permitted.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_candidate_unknown_is_never_described_as_canonical_authority",
            mutated,
        )

    def test_non_null_contract_test_rejects_newest_contract_fallback(self):
        mutated = append_to_section(
            self.reentry,
            "### Non-null source contract",
            "If no exact hash match is available, use the newest action contract "
            "as the event source.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_reentry_event_schema_parity_routes_contract_and_precontract_provenance",
            mutated,
        )

    def test_out_of_scope_test_rejects_provisional_implementation_while_pending(self):
        mutated = append_to_section(
            self.reentry,
            "## Route C — `OUT_OF_SCOPE_REQUEST`",
            "Implementation can continue provisionally while the scope decision is pending.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_out_of_scope_request_requires_scope_resolution",
            mutated,
        )

    def test_clear_authority_test_rejects_unrelated_without_before_unknown_permission(self):
        mutated = append_to_section(
            self.reentry,
            "## Route A — clear authority, incorrect implementation",
            "Without delay, the team is permitted to open a canonical `UNK-*` "
            "for this otherwise clear runtime bug.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_skill_says_clear_authority_runtime_bug_requires_implementation_fix_not_new_decision",
            mutated,
        )

    def test_route_b_test_rejects_unrelated_without_before_early_unknown_write(self):
        mutated = append_to_section(
            self.reentry,
            "## Route B — downstream semantic authority gap or real ambiguity",
            "Without changing any evidence, register the complete `UNK-*` in a "
            "canonical update before the revision transition.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_skill_says_semantic_gap_reenters_product_definition",
            mutated,
        )

    def test_candidate_test_rejects_unrelated_without_before_wording_copy(self):
        mutated = append_to_section(
            self.reentry,
            "## Candidate proposal boundary",
            "Without changing any evidence, direct use of the candidate wording "
            "is permitted.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_candidate_unknown_is_never_described_as_canonical_authority",
            mutated,
        )

    def test_non_null_contract_test_rejects_unrelated_without_before_newest_fallback(self):
        mutated = append_to_section(
            self.reentry,
            "### Non-null source contract",
            "Without additional validation, use the newest action contract as the "
            "event source when the exact hash match is unavailable.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_reentry_event_schema_parity_routes_contract_and_precontract_provenance",
            mutated,
        )

    def test_out_of_scope_test_rejects_unrelated_without_before_provisional_work(self):
        mutated = append_to_section(
            self.reentry,
            "## Route C — `OUT_OF_SCOPE_REQUEST`",
            "Without delay, implementation can continue provisionally while the "
            "scope decision is pending.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_out_of_scope_request_requires_scope_resolution",
            mutated,
        )

    def test_candidate_allows_read_only_use_to_locate_evidence_inspection(self):
        candidate = section(self.reentry, "## Candidate proposal boundary")
        positive_control = (
            candidate
            + "\nCandidate proposal metadata may be used only to identify where evidence "
            "inspection is needed, but it must never supply Product Definition "
            "wording or authority."
        )
        self.assertTrue(candidate_proposal_contract(positive_control))

    def test_clear_authority_test_rejects_never_hesitate_unknown_permission(self):
        mutated = append_to_section(
            self.reentry,
            "## Route A — clear authority, incorrect implementation",
            "Never hesitate to open a canonical `UNK-*` for this otherwise clear "
            "runtime bug.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_skill_says_clear_authority_runtime_bug_requires_implementation_fix_not_new_decision",
            mutated,
        )

    def test_route_b_test_rejects_never_hesitate_early_unknown_write(self):
        mutated = append_to_section(
            self.reentry,
            "## Route B — downstream semantic authority gap or real ambiguity",
            "Never hesitate to register the complete `UNK-*` in a canonical update "
            "before the revision transition.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_skill_says_semantic_gap_reenters_product_definition",
            mutated,
        )

    def test_candidate_test_rejects_never_hesitate_content_use(self):
        mutated = append_to_section(
            self.reentry,
            "## Candidate proposal boundary",
            "Never hesitate to use the candidate wording as Product Definition content.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_candidate_unknown_is_never_described_as_canonical_authority",
            mutated,
        )

    def test_non_null_contract_test_rejects_never_hesitate_newest_fallback(self):
        mutated = append_to_section(
            self.reentry,
            "### Non-null source contract",
            "Never hesitate to use the newest action contract as the event source "
            "when the exact hash match is unavailable.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_reentry_event_schema_parity_routes_contract_and_precontract_provenance",
            mutated,
        )

    def test_out_of_scope_test_rejects_never_hesitate_provisional_work(self):
        mutated = append_to_section(
            self.reentry,
            "## Route C — `OUT_OF_SCOPE_REQUEST`",
            "Never hesitate to continue implementation provisionally while the scope "
            "decision is pending.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_out_of_scope_request_requires_scope_resolution",
            mutated,
        )

    def test_candidate_allows_metadata_reuse_only_to_locate_evidence_inspection(self):
        candidate = section(self.reentry, "## Candidate proposal boundary")
        positive_control = (
            candidate
            + "\nCandidate proposal metadata may be reused only to identify where evidence "
            "inspection is needed; it must never supply Product Definition wording "
            "or authority."
        )
        self.assertTrue(candidate_proposal_contract(positive_control))

    def test_candidate_test_rejects_reviewed_question_used_verbatim(self):
        mutated = append_to_section(
            self.reentry,
            "## Candidate proposal boundary",
            "The candidate question may be used verbatim after review as the user question.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_candidate_unknown_is_never_described_as_canonical_authority",
            mutated,
        )

    def test_candidate_metadata_exemption_does_not_hide_compound_wording_copy(self):
        mutated = append_to_section(
            self.reentry,
            "## Candidate proposal boundary",
            "Candidate proposal metadata may be reused only to identify where evidence "
            "inspection is needed, and candidate wording may be copied verbatim after review.",
        )
        self.assert_test_method_rejects_reentry_mutation(
            "test_candidate_unknown_is_never_described_as_canonical_authority",
            mutated,
        )

    def test_candidate_allows_directly_attached_not_permitted_copy_denial(self):
        candidate = section(self.reentry, "## Candidate proposal boundary")
        positive_control = (
            candidate
            + "\nCandidate wording is not permitted to be copied into Product Definition "
            "authority."
        )
        self.assertTrue(candidate_proposal_contract(positive_control))

    def test_route_b_allows_complete_unknown_creation_only_off_state(self):
        route = section(
            self.reentry,
            "## Route B — downstream semantic authority gap or real ambiguity",
        )
        positive_control = (
            route
            + "\nCreate the complete unknown record only off-state; it is not canonical "
            "authority."
        )
        self.assertTrue(route_b_contract(positive_control))


if __name__ == "__main__":
    unittest.main()
