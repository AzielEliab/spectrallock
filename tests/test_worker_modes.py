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
