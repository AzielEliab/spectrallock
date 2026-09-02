---
name: SpectralLock
description: Use when calling SpectralLock hosted /v1 or installing the local package. Author Aziel Eliab.
---

# SpectralLock

Advisory digital overlays on photographs of manuscript pages. Not a lab spectrometer. Not real UV photography hardware. Not forensic ink proof. The human still reads the page. Author: Aziel Eliab.

**THIS IS:** advisory digital overlays on photographs of manuscript pages.

**THIS IS NOT:** a lab spectrometer, real UV photography hardware, forensic ink proof, or OCR truth. The human still reads the page.

Author: **Aziel Eliab**. Forks are welcome and always allowed. Apache-2.0.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/modes` | List overlay modes. |
| POST | `/v1/overlay` | Advisory overlay on a posted PNG (base64). Not a spectrometer. |

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/modes
```

## Local (after one-click install)

```bash
curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash
spectrallock ui
```

Then open http://127.0.0.1:8861 (loopback only).

Counted download (gzip HTTP 200, no 302): https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/spectrallock
