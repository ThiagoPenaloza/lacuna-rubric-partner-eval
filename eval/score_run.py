#!/usr/bin/env python3
"""Scores a run preserved by the local runner; content remains a proxy."""
import json
import sys
from pathlib import Path

from metagrader import grade


def main():
    root = Path(__file__).resolve().parent.parent
    run_dir = root / (sys.argv[1] if len(sys.argv) > 1 else "results/english_qwen2.5_7b")
    tasks = {t["id"]: t for t in json.loads((root / "eval" / "tasks.json").read_text())["tasks"]}
    rows = []
    for path in sorted(run_dir.glob("*.json")):
        # Only per-task records are scored; run_metadata, summary, and repro files are skipped.
        if path.stem not in tasks:
            continue
        record = json.loads(path.read_text())
        if "parsed_response" not in record:
            rows.append({"task_id": record["task_id"], "parseable": False})
            continue
        report = grade(tasks[record["task_id"]], json.dumps(record["parsed_response"], ensure_ascii=False))
        content = report["content"] or {}
        rows.append({"task_id": record["task_id"], "parseable": True,
                     "format_passed": report["format"]["passed"],
                     "content_proxy_passed": content.get("passed", False),
                     "matched_ids": content.get("matched_ids", []),
                     "missing_ids": content.get("missing_ids", []),
                     "literal_evidence_coverage": content.get("literal_evidence_coverage")})
    summary = {"run": str(run_dir.relative_to(root)), "task_count": len(rows),
               "format_pass_rate": sum(r.get("format_passed", False) for r in rows) / len(rows),
               "content_proxy_pass_rate": sum(r.get("content_proxy_passed", False) for r in rows) / len(rows),
               "tasks": rows,
               "warning": "content_proxy_passed is not human semantic adjudication."}
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
