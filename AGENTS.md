# micro1 Eval Hackathon

The real project root is `/Users/thiagopenaloza/Documents/micro1 Hackaton`.

Maestri may start agents in `.maestri/roles/<id>`. That directory holds the role instructions. The current specialist sessions may only write inside their own role folder. Read the sources from the real root; produce new artifacts inside the authorized folder and give the coordinator their absolute path. The coordinator integrates the result into the real root and verifies the integrated version. Do not try to change permissions or write outside the authorized locations. The canonical version of the docs stays in the real root.

Read `docs/BRIEF.md` and `docs/TEAM.md` in the real root. Work only on the delegated task. The topic is chosen with Thiago; do not implement a hypothesis before that choice. One agent per file: Prumo writes the plan, Spark the ideas, Crivo the review, and Forja the code. Save context and do not start collaboration loops.

When using the Maestri CLI, prefer the direct `maestri` command instead of hiding it inside Python or another wrapper. If a message fails because of permissions, do not retry in a loop: record the outcome in the final answer so the coordinator can read it from the terminal.

All project-facing text (documentation, code comments, CLI messages, fixtures, and the video) is in English.
