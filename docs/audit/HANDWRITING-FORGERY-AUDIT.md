# Handwriting / forgery-indicator audit (NO-LIE)

Operator lock 2026-09-19. Author: Aziel Eliab only.
Lamb Lens: Service → Clarity → Peace.

This audit is a coverage and honesty checklist, **not** a forensic
certification and **not** a court-qualified examiner opinion. Every
signal is a pixel heuristic from a user-supplied scan or photo of
paper. Phrasing is always **indicator / heuristic / candidate — human
verification required.** Confidence is signal quality from present
pixels, never “this is forged” and never writer identification as
identity fact.

## Honesty checklist

| Rule | Status |
|------|--------|
| Analyze present pixels / metadata only | PASS — ink mask from luminance; `invented: false` |
| Never invent marks (Balance / lemon rule) | PASS — helpers run inject OFF; empty gate ≠ broken lens |
| Heatmap ≠ transcript | PASS — overlays set `heatmap_is_transcript: false` |
| Heatmap ≠ court finding | PASS — overlays set `heatmap_is_court_finding: false` |
| No ESDA claim | PASS — `esda: false`; indent helper cites “not ESDA” |
| No chemical ink dating | PASS — `chemical_ink_dating: false` |
| No writer identity as fact | PASS — `writer_identification_as_fact: false` |
| No court examiner opinion | PASS — `forensic_certification: false` |
| Catalog door not invented | PASS — Worker `/v1/handwriting` + CLI; not a FragGate LIVE_OP |
| Worker overlay digest not invented | PASS — GitBaby CLEAR after merge; do not forward `3427dbcf…` |
| Hosted does not invent JPEG decode | PASS — hosted PNG only; JPEG is SLOT on the Worker |

## Feature matrix (package)

| Signal | Status | What is real | Gap |
|--------|--------|--------------|-----|
| stroke_weight | LIVE | chamfer / width of ink-mask pixels | not force in newtons |
| speed_cues | LIVE | taper, tremor residual, ballistic vs controlled *shape* | speed mm/s is SLOT |
| ink_density | LIVE | darkness of ink-mask pixels | not pigment mass |
| bleed_feathering | LIVE | edge-gradient width (capillary-spread proxy) | not a paper assay |
| handwriting_shifts | LIVE | baseline drift, slant std, size change | not a second-writer fact |
| erasures | LIVE | abrasion brightening + mid-gray ghosts | residual ≠ recovered letters |
| tracing | LIVE | width uniformity, doubled-edge energy, lift clustering | heuristic only |
| tremor_copy | LIVE | high-frequency wobble + uniform width | not a lab tremor meter |
| pen_lifts | LIVE | connected-component breaks | unnatural only in context |
| retouch_overwrite | LIVE | very dark cores | not dual-ink chemistry |
| dual_ink | LIVE | hue clusters in stroke pixels | lighting / scan color can mimic |
| baseline_misalign | LIVE | row-centroid drift | not proof of discontinuous writing |
| indent_helper | LIVE | existing indent mode, inject OFF | **not ESDA** |
| clone_stamp | LIVE | repeated 8×8 luminance hashes far apart | digital scan artifact |
| compression_paste | LIVE | 8×8 block-energy discontinuities | JPEG q-tables not parsed |
| ductus | LIVE | mean resultant of stroke gradients | not identity |
| style_shift | LIVE | aspect-ratio regime change | print↔cursive heuristic flag only |
| pressure_newtons | **SLOT** | — | no force sensor |
| speed_mm_s | **SLOT** | — | no temporal capture |
| writer_identity | **SLOT** | never claimed as identity fact | — |
| esda | **SLOT** | — | not electrostatic detection |
| chemical_ink_dating | **SLOT** | — | not a lab assay |
| court_examiner_opinion | **SLOT** | — | not a qualified examiner finding |

## Worker overlay honesty

Hosted `/v1/handwriting` is a **256 px PNG preview port**: ink-mask,
4-dir radius weight (not full chamfer), density, bleed, erasures,
clone-stamp hashes, stroke graph, helper-mode cites (`indent` /
`lemon` / `uv` / `candle` inject OFF), and small heatmap PNGs.

JPEG decode is **SLOT** on the Worker (PNG only). Full chamfer, larger
analyze side (640), and JPEG/photo decode live in the Python package.
The Worker does not claim package coverage it does not run.

## Refusal codes

| Code | When |
|------|------|
| SL-HANDWRITING-NO-INK | No writable ink-like strokes in the supplied pixels |
| SL-HANDWRITING-UNSUPPORTED | Bad / corrupt image, or hosted non-PNG |
| SL-HANDWRITING-LIMIT | Hosted size / resolution cap (warning + 256 px analyze) |

## Known gaps (do not paper over)

1. This is not ESDA, not a Raman / FTIR / TLC lab, and not a court finding.
2. Width / darkness is a pressure *proxy*. Newtons are SLOT.
3. Taper / tremor are shape cues. Speed in mm/s is SLOT.
4. Clone-stamp flags digital copy-paste on the *scan*, not wet-ink identity.
5. Indent helper is the existing ISA-1.0 image enhancement, inject OFF — not electrostatic detection.
6. Hosted Worker is PNG / 256 px only.
7. No FragGate `handwriting` door until GitBaby patterns it — Worker + CLI only.
8. Confidence is pixel signal quality, never a forgery verdict.

## Tests that lock this

`tests/test_handwriting.py`: ops/card honesty, heavy vs light stroke weight,
compare / side-by-side, white-out erasure candidate, cloned-patch
`clone-stamp`, graph nodes, `SL-HANDWRITING-NO-INK`,
`SL-HANDWRITING-UNSUPPORTED`, helper modes cited not ESDA, CLI `--json`.
`tests/test_worker_modes.py` locks hosted `listHandwriting` + PNG analyze.
