# Offline metagrader

This directory validates the synthetic fixtures of the V2 eval. The grader itself does not call models or measure LLM performance; `run_ollama.py` is the optional local runner.

```bash
python3 -B -m unittest discover -s eval -p 'test_*.py' -v
python3 eval/metagrader.py incident_01 response.json
```

The report separates format failures from content checks. The lexical proxy checks IDs, literal evidence, impact, a question when context is missing, and a verifiable proposal. Semantic equivalence, feedback quality, and adjudication of the answer keys still require Thiago's human review.

In command-line mode, a non-zero exit code only means invalid JSON/protocol; `content.passed` is a lexical diagnostic and does not replace human adjudication.

The six fixtures cover a missing requirement, insufficient context, an ambiguous criterion, generic feedback, code behavior, and iterative refinement. The answer keys are expected and synthetic; they do not represent model results.

| File | Purpose |
|---|---|
| `tasks.json` | Six English tasks: inputs sent to the model, plus answer keys, anchors, and patterns that are never sent. |
| `metagrader.py` | `grade(task, response_json)` and a CLI; standard library only. |
| `test_metagrader.py` | 24 synthetic tests (positive, negative, format, and paraphrase fixtures). |
| `run_ollama.py` | Local runner (Ollama, temperature 0, seed 17); writes raw responses and `run_metadata.json`. |
| `score_run.py` | Grades a preserved run and writes `summary.json`. |
