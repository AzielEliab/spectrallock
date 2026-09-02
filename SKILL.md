---
name: SpectralLock
description: Use when calling SpectralLock hosted /v1 or installing the local package. Author Aziel Eliab.
---

# SpectralLock

Digital overlay analysis of manuscript photographs. Advisory visualization. Author: **Aziel Eliab**.

**THIS IS:** digital overlay analysis of manuscript photographs.

**THIS IS NOT:** a certified forensic instrument, a court exhibit, or a claim of authenticity. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- Product POSTs listed in OpenAPI

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill
```

## Local (after one-click install)

```bash
curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash
spectrallock ui
spectrallock doctor
```

Then open http://127.0.0.1:8861 (loopback only).

Counted download (gzip HTTP 200, no 302): https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/spectrallock
