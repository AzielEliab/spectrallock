"""SpectralLock: digital overlay analysis of manuscript photographs.

August 2026. Aziel Eliab. Apache-2.0.

Advisory visualization on ordinary photographs of manuscript pages.
Not a lab spectrometer, not real UV hardware, not a forensic proof of
hidden ink, not OCR, not a claim of scribal truth. The human still
reads the page. Forks are welcome and always allowed.
"""

from __future__ import annotations

from spectrallock.engine import (
    CHAOS_WEIGHTS,
    LIMITATION,
    LIVE_MODES,
    MODES,
    ROSETTA_WEIGHTS,
    ZEN_WEIGHTS,
    OverlayResult,
    apply_mode,
    list_modes,
)

__version__ = "0.1.0"
__author__ = "Aziel Eliab"
__all__ = [
    "LIMITATION",
    "MODES",
    "LIVE_MODES",
    "ROSETTA_WEIGHTS",
    "ZEN_WEIGHTS",
    "CHAOS_WEIGHTS",
    "OverlayResult",
    "apply_mode",
    "list_modes",
    "__version__",
]
