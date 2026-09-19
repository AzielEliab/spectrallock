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
import {{ REFUSE_OPAQUE, UNREDACT_NOTE, parseUnredactOp, locatePdfBytes, locatePdfHistory, classifyCoverBuf, listUnredact, listRecover, DEEP_CAPABILITIES, unredactFromB64, recoverFromB64, parseRecoverOp }} from {json.dumps(str(OVERLAY))};
if (parseUnredactOp("redact-locate") !== "locate") throw new Error("locate alias");
if (parseUnredactOp("leftover-bytes") !== "recover") throw new Error("recover alias");
if (REFUSE_OPAQUE !== "SL-UNREDACT-OPAQUE") throw new Error("refuse code");
if (!UNREDACT_NOTE.includes("leftover")) throw new Error("leftover copy");
if (!UNREDACT_NOTE.includes("not a transcript")) throw new Error("transcript copy");
if (!UNREDACT_NOTE.includes("never invent") && !UNREDACT_NOTE.includes("does not invent")) throw new Error("invent copy");
if (!UNREDACT_NOTE.includes("OCR")) throw new Error("ocr copy");
const card = listUnredact();
if (!card.leftover_bytes_recovery) throw new Error("card leftover");
if (!card.deep_history) throw new Error("card deep");
if (card.capabilities.length !== 14) throw new Error("14 caps");
if (DEEP_CAPABILITIES.length !== 14) throw new Error("DEEP 14");
if (!card.revision_graph || !card.revision_copies) throw new Error("card graph");
const recCard = listRecover();
if (!recCard.no_lie || recCard.guessed_letters) throw new Error("recover card");
if (parseRecoverOp("deep") !== "deep-recover") throw new Error("recover alias");
if (!recCard.slot_kinds.includes("heic")) throw new Error("heic slot");
const enc = new TextEncoder();
const pdf = enc.encode("%PDF-1.4\\n1 0 obj << /Title (Docket) >> endobj\\n4 0 obj << /Length 20 >> stream\\nBT (ALICE SMITH) Tj ET\\nendstream\\nendobj\\n4 0 obj << /Length 8 >> stream\\n0 0 0 rg\\nendstream\\nendobj\\n%%EOF\\n%%EOF\\n");
const loc = locatePdfBytes(pdf);
if (!loc.leftover_bytes) throw new Error("expected leftover");
const previews = (loc.recovered || []).map((r) => r.preview || "").join(" ");
if (!previews.toUpperCase().includes("ALICE")) throw new Error("leftover text missing");
const efta = enc.encode("%PDF-1.4\\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\\n2 0 obj << /Type /Pages /Kids [10 0 R] /Count 1 >> endobj\\n10 0 obj << /Type /Page /Contents 90 0 R >> endobj\\n90 0 obj << /Length 8 >> stream\\n0 0 0 rg f\\nendstream\\nendobj\\n23 0 obj << /Length 22 >> stream\\nBT (STALE-STREAM-23) Tj ET\\nendstream\\nendobj\\n77 0 obj << /Type /Page /Contents 23 0 R >> endobj\\n%%EOF\\n");
const hist = await locatePdfHistory(efta);
if (!hist.leftover_bytes) throw new Error("efta leftover");
const stale = (hist.page_revisions || []).find((p) => p.page_object.startsWith("77"));
if (!stale || !stale.leftover) throw new Error("stale page 77");
const texts = (hist.operator_text || []).map((s) => s.text || "").join(" ");
if (!texts.includes("STALE-STREAM-23")) throw new Error("stale stream follow");
if (hist.ocr.covered_letters_from_context) throw new Error("ocr context");
const opaque = enc.encode("%PDF-1.4\\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\\n2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\\n3 0 obj << /Type /Page /Contents 4 0 R >> endobj\\n4 0 obj << /Length 8 >> stream\\n0 0 0 rg f\\nendstream\\nendobj\\n%%EOF\\n");
const toB64 = (u8) => Buffer.from(u8).toString("base64");
const refused = await unredactFromB64(toB64(opaque), {{ op: "recover" }});
if (refused.leftover_bytes) throw new Error("opaque leftover");
if (refused.refuse_code !== "SL-UNREDACT-OPAQUE") throw new Error("opaque refuse");
const twin = await unredactFromB64(toB64(efta), {{ op: "locate", twin_b64: toB64(opaque) }});
if (!twin.twin_diff || twin.twin_diff.invented) throw new Error("twin");
function xrefRow(offset, gen = 0, used = true) {{
  const flag = used ? "n" : "f";
  return String(offset).padStart(10, "0") + " " + String(gen).padStart(5, "0") + " " + flag + " \\n";
}}
function wrap(n, body) {{ return n + " 0 obj\\n" + body + "\\nendobj\\n"; }}
function assemble(objs) {{
  const parts = ["%PDF-1.4\\n"];
  const offsets = {{}};
  for (const [n, body] of objs) {{
    offsets[n] = parts.reduce((a, p) => a + p.length, 0);
    parts.push(wrap(n, body));
  }}
  const xrefAt = parts.reduce((a, p) => a + p.length, 0);
  const maxId = Math.max(...objs.map(([n]) => n));
  let xref = "xref\\n0 " + (maxId + 1) + "\\n" + xrefRow(0, 65535, false);
  for (let i = 1; i <= maxId; i++) xref += offsets[i] != null ? xrefRow(offsets[i]) : xrefRow(0, 0, false);
  parts.push(xref);
  parts.push("trailer << /Size " + (maxId + 1) + " /Root 1 0 R >>\\nstartxref\\n" + xrefAt + "\\n%%EOF\\n");
  return parts.join("");
}}
const first = assemble([
  [1, "<< /Type /Catalog /Pages 2 0 R >>"],
  [2, "<< /Type /Pages /Kids [3 0 R] /Count 1 >>"],
  [3, "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>"],
  [4, "<< /Length 42 >>\\nstream\\nBT /F1 12 Tf 10 100 Td (ALICE SMITH) Tj ET\\nendstream"],
]);
const prev = first.match(/startxref\\s+(\\d+)/)[1];
const tailObj = wrap(4, "<< /Length 19 >>\\nstream\\n0 0 0 rg 10 80 120 24 re f\\nendstream");
const xrefAt2 = first.length + tailObj.length;
const inc = enc.encode(first + tailObj + "xref\\n4 1\\n" + xrefRow(first.length) + "trailer << /Size 6 /Root 1 0 R /Prev " + prev + " >>\\nstartxref\\n" + xrefAt2 + "\\n%%EOF\\n");
const graphHist = await locatePdfHistory(inc);
if (!graphHist.revision_graph || graphHist.revision_graph.revisions.length !== 2) throw new Error("graph revs " + ((graphHist.revision_graph || {{}}).revisions || []).length);
if (graphHist.revision_graph.edges.length !== 1) throw new Error("graph edges");
if (!graphHist.revision_graph.edges[0].replaced.some((r) => r.id === 4)) throw new Error("obj 4 replaced");
const c0 = graphHist.revision_graph.revisions[0].copy;
const c1 = graphHist.revision_graph.revisions[1].copy;
if (c0.invented || c1.invented) throw new Error("invented copy");
if (!c0.sha256 || !c1.sha256 || c0.sha256 === c1.sha256) throw new Error("copy hashes");
if (c0.b64) {{
  const raw0 = Buffer.from(c0.b64, "base64");
  const {{ createHash }} = await import("node:crypto");
  if (createHash("sha256").update(raw0).digest("hex") !== c0.sha256) throw new Error("copy hash mismatch");
  if (!Buffer.from(raw0).includes("ALICE SMITH") && !raw0.toString("latin1").includes("ALICE SMITH")) throw new Error("rev0 missing ALICE");
}}
const buf = new Float32Array(32 * 48 * 3);
for (let i = 0; i < buf.length; i++) buf[i] = 0.93;
for (let y = 8; y < 24; y++) for (let x = 6; x < 42; x++) {{
  const p = (y * 48 + x) * 3; buf[p] = buf[p+1] = buf[p+2] = 0;
}}
const cover = classifyCoverBuf(buf, 48, 32);
if (!cover.opaque_replace) throw new Error("opaque box");
process.stdout.write(JSON.stringify({{ ok: true, leftover: loc.leftover_bytes, refuse: REFUSE_OPAQUE, stale: true }}));
"""
    raw = subprocess.check_output([node, "--input-type=module", "-e", script], text=True)
    body = json.loads(raw)
    assert body["ok"] is True
    assert body["leftover"] is True
    assert body["refuse"] == "SL-UNREDACT-OPAQUE"
    assert body["stale"] is True


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
