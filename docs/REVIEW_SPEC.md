# Independent review of the specification

Status: validity checklist; not an approval and not an experimental result.

## Core risk

The eval must separate three objects: (1) the candidate answer, (2) the LLM's JSON judgment, and (3) the metagrader that compares that judgment with the human reference. An eloquent judgment does not make up for a wrong label; getting the label right by chance does not prove the evidence is correct.

## Gate before freezing

- Adjudicate each answer key with an explicit rule, evidence, and a record of human disagreements. Do not use another LLM as the only source of truth.
- Make every criterion that affects credit public; remove answer keys, labels, and revealing metadata from the grader input.
- Separate protocol/JSON errors from substantive errors in the report.
- Define weights, dependencies, vetoes for mandatory requirements, and the partial credit policy before the runs.
- Fix the number of attempts, clean sessions, versions, prompts, tools, retries, and exclusion reasons.

## False passes and false fails to test

1. Correct label with invented evidence, or correct evidence attributed to the wrong criterion.
2. Valid paraphrase rejected by text matching.
3. A long, confident answer, or one with an embedded instruction, receiving undue credit.
4. A mandatory absence treated as an acceptable inference.
5. Correct final score despite wrong individual criteria.
6. A parser that accepts duplicated/omitted IDs or that rejects only key order and whitespace.

## Metagrader tests

Use human fixtures, with no model calls, containing: correct judgments with alternative wordings; an inverted label; nonexistent, irrelevant, or swapped evidence; an omitted decision; a duplicated ID; an unknown criterion; truncated JSON; null and out-of-schema values. Recompute the decision from the criteria vector and make sure weights and penalties are applied only once.

For each paraphrase or irrelevant-detail variant, record the transformation and the criteria that must stay the same. Add minimal substantive mutations that must change only the affected criteria. Measure invariance and correctness separately: two equally wrong evaluations are consistent, but not correct.

## Recommendation on the six tasks

The six cases in the specification should stay in the same professional domain, to reduce dependence on outside knowledge, and cover consistency, evidence, mandatory requirement, correct alternative, inclusive limit, and invariance separately. Each sheet needs the request, context, full candidate, atomic criteria, point rule, answer key, expected evidence, accepted alternatives, a negative case, and control mutations.

The next milestone is for Thiago to review the six answer keys and confirm that each decision is defensible. Then Forja can implement the offline metagrader and Crivo should test the positive and negative fixtures before any model run.
