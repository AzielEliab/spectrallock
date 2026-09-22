# spectrallock download tracker

Isolated Worker `spectrallock-download-tracker`. Project `spectrallock`.
KV namespace `SPECTRALLOCK_DOWNLOADS` bound as `DOWNLOADS`.
totalKey `spectrallock|__total__`. Does not 302 to GitHub on `/download`.
Serves gzip via `ASSETS.fetch`, `Cache-Control: private, no-store`.

`GET /count` returns `{project, views, downloads, total}` and does not increment KV.
`DEFAULT_ASSET` (`spectrallock-0.3.1.tar.gz`) must live in `public/` or `/download` returns `asset not hosted`.
Build it with `scripts/build_tarball.sh`. Author Aziel Eliab.

`/v1` never increments DOWNLOADS KV.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (`AZIEL_RUNTIME` / `https://aziel-runtime.vibelock.workers.dev`). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). Local qnsd is coded in [qnm-node](https://github.com/AzielEliab/qnm-node). Runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). AZInterface holds pair custody. No Node Gate. No public qnsd proxy. No auto-heal. Human UI Live Nodes strip polls `GET /v1/mesh`. Status / Live Nodes JSON includes `qns_cd_spec` + `qns_cd` so peers can see the cross-map.

Verify: `curl -sS -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh/status` returns MESH-OK style JSON with `enabled: false` by default and the QNS-CD-1.0 cross-map.

## Use with ChatGPT, Grok, Venice, Claude, Cursor, and other MCP/OpenAPI-capable assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

- OpenAPI: `https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json`
- Health: `GET /v1/health`
- Lenses: `GET /v1/lenses` (alias `GET /v1/modes`)
- Targets: `GET /v1/targets`
- Overlay: `POST /v1/overlay` `{b64, mode|lens|lenses, target, inject}` — PNG, max 256 px. `inject` true|false is false-color membership paint. LIVE: zero, tazel, vyrn, uv, rosetta, zen, chaos, balance, candle, indent, lemon (aliases resolve). Rosetta preview.
- Unredact: `GET /v1/unredact` honesty banner; `POST /v1/unredact` `{b64, op, query, twin_b64?}` locate / leftover-historical recover / residual lift. Returns `revision_graph` (startxref/Prev edges + per-revision tip-cut copies / embeds). Opaque rewrite + no leftover → `SL-UNREDACT-OPAQUE`. Never invents letters. Heatmaps are residual overlays. OCR only after structural recovery. Hosted may cap copy `b64` and cite sha256+offsets — never invents bytes.
- Recover: `GET /v1/recover` ops + LIVE vs SLOT; `POST /v1/recover` `{b64, op, filename, twin_b64?}`. Present bytes only. Secrets suppressed. SLOT stays SLOT; LIVE stays LIVE.
- Handwriting: `GET /v1/handwriting` ops + LIVE vs SLOT; `POST /v1/handwriting` `{b64, op, filename, twin_b64?}`. Synthetic ink-on-paper scan heuristics. 256 px PNG preview. Never invents marks.
- Setup HTML: `GET /ai`
- llms.txt: `GET /llms.txt`
- ai.txt: `GET /ai.txt`
- cite.json: `GET /cite.json`

Banner: Rosetta spectral analysis. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.

CORS `*` on API routes.

KV id in wrangler.toml: `0b998ba1bbec4eedadcf19e23f9995ce`. Binding name MUST stay `DOWNLOADS` (not `SPECTRALLOCK_DOWNLOADS` — that is the Cloudflare namespace title).

## Human / bot schema (`/stats` and `/count`)

Additive dual-count (Whitestone canary). Classification lives in `src/classify.js`
and response shaping in `src/stats-shape.js`.

Invariant: `views === views_human + views_bot` and
`downloads === downloads_human + downloads_bot`.

Legacy strategy (b): existing KV totals are never reset. Pre-split remainder
is shown as bot on read (`views_bot = views - views_human`). Author: Aziel Eliab only.

