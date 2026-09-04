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
- Balance never invents marks or symbols.

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

**Synthetic** 365–400 nm simulation from an ordinary RGB photo: boost
parchment luminance, blue-violet weight, microtexture high-pass, ink
darker.

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

## Hosted preview vs package

The Cloudflare Worker `/v1/overlay` is a simplified JavaScript port
(PNG decode, longest side ≤ 256 px, approximate hue matrices + the same
published weights, plus ink/page). Full histogram / band-pass / unsharp
lives in the Python package.

## UI

`spectrallock ui` binds **127.0.0.1:8861** only. Dark gold. Add file or
Sample page, SpectralLock lens grid (multi-select), Ink/Page target,
Simple/Advanced labels, overlay-only or side-by-side, Export PNG + JSON
sidecar, Verify receipt (lenses, target, paper, SHA-256 in/out, size).
`spectrallock doctor` checks all eight lenses × both targets, no NaN,
loopback, no telemetry.
