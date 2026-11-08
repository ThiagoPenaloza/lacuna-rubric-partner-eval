# EVAL_SPEC_V2 — rubric-writing partner

## Testable hypothesis

Given a goal, context, and a rubric draft, an LLM partner may fail to detect an important missing requirement, to tell a gap apart from missing context, to point out ambiguity precisely, or to offer actionable feedback. Another possible failure is suggesting criteria that change the goal instead of supporting the human decision. We test whether it identifies the right issue, anchors the observation in the text, calibrates when it needs to ask, and suggests an optional, verifiable revision. These are hypotheses; this specification contains no model results.

## Input and output contract

**JSON input:** `goal` (what is being evaluated), `context` (known requirements and constraints), `rubric_draft` (current criteria), and `history` (optional; earlier draft and partner response, the author's choice/edit). Benchmark content is synthetic.

**JSON output, with no surrounding text:**

```json
{"status":"review_ready","findings":[{"kind":"omission","criterion_ref":"","evidence":"excerpt of the input or empty","impact":"concrete risk","question":"question or empty","suggestion":"optional revision","confidence":"high"}],"human_decision_required":true}
```

`kind`: `omission`, `insufficient_context`, `ambiguity`, or `strength`; `status`: `review_ready` or `needs_context`. Only report an omission if the requirement is in the goal/context; otherwise ask instead of inventing it. Each finding quotes text or uses empty evidence for an absence, explains the impact, and suggests a bounded change. `suggestion` is a proposal, never an applied decision. Feedback must name the criterion/problem and a concrete action; "improve the rubric" is not enough. Extra fields earn no credit; invalid JSON or an incomplete schema is a format failure.

## Cases and adjudicated answer keys

Each item below is an independent input; the findings described are the expected answer key, not observed model output. Target rubrics say how to judge the partner's response. Multiple equivalent wordings are accepted.

### 1. Important requirement omitted
**Input:** goal: evaluate an incident report; context: must record the start time, the impact on users, and the recovery action; draft: "C1: The report describes the probable cause."
**Answer key:** an `omission` finding for impact and recovery (they may be separate); the evidence points to the requirements in the context and their absence from the draft; impact: the report states neither the scope nor the resolution. Optional suggestion: separate criteria requiring observable impact and the recovery action/outcome. `review_ready`. (Corrected after review: `eval/tasks.json` also requires the start time, which is equally explicit in the context.)
**Positive/negative:** the positive points out all of them; the negative only praises C1 or invents a cost/blame requirement. **Metric:** recall of the requirements, precision of findings (no inventions), evidence coverage.

### 2. Insufficient context
**Input:** goal: evaluate whether a summary "meets the customer's needs"; context: no customer profile, need, or operational rule is provided; draft: "C1: The summary is useful to the customer."
**Answer key:** `needs_context`; `insufficient_context`; points to vague terms and the missing profile/need; asks which need or outcome defines usefulness. Does not prescribe a requirement as if it were fact. Suggestion conditional on the author's answer, or empty.
**Positive/negative:** the positive asks and suspends judgment; the negative invents that the customer is a beginner or requires a 24h deadline. **Metric:** status accuracy, rate of unsupported assumptions, question quality (covers the needed information).

### 3. Ambiguous criterion
**Input:** goal: score a support response; context: resolution must happen within 2 business days; draft: "C1: Resolves the problem quickly."
**Answer key:** `ambiguity`: "quickly" defines neither a limit nor a unit; compare it with the given deadline. Optional suggestion: "Resolves within 2 business days", with an observable condition. `review_ready`.
**Positive/negative:** the positive identifies the term and offers the contextual threshold; the negative keeps "quickly" or invents 2 hours. **Metric:** localization accuracy, fidelity to the given limit, and verifiability of the suggestion.

### 4. Generic feedback
**Input:** goal/context: the rubric measures whether a summary contains a decision and an owner; draft: C1 explicit decision; C2 responsible person identified; previous feedback: "The rubric is vague; be more specific."
**Answer key:** identifies the feedback as unactionable, notes the missing criterion/location, and asks for a revision tied to C1/C2; concrete suggestion: state which textual evidence satisfies each criterion and a rule for absence. Does not declare C1/C2 vague without a reason.
**Positive/negative:** the positive locates the problem and the action; the negative repeats "be clearer" or rewrites without justification. **Metric:** share of actionable components present (location, reason, action) and fidelity to the draft.

### 5. Code/behavior requirement
**Input:** goal: rubric for an agent response that proposes a change to the `parse_date` function; context: valid ISO dates must become a date object; an invalid format must return an explicit error without terminating the process; draft: "C1: The code works correctly."
**Answer key:** points out that C1 is not observable and omits two behaviors; suggests separate criteria: valid ISO input produces the expected date; invalid input returns an explicit error and the process continues. Does not require an unspecified language, architecture, or style. `review_ready`.
**Positive/negative:** the positive covers success and error/continuity with observable behavior; the negative only proposes a happy-path test, or invents a library/language. **Metric:** recall of both behaviors, observability of the suggestion, count of invented requirements.

### 6. Iterative refinement
**Input:** goal: rubric for a support response; context: explain the next action and a deadline of up to 2 business days; initial draft: "C1: Useful response." history: the partner suggested splitting action and deadline; the author accepted the action and changed C1 to "States the next action"; the deadline still does not appear.
**Answer key:** recognizes the accepted edit and preserves scope; reports only the deadline as the remaining omission; suggests the explicit criterion "states a deadline of up to 2 business days". Does not present the resolved part as pending or change the author's decision. `review_ready`.
**Positive/negative:** the positive tracks the state and the remaining gap; the negative ignores the history, insists on the action already incorporated, or claims the author accepted a suggestion that was not accepted. **Metric:** accuracy on the residual gap, respect for history/decisions, and rate of duplicated resolved findings.

## Scoring and adjudication

Score each item separately: format (valid/invalid), identification (kind and requirement), evidence, impact, question when needed, faithful/verifiable suggestion, and preservation of the human decision. Use precision/recall/F1 of requirements and omissions, status accuracy, rate of invented assumptions, and rate of suggestions that preserve constraints. Adjudicate semantic equivalences; do not require model sentences. Thiago reviews inputs, answer keys, and weights before freezing. Report disagreements and evidence; never infer model results from these answer keys.
