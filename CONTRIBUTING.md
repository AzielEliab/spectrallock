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
2. **Do not invent marks.** Balance (BSA) reweights Zen vs Chaos. It
   must not draw symbols that were not in the photograph.
3. **Synthetic UV is a simulation** of a 365–400 nm look from an
   ordinary photo. Do not imply a UV lamp or fluorescence hardware.
4. **Keep the dependency list tiny.** Pillow + numpy. No OpenCV.
5. **UI binds loopback only** (`127.0.0.1:8861`). Do not listen on `0.0.0.0`.
6. **Do not mix the download tracker** with any other product's Worker or KV.
7. New behavior needs a test that fails without the change.
8. Hosted `/v1/overlay` is a simplified preview (max 256 px). The full
   pipeline is this Python package.

## Where to change things

- Engines / formulas: `spectrallock/engine.py`
- CLI: `spectrallock/cli.py`
- Local UI: `spectrallock/ui.py`, `spectrallock/web/`
- Papers: `docs/source/`, spec: `docs/whitepaper.md`
- Hosted preview: `workers/download-tracker/src/overlay.js`
- Flutter approximation: `mobile/lib/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Copyright 2026 Aziel Eliab.
