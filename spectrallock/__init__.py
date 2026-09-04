"""SpectralLock: Rosetta spectral analysis software.

August 2026. Aziel Eliab. Apache-2.0.

RSA-2.0 family. Same SpectralLock lenses as Aziel Corpus Library OCR
(overlays, ink/page modes). Balance never invents marks. The human
still reads the page. Forks are welcome and always allowed.
"""

from __future__ import annotations

from spectrallock.engine import (
    CHAOS_WEIGHTS,
    LENSES,
    LIMITATION,
    LIVE_MODES,
    MODES,
    PLAIN_NOT_IMAGE,
    ROSETTA_WEIGHTS,
    TARGETS,
    ZEN_WEIGHTS,
    OverlayResult,
    analyze,
    apply_mode,
    apply_target,
    compose_lenses,
    list_lenses,
    list_modes,
    list_targets,
    make_receipt,
    normalize_lenses,
    normalize_target,
    png_bytes,
    sha256_hex,
    write_sidecar,
)

__version__ = "0.3.0"
__author__ = "Aziel Eliab"
__all__ = [
    "LIMITATION",
    "MODES",
    "LIVE_MODES",
    "LENSES",
    "TARGETS",
    "ROSETTA_WEIGHTS",
    "ZEN_WEIGHTS",
    "CHAOS_WEIGHTS",
    "OverlayResult",
    "analyze",
    "apply_mode",
    "apply_target",
    "compose_lenses",
    "list_modes",
    "list_lenses",
    "list_targets",
    "make_receipt",
    "normalize_lenses",
    "normalize_target",
    "png_bytes",
    "sha256_hex",
    "write_sidecar",
    "PLAIN_NOT_IMAGE",
    "__version__",
]
