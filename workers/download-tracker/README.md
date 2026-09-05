# spectrallock download tracker

Isolated Worker `spectrallock-download-tracker`. Project `spectrallock`.
KV namespace `SPECTRALLOCK_DOWNLOADS` bound as `DOWNLOADS`.
totalKey `spectrallock|__total__`. Does not 302 to GitHub on `/download`.
Serves gzip via `ASSETS.fetch`, `Cache-Control: private, no-store`.

`/v1` never increments DOWNLOADS KV.

## Use with ChatGPT, Grok, Venice, Claude, Cursor, and other MCP/OpenAPI-capable assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

- OpenAPI: `https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json`
- Health: `GET /v1/health`
- Lenses: `GET /v1/lenses` (alias `GET /v1/modes`)
- Targets: `GET /v1/targets`
- Overlay: `POST /v1/overlay` `{b64, mode|lens|lenses, target}` — PNG, max 256 px. Rosetta preview.
- Setup HTML: `GET /ai`

Banner: Rosetta spectral analysis. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.

CORS `*` on API routes.

KV id in wrangler.toml: `0b998ba1bbec4eedadcf19e23f9995ce`. Binding name MUST stay `DOWNLOADS` (not `SPECTRALLOCK_DOWNLOADS` — that is the Cloudflare namespace title).
