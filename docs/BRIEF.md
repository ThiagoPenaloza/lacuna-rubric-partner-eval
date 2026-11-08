# micro1 Eval Hackathon — working brief

Author and participant: Thiago Penaloza. AI tools assist the participant; they are not a human team. The topic was chosen with Thiago based on his verifiable experience.

## Goal
Build a small, rigorous, and reproducible eval of a real professional limitation of current models. The first deliverable was to organize the agent team and discuss ideas, not to implement an idea before Thiago's choice.

## Deadline and sources
- Closes: 2026-11-09 05:15 UTC = 2026-11-09 02:15 America/Sao_Paulo.
- Proposed internal target: package ready by 2026-11-08 20:00 Sao Paulo time.
- Event: https://www.hackerrank.com/event/micro1-eval-hackathon
- Public guide: https://hrcdn.net/s3_pub/istreet-assets/R_8vs8ejamSPapSbUxmcWQ/Eval_Hackathon_Participant_Guide.pdf
- Check the Instructions tab of the authenticated challenge before freezing the format; it has not been accessed yet.

## Expected deliverable
A ZIP of code and small support files, up to 50 MB, with a README; an external video of up to 5 minutes; a short description. Do not include videos or credentials in the ZIP. Do not submit automatically.

## Chosen direction

Eval of LLMs as partners for writing rubrics/graders. The target is to test whether the model detects important requirements an author left out, explains the gap, and suggests a useful revision without replacing human judgment. Thiago's experience comes from AI training projects at Scale AI/Outlier. The specification is in `docs/EVAL_SPEC_V2.md`; `docs/EVAL_SPEC.md` records the earlier direction and is kept as history.

## Operating direction
- Prefer 5–10 clear professional tasks, with a verifiable answer key and explicit criteria.
- Use incomplete rubrics, task context, and the agent response as input; require the model to identify omissions, explain impact, and propose verifiable criteria.
- Measure recall of omitted requirements, precision of critiques, usefulness of revisions, specificity of feedback, and preservation of human judgment.
- Prefer a deterministic grader where appropriate; validate acceptance of alternative correct answers and rejection of deliberate errors.
- Evaluate every model with the same tasks and criteria. Record version, effort, available tools, prompts, and raw responses.
- Validate the mechanism without model calls; only run real experiments after the topic and the model access path are defined.
- Plan multiple independent attempts per task (3–5 is a recommendation from the guide), with at least one frontier model and one smaller model when feasible.
- Distinguish a failure hypothesis from an observed failure. Do not fabricate results or select only failed attempts.
- Thiago must review every task, answer key, and rule, and write/validate the analysis. Declare AI use and the provenance of data and ideas.

## Budget constraints
Local login confirmed as ChatGPT, without reading or exposing secrets. The Plus plan was confirmed on one agent's /status screen. The quota is dynamic and is not a fixed token budget. At setup time, /status showed 78% remaining in the 5-hour window and 96% for the week; these numbers change with use. Agent sessions share the account quota; do not add limits up as if they were individual. Credits and any promotional API access must be checked separately; do not assume API access is included or buy services.

## Open items
1. Thiago's review of the six task statements, answer keys, and calculations.
2. Full instructions of the authenticated challenge.
3. A reproducible path and cost for getting model responses (a free local Ollama run is in place; frontier models are not).
4. Grader test plan and independent review.
