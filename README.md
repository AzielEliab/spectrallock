# SpectralLock

**Rosetta spectral analysis** software (RSA-2.0 family).

Same **SpectralLock lenses** as [Aziel Corpus Library OCR](https://www.azielcorpuslibrary.net/ocr):
overlays plus ink/page targets.

**Author:** Aziel Eliab
**Date:** 2026
**License:** [Apache-2.0](LICENSE)
**Version:** 0.3.0

> The human still reads the page.

RSA-2.0 is the decoding composite `0.40·Z′ + 0.35·T′ + 0.25·V′`. Ink isolates
writing; page isolates parchment. Balance never invents marks — it only
reweights existing readings. Synthetic UV is a 365–400 nm look from an
ordinary photograph. Candlelight, indent, and lemon are synthetic looks
from ordinary photos (not a lab instrument, not forensic certification).
Hosted `/v1/overlay` is a 256 px preview; the full pipeline is this
Python package.

**Forks are welcome and always allowed.**


## One-click install

```bash
curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `spectrallock ui`.

Or tap **Download** / **One-click install** on the Worker homepage
(a 6th-grader can tap it):
https://spectrallock-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

# → [https://spectrallock-download-tracker.vibelock.workers.dev/](https://spectrallock-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted):
[spectrallock-0.3.0.tar.gz](https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.3.0.tar.gz)

- Live count JSON: [https://spectrallock-download-tracker.vibelock.workers.dev/count](https://spectrallock-download-tracker.vibelock.workers.dev/count) (`{project, views, downloads, total}`)
- Full stats JSON: [https://spectrallock-download-tracker.vibelock.workers.dev/stats](https://spectrallock-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json](https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill](https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill)
- Suite mesh proxy: [https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh](https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh) — default OFF; QNM live / locked / isolated; QNS-CD-1.0 cross-map (photon QNS1 packet transfer; not a Softwares-tab product; no public qnsd proxy)
- One-click install: [https://spectrallock-download-tracker.vibelock.workers.dev/install.sh](https://spectrallock-download-tracker.vibelock.workers.dev/install.sh)
- GitHub: [https://github.com/AzielEliab/spectrallock](https://github.com/AzielEliab/spectrallock)

Isolated counter: Worker `spectrallock-download-tracker`, KV `SPECTRALLOCK_DOWNLOADS`. Not mixed with any other product. `/v1` does not increment downloads.


## Quick start

1. Install (Python 3.10+):

   ```bash
   python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
   ```

2. Open the local app:

   ```bash
   spectrallock ui
   ```

3. In the browser at http://127.0.0.1:8861 (loopback only): tap **Add file**
   (or **Sample page**), pick SpectralLock lenses, choose **Ink** or **Page**,
   then **Export**. Optional: **Verify** shows a receipt (lenses, target,
   paper, SHA-256 in/out, size). No CDN, no telemetry. Dark gold.

Counted download: [https://spectrallock-download-tracker.vibelock.workers.dev/](https://spectrallock-download-tracker.vibelock.workers.dev/)

Direct tarball: [spectrallock-0.3.0.tar.gz](https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.3.0.tar.gz)

Papers: [docs/source/](docs/source/) · spec: [docs/whitepaper.md](docs/whitepaper.md) ·
runtime sync: [docs/runtime-sync.md](docs/runtime-sync.md)

How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Honest scope

v1 is **image processing** (Pillow + numpy) on a photograph you already
have. It reweights hues and contrast so faint marks are easier to *look
at*. It does not recover lost ink, date a page, identify a scribe, or
stand in for a conservator.

The hosted Worker `/v1/overlay` is a **simplified preview** (longest side
capped at 256 px, PNG in/out). The full pipeline is this Python package.

**Unredact / lift-overlay** locates leftover bytes and residual only.
It does not invent letters. Opaque replace with no leftover container
bytes refuses (`SL-UNREDACT-OPAQUE`). A heatmap is not a transcript.

## Lenses (all live in 0.3.0)

Same names as the Corpus OCR SpectralLock lens checkboxes, plus candle /
indent / lemon synthetic looks. Aliases resolve to the canonical id.

| id | paper | formula / action |
|----|-------|------------------|
| `zero` | ZSA-1.0 | Grayscale, hist-eq, band-pass, unsharp. Hue ~260°, `#6F6485`. |
| `tazel` | TSA-1.0 | Boost green–gold–turquoise (~170°, `#1EC9A5`). Lift faint midtones. |
| `vyrn` | VSA-1.0 | Boost magenta–red-violet (~350°, `#C00066`). Suppress green/cyan. |
| `uv` | UVSA-1.0 | Ultraviolet light analysis (synthetic). 365–400 nm look. Aliases: `ultraviolet`, `uv-light`, `uvsa`. |
| `rosetta` | RSA-2.0 | `0.40·Z′ + 0.35·T′ + 0.25·V′` after per-channel normalize. |
| `zen` | ZENA-1.0 | `(Z′ + T′ + U′ + V′) / 4` after normalize. |
| `chaos` | CSA-1.0 | `0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′` after normalize. |
| `balance` | BSA | `B=(Zn−Cn)/(Zn+Cn+ε)`, `α=(1+B)/2`, `RGB = α·Zen + (1−α)·Chaos`. Never invents marks. |
| `candle` | CLSA-1.0 | Candlelight analysis (synthetic). Amber ~1800–2700K flame-side look. Aliases: `candlelight`, `candle-light`. |
| `indent` | ISA-1.0 | Ink-suppress / indentation reveal (synthetic). Prefer `page`. Not ESDA. Aliases: `indentation`, `suppress-ink`, `ink-suppress`, `revealer-indent`. |
| `lemon` | LISA-1.0 | Hidden lemon ink analysis (synthetic). Heat-/acid-style browning from existing pixels. Never invents marks. Aliases: `lemon-ink`, `hidden-lemon`, `invisible-ink-lemon`. |

Stub (refused): `spectrometer`, `forensic`, `invent_mark`.

## Unredact / lift-overlay (operator lock — NO-LIE)

Not a spectral lens. Family: `unredact` / `lift` / `redact-locate`.
Ops: `locate`, `lift`, `recover`, `refuse`.

| op | honesty |
|----|---------|
| `locate` | Report text still in the PDF, metadata, attachments, twin-page residual, leftover container bytes, and historical page revisions (stale `/Page` graphs, prior streams, xref/ObjStm, after-EOF, incremental `startxref`/`Prev` revision graph + per-revision tip-cut copies). Do not invent letters. |
| `lift` | Non-opaque cover only. Contrast / residual with `--no-inject` (gray of the same gate). Heatmap ≠ transcript. |
| `recover` | If leftover / historical bytes remain (incremental update, unused/orphan objects, prior streams, stale pages, attachments, after-EOF), extract them with character provenance. That is reading present bytes — not guessing a black box. |
| `refuse` | Opaque sanitized rewrite / flattened screenshot and no leftover bytes → `SL-UNREDACT-OPAQUE`. |

Returns `opaque_replace`, `residual_usable`, `leftover_bytes`, `recovered_from`, `page_revisions`, `revision_compare`, `revision_graph` (revisions + edges + tip-cut `copy` / embeds; hosted may cite sha256+offsets when `b64` is capped), `operator_text`, `classifications`, `recovered_characters` (page, object_id, generation, xref_revision, stream_offset, operator, font, decoded_bytes, source_revision, sha256), `ocr` (after structural only; `covered_letters_from_context` is always false), `refuse_code`. OCR never reconstructs covered letters from context. Never claim pigment recovery, ESDA, chemical, lab, or forensic certification.

```bash
spectrallock unredact locate page.pdf --json
spectrallock unredact recover page.pdf --json
spectrallock lift cover.png --no-inject -o residual.png --json
spectrallock redact-locate page.pdf --twin page_less.pdf --query "Alice"
```

## Ink / page targets

Same polarity as Corpus OCR ink/page modes. Applied after the lens overlay.
Reweights existing pixels only.

| id | action |
|----|--------|
| `ink` | Isolate writing: crush parchment, keep strokes. Default. |
| `page` | Isolate substrate: lift parchment, wash ink. |

Several lenses may be selected (Corpus OCR checkbox family). They are mixed
equally, then the target is applied.

## Color inject switch (19 Sep 2026)

Each named mode accepts `--inject` / `--no-inject` (CLI, Python `inject=`,
Worker `POST /v1/overlay` `{inject: true|false}`).

| switch | meaning |
|--------|---------|
| **ON** (`--inject`) | False-color membership tint (paint). **Not** recovered pigment. |
| **OFF** (`--no-inject`) | Luminance of the **same gate** (gray). |
| `zero` | Ignores the switch (stays gray either way). |

- `tazel`: 170° `#1EC9A5` teal heat on in-band pixels when ON.
- `vyrn`: 350° `#C00066` magenta heat on in-band pixels when ON.
- `uv`: synthetic 365–400 look (violet parchment / residual) — still not a lamp.
- `rosetta` / `zen` / `chaos` / `balance`: composite tint when ON; gray gate when OFF. Balance does not invent marks.
- `candle` / `indent` / `lemon`: honest ON tint vs OFF gray of the same gate.

Overlay and verify JSON report **`tazel_inband_pct`** and **`vyrn_inband_pct`**
before any hit claim. Empty gate ≠ broken lens. Copy-of-copy only works if
the hue is still in-band.

```bash
python3 spectrallock_inject.py page.jpg --mode vyrn --inject -o vyrn_on.jpg
python3 spectrallock_inject.py page.jpg --mode vyrn --no-inject -o vyrn_off.jpg
python3 spectrallock_inject.py page.jpg --all --inject --outdir out/
python3 spectrallock_inject.py page.jpg --all --no-inject --outdir out_plain/
python3 spectrallock_inject.py page.jpg --mode zero --target ink --no-inject
```

Hosted `/v1/overlay` may accept `inject` on a 256 px PNG preview. Prefer the
local package (`spectrallock_inject.py`) for the full pipeline. The Worker
does not claim pigment recovery.

## Install

Python 3.10+. Pillow + numpy. No OpenCV.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

## CLI

```bash
spectrallock version
spectrallock doctor
spectrallock modes
spectrallock lenses
spectrallock overlay --mode zero|tazel|vyrn|uv|rosetta|zen|chaos|balance|candle|indent|lemon --target ink|page --inject|--no-inject IN.png OUT.png
spectrallock overlay --lens tazel --target page --no-inject page.jpg out.png --json
spectrallock overlay --mode tazel page.jpg out.png --verify --sidecar
spectrallock inject page.jpg --mode vyrn --inject -o vyrn_on.jpg
spectrallock unredact locate page.pdf --json
spectrallock unredact recover page.pdf --json
spectrallock lift cover.png --no-inject -o residual.png --json
spectrallock redact-locate page.pdf --twin other.pdf --query Alice
spectrallock ui          # 127.0.0.1:8861
spectrallock serve       # alias for ui
```

PNG or JPEG in. `--verify` prints lenses, target, paper, sha256 in/out, size.
`--sidecar` writes a JSON next to the overlay PNG.
`SPECTRALLOCK_DEBUG=1` traces to stderr (never image bytes).

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.spectrallock`.
Offline color-matrix approximation of the hues. Not the full Python pipeline.
**Add file** + **Export**.

```bash
cd mobile
flutter create --org com.azieeliab --project-name spectrallock .
flutter pub get
flutter run
```

## Hosted preview

- OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Health: `GET /v1/health`
- Lenses: `GET /v1/lenses` (alias `GET /v1/modes`)
- Targets: `GET /v1/targets`
- Overlay: `POST /v1/overlay` `{b64, mode|lens|lenses, target, inject}` — PNG, max 256 px longest side. `inject` true\|false is paint, not pigment. Mode aliases (`ultraviolet`, `candlelight`, `ink-suppress`, `hidden-lemon`, …) resolve to canonical ids. Does **not** increment the download counter.
- Unredact: `GET /v1/unredact` honesty banner; `POST /v1/unredact` `{b64, op, query, twin_b64?}` locate / leftover-historical recover / residual lift. Returns `revision_graph` (startxref/Prev edges + per-revision tip-cut copies). Opaque rewrite + no leftover → `SL-UNREDACT-OPAQUE`. Aliases `POST /v1/lift`, `POST /v1/redact-locate`. Hosted preview may cap size / copy `b64` (sha256+offset cites, no invented bytes) and has no OCR engine — it does not lie about that. Never invents letters.
- Suite mesh: `GET /v1/mesh` PROXY to aziel-runtime (default OFF; QNM-BUILD-1.0 live|locked|isolated; QNS-CD-1.0 hub cite / Worker mesh cross-map only — photon QNS1 packet transfer; local qnsd in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); no Node Gate; no public qnsd proxy; not a Softwares-tab product)
- AI help: https://spectrallock-download-tracker.vibelock.workers.dev/ai
- Catalog: https://aziel-runtime.vibelock.workers.dev/ (MCP tools `spectrallock_modes`, `spectrallock_overlay`; catalog `mesh_*` + FragGate `slug=mesh`)
- Corpus OCR: https://www.azielcorpuslibrary.net/ocr

Isolated counter: Worker `spectrallock-download-tracker`, project `spectrallock`,
KV `SPECTRALLOCK_DOWNLOADS`. `totalKey` `spectrallock|__total__`. `/download`
serves gzip from Worker assets (`private, no-store`). No 302 to GitHub.

## Use with ChatGPT, Grok, Venice, Claude, Cursor, and other MCP/OpenAPI-capable assistants

Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
This Worker skill: https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill
This Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
Suite mesh `/v1/mesh/*` PROXY via `AZIEL_RUNTIME` (default OFF; QNM-BUILD-1.0 live|locked|isolated; QNS-CD-1.0 hub cite / Worker mesh cross-map only; no Node Gate; no public qnsd proxy). Catalog MCP `mesh_*` + FragGate `slug=mesh`. Local qnsd lives in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). AZInterface holds pair custody. Not a Softwares-tab product.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a custom tool, GPT Action (no auth), HTTP tool, or MCP connector. Always send `User-Agent: Mozilla/5.0`.

## Cite this

Aziel Eliab. SpectralLock. https://github.com/AzielEliab/spectrallock. https://spectrallock-download-tracker.vibelock.workers.dev.

- Catalog: https://aziel-runtime.vibelock.workers.dev/
- Worker homepage: https://spectrallock-download-tracker.vibelock.workers.dev/
- Counted download (gzip HTTP 200, no 302): https://spectrallock-download-tracker.vibelock.workers.dev/download
- GitHub: https://github.com/AzielEliab/spectrallock
- Citation JSON: https://spectrallock-download-tracker.vibelock.workers.dev/cite.json

## License

Apache License 2.0. Copyright 2026 Aziel Eliab.
