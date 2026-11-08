#!/bin/zsh
# Regenerates submission/startup_app_demo.mp4 from the real data in the repository.
# Free local tools only: Python 3 (stdlib), macOS `say` (English voice Samantha),
# Node.js, playwright-core (headless Chromium), and ffmpeg-static. No external upload.
#
# Usage:  submission/video_build/make_video.sh [output.mp4]
# Optional: LACUNA_TOOLS=/folder/with/node_modules (reuses dependencies already installed)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="${1:-$ROOT/submission/startup_app_demo.mp4}"
TOOLS="${LACUNA_TOOLS:-${TMPDIR:-/tmp}/lacuna-video-tools}"
BUILD="$(mktemp -d "${TMPDIR:-/tmp}/lacuna-video-build.XXXXXX")"

if [ ! -d "$TOOLS/node_modules/playwright-core" ] || [ ! -d "$TOOLS/node_modules/ffmpeg-static" ]; then
  mkdir -p "$TOOLS"
  [ -f "$TOOLS/package.json" ] || (cd "$TOOLS" && npm init -y >/dev/null)
  (cd "$TOOLS" && npm install --no-audit --no-fund playwright-core@1.56.1 ffmpeg-static@5.2.0 >/dev/null)
fi
node "$TOOLS/node_modules/playwright-core/cli.js" install chromium-headless-shell >/dev/null
FFMPEG="$(cd "$TOOLS" && node -e 'process.stdout.write(require("ffmpeg-static"))')"

echo "[1/5] real data → $BUILD/data.json"
python3 -B "$HERE/build_data.py" --out "$BUILD" >/dev/null
echo "[2/5] local narration (say) + timeline"
python3 -B "$HERE/build_audio.py" --out "$BUILD" --ffmpeg "$FFMPEG"
echo "[3/5] frame-by-frame capture (1920x1080, 30 fps)"
LACUNA_TOOLS="$TOOLS" node "$HERE/render.mjs" --build "$BUILD" --out "$BUILD/video.mp4" --workers "${LACUNA_WORKERS:-4}"
echo "[4/5] synthesized soundtrack and effects"
node "$HERE/music.mjs" --build "$BUILD"
echo "[5/5] mix (voice + ducked music + effects, -16 LUFS) and mux"
"$FFMPEG" -y -hide_banner -loglevel error \
  -i "$BUILD/video.mp4" -i "$BUILD/narration.wav" -i "$BUILD/music.wav" -i "$BUILD/sfx.wav" \
  -filter_complex "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v1][v2];\
[2:a]volume=0.55[m];[m][v2]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[md];\
[3:a]volume=0.8[s];[v1][md][s]amix=inputs=3:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT"
echo "video: $OUT"
echo "intermediate files (safe to delete): $BUILD"
