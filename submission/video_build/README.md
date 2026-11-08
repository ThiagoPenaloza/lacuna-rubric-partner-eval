# "Lacuna" demo video — regenerable script

Builds `submission/startup_app_demo.mp4` (1920×1080, 30 fps, H.264 + AAC, about 3 min 13 s) from the real files in the repository. The interface shown in the video is only a **render template** (`scene.html`), not a permanent product UI.

```bash
submission/video_build/make_video.sh            # default output: submission/startup_app_demo.mp4
```

Free local requirements: macOS (`say` with the English voice Samantha; `afinfo`), Python 3 (stdlib), Node.js. On the first run the script installs `playwright-core@1.56.1` and `ffmpeg-static@5.2.0` into a temporary folder (`$TMPDIR/lacuna-video-tools`) and uses Playwright's headless Chromium. Intermediate files go to a `mktemp` folder and can be deleted. Nothing is sent off the machine.

## Steps

| File | Role |
|---|---|
| `build_data.py` | Reads `eval/tasks.json`, `results/english_qwen2.5_7b/*` (raw responses, summary, provisional review, rerun check), and `docs/EVAL_SPEC_V2.md`; recomputes every check with `eval/metagrader.grade()`; runs the test suite and captures its real output. |
| `narration.json` | Script: on-screen caption (`text`) and an optional pronunciation spelling for the local voice (`tts`). |
| `build_audio.py` | Generates the narration with `say`, measures each clip, and builds the scene and caption timeline. |
| `scene.html` | Template with the screens, camera, cursor, and captions, all driven by `__renderAt(t)` in virtual (deterministic) time. |
| `render.mjs` | Captures frame by frame in headless Chromium (4 workers) and encodes H.264. `--stills 12,40` writes PNGs for review. |
| `music.mjs` | Synthesizes an original soundtrack and effects (no external samples). |
| `make_video.sh` | Orchestrates everything and mixes voice + ducked music + effects, normalized to −16 LUFS. |

## What the video shows (every number comes from `data.json`)

- The analysis is a **replay** of the run recorded in `results/english_qwen2.5_7b/` (English inputs, one attempt per task). The payload shown is the one the runner sends to the model: `task_id` + input fields. The answer key, `expected_status`, and `rejection_patterns` never enter the prompt.
- Metrics: 6 tasks; 24 passing tests; parseable JSON 6/6; protocol 6/6 (100%); content proxy 2/6 (33%); correct status 5/6; answer-key IDs found 7/9; literal evidence in 6/6 findings; rerun with the same settings 6/6 identical (`results/english_qwen2.5_7b/repro_check.json`).
- The "human edit" on the review screen is a simulated interaction that demonstrates the human gate. It is labeled as such and is not model output.
- The per-case readings come from `results/english_qwen2.5_7b/provisional_review.md`, a provisional team reading, not a final adjudication.
- The earlier Portuguese video and runs are kept in `submission/superseded_portuguese/` and `results/superseded_portuguese/`; they are excluded from the deliverable.
