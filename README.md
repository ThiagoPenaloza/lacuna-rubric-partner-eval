# Lacuna — Rubric Partner Eval

## Short description

Lacuna evaluates whether an LLM can act as a careful rubric-writing partner. Given a goal, context, draft rubric, and optional revision history, the model must identify missing requirements, distinguish missing context from an omission, resolve vague language into observable criteria, turn generic feedback into an actionable edit, cover both success and failure behavior in code tasks, and preserve decisions already accepted by the author.

## Domain and expertise

This eval comes from professional rubric and grader-authoring work for AI training and evaluation. The practical gap is that rubric authors can omit mandatory requirements, accept vague criteria, or receive feedback that does not identify what to change. The benchmark focuses on that workflow rather than on generic chat quality.

## What it tests and why it matters

The benchmark contains six synthetic, adjudicable tasks: incident-report omissions, insufficient context, an ambiguous deadline, generic feedback, code behavior, and iterative refinement. Each task has a public answer key, positive and negative fixtures, deliberate edge cases, and a metric. The goal is to expose failures that matter in production evaluation: unsupported assumptions, missing mandatory criteria, fabricated evidence, incorrect thresholds, and loss of author decisions.

## Contract and scoring

The model receives only the task input and must return JSON with `status`, `findings`, and `human_decision_required`. Each finding contains `kind`, `criterion_ref`, literal `evidence`, `impact`, `question`, `suggestion`, and `confidence`. The metagrader reports protocol and content separately. It checks schema validity, literal evidence, expected finding IDs, impact, required questions, suggestion patterns, and explicit contradiction guards. The content proxy is diagnostic; semantic equivalence, evidence relevance, partial credit, and final adjudication remain human decisions.

## Setup and run

Python 3.9+ and the Python standard library are enough for the eval. No API key is required for the included offline tests.

```bash
python3 -B -m unittest discover -s eval -p 'test_*.py' -v
submission/demo.sh
```

Optional free local model run (requires Ollama and the local `qwen2.5:7b` model):

```bash
ollama serve
python3 -B eval/run_ollama.py --model qwen2.5:7b --out results/english_qwen2.5_7b
python3 -B eval/score_run.py results/english_qwen2.5_7b
```

Video regeneration is optional and uses local macOS `say`, Python, Node.js, Playwright Chromium, and temporary `ffmpeg-static` dependencies:

```bash
submission/video_build/make_video.sh
```

## Models tested and results

Model: `qwen2.5:7b` through Ollama 0.40.3; English inputs; temperature 0; seed 17; one attempt per task; run date 2026-11-08. The runner sends only `task_id` and input fields, never answer keys or rejection patterns.

- Parseable JSON: 6/6
- Valid protocol: 6/6 (100%)
- Content proxy complete: 2/6 (33%)
- Correct status: 5/6
- Answer-key IDs found: 7/9
- Literal evidence coverage: 6/6
- Identical raw responses on deterministic rerun: 6/6

These are exploratory local results, not a general model score. The English raw outputs and summary are in `results/english_qwen2.5_7b/`.

## Failure analysis

The model reliably produced the required JSON and found all incident and iterative-deadline IDs. It failed the context-insufficiency case by choosing the wrong status/kind, missed the generic feedback in revision history, and produced a likely lexical false negative on the code case even though the proposed behaviors were substantively correct in a different word order. This demonstrates why protocol checks, lexical proxies, and human semantic adjudication must be reported separately.

## Prior work and sources

The benchmark was created for this hackathon from the author's professional experience writing rubrics and graders for AI training/evaluation. The task data is synthetic and contains no employer, client, or personal data. No external benchmark or dataset was copied. Challenge rules and submission requirements: https://www.hackerrank.com/event/micro1-eval-hackathon

## Video walkthrough

Host `submission/startup_app_demo.mp4` on YouTube, Google Drive, Loom, Vimeo, or a similar service and paste the public link here before submission:

`VIDEO_LINK_TO_ADD_BEFORE_SUBMITTING`

The final video is 3:13.5, 1920×1080, H.264/AAC, with English narration and captions.

## Reproducibility and package contents

- `eval/tasks.json`: six English tasks and answer keys.
- `eval/metagrader.py`: protocol/content diagnostic.
- `eval/test_metagrader.py`: 24 offline tests.
- `results/english_qwen2.5_7b/`: raw outputs, summary, and rerun evidence.
- `submission/video_build/`: regenerable English video pipeline.

All files in the submission ZIP are code, documentation, fixtures, or small supporting data. The MP4/MOV is intentionally excluded from the ZIP.
