"""Offline scaffold for the V2 contract, Python standard library only.

Usage: python3 eval/metagrader.py TASK_ID response.json
Format and content are graded independently. Extra fields are ignored.
Answer-key IDs are internal: a V2 response does not need requirement_id.
Coverage uses configurable lexical anchors and accepts combined findings.
Non-empty evidence must be an exact substring of a text field of the input.
Empty evidence is allowed by V2, but earns no literal-evidence coverage.
Verifiability uses anchors from the expected review; optional groups require
joint coverage of observable components. This does not prove semantic fidelity.
Explanation, assumptions, equivalences, and the human decision need adjudication.
Paraphrases are accepted only through the answer key's explicit anchors and patterns.
Contradiction rules cover known negations and inverted limits, not every
possible contradiction. Do not read this as a validated semantic grader.
"""
import json
import re
import unicodedata
from pathlib import Path
import sys


# A suggestion for an insufficient-context finding must be empty or conditional:
# it may not invent a requirement before the missing context is supplied.
CONDITIONAL_PATTERNS = [r"\b(?:if|after|once|when|whenever|unless|depending on|provided that|as soon as)\b"]
# A suggestion that tells the author NOT to require/include something cannot
# close a gap. Applied to the suggestion only, never to the impact text.
NEGATED_SUGGESTION_PATTERNS = [
    r"\b(?:do not|does not|don't|doesn't|should not|shouldn't|must not|need not|no need to|"
    r"(?:it is )?not (?:necessary|needed|required) to)\b.{0,15}"
    r"(?:requir|includ|record|report|describ|stat|mention|specif)"
]


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate key: {key}")
        obj[key] = value
    return obj


def _constant(value):
    raise ValueError(f"Invalid constant: {value}")


def _texts(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _texts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _texts(child)


def _has(text, anchors):
    return any(anchor.casefold() in text.casefold() for anchor in anchors)


def _normalize(text):
    text = text.replace("’", "'").replace("‘", "'")
    return "".join(char for char in unicodedata.normalize("NFKD", text.casefold())
                   if not unicodedata.combining(char))


def _matches_pattern(text, patterns):
    return any(re.search(pattern, _normalize(text), re.DOTALL | re.IGNORECASE) for pattern in patterns)


def grade(task, response_json):
    report = {"format": {"passed": False, "errors": []}, "content": None}
    errors = report["format"]["errors"]
    try:
        obj = json.loads(response_json, object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, TypeError) as exc:
        errors.append(f"Invalid JSON: {exc}")
        return report
    if not isinstance(obj, dict):
        errors.append("Output must be an object.")
        return report
    if obj.get("status") not in ("review_ready", "needs_context"):
        errors.append("status is invalid or missing.")
    if type(obj.get("human_decision_required")) is not bool:
        errors.append("human_decision_required must be a boolean.")
    if not isinstance(obj.get("findings"), list):
        errors.append("findings must be a list.")
    else:
        for index, finding in enumerate(obj["findings"]):
            if not isinstance(finding, dict):
                errors.append(f"findings[{index}] must be an object.")
                continue
            for key in ("kind", "criterion_ref", "evidence", "impact", "question", "suggestion", "confidence"):
                if not isinstance(finding.get(key), str):
                    errors.append(f"findings[{index}].{key} must be a string.")
            if finding.get("kind") not in ("omission", "insufficient_context", "ambiguity", "strength"):
                errors.append(f"findings[{index}].kind is invalid.")
            # V2 shows "high" as an example but does not define a confidence enum.
    if errors:
        return report
    report["format"]["passed"] = True
    expected = task["expected_findings"]
    sources = list(_texts(task["input"]))
    matched = set()
    details = []
    for finding in obj["findings"]:
        text = " ".join(finding[key] for key in ("criterion_ref", "evidence", "impact", "question", "suggestion"))
        matches = [item for item in expected if finding["kind"] == item["kind"] and _has(text, item["anchors"])]
        ids = [item["id"] for item in matches]
        matched.update(ids)
        evidence = finding["evidence"]
        suggestion = finding["suggestion"]
        needs_context = finding["kind"] == "insufficient_context"
        question_ok = not needs_context or (bool(finding["question"].strip()) and all(
            _has(finding["question"], item.get("question_anchors", [])) for item in matches))
        suggestion_ok = bool(matches) and all(
            _has(suggestion, item["suggestion_anchors"]) if item["suggestion_anchors"]
            else (not suggestion.strip() or _matches_pattern(suggestion, CONDITIONAL_PATTERNS))
            for item in matches)
        suggestion_ok = suggestion_ok and all(
            all(_has(suggestion, group) for group in item.get("suggestion_anchor_groups", []))
            for item in matches)
        # Positive patterns spell out the accepted paraphrases; they are not semantic inference.
        suggestion_ok = suggestion_ok and all(
            not item.get("suggestion_patterns") or
            _matches_pattern(suggestion, item["suggestion_patterns"])
            for item in matches)
        # Semantic rejections look mainly at the proposal: a justification of a
        # gap can naturally say "does not report".
        assertion = " ".join(finding[key] for key in ("criterion_ref", "question", "suggestion"))
        assertions_ok = not _matches_pattern(assertion, task.get("rejection_patterns", []))
        # Explicit denials inserted into the impact are still caught, without
        # turning every "does not report" into a contradiction.
        denial_patterns = task.get("rejection_patterns", [])[:4]
        assertions_ok = assertions_ok and not _matches_pattern(finding["impact"], denial_patterns)
        assertions_ok = assertions_ok and not _matches_pattern(suggestion, NEGATED_SUGGESTION_PATTERNS)
        details.append({
            "matched_ids": ids,
            "assertions_consistent_proxy": assertions_ok,
            "expected_finding": bool(matches),
            "evidence_valid": evidence == "" or any(evidence in source for source in sources),
            "literal_evidence_present": bool(evidence.strip()) and any(evidence in source for source in sources),
            "impact_present": bool(finding["impact"].strip()),
            "question_ok": question_ok,
            "suggestion_verifiable_proxy": suggestion_ok,
            "confidence_present": bool(finding["confidence"].strip()),
        })
    missing = sorted({item["id"] for item in expected} - matched)
    status_ok = obj["status"] == task["expected_status"]
    human_ok = obj["human_decision_required"] is True
    checks = ("assertions_consistent_proxy", "expected_finding", "evidence_valid", "impact_present", "question_ok", "suggestion_verifiable_proxy", "confidence_present")
    report["content"] = {
        "passed": status_ok and human_ok and not missing and all(all(row[key] for key in checks) for row in details),
        "status_correct": status_ok,
        "human_decision_preserved": human_ok,
        "matched_ids": sorted(matched),
        "missing_ids": missing,
        "unexpected_findings": sum(not row["expected_finding"] for row in details),
        "requirement_recall_proxy": len(matched) / len(expected) if expected else None,
        "literal_evidence_coverage": sum(row["literal_evidence_present"] for row in details) / len(details) if details else None,
        "details": details,
        "semantic_review_required": True,
    }
    return report


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python3 eval/metagrader.py TASK_ID response.json")
    tasks = json.loads(Path(__file__).with_name("tasks.json").read_text(encoding="utf-8"))["tasks"]
    task = next((item for item in tasks if item["id"] == sys.argv[1]), None)
    if task is None:
        raise SystemExit(f"Unknown task: {sys.argv[1]}")
    report = grade(task, Path(sys.argv[2]).read_text(encoding="utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # The content proxy is never a semantic verdict: responses with a valid
    # format go to human adjudication even when the proxy marks
    # `content.passed=false`.
    return 0 if report["format"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
