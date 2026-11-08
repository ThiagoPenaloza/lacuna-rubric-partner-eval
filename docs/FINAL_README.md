# Eval: the LLM as a rubric-writing partner

> **Status:** offline V2 package ready for human review and submission. The metagrader and the six fixtures pass locally (24 tests). One free local exploratory run (`qwen2.5:7b`, English inputs, one attempt per task) is preserved with raw responses; it is not a general model score.

## Problem

Rubric authors can leave important requirements out, use vague criteria, or receive feedback that does not explain how to improve. A useful assistant should point out gaps grounded in the goal and context, explain the risk, and suggest an optional revision. The final decision on scope and wording stays with the author.

## Hypothesis

In synthetic rubric-writing and rubric-review tasks, an LLM may fail to find omissions, to tell missing information apart from insufficient context, to explain ambiguities, and to produce specific suggestions without inventing requirements or ignoring earlier human decisions. This is a hypothesis to test, not an observed result.

## Tasks

The set has six synthetic cases in the same domain of rubric-writing assistance:

1. Detect important requirements omitted from a criterion.
2. Ask for context when the goal and rubric do not define what counts as success.
3. Locate ambiguous terms and propose an observable wording using the limits given.
4. Identify generic feedback and turn it into a located, concrete action.
5. Turn code requirements into testable behaviors, covering success and error.
6. Track iterative refinement, preserving accepted choices and pointing out only the remaining gaps.

Inputs, expected answer keys, and positive/negative cases are described in `docs/EVAL_SPEC_V2.md` and materialized in `eval/tasks.json`. The answer keys require human review before the benchmark is frozen.

## Contract and grader

Each input provides `goal`, `context`, `rubric_draft`, and, optionally, `history`. The partner returns structured JSON with `status`, `findings`, and `human_decision_required`. Each finding gives the kind, a reference to the criterion, evidence from the input, impact, a question when needed, an optional suggestion, and confidence. The partner does not apply changes or replace human judgment.

The grader separates two things:

- **Protocol:** valid JSON, fields and values in the schema, no missing required fields. Format failures are reported separately.
- **Content:** compare findings with the answer keys, accepting only the paraphrases made explicit by anchors and patterns. A correct label does not make up for invented or swapped evidence; an eloquent justification does not make up for a wrong label. This content check is a conservative lexical proxy, not semantic adjudication.

The offline metagrader is validated with correct fixtures and mutations: invalid JSON, non-standard constants, duplicate keys, missing fields, wrong types, fabricated evidence, empty findings, denied gaps, inverted deadlines even when the correct deadline is also present, missing error/continuity behavior in code, unlocated feedback, and explicitly accepted paraphrases. Weights, partial credit, and the final aggregation policy are **pending confirmation** by Thiago.

## Metrics

Report per task and in aggregate: format validity; precision, recall, and F1 of requirements/omissions; status accuracy; evidence coverage and precision; rate of unsupported assumptions; question quality when context is missing; verifiability and fidelity of suggestions; respect for the history and the author's decisions. Also report false passes/fails and paraphrase invariance separately from correctness. Weights, dependencies, vetoes, and the partial credit rule must be defined before the runs.

## How to run

1. Requires Python 3.9+ (standard library only).
2. Run the metagrader fixtures, with no model calls:

   ```bash
   python3 -B -m unittest discover -s eval -p 'test_*.py' -v
   ```

3. To inspect a local JSON response against a task:

   ```bash
   python3 eval/metagrader.py incident_01 response.json
   ```

   `response.json` must contain only the partner contract; do not include answer keys in the model prompt.
4. Free local run (optional, needs [Ollama](https://ollama.com) and the `qwen2.5:7b` model):

   ```bash
   ollama serve
   python3 -B eval/run_ollama.py --model qwen2.5:7b --out results/english_qwen2.5_7b
   python3 -B eval/score_run.py results/english_qwen2.5_7b
   ```

   The runner sends only `task_id` and the input fields. `expected_findings`, `expected_status`, and `rejection_patterns` are never sent to the model.
5. For other models, run the same tasks in clean sessions with a fixed number of attempts (**number to be defined**). Preserve raw responses, model versions, effort, tools, prompts, retries, and exclusion reasons; compute the metrics with the frozen grader.

## Results

One free, local exploratory run with Ollama and `qwen2.5:7b` (temperature 0, seed 17), on the English task set, one attempt per task:

| Metric | Result |
|---|---:|
| Parseable JSON | 6/6 (100%) |
| Protocol accepted | 6/6 (100%) |
| `content_proxy_passed` | 2/6 (33%) — `incident_01`, `iteration_06` |
| Correct status | 5/6 |
| Answer-key IDs found by the proxy | 7/9 |
| Findings with literal evidence | 6/6 |
| Rerun with the same settings | 6/6 identical raw responses |

The content proxy is a conservative diagnostic, not semantic adjudication. The team's provisional reading (`results/english_qwen2.5_7b/provisional_review.md`) flags `code_05` as a likely proxy false negative and points to the real failures in `context_02` (wrong status and kind), `ambiguity_03` (no verifiable threshold in the suggestion), and `feedback_04` (ignored the generic feedback in the history). Raw responses, inputs, metadata, and the summary are in `results/english_qwen2.5_7b/`.

Earlier runs used the original Portuguese task set and prompt. They are archived in `results/superseded_portuguese/` in the working repository (not in the submission ZIP) and excluded from the reported results; they are not directly comparable, because the language, prompt, and lexical patterns changed.

Do not extrapolate this run to general performance: it is a single local model, one attempt per task, and six synthetic examples.

## Limitations

Six synthetic tasks do not show generalization to real rubrics or to every domain. Human answer keys can have disagreements; record adjudicators, evidence, and disagreements. The lexical proxy is order- and wording-sensitive and can produce false negatives (see `code_05`) as well as false positives. Metrics depend on weights and a credit policy defined in advance. Responses can vary across runs and versions. Access, cost, comparable frontier models, the number of attempts, and the final format still depend on confirmation. Synthetic input reduces exposure of personal data but does not replace evaluation in a real usage context.

## AI use and provenance

The project evaluates an LLM as a rubric-writing partner. AI agents (Codex and Claude) also helped draft this specification, the code, the English translation, the README, and the demo video. The six examples are synthetic; they are not model responses or empirical observations. Before publishing, declare the models and tools used in preparation, relevant prompts/settings, human authorship of the answer keys, and the provenance/licenses of any additional material. No credentials or secrets are included in the package.

## Submission checklist

- [ ] Thiago reviewed and adjudicated each answer key, acceptable alternative, piece of evidence, and disagreement.
- [ ] Authenticated challenge Instructions checked; delivery format and requirements validated.
- [x] The model input does not reveal answer keys or response metadata (`eval/run_ollama.py` sends only `task_id` and the input).
- [x] The offline metagrader passed positive, negative, and format fixtures; protocol and content are reported separately.
- [ ] Weights, dependencies, veto, and partial credit defined before the runs.
- [ ] Attempts, clean sessions, versions, prompts, tools, retries, and exclusions recorded for every model beyond the local run.
- [x] A local exploratory run was preserved with raw data and limitations, without fabricating or selecting results.
- [ ] README, commands, dependencies, artifacts, and publication links checked by Thiago.
- [x] ZIP smaller than 50 MB with a README; external video of 3:13.5 and a short description prepared.
- [ ] No video or credentials in the ZIP; final human review done; nothing submitted automatically.
