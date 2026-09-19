# SpectralLock 0.3.0 — product spec

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

## Live lenses (package 0.3.0)

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

- **ON** paints membership (false color). Not recovered pigment.
- **OFF** is luminance of the same gate (gray).
- **`zero`** ignores the switch (stays gray).
- tazel: 170° `#1EC9A5` teal heat on in-band pixels.
- vyrn: 350° `#C00066` magenta heat on in-band pixels.
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
  follow; xref streams and object streams; bytes after logical EOF).
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
  source_revision / sha256. That is reading present bytes.
- **OCR** runs only after structural recovery. It may read unredacted
  surrounding text and historical raster differences. It never
  reconstructs covered letters from context. Context guesses are not
  recovery. Heatmap ≠ transcript.
- **Refuse** `SL-UNREDACT-OPAQUE` when the cover is an opaque sanitized
  rewrite (or a flattened box) **and** leftover bytes are gone.

Hosted `/v1/unredact` may keep preview limits (payload cap, no OCR
engine) but must not lie about capabilities. Runtime rehash after merge
still copies `overlay.js` only — follow-on aziel-runtime sync after this
product PR (GitBaby CLEARs). Do not invent a digest.

Runtime rehash after merge still copies `overlay.js` only, then
`node scripts/hash-engines.mjs --write`. GitBaby CLEARs `spectrallock`
then bumps aziel-runtime. Do not invent a digest.

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
