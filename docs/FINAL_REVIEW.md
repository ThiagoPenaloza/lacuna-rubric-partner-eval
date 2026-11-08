# Integrated final review — Eval V2

Date: 2026-11-08. This review replaces the preliminary opinion that came with the three-task scaffold and the 2026-11-07 review of the Portuguese version.

## Offline verdict

The package can be released for offline validation: it has six materialized tasks, explicit expected answer keys, the V2 JSON contract, and a separation between format validation and the content proxy. The local suite passes with 24 tests:

    python3 -B -m unittest discover -s eval -p 'test_*.py' -v

One local exploratory run with Ollama/`qwen2.5:7b`, at no cost and with one attempt per task, is preserved in `results/english_qwen2.5_7b/`. It is not a general evaluation or a final semantic adjudication.

## Integrated fixes

- `incident_01` now requires all three public requirements of the context: start time, impact on users, and recovery action.
- `context_02`, `ambiguity_03`, `feedback_04`, `code_05`, and `iteration_06` are materialized in `eval/tasks.json`, with inputs, history where applicable, and answer keys.
- The contract separates `format` and `content`; literal evidence is checked without turning that check into semantic proof.
- Tests were added for invalid JSON, missing fields, fabricated evidence, denied gaps, an inverted deadline even with the correct deadline present, code continuity, located feedback, and explicitly accepted paraphrases.
- Pattern matching is case-insensitive so that `ISO` is not rejected because of capitalization. Justifications such as "does not report" are not confused with denying the gap, while explicit denials are still rejected by the proxy.
- The whole package was migrated to English: inputs, answer keys, anchors, suggestion and rejection patterns, test fixtures, CLI messages, the runner prompt, docs, and the video. The 24 tests were rewritten with English fixtures and pass. English negations that are not contradictions ("no more than 2 business days", "never crashes the process") are explicitly excluded from the rejection patterns.
- A new English local run obtained 6/6 parseable responses and 6/6 valid protocols; the content proxy marked 2/6 complete (`incident_01`, `iteration_06`). A rerun produced 6/6 identical raw responses. The Portuguese runs were moved to `results/superseded_portuguese/` and are excluded from the reported results.

## Limitations and condition for experiments

The metagrader is still a lexical/protocol diagnostic. Semantic equivalence, evidence relevance, question quality, suggestion fidelity, deduplication, and partial credit require documented human adjudication per task. The English run already shows one likely lexical false negative (`code_05`: correct behaviors written in a different word order). Before running more models, Thiago must freeze the acceptable alternatives, weights, and aggregation policy and record the approval of the six answer keys.

The package includes no credentials and no paid calls. The local runner is `eval/run_ollama.py`; results should only be generalized after more models/attempts, with version, effort, prompt, and raw responses preserved.

## Canonical files

- `eval/tasks.json`
- `eval/metagrader.py`
- `eval/test_metagrader.py`
- `eval/run_ollama.py`, `eval/score_run.py`
- `results/english_qwen2.5_7b/`
- `docs/EVAL_SPEC_V2.md`
- `docs/FINAL_README.md`
