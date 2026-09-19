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
   `candle`, `indent`, `lemon` plus aliases).

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
   canonical ids above. Aliases resolve to those ids. Lamb Lens remains
   Service → Clarity → Peace (no invented marks).

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
