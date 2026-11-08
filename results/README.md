# Local exploratory results

One free run was made on the author's computer with Ollama `0.40.3` and `qwen2.5:7b`, temperature 0 and seed 17, on the English task set. The runner sent only `task_id` and the input fields; `expected_findings`, `expected_status`, and `rejection_patterns` were never sent to the model.

Commands:

```bash
ollama serve
python3 -B eval/run_ollama.py --model qwen2.5:7b --out results/english_qwen2.5_7b
python3 -B eval/score_run.py results/english_qwen2.5_7b
```

Result of the English run (six tasks, one attempt per task, `results/english_qwen2.5_7b/`):

| Metric | Result |
|---|---:|
| Parseable JSON | 6/6 (100%) |
| Protocol accepted | 6/6 (100%) |
| `content_proxy_passed` | 2/6 (33%) |
| Correct status | 5/6 |
| Cases with every answer-key ID found by the proxy | 4/6 |
| Answer-key IDs found by the proxy | 7/9 |
| Findings with literal evidence | 6/6 |

| Task | Protocol | Status | IDs found | Content proxy |
|---|:---:|:---:|:---:|:---:|
| incident_01 | ✓ | ✓ review_ready | 3/3 | ✓ |
| context_02 | ✓ | ✗ review_ready (expected needs_context) | 0/1 | ✗ |
| ambiguity_03 | ✓ | ✓ review_ready | 1/1 | ✗ |
| feedback_04 | ✓ | ✓ review_ready | 0/1 | ✗ |
| code_05 | ✓ | ✓ review_ready | 2/2 | ✗ |
| iteration_06 | ✓ | ✓ review_ready | 1/1 | ✓ |

The content proxy is not a final semantic score. It requires conservative anchors and patterns; human review must check valid alternatives, evidence relevance, and suggestion quality. `english_qwen2.5_7b/provisional_review.md` holds the team's provisional reading, including a likely proxy false negative on `code_05`.

Reproducibility: a second execution with the same settings produced 6/6 byte-identical `raw_response` values (`english_qwen2.5_7b/repro_check.json`). The system prompt hash is stored in `run_metadata.json`.

## Superseded runs

`superseded_portuguese/` keeps the three earlier runs made with the original Portuguese task set and prompt (two prompt attempts that failed the protocol by copying `review_ready|needs_context`, and a final Portuguese run with protocol 6/6 and content proxy 0/6). They are kept in the working repository as history only (not included in the submission ZIP): they are excluded from the reported results and are not comparable with the English run, because the inputs, prompt, and lexical patterns changed. Their `summary.json` files were computed with the Portuguese grader patterns, which are no longer in `eval/tasks.json`.
