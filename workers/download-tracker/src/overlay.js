/**
 * Simplified SpectralLock overlay for the hosted Worker.
 * Full histogram / band-pass / unsharp lives in the Python package.
 * PNG 8-bit RGB/RGBA, longest side capped at 256. Advisory only.
 */
export const LIMITATION =
  "Advisory digital overlays on photographs of manuscript pages. " +
  "Not a lab spectrometer, not real UV photography hardware, not a " +
  "forensic proof of hidden ink, not OCR, and not a claim of scribal truth. " +
  "Synthetic UV simulates a 365–400 nm look from an ordinary photo. " +
  "Balance never invents marks. Hosted overlay is a simplified preview " +
  "(max 256 px); the full pipeline is the Python package. The human still reads the page.";

export const VERSION = "0.1.0";
export const MAX_SIDE = 256;
export const LIVE = ["zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance"];

export const MODES = [
  { id: "zero", paper: "ZSA-1.0", status: "live", summary: "Equilibrium / geometry (simplified grayscale stretch)." },
  { id: "tazel", paper: "TSA-1.0", status: "live", summary: "Boost green–gold–turquoise (~170°, #1EC9A5)." },
  { id: "vyrn", paper: "VSA-1.0", status: "live", summary: "Boost magenta–red-violet (~350°, #C00066)." },
  { id: "uv", paper: "UVSA-1.0", status: "live", summary: "Synthetic 365–400 nm simulation. Not a real UV lamp." },
  { id: "rosetta", paper: "RSA-2.0", status: "live", summary: "0.40·Z′ + 0.35·T′ + 0.25·V′ after normalize." },
  { id: "zen", paper: "ZENA-1.0", status: "live", summary: "(Z′ + T′ + U′ + V′) / 4 after normalize." },
  { id: "chaos", paper: "CSA-1.0", status: "live", summary: "0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′ after normalize." },
  { id: "balance", paper: "BSA", status: "live", summary: "α·Zen + (1-α)·Chaos. Never invents marks." },
];

const ROSETTA_W = { zero: 0.4, tazel: 0.35, vyrn: 0.25 };
const ZEN_W = { zero: 0.25, tazel: 0.25, uv: 0.25, vyrn: 0.25 };
const CHAOS_W = { uv: 0.4, vyrn: 0.35, tazel: 0.2, zero: 0.05 };
const EPS = 1e-6;

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

function applyMode(buf, w, h, mode) {
  if (mode === "zero") return modeZero(buf);
  if (mode === "tazel") return modeTazel(buf);
  if (mode === "vyrn") return modeVyrn(buf);
  if (mode === "uv") return modeUv(buf);
  const ch = baseChannels(buf, w, h);
  if (mode === "rosetta") return grayToRgb(mixLuma(ch, ROSETTA_W));
  if (mode === "zen") return grayToRgb(mixLuma(ch, ZEN_W));
  if (mode === "chaos") return grayToRgb(mixLuma(ch, CHAOS_W));
  if (mode === "balance") {
    const zen = grayToRgb(mixLuma(ch, ZEN_W));
    const chaos = grayToRgb(mixLuma(ch, CHAOS_W));
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
    return out;
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

export async function overlayFromB64(b64, mode) {
  const key = String(mode || "").trim().toLowerCase();
  if (!LIVE.includes(key)) {
    return { error: "unknown mode", known: LIVE, advisory: LIMITATION };
  }
  let decoded;
  try {
    decoded = await decodePng(b64ToBytes(b64));
  } catch (err) {
    return { error: "PNG decode failed (hosted preview is PNG only): " + String(err.message || err), advisory: LIMITATION };
  }
  const capped = capSide(decoded.buf, decoded.w, decoded.h);
  const out = applyMode(capped.buf, capped.w, capped.h, key);
  const png = await encodePng(out, capped.w, capped.h);
  const com = centerOfMass(out, capped.w, capped.h);
  return {
    mode: key,
    paper: (MODES.find((m) => m.id === key) || {}).paper,
    width: capped.w,
    height: capped.h,
    com,
    png_b64: bytesToB64(png),
    simplified: true,
    max_side: MAX_SIDE,
    product: "spectrallock",
    version: VERSION,
    advisory: LIMITATION,
  };
}

void pixelsFromRgb;
void copyBuf;
