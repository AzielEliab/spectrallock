---
name: SpectralLock
description: Use when calling SpectralLock hosted /v1 or installing the local package. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Not a Softwares-tab product. Rosetta spectral analysis — same lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.
---

# SpectralLock

Rosetta spectral analysis software (RSA-2.0 family). Same SpectralLock lenses as Aziel Corpus Library OCR: overlays plus ink/page targets. LIVE modes: `zero`, `tazel`, `vyrn`, `uv` (aliases `ultraviolet`, `uv-light`, `uvsa`), `rosetta`, `zen`, `chaos`, `balance`, `candle` (aliases `candlelight`, `candle-light`), `indent` (aliases `indentation`, `suppress-ink`, `ink-suppress`, `revealer-indent`), `lemon` (aliases `lemon-ink`, `hidden-lemon`, `invisible-ink-lemon`). Honest unredact family (not a lens): `unredact` / `lift` / `redact-locate` with ops `locate`, `lift`, `recover`, `refuse`. Locate leftover / historical page bytes and residual only — never invent letters. Opaque rewrite with nothing left refuses `SL-UNREDACT-OPAQUE`. OCR only after structural recovery. Synthetic image analysis — not a lab instrument, not forensic certification. Stub: `spectrometer`, `forensic`, `invent_mark`. Author: **Aziel Eliab**.

**THIS IS:** Rosetta spectral analysis — SpectralLock lenses, overlays, and ink/page modes, aligned with [Aziel Corpus Library OCR](https://www.azielcorpuslibrary.net/ocr).

**THIS IS NOT:** a court exhibit or a claim of authenticity. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`
- Suite mesh: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh` (PROXY; default OFF; QNS-CD-1.0 cross-map)
- Corpus OCR (reference): https://www.azielcorpuslibrary.net/ocr

Ops (do **not** increment downloads or views):

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/modes` | List SpectralLock lenses (canonical ids + aliases). |
| GET | `/v1/lenses` | Alias for `/v1/modes`. |
| GET | `/v1/targets` | Ink and page targets. |
| POST | `/v1/overlay` | Rosetta spectral overlay on a posted PNG (base64). Accepts `mode`/`lens`/`lenses`, `target` (`ink`\|`page`), and `inject` (`true`\|`false`). ON is false-color membership tint (paint), not recovered pigment. OFF is gray of the same gate. Zero ignores the switch. Returns `tazel_inband_pct` and `vyrn_inband_pct` before any hit claim. 256 px preview; prefer local `spectrallock_inject.py`. |
| GET | `/v1/unredact` | Honesty banner + unredact ops (`locate`, `lift`, `recover`, `refuse`). Does not increment downloads. |
| POST | `/v1/unredact` | Locate leftover / historical page bytes. Body `{b64, op, query, twin_b64?}`. Returns `leftover_bytes`, `recovered_from`, `page_revisions`, `revision_compare`, `revision_graph` (`revisions[]` with tip-cut `copy` `{media_type, filename, b64, sha256, byte_length, source_revision}` plus surviving embeds; `edges[]` with added/replaced/deleted/freed / `page_deltas` / `redaction_ops` classified `replaced` \| `overlaid` \| `detached` \| `sanitized rewrite`; `root_startxref`, `eof_offsets`), `operator_text`, `classifications`, `recovered_characters` (page / object_id / generation / xref_revision / stream_offset / operator / font / decoded_bytes / source_revision / sha256), `ocr` (after structural only; never covered letters from context), `refuse_code` (`SL-UNREDACT-OPAQUE`). Hosted preview may cap copy size (sha256+offset cites; no invented bytes) and has no OCR engine — it does not lie about that. Aliases: `POST /v1/lift`, `POST /v1/redact-locate`. |
| GET | `/v1/recover` | Universal recover ops + LIVE vs SLOT format matrix. Does not increment downloads. Not a catalog door op. |
| POST | `/v1/recover` | Universal artifact recovery. Body `{b64, op, filename, query, twin_b64?}`. Ops: `locate` · `deep-recover` · `revision-graph` · `cross-compare` · `extract-embedded` · `scan-orphans` · `scan-metadata` · `scan-sidecars` · `scan-history` · `refuse`. Envelope: `{artifact, type, revisions, metadata, embedded, orphans, prior_content, redaction_regions, recovered, refused, provenance, no_lie}`. Present bytes only. Secrets: `secret_material_present` + path/offset; values suppressed. SLOT parsers are not advertised as LIVE. |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live|locked|isolated. QNS-CD-1.0 cross-map (photon QNS1; not a Softwares-tab product). Never enables. No public qnsd proxy. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). Peers see the QNS-CD-1.0 cross-map. |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import OpenAPI as a custom tool, GPT Action, HTTP tool, or MCP connector. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer; local qnsd in https://github.com/AzielEliab/qnm-node; runtime cites in https://github.com/AzielEliab/aziel-runtime). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Not a Softwares-tab product.

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

Author: **Aziel Eliab**. Rosetta spectral analysis. 256px hosted preview; full pipeline is the Python package. Lamb Lens: Service → Clarity → Peace. Never invent marks.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/spectrallock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/example`
- Suite mesh: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh` PROXY (default OFF; QNS-CD-1.0 cross-map)

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Lenses + Ink/Page + inject ON/OFF. Then `spectrallock doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). QNS-CD-1.0 is a hub cite / Worker mesh cross-map only — not a Softwares-tab product; no public qnsd proxy.

Color inject (operator lock 19 Sep 2026): `--inject` / `--no-inject` on every named mode. ON paints membership; OFF is luminance of the same gate; `zero` stays gray. tazel=170° `#1EC9A5`, vyrn=350° `#C00066`. UV is synthetic, not a lamp. Balance does not invent marks. Report `tazel_inband_pct` and `vyrn_inband_pct` before claiming a hit. Empty gate ≠ broken lens. Prefer `python3 spectrallock_inject.py`. Identity: Aziel Eliab. Lamb Lens: Service → Clarity → Peace. NO-LIE.

Unredact / lift-overlay (operator lock 2026-09-19 — NO-LIE): `locate` reports text still in the PDF, metadata, attachments, twin-page residual, leftover container bytes, and historical page revisions (stale `/Page` graphs, prior streams, xref/ObjStm, after-EOF, incremental `startxref`/`Prev` revision graph + per-revision tip-cut PDF/embed copies). That is reading bytes that are still present — not guessing a black box. `lift` is non-opaque residual with `--no-inject` only; heatmaps are not transcripts. Opaque sanitized rewrite with nothing left refuses `SL-UNREDACT-OPAQUE`. If leftover / historical bytes remain, `recover` surfaces them with character provenance. OCR runs only after structural recovery and never reconstructs covered letters from context. Hosted `/v1/unredact` may keep preview limits (copy-size cap cites sha256 + offsets; never invents bytes) but does not lie about capabilities. Never invent letters. Never claim pigment recovery, ESDA, chemical, lab, or forensic certification.

Universal recover (operator lock 2026-09-19 — NO-LIE): `spectrallock recover …` and `GET|POST /v1/recover`. Search all physically present representations (old streams, tracked changes, thumbnails, JSON/XML tombstones, metadata, attachments, siblings, SQLite freelist, Git objects when `.git` is supplied, shared strings, comments, hidden sheets, archive members) before declaring gone. Confidence is provenance quality, not guessed correctness. Audit: `docs/audit/UNIVERSAL-RECOVER-AUDIT.md`. Catalog LIVE_OPS stay honest — do not invent a FragGate `recover` door.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a custom tool, GPT Action, HTTP tool, or MCP connector. MCP clients can use the catalog MCP endpoint. Suite mesh: `GET /v1/mesh` PROXY (default OFF). QNS-CD-1.0 cross-map (photon QNS1 packet transfer). Catalog MCP `mesh_*` + FragGate `slug=mesh`.
