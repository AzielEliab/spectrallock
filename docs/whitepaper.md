# SpectralLock 0.2.0 — product spec

**Author:** Aziel Eliab  
**Date:** 2026  
**License:** Apache-2.0

Source papers (verbatim extracts) live in [`docs/source/`](source/).

## What this is

SpectralLock applies **named digital overlays** to ordinary photographs of
manuscript pages so a human can look again. It is image processing
(Pillow + numpy): hue weighting, histogram equalization, band-pass,
unsharp, and documented linear mixes of those channels.

## What this is not

- Not a lab spectrometer.
- Not real UV photography hardware, not a 365 nm lamp, not fluorescence capture.
- Not a forensic proof of hidden ink.
- Not OCR and not transcription.
- Not a claim of scribal truth, dating, authorship, or conservation science.
- Balance never invents marks or symbols.

The human still reads the page.

## Color definitions

| name | hex | hue | role |
|------|-----|-----|------|
| Tazel | `#1EC9A5` | ~170° | revelation (green–gold–turquoise) |
| Vyrn | `#C00066` | ~350° | purification / pressure (magenta–red-violet) |
| Zero | `#6F6485` | ~260° | equilibrium (indigo / blue-violet) |

## Live engines (v1.0 / package 0.2.0)

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
darker. Not a real UV lamp.

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

## Hosted preview vs package

The Cloudflare Worker `/v1/overlay` is a simplified JavaScript port
(PNG decode, longest side ≤ 256 px, approximate hue matrices + the same
published weights). Full histogram / band-pass / unsharp lives in the
Python package.

## UI

`spectrallock ui` binds **127.0.0.1:8861** only. Dark gold. Add file or
Sample page, Simple/Advanced labels, overlay-only or side-by-side, Export
PNG + JSON sidecar, Verify receipt (mode, paper, SHA-256 in/out, size).
Banner: overlays are not forensic proof. `spectrallock doctor` checks all
eight modes, no NaN, loopback, no telemetry.
