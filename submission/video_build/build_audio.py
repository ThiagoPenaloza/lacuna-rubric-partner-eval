#!/usr/bin/env python3
"""Local narration (macOS `say`) + timeline of scenes and captions.

Usage: python3 -B build_audio.py --out DIR --ffmpeg PATH
Writes DIR/voice/*.wav, DIR/narration.wav, and DIR/timeline.json.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def duration(path):
    out = subprocess.run(["afinfo", str(path)], capture_output=True, text=True, check=True).stdout
    return float(re.search(r"estimated duration: ([0-9.]+)", out).group(1))


def split_balanced(part, limit):
    if len(part) <= limit:
        return [part]
    # Prefer punctuation; otherwise the space closest to the middle. Avoid short fragments.
    cands = [m.end() for m in re.finditer(r"[,;:—]\s", part) if 18 <= m.end() <= len(part) - 18]
    if not cands:
        cands = [m.end() for m in re.finditer(r"\s", part) if 18 <= m.end() <= len(part) - 18]
    if not cands:
        return [part]
    cut = min(cands, key=lambda c: max(c, len(part) - c))
    return split_balanced(part[:cut].strip(), limit) + split_balanced(part[cut:].strip(), limit)


def chunks(text, limit=78):
    """Split the caption into short, readable chunks."""
    result = []
    for part in re.split(r"(?<=[.!?])\s+", text.strip()):
        if part:
            result += split_balanced(part, limit)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    cfg = json.loads((HERE / "narration.json").read_text(encoding="utf-8"))
    out = Path(args.out)
    voice_dir = out / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    t = 0.0
    scenes, lines = [], []
    for scene in cfg["scenes"]:
        start = t
        t += scene.get("lead", 0.4)
        last_end = t
        for line in scene["lines"]:
            wav = voice_dir / f"{line['id']}.wav"
            raw = voice_dir / f"{line['id']}.raw.wav"
            subprocess.run(["say", "-v", cfg["voice"], "-r", str(line.get("rate", cfg["rate"])),
                            "--file-format=WAVE", "--data-format=LEI16@48000", "-o", str(raw),
                            line.get("tts", line["text"])], check=True)
            subprocess.run([args.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
                            "-af", f"atempo={line.get('tempo', 1.0)}", str(wav)], check=True)
            d = duration(wav)
            pieces = chunks(line["text"])
            weights = [len(p) + 6 for p in pieces]
            caps, c = [], t
            for piece, w in zip(pieces, weights):
                span = d * w / sum(weights)
                caps.append({"start": round(c, 3), "end": round(c + span, 3), "text": piece})
                c += span
            lines.append({"id": line["id"], "scene": scene["id"], "start": round(t, 3), "end": round(t + d, 3),
                          "text": line["text"], "wav": str(wav), "captions": caps})
            last_end = t + d
            t = last_end + scene.get("gap", cfg["gap"])
        t = last_end + scene.get("tail", 0.6)
        scenes.append({"id": scene["id"], "start": round(start, 3), "end": round(t, 3)})
    total = round(t, 3)

    # Narration track: each clip placed at its exact start.
    cmd = [args.ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
    for line in lines:
        cmd += ["-i", line["wav"]]
    filters = []
    for i, line in enumerate(lines):
        ms = int(round(line["start"] * 1000))
        filters.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,adelay={ms}|{ms}[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(len(lines))) +
                   f"amix=inputs={len(lines)}:normalize=0,apad=whole_dur={total}[mix]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[mix]", "-ac", "1", "-ar", "48000",
            "-t", str(total), str(out / "narration.wav")]
    subprocess.run(cmd, check=True)

    timeline = {"total": total, "scenes": scenes,
                "lines": [{k: v for k, v in l.items() if k != "wav"} for l in lines]}
    (out / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for s in scenes:
        print(f"{s['id']:<9} {s['start']:7.2f} → {s['end']:7.2f}  ({s['end'] - s['start']:.1f}s)")
    print(f"total {total:.2f}s")


if __name__ == "__main__":
    main()
