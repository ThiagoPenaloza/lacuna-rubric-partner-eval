# Final video script — Lacuna (3:13.5)

The final video is `submission/startup_app_demo.mp4`: 3:13.5, 1920×1080, 30 fps, H.264 with stereo AAC, English narration (local macOS voice Samantha) and English captions. It was checked with ffprobe, Spotlight metadata (mdls), a full decode, and a visual review of frames.

All numbers and model outputs on screen come from the English local run in `results/english_qwen2.5_7b/` (qwen2.5:7b, temperature 0, seed 17, one attempt per task).

## Sequence

1. **Opening (0:00–0:07):** Lacuna, the problem ("Incomplete rubric, wrong grade.") and the promise: find the gap with literal evidence and human review.
2. **Input (0:07–0:23):** `goal`, `context`, and `rubric_draft` of the `incident_01` case; the three requirements in the context are emphasized.
3. **Analysis (0:23–1:10):** the real payload the runner sends (answer key, expected status, and rejection patterns stay out of the prompt), the recorded qwen2.5:7b response, the 6/6 identical rerun, the raw JSON, the finding card with literal evidence highlighted in the input, impact, question, suggestion, and the metagrader signals. On this case the content proxy passes.
4. **Human review (1:10–1:28):** the human gate (accept, edit, reject); the edit is labeled as simulated; the proxy is shown as a conservative signal, not a verdict, next to the pending human adjudication.
5. **Dashboard (1:28–1:55):** six tasks, 24 passing tests (real suite output), protocol 6/6 (100%), content proxy 2/6 (33%), correct status 5/6 (the model never chose `needs_context`), answer-key IDs 7/9, literal evidence 6/6, and the 6/6 rerun check.
6. **Six cases (1:55–2:42):** missing requirement (passes), insufficient context (wrong status), ambiguity (no verifiable threshold), generic feedback (history ignored), code behavior (likely proxy false negative), iterative refinement (passes), each with the team's provisional reading.
7. **Hypothesis and limits (2:42–3:13):** the model finds explicit omissions but struggles to ask for missing context, use the history, and make vague criteria verifiable; limits: six synthetic tasks, one local model, one attempt per task, answer keys pending human adjudication; next step: frontier models with 3–5 attempts per task.

## Reproduction

```bash
cd "/Users/thiagopenaloza/Documents/micro1 Hackaton"
submission/video_build/make_video.sh
```

The build uses only local project data: `eval/tasks.json`, the preserved English run, and the metagrader. A local rerun of qwen2.5:7b produced raw responses identical to the recorded ones; this is documented in `results/english_qwen2.5_7b/repro_check.json`. The earlier Portuguese video is kept, excluded from the deliverable, in `submission/superseded_portuguese/`.
