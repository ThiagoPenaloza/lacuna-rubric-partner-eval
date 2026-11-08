"""Synthetic tests of the grading mechanism; they do not measure model performance."""
import copy
import json
from pathlib import Path
import unittest

from metagrader import grade


TASKS = json.loads(Path(__file__).with_name("tasks.json").read_text(encoding="utf-8"))["tasks"]


def finding(kind, evidence, impact, suggestion, question="", criterion_ref="C1"):
    return dict(kind=kind, criterion_ref=criterion_ref, evidence=evidence,
                impact=impact, question=question, suggestion=suggestion, confidence="high")


POSITIVES = [
    dict(status="review_ready", human_decision_required=True, findings=[
        finding("omission", "start time", "Without the start time, the timeline cannot be verified.",
                "Proposal: records the start time of the incident."),
        finding("omission", "the impact on users, and the recovery action",
                "Without impact and recovery, neither the scope nor the resolution is known.",
                "Proposal, as separate criteria: describes the observable impact on users and records the recovery action and its outcome.")]),
    dict(status="needs_context", human_decision_required=True, findings=[
        finding("insufficient_context", "useful to the customer",
                "Without knowing the need, usefulness cannot be judged.", "",
                "Which need or outcome defines usefulness for the customer?")]),
    dict(status="review_ready", human_decision_required=True, findings=[
        finding("ambiguity", "quickly", "Quickly gives neither a limit nor a unit.",
                "Proposal: resolves the problem within 2 business days.")]),
    dict(status="review_ready", human_decision_required=True, findings=[
        finding("ambiguity", "The rubric is vague; be more specific.",
                "The previous feedback does not locate a problem in C1/C2 or say how to verify the criteria.",
                "Proposal: indicate the textual evidence that satisfies C1 and C2, with an absence rule for each criterion.",
                criterion_ref="previous feedback on C1/C2")]),
    dict(status="review_ready", human_decision_required=True, findings=[
        finding("omission", "valid ISO dates must become a date object",
                "C1 is not observable and does not distinguish success from failure.",
                "Proposal: valid ISO input produces the expected date object."),
        finding("omission", "an invalid format must return an explicit error without terminating the process",
                "C1 does not check the error return or continuity on invalid input.",
                "Proposal: invalid input returns an explicit error and the process continues.")]),
    dict(status="review_ready", human_decision_required=True, findings=[
        finding("omission", "deadline of up to 2 business days",
                "The author already accepted the next action in C1; only the deadline is still absent from the current version.",
                "Proposal: states a deadline of up to 2 business days.", criterion_ref="remaining deadline")]),
]


class MetagraderTests(unittest.TestCase):
    def check_response(self, index, response):
        return grade(TASKS[index], json.dumps(response, ensure_ascii=False))

    def test_six_v2_fixtures(self):
        self.assertEqual(len(TASKS), 6)
        self.assertEqual(len(POSITIVES), 6)
        self.assertEqual({task["expected_findings"][0]["kind"] for task in TASKS},
                         {"omission", "insufficient_context", "ambiguity"})
        for task in TASKS:
            self.assertTrue({"goal", "context", "rubric_draft"} <= task["input"].keys())

    def test_positive_fixtures(self):
        for index, response in enumerate(POSITIVES):
            with self.subTest(task=TASKS[index]["id"]):
                report = self.check_response(index, response)
                self.assertTrue(report["format"]["passed"])
                self.assertTrue(report["content"]["passed"], report)

    def test_invalid_json_and_nonstandard_constants(self):
        for raw in ("not json", "{} trailing", '{"status": NaN}', '{"x":1,"x":2}', "[]"):
            with self.subTest(raw=raw):
                report = grade(TASKS[0], raw)
                self.assertFalse(report["format"]["passed"])
                self.assertIsNone(report["content"])

    def test_missing_fields_and_wrong_types(self):
        mutations = []
        for field in ("status", "findings", "human_decision_required"):
            response = copy.deepcopy(POSITIVES[0])
            del response[field]
            mutations.append(response)
        for field in POSITIVES[0]["findings"][0]:
            response = copy.deepcopy(POSITIVES[0])
            del response["findings"][0][field]
            mutations.append(response)
        response = copy.deepcopy(POSITIVES[0])
        response["human_decision_required"] = 1
        mutations.append(response)
        response = copy.deepcopy(POSITIVES[0])
        response["findings"][0]["suggestion"] = {"text": "legacy contract"}
        mutations.append(response)
        response = copy.deepcopy(POSITIVES[0])
        response["findings"][0]["kind"] = "unknown"
        mutations.append(response)
        for response in mutations:
            with self.subTest(response=response):
                report = self.check_response(0, response)
                self.assertFalse(report["format"]["passed"])
                self.assertIsNone(report["content"])

    def test_extra_fields_do_not_score(self):
        response = copy.deepcopy(POSITIVES[0])
        response["ignored"] = "extra"
        response["findings"][0]["requirement_id"] = "invented"
        self.assertEqual(self.check_response(0, response), self.check_response(0, POSITIVES[0]))

    def test_missing_requirement(self):
        response = copy.deepcopy(POSITIVES[0])
        response["findings"] = [finding("omission", "the impact on users",
                                        "Does not report the scope.", "Requires the observable impact.")]
        report = self.check_response(0, response)
        self.assertTrue(report["format"]["passed"])
        self.assertFalse(report["content"]["passed"])
        self.assertEqual(report["content"]["missing_ids"], ["recovery", "start_time"])

    def test_split_findings_accepted(self):
        response = copy.deepcopy(POSITIVES[0])
        response["findings"] = [
            finding("omission", "start time", "Without the start, there is no timeline.", "Records the start time."),
            finding("omission", "the impact on users", "Does not report the scope.", "Requires the observable impact."),
            finding("omission", "the recovery action", "Does not report the resolution.",
                    "Requires the recovery action and its outcome.")]
        self.assertTrue(self.check_response(0, response)["content"]["passed"])

    def test_invented_finding(self):
        response = copy.deepcopy(POSITIVES[0])
        response["findings"].append(finding("omission", "", "Without the cost, the loss is unknown.",
                                            "Requires the cost in dollars."))
        report = self.check_response(0, response)
        self.assertFalse(report["content"]["passed"])
        self.assertEqual(report["content"]["unexpected_findings"], 1)

    def test_fabricated_evidence(self):
        response = copy.deepcopy(POSITIVES[2])
        response["findings"][0]["evidence"] = "quickly invented"
        report = self.check_response(2, response)
        self.assertTrue(report["format"]["passed"])
        self.assertFalse(report["content"]["passed"])
        self.assertFalse(report["content"]["details"][0]["evidence_valid"])

    def test_empty_evidence_allowed_but_no_literal_credit(self):
        response = copy.deepcopy(POSITIVES[1])
        response["findings"][0]["evidence"] = ""
        report = self.check_response(1, response)
        self.assertTrue(report["content"]["passed"])
        self.assertEqual(report["content"]["literal_evidence_coverage"], 0)

    def test_wrong_status_and_human_flag(self):
        for field, value in (("status", "needs_context"), ("human_decision_required", False)):
            response = copy.deepcopy(POSITIVES[0])
            response[field] = value
            report = self.check_response(0, response)
            self.assertTrue(report["format"]["passed"])
            self.assertFalse(report["content"]["passed"])

    def test_question_required_for_insufficient_context(self):
        for question in ("", "What deadline?"):
            response = copy.deepcopy(POSITIVES[1])
            response["findings"][0]["question"] = question
            self.assertFalse(self.check_response(1, response)["content"]["passed"])

    def test_context_suggestion_must_be_conditional_or_empty(self):
        response = copy.deepcopy(POSITIVES[1])
        response["findings"][0]["suggestion"] = "Require a 24h deadline for the beginner customer."
        self.assertFalse(self.check_response(1, response)["content"]["passed"])
        response["findings"][0]["suggestion"] = "After the need is defined, propose an observable criterion."
        self.assertTrue(self.check_response(1, response)["content"]["passed"])

    def test_vague_or_wrong_threshold_suggestion(self):
        for suggestion in ("", "Improve the rubric.", "Resolves quickly.", "Resolves within 2 hours."):
            response = copy.deepcopy(POSITIVES[2])
            response["findings"][0]["suggestion"] = suggestion
            report = self.check_response(2, response)
            self.assertTrue(report["format"]["passed"])
            self.assertFalse(report["content"]["passed"])

    def test_empty_impact(self):
        response = copy.deepcopy(POSITIVES[2])
        response["findings"][0]["impact"] = "  "
        self.assertFalse(self.check_response(2, response)["content"]["passed"])

    def test_empty_findings_is_content_failure(self):
        response = copy.deepcopy(POSITIVES[0])
        response["findings"] = []
        report = self.check_response(0, response)
        self.assertTrue(report["format"]["passed"])
        self.assertFalse(report["content"]["passed"])

    def test_negative_fixture_for_each_case(self):
        negatives = copy.deepcopy(POSITIVES)
        # 1: impact and recovery are correct, but the start time is missing.
        negatives[0]["findings"].pop(0)
        # 2: invents a requirement instead of asking for context.
        negatives[1]["findings"][0]["question"] = ""
        negatives[1]["findings"][0]["suggestion"] = "Requires a 24h deadline for the beginner customer."
        # 3: keeps the original vagueness.
        negatives[2]["findings"][0]["suggestion"] = "Resolves the problem quickly."
        # 4: repeats unactionable feedback.
        negatives[3]["findings"][0]["suggestion"] = "Be clearer and more specific."
        # 5: covers only the happy path.
        negatives[4]["findings"].pop()
        # 6: reopens a decision the author already accepted.
        negatives[5]["findings"].append(finding(
            "omission", "C1: States the next action.", "The next action is missing.", "Proposal: state the next action."))
        for index, response in enumerate(negatives):
            with self.subTest(task=TASKS[index]["id"]):
                report = self.check_response(index, response)
                self.assertTrue(report["format"]["passed"], report)
                self.assertFalse(report["content"]["passed"], report)

    def test_incident_requires_all_three_requirements(self):
        self.assertEqual({item["id"] for item in TASKS[0]["expected_findings"]},
                         {"start_time", "user_impact", "recovery"})
        report = self.check_response(0, POSITIVES[0])
        self.assertEqual(report["content"]["missing_ids"], [])
        response = copy.deepcopy(POSITIVES[0])
        response["findings"].pop(0)
        self.assertEqual(self.check_response(0, response)["content"]["missing_ids"], ["start_time"])

    def test_negated_gaps_rejected(self):
        for index in (0, 2, 5):
            for denial in ("There is no gap.", "No omission exists.",
                           "Nothing is missing, neither deadline nor requirement.", "All requirements are covered."):
                with self.subTest(task=TASKS[index]["id"], denial=denial):
                    response = copy.deepcopy(POSITIVES[index])
                    response["findings"][0]["impact"] += " " + denial
                    report = self.check_response(index, response)
                    self.assertTrue(report["format"]["passed"])
                    self.assertFalse(report["content"]["passed"], report)

    def test_inverted_deadline_and_conflicting_suggestions(self):
        for index in (2, 5):
            for limit in ("more than 2 business days", "at least two business days", "2 hours"):
                with self.subTest(task=TASKS[index]["id"], limit=limit):
                    response = copy.deepcopy(POSITIVES[index])
                    response["findings"][0]["suggestion"] = "Proposal: resolves and states a deadline of " + limit + "."
                    self.assertFalse(self.check_response(index, response)["content"]["passed"])
                    # The presence of the correct limit must not mask the contradiction.
                    response["findings"][0]["suggestion"] += " Also resolves and states a deadline of up to 2 business days."
                    self.assertFalse(self.check_response(index, response)["content"]["passed"])

    def test_explicit_equivalent_paraphrases(self):
        variants = copy.deepcopy(POSITIVES)
        variants[0]["findings"][0]["suggestion"] = "Report when the incident started."
        variants[0]["findings"][1]["suggestion"] = "Describe the observable impact and record the restoration action and its outcome."
        variants[2]["findings"][0]["suggestion"] = "Proposal: resolution in at most two business days."
        variants[3]["findings"][0]["suggestion"] = "Define the text excerpt that satisfies C1 and C2 and a rule for when the evidence is absent."
        variants[4]["findings"][0]["suggestion"] = "A valid ISO date returns the expected date."
        variants[4]["findings"][1]["suggestion"] = "An invalid format gives back an explicit error and the process stays alive."
        variants[5]["findings"][0]["suggestion"] = "Indicate a deadline of at most two business days."
        for index, response in enumerate(variants):
            with self.subTest(task=TASKS[index]["id"]):
                self.assertTrue(self.check_response(index, response)["content"]["passed"])

    def test_code_requires_error_and_continuity(self):
        for suggestion in ("Invalid input returns an explicit error.",
                           "Invalid input returns an explicit error and terminates the process."):
            response = copy.deepcopy(POSITIVES[4])
            response["findings"][1]["suggestion"] = suggestion
            self.assertFalse(self.check_response(4, response)["content"]["passed"])

    def test_feedback_requires_location_and_absence_rule(self):
        for suggestion in ("Indicate textual evidence for C1 and C2.",
                           "Indicate textual evidence for C1 and an absence rule."):
            response = copy.deepcopy(POSITIVES[3])
            response["findings"][0]["suggestion"] = suggestion
            self.assertFalse(self.check_response(3, response)["content"]["passed"])

    def test_format_content_separation_across_six_cases(self):
        for index in range(6):
            with self.subTest(task=TASKS[index]["id"]):
                response = copy.deepcopy(POSITIVES[index])
                del response["findings"][0]["evidence"]
                report = self.check_response(index, response)
                self.assertFalse(report["format"]["passed"])
                self.assertIsNone(report["content"])
                response = copy.deepcopy(POSITIVES[index])
                response["findings"][0]["evidence"] = "Fabricated nonexistent excerpt."
                report = self.check_response(index, response)
                self.assertTrue(report["format"]["passed"])
                self.assertFalse(report["content"]["passed"])


if __name__ == "__main__":
    unittest.main()
