# micro1 eval plan

**Internal target:** a reviewable package by 2026-11-08, 8 p.m. (America/Sao_Paulo). The official deadline stated in the brief is 2026-11-09, 2:15 a.m. No experiment or topic is presumed.

| When | Owner | Step and deliverable | Criterion to move on |
|---|---|---|---|
| 11/06 | Thiago, with Spark if requested | Review of the Scale AI/Outlier experience and of the `docs/EVAL_SPEC_V2.md` specification | Thiago validates the six scenarios, omitted requirements, and answer keys; without this review, no model run starts. |
| 11/06 | Codex | Check the authenticated challenge Instructions and record format, rules, submission, and limits | Instructions checked; resolve differences with the brief before freezing scope. |
| 11/06–11/07 | Prumo + Thiago; Crivo reviewing | Refine `docs/EVAL_SPEC_V2.md` with 5–10 scenarios, JSON contract, expected requirements, verifiable answer keys, and usefulness criteria | Each scenario has a known omission, expected critique, minimum acceptable revision, valid alternatives, and a deliberate error; Thiago approves tasks and analysis. |
| 11/07 | Codex + Thiago | Documented decision on model access, cost, availability, and recording of versions/settings | Reproducible path and acceptable cost confirmed. Do not assume API/credits; while the path is pending, advance the task set, answer keys, and offline validation without inventing results. |
| 11/07 | Forja + Codex | Harness/metagrader and initial package | Offline V2 metagrader implemented in `eval/`, with six fixtures, format/content separation, literal evidence, and a verifiable-suggestion proxy; 24 integrated tests pass. |
| 11/08, by 2 p.m. | Thiago + Forja | Authorized runs (3–5 independent attempts per task, if feasible), raw responses, versions, effort, tools, and prompts | Same tasks and criteria for every model; separate hypothesis from observed failure; do not select attempts. If access/cost prevents it, record the limitation without inventing results. |
| 11/08, 2 p.m.–6 p.m. | Thiago; Crivo; Codex | Human review, analysis, provenance/AI declaration, and fixes | Evidence supports every claim; answer keys and grader pass independent review; Thiago validates analysis and content. |
| 11/08, 6 p.m.–8 p.m. | Forja + Codex; Thiago approves | README, ZIP ≤50 MB, short description, and external video ≤5 min, if feasible | Artifacts open, match the authenticated Instructions, and include no video or credentials in the ZIP; final review by Thiago. Do not submit automatically. |
| 11/08 | Codex + Claude | Migrate the whole package to English: docs, code comments, CLI messages, fixtures, answer keys, anchors, patterns, prompt, and video | Unit tests pass with the English fixtures; a new local `qwen2.5:7b` run with English inputs is preserved in `results/english_qwen2.5_7b/`; Portuguese runs move to `results/superseded_portuguese/`; the video is regenerated in English from that run. |

**Critical dependencies:** Thiago's verifiable experience and choice; access to the authenticated Instructions; reproducible access to models and their cost. Validate the mechanism without calls before any experiment. The account quota is shared and dynamic; do not treat agents as independent limits or buy services.

**Integration:** specialists write in their own authorized folders; Codex gathers and verifies the artifacts in the project root.

**Current state:** the V2 direction was chosen, the six-task offline scaffold is in `eval/`, the suite passes with 24 tests, and the English local Qwen run is preserved in `results/english_qwen2.5_7b/` (protocol 6/6, content proxy 2/6, one attempt per task, 6/6 raw responses identical on rerun). The English video is `submission/startup_app_demo.mp4`. Only the final human review and the external submission remain.
