"""Hosted overlay.js lists new LIVE modes and resolves aliases."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "workers" / "download-tracker" / "src" / "overlay.js"
INDEX = ROOT / "workers" / "download-tracker" / "src" / "index.js"

LIVE = [
    "zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance",
    "candle", "indent", "lemon",
]
ALIASES = {
    "candlelight": "candle",
    "candle-light": "candle",
    "ultraviolet": "uv",
    "uv-light": "uv",
    "uvsa": "uv",
    "indentation": "indent",
    "suppress-ink": "indent",
    "ink-suppress": "indent",
    "revealer-indent": "indent",
    "lemon-ink": "lemon",
    "hidden-lemon": "lemon",
    "invisible-ink-lemon": "lemon",
}


def test_overlay_js_lists_new_modes_and_aliases() -> None:
    js = OVERLAY.read_text(encoding="utf-8")
    for mode in LIVE:
        assert f'"{mode}"' in js
    for alias, canonical in ALIASES.items():
        assert alias in js
        assert canonical in js
    assert "Ultraviolet light analysis (synthetic)" in js
    assert "CLSA-1.0" in js
    assert "ISA-1.0" in js
    assert "LISA-1.0" in js
    assert "spectrometer" in js and "invent_mark" in js
    assert "electrostatic" in js.lower() or "not electrostatic" in js.lower()
    idx = INDEX.read_text(encoding="utf-8")
    for mode in ("candle", "indent", "lemon"):
        assert mode in idx


def test_overlay_js_resolve_mode_in_node() -> None:
    node = shutil.which("node")
    assert node, "node is required to execute overlay resolveMode"
    script = f"""
import {{ LIVE, ALIASES, MODES, resolveMode, LIMITATION }} from {json.dumps(str(OVERLAY))};
const aliases = {json.dumps(ALIASES)};
const live = {json.dumps(LIVE)};
if (JSON.stringify(LIVE) !== JSON.stringify(live)) throw new Error("LIVE mismatch");
for (const [alias, canonical] of Object.entries(aliases)) {{
  const got = resolveMode(alias);
  if (got !== canonical) throw new Error(alias + " -> " + got);
}}
if (resolveMode("uv").error) throw new Error("uv should be live");
if (resolveMode("spectrometer").error !== "stub") throw new Error("spectrometer stub");
if (!LIMITATION.includes("candle")) throw new Error("limitation missing candle");
if (!MODES.find((m) => m.id === "uv").summary.includes("Ultraviolet light analysis (synthetic)")) {{
  throw new Error("uv summary");
}}
process.stdout.write(JSON.stringify({{ ok: true, live: LIVE, aliases: ALIASES }}));
"""
    raw = subprocess.check_output([node, "--input-type=module", "-e", script], text=True)
    body = json.loads(raw)
    assert body["ok"] is True
    assert body["live"] == LIVE
    assert body["aliases"] == ALIASES


def test_overlay_js_unredact_honesty_in_node() -> None:
    node = shutil.which("node")
    assert node, "node is required to execute overlay unredact helpers"
    script = f"""
import {{ REFUSE_OPAQUE, UNREDACT_NOTE, parseUnredactOp, locatePdfBytes, classifyCoverBuf, listUnredact }} from {json.dumps(str(OVERLAY))};
if (parseUnredactOp("redact-locate") !== "locate") throw new Error("locate alias");
if (parseUnredactOp("leftover-bytes") !== "recover") throw new Error("recover alias");
if (REFUSE_OPAQUE !== "SL-UNREDACT-OPAQUE") throw new Error("refuse code");
if (!UNREDACT_NOTE.includes("leftover")) throw new Error("leftover copy");
if (!UNREDACT_NOTE.includes("not a transcript")) throw new Error("transcript copy");
if (!UNREDACT_NOTE.includes("never invent") && !UNREDACT_NOTE.includes("does not invent")) throw new Error("invent copy");
const card = listUnredact();
if (!card.leftover_bytes_recovery) throw new Error("card leftover");
const enc = new TextEncoder();
const pdf = enc.encode("%PDF-1.4\\n1 0 obj << /Title (Docket) >> endobj\\n4 0 obj << /Length 20 >> stream\\nBT (ALICE SMITH) Tj ET\\nendstream\\nendobj\\n4 0 obj << /Length 8 >> stream\\n0 0 0 rg\\nendstream\\nendobj\\n%%EOF\\n%%EOF\\n");
const loc = locatePdfBytes(pdf);
if (!loc.leftover_bytes) throw new Error("expected leftover");
const previews = (loc.recovered || []).map((r) => r.preview || "").join(" ");
if (!previews.toUpperCase().includes("ALICE")) throw new Error("leftover text missing");
const buf = new Float32Array(32 * 48 * 3);
for (let i = 0; i < buf.length; i++) buf[i] = 0.93;
for (let y = 8; y < 24; y++) for (let x = 6; x < 42; x++) {{
  const p = (y * 48 + x) * 3; buf[p] = buf[p+1] = buf[p+2] = 0;
}}
const cover = classifyCoverBuf(buf, 48, 32);
if (!cover.opaque_replace) throw new Error("opaque box");
process.stdout.write(JSON.stringify({{ ok: true, leftover: loc.leftover_bytes, refuse: REFUSE_OPAQUE }}));
"""
    raw = subprocess.check_output([node, "--input-type=module", "-e", script], text=True)
    body = json.loads(raw)
    assert body["ok"] is True
    assert body["leftover"] is True
    assert body["refuse"] == "SL-UNREDACT-OPAQUE"


def test_overlay_js_inject_and_inband_in_node() -> None:
    node = shutil.which("node")
    assert node, "node is required to execute overlay inject helpers"
    script = f"""
import {{ parseInject, inbandPct, gateInband, INJECT_NOTE, LIMITATION }} from {json.dumps(str(OVERLAY))};
if (parseInject(false) !== false) throw new Error("inject false");
if (parseInject(true) !== true) throw new Error("inject true");
if (parseInject("no-inject") !== false) throw new Error("no-inject");
const buf = new Float32Array(12);
buf.set([0.10, 0.72, 0.62, 0.78, 0.08, 0.42, 0.93, 0.88, 0.76, 0.12, 0.09, 0.06]);
const band = gateInband(buf);
if (typeof band.tazel_inband_pct !== "number") throw new Error("tazel field");
if (typeof band.vyrn_inband_pct !== "number") throw new Error("vyrn field");
if (!INJECT_NOTE.includes("not recovered pigment")) throw new Error("note");
if (!LIMITATION.includes("not recovered pigment")) throw new Error("limitation");
if (inbandPct(new Float32Array([0.93, 0.88, 0.76]), 170, 24) !== 0) throw new Error("empty gate");
process.stdout.write(JSON.stringify({{ ok: true, band }}));
"""
    raw = subprocess.check_output([node, "--input-type=module", "-e", script], text=True)
    body = json.loads(raw)
    assert body["ok"] is True
    assert "tazel_inband_pct" in body["band"]
    assert "vyrn_inband_pct" in body["band"]
