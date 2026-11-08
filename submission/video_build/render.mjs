#!/usr/bin/env node
// Renders scene.html frame by frame (deterministic virtual time) and encodes H.264.
// Usage: node render.mjs --build DIR --out video.mp4 [--fps 30] [--workers 4] [--stills 5,40.2]
// Requires LACUNA_TOOLS pointing to a folder with playwright-core and ffmpeg-static installed.
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith("--")) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]);
  return acc;
}, []));
const TOOLS = process.env.LACUNA_TOOLS;
if (!TOOLS) throw new Error("Set LACUNA_TOOLS (folder with playwright-core and ffmpeg-static).");
const require = createRequire(path.join(TOOLS, "package.json"));
const { chromium } = require("playwright-core");
const FFMPEG = require("ffmpeg-static");

const BUILD = path.resolve(args.build);
const FPS = +(args.fps || 30);
const WORKERS = +(args.workers || 4);
const SCALE = +(args.scale || 1.5);
const data = fs.readFileSync(path.join(BUILD, "data.json"), "utf8");
const timeline = fs.readFileSync(path.join(BUILD, "timeline.json"), "utf8");
const TOTAL = JSON.parse(timeline).total;
const FRAMES = Math.ceil(TOTAL * FPS);

async function newPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: SCALE });
  await page.addInitScript(`window.LACUNA_DATA=${data};window.LACUNA_TIMELINE=${timeline};`);
  page.on("pageerror", e => { console.error("pageerror:", e.message); process.exitCode = 1; });
  await page.goto(pathToFileURL(path.join(HERE, "scene.html")).href);
  await page.waitForFunction(() => window.__ready === true);
  await page.evaluate(() => document.fonts.ready);
  return page;
}
// Advances frame by frame without capturing, so the state matches a sequential render.
const advance = (page, f0, f1) => page.evaluate(([a, b, fps]) => { for (let f = a; f < b; f++) window.__renderAt(f / fps); }, [f0, f1, FPS]);

async function renderSegment(browser, idx, f0, f1, out) {
  const page = await newPage(browser);
  await advance(page, 0, f0);
  const ff = spawn(FFMPEG, ["-y", "-hide_banner", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS),
    "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
    "-r", String(FPS), out], { stdio: ["pipe", "inherit", "inherit"] });
  const done = new Promise((res, rej) => ff.on("close", c => c === 0 ? res() : rej(new Error("ffmpeg " + c))));
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    await page.evaluate(t => window.__renderAt(t), f / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if ((f - f0) % 300 === 0) console.log(`[w${idx}] ${f - f0}/${f1 - f0} frames · ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await done;
  const sfx = await page.evaluate(() => window.__sfx);
  await page.close();
  return sfx;
}

const browser = await chromium.launch();
try {
  if (args.stills) {
    const dir = path.join(BUILD, "stills");
    fs.mkdirSync(dir, { recursive: true });
    for (const t of String(args.stills).split(",").map(Number)) {
      const page = await newPage(browser);
      const f = Math.round(t * FPS);
      await advance(page, 0, f + 1);
      const file = path.join(dir, `still_${t.toFixed(1).padStart(6, "0")}.png`);
      await page.screenshot({ path: file });
      console.log(file);
      await page.close();
    }
  } else {
    const out = path.resolve(args.out);
    const per = Math.ceil(FRAMES / WORKERS);
    const parts = [];
    const jobs = [];
    for (let i = 0; i < WORKERS; i++) {
      const f0 = i * per, f1 = Math.min(FRAMES, (i + 1) * per);
      if (f0 >= f1) break;
      const part = path.join(BUILD, `part_${i}.mp4`);
      parts.push(part);
      jobs.push(renderSegment(browser, i, f0, f1, part));
    }
    const sfxLists = await Promise.all(jobs);
    // Sound events are identical in every worker (same cues); use the last complete list.
    const all = sfxLists[sfxLists.length - 1].filter(e => e.t <= TOTAL);
    fs.writeFileSync(path.join(BUILD, "sfx.json"), JSON.stringify(all, null, 1));
    const list = path.join(BUILD, "parts.txt");
    fs.writeFileSync(list, parts.map(p => `file '${p}'`).join("\n"));
    await new Promise((res, rej) => spawn(FFMPEG, ["-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
      "-i", list, "-c", "copy", out], { stdio: "inherit" }).on("close", c => c === 0 ? res() : rej(new Error("concat " + c))));
    console.log(`video: ${out} · ${FRAMES} frames · ${TOTAL}s`);
  }
} finally {
  await browser.close();
}
