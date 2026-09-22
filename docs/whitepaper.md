# SpectralLock 0.3.1 — product spec

**Author:** Aziel Eliab  
**Date:** 2026  
**License:** Apache-2.0

Source papers (verbatim extracts) live in [`docs/source/`](source/).

## What this is

SpectralLock is **Rosetta spectral analysis** software (RSA-2.0 family).
It applies the same **SpectralLock lenses** used by
[Aziel Corpus Library OCR](https://www.azielcorpuslibrary.net/ocr):
named overlays plus ink/page targets on ordinary photographs of
manuscript pages.

It is image processing (Pillow + numpy): hue weighting, histogram
equalization, band-pass, unsharp, documented linear mixes, then an
ink or page polarity.

## What this is not

- Not a court exhibit or a claim of authenticity.
- Not a substitute for a human reading the page.
- Synthetic UV is a 365–400 nm *look* from an ordinary photograph, not a lamp.
- Candlelight, indent, and lemon are synthetic looks from ordinary photos.
- Balance never invents marks or symbols. Lemon never invents marks.

The human still reads the page.

## Color definitions

| name | hex | hue | role |
|------|-----|-----|------|
| Tazel | `#1EC9A5` | ~170° | revelation (green–gold–turquoise) |
| Vyrn | `#C00066` | ~350° | purification / pressure (magenta–red-violet) |
| Zero | `#6F6485` | ~260° | equilibrium (indigo / blue-violet) |

## Spectral Harmonic Wheel paint (operator lock 2026-09-22)

Separate from the triad above. Densitometry and in-band math keep `#1EC9A5` / `#C00066` / `#6F6485`. Inject membership tints use the wheel. Source: [`docs/source/color-wheel-paint.txt`](source/color-wheel-paint.txt). Hexes are authoritative.

| label | paint hex |
|-------|-----------|
| ZERO | `#325767` |
| CHAOS | `#8D223D` |
| VYRN | `#A22639` |
| UV | `#9F3B2B` |
| TAZEL | `#797A2D` |
| ROSETTA | `#467542` |
| ZEN | `#DFD2B5` |

## Live lenses (package 0.3.1)

Same ids as the Corpus OCR SpectralLock lens checkboxes.

### ZSA-1.0 `zero`

Desaturate → histogram-equalize luminance → mild band-pass (blur subtract)
→ unsharp for grooves. Report center-of-mass of the output luminance.

### TSA-1.0 `tazel`

Boost the ~170° band vs other hues, lift faint midtones, fine-line
unsharp, parchment-smoothing (large-scale blur subtract).

### VSA-1.0 `vyrn`

Boost the ~350° band, suppress green/cyan, edge/pressure unsharp, wash
the background.

### UVSA-1.0 `uv`

Ultraviolet light analysis (synthetic). 365–400 nm *look* from an
ordinary RGB photo: boost parchment luminance, blue-violet weight,
microtexture high-pass, ink darker. Aliases: `ultraviolet`, `uv-light`,
`uvsa`.

### CLSA-1.0 `candle`

Warm flame-side illumination look (~1800–2700 K ambers, parchment glow,
ink readable) from an ordinary photograph. Not real multispectral
capture. Aliases: `candlelight`, `candle-light`.

### ISA-1.0 `indent`

Suppress visible writing so paper-fiber / pressure indentations and
surface relief are easier to see. Image-enhancement heuristic. Prefer
target `page`. Not ESDA / electrostatic detection, and not a claim of
recovering invisible writing with certainty. Aliases: `indentation`,
`suppress-ink`, `ink-suppress`, `revealer-indent`.

### LISA-1.0 `lemon`

Heat-/acid-revealed style lemon (citrus) invisible-ink cues: warm
browning and contrast shifts already in the pixels. Not a chemical test.
Never invents marks. Aliases: `lemon-ink`, `hidden-lemon`,
`invisible-ink-lemon`.

### RSA-2.0 `rosetta`

Compute Z′, T′, V′ as float fields 0–1, min–max normalize each, then

```
RSA-2.0 = 0.40·Z′ + 0.35·T′ + 0.25·V′
```

### ZENA-1.0 `zen`

```
ZENA-1.0 = (Z′ + T′ + U′ + V′) / 4
```

after per-channel normalize.

### CSA-1.0 `chaos`

```
CSA-1.0 = 0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′
```

after per-channel normalize.

### BSA `balance`

```
B  = (Zn − Cn) / (Zn + Cn + ε)
α  = (1 + B) / 2
RGB = α·Zen + (1 − α)·Chaos
```

Never invents marks: every output pixel is a convex combination of the
Zen and Chaos pixels already computed.

## Ink / page targets

Applied after the lens overlay. Reweights existing pixels only.
Parchment color is estimated from the brightest quintile of the photo.

### `ink`

Isolate writing: crush parchment toward the estimated page color, keep
strokes darker. Default. Matches Corpus OCR ink mode.

### `page`

Isolate substrate: wash ink toward the estimated parchment color, keep
large-scale page texture. Matches Corpus OCR page mode.

Several lenses may be selected (Corpus OCR checkbox family). They are
mixed equally, then the target is applied.

## Color inject switch

Operator lock 19 Sep 2026. Each named mode has `--inject` / `--no-inject`
(Python `inject=True|False`, Worker payload `inject`).

- **ON** paints membership from the Spectral Harmonic Wheel.
- **OFF** is luminance of the same gate (gray).
- **`zero`** ignores the switch (stays gray).
- In-band spectral math: tazel 170° `#1EC9A5`, vyrn 350° `#C00066`, zero `#6F6485`.
- Wheel membership paint: TAZEL `#797A2D`, VYRN `#A22639`, and the other five labels in the wheel table.
- uv: synthetic 365–400 look (violet parchment / residual) — not a lamp.
- rosetta / zen / chaos / balance: composite tint when ON; gray gate when OFF.
  Balance does not invent marks.
- candle / indent / lemon: honest ON tint vs OFF gray of the same gate.

`tazel_inband_pct` and `vyrn_inband_pct` are reported on overlay/verify JSON
from the **source** photograph (hue within σ of 170° / 350° and enough
chroma). Empty gate ≠ broken lens. Copy-of-copy only works if the hue is
still in-band.

```bash
python3 spectrallock_inject.py page.jpg --mode vyrn --inject -o vyrn_on.jpg
```

Hosted `/v1/overlay` may accept `inject` without claiming pigment recovery.
256 px preview honesty stays. Prefer the local package.

## Unredact / leftover-bytes (operator lock — NO-LIE)

Not a lens. Does not invent letters. Does not claim ESDA, chemical, lab,
or forensic certification.

- **Locate** reports text still in a PDF under a visual box, metadata,
  attachments, twin-page residual, leftover container bytes, and
  historical page revisions (stale `/Page` objects with recursive
  `/Contents` `/Resources` `/XObject` `/Font` `/ToUnicode` `/Annots`
  `/Metadata` `/PieceInfo` `/StructParents` `/AcroForm` / embedded-file
  follow; xref streams and object streams; bytes after logical EOF;
  explicit incremental-update revision graph from `startxref` / `/Prev`
  / trailer / classic xref + XRef streams).
- **Lift** is non-opaque residual enhancement with inject OFF. A heatmap
  is not a transcript. Flattened screenshots of a box are treated as replace.
- **Recover** is allowed only when leftover / historical bytes remain
  (incremental update, unused/orphan objects, prior streams, stale pages,
  attachments, after-EOF). Fields include `leftover_bytes`,
  `recovered_from`, `page_revisions`, `revision_compare` (bytes / text
  operators / strings / glyph sequences / XObject refs only in old;
  object IDs replaced), `operator_text`, `classifications`
  (`text_under_vector_overlay` / `text_converted_to_outlines` /
  `text_rasterized_into_image` / `old_revision_survives` /
  `object_deleted_bytes_remain` / `sanitized_rewrite`), and
  `recovered_characters` with page / object_id / generation /
  xref_revision / stream_offset / operator / font / decoded_bytes /
  source_revision / sha256, and `revision_graph` (`revisions[]` nodes
  with `startxref`, `trailer_offset`, `page_ids`, `sha256_tip`, and a
  reconstructable tip-cut `copy` plus surviving embeds from that
  revision's object set; `edges[]` report objects added / replaced /
  deleted / freed, pages whose `/Contents` `/Resources` `/XObject`
  `/Annots` `/Metadata` changed, and `redaction_ops` classified
  `replaced` | `overlaid` | `detached` | `sanitized rewrite` with
  object ids, generations, stream offsets, and sha256 of before/after
  streams). Copies are leftover bytes carved at each `%%EOF`, not
  invented. Hosted preview may omit large `b64` and cite sha256 +
  offsets. That is reading present bytes.
- **OCR** runs only after structural recovery. It may read unredacted
  surrounding text and historical raster differences. It never
  reconstructs covered letters from context. Context guesses are not
  recovery. Heatmap ≠ transcript.
- **Refuse** `SL-UNREDACT-OPAQUE` when the cover is an opaque sanitized
  rewrite (or a flattened box) **and** leftover bytes are gone.

Hosted `/v1/unredact` may keep preview limits (payload cap, revision-copy
cap, no OCR engine) but must not invent bytes or lie about capabilities.

## Universal recover (operator lock — NO-LIE)

Unredact is the PDF-focused leftover-bytes / visual path. `spectrallock recover`
and `GET|POST /v1/recover` are the universal family: locate, deep-recover,
revision-graph, cross-compare, extract-embedded, scan-orphans, scan-metadata,
scan-sidecars, scan-history, refuse.

Black rectangles may be visually unrecoverable while the value still exists
in old streams, tracked changes, thumbnails, JSON/XML tombstones, metadata,
attachments, siblings, SQLite freelist pages, supplied Git objects, shared
strings, comments, hidden sheets, or archive members. Search every
**physically present** representation before declaring gone. Confidence is
provenance quality (1.00 exact bytes … 0.85 strong sibling). Linguistic
reconstruction is not recovery.

Format coverage is an honest LIVE vs SLOT matrix
(`docs/audit/UNIVERSAL-RECOVER-AUDIT.md`). SLOT parsers (7z, HEIC, YAML AST
without PyYAML) are never advertised as LIVE. Secrets are cited
`secret_material_present` with path/offset; values are suppressed.

Runtime rehash after merge
still copies `overlay.js` only — follow-on aziel-runtime sync after this
product PR (GitBaby CLEARs). Do not invent a digest.

Runtime rehash after merge still copies `overlay.js` only, then
`node scripts/hash-engines.mjs --write`. GitBaby CLEARs `spectrallock`
then bumps aziel-runtime. Do not invent a digest.

## Handwriting / ink-on-paper (operator lock — NO-LIE)

`spectrallock handwriting` and `GET|POST /v1/handwriting` analyze
user-supplied scans or photos of physical ink on paper. This is
**synthetic image analysis**, not a lab instrument.

LIVE pixel heuristics: stroke-weight variation (width / darkness as a
pressure *proxy*), speed *cues* (taper, tremor frequency, ballistic vs
controlled shape), ink density, bleed / feathering, baseline / slant /
size shifts, erasure candidates (abrasion brightening, residual ghosts),
tracing (doubled-edge / unnatural uniformity), and a non-exhaustive
forgery-indicator list (tremor-copy, unnatural lifts, retouch, dual-ink,
clone-stamp, compression discontinuities, ductus, style-shift). Side-by-side
questioned vs known. Stroke/feature graph. Density / bleed / erasure
heatmaps. Spectral helpers (`uv`, `candle`, `indent`, `lemon`) may be
cited with inject OFF when they strengthen a present-pixel signal.

SLOT and never claimed: ESDA, chemical ink dating, force in newtons,
speed in mm/s, court-qualified examiner opinion, writer identification
as identity fact. Confidence is pixel signal quality, not “this is
forged.” Phrasing is always indicator / heuristic / candidate — human
verification required. Empty gate ≠ broken lens. Balance / lemon never
invent marks. Hosted preview is size-capped PNG; the full pipeline is
the Python package. Audit: `docs/audit/HANDWRITING-FORGERY-AUDIT.md`.
Do not invent a FragGate `handwriting` door.

## Hosted preview vs package

The Cloudflare Worker `/v1/overlay` is a simplified JavaScript port
(PNG decode, longest side ≤ 256 px, approximate hue matrices + the same
published weights, plus ink/page). Full histogram / band-pass / unsharp
lives in the Python package.

The Worker homepage shows a suite Live Nodes strip. `/v1/mesh/*` PROXY
to aziel-runtime. Suite mesh default OFF. QNM rollup is
live|locked|isolated counts only. No Node Gate. No auto-heal. Not an
anonymity network. Anon-broadcast is not a publish path. SpectralLock
remains Rosetta spectral analysis.

## UI

`spectrallock ui` binds **127.0.0.1:8861** only. Dark gold. Add file or
Sample page, SpectralLock lens grid (multi-select), Ink/Page target,
inject ON (paint) / OFF (gray), Simple/Advanced labels, overlay-only or
side-by-side, Export PNG + JSON sidecar, Verify receipt (lenses, target,
paper, inject, in-band percents, SHA-256 in/out, size).
`spectrallock doctor` checks all live lenses × both targets, no NaN,
loopback, no telemetry.

Runtime rehash after merge: [runtime-sync.md](runtime-sync.md).
