"""JOEFLOW 2.0.2 builders: resolve, requirement --from-decisions, topology-on/-off, edit, grouped questions.

Friction from the ATELIER run (TOOL-FRICTION.md JOEFLOW 1-15; review bundles A, B, C, D, G):
closing an existing question, turning a topology domain on and closing a surface each needed
ad-hoc Python; builders and validator disagreed on decision authority.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import decision_policy  # noqa: E402
from grill_v2 import derive_decision_authority  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402


def _run(script, *args, cwd):
    result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args)], cwd=cwd,
                            capture_output=True, stdin=subprocess.DEVNULL, check=False)
    return result.returncode, result.stdout.decode("utf-8")


class BuilderFlowTest(unittest.TestCase):
    """The template to an OPEN money pack, then every axis answered and the surface closed."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)
        shutil.copyfile(SKILL / "templates" / "state-v0.2.0.example.json", self.dir / "state.json")

    def nr(self, patch, *args, expect=0):
        code, out = _run("new_records.py", "--state", "state.json", "--patch", patch, *args, cwd=self.dir)
        self.assertEqual(code, expect, out)
        return json.loads(out)

    def apply(self, patch, status="OPEN"):
        code, out = _run("open_revision.py", "state.json", "--patch", patch, "--status", status, "--write", cwd=self.dir)
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def state(self):
        return json.loads((self.dir / "state.json").read_text(encoding="utf-8"))

    def money_on(self):
        self.nr("p2.json", "evidence", "--id", "EVD-001", "--source-kind", "USER_CONFIRMED_INTENT", "--class", "INTENT",
                "--locator", "chat", "--claim", "One item sold to a guest buyer.")
        for unknown, option in (("UNK-902", "OPT-MONEY-ON"), ("UNK-901", "OPT-AUTH-OFF"), ("UNK-903", "OPT-UPLOAD-OFF"),
                                ("UNK-904", "OPT-ASYNC-OFF"), ("UNK-905", "OPT-PERM-OFF"), ("UNK-906", "OPT-DESTR-OFF")):
            self.nr("p2.json", "resolve", unknown, "--option", option, "--words", "money yes, the rest no")
        report = self.nr("p2.json", "topology-on", "DEC-001", "--new-surface", "SURF-001", "--name", "Checkout")
        for decision in ("DEC-002", "DEC-003", "DEC-004", "DEC-005", "DEC-006"):
            self.nr("p2.json", "topology-off", decision, "--rationale", "The user said the product has none.")
        self.apply("p2.json")
        return report

    def test_template_starts_open_and_validates(self):
        state = self.state()
        self.assertEqual(validate_state_v2(state), [])
        self.assertEqual(state["evidence"], [])
        self.assertEqual({cell["status"] for cell in state["surface_manifest"]["grill_profile"].values()}, {"OPEN"})

    def test_topology_on_writes_surface_row_and_one_question_per_axis(self):
        report = self.money_on()
        self.assertEqual(report["rows"], ["grill_coverage[SURF-001]"])
        state = self.state()
        self.assertEqual(state["surface_manifest"]["grill_profile"]["MONEY"]["status"], "ACTIVE")
        surface = next(s for s in state["surface_manifest"]["records"] if s["id"] == "SURF-001")
        self.assertEqual(surface["kind"], "MONEY_FLOW")
        axes = [u for u in state["objects"]["unknowns"] if u["origin"]["kind"] == "GRILL_PACK_AXIS"]
        self.assertEqual(len(axes), 12)
        self.assertEqual(len({u["origin"]["axis_id"] for u in axes}), 12)
        self.assertEqual([u["id"] for u in axes][0], "UNK-001")  # the template's 900 range is not the project's sequence
        self.assertEqual(state["grill_coverage"][0]["pack_id"], "GRILL-MONEY-1")
        topology = [d for d in state["objects"]["decisions"] if d["source_unknown_refs"][0] == "UNK-902"][0]
        self.assertEqual(topology["resolution_mode"], "USER_DECISION")  # high risk: money
        self.assertEqual(state["surface_manifest"]["grill_profile"]["AUTH"]["status"], "N/A")

    def test_grouped_questions_then_accept_recommended_then_requirement(self):
        self.money_on()
        state = self.state()
        axes = {u["origin"]["axis_id"]: u["id"] for u in state["objects"]["unknowns"] if u["origin"]["kind"] == "GRILL_PACK_AXIS"}
        for axis, unknown in axes.items():
            code, out = _run("new_records.py", "--state", "state.json", "--patch", "p3.json", "--replace", "question",
                             "--unknown", unknown, "--pack", "GRILL-MONEY-1", "--axis", axis, "--surface", "SURF-001",
                             "--question", f"{axis}?", "--why", "It decides the checkout.", "--affects", "SURF-001",
                             "--option", "OPT-A=Simple|Built", "--option", "OPT-B=Rich|Built after launch",
                             "--materiality", "MEDIUM,MULTI_OBJECT,true,REVERSIBLE,money",
                             "--recommend", "OPT-A", "--reason", "EVD-001", "--tradeoff", "Rich is out of scope.", cwd=self.dir)
            self.assertEqual(code, 0, out)
        self.apply("p3.json")
        code, out = _run("next_product_question.py", "state.json", "--grouped", cwd=self.dir)
        self.assertEqual(code, 0, out)
        groups = json.loads(out)["groups"]
        self.assertEqual(len(groups), 1)
        self.assertTrue(groups[0]["present_as_one_table"])
        self.assertIn("--accept-recommended --pack GRILL-MONEY-1", groups[0]["record_all_as_recommended"])
        report = self.nr("p4.json", "resolve", "--accept-recommended", "--pack", "GRILL-MONEY-1", "--words", "all as recommended")
        self.assertEqual(len([r for r in report["added"] if r.startswith("DEC-")]), 12)
        self.assertEqual(len(report["cells"]), 12)
        self.assertEqual({d["resolution_mode"] for d in report["derived"]}, {"USER_DECISION"})  # money axes are high risk
        self.assertEqual(report["surfaces_left_without_open_question"][0]["surface"], "SURF-001")
        req = self.nr("p4.json", "requirement", "--from-decisions", ",".join(f"DEC-{n:03d}" for n in range(7, 19)),
                      "--surface", "SURF-001", "--requirement", "REQ-001", "--ui-required", "false")
        self.assertEqual(req["added"], ["REQ-001"])
        self.apply("p4.json")
        state = self.state()
        surface = next(s for s in state["surface_manifest"]["records"] if s["id"] == "SURF-001")
        self.assertEqual((surface["status"], surface["authority_refs"]), ("IN_SCOPE", ["REQ-001"]))
        self.assertEqual({cell["status"] for cell in state["grill_coverage"][0]["axes"].values()}, {"ADDRESSED"})

    def test_resolve_cleans_blocks_and_refuses_twice(self):
        self.money_on()
        state = self.state()
        first, second = [u["id"] for u in state["objects"]["unknowns"] if u["origin"]["kind"] == "GRILL_PACK_AXIS"][:2]
        self.nr("p3.json", "edit", second, "--set-json", "/blocks_unknown_refs", json.dumps([first]))
        self.apply("p3.json")
        report = self.nr("p4.json", "resolve", first, "--option", "OPT-SPECIFY", "--words", "yes")
        self.assertIn(second, report["changed"])
        self.assertTrue(any("blocks_unknown_refs" in note for note in report["notes"]))
        self.apply("p4.json")
        again = self.nr("p5.json", "resolve", first, "--option", "OPT-SPECIFY", "--words", "yes", expect=1)
        self.assertIn("not OPEN", again["error"])

    def test_edit_refuses_ambiguous_text_and_rederives_authority(self):
        self.money_on()
        unknown = [u for u in self.state()["objects"]["unknowns"] if u["origin"]["kind"] == "GRILL_PACK_AXIS"][0]["id"]
        bad = self.nr("p3.json", "edit", unknown, "--replace-text", "OPT", "X", expect=1)
        self.assertIn("exactly once", bad["error"])
        report = self.nr("p3.json", "edit", unknown, "--set-json", "/materiality/risk_flags/money", "false",
                         "--set", "/materiality/reversibility", "TRIVIALLY_REVERSIBLE",
                         "--set", "/materiality/outcome_divergence", "LOW", "--set", "/materiality/fan_out", "LOCAL")
        self.assertTrue(any("AGENT_AUTONOMOUS" in note for note in report["notes"]), report)


class PolicyTest(unittest.TestCase):
    """C: the builders call the validator's derivation and refuse what it does not allow."""

    def unknown(self, **materiality):
        base = {"outcome_divergence": "HIGH", "fan_out": "MULTI_FLOW", "user_visible": True, "reversibility": "REVERSIBLE"}
        base.update(materiality)
        flags = base.pop("flags", ())
        import record_builders as build
        return build.unknown("UNK-001", question="q?", why="w", category="CORE_FLOW",
                             options=[build.option("OPT-A", "a", "x"), build.option("OPT-B", "b", "y")], affects=[],
                             evidence_refs=[], rec=build.recommendation("OPT-A", ["REQ-001"], ["t"]),
                             mat=build.materiality(base["outcome_divergence"], base["fan_out"], base["user_visible"],
                                                   base["reversibility"], flags))

    def test_builder_authority_is_the_validator_derivation(self):
        for kwargs in ({}, {"reversibility": "COSTLY_TO_REVERSE"}, {"flags": ("security",)}):
            record = self.unknown(**kwargs)
            self.assertEqual(record["decision_authority"], derive_decision_authority(record, evidence_index={}))
        self.assertEqual(self.unknown(reversibility="COSTLY_TO_REVERSE")["decision_authority"], "USER_DECISION_REQUIRED")

    def test_accepted_refused_when_user_decision_required(self):
        record = self.unknown(flags=("money",))
        with self.assertRaises(decision_policy.PolicyError) as caught:
            decision_policy.user_resolution(record, "OPT-A", {}, accepted=True)
        self.assertIn("USER_DECISION_REQUIRED", str(caught.exception))
        self.assertIn("money", str(caught.exception))
        self.assertEqual(decision_policy.user_resolution(record, "OPT-A", {})[0], "USER_DECISION")
        self.assertEqual(decision_policy.user_resolution(self.unknown(), "OPT-A", {})[0], "USER_ACCEPTED_RECOMMENDATION")
        self.assertEqual(decision_policy.user_resolution(self.unknown(), "OPT-B", {})[0], "USER_DECISION")

    def test_evidence_answered_question_is_not_resolved_by_the_user(self):
        record = self.unknown()
        record["evidence_refs"] = ["EVD-001"]
        index = {"EVD-001": {"id": "EVD-001", "status": "CURRENT", "source_kind": "USER_CONFIRMED_INTENT",
                             "authority_classes": ["INTENT"], "confidence": "DIRECT", "locator": "chat", "claim": "c",
                             "observed_version": None, "content_hash": None}}
        with self.assertRaises(decision_policy.PolicyError) as caught:
            decision_policy.user_resolution(record, "OPT-A", index)
        self.assertIn("EVIDENCE_RESOLVABLE", str(caught.exception))

    def test_materiality_claim_and_unknown_flag(self):
        with self.assertRaises(decision_policy.PolicyError) as caught:
            decision_policy.materiality("LOW", "LOCAL", False, "TRIVIALLY_REVERSIBLE", claimed="MATERIAL")
        self.assertIn("NON_MATERIAL", str(caught.exception))
        with self.assertRaises(decision_policy.PolicyError):
            decision_policy.materiality("LOW", "LOCAL", False, "TRIVIALLY_REVERSIBLE", ("monye",))


class OpenRevisionProfileKeyTest(unittest.TestCase):
    def test_grill_profile_is_a_patch_key_and_rejects_unknown_domains(self):
        from revision_v2 import RevisionError, apply_patch
        state = json.loads((SKILL / "templates" / "state-v0.2.0.example.json").read_text(encoding="utf-8"))
        cell = {"status": "N/A", "surface_refs": [], "unknown_refs": [], "basis_refs": [], "rationale": "r"}
        report = apply_patch(state, {"grill_profile": {"MONEY": cell}})
        self.assertEqual(report["grill_profile"], ["MONEY"])
        self.assertEqual(state["surface_manifest"]["grill_profile"]["MONEY"], cell)
        with self.assertRaises(RevisionError):
            apply_patch(state, {"grill_profile": {"PAYMENTS": cell}})


if __name__ == "__main__":
    unittest.main()
