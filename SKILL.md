---
name: SpectralLock
description: Use when calling SpectralLock hosted /v1 or installing the local package. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Rosetta spectral analysis — same lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.
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
- Suite mesh: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh` (PROXY; default OFF)
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
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live|locked|isolated. Never enables. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import OpenAPI as a custom tool, GPT Action, HTTP tool, or MCP connector. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/lenses
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh
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
- Suite mesh: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh` PROXY (default OFF)

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Lenses + Ink/Page. Then `spectrallock doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF).

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a custom tool, GPT Action, HTTP tool, or MCP connector. MCP clients can use the catalog MCP endpoint. Suite mesh: `GET /v1/mesh` PROXY (default OFF). Catalog MCP `mesh_*` + FragGate `slug=mesh`.
