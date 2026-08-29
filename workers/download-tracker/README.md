# spectrallock download tracker

Isolated Worker `spectrallock-download-tracker`. Project `spectrallock`.
KV namespace `SPECTRALLOCK_DOWNLOADS` bound as `DOWNLOADS`.
totalKey `spectrallock|__total__`. Does not 302 to GitHub on `/download`.
Serves gzip via `ASSETS.fetch`, `Cache-Control: private, no-store`.

`/v1` never increments DOWNLOADS KV.

## Use with Grok, ChatGPT, Venice

- OpenAPI: `https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json`
- Health: `GET /v1/health`
- Modes: `GET /v1/modes`
- Overlay: `POST /v1/overlay` `{b64, mode}` — PNG, max 256 px. Simplified preview.
- Setup HTML: `GET /ai`

Banner: not a lab spectrometer, not real UV hardware, not forensic proof.

CORS `*` on API routes.
