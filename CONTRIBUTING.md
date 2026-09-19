# Contributing to SpectralLock

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is Pillow + numpy (no OpenCV). pytest is the dev extra.
No network.

## Ground rules

1. **Rosetta spectral analysis.** Same SpectralLock lenses as Aziel
   Corpus Library OCR: overlays plus ink/page targets. Digital
   reweighting of photographs of manuscript pages. The human still
   reads the page. Author Aziel Eliab only.
2. **Do not invent marks.** Balance (BSA) reweights Zen vs Chaos. Lemon
   and indent only reweight pixels already in the photograph. They must
   not draw symbols that were not there. `invent_mark` stays a stub.
3. **Synthetic looks are simulations** from an ordinary photo: UV
   (365–400 nm look), candlelight (warm flame-side), indent (fiber /
   pressure heuristic, not ESDA), lemon (heat-style browning, not a
   chemical test). Do not imply a lamp, lab instrument, or forensic
   certification. `spectrometer` and `forensic` stay stubs.
4. **Keep the dependency list tiny.** Pillow + numpy. No OpenCV.
5. **UI binds loopback only** (`127.0.0.1:8861`). Do not listen on `0.0.0.0`.
6. **Do not mix the download tracker** with any other product's Worker or KV.
7. **Door vs local op.** `/v1/mesh/*` PROXY to aziel-runtime. Local ops are `/v1/{op}` only.
   Suite mesh default OFF; QNM rollup live|locked|isolated; no Node Gate;
   no auto-heal; not anonymity.
8. New behavior needs a test that fails without the change.
9. Hosted `/v1/overlay` is a simplified preview (max 256 px). The full
   pipeline is this Python package (`spectrallock_inject.py` for the color
   inject switch). Inject ON is paint, not recovered pigment. Zero ignores
   the switch. Report in-band percents before any hit claim.

## Where to change things

- Engines / formulas: `spectrallock/engine.py`
- CLI: `spectrallock/cli.py`, inject card: `spectrallock/inject.py`, `spectrallock_inject.py`
- Local UI: `spectrallock/ui.py`, `spectrallock/web/`
- Papers: `docs/source/`, spec: `docs/whitepaper.md`, runtime sync: `docs/runtime-sync.md`
- Hosted preview: `workers/download-tracker/src/overlay.js`
- Suite mesh / QNM Live Nodes: `workers/download-tracker/src/mesh.js` (`/v1/mesh/*` PROXY to aziel-runtime). QNS-CD-1.0 is a hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). Not a Softwares-tab product. No public qnsd proxy.
- Flutter approximation: `mobile/lib/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Copyright 2026 Aziel Eliab.
