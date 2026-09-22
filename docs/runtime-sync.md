# Runtime sync — vendored SpectralLock engine

After this repository merges to `main`, **GitBaby will CLEAR `spectrallock`
then bump aziel-runtime.** Do not invent a digest. Identity is Aziel Eliab
only.

Hosted overlay source of truth in this repo:

`workers/download-tracker/src/overlay.js`

Vendored artifact path in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime):

`src/engines/spectrallock/overlay.js`

`ENGINE_ARTIFACTS.spectrallock` is exactly `["spectrallock/overlay.js"]`.
`engine_digest` is SHA-256 of those file bytes (sorted path order,
concatenated with `path\\n` + bytes + `\\n`). Recompute only from disk.

## Exact steps (GitBaby / operator)

1. Wait until `AzielEliab/spectrallock` `main` includes the new LIVE modes
   in `workers/download-tracker/src/overlay.js`
   (`zero`, `tazel`, `vyrn`, `uv`, `rosetta`, `zen`, `chaos`, `balance`,
   `candle`, `indent`, `lemon` plus aliases) **and** the color inject switch
   (`inject` true\|false, `tazel_inband_pct`, `vyrn_inband_pct`, paint ≠ pigment).

2. In `aziel-runtime`, **CLEAR** the previous SpectralLock vendor copy:
   - wipe `src/engines/spectrallock/` (GitBaby CLEAR of the slug)
   - leave `ENGINE_ARTIFACTS.spectrallock = ["spectrallock/overlay.js"]`
   - the previous `ENGINE_DIGESTS.spectrallock` hex is stale the moment
     bytes change — do not copy the old hex forward

3. Copy this repo's overlay into the vendor slot, byte-for-byte:

   ```bash
   mkdir -p src/engines/spectrallock
   cp /path/to/spectrallock/workers/download-tracker/src/overlay.js \
      src/engines/spectrallock/overlay.js
   ```

4. Rehash:

   ```bash
   node scripts/hash-engines.mjs --write
   ```

   That rewrites `src/engines/digest.js` `ENGINE_DIGESTS.spectrallock`.
   Confirm freshness (must print `spectrallock <64-hex>` and exit 0):

   ```bash
   node scripts/hash-engines.mjs
   ```

5. FragGate modes list. Catalog LIVE_OPS stay
   `health`, `modes`, `targets`, `overlay`, `verify`, `doctor`, `skill`.
   Stub ops stay `spectrometer`, `forensic`, `invent_mark`.
   After rehash + runtime deploy, `fraggate_call slug=spectrallock op=modes`
   (and `GET /v1/software` / Worker `GET /v1/modes`) must list the eleven
   canonical ids above. Aliases resolve to those ids. Overlay/verify must
   accept `inject` and report `tazel_inband_pct` / `vyrn_inband_pct` before
   any hit claim. Lamb Lens remains Service → Clarity → Peace (no invented
   marks; inject ON is paint, not pigment).
   `overlay.js` now also carries the honest unredact / leftover-bytes
   family (`locate`, `lift`, `recover`, `refuse`) plus deep historical
   PDF revision recovery (operator lock 2026-09-19). Product Worker
   `GET|POST /v1/unredact` (aliases `/v1/lift`, `/v1/redact-locate`) must
   refuse opaque sanitized rewrite with no leftover bytes (`SL-UNREDACT-OPAQUE`)
   and must never invent letters. Recover/locate return `page_revisions`,
   `revision_compare`, `revision_graph` (startxref/Prev edges + per-revision
   tip-cut `copy` / embeds; hosted may cap `b64` and cite sha256+offsets),
   `operator_text`, `classifications`,
   `recovered_characters` (page / object_id / generation / xref_revision /
   stream_offset / operator / font / decoded_bytes / source_revision /
   sha256), `ocr` (after structural only; hosted OCR unbound), and
   optional `twin_b64` compare. Leftover / historical bytes = recover;
   leftover_bytes is false when the container was rewritten and old
   bytes are gone.    Catalog door ops for unredact / recover / handwriting stay the list above until GitBaby
   adds those names to LIVE_OPS. Operator lock 2026-09-22 adds restore lost pigment
   as a LIVE SpectralLock door: vendored `overlay.js` exports `listPigment` and
   `pigmentFromB64`. After rehash, FragGate `slug=spectrallock` ops `pigment` and
   `restore-pigment` should join LIVE_OPS beside `modes` / `overlay`. AMOE stays
   on the suite project map and is not a SpectralLock 0.3.x product. Product Worker also serves `GET|POST /v1/recover`
   (universal family; LIVE vs SLOT matrix; secrets suppressed) and
   `GET|POST /v1/handwriting` (synthetic ink-on-paper scan heuristics;
   256 px PNG preview; not ESDA / chemical dating / writer identity /
   court finding). Rehash still
   uses `ENGINE_ARTIFACTS.spectrallock = ["spectrallock/overlay.js"]`
   only. **This product PR does not bump the runtime digest.** After
   merge, GitBaby CLEARs `spectrallock` then rehashes. Do not invent
   `3427dbcf…` forward.

6. **Bump runtime** (GitBaby bump) and deploy
   `aziel-runtime.vibelock.workers.dev`.

## Deploy note — spectrallock-download-tracker

This product Worker must be deployed after merge so hosted `/v1/modes`,
`/v1/lenses`, and `POST /v1/overlay` serve the new LIVE modes. `/v1` must
not increment `SPECTRALLOCK_DOWNLOADS`. Hosted overlay remains 256 px
preview honesty. Full pipeline is the Python package.

```bash
cd workers/download-tracker
npx wrangler deploy
```

Hostname: `spectrallock-download-tracker.vibelock.workers.dev`.

Author: Aziel Eliab.
