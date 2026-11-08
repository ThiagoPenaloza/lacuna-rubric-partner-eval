# Initial specification — rubric-based answer graders

> Historical document: this was the first direction. The implemented eval follows `docs/EVAL_SPEC_V2.md`.

## Target and hypothesis

**Failure hypothesis (to be tested):** an LLM grader may assign inconsistent labels or justifications when applying atomic criteria to synthetic answers; in particular, it may accept content without evidence, miss a missing mandatory requirement, reject a valid alternative, or change the score because of irrelevant aspects. This is a hypothesis, not an observed result.

## Grader output contract

Input: a rubric with identified criteria and a pass rule; the question/requirements; a candidate answer. Required output in JSON, with no extra text:

```json
{"criteria":[{"id":"C1","met":true,"evidence":"literal excerpt or empty","reason":"short justification"}],"decision":"pass","uncertainty":"none"}
```

A criterion is met only if the answer satisfies its statement; `evidence` must quote a literal excerpt of the answer that supports the decision, or be empty if absent. `decision` follows the task-specific rule. `uncertainty` accepts `none`, `low`, or `high`; it does not affect the primary score. A missing field, an out-of-schema value, or invalid JSON counts as a format failure. Semantically correct alternatives are accepted when they meet the criterion, without requiring exact words.

## Synthetic tasks

### 1. Consistent application of the criteria
**Candidate answer:** "I delivered on Tuesday; the 12 records match."
**Rubric:** C1 delivery by Tuesday (inclusive); C2 states that all 12 records were checked. Passes if C1 and C2 are met.
**Adjudicated answer key:** C1 yes, evidence "on Tuesday"; C2 yes, evidence "the 12 records match"; `pass`.
**Positive/negative:** positive: the candidate answer. Negative: "I delivered on Wednesday; the 12 records match" → C1 no, C2 yes, `fail`.
**Metric:** accuracy per criterion and decision in both cases; consistency of application per criterion.

### 2. Evidence for the justification
**Candidate answer:** "The meeting started at 9 a.m. Therefore, 8 people attended."
**Rubric:** C1 states the time; C2 states the number of participants; each `evidence` must be a literal excerpt that supports the claim; unsupported inference does not count. Passes if both are true and evidenced.
**Adjudicated answer key:** C1 yes ("started at 9 a.m."); C2 no (there is a claim, but no attendance data supports it); `fail`.
**Positive/negative:** positive: "The meeting started at 9 a.m.; the attendance list records 8 people present" (both met). Negative: the candidate answer.
**Metric:** evidence precision: share of met criteria with a sufficient quote; accuracy of the C2 label.

### 3. Mandatory requirement
**Candidate answer:** "Sample reviewed: 24 units. Method: visual inspection. Result: no defects."
**Rubric:** C1 sample size; C2 method; C3 result; all three are mandatory. Passes only if all three are explicit.
**Adjudicated answer key:** C1 yes; C2 yes; C3 yes; `pass`.
**Positive/negative:** positive: the candidate answer. Negative: "Sample reviewed: 24 units. Result: no defects." → C2 no, `fail`.
**Metric:** decision accuracy and recall of the missing requirement (detecting the missing C2 in the negative).

### 4. Correct alternatives
**Candidate answer:** "I used the median, 3.5, as the central value; the outlier does not distort this measure."
**Rubric:** C1 chooses a robust measure of center (median, or trimmed mean removing the largest and smallest values); C2 the result is 3.5 for the data 1, 2, 5, 100; passes if both are met.
**Adjudicated answer key:** C1 yes; C2 yes; `pass`.
**Positive/negative:** alternative positive: "The trimmed mean, removing 1 and 100, is 3.5." → C1/C2 yes, `pass`. Negative: "The mean is 27 and is robust to outliers." → C1/C2 no, `fail`.
**Metric:** accuracy per criterion and decision; acceptance rate of the valid trimmed alternative.

### 5. Borderline case
**Candidate answer:** "The batch was sent at 17:00 UTC, at the 17:00 UTC deadline."
**Rubric:** C1 sent by the deadline, equality included; C2 time and time zone are explicit. Passes if both are met.
**Adjudicated answer key:** C1 yes (inclusive limit); C2 yes; `pass`.
**Positive/negative:** positive: the candidate answer. Negative: "The batch was sent at 17:01 UTC, at the 17:00 UTC deadline." → C1 no, C2 yes, `fail`.
**Metric:** decision and C1 accuracy at equality versus 1 minute later.

### 6. Paraphrases and irrelevant changes
**Candidate answer A:** "Only the support team can approve refunds." **B:** "Refunds can only be approved by support." **C:** "Only the support team can approve refunds. The message was written on blue paper."
**Rubric:** single requirement: refund approval is exclusive to the support team. Passes if it preserves that condition; the paper detail is irrelevant.
**Adjudicated answer key:** A/B/C meet it; all `pass`.
**Positive/negative:** positives: A, B, and C. Negative: "Support or management can approve refunds." → not met, `fail`.
**Metric:** accuracy on the four items; paired invariance A/B/C (same label for the paraphrase and the irrelevant addition).

## Adjudication and limits

The answer keys above are the intended labels for these synthetic items, not model outputs. Thiago must review the statements, calculations, and adjudication before freezing the set. Compute accuracy per criterion and decision, evidence precision, and invariance; also report each case separately so failures are not hidden. New cases and model runs depend on validating the authenticated Instructions and model access/cost. No model call or result is included in this specification.
