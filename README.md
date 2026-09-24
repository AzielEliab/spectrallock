# SpectralLock

SpectralLock applies a spectral lens to a photograph so faint marks are easier to see.

**Author:** Aziel Eliab  
**License:** [Apache-2.0](LICENSE)  
**Version:** 0.3.1

## Start

1. Install (Python 3.10+):

   ```bash
   python -m venv .venv && source .venv/bin/activate && pip install -e .
   ```

2. Open the local app:

   ```bash
   spectrallock ui
   ```

3. Open http://127.0.0.1:8861 and choose **Add file** (or **Sample page**).

`spectrallock doctor` checks the install. `spectrallock --help` lists commands. Add `--json` when a program should read the result.

Rosetta spectral analysis — the same **SpectralLock lenses** as [Aziel Corpus Library OCR](https://www.azielcorpuslibrary.net/ocr): overlays, ink and page. Balance never invents marks. The human still reads the page. Forks are welcome and always allowed.

Papers: [docs/source/](docs/source/) · spec: [docs/whitepaper.md](docs/whitepaper.md) · runtime sync: [docs/runtime-sync.md](docs/runtime-sync.md)

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
[spectrallock-0.3.1.tar.gz](https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.3.1.tar.gz)

- Live count JSON: [https://spectrallock-download-tracker.vibelock.workers.dev/count](https://spectrallock-download-tracker.vibelock.workers.dev/count) (`{project, views, downloads, total}`)
- Full stats JSON: [https://spectrallock-download-tracker.vibelock.workers.dev/stats](https://spectrallock-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json](https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill](https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill)
- Suite mesh proxy: [https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh](https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh) — default OFF; QNM live / locked / isolated; QNS-CD-1.0 cross-map (photon QNS1 packet transfer; no public qnsd proxy)
- llms.txt: [https://spectrallock-download-tracker.vibelock.workers.dev/llms.txt](https://spectrallock-download-tracker.vibelock.workers.dev/llms.txt)
- ai.txt: [https://spectrallock-download-tracker.vibelock.workers.dev/ai.txt](https://spectrallock-download-tracker.vibelock.workers.dev/ai.txt)
- cite.json: [https://spectrallock-download-tracker.vibelock.workers.dev/cite.json](https://spectrallock-download-tracker.vibelock.workers.dev/cite.json)
- One-click install: [https://spectrallock-download-tracker.vibelock.workers.dev/install.sh](https://spectrallock-download-tracker.vibelock.workers.dev/install.sh)
- GitHub: [https://github.com/AzielEliab/spectrallock](https://github.com/AzielEliab/spectrallock)

Isolated counter: Worker `spectrallock-download-tracker`, KV `SPECTRALLOCK_DOWNLOADS`. SpectralLock only. `/v1` does not increment downloads.


How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Honest scope

v1 is **image processing** (Pillow + numpy) on a photograph you already
have. It reweights hues and contrast so faint marks are easier to *look
at*.

The hosted Worker `/v1/overlay` is a **simplified preview** (longest side
capped at 256 px, PNG in/out). The full pipeline is this Python package.

**Unredact / lift-overlay** locates leftover bytes and residual only.
Never invent letters. Opaque replace with no leftover container
bytes refuses (`SL-UNREDACT-OPAQUE`). Heatmaps are residual overlays.

**Handwriting** is synthetic image analysis of a scan or photo of ink
on paper. Indicators are heuristics — human verification required.

## Lenses (all live in 0.3.1)

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
| `indent` | ISA-1.0 | Ink-suppress / indentation reveal (synthetic). Prefer `page`. Aliases: `indentation`, `suppress-ink`, `ink-suppress`, `revealer-indent`. |
| `lemon` | LISA-1.0 | Hidden lemon ink analysis (synthetic). Heat-/acid-style browning from existing pixels. Never invents marks. Aliases: `lemon-ink`, `hidden-lemon`, `invisible-ink-lemon`. |

Stub (refused): `spectrometer`, `forensic`, `invent_mark`.

## Unredact / lift-overlay (operator lock — NO-LIE)

Family: `unredact` / `lift` / `redact-locate`.
Ops: `locate`, `lift`, `recover`, `refuse`.

| op | honesty |
|----|---------|
| `locate` | Report text still in the PDF, metadata, attachments, twin-page residual, leftover container bytes, and historical page revisions (stale `/Page` graphs, prior streams, xref/ObjStm, after-EOF, incremental `startxref`/`Prev` revision graph + per-revision tip-cut copies). Do not invent letters. |
| `lift` | Non-opaque cover only. Contrast / residual with `--no-inject` (gray of the same gate). Heatmaps are residual overlays. |
| `recover` | If leftover / historical bytes remain (incremental update, unused/orphan objects, prior streams, stale pages, attachments, after-EOF), extract them with character provenance. That is reading present bytes. |
| `refuse` | Opaque sanitized rewrite / flattened screenshot and no leftover bytes → `SL-UNREDACT-OPAQUE`. |

Returns `opaque_replace`, `residual_usable`, `leftover_bytes`, `recovered_from`, `page_revisions`, `revision_compare`, `revision_graph` (revisions + edges + tip-cut `copy` / embeds; hosted may cite sha256+offsets when `b64` is capped), `operator_text`, `classifications`, `recovered_characters` (page, object_id, generation, xref_revision, stream_offset, operator, font, decoded_bytes, source_revision, sha256), `ocr` (after structural only; `covered_letters_from_context` is always false), `refuse_code`. OCR never reconstructs covered letters from context. Never invents letters.

## Handwriting / ink-on-paper (operator lock — NO-LIE)

Family: `handwriting` / `handwrite` / `ink-hand` / `forgery-scan`.
Ops: `analyze`, `compare`, `side-by-side`, `graph`, `forgery-indicators`, `refuse`.

Synthetic image analysis of a user-supplied scan or photo of physical ink on paper. Looks at present pixels only: stroke-weight variation (pressure proxy), speed cues (taper / tremor — heuristic), ink density, bleed / feathering, baseline / slant / size shifts, erasures, tracing evidence, and forgery indicators (tremor-copy, unnatural lifts, retouch, dual-ink, clone-stamp, compression paste-up, ductus, style-shift). Side-by-side questioned vs known. Stroke/feature graph flags anomalous edges. Density / bleed / erasure heatmaps are residual overlays.

| honesty | meaning |
|---------|---------|
| LIVE | pixel heuristics listed in `docs/audit/HANDWRITING-FORGERY-AUDIT.md` |
| SLOT | ESDA, chemical ink dating, force in newtons, speed in mm/s, writer identity as fact, court examiner opinion |
| refuse | `SL-HANDWRITING-NO-INK` · `SL-HANDWRITING-UNSUPPORTED` · `SL-HANDWRITING-LIMIT` |

Phrasing: **indicator / heuristic / candidate — human verification required.** Confidence is signal quality from pixels, not “this is forged.” Spectral helpers (`uv`, `candle`, `indent`, `lemon`) may be cited with inject OFF. Balance / lemon never invent marks.

```bash
spectrallock unredact locate page.pdf --json
spectrallock unredact recover page.pdf --json
spectrallock recover locate page.pdf --json
spectrallock recover deep file.docx --all-metadata --scan-orphans --json
spectrallock recover compare old.json new.json --json
spectrallock recover revision-graph page.pdf --json
spectrallock handwriting analyze ink_scan.png --json
spectrallock handwriting compare questioned.png --twin known.png --json
spectrallock forgery-scan ink_scan.png --json
spectrallock pigment restore page.png --json
spectrallock restore-pigment page.png -o restored.png --json
spectrallock lift cover.png --no-inject -o residual.png --json
spectrallock redact-locate page.pdf --twin page_less.pdf --query "Alice"
```

## Restore lost pigment (operator lock 2026-09-22 — NO-LIE)

Family: `pigment` / `restore-pigment`.
Ops: `restore`, `estimate`, `refuse`.

LIVE on SpectralLock (CLI, local UI, Worker `GET|POST /v1/pigment`, alias `POST /v1/restore-pigment`). Estimates faded pigment where pixels still differ from the page in a supported cluster. Visible dark ink stays already-present pigment. When the faded signal is gone the op refuses `SL-PIGMENT-GONE` and writes no new marks. Receipts set `pigment_recovery` true only when this path ran. Overlay and unredact receipts keep `pigment_recovery` false. Wheel paint is a separate plane from this estimate.

```bash
spectrallock pigment restore page.png -o restored.png --json
spectrallock pigment estimate page.png --json
spectrallock restore-pigment page.png --json
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
| **ON** (`--inject`) | False-color membership tint (paint). |
| **OFF** (`--no-inject`) | Luminance of the **same gate** (gray). |
| `zero` | Ignores the switch (stays gray either way). |

- In-band spectral math stays tazel 170° `#1EC9A5`, vyrn 350° `#C00066`, zero `#6F6485`.
- Membership paint (Spectral Harmonic Wheel, operator lock 2026-09-22): ZERO `#325767`, CHAOS `#8D223D`, VYRN `#A22639`, UV `#9F3B2B`, TAZEL `#797A2D`, ROSETTA `#467542`, ZEN `#DFD2B5`. Source: `docs/source/color-wheel-paint.txt`.
- `uv`: synthetic 365–400 look (violet parchment / residual) from an ordinary photograph.
- `rosetta` / `zen` / `chaos` / `balance`: composite tint when ON; gray gate when OFF. Balance never invents marks.
- `candle` / `indent` / `lemon`: honest ON tint vs OFF gray of the same gate.

Overlay and verify JSON report **`tazel_inband_pct`** and **`vyrn_inband_pct`**
before any hit claim. An empty gate is a valid reading. Copy-of-copy only works if
the hue is still in-band.

```bash
python3 spectrallock_inject.py page.jpg --mode vyrn --inject -o vyrn_on.jpg
python3 spectrallock_inject.py page.jpg --mode vyrn --no-inject -o vyrn_off.jpg
python3 spectrallock_inject.py page.jpg --all --inject --outdir out/
python3 spectrallock_inject.py page.jpg --all --no-inject --outdir out_plain/
python3 spectrallock_inject.py page.jpg --mode zero --target ink --no-inject
```

Hosted `/v1/overlay` may accept `inject` on a 256 px PNG preview. Prefer the
local package (`spectrallock_inject.py`) for the full pipeline.

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
spectrallock
spectrallock --help
spectrallock ui
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
spectrallock recover locate page.pdf --json
spectrallock recover production ./case_folder --recursive --json
spectrallock handwriting analyze ink_scan.png --json
spectrallock handwriting compare questioned.png known.png --json
spectrallock pigment restore page.png --json
spectrallock restore-pigment page.png -o restored.png --json
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
Offline color-matrix approximation of the hues. The full Python pipeline is this package.
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
- Overlay: `POST /v1/overlay` `{b64, mode|lens|lenses, target, inject}` — PNG, max 256 px longest side. `inject` true\|false is paint (false-color membership). Mode aliases (`ultraviolet`, `candlelight`, `ink-suppress`, `hidden-lemon`, …) resolve to canonical ids. Does **not** increment the download counter.
- Unredact: `GET /v1/unredact` honesty banner; `POST /v1/unredact` `{b64, op, query, twin_b64?}` locate / leftover-historical recover / residual lift. Returns `revision_graph` (startxref/Prev edges + per-revision tip-cut copies). Opaque rewrite + no leftover → `SL-UNREDACT-OPAQUE`. Aliases `POST /v1/lift`, `POST /v1/redact-locate`. Hosted preview may cap size / copy `b64` (sha256+offset cites, no invented bytes) and has no OCR engine — it does not lie about that. Never invents letters.
- Recover: `GET /v1/recover` ops + LIVE vs SLOT matrix; `POST /v1/recover` `{b64, op, filename, twin_b64?}` universal artifact recovery. Present bytes only. Secrets suppressed. SLOT stays SLOT; LIVE stays LIVE. Audit: `docs/audit/UNIVERSAL-RECOVER-AUDIT.md`.
- Handwriting: `GET /v1/handwriting` ops + LIVE vs SLOT features; `POST /v1/handwriting` `{b64, op, filename, twin_b64?}` synthetic ink-on-paper scan heuristics. Hosted 256 px PNG preview. Audit: `docs/audit/HANDWRITING-FORGERY-AUDIT.md`.
- Suite mesh: `GET /v1/mesh` PROXY to aziel-runtime (default OFF; QNM-BUILD-1.0 live|locked|isolated; QNS-CD-1.0 hub cite / Worker mesh cross-map only — photon QNS1 packet transfer; local qnsd in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); no Node Gate; no public qnsd proxy)
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
Suite mesh `/v1/mesh/*` PROXY via `AZIEL_RUNTIME` (default OFF; QNM-BUILD-1.0 live|locked|isolated; QNS-CD-1.0 hub cite / Worker mesh cross-map only; no Node Gate; no public qnsd proxy). Catalog MCP `mesh_*` + FragGate `slug=mesh`. Local qnsd lives in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). AZInterface holds pair custody.

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
