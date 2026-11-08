#!/usr/bin/env python3
"""Builds data.json (the demo video data) from the real files in the repository.

Nothing here is invented: inputs come from eval/tasks.json, model responses from
results/english_qwen2.5_7b/, metagrader checks are recomputed with
eval/metagrader.grade(), and the test output is captured by running the suite.

Usage: python3 -B submission/video_build/build_data.py --out DIR [--repro DIR]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
from metagrader import grade  # noqa: E402

ORDER = ["incident_01", "context_02", "ambiguity_03", "feedback_04", "code_05", "iteration_06"]
TITLES = {
    "incident_01": "Missing requirement",
    "context_02": "Insufficient context",
    "ambiguity_03": "Ambiguous criterion",
    "feedback_04": "Generic feedback",
    "code_05": "Code behavior",
    "iteration_06": "Iterative refinement",
}
FINAL = ROOT / "results" / "english_qwen2.5_7b"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def texts(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from texts(child)


def locate(evidence, task_input):
    """Where the evidence appears in the input (field + offsets), or the best prefix."""
    fields = []
    for key, value in task_input.items():
        if isinstance(value, dict):
            fields += [(f"history.{k}", v) for k, v in value.items()]
        else:
            fields.append((key, value))
    if evidence:
        for name, value in fields:
            idx = value.find(evidence)
            if idx >= 0:
                return {"literal": True, "field": name, "start": idx, "end": idx + len(evidence)}
    best = {"literal": False, "field": None, "start": 0, "end": 0, "prefix": 0}
    for name, value in fields:
        for start in range(len(value)):
            n = 0
            while n < len(evidence) and start + n < len(value) and value[start + n] == evidence[n]:
                n += 1
            if n > best["prefix"]:
                best = {"literal": False, "field": name, "start": start, "end": start + n, "prefix": n}
    if best["prefix"] < 8:  # a short coincidence is not a location
        best = {"literal": False, "field": None, "start": 0, "end": 0, "prefix": 0}
    return best


def answer_keys():
    spec = (ROOT / "docs" / "EVAL_SPEC_V2.md").read_text(encoding="utf-8")
    found = re.findall(r"\*\*Answer key:\*\*\s*(.+)", spec)
    return dict(zip(ORDER, found))


def provisional():
    md = (FINAL / "provisional_review.md").read_text(encoding="utf-8")
    rows = {}
    for line in md.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in ORDER:
            rows[cells[0]] = {"reading": cells[1], "main_failure": cells[2]}
    return rows


def run_tests():
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "eval", "-p", "test_*.py", "-v"],
        cwd=ROOT, capture_output=True, text=True)
    out = (proc.stdout + proc.stderr).strip().splitlines()
    out = [re.sub(r"Ran (\d+) tests in [0-9.]+s", r"Ran \1 tests", l) for l in out]
    ran = next((int(m.group(1)) for l in out if (m := re.match(r"Ran (\d+) tests", l))), None)
    return {"command": "python3 -B -m unittest discover -s eval -p 'test_*.py' -v",
            "returncode": proc.returncode, "lines": out, "ran": ran,
            "ok": proc.returncode == 0 and out[-1].startswith("OK")}


def repro(dir_):
    if not dir_:
        return None
    rows = []
    for tid in ORDER:
        a = load(FINAL / f"{tid}.json")
        b = load(Path(dir_) / f"{tid}.json")
        rows.append({"task_id": tid, "identical": a["raw_response"] == b["raw_response"],
                     "eval_count_recorded": a.get("eval_count"), "eval_count_rerun": b.get("eval_count")})
    meta = load(Path(dir_) / "run_metadata.json")
    return {"rerun_started_at": meta["started_at"], "model": meta["model"],
            "identical": sum(r["identical"] for r in rows), "total": len(rows), "tasks": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="temporary build folder")
    parser.add_argument("--repro", help="folder of a runner re-execution to compare against")
    args = parser.parse_args()

    tasks = {t["id"]: t for t in load(ROOT / "eval" / "tasks.json")["tasks"]}
    summary = load(FINAL / "summary.json")
    meta = load(FINAL / "run_metadata.json")
    keys = answer_keys()
    prov = provisional()

    cases = []
    for tid in ORDER:
        task = tasks[tid]
        rec = load(FINAL / f"{tid}.json")
        parsed = rec["parsed_response"]
        report = grade(task, json.dumps(parsed, ensure_ascii=False))
        content = report["content"]
        findings = []
        for finding, detail in zip(parsed["findings"], content["details"]):
            findings.append({**finding, "grader": detail, "evidence_location": locate(finding["evidence"], task["input"])})
        cases.append({
            "id": tid,
            "n": ORDER.index(tid) + 1,
            "title": TITLES[tid],
            "input": task["input"],
            "expected_status": task["expected_status"],
            "expected_findings": [{"id": f["id"], "kind": f["kind"]} for f in task["expected_findings"]],
            "answer_key_spec": keys.get(tid, ""),
            "raw_response": rec["raw_response"],
            "eval_count": rec.get("eval_count"),
            "response": {"status": parsed["status"], "human_decision_required": parsed["human_decision_required"]},
            "findings": findings,
            "grader": {k: content[k] for k in ("passed", "status_correct", "human_decision_preserved", "matched_ids",
                                                "missing_ids", "unexpected_findings", "requirement_recall_proxy",
                                                "literal_evidence_coverage")},
            "format_passed": report["format"]["passed"],
            "provisional": prov.get(tid),
        })

    all_findings = [f for c in cases for f in c["findings"]]
    expected = [f for c in cases for f in c["expected_findings"]]
    kinds = ("omission", "insufficient_context", "ambiguity", "strength")
    metrics = {
        "tasks": len(cases),
        "parseable": sum(t.get("parseable", False) for t in summary["tasks"]),
        "format_passed": sum(c["format_passed"] for c in cases),
        "content_proxy_passed": sum(c["grader"]["passed"] for c in cases),
        "all_ids_matched": sum(not c["grader"]["missing_ids"] for c in cases),
        "status_correct": sum(c["grader"]["status_correct"] for c in cases),
        "status_missed": [c["id"] for c in cases if not c["grader"]["status_correct"]],
        "proxy_passed_ids": [c["id"] for c in cases if c["grader"]["passed"]],
        "human_flag_true": sum(c["response"]["human_decision_required"] is True for c in cases),
        "ids_expected": len(expected),
        "ids_matched": sum(len(c["grader"]["matched_ids"]) for c in cases),
        "findings_total": len(all_findings),
        "findings_literal": sum(f["grader"]["literal_evidence_present"] for f in all_findings),
        "status_model": {s: sum(c["response"]["status"] == s for c in cases) for s in ("review_ready", "needs_context")},
        "status_expected": {s: sum(c["expected_status"] == s for c in cases) for s in ("review_ready", "needs_context")},
        "kinds_model": {k: sum(f["kind"] == k for f in all_findings) for k in kinds},
        "kinds_expected": {k: sum(f["kind"] == k for f in expected) for k in kinds},
        "summary_format_pass_rate": summary["format_pass_rate"],
        "summary_content_proxy_pass_rate": summary["content_proxy_pass_rate"],
    }
    data = {
        "generated_from": ["eval/tasks.json", "eval/metagrader.py", "results/english_qwen2.5_7b/",
                           "docs/EVAL_SPEC_V2.md"],
        "run": {**meta, "dir": "results/english_qwen2.5_7b"},
        "cases": cases,
        "metrics": metrics,
        "tests": run_tests(),
        "repro": repro(args.repro),
    }
    if data["repro"] is None and (FINAL / "repro_check.json").exists():
        data["repro"] = load(FINAL / "repro_check.json")  # preserved evidence of the rerun
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": metrics,
                      "tests": {k: data["tests"][k] for k in ("ran", "ok")},
                      "repro": data["repro"] and {k: data["repro"][k] for k in ("identical", "total")}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
