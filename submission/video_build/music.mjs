#!/usr/bin/env node
// Original soundtrack synthesized locally (no external samples) + sound effects.
// Usage: node music.mjs --build DIR   (reads timeline.json and sfx.json; writes music.wav and sfx.wav)
import fs from "node:fs";
import path from "node:path";

const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith("--") && a.push([v.slice(2), arr[i + 1]]), a), []));
const BUILD = path.resolve(args.build);
const TL = JSON.parse(fs.readFileSync(path.join(BUILD, "timeline.json"), "utf8"));
const SFX = fs.existsSync(path.join(BUILD, "sfx.json")) ? JSON.parse(fs.readFileSync(path.join(BUILD, "sfx.json"), "utf8")) : [];
const SR = 48000, DUR = TL.total, N = Math.ceil(DUR * SR);
const sc = id => TL.scenes.find(s => s.id === id);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647 * 2 - 1;

function writeWav(file, L, R) {
  const buf = Buffer.alloc(44 + L.length * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + L.length * 4, 4); buf.write("WAVE", 8); buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(L.length * 4, 40);
  for (let i = 0; i < L.length; i++) {
    buf.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(L[i] * 32767))), 44 + i * 4);
    buf.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(R[i] * 32767))), 46 + i * 4);
  }
  fs.writeFileSync(file, buf);
}
const hz = m => 440 * Math.pow(2, (m - 69) / 12);
const smooth = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);

/* ---------- music ---------- */
const BPM = 96, BEAT = 60 / BPM, CH = 8 * BEAT; // one chord every 2 bars
const CHORDS = [ // Fmaj7, Am7, Cmaj7, G6 — mid voicings + bass
  { root: 41, notes: [53, 57, 60, 64] },
  { root: 45, notes: [57, 60, 64, 67] },
  { root: 48, notes: [55, 60, 64, 71] },
  { root: 43, notes: [55, 59, 62, 64] },
];
const L = new Float32Array(N), R = new Float32Array(N);
const tIn = sc("input").start, tClose = sc("close").start;
const lp = [0, 0, 0, 0, 0, 0, 0, 0];
const phase = new Float64Array(16);
let bassPh = 0;
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const k = Math.floor(t / CH), u = (t % CH) / CH;
  const cur = CHORDS[k % 4], nxt = CHORDS[(k + 1) % 4];
  const xf = smooth((u - .9) / .1); // crossfade at the end of the chord
  // pad: two slightly detuned triangle oscillators per note, filtered
  let pl = 0, pr = 0;
  for (let n = 0; n < 4; n++) {
    for (const [ci, chord, w] of [[0, cur, 1 - xf], [1, nxt, xf]]) {
      if (w <= 0) continue;
      const f = hz(chord.notes[n]);
      const idx = n * 4 + ci * 2;
      phase[idx] += f * 1.0016 / SR; phase[idx + 1] += f * 0.9984 / SR;
      const tri = p => 1 - 4 * Math.abs((p % 1) - .5);
      pl += w * tri(phase[idx]); pr += w * tri(phase[idx + 1]);
    }
  }
  const a = 0.06;
  lp[0] += a * (pl - lp[0]); lp[1] += a * (pr - lp[1]);
  const swell = .55 + .45 * Math.sin(2 * Math.PI * t / (CH * 2));
  let padL = lp[0] * .055 * swell, padR = lp[1] * .055 * swell;
  // bass with a light "pump" on the beat (simulated sidechain)
  const beatPos = (t % BEAT) / BEAT;
  const pump = t > tIn ? .55 + .45 * smooth(beatPos * 2.2) : 1;
  const root = xf > .5 ? nxt.root : cur.root;
  bassPh += hz(root) / SR;
  const bass = Math.sin(2 * Math.PI * bassPh) * .09 * pump * (t > tIn - 1 ? smooth((t - tIn + 1) / 2) : .35);
  padL *= (t > tIn ? .75 + .25 * pump : 1); padR *= (t > tIn ? .75 + .25 * pump : 1);
  // eighth-note arpeggio during the product section
  let arp = 0, pan = 0;
  if (t > tIn && t < tClose + 6) {
    const step = Math.floor(t / (BEAT / 2)), st = t - step * (BEAT / 2);
    const chord = CHORDS[Math.floor((step * BEAT / 2) / CH) % 4];
    const seq = [0, 2, 1, 3, 2, 1, 3, 2];
    const f = hz(chord.notes[seq[step % 8]] + 12);
    const env = Math.exp(-st / .16) * smooth(st / .004);
    arp = (Math.sin(2 * Math.PI * f * st) + .25 * Math.sin(4 * Math.PI * f * st)) * env * .045;
    pan = step % 2 ? .35 : -.35;
    const fadeArp = smooth((t - tIn) / 3) * (t > tClose ? 1 - smooth((t - tClose) / 6) : 1);
    arp *= fadeArp;
  }
  // soft shaker on the off-beats
  let hat = 0;
  if (t > tIn + 4 && t < tClose) {
    const off = ((t + BEAT / 2) % BEAT);
    if (off < .05) hat = rnd() * Math.exp(-off / .012) * .012;
  }
  L[i] = padL + bass + arp * (1 - pan) + hat;
  R[i] = padR + bass + arp * (1 + pan) + hat * .8;
}
// global fade-in and fade-out
for (let i = 0; i < N; i++) {
  const t = i / SR, g = smooth(t / 2.5) * (1 - smooth((t - (DUR - 3.5)) / 3.4));
  L[i] *= g; R[i] *= g;
}
writeWav(path.join(BUILD, "music.wav"), L, R);

/* ---------- effects ---------- */
const FL = new Float32Array(N), FR = new Float32Array(N);
function add(t0, len, fn, pan = 0) {
  const s0 = Math.floor(t0 * SR), n = Math.floor(len * SR);
  for (let j = 0; j < n && s0 + j < N; j++) { if (s0 + j < 0) continue; const v = fn(j / SR); FL[s0 + j] += v * (1 - pan); FR[s0 + j] += v * (1 + pan); }
}
for (const e of SFX) {
  const g = e.gain ?? 1;
  if (e.type === "click") {
    add(e.t, .05, x => (Math.sin(2 * Math.PI * 2100 * x) * Math.exp(-x / .006) * .22 + rnd() * Math.exp(-x / .002) * .12) * g);
  } else if (e.type === "pop") {
    add(e.t, .12, x => Math.sin(2 * Math.PI * (880 - 2200 * x) * x) * Math.exp(-x / .03) * smooth(x / .003) * .16 * g);
  } else if (e.type === "whoosh") {
    let y = 0;
    add(e.t, .7, x => { const c = .02 + .25 * Math.sin(Math.PI * x / .7); y += c * (rnd() - y); return y * Math.sin(Math.PI * x / .7) * .55 * g; });
  } else if (e.type === "boom") {
    add(e.t, 2.2, x => (Math.sin(2 * Math.PI * 52 * x) * .5 + Math.sin(2 * Math.PI * 104 * x) * .18) * Math.exp(-x / .55) * smooth(x / .01) * .55 * g);
  }
}
writeWav(path.join(BUILD, "sfx.wav"), FL, FR);
console.log(`music and effects: ${DUR}s · ${SFX.length} events`);
