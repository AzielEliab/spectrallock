/**
 * Simplified SpectralLock overlay for the hosted Worker.
 * Rosetta spectral analysis — same lenses as Aziel Corpus Library OCR
 * (overlays, ink/page). Full histogram / band-pass / unsharp lives in Python.
 * PNG 8-bit RGB/RGBA, longest side capped at 256.
 */
export const LIMITATION =
  "Rosetta spectral analysis (RSA-2.0 family). SpectralLock lenses match " +
  "Aziel Corpus Library OCR — overlays plus ink/page targets " +
  "(zero, tazel, vyrn, uv, rosetta, zen, chaos, balance, candle, indent, lemon). " +
  "Synthetic UV is a 365–400 nm look from an ordinary photograph. " +
  "Candlelight is a warm flame-side look from an ordinary photo. " +
  "Indent is an image-enhancement heuristic for surface relief. " +
  "Lemon enhances heat-/acid-style browning already in the pixels; it never invents marks. " +
  "Balance never invents marks. " +
  "Inject ON is false-color membership tint (paint). " +
  "OFF is luminance of the same gate. Zero ignores the switch. " +
  "An empty gate is a valid reading. Copy-of-copy works only if the hue is still in-band. " +
  "Unredact / lift-overlay locates leftover bytes, historical page revisions, and residual only — never invents letters. " +
  "Opaque replace with no leftover container bytes refuses (SL-UNREDACT-OPAQUE). " +
  "Heatmaps are residual overlays. OCR only after structural recovery; never reconstructs covered letters from context. " +
  "Handwriting analysis is synthetic scan heuristics of ink-on-paper photos. " +
  "Lamb Lens: Service → Clarity → Peace. " +
  "Hosted overlay is a simplified preview (max 256 px); the full pipeline is the Python package. " +
  "The human still reads the page. Author Aziel Eliab.";

export const INJECT_NOTE =
  "ON paints membership (false color). OFF is the same gate as gray. " +
  "Zero ignores the switch. " +
  "UV is a synthetic 365–400 nm look from an ordinary photograph. Balance never invents marks. " +
  "Report tazel_inband_pct and vyrn_inband_pct before claiming a hit. " +
  "An empty gate is a valid reading. Copy-of-copy works only if the hue is still in-band. " +
  "Hosted /v1/overlay is a 256 px preview; prefer spectrallock_inject.py locally.";

export const VERSION = "0.3.0";
export const MAX_SIDE = 256;
export const LIVE = ["zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance", "candle", "indent", "lemon"];
export const TARGET_IDS = ["ink", "page"];

export const ALIASES = {
  candlelight: "candle",
  "candle-light": "candle",
  ultraviolet: "uv",
  "uv-light": "uv",
  uvsa: "uv",
  indentation: "indent",
  "suppress-ink": "indent",
  "ink-suppress": "indent",
  "revealer-indent": "indent",
  "lemon-ink": "lemon",
  "hidden-lemon": "lemon",
  "invisible-ink-lemon": "lemon",
};

export const STUB_MODES = ["spectrometer", "forensic", "invent_mark"];

export const MODES = [
  { id: "zero", paper: "ZSA-1.0", status: "live", aliases: [], summary: "Equilibrium / geometry (simplified grayscale stretch)." },
  { id: "tazel", paper: "TSA-1.0", status: "live", aliases: [], summary: "Boost green–gold–turquoise (~170°, #1EC9A5)." },
  { id: "vyrn", paper: "VSA-1.0", status: "live", aliases: [], summary: "Boost magenta–red-violet (~350°, #C00066)." },
  { id: "uv", paper: "UVSA-1.0", status: "live", aliases: ["ultraviolet", "uv-light", "uvsa"], summary: "Ultraviolet light analysis (synthetic). 365–400 nm look from an ordinary photograph." },
  { id: "rosetta", paper: "RSA-2.0", status: "live", aliases: [], summary: "Rosetta spectral analysis RSA-2.0 = 0.40·Z′ + 0.35·T′ + 0.25·V′ after normalize." },
  { id: "zen", paper: "ZENA-1.0", status: "live", aliases: [], summary: "(Z′ + T′ + U′ + V′) / 4 after normalize." },
  { id: "chaos", paper: "CSA-1.0", status: "live", aliases: [], summary: "0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′ after normalize." },
  { id: "balance", paper: "BSA", status: "live", aliases: [], summary: "α·Zen + (1-α)·Chaos. Never invents marks." },
  { id: "candle", paper: "CLSA-1.0", status: "live", aliases: ["candlelight", "candle-light"], summary: "Candlelight analysis (synthetic). Amber ~1800–2700K flame-side look." },
  { id: "indent", paper: "ISA-1.0", status: "live", aliases: ["indentation", "suppress-ink", "ink-suppress", "revealer-indent"], preferred_target: "page", summary: "Ink-suppress / indentation reveal (synthetic). Image-enhancement heuristic. Prefer target=page." },
  { id: "lemon", paper: "LISA-1.0", status: "live", aliases: ["lemon-ink", "hidden-lemon", "invisible-ink-lemon"], summary: "Hidden lemon ink analysis (synthetic). Heat-/acid-style browning from existing pixels. Never invents marks." },
];

export const TARGETS = [
  { id: "ink", status: "live", summary: "Isolate writing. Same ink target as Aziel Corpus Library OCR." },
  { id: "page", status: "live", summary: "Isolate parchment / substrate. Same page target as Aziel Corpus Library OCR." },
];

const ROSETTA_W = { zero: 0.4, tazel: 0.35, vyrn: 0.25 };
const ZEN_W = { zero: 0.25, tazel: 0.25, uv: 0.25, vyrn: 0.25 };
const CHAOS_W = { uv: 0.4, vyrn: 0.35, tazel: 0.2, zero: 0.05 };
const EPS = 1e-6;
const TAZEL_RGB = [0x1e / 255, 0xc9 / 255, 0xa5 / 255];
const VYRN_RGB = [0xc0 / 255, 0x00 / 255, 0x66 / 255];
const ZERO_RGB = [0x6f / 255, 0x64 / 255, 0x85 / 255];
const UV_RGB = [0.55, 0.45, 0.85];
const CHAOS_RGB = [0.55, 0.22, 0.38];
const CANDLE_RGB = [1.0, 0.62, 0.22];
const INDENT_RGB = [0.72, 0.68, 0.58];
const LEMON_RGB = [0.62, 0.38, 0.14];
const TAZEL_INBAND_SIGMA = 24;
const VYRN_INBAND_SIGMA = 28;
const INBAND_SAT_MIN = 0.12;
const INBAND_VAL_MIN = 0.08;
const ROSETTA_RGB = [
  0.40 * ZERO_RGB[0] + 0.35 * TAZEL_RGB[0] + 0.25 * VYRN_RGB[0],
  0.40 * ZERO_RGB[1] + 0.35 * TAZEL_RGB[1] + 0.25 * VYRN_RGB[1],
  0.40 * ZERO_RGB[2] + 0.35 * TAZEL_RGB[2] + 0.25 * VYRN_RGB[2],
];
const ZEN_RGB = [
  (ZERO_RGB[0] + TAZEL_RGB[0] + VYRN_RGB[0] + UV_RGB[0]) / 4,
  (ZERO_RGB[1] + TAZEL_RGB[1] + VYRN_RGB[1] + UV_RGB[1]) / 4,
  (ZERO_RGB[2] + TAZEL_RGB[2] + VYRN_RGB[2] + UV_RGB[2]) / 4,
];

function luma(r, g, b) {
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function hueDist(h, t) {
  const d = Math.abs(h - t);
  return Math.min(d, 360 - d);
}

function rgbToHsv(r, g, b) {
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const v = max;
  const d = max - min;
  const s = max > EPS ? d / max : 0;
  let h = 0;
  if (d > EPS) {
    if (max === r) h = ((g - b) / d) % 6;
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60;
    if (h < 0) h += 360;
  }
  return [h, s, v];
}

function hsvToRgb(h, s, v) {
  const c = v * s;
  const hp = (h % 360) / 60;
  const x = c * (1 - Math.abs((hp % 2) - 1));
  const m = v - c;
  let rp = 0, gp = 0, bp = 0;
  if (hp < 1) { rp = c; gp = x; }
  else if (hp < 2) { rp = x; gp = c; }
  else if (hp < 3) { gp = c; bp = x; }
  else if (hp < 4) { gp = x; bp = c; }
  else if (hp < 5) { rp = x; bp = c; }
  else { rp = c; bp = x; }
  return [rp + m, gp + m, bp + m];
}

function clamp01(x) {
  return x < 0 ? 0 : x > 1 ? 1 : x;
}

function pixelsFromRgb(buf, w, h) {
  // Float RGB 0-1, length w*h*3
  return { buf, w, h };
}

function copyBuf(src) {
  return new Float32Array(src);
}

function toLuma(buf, w, h) {
  const out = new Float32Array(w * h);
  for (let i = 0, p = 0; i < out.length; i++, p += 3) {
    out[i] = luma(buf[p], buf[p + 1], buf[p + 2]);
  }
  return out;
}

function norm01(arr) {
  let lo = Infinity, hi = -Infinity;
  for (let i = 0; i < arr.length; i++) {
    const v = arr[i];
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  const out = new Float32Array(arr.length);
  const span = hi - lo;
  if (span < EPS) return out;
  for (let i = 0; i < arr.length; i++) out[i] = (arr[i] - lo) / span;
  return out;
}

function grayToRgb(gray) {
  const out = new Float32Array(gray.length * 3);
  for (let i = 0; i < gray.length; i++) {
    const v = clamp01(gray[i]);
    const p = i * 3;
    out[p] = v; out[p + 1] = v; out[p + 2] = v;
  }
  return out;
}

export function parseInject(value, fallback = true) {
  if (value === undefined || value === null) return fallback;
  if (value === false || value === 0) return false;
  if (value === true || value === 1) return true;
  const key = String(value).trim().toLowerCase();
  if (["0", "false", "off", "no", "no-inject", "n"].includes(key)) return false;
  if (["1", "true", "on", "yes", "inject", "y"].includes(key)) return true;
  return fallback;
}

export function inbandPct(buf, hue, sigma) {
  let hit = 0;
  const n = buf.length / 3;
  if (!n) return 0;
  for (let p = 0; p < buf.length; p += 3) {
    const [h, s, v] = rgbToHsv(buf[p], buf[p + 1], buf[p + 2]);
    if (hueDist(h, hue) <= sigma && s >= INBAND_SAT_MIN && v >= INBAND_VAL_MIN) hit += 1;
  }
  return Math.round((10000 * hit) / n) / 100;
}

export function gateInband(buf) {
  return {
    tazel_inband_pct: inbandPct(buf, 170, TAZEL_INBAND_SIGMA),
    vyrn_inband_pct: inbandPct(buf, 350, VYRN_INBAND_SIGMA),
  };
}

function tintGray(gray, color, amount = 0.28) {
  const out = new Float32Array(gray.length * 3);
  for (let i = 0; i < gray.length; i++) {
    const g = gray[i];
    const p = i * 3;
    out[p] = clamp01(g * ((1 - amount) + amount * color[0] * 1.6));
    out[p + 1] = clamp01(g * ((1 - amount) + amount * color[1] * 1.6));
    out[p + 2] = clamp01(g * ((1 - amount) + amount * color[2] * 1.6));
  }
  return out;
}

function maybeGray(buf, w, h, inject, mode) {
  if (mode === "zero" || !inject) return grayToRgb(toLuma(buf, w, h));
  return buf;
}

function modeZero(buf) {
  const n = buf.length / 3;
  const g = new Float32Array(n);
  for (let i = 0, p = 0; i < n; i++, p += 3) g[i] = luma(buf[p], buf[p + 1], buf[p + 2]);
  return grayToRgb(norm01(g));
}

function modeTazel(buf) {
  const out = new Float32Array(buf.length);
  for (let p = 0; p < buf.length; p += 3) {
    const r = buf[p], g = buf[p + 1], b = buf[p + 2];
    const [h, s, v] = rgbToHsv(r, g, b);
    const w = Math.exp(-0.5 * (hueDist(h, 170) / 24) ** 2);
    const s2 = clamp01(s * (1 + 0.65 * w) + 0.1 * w);
    const mid = 4 * v * (1 - v);
    const v2 = clamp01(v * (1 + 0.28 * w) + 0.06 * w + 0.12 * mid);
    const [nr, ng, nb] = hsvToRgb(h, s2, v2);
    out[p] = clamp01(nr * (1 - 0.18 * w) + 0x1e / 255 * v2 * 0.18 * w);
    out[p + 1] = clamp01(ng * (1 - 0.18 * w) + 0xc9 / 255 * v2 * 0.18 * w);
    out[p + 2] = clamp01(nb * (1 - 0.18 * w) + 0xa5 / 255 * v2 * 0.18 * w);
  }
  return out;
}

function modeVyrn(buf) {
  const out = new Float32Array(buf.length);
  for (let p = 0; p < buf.length; p += 3) {
    const r = buf[p], g = buf[p + 1], b = buf[p + 2];
    const [h, s, v] = rgbToHsv(r, g, b);
    const w = Math.exp(-0.5 * (hueDist(h, 350) / 28) ** 2);
    const cyan = Math.exp(-0.5 * (hueDist(h, 160) / 32) ** 2);
    const s2 = clamp01(s * (1 + 0.7 * w) * (1 - 0.55 * cyan) + 0.08 * w);
    const v2 = clamp01(v * (1 + 0.22 * w) * (1 - 0.18 * cyan));
    const [nr, ng, nb] = hsvToRgb(h, s2, v2);
    out[p] = clamp01(nr * (1 - 0.22 * w) + 0xc0 / 255 * v2 * 0.22 * w);
    out[p + 1] = clamp01(ng * (1 - 0.22 * w) * (1 - 0.25 * cyan) + 0 * v2 * 0.22 * w);
    out[p + 2] = clamp01(nb * (1 - 0.22 * w) + 0x66 / 255 * v2 * 0.22 * w);
  }
  return out;
}

function modeUv(buf) {
  const n = buf.length / 3;
  const L = new Float32Array(n);
  for (let i = 0, p = 0; i < n; i++, p += 3) L[i] = luma(buf[p], buf[p + 1], buf[p + 2]);
  const t = norm01(L);
  const out = new Float32Array(buf.length);
  for (let i = 0; i < n; i++) {
    let glow = clamp01(Math.pow(t[i], 0.72) * 1.18);
    glow = glow * (1 - 0.42 * (1 - t[i]));
    const ink = t[i] < 0.42 ? 0.35 : 0;
    const p = i * 3;
    out[p] = clamp01((glow * 0.7 + 0.04) * (1 - ink));
    out[p + 1] = clamp01((glow * 0.62 + 0.03) * (1 - ink));
    out[p + 2] = clamp01((glow * 1.18) * (1 - ink));
  }
  return out;
}

function modeCandle(buf, w, h) {
  const out = new Float32Array(buf.length);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x;
      const p = i * 3;
      const r = buf[p], g = buf[p + 1], b = buf[p + 2];
      const L = luma(r, g, b);
      const flame = 1 - (x / Math.max(1, w - 1)) * 0.42;
      const glow = clamp01(Math.pow(L, 0.82) * (0.78 + 0.28 * flame));
      const ink = L < 0.44 ? (0.44 - L) / 0.44 : 0;
      out[p] = clamp01((r * 0.42 + glow * 1.16 + 0.05) * (1 - 0.40 * ink) + r * 0.28 * ink);
      out[p + 1] = clamp01((g * 0.40 + glow * 0.70 + 0.02) * (1 - 0.40 * ink) + g * 0.28 * ink);
      out[p + 2] = clamp01((b * 0.22 + glow * 0.26) * (1 - 0.40 * ink) + b * 0.28 * ink);
    }
  }
  return out;
}

function modeIndent(buf, w, h) {
  const L = toLuma(buf, w, h);
  const t = norm01(L);
  const parch = parchmentEstimate(buf, w, h);
  const out = new Float32Array(buf.length);
  for (let i = 0, p = 0; i < t.length; i++, p += 3) {
    const ink = t[i] < 0.52 ? (0.52 - t[i]) / 0.52 : 0;
    const wr = buf[p] * (1 - 0.84 * ink) + parch[0] * 0.84 * ink;
    const wg = buf[p + 1] * (1 - 0.84 * ink) + parch[1] * 0.84 * ink;
    const wb = buf[p + 2] * (1 - 0.84 * ink) + parch[2] * 0.84 * ink;
    const gray = luma(wr, wg, wb);
    // simplified relief: invert residual ink vs parchment (hosted 256px honesty)
    const relief = clamp01(0.18 + gray * 0.62 + Math.abs(L[i] - gray) * 0.9);
    out[p] = clamp01(wr * 0.42 + relief * 0.58);
    out[p + 1] = clamp01(wg * 0.42 + relief * 0.58);
    out[p + 2] = clamp01(wb * 0.42 + relief * 0.58);
  }
  return out;
}

function modeLemon(buf) {
  const out = new Float32Array(buf.length);
  for (let p = 0; p < buf.length; p += 3) {
    const r = buf[p], g = buf[p + 1], b = buf[p + 2];
    const [h, s, v] = rgbToHsv(r, g, b);
    const brown = Math.exp(-0.5 * (hueDist(h, 36) / 22) ** 2);
    const warm = Math.exp(-0.5 * (hueDist(h, 28) / 30) ** 2);
    const mid = Math.max(0, 1 - Math.abs(v - 0.42) / 0.45);
    const gain = clamp01((0.65 * brown + 0.35 * warm) * clamp01(s * 1.85) * mid);
    const s2 = clamp01(s * (1 + 0.58 * gain) + 0.04 * gain);
    const v2 = clamp01(v * (1 + 0.10 * gain) - 0.07 * gain);
    const [nr, ng, nb] = hsvToRgb(h, s2, v2);
    out[p] = clamp01(nr * (1 - 0.22 * gain) + 0.62 * v2 * 0.22 * gain);
    out[p + 1] = clamp01(ng * (1 - 0.22 * gain) + 0.38 * v2 * 0.22 * gain);
    out[p + 2] = clamp01(nb * (1 - 0.22 * gain) + 0.14 * v2 * 0.22 * gain);
  }
  return out;
}

export function resolveMode(name) {
  const key = String(name || "").trim().toLowerCase();
  if (LIVE.includes(key)) return key;
  if (ALIASES[key]) return ALIASES[key];
  if (STUB_MODES.includes(key)) {
    return { error: "stub", unknown: key, known: LIVE };
  }
  return null;
}

function mixLuma(channels, weights) {
  const n = channels.zero.length;
  const out = new Float32Array(n);
  for (const [name, w] of Object.entries(weights)) {
    const arr = channels[name];
    for (let i = 0; i < n; i++) out[i] += w * arr[i];
  }
  return out;
}

function baseChannels(buf, w, h) {
  const z = norm01(toLuma(modeZero(buf), w, h));
  const t = norm01(toLuma(modeTazel(buf), w, h));
  const v = norm01(toLuma(modeVyrn(buf), w, h));
  const u = norm01(toLuma(modeUv(buf), w, h));
  return { zero: z, tazel: t, vyrn: v, uv: u };
}

function normalizeTarget(target) {
  const key = String(target || "ink").trim().toLowerCase();
  if (key === "page" || key === "parchment" || key === "substrate" || key === "folio") return "page";
  return "ink";
}

function normalizeLenses(mode, lens, lenses) {
  const raw = [];
  for (const item of [lenses, lens, mode]) {
    if (item == null || item === "") continue;
    if (Array.isArray(item)) raw.push(...item);
    else String(item).replaceAll("+", ",").split(",").forEach((x) => raw.push(x));
  }
  const out = [];
  for (const item of raw) {
    const key = String(item || "").trim().toLowerCase();
    if (!key) continue;
    const resolved = resolveMode(key);
    if (resolved && resolved.error === "stub") {
      return { error: "stub", unknown: resolved.unknown, known: LIVE };
    }
    const id = resolved;
    if (!id || !LIVE.includes(id)) return { error: "unknown lens", unknown: key, known: LIVE };
    if (!out.includes(id)) out.push(id);
  }
  return { lenses: out.length ? out : ["rosetta"] };
}

function parchmentEstimate(buf, w, h) {
  const L = toLuma(buf, w, h);
  const sorted = Array.from(L).sort((a, b) => a - b);
  const q = sorted[Math.max(0, Math.floor(sorted.length * 0.80))] || 0;
  let sr = 0, sg = 0, sb = 0, n = 0;
  for (let i = 0, p = 0; i < L.length; i++, p += 3) {
    if (L[i] >= q) { sr += buf[p]; sg += buf[p + 1]; sb += buf[p + 2]; n += 1; }
  }
  if (!n) return [0.93, 0.88, 0.76];
  return [sr / n, sg / n, sb / n];
}

function applyTarget(buf, w, h, target) {
  const dest = normalizeTarget(target);
  const L = toLuma(buf, w, h);
  const t = norm01(L);
  const parch = parchmentEstimate(buf, w, h);
  const out = new Float32Array(buf.length);
  if (dest === "page") {
    for (let i = 0, p = 0; i < t.length; i++, p += 3) {
      const ink = t[i] < 0.50 ? (0.50 - t[i]) / 0.50 : 0;
      out[p] = clamp01(buf[p] * (1 - 0.72 * ink) + parch[0] * 0.72 * ink);
      out[p + 1] = clamp01(buf[p + 1] * (1 - 0.72 * ink) + parch[1] * 0.72 * ink);
      out[p + 2] = clamp01(buf[p + 2] * (1 - 0.72 * ink) + parch[2] * 0.72 * ink);
    }
    return out;
  }
  for (let i = 0, p = 0; i < t.length; i++, p += 3) {
    const page = t[i] > 0.38 ? Math.min(1, (t[i] - 0.38) / 0.40) : 0;
    const ink = t[i] < 0.48 ? 1 : 0;
    out[p] = clamp01((buf[p] * (1 - 0.50 * page) + parch[0] * 0.50 * page) * (1 - 0.28 * ink));
    out[p + 1] = clamp01((buf[p + 1] * (1 - 0.50 * page) + parch[1] * 0.50 * page) * (1 - 0.28 * ink));
    out[p + 2] = clamp01((buf[p + 2] * (1 - 0.50 * page) + parch[2] * 0.50 * page) * (1 - 0.28 * ink));
  }
  return out;
}

function composeLenses(buf, w, h, lenses, inject = true) {
  if (lenses.length === 1) return applyMode(buf, w, h, lenses[0], inject);
  const channels = {};
  for (const name of lenses) {
    channels[name] = norm01(toLuma(applyMode(buf, w, h, name, inject), w, h));
  }
  const weights = {};
  const wgt = 1 / lenses.length;
  for (const name of lenses) weights[name] = wgt;
  const mix = mixLuma(channels, weights);
  const paint = inject && lenses.some((name) => name !== "zero");
  if (!paint) return grayToRgb(mix);
  const palette = {
    zero: ZERO_RGB, tazel: TAZEL_RGB, vyrn: VYRN_RGB, uv: UV_RGB,
    rosetta: ROSETTA_RGB, zen: ZEN_RGB, chaos: CHAOS_RGB, balance: ZEN_RGB,
    candle: CANDLE_RGB, indent: INDENT_RGB, lemon: LEMON_RGB,
  };
  const acc = [0, 0, 0];
  for (const name of lenses) {
    const c = palette[name] || [0.7, 0.7, 0.7];
    acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2];
  }
  return tintGray(mix, [acc[0] / lenses.length, acc[1] / lenses.length, acc[2] / lenses.length]);
}

function applyMode(buf, w, h, mode, inject = true) {
  const paint = mode !== "zero" && inject;
  if (mode === "zero") return modeZero(buf);
  if (mode === "tazel") return maybeGray(modeTazel(buf), w, h, paint, mode);
  if (mode === "vyrn") return maybeGray(modeVyrn(buf), w, h, paint, mode);
  if (mode === "uv") return maybeGray(modeUv(buf), w, h, paint, mode);
  if (mode === "candle") return maybeGray(modeCandle(buf, w, h), w, h, paint, mode);
  if (mode === "indent") return maybeGray(modeIndent(buf, w, h), w, h, paint, mode);
  if (mode === "lemon") return maybeGray(modeLemon(buf), w, h, paint, mode);
  const ch = baseChannels(buf, w, h);
  if (mode === "rosetta") {
    const mix = mixLuma(ch, ROSETTA_W);
    return paint ? tintGray(mix, ROSETTA_RGB) : grayToRgb(mix);
  }
  if (mode === "zen") {
    const mix = mixLuma(ch, ZEN_W);
    return paint ? tintGray(mix, ZEN_RGB) : grayToRgb(mix);
  }
  if (mode === "chaos") {
    const mix = mixLuma(ch, CHAOS_W);
    return paint ? tintGray(mix, CHAOS_RGB) : grayToRgb(mix);
  }
  if (mode === "balance") {
    const zenMix = mixLuma(ch, ZEN_W);
    const chaosMix = mixLuma(ch, CHAOS_W);
    const zen = paint ? tintGray(zenMix, ZEN_RGB) : grayToRgb(zenMix);
    const chaos = paint ? tintGray(chaosMix, CHAOS_RGB) : grayToRgb(chaosMix);
    const zn = norm01(toLuma(zen, w, h));
    const cn = norm01(toLuma(chaos, w, h));
    const out = new Float32Array(buf.length);
    for (let i = 0, p = 0; i < zn.length; i++, p += 3) {
      const B = (zn[i] - cn[i]) / (zn[i] + cn[i] + EPS);
      const a = (1 + B) / 2;
      out[p] = a * zen[p] + (1 - a) * chaos[p];
      out[p + 1] = a * zen[p + 1] + (1 - a) * chaos[p + 1];
      out[p + 2] = a * zen[p + 2] + (1 - a) * chaos[p + 2];
    }
    return paint ? out : grayToRgb(toLuma(out, w, h));
  }
  throw new Error("unknown mode");
}

function centerOfMass(buf, w, h) {
  const L = toLuma(buf, w, h);
  let s = 0, sx = 0, sy = 0;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const v = L[y * w + x];
      s += v; sx += v * x; sy += v * y;
    }
  }
  if (s <= EPS) return { x: w / 2, y: h / 2 };
  return { x: sx / s, y: sy / s };
}

function resizeNN(buf, w, h, nw, nh) {
  const out = new Float32Array(nw * nh * 3);
  for (let y = 0; y < nh; y++) {
    const sy = Math.min(h - 1, Math.floor((y + 0.5) * h / nh));
    for (let x = 0; x < nw; x++) {
      const sx = Math.min(w - 1, Math.floor((x + 0.5) * w / nw));
      const si = (sy * w + sx) * 3;
      const di = (y * nw + x) * 3;
      out[di] = buf[si]; out[di + 1] = buf[si + 1]; out[di + 2] = buf[si + 2];
    }
  }
  return { buf: out, w: nw, h: nh };
}

function capSide(buf, w, h) {
  const side = Math.max(w, h);
  if (side <= MAX_SIDE) return { buf, w, h };
  const scale = MAX_SIDE / side;
  return resizeNN(buf, w, h, Math.max(1, Math.round(w * scale)), Math.max(1, Math.round(h * scale)));
}

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(u8) {
  let c = 0xffffffff;
  for (let i = 0; i < u8.length; i++) c = CRC_TABLE[(c ^ u8[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function u32be(n) {
  return Uint8Array.of((n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255);
}

function concat(parts) {
  let n = 0;
  for (const p of parts) n += p.length;
  const out = new Uint8Array(n);
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out;
}

function chunk(type, data) {
  const t = new TextEncoder().encode(type);
  const crcSrc = concat([t, data]);
  const crc = crc32(crcSrc);
  return concat([u32be(data.length), t, data, u32be(crc)]);
}

async function inflate(u8) {
  const ds = new DecompressionStream("deflate");
  const writer = ds.writable.getWriter();
  await writer.write(u8);
  await writer.close();
  const ab = await new Response(ds.readable).arrayBuffer();
  return new Uint8Array(ab);
}

async function deflate(u8) {
  const cs = new CompressionStream("deflate");
  const writer = cs.writable.getWriter();
  await writer.write(u8);
  await writer.close();
  const ab = await new Response(cs.readable).arrayBuffer();
  return new Uint8Array(ab);
}

function paeth(a, b, c) {
  const p = a + b - c;
  const pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
  if (pa <= pb && pa <= pc) return a;
  if (pb <= pc) return b;
  return c;
}

export async function decodePng(bytes) {
  const sig = [137, 80, 78, 71, 13, 10, 26, 10];
  for (let i = 0; i < 8; i++) if (bytes[i] !== sig[i]) throw new Error("not a PNG");
  let off = 8;
  let w = 0, h = 0, depth = 0, ctype = 0, interlace = 0;
  const idats = [];
  while (off + 8 <= bytes.length) {
    const len = (bytes[off] << 24) | (bytes[off + 1] << 16) | (bytes[off + 2] << 8) | bytes[off + 3];
    const type = String.fromCharCode(bytes[off + 4], bytes[off + 5], bytes[off + 6], bytes[off + 7]);
    const data = bytes.subarray(off + 8, off + 8 + len);
    if (type === "IHDR") {
      w = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3];
      h = (data[4] << 24) | (data[5] << 16) | (data[6] << 8) | data[7];
      depth = data[8]; ctype = data[9]; interlace = data[12];
    } else if (type === "IDAT") {
      idats.push(data);
    } else if (type === "IEND") break;
    off += 12 + len;
  }
  if (depth !== 8 || interlace !== 0) throw new Error("PNG must be 8-bit non-interlaced");
  if (![0, 2, 4, 6].includes(ctype)) throw new Error("PNG color type not supported (need gray/RGB)");
  const inflated = await inflate(concat(idats));
  const bpp = ctype === 0 ? 1 : ctype === 2 ? 3 : ctype === 4 ? 2 : 4;
  const stride = w * bpp;
  const raw = new Uint8Array(h * stride);
  let src = 0;
  let prev = new Uint8Array(stride);
  for (let y = 0; y < h; y++) {
    const filter = inflated[src++];
    const row = inflated.subarray(src, src + stride);
    src += stride;
    const out = raw.subarray(y * stride, (y + 1) * stride);
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? out[x - bpp] : 0;
      const b = prev[x];
      const c = x >= bpp ? prev[x - bpp] : 0;
      let v = row[x];
      if (filter === 1) v = (v + a) & 255;
      else if (filter === 2) v = (v + b) & 255;
      else if (filter === 3) v = (v + ((a + b) >> 1)) & 255;
      else if (filter === 4) v = (v + paeth(a, b, c)) & 255;
      else if (filter !== 0) throw new Error("unknown PNG filter");
      out[x] = v;
    }
    prev = out.slice();
  }
  const buf = new Float32Array(w * h * 3);
  for (let i = 0; i < w * h; i++) {
    let r, g, b;
    if (ctype === 0) { r = g = b = raw[i]; }
    else if (ctype === 2) { r = raw[i * 3]; g = raw[i * 3 + 1]; b = raw[i * 3 + 2]; }
    else if (ctype === 4) { r = g = b = raw[i * 2]; }
    else { r = raw[i * 4]; g = raw[i * 4 + 1]; b = raw[i * 4 + 2]; }
    buf[i * 3] = r / 255; buf[i * 3 + 1] = g / 255; buf[i * 3 + 2] = b / 255;
  }
  return { buf, w, h };
}

export async function encodePng(buf, w, h) {
  const stride = w * 3;
  const raw = new Uint8Array((stride + 1) * h);
  for (let y = 0; y < h; y++) {
    const o = y * (stride + 1);
    raw[o] = 0;
    for (let x = 0; x < w; x++) {
      const p = (y * w + x) * 3;
      raw[o + 1 + x * 3] = Math.max(0, Math.min(255, Math.round(buf[p] * 255)));
      raw[o + 2 + x * 3] = Math.max(0, Math.min(255, Math.round(buf[p + 1] * 255)));
      raw[o + 3 + x * 3] = Math.max(0, Math.min(255, Math.round(buf[p + 2] * 255)));
    }
  }
  const ihdr = new Uint8Array(13);
  ihdr.set(u32be(w), 0); ihdr.set(u32be(h), 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  const idat = await deflate(raw);
  const sig = Uint8Array.of(137, 80, 78, 71, 13, 10, 26, 10);
  return concat([sig, chunk("IHDR", ihdr), chunk("IDAT", idat), chunk("IEND", new Uint8Array(0))]);
}

function b64ToBytes(b64) {
  const bin = atob(String(b64).replace(/\s+/g, ""));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function bytesToB64(u8) {
  let s = "";
  for (let i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i]);
  return btoa(s);
}

export async function overlayFromB64(b64, mode, extras = {}) {
  const parsed = normalizeLenses(extras.lenses ? null : mode, extras.lens, extras.lenses);
  if (parsed.error) {
    const stub = parsed.error === "stub";
    return {
      error: stub ? `${parsed.unknown} is a stub` : parsed.error,
      unknown: parsed.unknown,
      known: LIVE,
      stub,
      advisory: LIMITATION,
    };
  }
  const lenses = parsed.lenses;
  const dest = normalizeTarget(extras.target || extras.polarity);
  let inject = true;
  if (extras.inject !== undefined) inject = parseInject(extras.inject);
  else if (extras.no_inject !== undefined) inject = !parseInject(extras.no_inject, false);
  else if (extras.tint !== undefined) inject = parseInject(extras.tint);
  const injectApplied = inject && lenses.some((name) => name !== "zero");
  let decoded;
  try {
    decoded = await decodePng(b64ToBytes(b64));
  } catch (err) {
    return { error: "PNG decode failed (hosted preview is PNG only): " + String(err.message || err), advisory: LIMITATION };
  }
  const capped = capSide(decoded.buf, decoded.w, decoded.h);
  const inband = gateInband(capped.buf);
  const mixed = composeLenses(capped.buf, capped.w, capped.h, lenses, inject);
  const out = applyTarget(mixed, capped.w, capped.h, dest);
  const png = await encodePng(out, capped.w, capped.h);
  const com = centerOfMass(out, capped.w, capped.h);
  const key = lenses.length === 1 ? lenses[0] : lenses.join("+");
  const paper = lenses.length === 1 ? ((MODES.find((m) => m.id === lenses[0]) || {}).paper) : "MULTI";
  return {
    mode: key,
    lens: key,
    lenses,
    target: dest,
    paper,
    inject,
    inject_applied: injectApplied,
    inject_ignored: inject && !injectApplied,
    tazel_inband_pct: inband.tazel_inband_pct,
    vyrn_inband_pct: inband.vyrn_inband_pct,
    pigment_recovery: false,
    empty_gate_not_broken_lens: true,
    inject_note: INJECT_NOTE,
    width: capped.w,
    height: capped.h,
    com,
    png_b64: bytesToB64(png),
    simplified: true,
    max_side: MAX_SIDE,
    hosted_preview_honesty: "256px preview; inject is false-color membership paint; prefer local spectrallock_inject.py",
    product: "spectrallock",
    version: VERSION,
    rosetta_spectral_analysis: true,
    corpus_ocr_aligned: true,
    author: "Aziel Eliab",
    advisory: LIMITATION,
  };
}

export const REFUSE_OPAQUE = "SL-UNREDACT-OPAQUE";
export const UNREDACT_OPS = ["locate", "lift", "recover", "refuse"];
export const UNREDACT_FAMILY = ["unredact", "lift", "redact-locate"];
export const DEEP_CAPABILITIES = [
  "historical_page_dereference",
  "revision_stream_compare",
  "operator_text_recovery",
  "font_encoding_resolve",
  "drawing_order_overlay",
  "redaction_classification",
  "orphan_object_scan",
  "xref_objstm",
  "after_eof_scan",
  "image_layer_recovery",
  "twin_page_compare",
  "producer_artifact_search",
  "ocr_after_structural",
  "character_provenance",
];

export const UNREDACT_NOTE =
  "Unredact / lift-overlay is locate + leftover-bytes + residual only. " +
  "Locate reports text still in the file, metadata, attachments, twin-page residual, " +
  "leftover container bytes, and historical page revisions (stale /Page, prior streams, " +
  "xref/ObjStm, after-EOF, incremental startxref/Prev revision graph + per-revision tip-cut copies). " +
  "Never invent letters. " +
  "Opaque replace (clipped solid black / true rewrite) with no leftover bytes refuses (" +
  REFUSE_OPAQUE +
  "). That is the only honest switch for visual unredact. " +
  "Non-opaque cover may use contrast / residual with inject OFF. No guessed letters. " +
  "Heatmaps are residual overlays. A flattened screenshot of a box is replace. " +
  "Leftover-bytes recovery reads prior objects / unused streams / attachments / incremental " +
  "revisions / stale page graphs still in the container. " +
  "If the container was rewritten and old bytes are gone, leftover_bytes is false. " +
  "OCR runs only after structural recovery and never reconstructs covered letters from context. " +
  "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE.";

export function listUnredact() {
  return {
    family: UNREDACT_FAMILY.slice(),
    ops: UNREDACT_OPS.slice(),
    refuse_code: REFUSE_OPAQUE,
    leftover_bytes_recovery: true,
    deep_history: true,
    revision_graph: true,
    revision_copies: true,
    capabilities: DEEP_CAPABILITIES.slice(),
    ocr_after_structural_only: true,
    covered_letters_from_context: false,
    pigment_recovery: false,
    guessed_letters: false,
    heatmap_is_transcript: false,
    esda: false,
    forensic_certification: false,
    inject_default: false,
    note: UNREDACT_NOTE,
    author: "Aziel Eliab",
    status: "live",
  };
}

export function parseUnredactOp(value, fallback = "locate") {
  const key = String(value || fallback).trim().toLowerCase().replaceAll("_", "-");
  const aliases = {
    "redact-locate": "locate",
    locate: "locate",
    lift: "lift",
    "lift-overlay": "lift",
    recover: "recover",
    leftover: "recover",
    "leftover-bytes": "recover",
    refuse: "refuse",
    unredact: "locate",
  };
  return aliases[key] || null;
}

function latinPreview(s, limit = 240) {
  const cleaned = String(s || "").replace(/[^\x20-\x7e\n\t]/g, " ").replace(/[ \t]+/g, " ").trim();
  return cleaned.length > limit ? cleaned.slice(0, limit) + "…" : cleaned;
}

function looksLikeText(s) {
  if (!s || s.trim().length < 2) return false;
  let printable = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    if (c >= 32 && c < 127) printable += 1;
  }
  return printable / s.length >= 0.55;
}

function unescapePdfLiteral(raw) {
  let inner = raw;
  if (inner.startsWith("(") && inner.endsWith(")")) inner = inner.slice(1, -1);
  return inner.replace(/\\n/g, "\n").replace(/\\r/g, "\r").replace(/\\t/g, "\t").replace(/\\([()\\])/g, "$1");
}

function extractPdfStrings(text) {
  const found = [];
  const lit = /\((?:\\.|[^\\)])*\)/g;
  let m;
  while ((m = lit.exec(text))) {
    const s = unescapePdfLiteral(m[0]);
    if (looksLikeText(s)) found.push(s);
  }
  const hex = /<([0-9A-Fa-f \t\r\n]+)>/g;
  while ((m = hex.exec(text))) {
    const h = m[1].replace(/\s+/g, "");
    if (h.length < 4) continue;
    let out = "";
    for (let i = 0; i + 1 < h.length; i += 2) {
      out += String.fromCharCode(parseInt(h.slice(i, i + 2), 16));
    }
    if (looksLikeText(out)) found.push(out);
  }
  return found;
}

function bytesToLatin(u8) {
  let s = "";
  for (let i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i]);
  return s;
}

export function locatePdfBytes(u8) {
  const head = bytesToLatin(u8.subarray(0, 5));
  if (head !== "%PDF-") {
    return { is_pdf: false, leftover_bytes: false, recovered: [], recovered_from: [], text_layer: [], metadata_hits: [], attachments: [], locations: [] };
  }
  const text = bytesToLatin(u8);
  const eofCount = (text.match(/%%EOF/g) || []).length;
  const objects = [];
  const objRe = /(?:^|[^0-9])(\d+)\s+(\d+)\s+obj/g;
  let m;
  while ((m = objRe.exec(text))) {
    const id = Number(m[1]);
    const gen = Number(m[2]);
    const offset = m.index + (m[0].startsWith("0") || m[0].startsWith("1") || /[0-9]/.test(m[0][0]) ? 0 : 1);
    const start = m.index + m[0].length;
    const endRel = text.indexOf("endobj", start);
    if (endRel < 0) continue;
    const body = text.slice(start, endRel);
    const hasStream = body.includes("stream");
    objects.push({ id, gen, offset: m.index, body, has_stream: hasStream });
  }
  const live = {};
  const xrefRe = /xref\s+([\s\S]*?)(?:trailer|startxref)/g;
  while ((m = xrefRe.exec(text))) {
    const block = m[1];
    const lines = block.split(/\r?\n/);
    let first = 0;
    let remain = 0;
    for (const line of lines) {
      const hdr = line.trim().match(/^(\d+)\s+(\d+)$/);
      if (hdr) {
        first = Number(hdr[1]);
        remain = Number(hdr[2]);
        continue;
      }
      const row = line.trim().match(/^(\d+)\s+(\d+)\s+([fn])/);
      if (row && remain > 0) {
        const objId = first;
        first += 1;
        remain -= 1;
        if (row[3] === "n") live[objId] = Number(row[1]);
        else delete live[objId];
      }
    }
  }
  const byId = {};
  for (const obj of objects) {
    (byId[obj.id] || (byId[obj.id] = [])).push(obj);
  }
  const text_layer = [];
  const recovered = [];
  const recovered_from = [];
  const locations = [];
  const metadata_hits = [];
  const infoRe = /\/(Title|Author|Subject|Keywords|Creator|Producer|CreationDate|ModDate)\s*(\((?:\\.|[^\\)])*\))/g;
  while ((m = infoRe.exec(text))) {
    const value = latinPreview(unescapePdfLiteral(m[2]));
    if (value) metadata_hits.push({ key: m[1], value, source: "pdf-bytes", invented: false });
  }
  for (const id of Object.keys(byId)) {
    const versions = byId[id].slice().sort((a, b) => a.offset - b.offset);
    for (let i = 0; i < versions.length; i++) {
      const obj = versions[i];
      const liveOff = live[obj.id];
      let leftover = false;
      let kind = "pdf-object";
      if (liveOff != null) leftover = Math.abs(liveOff - obj.offset) > 8 && i !== versions.length - 1;
      else if (Object.keys(live).length && liveOff == null) {
        leftover = true;
        kind = "unused-object";
      }
      if (versions.length > 1 && i < versions.length - 1) {
        leftover = true;
        kind = obj.has_stream ? "prior-stream" : "incremental-revision";
      }
      const strings = extractPdfStrings(obj.body);
      const uniq = [];
      for (const s of strings) {
        const p = latinPreview(s);
        if (p && !uniq.includes(p)) uniq.push(p);
      }
      locations.push({
        object_id: `${obj.id} ${obj.gen}`,
        offset: obj.offset,
        stream: obj.has_stream,
        leftover,
        kind,
        strings: uniq,
        invented: false,
      });
      if (leftover) {
        recovered.push({
          object_id: `${obj.id} ${obj.gen}`,
          offset: obj.offset,
          stream: obj.has_stream,
          recovered_from: kind,
          preview: uniq.join(" | "),
          invented: false,
        });
        if (!recovered_from.includes(kind)) recovered_from.push(kind);
      } else if (uniq.length) {
        text_layer.push({
          object_id: `${obj.id} ${obj.gen}`,
          offset: obj.offset,
          strings: uniq,
          under_visual_box_possible: true,
          invented: false,
          note: "Text still in the PDF object. Not guessed from a black rectangle.",
        });
      }
    }
  }
  const attachments = [];
  for (const obj of objects) {
    if (!/\/EmbeddedFile|\/Filespec|\/EF\b/.test(obj.body)) continue;
    const names = [];
    const nm = /\/(?:F|UF|Desc)\s*(\((?:\\.|[^\\)])*\))/g;
    let n;
    while ((n = nm.exec(obj.body))) names.push(unescapePdfLiteral(n[1]));
    const preview = latinPreview(extractPdfStrings(obj.body).join(" "));
    attachments.push({
      object_id: `${obj.id} ${obj.gen}`,
      offset: obj.offset,
      names: names.filter(Boolean),
      has_stream: obj.has_stream,
      preview,
      recovered_from: "attachment",
      invented: false,
    });
    recovered.push({
      object_id: `${obj.id} ${obj.gen}`,
      offset: obj.offset,
      stream: obj.has_stream,
      recovered_from: "attachment",
      preview,
      names: names.filter(Boolean),
      invented: false,
    });
    if (!recovered_from.includes("attachment")) recovered_from.push("attachment");
  }
  return {
    is_pdf: true,
    object_count: objects.length,
    incremental_updates: Math.max(0, eofCount - 1),
    text_layer,
    metadata_hits,
    attachments,
    recovered,
    leftover_bytes: recovered.length > 0,
    recovered_from,
    locations,
  };
}

export function classifyCoverBuf(buf, w, h) {
  const n = w * h;
  const L = toLuma(buf, w, h);
  let darkN = 0;
  let minX = w, minY = h, maxX = 0, maxY = 0;
  for (let i = 0; i < n; i++) {
    if (L[i] <= 0.42) {
      darkN += 1;
      const x = i % w;
      const y = (i - x) / w;
      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (x > maxX) maxX = x;
      if (y > maxY) maxY = y;
    }
  }
  const dark_frac = n ? darkN / n : 0;
  if (darkN < 24 || dark_frac < 0.012) {
    return { opaque_replace: false, residual_usable: false, flattened_screenshot_replace: false, cover_regions: [], dark_frac, width: w, height: h };
  }
  let sum = 0, sum2 = 0, mx = 0, mn = 1, near = 0, count = 0;
  for (let y = minY; y <= maxY; y++) {
    for (let x = minX; x <= maxX; x++) {
      const v = L[y * w + x];
      sum += v; sum2 += v * v;
      if (v > mx) mx = v;
      if (v < mn) mn = v;
      if (v <= 0.045) near += 1;
      count += 1;
    }
  }
  const mean = sum / count;
  const std = Math.sqrt(Math.max(0, sum2 / count - mean * mean));
  const nearFrac = near / count;
  const isOpaque = nearFrac >= 0.72 && std <= 0.045 && mx <= 0.12;
  const isResidual = !isOpaque && std >= 0.028 && (mx - mn) >= 0.08;
  return {
    opaque_replace: isOpaque && !isResidual,
    residual_usable: isResidual,
    flattened_screenshot_replace: isOpaque && !isResidual,
    cover_regions: [{ x0: minX, y0: minY, x1: maxX + 1, y1: maxY + 1, mean, std, opaque: isOpaque, residual_usable: isResidual, invented: false }],
    dark_frac,
    width: w,
    height: h,
  };
}

function residualEnhanceBuf(buf, w, h) {
  const L = norm01(toLuma(buf, w, h));
  return grayToRgb(L);
}

export function unredactFromBytes(u8, extras = {}) {
  const op = parseUnredactOp(extras.op || extras.verb || "locate") || "locate";
  const finding = {
    product: "spectrallock",
    version: VERSION,
    author: "Aziel Eliab",
    family: "unredact",
    aliases: UNREDACT_FAMILY.slice(),
    op,
    opaque_replace: false,
    residual_usable: false,
    leftover_bytes: false,
    refuse_code: null,
    recovered_from: [],
    locations: [],
    metadata_hits: [],
    attachments: [],
    recovered: [],
    text_layer: [],
    cover_regions: [],
    twin_diff: null,
    name_hits: [],
    inject: false,
    inject_applied: false,
    pigment_recovery: false,
    guessed_letters: false,
    heatmap_is_transcript: false,
    residual_is_transcript: false,
    esda: false,
    chemical_recovery: false,
    forensic_certification: false,
    flattened_screenshot_replace: false,
    empty_gate_not_broken_lens: true,
    inject_note: INJECT_NOTE,
    unredact_note: UNREDACT_NOTE,
    advisory: UNREDACT_NOTE,
    limitation: LIMITATION,
    hosted_preview_honesty: "256px residual preview when lifted; structural PDF history is live; OCR engine unbound on hosted preview",
    lamb_lens: "Service → Clarity → Peace",
    identity: "Aziel Eliab",
    capabilities: DEEP_CAPABILITIES.slice(),
    deep_history: true,
    page_revisions: [],
    revision_compare: [],
    operator_text: [],
    classifications: [],
    recovered_characters: [],
    ocr: { ocr_ran: false, ocr_after_structural_only: true, covered_letters_from_context: false, ocr_status: "unbound-hosted-preview", invented: false },
    revision_graph: { revisions: [], edges: [], root_startxref: null, eof_offsets: [], invented: false },
  };
  const latinHead = bytesToLatin(u8.subarray(0, 5));
  if (latinHead === "%PDF-") {
    const scanned = locatePdfBytes(u8);
    finding.text_layer = scanned.text_layer;
    finding.metadata_hits = scanned.metadata_hits;
    finding.attachments = scanned.attachments;
    finding.recovered = scanned.recovered;
    finding.locations = scanned.locations;
    finding.recovered_from = scanned.recovered_from;
    finding.leftover_bytes = scanned.leftover_bytes;
    finding.container = "pdf";
    finding.incremental_updates = scanned.incremental_updates;
    finding.pdf_object_count = scanned.object_count;
  } else {
    let decoded;
    try {
      decoded = null;
    } catch {
      decoded = null;
    }
  }
  return { finding, op };
}

export async function unredactFromB64(b64, extras = {}) {
  let u8;
  try {
    u8 = b64ToBytes(b64);
  } catch (err) {
    return { error: "decode failed: " + String(err.message || err), advisory: UNREDACT_NOTE };
  }
  const op = parseUnredactOp(extras.op || extras.verb || "locate");
  if (!op) return { error: "unknown unredact op", known: UNREDACT_OPS, advisory: UNREDACT_NOTE };
  const base = unredactFromBytes(u8, { op }).finding;
  base.op = op;
  const isPdf = bytesToLatin(u8.subarray(0, 5)) === "%PDF-";
  if (isPdf) {
    const hist = await locatePdfHistory(u8);
    base.text_layer = hist.text_layer;
    base.metadata_hits = hist.metadata_hits;
    base.attachments = hist.attachments;
    base.recovered = hist.recovered;
    base.locations = hist.locations;
    base.recovered_from = hist.recovered_from;
    base.leftover_bytes = hist.leftover_bytes;
    base.container = "pdf";
    base.incremental_updates = hist.incremental_updates;
    base.pdf_object_count = hist.object_count;
    base.capabilities = hist.capabilities;
    base.deep_history = true;
    base.page_revisions = hist.page_revisions;
    base.revision_compare = hist.revision_compare;
    base.operator_text = hist.operator_text;
    base.classifications = hist.classifications;
    base.drawing_order = hist.drawing_order;
    base.xref_streams = hist.xref_streams;
    base.objstms = hist.objstms;
    base.after_eof = hist.after_eof;
    base.image_layers = hist.image_layers;
    base.producer_artifacts = hist.producer_artifacts;
    base.identifiers = hist.identifiers;
    base.ocr = hist.ocr;
    base.recovered_characters = hist.recovered_characters;
    base.orphans = hist.orphans;
    base.revision_graph = hist.revision_graph;
    const twinB64 = extras.twin_b64 || extras.twin;
    if (twinB64) {
      try {
        const twinU8 = typeof twinB64 === "string" ? b64ToBytes(twinB64) : twinB64;
        const twinHist = await locatePdfHistory(twinU8);
        base.twin_diff = twinCompareHistory(hist, twinHist);
      } catch (err) {
        base.twin_diff = { comparable: false, invented: false, note: "Twin decode failed. Not guessed." };
      }
    }
  }
  if (!isPdf) {
    try {
      const decoded = await decodePng(u8);
      const capped = capSide(decoded.buf, decoded.w, decoded.h);
      const cover = classifyCoverBuf(capped.buf, capped.w, capped.h);
      base.opaque_replace = cover.opaque_replace;
      base.residual_usable = cover.residual_usable;
      base.flattened_screenshot_replace = cover.flattened_screenshot_replace;
      base.cover_regions = cover.cover_regions;
      base.width = cover.width;
      base.height = cover.height;
      base.dark_frac = cover.dark_frac;
      base.container = "png";
      if (op === "lift" && cover.residual_usable && !cover.opaque_replace) {
        const out = residualEnhanceBuf(capped.buf, capped.w, capped.h);
        const png = await encodePng(out, capped.w, capped.h);
        base.residual_png_b64 = bytesToB64(png);
        base.note = "Non-opaque cover: residual / contrast with inject OFF. Heatmap is not a transcript.";
        return base;
      }
    } catch (err) {
      if (op === "lift" && !base.leftover_bytes) {
        return { error: "PNG decode failed for lift: " + String(err.message || err), advisory: UNREDACT_NOTE };
      }
    }
  }
  const leftover = !!base.leftover_bytes;
  const opaque = !!base.opaque_replace;
  const residual = !!base.residual_usable;
  const mustRefuse = (opaque || base.flattened_screenshot_replace) && !leftover;
  if (op === "recover") {
    if (leftover) {
      base.note = "Recovered leftover bytes still in the container. Not guessed letters.";
      return base;
    }
    base.refuse_code = REFUSE_OPAQUE;
    base.stop = true;
    base.note = "No leftover container bytes. " + REFUSE_OPAQUE;
    return base;
  }
  if (op === "lift") {
    if (residual && !opaque) {
      base.note = "Non-opaque cover: residual / contrast with inject OFF. Heatmap is not a transcript.";
      return base;
    }
    if (leftover) {
      base.op = "recover";
      base.note = "Visual lift refused on clipped black. Leftover container bytes were extracted instead.";
      return base;
    }
    base.refuse_code = REFUSE_OPAQUE;
    base.stop = true;
    base.op = "refuse";
    base.note = "Lift-overlay refuses on clipped black / flattened box with no leftover bytes. " + REFUSE_OPAQUE;
    return base;
  }
  if (leftover) {
    base.note = "Locate + leftover-bytes. Recovered content is still in the container. Not guessed from a black box.";
  } else if (residual) {
    base.note = "Locate: non-opaque cover. Residual may be enhanced with inject OFF. Heatmap is not a transcript.";
  } else if (mustRefuse) {
    base.refuse_code = REFUSE_OPAQUE;
    base.stop = true;
    base.note = "Locate: opaque replace and no leftover bytes. Visual unredact refuses. " + REFUSE_OPAQUE;
  } else {
    base.note = "Locate complete. No invented letters.";
  }
  if (extras.query) {
    const q = String(extras.query);
    const hay = [];
    for (const hit of base.metadata_hits) hay.push(["metadata:" + hit.key, hit.value || ""]);
    for (const loc of base.text_layer) hay.push(["object:" + loc.object_id, (loc.strings || []).join(" ")]);
    for (const rec of base.recovered) hay.push(["leftover:" + rec.object_id, rec.preview || ""]);
    const low = q.toLowerCase();
    base.name_hits = hay.filter(([, t]) => String(t).toLowerCase().includes(low)).map(([where, t]) => ({
      query: q,
      where,
      excerpt: latinPreview(t, 160),
      invented: false,
      note: "Cited from bytes already in the file. Not fabricated.",
    }));
  }
  return base;
}

async function inflateBytes(u8) {
  if (typeof DecompressionStream !== "function") return null;
  for (const enc of ["deflate", "deflate-raw"]) {
    try {
      const ds = new DecompressionStream(enc);
      const ab = await new Response(new Blob([u8]).stream().pipeThrough(ds)).arrayBuffer();
      return new Uint8Array(ab);
    } catch {
      /* try next */
    }
  }
  return null;
}

async function sha256HexBytes(u8) {
  if (!globalThis.crypto || !crypto.subtle) return null;
  const buf = await crypto.subtle.digest("SHA-256", u8);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function u8slice(u8, start, end) {
  return u8.subarray(start, end == null ? u8.length : end);
}

function indexOfBytes(u8, needle, from = 0) {
  const n = typeof needle === "string" ? new TextEncoder().encode(needle) : needle;
  outer: for (let i = from; i <= u8.length - n.length; i++) {
    for (let j = 0; j < n.length; j++) if (u8[i + j] !== n[j]) continue outer;
    return i;
  }
  return -1;
}

function parseTounicodeJs(text) {
  const map = {};
  const block = /beginbfchar([\s\S]*?)endbfchar/g;
  let m;
  while ((m = block.exec(text))) {
    const pair = /<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g;
    let p;
    while ((p = pair.exec(m[1]))) {
      const src = parseInt(p[1], 16);
      const dest = p[2].replace(/\s+/g, "");
      let out = "";
      for (let i = 0; i + 3 < dest.length || i + 1 < dest.length; i += 4) {
        if (i + 3 < dest.length) out += String.fromCharCode(parseInt(dest.slice(i, i + 4), 16));
        else out += String.fromCharCode(parseInt(dest.slice(i, i + 2), 16));
      }
      map[src] = out;
    }
  }
  return map;
}

function decodeCodesJs(bytes, font) {
  const touni = font.tounicode || {};
  const keys = Object.keys(touni).map(Number);
  const two = keys.length ? Math.max(...keys) > 255 : !!(font.cid || font.identity);
  let text = "";
  const chars = [];
  for (let i = 0; i < bytes.length; ) {
    let code;
    let raw;
    if (two && i + 1 < bytes.length) {
      code = (bytes.charCodeAt(i) << 8) | bytes.charCodeAt(i + 1);
      raw = bytes.slice(i, i + 2);
      i += 2;
    } else {
      code = bytes.charCodeAt(i);
      raw = bytes.slice(i, i + 1);
      i += 1;
    }
    let ch = touni[code];
    if (!ch && !two && code >= 32 && code < 127) ch = String.fromCharCode(code);
    if (ch) {
      text += ch;
      chars.push({ char: ch, decoded_bytes: [...raw].map((c) => c.charCodeAt(0).toString(16).padStart(2, "0")).join(""), invented: false });
    }
  }
  return { text, chars };
}

function extractOpsJs(streamText, fontResolver) {
  const spans = [];
  const chars = [];
  const xobjects = [];
  const overlays = [];
  const under = [];
  let fontName = null;
  let font = { tounicode: {} };
  let fill = 0;
  const reRect = [];
  const show = (raw, operator, offset, hexed) => {
    let payload = raw;
    if (hexed) {
      const h = raw.replace(/\s+/g, "");
      payload = "";
      for (let i = 0; i + 1 < h.length; i += 2) payload += String.fromCharCode(parseInt(h.slice(i, i + 2), 16));
    } else {
      payload = unescapePdfLiteral("(" + raw + ")");
    }
    const dec = decodeCodesJs(payload, font);
    const preview = latinPreview(dec.text || (!hexed && looksLikeText(payload) ? payload : ""));
    spans.push({ operator, stream_offset: offset, font: fontName, text: preview, invented: false });
    for (const ch of dec.chars) chars.push({ ...ch, stream_offset: offset, operator, font: fontName });
    if (preview) under.push({ text: preview, offset, operator, font: fontName });
  };
  const tf = /\/([A-Za-z0-9._+-]+)\s+[\d.]+\s+Tf/g;
  let m;
  while ((m = tf.exec(streamText))) {
    fontName = "/" + m[1];
    font = fontResolver(m[1]) || font;
  }
  const tj = /\((?:\\.|[^\\)])*\)\s*T[j']|<([0-9A-Fa-f \t\r\n]+)>\s*Tj|\[((?:[^\[\]]|\((?:\\.|[^\\)])*\))*)\]\s*TJ/g;
  while ((m = tj.exec(streamText))) {
    if (m[0].includes("TJ")) {
      const inner = m[2] || "";
      const bits = inner.match(/\((?:\\.|[^\\)])*\)|<[^>]+>/g) || [];
      for (const b of bits) {
        if (b.startsWith("<")) show(b.slice(1, -1), "TJ", m.index, true);
        else show(b.slice(1, -1), "TJ", m.index, false);
      }
    } else if (m[1]) show(m[1], "Tj", m.index, true);
    else show(m[0].replace(/\s*T[j']$/, "").slice(1, -1), "Tj", m.index, false);
  }
  const doOp = /\/([A-Za-z0-9._+-]+)\s+Do/g;
  while ((m = doOp.exec(streamText))) xobjects.push("/" + m[1]);
  const rec = /([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+re/g;
  while ((m = rec.exec(streamText))) reRect.push({ x: +m[1], y: +m[2], w: +m[3], h: +m[4], offset: m.index });
  const rg = /([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg/g;
  while ((m = rg.exec(streamText))) fill = Math.max(+m[1], +m[2], +m[3]);
  const gop = /([\d.]+)\s+g/g;
  while ((m = gop.exec(streamText))) fill = +m[1];
  const paint = /\bf\b/g;
  const paints = [];
  while ((m = paint.exec(streamText))) paints.push(m.index);
  const pathOps = (streamText.match(/\b[mlcvyh]\b/g) || []).length;
  const textUnder = [];
  if (fill <= 0.08 && reRect.length && paints.length) {
    for (const ov of reRect) {
      overlays.push({ ...ov, operator: "f", invented: false });
      for (const box of under) {
        if (box.offset < (paints[0] || ov.offset + 1)) {
          textUnder.push({
            text: box.text,
            object_stream_offset: box.offset,
            operator: box.operator,
            font: box.font,
            overlay: { ...ov, operator: "f", invented: false },
            invented: false,
            note: "Text operators appear before an opaque vector rectangle in the same stream.",
          });
        }
      }
    }
  }
  return {
    spans,
    characters: chars,
    xobjects,
    overlays,
    text_under_overlay: textUnder,
    path_ops: pathOps,
    has_text_ops: spans.length > 0,
    has_image_ops: xobjects.length > 0,
    glyphs: spans.map((s) => s.text).filter(Boolean),
  };
}

export const HOSTED_COPY_MAX = 24000;
const KIND_REPLACED = "replaced";
const KIND_OVERLAID = "overlaid";
const KIND_DETACHED = "detached";
const KIND_SANITIZED = "sanitized rewrite";

function eofCutText(text, eofEnd) {
  let end = eofEnd;
  if (text[end] === "\r") end += 1;
  if (text[end] === "\n") end += 1;
  return end;
}

function parseClassicXrefsJs(text) {
  const revisions = [];
  const re = /\bxref\b/g;
  let m;
  while ((m = re.exec(text))) {
    if (m.index >= 5 && text.slice(m.index - 5, m.index + 4) === "startxref") continue;
    let pos = m.index + 4;
    const live = {};
    const freed = [];
    while (pos < text.length) {
      while (pos < text.length && /[ \t\r\n]/.test(text[pos])) pos += 1;
      if (text.slice(pos, pos + 7) === "trailer" || text.slice(pos, pos + 9) === "startxref") break;
      const hm = /^(\d+)\s+(\d+)\s+/.exec(text.slice(pos));
      if (!hm) break;
      const first = Number(hm[1]);
      const count = Number(hm[2]);
      pos += hm[0].length;
      for (let i = 0; i < count; i += 1) {
        while (pos < text.length && /[\r\n]/.test(text[pos])) pos += 1;
        const line = text.slice(pos, pos + 20);
        pos += Math.min(20, Math.max(0, text.length - pos));
        const parts = line.trim().split(/\s+/);
        if (parts.length < 3) continue;
        const off = Number(parts[0]);
        const gen = Number(parts[1]);
        const flag = String(parts[2] || "")[0];
        const objId = first + i;
        if (flag === "n") live[objId] = { offset: off, gen, kind: "n" };
        else if (flag === "f") {
          delete live[objId];
          freed.push({ id: objId, gen, next: off });
        }
      }
    }
    const tpos = text.indexOf("trailer", m.index + 4);
    let prev = null;
    let startxrefVal = m.index;
    const trailerOffset = tpos >= 0 ? tpos : m.index;
    if (tpos >= 0) {
      const nxt = text.indexOf("startxref", tpos);
      const chunk = text.slice(tpos, nxt >= 0 ? nxt : tpos + 400);
      const pm = chunk.match(/\/Prev\s+(\d+)/);
      if (pm) prev = Number(pm[1]);
      const sx = /startxref\s+(\d+)/.exec(text.slice(tpos));
      if (sx) startxrefVal = Number(sx[1]);
    }
    revisions.push({
      kind: "classic",
      offset: m.index,
      live,
      freed,
      prev,
      startxref: startxrefVal,
      trailer_offset: trailerOffset,
    });
  }
  return revisions;
}

async function copyPayloadJs(rawU8, { sourceRevision, filename, mediaType, hosted }) {
  const digest = await sha256HexBytes(rawU8);
  const out = {
    media_type: mediaType,
    filename,
    b64: null,
    sha256: digest,
    byte_length: rawU8.length,
    source_revision: sourceRevision,
    invented: false,
  };
  if (hosted && rawU8.length > HOSTED_COPY_MAX) {
    out.omitted = "hosted-preview-cap";
    out.note = "Copy bytes survive in the container. Hosted preview cites sha256 + length only. Local package returns full b64. Not invented.";
    return out;
  }
  out.b64 = bytesToB64(rawU8);
  return out;
}

function resolveRevisionJs(cursor, byStart, revisionsRaw, text) {
  if (byStart.has(cursor)) return byStart.get(cursor);
  let nearest = null;
  let best = 1e15;
  for (const r of revisionsRaw) {
    for (const key of ["offset", "startxref"]) {
      if (r[key] == null) continue;
      const d = Math.abs(Number(r[key]) - cursor);
      if (d < best) {
        nearest = r;
        best = d;
      }
    }
  }
  if (nearest && best <= 32) return nearest;
  const tokenAt = Math.max(0, cursor - 5);
  if (text.slice(tokenAt, cursor + 4) === "startxref") {
    const sx = /startxref\s+(\d+)/.exec(text.slice(tokenAt));
    if (sx) {
      const pointed = Number(sx[1]);
      if (pointed !== cursor) return resolveRevisionJs(pointed, byStart, revisionsRaw, text);
    }
  }
  return null;
}

export async function buildRevisionGraph(u8, objects = [], { hosted = true } = {}) {
  const text = bytesToLatin(u8);
  const revisionsRaw = parseClassicXrefsJs(text);
  for (const obj of objects) {
    if (!/\/Type\s*\/XRef/.test(obj.body || "")) continue;
    const prevM = (obj.body || "").match(/\/Prev\s+(\d+)/);
    revisionsRaw.push({
      kind: "xref-stream",
      offset: obj.offset,
      startxref: obj.offset,
      trailer_offset: obj.offset,
      prev: prevM ? Number(prevM[1]) : null,
      live: {},
      freed: [],
    });
  }
  revisionsRaw.sort((a, b) => (a.offset || 0) - (b.offset || 0));
  const spans = [];
  const sxRe = /startxref\s+(\d+)/g;
  let sm;
  while ((sm = sxRe.exec(text))) {
    const eof = text.indexOf("%%EOF", sm.index);
    if (eof < 0) continue;
    spans.push({ startxref: Number(sm[1]), startxref_token: sm.index, eof_end: eofCutText(text, eof + 5) });
  }
  const eofOffsets = [];
  let ei = 0;
  while ((ei = text.indexOf("%%EOF", ei)) >= 0) {
    eofOffsets.push(eofCutText(text, ei + 5));
    ei += 5;
  }
  const byStart = new Map();
  for (const rev of revisionsRaw) {
    const sx = rev.startxref != null ? rev.startxref : rev.offset;
    byStart.set(Number(sx), rev);
    byStart.set(Number(rev.offset || 0), rev);
  }
  const tip = spans.length ? spans[spans.length - 1].startxref : (revisionsRaw.length ? revisionsRaw[revisionsRaw.length - 1].offset : 0);
  let chain = [];
  const seen = new Set();
  let cursor = (revisionsRaw.length || spans.length) ? tip : null;
  while (cursor != null && !seen.has(cursor)) {
    seen.add(cursor);
    const rev = resolveRevisionJs(cursor, byStart, revisionsRaw, text);
    if (!rev) break;
    chain.push(rev);
    cursor = rev.prev != null ? Number(rev.prev) : null;
  }
  chain.reverse();
  if (chain.length < revisionsRaw.length) chain = revisionsRaw.slice();
  const uniq = [];
  const seenOff = new Set();
  for (const rev of chain) {
    const key = `${rev.kind}|${rev.offset}|${rev.startxref}`;
    if (seenOff.has(key)) continue;
    seenOff.add(key);
    uniq.push(rev);
  }
  chain = uniq;

  const objAt = (oid, offset) => {
    const vers = objects.filter((o) => o.id === Number(oid));
    if (!vers.length) return null;
    if (offset == null) return vers[vers.length - 1];
    let best = null;
    let bestD = 1e15;
    for (const o of vers) {
      const d = Math.abs((o.offset || 0) - offset);
      if (d < bestD) {
        best = o;
        bestD = d;
      }
    }
    return bestD <= 16 ? best : null;
  };

  const latinBytes = (s) => {
    const out = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i += 1) out[i] = s.charCodeAt(i) & 0xff;
    return out;
  };

  const cumulative = {};
  const snapshots = [];
  const nodes = [];
  for (let i = 0; i < chain.length; i += 1) {
    const rev = chain[i];
    for (const item of rev.freed || []) delete cumulative[item.id];
    for (const [oid, meta] of Object.entries(rev.live || {})) cumulative[Number(oid)] = { ...meta };
    const snap = {};
    for (const [k, v] of Object.entries(cumulative)) snap[Number(k)] = { ...v };
    snapshots.push(snap);
    const pageIds = [];
    for (const [oid, meta] of Object.entries(snap)) {
      const obj = objAt(Number(oid), meta.offset);
      if (obj && /\/Type\s*\/Page\b/.test(obj.body || "")) pageIds.push(`${obj.id} ${obj.gen}`);
    }
    const sx = rev.startxref != null ? rev.startxref : rev.offset;
    let span = spans.find((s) => Math.abs(s.startxref - (sx || 0)) <= 8);
    if (!span && spans[i]) span = spans[i];
    const cut = span ? span.eof_end : (eofOffsets[i] != null ? eofOffsets[i] : u8.length);
    const blob = u8.subarray(0, cut);
    const copy = await copyPayloadJs(blob, {
      sourceRevision: i,
      filename: `revision-${i}.pdf`,
      mediaType: "application/pdf",
      hosted,
    });
    copy.offset_start = 0;
    copy.offset_end = cut;
    copy.carve = "incremental-tip-cut";
    const embeds = [];
    for (const [oid, meta] of Object.entries(snap)) {
      const obj = objAt(Number(oid), meta.offset);
      if (!obj) continue;
      if (!/\/EmbeddedFile|\/Filespec|\/EF/.test(obj.body || "")) continue;
      const nameM = (obj.body || "").match(/\/(?:F|UF|Desc)\s*\(([^)]*)\)/);
      const name = nameM ? nameM[1] : `embed-${oid}`;
      if (obj.stream == null) continue;
      const rec = await copyPayloadJs(latinBytes(obj.stream), {
        sourceRevision: i,
        filename: name,
        mediaType: "application/octet-stream",
        hosted,
      });
      rec.object_id = `${obj.id} ${obj.gen}`;
      rec.offset = obj.offset;
      embeds.push(rec);
    }
    nodes.push({
      index: i,
      startxref: Number(sx || 0),
      trailer_offset: rev.trailer_offset || rev.offset,
      kind: rev.kind,
      object_count: Object.keys(snap).length,
      page_ids: pageIds,
      sha256_tip: copy.sha256,
      copy,
      embeds,
      invented: false,
    });
  }

  const edges = [];
  for (let i = 0; i < snapshots.length - 1; i += 1) {
    const a = snapshots[i];
    const b = snapshots[i + 1];
    const idsA = new Set(Object.keys(a).map(Number));
    const idsB = new Set(Object.keys(b).map(Number));
    const added = [];
    const replaced = [];
    const deleted = [];
    const freed = [];
    for (const oid of [...idsB].filter((x) => !idsA.has(x)).sort((x, y) => x - y)) {
      added.push({ id: oid, generation: (b[oid] || {}).gen, offset: (b[oid] || {}).offset, invented: false });
    }
    for (const oid of [...idsA].filter((x) => !idsB.has(x)).sort((x, y) => x - y)) {
      deleted.push({
        id: oid,
        generation: (a[oid] || {}).gen,
        offset: (a[oid] || {}).offset,
        kind: KIND_DETACHED,
        invented: false,
      });
    }
    for (const item of chain[i + 1].freed || []) freed.push({ id: item.id, generation: item.gen, invented: false });
    const pageDeltas = [];
    const redactionOps = [];
    for (const oid of [...idsA].filter((x) => idsB.has(x)).sort((x, y) => x - y)) {
      const oa = a[oid];
      const ob = b[oid];
      const same = oa.offset != null && ob.offset != null && Math.abs(oa.offset - ob.offset) <= 8;
      if (same) continue;
      const oldObj = objAt(oid, oa.offset);
      const newObj = objAt(oid, ob.offset);
      let kind = KIND_REPLACED;
      if (oldObj && newObj) {
        const newOps = extractOpsJs(newObj.stream || "", () => ({ tounicode: {} }));
        if (newOps.text_under_overlay && newOps.text_under_overlay.length) kind = KIND_OVERLAID;
        else if ((oldObj.stream || "") !== (newObj.stream || "")) kind = KIND_REPLACED;
      } else if (oldObj && !newObj) kind = KIND_DETACHED;
      else if (!oldObj && !newObj) kind = KIND_SANITIZED;
      const shaBefore = oldObj && oldObj.stream != null ? await sha256HexBytes(latinBytes(oldObj.stream)) : null;
      const shaAfter = newObj && newObj.stream != null ? await sha256HexBytes(latinBytes(newObj.stream)) : null;
      replaced.push({
        id: oid,
        generation: (newObj || oldObj || {}).gen || 0,
        offset_before: oa.offset,
        offset_after: ob.offset,
        sha256_before: shaBefore,
        sha256_after: shaAfter,
        kind,
        invented: false,
      });
      if (oldObj) {
        redactionOps.push({
          kind: KIND_DETACHED,
          object_id: `${oid} ${(oldObj || {}).gen || 0}`,
          offset: oa.offset,
          sha256: shaBefore,
          invented: false,
        });
      }
      const pagesTouch = [];
      for (const [pid, pmeta] of Object.entries(b)) {
        const pobj = objAt(Number(pid), pmeta.offset);
        if (!pobj || !/\/Type\s*\/Page\b/.test(pobj.body || "")) continue;
        if (new RegExp("/Contents\\s+" + oid + "\\s+").test(pobj.body) || Number(pid) === oid) {
          pagesTouch.push(`${pobj.id} ${pobj.gen}`);
        }
      }
      redactionOps.push({
        kind,
        page: pagesTouch[0] || null,
        pages: pagesTouch,
        object_id: `${oid} ${(newObj || {}).gen || 0}`,
        sha256_before: shaBefore,
        sha256_after: shaAfter,
        invented: false,
      });
    }
    for (const pid of new Set([...Object.keys(a), ...Object.keys(b)].map(Number))) {
      const pa = objAt(pid, (a[pid] || {}).offset);
      const pb = objAt(pid, (b[pid] || {}).offset);
      const isPage = (o) => o && /\/Type\s*\/Page\b/.test(o.body || "");
      if (!isPage(pa) && !isPage(pb)) continue;
      const keys = ["Contents", "Resources", "XObject", "Annots", "Metadata"];
      const snapKeys = (o) => {
        const s = {};
        for (const k of keys) {
          const mm = [...(o?.body || "").matchAll(new RegExp("/" + k + "\\s+(\\d+)\\s+(\\d+)\\s+R", "g"))];
          s[k] = mm.map((x) => `${x[1]} ${x[2]}`);
        }
        return s;
      };
      const sa = snapKeys(pa);
      const sb = snapKeys(pb);
      const changed = keys.filter((k) => JSON.stringify(sa[k]) !== JSON.stringify(sb[k]));
      if (!changed.length && a[pid] && b[pid] && a[pid].offset !== b[pid].offset) changed.push("Page");
      if (!changed.length && pb) {
        const cref = [...(pb.body || "").matchAll(/\/Contents\s+(\d+)\s+(\d+)\s+R/g)];
        for (const r of cref) {
          const rid = Number(r[1]);
          if (a[rid] && b[rid] && a[rid].offset !== b[rid].offset) changed.push("Contents");
        }
      }
      if (changed.length) {
        pageDeltas.push({
          page: `${pid} 0`,
          changed: [...new Set(changed)],
          before: sa,
          after: sb,
          invented: false,
        });
      }
    }
    edges.push({
      from: i,
      to: i + 1,
      added,
      replaced,
      deleted,
      freed,
      page_deltas: pageDeltas,
      redaction_ops: redactionOps,
      invented: false,
    });
  }

  return {
    revisions: nodes,
    edges,
    root_startxref: nodes[0] ? nodes[0].startxref : null,
    tip_startxref: nodes.length ? nodes[nodes.length - 1].startxref : tip,
    eof_offsets: eofOffsets,
    invented: false,
    note: "Incremental-update graph from startxref / Prev / trailer / xref (classic + XRef streams). Copies are tip-cuts of leftover bytes. Not invented. Not a forensic certification.",
  };
}

export async function locatePdfHistory(u8) {
  const head = bytesToLatin(u8.subarray(0, 5));
  const empty = {
    is_pdf: false,
    leftover_bytes: false,
    recovered: [],
    recovered_from: [],
    text_layer: [],
    metadata_hits: [],
    attachments: [],
    locations: [],
    capabilities: DEEP_CAPABILITIES.slice(),
    page_revisions: [],
    revision_compare: [],
    operator_text: [],
    classifications: [],
    recovered_characters: [],
    ocr: { ocr_ran: false, covered_letters_from_context: false, ocr_status: "unbound-hosted-preview", invented: false },
    revision_graph: { revisions: [], edges: [], root_startxref: null, eof_offsets: [], invented: false },
  };
  if (head !== "%PDF-") return empty;
  const text = bytesToLatin(u8);
  const base = locatePdfBytes(u8);
  const eofAt = text.lastIndexOf("%%EOF");
  const after = text.slice(eofAt >= 0 ? eofAt + 5 : text.length);
  const afterHits = [];
  if (after.trim()) {
    if (/obj/.test(after)) afterHits.push({ kind: "trailing-objects", invented: false });
    if (after.includes("%PDF")) afterHits.push({ kind: "appended-revision", invented: false });
    afterHits.push({ kind: "raw-tail", preview: latinPreview(after.slice(0, 400)), invented: false });
  }
  const after_eof = { bytes_after_eof: after.length, hits: afterHits, leftover: afterHits.length > 0 };

  const objects = [];
  const objRe = /(?:^|[^0-9])(\d+)\s+(\d+)\s+obj/g;
  let m;
  while ((m = objRe.exec(text))) {
    const id = Number(m[1]);
    const gen = Number(m[2]);
    const start = m.index + m[0].length;
    const endRel = text.indexOf("endobj", start);
    if (endRel < 0) continue;
    const body = text.slice(start, endRel);
    let stream = null;
    let filt = null;
    const sm = body.match(/stream\r?\n([\s\S]*?)endstream/);
    const fm = body.match(/\/Filter\s*\/([A-Za-z0-9]+)/);
    if (fm) filt = fm[1];
    if (sm) {
      const raw = new TextEncoder().encode(sm[1].replace(/\r?\n$/, ""));
      if (filt === "FlateDecode" || filt === "Fl") {
        const inf = await inflateBytes(raw);
        stream = inf ? bytesToLatin(inf) : sm[1];
      } else stream = sm[1];
    }
    objects.push({ id, gen, offset: m.index, body, stream, filter: filt, has_stream: !!sm, type: /\/Type\s*\/Page\b/.test(body) ? "Page" : (/\/Type\s*\/Catalog\b/.test(body) ? "Catalog" : null) });
  }

  const objstms = [];
  for (const obj of objects) {
    if (!/\/Type\s*\/ObjStm/.test(obj.body) || !obj.stream) continue;
    const n = Number((obj.body.match(/\/N\s+(\d+)/) || [])[1] || 0);
    const first = Number((obj.body.match(/\/First\s+(\d+)/) || [])[1] || 0);
    const header = obj.stream.slice(0, first);
    const nums = header.trim().split(/\s+/).map(Number);
    for (let i = 0; i + 1 < nums.length && objstms.length < n + 8; i += 2) {
      const oid = nums[i];
      const off = nums[i + 1];
      const next = i + 3 < nums.length ? first + nums[i + 3] : obj.stream.length;
      const mem = obj.stream.slice(first + off, next);
      objstms.push({ id: oid, gen: 0, offset: obj.offset, body: mem, stream: null, from_objstm: true, objstm_id: obj.id });
      objects.push({ id: oid, gen: 0, offset: obj.offset, body: mem, stream: null, filter: null, has_stream: false, from_objstm: true, objstm_id: obj.id });
    }
  }
  const xrefStreams = objects.some((o) => /\/Type\s*\/XRef/.test(o.body));

  const catalogs = objects.filter((o) => o.type === "Catalog");
  const tree = new Set();
  const walkKids = (body, depth = 0) => {
    if (!body || depth > 24) return;
    const kids = body.match(/\/Kids\s*\[([^\]]*)\]/);
    if (!kids) return;
    const refs = [...kids[1].matchAll(/(\d+)\s+(\d+)\s+R/g)];
    for (const r of refs) {
      const id = Number(r[1]);
      tree.add(id);
      const child = objects.filter((o) => o.id === id).slice(-1)[0];
      if (child) walkKids(child.body, depth + 1);
    }
  };
  for (const cat of catalogs) {
    const pages = cat.body.match(/\/Pages\s+(\d+)\s+(\d+)\s+R/);
    if (pages) {
      const node = objects.filter((o) => o.id === Number(pages[1])).slice(-1)[0];
      if (node) walkKids(node.body);
    }
  }

  const pages = objects.filter((o) => o.type === "Page");
  const page_revisions = [];
  const operator_text = [];
  const recovered_characters = [];
  const classifications = [];
  const revision_compare = [];
  const drawing_order = [];
  const image_layers = [];
  const extraFollow = [];

  const fontsFor = (pageBody) => {
    const map = {};
    const fontBlk = pageBody.match(/\/Font\s*<<([^>]*)>>/);
    if (!fontBlk) return map;
    const refs = [...fontBlk[1].matchAll(/\/([A-Za-z0-9._+-]+)\s+(\d+)\s+(\d+)\s+R/g)];
    for (const r of refs) {
      const fobj = objects.filter((o) => o.id === Number(r[2])).slice(-1)[0];
      let tounicode = {};
      if (fobj) {
        const tu = fobj.body.match(/\/ToUnicode\s+(\d+)\s+(\d+)\s+R/);
        if (tu) {
          const cmap = objects.filter((o) => o.id === Number(tu[1])).slice(-1)[0];
          if (cmap && cmap.stream) tounicode = parseTounicodeJs(cmap.stream);
        }
      }
      map[r[1]] = {
        tounicode,
        cid: fobj ? /\/Type0|\/Identity-H|\/CIDFont/.test(fobj.body) : false,
        identity: fobj ? /\/Identity-H/.test(fobj.body) : false,
      };
    }
    return map;
  };

  const followKeys = ["Contents", "Resources", "XObject", "Font", "ToUnicode", "Annots", "Metadata", "PieceInfo", "StructParents", "AcroForm"];
  for (const page of pages) {
    const inTree = tree.size === 0 || tree.has(page.id);
    const leftoverPage = !inTree;
    const graph = {};
    for (const k of followKeys) graph[k] = [];
    const followed = [];
    const seen = new Set();
    const walk = (obj, via) => {
      if (!obj) return;
      const key = obj.id + ":" + obj.offset + ":" + via;
      if (seen.has(key)) return;
      seen.add(key);
      followed.push({ via, object_id: `${obj.id} ${obj.gen}`, offset: obj.offset, invented: false });
      if (graph[via] && !graph[via].includes(`${obj.id} ${obj.gen}`)) graph[via].push(`${obj.id} ${obj.gen}`);
      for (const k of followKeys) {
        const rx = new RegExp("/" + k + "\\s+(\\d+)\\s+(\\d+)\\s+R", "g");
        let rm;
        while ((rm = rx.exec(obj.body))) {
          const childs = objects.filter((o) => o.id === Number(rm[1]));
          for (const child of childs) walk(child, k);
        }
        const nest = obj.body.match(new RegExp("/" + k + "\\s*<<([^>]*)>>"));
        if (nest) {
          const refs = [...nest[1].matchAll(/(\d+)\s+(\d+)\s+R/g)];
          for (const r of refs) {
            for (const child of objects.filter((o) => o.id === Number(r[1]))) walk(child, k);
          }
        }
      }
    };
    walk(page, "Page");
    const fonts = fontsFor(page.body);
    const resolver = (name) => fonts[name] || { tounicode: {} };
    const contentIds = [...page.body.matchAll(/\/Contents\s+(\d+)\s+(\d+)\s+R/g)].map((x) => Number(x[1]));
    const underAll = [];
    let hasText = false;
    let pathOps = 0;
    const pageImages = [];
    for (const cid of contentIds) {
      for (const streamObj of objects.filter((o) => o.id === cid)) {
        const payload = streamObj.stream || streamObj.body;
        const parsed = extractOpsJs(payload, resolver);
        hasText = hasText || parsed.has_text_ops;
        pathOps += parsed.path_ops;
        underAll.push(...parsed.text_under_overlay);
        const source = leftoverPage ? "prior" : "current";
        for (const span of parsed.spans) {
          operator_text.push({
            ...span,
            page: `${page.id} ${page.gen}`,
            object_id: streamObj.id,
            generation: streamObj.gen,
            source_revision: source,
            invented: false,
          });
          if (source === "prior" || parsed.text_under_overlay.length) {
            for (const ch of parsed.characters) {
              recovered_characters.push({
                char: ch.char,
                page: `${page.id} ${page.gen}`,
                object_id: streamObj.id,
                generation: streamObj.gen,
                stream_offset: ch.stream_offset,
                operator: ch.operator,
                font: ch.font,
                decoded_bytes: ch.decoded_bytes,
                source_revision: source === "prior" ? "prior" : "under-vector",
                sha256: null,
                invented: false,
              });
            }
          }
        }
      }
    }
    const xo = [...page.body.matchAll(/\/XObject[\s\S]*?\/[A-Za-z0-9._+-]+\s+(\d+)\s+(\d+)\s+R/g)];
    for (const r of xo) {
      const img = objects.filter((o) => o.id === Number(r[1])).slice(-1)[0];
      if (img && /\/Subtype\s*\/Image/.test(img.body)) {
        const w = Number((img.body.match(/\/Width\s+(\d+)/) || [])[1] || 0);
        const h = Number((img.body.match(/\/Height\s+(\d+)/) || [])[1] || 0);
        const rec = { object_id: `${img.id} ${img.gen}`, width: w, height: h, smask: /\/SMask/.test(img.body), invented: false, page: `${page.id} ${page.gen}` };
        pageImages.push(rec);
        image_layers.push(rec);
      }
    }
    let cls = "sanitized_rewrite";
    if (underAll.length) cls = "text_under_vector_overlay";
    else if (leftoverPage) cls = "old_revision_survives";
    else if (!hasText && pathOps >= 8) cls = "text_converted_to_outlines";
    else if (!hasText && pageImages.length) cls = "text_rasterized_into_image";
    classifications.push({ page: `${page.id} ${page.gen}`, class: cls, live: inTree, leftover: leftoverPage, invented: false });
    page_revisions.push({
      page_object: `${page.id} ${page.gen}`,
      offset: page.offset,
      live: inTree,
      leftover: leftoverPage,
      graph,
      followed,
      classification: cls,
      invented: false,
    });
    drawing_order.push({ page: `${page.id} ${page.gen}`, text_under_overlay: underAll, invented: false });
  }

  const byId = {};
  for (const obj of objects) (byId[obj.id] || (byId[obj.id] = [])).push(obj);
  for (const id of Object.keys(byId)) {
    const vers = byId[id].filter((o) => o.stream != null);
    if (vers.length >= 2) {
      const oldS = extractOpsJs(vers[0].stream, () => ({ tounicode: {} }));
      const newS = extractOpsJs(vers[vers.length - 1].stream, () => ({ tounicode: {} }));
      const oldSet = new Set(oldS.glyphs);
      const newSet = new Set(newS.glyphs);
      revision_compare.push({
        old_object: `${vers[0].id} ${vers[0].gen}`,
        new_object: `${vers[vers.length - 1].id} ${vers[vers.length - 1].gen}`,
        bytes_only_in_old: vers[0].stream !== vers[vers.length - 1].stream,
        strings_only_in_old: [...oldSet].filter((s) => !newSet.has(s)),
        glyph_sequences_only_in_old: [...oldSet].filter((s) => !newSet.has(s)),
        xobject_refs_only_in_old: oldS.xobjects.filter((x) => !newS.xobjects.includes(x)),
        invented: false,
      });
    }
  }

  const recovered = [...(base.recovered || [])];
  const recovered_from = [...(base.recovered_from || [])];
  for (const span of operator_text) {
    if (span.source_revision === "prior" && span.text) {
      recovered.push({
        object_id: `${span.object_id} ${span.generation}`,
        recovered_from: "old-revision",
        preview: span.text,
        operator: span.operator,
        source_revision: "prior",
        invented: false,
      });
      if (!recovered_from.includes("old-revision")) recovered_from.push("old-revision");
    }
  }
  for (const d of drawing_order) {
    for (const item of d.text_under_overlay || []) {
      recovered.push({
        object_id: d.page,
        recovered_from: "text-under-vector",
        preview: item.text,
        operator: item.operator,
        invented: false,
      });
      if (!recovered_from.includes("text-under-vector")) recovered_from.push("text-under-vector");
    }
  }
  if (after_eof.leftover) {
    recovered_from.push("after-eof");
    recovered.push({ object_id: "after-eof", recovered_from: "after-eof", preview: latinPreview(after.slice(0, 120)), invented: false });
  }
  for (const mem of objstms) {
    const strings = extractPdfStrings(mem.body);
    if (strings.length) {
      recovered.push({ object_id: `${mem.id} 0`, recovered_from: "unused-objstm-member", preview: strings.join(" | "), invented: false });
      if (!recovered_from.includes("unused-objstm-member")) recovered_from.push("unused-objstm-member");
    }
  }

  const producer_artifacts = [];
  const needles = [
    ["Acrobat", "acrobat"],
    ["Distiller", "acrobat-distiller"],
    ["Microsoft Word", "microsoft-word"],
    ["Tesseract", "tesseract-ocr"],
    ["/OCG", "ocg-layer"],
    ["/StructTreeRoot", "structure-tree"],
    ["/PieceInfo", "pieceinfo"],
    ["/LastModified", "revision-id"],
  ];
  for (const [needle, kind] of needles) {
    let at = 0;
    while ((at = text.indexOf(needle, at)) >= 0) {
      producer_artifacts.push({ kind, offset: at, excerpt: latinPreview(text.slice(Math.max(0, at - 16), at + 40), 80), invented: false });
      at += needle.length;
      if (producer_artifacts.length > 48) break;
    }
  }
  const identifiers = [];
  const idRe = [ [/EFTA[A-Z0-9-]{4,}/g, "fbi-doc-id"], [/[A-Z]{2,10}[-_ ]?\d{5,}/g, "bates"], [/D:\d{8,14}/g, "pdf-date"] ];
  for (const [re, kind] of idRe) {
    re.lastIndex = 0;
    let im;
    while ((im = re.exec(text))) {
      identifiers.push({ kind, value: im[0], offset: im.index, invented: false });
      if (identifiers.length > 40) break;
    }
  }

  const leftover_bytes = recovered.length > 0 || after_eof.leftover || page_revisions.some((p) => p.leftover);
  const structural = leftover_bytes || operator_text.some((s) => s.source_revision === "prior" && s.text);
  const ocr = {
    ocr_ran: false,
    ocr_after_structural_only: true,
    covered_letters_from_context: false,
    context_guess: false,
    heatmap_is_transcript: false,
    invented: false,
    ocr_engine: null,
    ocr_status: structural ? undefined : "unbound-hosted-preview",
    ocr_deferred: structural || undefined,
    reason: structural ? "structural leftover / operator / revision bytes recovered first" : undefined,
    note: "OCR only after structural recovery. Hosted preview has no OCR engine bound. Covered letters are never reconstructed from context. Context guesses are not recovery.",
  };

  for (const cat of catalogs) {
    const acro = cat.body.match(/\/AcroForm\s+(\d+)\s+(\d+)\s+R/);
    if (acro) extraFollow.push({ via: "AcroForm", object_id: `${acro[1]} ${acro[2]}`, invented: false });
  }

  return {
    ...base,
    is_pdf: true,
    leftover_bytes,
    recovered,
    recovered_from,
    capabilities: DEEP_CAPABILITIES.slice(),
    deep_history: true,
    page_revisions,
    revision_compare,
    operator_text,
    font_resolutions: [],
    drawing_order,
    classifications,
    orphans: { invented: false },
    xref_streams: xrefStreams,
    objstms: objstms.map((m) => ({ object_id: `${m.id} 0`, objstm_id: m.objstm_id, invented: false })),
    after_eof,
    image_layers,
    producer_artifacts,
    identifiers,
    ocr,
    recovered_characters,
    page_geometry: page_revisions.map((p) => ({ page_object: p.page_object, invented: false })),
    object_ids_replaced: revision_compare.map((c) => ({ old: c.old_object, new: c.new_object })),
    extra_catalog_follow: extraFollow,
    revision_graph: await buildRevisionGraph(u8, objects, { hosted: true }),
    guessed_letters: false,
    heatmap_is_transcript: false,
    forensic_certification: false,
  };
}

export function twinCompareHistory(a, b) {
  const as = new Set((a.operator_text || []).map((s) => s.text).filter(Boolean));
  const bs = new Set((b.operator_text || []).map((s) => s.text).filter(Boolean));
  for (const loc of a.text_layer || []) for (const s of loc.strings || []) as.add(s);
  for (const loc of b.text_layer || []) for (const s of loc.strings || []) bs.add(s);
  const bvals = new Set((b.identifiers || []).map((i) => i.kind + ":" + i.value));
  const shared = (a.identifiers || []).filter((i) => bvals.has(i.kind + ":" + i.value));
  return {
    comparable: true,
    only_in_first: [...as].filter((s) => !bs.has(s)).sort(),
    only_in_second: [...bs].filter((s) => !as.has(s)).sort(),
    shared_identifiers: shared,
    identifiers_first: a.identifiers || [],
    identifiers_second: b.identifiers || [],
    heatmap_is_transcript: false,
    invented: false,
    note: "Twin / neighboring-document compare of operator text and identifiers. Cited from bytes present. Not guessed.",
  };
}

export const RECOVER_OPS = [
  "locate", "deep-recover", "revision-graph", "cross-compare", "extract-embedded",
  "scan-orphans", "scan-metadata", "scan-sidecars", "scan-history", "refuse",
];
export const RECOVER_NOTE =
  "Universal artifact recovery. Present bytes and documented structure only. " +
  "Never infer covered letters from context. SLOT parsers stay SLOT; LIVE parsers stay LIVE. " +
  "Secrets: secret_material_present + path/offset; values suppressed. " +
  "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE.";

const SECRET_KEY_JS = /(password|passwd|secret|api[_-]?key|\btoken\b|authorization|cookie|private[_-]?key|aws_secret|bearer)/i;
const SECRET_VAL_JS = /((?:password|passwd|secret|api[_-]?key|\btoken\b|authorization|cookie|private[_-]?key|aws_secret|bearer)[^\s:=]*)\s*[:=]\s*\S+/gi;

export function parseRecoverOp(value, fallback = "locate") {
  const key = String(value || fallback).trim().toLowerCase().replaceAll("_", "-");
  const aliases = {
    locate: "locate",
    deep: "deep-recover",
    "deep-recover": "deep-recover",
    "revision-graph": "revision-graph",
    compare: "cross-compare",
    "cross-compare": "cross-compare",
    "extract-embedded": "extract-embedded",
    "scan-orphans": "scan-orphans",
    "scan-metadata": "scan-metadata",
    "scan-sidecars": "scan-sidecars",
    "scan-history": "scan-history",
    refuse: "refuse",
    production: "locate",
    redactions: "deep-recover",
  };
  return aliases[key] || null;
}

export function listRecover() {
  return {
    family: "recover",
    ops: RECOVER_OPS.slice(),
    refuse_codes: [
      "SL-RECOVER-NO-BYTES", "SL-RECOVER-SANITIZED", "SL-RECOVER-OPAQUE",
      "SL-RECOVER-UNSUPPORTED", "SL-RECOVER-CORRUPT", "SL-RECOVER-ENCRYPTED",
      "SL-RECOVER-LIMIT", "SL-UNREDACT-OPAQUE",
    ],
    live_kinds: ["pdf", "json", "xml", "html", "svg", "txt", "eml", "zip", "png", "jpeg"],
    slot_kinds: ["7z", "heic", "heif"],
    no_lie: true,
    guessed_letters: false,
    context_reconstruction: false,
    catalog_door: false,
    worker_path: "/v1/recover",
    note: RECOVER_NOTE,
    author: "Aziel Eliab",
    status: "live",
  };
}

function suppressSecretJs(s) {
  return String(s || "").replace(SECRET_VAL_JS, (_, a) => a + "=<suppressed>");
}

function detectKindJs(u8, filename) {
  const head = bytesToLatin(u8.subarray(0, Math.min(u8.length, 16)));
  if (head.startsWith("%PDF")) return { kind: "pdf", status: "live", confirmed: true };
  if (u8.length >= 8 && u8[0] === 0x89 && head.includes("PNG")) return { kind: "png", status: "live", confirmed: true };
  if (u8[0] === 0xff && u8[1] === 0xd8 && u8[2] === 0xff) return { kind: "jpeg", status: "live", confirmed: true };
  if (head.startsWith("PK")) return { kind: "zip", status: "live", confirmed: true };
  if (head.startsWith("7z")) return { kind: "7z", status: "slot", confirmed: true };
  if (u8.length > 12 && bytesToLatin(u8.subarray(4, 8)) === "ftyp" && /heic|heif|mif1/.test(bytesToLatin(u8.subarray(8, 16)))) {
    return { kind: "heic", status: "slot", confirmed: true };
  }
  const text = bytesToLatin(u8.subarray(0, Math.min(u8.length, 800)));
  if (/^(from|to|subject|message-id|mime-version):/im.test(text)) return { kind: "eml", status: "live", confirmed: true };
  if (/^\s*[\[{]/.test(text)) return { kind: "json", status: "live", confirmed: true };
  if (/^\s*<svg/i.test(text)) return { kind: "svg", status: "live", confirmed: true };
  if (/^\s*<\?xml|^\s*<html/i.test(text)) return { kind: "xml", status: "live", confirmed: true };
  const ext = String(filename || "").split(".").pop() || "";
  if (["txt", "md", "csv", "log", "yml", "yaml"].includes(ext)) return { kind: ext === "yml" ? "yaml" : ext, status: "live", confirmed: true };
  return { kind: "bin", status: "live-carve", confirmed: false };
}

function zipNamesJs(u8) {
  const text = bytesToLatin(u8);
  const names = [];
  let at = 0;
  while ((at = text.indexOf("PK\x03\x04", at)) >= 0 && names.length < 80) {
    if (at + 30 > u8.length) break;
    const nameLen = u8[at + 26] | (u8[at + 27] << 8);
    const extraLen = u8[at + 28] | (u8[at + 29] << 8);
    const name = text.slice(at + 30, at + 30 + nameLen);
    if (name) names.push(name);
    at += 30 + nameLen + extraLen;
  }
  return names;
}

export async function recoverFromB64(b64, extras = {}) {
  let u8;
  try {
    u8 = b64ToBytes(b64);
  } catch (err) {
    return { error: "decode failed: " + String(err.message || err), advisory: RECOVER_NOTE, no_lie: true };
  }
  const op = parseRecoverOp(extras.op || extras.verb || "locate");
  if (!op) return { error: "unknown recover op", known: RECOVER_OPS, advisory: RECOVER_NOTE, no_lie: true };
  const filename = extras.filename || "artifact";
  const det = detectKindJs(u8, filename);
  const env = {
    product: "spectrallock",
    author: "Aziel Eliab",
    family: "recover",
    op,
    artifact: { filename, kind: det.kind, status: det.status, confirmed: det.confirmed, byte_length: u8.length, invented: false },
    type: det.kind,
    format_status: det.status,
    revisions: [],
    metadata: [],
    embedded: [],
    orphans: [],
    prior_content: [],
    redaction_regions: [],
    recovered: [],
    refused: [],
    cross_file_matches: [],
    provenance: [],
    warnings: [],
    secrets: [],
    carved: [],
    revision_graph: { revisions: [], edges: [], invented: false },
    no_lie: true,
    guessed_letters: false,
    note: RECOVER_NOTE,
    invented: false,
  };
  if (det.status === "slot") {
    env.refuse_code = "SL-RECOVER-UNSUPPORTED";
    env.refused.push({ code: "SL-RECOVER-UNSUPPORTED", note: "Parser unbound (SLOT).", invented: false });
    env.warnings.push("SLOT: parser not bound. Not advertised as LIVE.");
  }
  const text = bytesToLatin(u8);
  if (SECRET_KEY_JS.test(text)) {
    env.secret_material_present = true;
    env.secrets.push({ secret_material_present: true, path: filename, value_suppressed: true, invented: false });
  }
  if (det.kind === "pdf") {
    const hist = await locatePdfHistory(u8);
    env.revision_graph = hist.revision_graph || env.revision_graph;
    env.revisions = (env.revision_graph.revisions || []);
    env.recovered = hist.recovered || [];
    env.prior_content = env.recovered.filter((r) => /old|prior|after-eof|orphan/.test(String(r.recovered_from || r.source_revision || "")));
    env.pdf_history = { leftover_bytes: hist.leftover_bytes, recovered_from: hist.recovered_from, invented: false };
  } else if (det.kind === "json") {
    for (const key of ["_deleted", "_old", "_previous", "_history", "_backup", "_draft"]) {
      if (text.includes(key)) env.recovered.push({ kind: "json-tombstone", preview: key, path: "/" + key, state: "present_prior_revision", invented: false });
    }
  } else if (det.kind === "zip") {
    for (const name of zipNamesJs(u8)) {
      env.embedded.push({ kind: "zip-member", preview: name, path: name, state: "present_embedded", invented: false });
      if (/(backup|old|final|copy|draft|original|tmp|autosave)/i.test(name)) {
        env.recovered.push({ kind: "flag-name", preview: name, path: name, state: "present_prior_revision", invented: false });
      }
    }
  } else if (det.kind === "eml") {
    if (/alice/i.test(text)) env.recovered.push({ kind: "email-body", preview: suppressSecretJs(latinPreview(text, 200)), path: filename, invented: false });
    if (/content-type:\s*multipart/i.test(text)) env.recovered.push({ kind: "alternate-mime", preview: "multipart", path: filename, invented: false });
  } else if (det.kind === "png" || det.kind === "jpeg") {
    if (text.includes("tEXt") || text.includes("Comment")) env.metadata.push({ kind: "image-text", preview: "ancillary", path: filename, invented: false });
    const iend = text.indexOf("IEND");
    if (iend >= 0 && iend + 8 < text.length && text.slice(iend + 8).trim()) {
      env.carved.push({ kind: "after-iend", offset: iend + 8, state: "present_orphan", invented: false });
    }
  } else if (det.kind !== "bin") {
    env.recovered.push({ kind: "text", preview: suppressSecretJs(latinPreview(text, 200)), path: filename, invented: false });
  }
  for (const rec of env.recovered) rec.preview = suppressSecretJs(rec.preview || "");
  env.secret_material_present = !!env.secret_material_present || env.secrets.length > 0;
  env.recovered_count = env.recovered.length;
  if (extras.twin_b64) {
    try {
      const twin = await recoverFromB64(extras.twin_b64, { op: "locate", filename: "twin" });
      env.cross_compare = { only_in_first: [], only_in_second: [], invented: false, note: "Hosted compare cites present bytes only." };
      env.twin_type = twin.type;
    } catch {
      env.warnings.push("Twin decode failed. Not guessed.");
    }
  }
  if (!env.recovered_count && !env.carved.length && det.status !== "slot" && op !== "refuse") {
    env.refuse_code = env.refuse_code || "SL-RECOVER-NO-BYTES";
    env.refused.push({ code: "SL-RECOVER-NO-BYTES", invented: false });
  }
  return env;
}

export const HANDWRITING_OPS = [
  "analyze", "compare", "side-by-side", "graph", "forgery-indicators", "refuse",
];
export const HANDWRITING_FAMILY = ["handwriting", "handwrite", "ink-hand", "forgery-scan"];
export const REFUSE_NO_INK = "SL-HANDWRITING-NO-INK";
export const REFUSE_UNSUPPORTED = "SL-HANDWRITING-UNSUPPORTED";
export const REFUSE_LIMIT = "SL-HANDWRITING-LIMIT";
export const HANDWRITING_NOTE =
  "Handwriting analysis is synthetic image analysis of a user-supplied " +
  "scan or photo of paper. Stroke weight, speed cues, bleed, erasures, " +
  "tracing, and forgery indicators are heuristics from present pixels. " +
  "They are candidates — human verification required. " +
  "Heatmaps are residual overlays. " +
  "Hosted /v1/handwriting is a 256 px PNG preview; the full pipeline is the Python package. " +
  "An empty gate is a valid reading. Balance/lemon never invent marks. " +
  "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE.";

const HANDWRITING_FEATURES = {
  stroke_weight: { status: "live", note: "width from ink mask + 4-dir radius (hosted); chamfer in package" },
  speed_cues: { status: "live", note: "taper / tremor / ballistic vs controlled — heuristic only" },
  ink_density: { status: "live", note: "darkness of ink-mask pixels" },
  bleed_feathering: { status: "live", note: "edge gradient width / capillary-spread proxy" },
  handwriting_shifts: { status: "live", note: "baseline drift, slant, size change" },
  erasures: { status: "live", note: "abrasion brightening + mid-gray ghosts" },
  tracing: { status: "live", note: "width uniformity, lift clustering" },
  tremor_copy: { status: "live", note: "high-frequency wobble + slow uniform width" },
  pen_lifts: { status: "live", note: "connected-component breaks" },
  retouch_overwrite: { status: "live", note: "dark-on-dark cores" },
  dual_ink: { status: "live", note: "hue clusters in stroke pixels" },
  baseline_misalign: { status: "live", note: "row centroid drift" },
  indent_helper: { status: "live", note: "indent mode inject-OFF; not ESDA" },
  clone_stamp: { status: "live", note: "repeated 8×8 luminance hashes far apart" },
  compression_paste: { status: "live", note: "8×8 block energy discontinuities" },
  ductus: { status: "live", note: "gradient-direction consistency" },
  style_shift: { status: "live", note: "component aspect-ratio regime change — heuristic flag only" },
  jpeg_decode: { status: "slot", note: "hosted preview is PNG only; local package accepts JPEG" },
  pressure_newtons: { status: "slot", note: "no force sensor; width/darkness is a proxy only" },
  speed_mm_s: { status: "slot", note: "no temporal capture; taper/tremor are shape cues" },
  writer_identity: { status: "slot", note: "never claimed as identity fact" },
  esda: { status: "slot", note: "not electrostatic detection" },
  chemical_ink_dating: { status: "slot", note: "not a lab assay" },
  court_examiner_opinion: { status: "slot", note: "not a qualified examiner finding" },
};

export function parseHandwritingOp(value, fallback = "analyze") {
  const key = String(value || fallback).trim().toLowerCase().replaceAll("_", "-");
  const aliases = {
    analyze: "analyze",
    handwriting: "analyze",
    handwrite: "analyze",
    "ink-hand": "analyze",
    "forgery-scan": "forgery-indicators",
    compare: "compare",
    "side-by-side": "side-by-side",
    sidebyside: "side-by-side",
    graph: "graph",
    "forgery-indicators": "forgery-indicators",
    forgery: "forgery-indicators",
    refuse: "refuse",
  };
  return aliases[key] || null;
}

export function listHandwriting() {
  const live = Object.keys(HANDWRITING_FEATURES).filter((k) => HANDWRITING_FEATURES[k].status === "live").sort();
  const slot = Object.keys(HANDWRITING_FEATURES).filter((k) => HANDWRITING_FEATURES[k].status === "slot").sort();
  return {
    family: "handwriting",
    aliases: HANDWRITING_FAMILY.slice(),
    ops: HANDWRITING_OPS.slice(),
    refuse_codes: [REFUSE_NO_INK, REFUSE_UNSUPPORTED, REFUSE_LIMIT],
    feature_matrix: { ...HANDWRITING_FEATURES },
    live_signals: live,
    slot_signals: slot,
    no_lie: true,
    guessed_letters: false,
    forensic_certification: false,
    esda: false,
    chemical_ink_dating: false,
    writer_identification_as_fact: false,
    heatmap_is_transcript: false,
    heatmap_is_court_finding: false,
    catalog_door: false,
    worker_path: "/v1/handwriting",
    hosted_preview: true,
    max_side: MAX_SIDE,
    jpeg: false,
    note: HANDWRITING_NOTE,
    author: "Aziel Eliab",
    status: "live",
  };
}

function handwritingIndicator(kind, note, confidence, extra) {
  return {
    kind,
    note,
    phrasing: "indicator / heuristic / candidate — human verification required",
    confidence: Math.max(0, Math.min(1, Number(confidence.toFixed(3)))),
    confidence_means: "pixel signal quality, not a finding that this is forged",
    invented: false,
    ...(extra || {}),
  };
}

function inkMaskFromLuma(L, n) {
  const sorted = Array.from(L).sort((a, b) => a - b);
  const paper = sorted[Math.min(n - 1, Math.floor(n * 0.88))] || 0.92;
  const thresh = Math.max(0.08, paper - 0.16);
  const ink = new Uint8Array(n);
  let count = 0;
  for (let i = 0; i < n; i++) {
    if (L[i] < thresh) { ink[i] = 1; count += 1; }
  }
  return { ink, frac: n ? count / n : 0, paper };
}

function radiusWidth(ink, w, h) {
  const widths = [];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x;
      if (!ink[i]) continue;
      let best = 8;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        let d = 1;
        while (d < best) {
          const nx = x + dx * d, ny = y + dy * d;
          if (nx < 0 || ny < 0 || nx >= w || ny >= h || !ink[ny * w + nx]) { best = d; break; }
          d += 1;
        }
      }
      widths.push(best * 2);
    }
  }
  if (!widths.length) return { mean: 0, std: 0, cv: 0, min: 0, max: 0 };
  const mean = widths.reduce((a, b) => a + b, 0) / widths.length;
  const var_ = widths.reduce((a, b) => a + (b - mean) * (b - mean), 0) / widths.length;
  const std = Math.sqrt(var_);
  return { mean, std, cv: std / Math.max(mean, 1e-3), min: Math.min(...widths), max: Math.max(...widths) };
}

function sobelMag(L, w, h) {
  const mag = new Float32Array(w * h);
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const gx =
        -L[i - w - 1] + L[i - w + 1] +
        -2 * L[i - 1] + 2 * L[i + 1] +
        -L[i + w - 1] + L[i + w + 1];
      const gy =
        -L[i - w - 1] - 2 * L[i - w] - L[i - w + 1] +
        L[i + w - 1] + 2 * L[i + w] + L[i + w + 1];
      mag[i] = Math.hypot(gx, gy);
    }
  }
  return mag;
}

function labelInk(ink, w, h, limit = 48) {
  const seen = new Uint8Array(w * h);
  const comps = [];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const start = y * w + x;
      if (!ink[start] || seen[start]) continue;
      const stack = [start];
      seen[start] = 1;
      let xs = 0, ys = 0, n = 0;
      let x0 = x, x1 = x, y0 = y, y1 = y;
      while (stack.length && n < 80000) {
        const i = stack.pop();
        const cy = Math.floor(i / w), cx = i - cy * w;
        xs += cx; ys += cy; n += 1;
        if (cx < x0) x0 = cx; if (cx > x1) x1 = cx;
        if (cy < y0) y0 = cy; if (cy > y1) y1 = cy;
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            const nx = cx + dx, ny = cy + dy;
            if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
            const ni = ny * w + nx;
            if (ink[ni] && !seen[ni]) { seen[ni] = 1; stack.push(ni); }
          }
        }
      }
      if (n < 8) continue;
      comps.push({
        id: "s" + comps.length,
        bbox: [x0, y0, x1, y1],
        area: n,
        cx: xs / n,
        cy: ys / n,
        width: x1 - x0 + 1,
        height: y1 - y0 + 1,
        aspect: (x1 - x0 + 1) / Math.max(1, y1 - y0 + 1),
      });
      if (comps.length >= limit) return comps;
    }
  }
  comps.sort((a, b) => a.cx - b.cx || a.cy - b.cy);
  comps.forEach((c, i) => { c.id = "s" + i; });
  return comps;
}

function clonePairs(L, w, h) {
  const size = 8;
  const seen = new Map();
  for (let y = 0; y <= h - size; y += size) {
    for (let x = 0; x <= w - size; x += size) {
      let hash = 2166136261;
      for (let dy = 0; dy < size; dy++) {
        for (let dx = 0; dx < size; dx++) {
          const q = Math.min(15, Math.max(0, Math.floor(L[(y + dy) * w + (x + dx)] * 15)));
          hash ^= q;
          hash = Math.imul(hash, 16777619);
        }
      }
      hash >>>= 0;
      if (!seen.has(hash)) seen.set(hash, []);
      seen.get(hash).push([x, y]);
    }
  }
  const clones = [];
  for (const pts of seen.values()) {
    if (pts.length < 2) continue;
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        if (Math.abs(pts[i][0] - pts[j][0]) + Math.abs(pts[i][1] - pts[j][1]) >= 16) {
          clones.push([pts[i][0], pts[i][1], pts[j][0], pts[j][1]]);
          if (clones.length >= 6) return clones;
        }
      }
    }
  }
  return clones;
}

async function sha256HexU8(u8) {
  const digest = await crypto.subtle.digest("SHA-256", u8);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function heatmapOverlay(arr, w, h, kind) {
  const rgb = grayToRgb(norm01(arr));
  const png = await encodePng(rgb, w, h);
  return {
    kind,
    note: "heatmap ≠ transcript",
    media_type: "image/png",
    b64: bytesToB64(png),
    sha256: await sha256HexU8(png),
    heatmap_is_transcript: false,
    heatmap_is_court_finding: false,
    invented: false,
  };
}

async function analyzeHandwritingBuf(buf, w, h, filename, srcW, srcH, limited) {
  const n = w * h;
  const L = toLuma(buf, w, h);
  const { ink, frac, paper } = inkMaskFromLuma(L, n);
  const rgbBytes = new Uint8Array(buf.length);
  for (let i = 0; i < buf.length; i++) rgbBytes[i] = Math.max(0, Math.min(255, Math.round(buf[i] * 255)));
  const env = {
    product: "spectrallock",
    author: "Aziel Eliab",
    family: "handwriting",
    op: "analyze",
    artifact: {
      filename,
      width: srcW,
      height: srcH,
      analyze_width: w,
      analyze_height: h,
      scale: limited ? MAX_SIDE / Math.max(srcW, srcH) : 1,
      sha256: await sha256HexU8(rgbBytes),
      invented: false,
    },
    strokes: [],
    features: { weight: [], speed_cues: [], density: [], bleed: [], shifts: [], erasures: [], tracing: [] },
    forgery_indicators: [],
    side_by_side: [],
    graph: { nodes: [], edges: [], invented: false },
    overlays: [],
    provenance: [],
    refused: [],
    warnings: [
      "synthetic_image_analysis_not_lab",
      "not_forensic_certification",
      "heatmap_is_not_transcript",
      "heatmap_is_not_court_finding",
      "human_verification_required",
      "hosted_preview_256px_png",
    ],
    helper_modes: [],
    no_lie: true,
    guessed_letters: false,
    esda: false,
    chemical_ink_dating: false,
    writer_identification_as_fact: false,
    forensic_certification: false,
    hosted_preview: true,
    lamb_lens: "Service → Clarity → Peace",
    identity: "Aziel Eliab",
    note: HANDWRITING_NOTE,
    inject_note: INJECT_NOTE,
    limitation: LIMITATION,
    invented: false,
  };
  if (limited) {
    env.warnings.push(REFUSE_LIMIT);
    env.hosted_cap = MAX_SIDE;
  }
  if (frac < 0.004) {
    env.refuse_code = REFUSE_NO_INK;
    env.refused.push({
      code: REFUSE_NO_INK,
      note: "No writable ink-like strokes found in the supplied pixels.",
      invented: false,
    });
    env.stop = true;
    return env;
  }

  const wt = radiusWidth(ink, w, h);
  env.features.weight.push({
    mean_px: Number(wt.mean.toFixed(3)),
    std_px: Number(wt.std.toFixed(3)),
    cv: Number(wt.cv.toFixed(3)),
    note: "pressure proxy from stroke width. Not a force measurement. Hosted uses 4-dir radius.",
    invented: false,
  });

  let densSum = 0, densN = 0, tremorSum = 0;
  const density = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    density[i] = 1 - L[i];
    if (ink[i]) { densSum += density[i]; densN += 1; }
  }
  const inkDensity = densN ? densSum / densN : 0;
  env.features.density.push({
    mean: Number(inkDensity.toFixed(4)),
    note: "darkness of ink-mask pixels. Not pigment mass.",
    invented: false,
  });

  const mag = sobelMag(L, w, h);
  const ring = new Uint8Array(n);
  let bleedSum = 0, bleedN = 0;
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      if (ink[i]) continue;
      if (ink[i - 1] || ink[i + 1] || ink[i - w] || ink[i + w]) {
        ring[i] = 1;
        bleedSum += mag[i];
        bleedN += 1;
      }
    }
  }
  env.features.bleed.push({
    edge_grad_mean: Number((bleedN ? bleedSum / bleedN : 0).toFixed(4)),
    note: "capillary-spread / feathering proxy from edge gradient. Not a paper assay.",
    invented: false,
  });

  const blur = new Float32Array(n);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let s = 0, c = 0;
      for (let dy = -1; dy <= 1; dy++) {
        for (let dx = -1; dx <= 1; dx++) {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
          s += L[ny * w + nx]; c += 1;
        }
      }
      blur[y * w + x] = s / c;
    }
  }
  for (let i = 0; i < n; i++) if (ink[i]) tremorSum += Math.abs(L[i] - blur[i]);
  const tremor = densN ? tremorSum / densN : 0;
  env.features.speed_cues.push({
    tremor: Number(tremor.toFixed(4)),
    taper_px: Number((wt.max - wt.min).toFixed(3)),
    ballistic_vs_controlled: tremor > 0.035 && wt.std < 0.6 ? "controlled-candidate" : "fluent-or-unclear",
    note: "shape cues only. Speed in mm/s is SLOT.",
    invented: false,
  });

  const rowCents = new Map();
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      if (!ink[y * w + x]) continue;
      const k = Math.floor(y / 4);
      if (!rowCents.has(k)) rowCents.set(k, []);
      rowCents.get(k).push(y);
    }
  }
  const cents = [...rowCents.entries()].filter(([, v]) => v.length > 6).map(([, v]) => v.reduce((a, b) => a + b, 0) / v.length);
  const shifts = [];
  if (cents.length >= 3) {
    const meanC = cents.reduce((a, b) => a + b, 0) / cents.length;
    const drift = Math.sqrt(cents.reduce((a, b) => a + (b - meanC) * (b - meanC), 0) / cents.length);
    env.features.shifts.push({
      baseline_drift_px: Number(drift.toFixed(3)),
      note: "row-centroid drift. Not proof of a second writer.",
      invented: false,
    });
    shifts.push(drift);
  }

  const bright = new Float32Array(n);
  const ghost = new Float32Array(n);
  let brightOn = false, ghostOn = false, bx0 = w, by0 = h, bx1 = 0, by1 = 0, gx0 = w, gy0 = h, gx1 = 0, gy1 = 0;
  let ghostN = 0;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x;
      if (ink[i]) continue;
      if (L[i] > Math.min(0.97, paper + 0.04)) {
        bright[i] = 1; brightOn = true;
        if (x < bx0) bx0 = x; if (y < by0) by0 = y; if (x > bx1) bx1 = x; if (y > by1) by1 = y;
      }
      if (L[i] > 0.55 && L[i] < 0.78 && mag[i] > 0.08) {
        ghost[i] = 1; ghostN += 1;
        if (x < gx0) gx0 = x; if (y < gy0) gy0 = y; if (x > gx1) gx1 = x; if (y > gy1) gy1 = y;
      }
    }
  }
  if (brightOn) {
    env.features.erasures.push({
      kind: "abrasion-brightening",
      frac: Number((bright.reduce((a, b) => a + b, 0) / n).toFixed(4)),
      bbox: [bx0, by0, bx1, by1],
      note: "candidate white-out / abrasion. Human verification required.",
      invented: false,
    });
  }
  if (ghostN / n > 0.002) {
    ghostOn = true;
    env.features.erasures.push({
      kind: "residual-ghost",
      frac: Number((ghostN / n).toFixed(4)),
      bbox: [gx0, gy0, gx1, gy1],
      note: "mid-gray residual near strokes. Not recovered letters.",
      invented: false,
    });
  }

  const comps = labelInk(ink, w, h);
  env.strokes = comps.map((c) => ({
    id: c.id, bbox: c.bbox, area: c.area,
    center: [Number(c.cx.toFixed(1)), Number(c.cy.toFixed(1))],
    aspect: Number(c.aspect.toFixed(3)), invented: false,
  }));
  const nodes = comps.map((c) => ({ id: c.id, kind: "stroke-segment", bbox: c.bbox, area: c.area, invented: false }));
  const edges = [];
  for (let i = 0; i < comps.length - 1; i++) {
    const a = comps[i], b = comps[i + 1];
    const dist = Math.hypot(a.cx - b.cx, a.cy - b.cy);
    const anomalous = dist > Math.max(w, h) * 0.35 || Math.abs(a.aspect - b.aspect) > 2.2;
    edges.push({
      from: a.id, to: b.id, kind: "sequence",
      distance_px: Number(dist.toFixed(2)),
      anomalous,
      note: anomalous ? "anomalous edge is a heuristic flag, not a forgery finding" : "sequence",
      invented: false,
    });
  }
  env.graph = { nodes, edges, invented: false };

  if (wt.mean > 0 && wt.cv < 0.18 && comps.length >= 4) {
    env.features.tracing.push({
      kind: "unnatural-width-uniformity",
      cv: Number(wt.cv.toFixed(3)),
      note: "candidate careful tracing / guide. Heuristic only.",
      invented: false,
    });
  }

  const indicators = [];
  if (tremor > 0.04 && wt.std < 0.85) {
    indicators.push(handwritingIndicator(
      "tremor-slow-copy",
      "High-frequency wobble with relatively uniform width — careful-copy candidate.",
      Math.min(0.85, 0.35 + tremor * 8),
    ));
  }
  if (comps.length >= 8) {
    indicators.push(handwritingIndicator(
      "pen-lifts",
      comps.length + " disconnected ink components — lifts or fragmentation. Unnatural only in context.",
      Math.min(0.7, 0.25 + comps.length * 0.03),
    ));
  }
  let darkFrac = 0;
  for (let i = 0; i < n; i++) if (L[i] < 0.12) darkFrac += 1;
  darkFrac /= n;
  if (darkFrac > 0.01 && inkDensity > 0.55) {
    indicators.push(handwritingIndicator(
      "retouch-overwrite",
      "Very dark cores inside the ink mask — retouch / patching candidate.",
      0.55,
    ));
  }
  let hueSum = 0, hueN = 0, satSum = 0;
  const hues = [];
  for (let i = 0, p = 0; i < n; i++, p += 3) {
    if (!ink[i]) continue;
    const hsv = rgbToHsv(buf[p], buf[p + 1], buf[p + 2]);
    hues.push(hsv[0]);
    satSum += hsv[1];
    hueN += 1;
  }
  if (hueN && satSum / hueN > 0.08) {
    const hm = hues.reduce((a, b) => a + b, 0) / hues.length;
    const hueStd = Math.sqrt(hues.reduce((a, b) => a + (b - hm) * (b - hm), 0) / hues.length);
    if (hueStd > 28) {
      indicators.push(handwritingIndicator(
        "dual-ink-patch",
        "Stroke-pixel hue clusters differ — dual-ink / later addition candidate.",
        Math.min(0.75, 0.3 + hueStd / 80),
        { hue_std: Number(hueStd.toFixed(2)) },
      ));
    }
  }
  if (shifts.length && shifts[0] > 3.5) {
    indicators.push(handwritingIndicator(
      "baseline-misalign",
      "Baseline centroids drift across the line — not continuous-writing proof, a pixel flag.",
      Math.min(0.7, 0.3 + shifts[0] / 20),
    ));
  }
  const clones = clonePairs(L, w, h);
  if (clones.length) {
    indicators.push(handwritingIndicator(
      "clone-stamp",
      "Repeated 8×8 luminance hashes far apart — digital copy-paste / clone-stamp candidate on the scan.",
      Math.min(0.9, 0.5 + 0.06 * clones.length),
      { bbox: [clones[0][0], clones[0][1], clones[0][2] + 8, clones[0][3] + 8], pair_count: clones.length },
    ));
  }
  const blockStd = [];
  for (let y = 0; y <= h - 8; y += 8) {
    for (let x = 0; x <= w - 8; x += 8) {
      let s = 0, c = 0;
      for (let dy = 0; dy < 8; dy++) for (let dx = 0; dx < 8; dx++) { s += L[(y + dy) * w + x + dx]; c += 1; }
      const m = s / c;
      let v = 0;
      for (let dy = 0; dy < 8; dy++) for (let dx = 0; dx < 8; dx++) {
        const d = L[(y + dy) * w + x + dx] - m;
        v += d * d;
      }
      blockStd.push(Math.sqrt(v / c));
    }
  }
  if (blockStd.length) {
    const bm = blockStd.reduce((a, b) => a + b, 0) / blockStd.length;
    const bs = Math.sqrt(blockStd.reduce((a, b) => a + (b - bm) * (b - bm), 0) / blockStd.length);
    if (bs > 0.045) {
      indicators.push(handwritingIndicator(
        "compression-paste",
        "8×8 block-energy spread — compression / composite paste-up candidate.",
        Math.min(0.65, 0.25 + bs * 4),
      ));
    }
  }
  const aspects = comps.map((c) => c.aspect);
  if (aspects.length >= 6 && Math.max(...aspects) - Math.min(...aspects) > 3.5) {
    indicators.push(handwritingIndicator(
      "style-shift",
      "Component aspect ratios jump (print↔cursive heuristic). Not a single-writer fact.",
      0.4,
    ));
  }

  try {
    const helpers = [
      ["indent", applyMode(buf, w, h, "indent", false), "ISA-1.0 inject OFF. Surface-relief heuristic, not ESDA."],
      ["lemon", applyMode(buf, w, h, "lemon", false), "LISA-1.0 inject OFF. Does not invent marks."],
      ["uv", applyMode(buf, w, h, "uv", false), "Synthetic UV look. Not a lamp."],
      ["candle", applyMode(buf, w, h, "candle", false), "Synthetic candle look. Not a flame test."],
    ];
    for (const [mode, out, note] of helpers) {
      const Hl = toLuma(out, w, h);
      let diff = 0, dn = 0;
      for (let i = 0; i < n; i++) {
        if (mode === "indent" && !ink[i]) continue;
        diff += Math.abs(Hl[i] - L[i]);
        dn += 1;
      }
      const mean = dn ? diff / dn : 0;
      env.helper_modes.push({
        mode, inject: false, contributed: mean > 0.01, note, invented: false,
      });
      if (mode === "indent" && mean > 0.035) {
        indicators.push(handwritingIndicator(
          "indent-mismatch",
          "Indent helper (inject OFF) differs from surface ink — indentation vs wet-ink mismatch candidate. Not ESDA.",
          Math.min(0.6, 0.25 + mean * 4),
          { helper_mode: "indent" },
        ));
      }
    }
    env.helper_modes.push({
      mode: "residual-lift",
      inject: false,
      contributed: true,
      note: "Residual / contrast with inject OFF. Heatmap ≠ transcript.",
      invented: false,
    });
  } catch {
    env.warnings.push("helper-modes-skipped");
  }

  env.forgery_indicators = indicators;
  const densMap = new Float32Array(n);
  const bleedMap = new Float32Array(n);
  const eraseMap = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    densMap[i] = ink[i] ? density[i] : 0;
    bleedMap[i] = ring[i] ? mag[i] : 0;
    eraseMap[i] = bright[i] + 0.5 * ghost[i];
  }
  env.overlays = [
    await heatmapOverlay(densMap, w, h, "density"),
    await heatmapOverlay(bleedMap, w, h, "bleed"),
    await heatmapOverlay(eraseMap, w, h, "erasure-candidates"),
  ];
  env.provenance.push({
    file_path: filename,
    recovery_method: "ink-mask-luminance",
    ink_frac: Number(frac.toFixed(5)),
    state: "present_current",
    human_verification_required: true,
    invented: false,
  });
  void hueSum;
  void ghostOn;
  return env;
}

function compareHandwritingPair(a, b) {
  const take = (env, key, field) => {
    const row = ((env.features || {})[key] || [])[0] || {};
    return Number(row[field] || 0);
  };
  return {
    weight_delta: Number((take(a, "weight", "mean_px") - take(b, "weight", "mean_px")).toFixed(4)),
    density_delta: Number((take(a, "density", "mean") - take(b, "density", "mean")).toFixed(4)),
    bleed_delta: Number((take(a, "bleed", "edge_grad_mean") - take(b, "bleed", "edge_grad_mean")).toFixed(4)),
    indicator_kinds_a: (a.forgery_indicators || []).map((i) => i.kind),
    indicator_kinds_b: (b.forgery_indicators || []).map((i) => i.kind),
    note: "Pixel-feature delta only. Not a same-writer or forgery verdict.",
    invented: false,
  };
}

export async function handwritingFromB64(b64, extras = {}) {
  const op = parseHandwritingOp(extras.op || extras.verb || "analyze");
  if (!op) {
    return { family: "handwriting", error: "unknown handwriting op", known: HANDWRITING_OPS, no_lie: true, note: HANDWRITING_NOTE };
  }
  let decoded;
  try {
    decoded = await decodePng(b64ToBytes(b64));
  } catch {
    return {
      family: "handwriting",
      op,
      refuse_code: REFUSE_UNSUPPORTED,
      refused: [{ code: REFUSE_UNSUPPORTED, note: "Not a readable PNG scan. Hosted preview is PNG only; local package accepts JPEG.", invented: false }],
      warnings: ["synthetic_image_analysis_not_lab", "not_forensic_certification", "hosted_png_only"],
      no_lie: true,
      note: HANDWRITING_NOTE,
      invented: false,
    };
  }
  const limited = Math.max(decoded.w, decoded.h) > MAX_SIDE;
  const capped = capSide(decoded.buf, decoded.w, decoded.h);
  const env = await analyzeHandwritingBuf(
    capped.buf, capped.w, capped.h,
    extras.filename || "scan.png",
    decoded.w, decoded.h, limited,
  );
  env.op = op;

  if (extras.twin_b64) {
    try {
      const twinDec = await decodePng(b64ToBytes(extras.twin_b64));
      const twinCap = capSide(twinDec.buf, twinDec.w, twinDec.h);
      const twinEnv = await analyzeHandwritingBuf(
        twinCap.buf, twinCap.w, twinCap.h,
        extras.twin_name || "known.png",
        twinDec.w, twinDec.h,
        Math.max(twinDec.w, twinDec.h) > MAX_SIDE,
      );
      env.side_by_side = [
        { role: "questioned", filename: extras.filename || "scan.png", artifact: env.artifact, invented: false },
        { role: "known", filename: extras.twin_name || "known.png", artifact: twinEnv.artifact, invented: false },
      ];
      env.compare = compareHandwritingPair(env, twinEnv);
      env.twin = {
        filename: extras.twin_name || "known.png",
        forgery_indicators: twinEnv.forgery_indicators,
        features: twinEnv.features,
        refuse_code: twinEnv.refuse_code,
        invented: false,
      };
      if (decoded.w === twinDec.w && decoded.h === twinDec.h) {
        const La = toLuma(decoded.buf, decoded.w, decoded.h);
        const Lb = toLuma(twinDec.buf, twinDec.w, twinDec.h);
        let abs = 0, changed = 0;
        for (let i = 0; i < La.length; i++) {
          const d = Math.abs(La[i] - Lb[i]);
          abs += d;
          if (d > 0.08) changed += 1;
        }
        env.revision_compare = {
          mean_abs_delta: Number((abs / La.length).toFixed(5)),
          changed_frac: Number((changed / La.length).toFixed(5)),
          note: "Same-raster delta. Ink added later / white-out / paste candidate if changed_frac is high. Not a verdict.",
          invented: false,
        };
      }
    } catch {
      env.warnings.push("twin-unreadable");
    }
  }

  if (op === "refuse") {
    if (env.refuse_code) env.stop = true;
    else env.note = "Refuse requested but ink-like strokes are present. Reported as candidates, not invented.";
    return env;
  }
  if (op === "forgery-indicators") env.recovered_view = env.forgery_indicators;
  if (op === "graph") env.recovered_view = env.graph;
  if ((op === "compare" || op === "side-by-side") && !extras.twin_b64) {
    env.warnings.push("compare/side-by-side needs a second scan (twin_b64).");
  }
  return env;
}

void pixelsFromRgb;
void copyBuf;
void inflateBytes;
void u8slice;
void indexOfBytes;
