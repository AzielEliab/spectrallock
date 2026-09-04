---
name: SpectralLock
description: Use when calling SpectralLock hosted /v1 or installing the local package. Rosetta spectral analysis — same lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.
---

# SpectralLock

Rosetta spectral analysis software (RSA-2.0 family). Same SpectralLock lenses as Aziel Corpus Library OCR: overlays plus ink/page targets. Author: **Aziel Eliab**.

**THIS IS:** Rosetta spectral analysis — SpectralLock lenses, overlays, and ink/page modes, aligned with [Aziel Corpus Library OCR](https://www.azielcorpuslibrary.net/ocr).

**THIS IS NOT:** a court exhibit or a claim of authenticity. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`
- Corpus OCR (reference): https://www.azielcorpuslibrary.net/ocr

Ops (do **not** increment downloads or views):

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/modes` | List SpectralLock lenses. |
| GET | `/v1/lenses` | Alias for `/v1/modes`. |
| GET | `/v1/targets` | Ink and page targets. |
| POST | `/v1/overlay` | Rosetta spectral overlay on a posted PNG (base64). Accepts `mode`/`lens`/`lenses` and `target` (`ink`\|`page`). |

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/lenses
```

## Local (after one-click install)

```bash
curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash
spectrallock ui
spectrallock doctor
```

Then open http://127.0.0.1:8861 (loopback only).

Counted download (gzip HTTP 200, no 302): https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.3.0.tar.gz
GitHub: https://github.com/AzielEliab/spectrallock

## Catalog + local UI

Author: **Aziel Eliab**. Rosetta spectral analysis. 256px hosted preview; full pipeline is the Python package.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/spectrallock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Lenses + Ink/Page. Then `spectrallock doctor`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.
