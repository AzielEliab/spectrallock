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
ordinary photograph. Hosted `/v1/overlay` is a 256 px preview; the full
pipeline is this Python package.

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

- Live count JSON: [https://spectrallock-download-tracker.vibelock.workers.dev/stats](https://spectrallock-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json](https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill](https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill)
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

Papers: [docs/source/](docs/source/) · spec: [docs/whitepaper.md](docs/whitepaper.md)

How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Honest scope

v1 is **image processing** (Pillow + numpy) on a photograph you already
have. It reweights hues and contrast so faint marks are easier to *look
at*. It does not recover lost ink, date a page, identify a scribe, or
stand in for a conservator.

The hosted Worker `/v1/overlay` is a **simplified preview** (longest side
capped at 256 px, PNG in/out). The full pipeline is this Python package.

## Lenses (all live in 0.3.0)

Same names as the Corpus OCR SpectralLock lens checkboxes.

| id | paper | formula / action |
|----|-------|------------------|
| `zero` | ZSA-1.0 | Grayscale, hist-eq, band-pass, unsharp. Hue ~260°, `#6F6485`. |
| `tazel` | TSA-1.0 | Boost green–gold–turquoise (~170°, `#1EC9A5`). Lift faint midtones. |
| `vyrn` | VSA-1.0 | Boost magenta–red-violet (~350°, `#C00066`). Suppress green/cyan. |
| `uv` | UVSA-1.0 | Synthetic 365–400 nm simulation. Parchment glow, ink darker. |
| `rosetta` | RSA-2.0 | `0.40·Z′ + 0.35·T′ + 0.25·V′` after per-channel normalize. |
| `zen` | ZENA-1.0 | `(Z′ + T′ + U′ + V′) / 4` after normalize. |
| `chaos` | CSA-1.0 | `0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′` after normalize. |
| `balance` | BSA | `B=(Zn−Cn)/(Zn+Cn+ε)`, `α=(1+B)/2`, `RGB = α·Zen + (1−α)·Chaos`. Never invents marks. |

## Ink / page targets

Same polarity as Corpus OCR ink/page modes. Applied after the lens overlay.
Reweights existing pixels only.

| id | action |
|----|--------|
| `ink` | Isolate writing: crush parchment, keep strokes. Default. |
| `page` | Isolate substrate: lift parchment, wash ink. |

Several lenses may be selected (Corpus OCR checkbox family). They are mixed
equally, then the target is applied.

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
spectrallock overlay --mode zero|tazel|vyrn|uv|rosetta|zen|chaos|balance --target ink|page IN.png OUT.png
spectrallock overlay --lens tazel --target page page.jpg out.png --json
spectrallock overlay --mode tazel page.jpg out.png --verify --sidecar
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
- Overlay: `POST /v1/overlay` `{b64, mode|lens|lenses, target}` — PNG, max 256 px longest side. Does **not** increment the download counter.
- AI help: https://spectrallock-download-tracker.vibelock.workers.dev/ai
- Catalog: https://aziel-runtime.vibelock.workers.dev/ (MCP tools `spectrallock_modes`, `spectrallock_overlay`)
- Corpus OCR: https://www.azielcorpuslibrary.net/ocr

Isolated counter: Worker `spectrallock-download-tracker`, project `spectrallock`,
KV `SPECTRALLOCK_DOWNLOADS`. `totalKey` `spectrallock|__total__`. `/download`
serves gzip from Worker assets (`private, no-store`). No 302 to GitHub.

## Use with ChatGPT, Grok, Venice, Claude, Cursor, and other MCP/OpenAPI-capable assistants

Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
This Worker skill: https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill
This Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json

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
