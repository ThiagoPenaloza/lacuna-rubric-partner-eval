#!/usr/bin/env python3
"""Runs the rubric partner locally through Ollama without sending answer keys."""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib import request


SYSTEM = """You are a rubric review partner. Analyze only the goal, context,
rubric_draft, and history you receive. Do not invent requirements. Point out
omissions, insufficient context, ambiguities, generic feedback, and code
requirements. Preserve decisions already accepted in the history. Answer ONLY
with valid JSON, without markdown. Choose exactly ONE value for status; never
write the literal string "review_ready|needs_context". Use evidence only as a
literal substring of the input, or an empty string when there is no suitable
excerpt. Contract:
{"status":"review_ready","findings":[{"kind":"omission","criterion_ref":"string","evidence":"literal excerpt of the input or empty string","impact":"string","question":"string","suggestion":"string","confidence":"high"}],"human_decision_required":true}
Allowed values: status review_ready or needs_context; kind omission, insufficient_context, ambiguity, or strength; confidence low, medium, or high.
"""


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.S).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def call_ollama(model, prompt, host):
    payload = json.dumps({
        "model": model,
        "system": SYSTEM,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "seed": 17},
    }).encode()
    req = request.Request(host.rstrip("/") + "/api/generate", data=payload,
                          headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=300) as response:
        body = json.loads(response.read().decode())
    return body.get("response", ""), body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--out", default="results/english_qwen2.5_7b")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    tasks = json.loads((root / "eval" / "tasks.json").read_text(encoding="utf-8"))["tasks"]
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    language = json.loads((root / "eval" / "tasks.json").read_text(encoding="utf-8")).get("language")
    metadata = {"model": args.model, "host": args.host, "temperature": 0,
                "seed": 17, "task_count": len(tasks), "input_language": language,
                "system_prompt_sha256": hashlib.sha256(SYSTEM.encode("utf-8")).hexdigest(),
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (out / "run_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")

    for task in tasks:
        # Only the input is sent on purpose; expected_findings/rejection_patterns stay out.
        prompt = json.dumps({"task_id": task["id"], **task["input"]}, ensure_ascii=False, indent=2)
        raw, api = call_ollama(args.model, prompt, args.host)
        record = {"task_id": task["id"], "prompt_input": json.loads(prompt), "raw_response": raw,
                  "api_done": api.get("done"), "eval_count": api.get("eval_count")}
        try:
            record["parsed_response"] = extract_json(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            record["parse_error"] = str(exc)
        (out / f"{task['id']}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        print(task["id"], "ok" if "parsed_response" in record else "parse_error")


if __name__ == "__main__":
    main()
