# SpectralLock

Digital **overlays on photographs** of manuscript pages.

**Author:** Aziel Eliab
**Date:** 2026
**License:** [Apache-2.0](LICENSE)
**Version:** 0.2.0

> Advisory visualization. The human still reads the page.

Not a lab spectrometer. Not real UV photography hardware. Not a forensic
proof of hidden ink. Not OCR. Not a claim of scribal truth. Synthetic UV
simulates a 365–400 nm *look* from an ordinary photo. Balance never
invents marks — it only reweights existing readings.

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
[spectrallock-0.2.0.tar.gz](https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.2.0.tar.gz)

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
   (or **Sample page**), pick a mode, then **Export**. Optional: **Verify**
   shows a receipt (mode, paper, SHA-256 in/out, size). Advisory overlay,
   not forensic. No CDN, no telemetry. Dark gold.

Counted download: [https://spectrallock-download-tracker.vibelock.workers.dev/](https://spectrallock-download-tracker.vibelock.workers.dev/)

Direct tarball: [spectrallock-0.2.0.tar.gz](https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.2.0.tar.gz)

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

## Modes (all live in 0.2.0)

| id | paper | formula / action |
|----|-------|------------------|
| `zero` | ZSA-1.0 | Grayscale, hist-eq, band-pass, unsharp. Hue ~260°, `#6F6485`. |
| `tazel` | TSA-1.0 | Boost green–gold–turquoise (~170°, `#1EC9A5`). Lift faint midtones. |
| `vyrn` | VSA-1.0 | Boost magenta–red-violet (~350°, `#C00066`). Suppress green/cyan. |
| `uv` | UVSA-1.0 | Synthetic 365–400 nm simulation. Parchment glow, ink darker. **Not a UV lamp.** |
| `rosetta` | RSA-2.0 | `0.40·Z′ + 0.35·T′ + 0.25·V′` after per-channel normalize. |
| `zen` | ZENA-1.0 | `(Z′ + T′ + U′ + V′) / 4` after normalize. |
| `chaos` | CSA-1.0 | `0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′` after normalize. |
| `balance` | BSA | `B=(Zn−Cn)/(Zn+Cn+ε)`, `α=(1+B)/2`, `RGB = α·Zen + (1−α)·Chaos`. Never invents marks. |

Simple UI labels (kid-plain): clearer lines, lift green-gold, lift magenta,
fake UV look, mix of three, even mix of four, strong mix, blend two mixes.

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
spectrallock overlay --mode zero|tazel|vyrn|uv|rosetta|zen|chaos|balance IN.png OUT.png
spectrallock overlay --mode tazel page.jpg out.png --json
spectrallock overlay --mode tazel page.jpg out.png --verify --sidecar
spectrallock ui          # 127.0.0.1:8861
spectrallock serve       # alias for ui
```

PNG or JPEG in. `--verify` prints mode, paper, sha256 in/out, size.
`--sidecar` writes a JSON next to the overlay PNG (mode, hashes, limitation).
`SPECTRALLOCK_DEBUG=1` traces to stderr (never image bytes).

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.spectrallock`.
Offline color-matrix approximation of the hues. Not forensic. Not the
full Python pipeline. **Add file** + **Export**.

```bash
cd mobile
flutter create --org com.azieeliab --project-name spectrallock .
flutter pub get
flutter run
```

## Hosted preview

- OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Health: `GET /v1/health`
- Modes: `GET /v1/modes`
- Overlay: `POST /v1/overlay` `{b64, mode}` — PNG, max 256 px longest side. Does **not** increment the download counter.
- AI help: https://spectrallock-download-tracker.vibelock.workers.dev/ai
- Catalog: https://aziel-runtime.vibelock.workers.dev/ (MCP tools `spectrallock_modes`, `spectrallock_overlay`)

Isolated counter: Worker `spectrallock-download-tracker`, project `spectrallock`,
KV `SPECTRALLOCK_DOWNLOADS`. `totalKey` `spectrallock|__total__`. `/download`
serves gzip from Worker assets (`private, no-store`). No 302 to GitHub.

## License

Apache License 2.0. Copyright 2026 Aziel Eliab.
