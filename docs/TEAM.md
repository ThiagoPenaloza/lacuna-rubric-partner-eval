# Agent team — micro1

Coordinator: Codex, main conversation. The agents below are real terminals on the Maestri canvas; they work only on request, without automatic routines.

| Agent | Role | Model | Default effort | When to call |
|---|---|---|---|---|
| Prumo | Planning and scope | gpt-6-luna | medium | Initial plan, decomposition, and replanning |
| Forja | Development | gpt-6.1-sol | medium | Harness, graders, execution, and packaging |
| Crivo | Independent eval review and QA | gpt-6.1-sol | medium | Review of the spec, grader, and evidence at milestones |
| Spark | Idea discussion | gpt-6-luna | low | Explore the author's experience and compare hypotheses |

The selection is an operational cost/quality decision, not a measured result. Luna saves quota on bounded tasks; Sol handles implementation and grader validity. If a Luna task needs a hard judgment call, send a specific question to the coordinator, who can forward it to Crivo instead of duplicating the whole analysis.

Speed: Standard for the project agents. The inherited Fast mode was turned off to save quota, keeping the chosen model and effort.

## Usage economy
1. One bounded task per agent; use at most two specialists at the same time by default.
2. When done, record a short artifact and wait. No polling, recursive reviews, automatic tasks, or new agents without a concrete need.
3. Share context through docs/BRIEF.md and the project artifacts. Do not copy whole histories or files without need.
4. Up to 400 words in initial reports; reproducible details can go into the file the agent owns.
5. High effort only for a specific problem that medium did not solve; xhigh, max, ultra, and Astra are not defaults in this project. No extra spending or paid API was authorized.
6. Only Forja changes code. Prumo owns the plan, Spark the ideas, and Crivo the review report, avoiding concurrent edits.
7. The quota is shared by the account. Several terminals do not multiply the subscription. Check /status when needed; do not promise a fixed number of hours or tokens.

## Collaboration
Everyone connects to Codex and to the note "micro1 — Direction". Prumo, Forja, and Crivo have direct connections for handoffs. Spark connects to Prumo to turn a topic choice into a plan. Run maestri list before addressing messages. Do not start message chains without an explicit task; report once to the coordinator and wait.

Official sources consulted on 2026-11-06:
- Models: https://learn.chatgpt.com/docs/models
- Usage and plans: https://learn.chatgpt.com/docs/pricing
- Reasoning effort: https://developers.openai.com/api/docs/guides/reasoning

Speed and consumption: https://learn.chatgpt.com/docs/agent-configuration/speed

## Write limit of the current sessions

Maestri starts each specialist in a `.maestri/roles/<id>` folder, and the current sandbox allows writing only in that folder. The project documents could be read, but writing to the root was blocked in the first tasks. The coordinator's attempt to reconfigure the terminals with extra access did not run: the CLI socket returned Operation not permitted, and the session policy does not allow requesting elevated execution. Models, effort levels, connections, and Standard speed were configured and checked before that block.

Permission-compatible flow: specialists produce files in their own authorized folder and hand over the absolute path; Codex integrates and verifies them in the project root, which is writable in its session. Without automatic CLI messaging, the final terminal output serves as the handoff. The user can also talk to each terminal directly on the canvas. Do not retry blocked attempts in a loop or promise automatic collaboration while the CLI is unavailable.

The first hypotheses and the plan were integrated into docs/IDEAS.md and docs/PLAN.md. The agents are waiting for the next task.
