"""SpectralLock: Rosetta spectral analysis software.

August 2026. Aziel Eliab. Apache-2.0.

RSA-2.0 family. Same SpectralLock lenses as Aziel Corpus Library OCR
(overlays, ink/page modes). Balance never invents marks. The human
still reads the page. Forks are welcome and always allowed.
"""

from __future__ import annotations

from spectrallock.engine import (
    CHAOS_WEIGHTS,
    INJECT_NOTE,
    LENSES,
    LIMITATION,
    LIVE_MODES,
    MODE_ALIASES,
    MODES,
    PLAIN_NOT_IMAGE,
    ROSETTA_WEIGHTS,
    STUB_MODES,
    TARGETS,
    ZEN_WEIGHTS,
    OverlayResult,
    analyze,
    apply_mode,
    apply_target,
    compose_lenses,
    gate_inband,
    inject_applied_for,
    list_lenses,
    list_modes,
    list_targets,
    make_receipt,
    normalize_lenses,
    normalize_target,
    parse_inject,
    png_bytes,
    resolve_inject,
    resolve_mode,
    sha256_hex,
    write_sidecar,
)

__version__ = "0.3.0"
__author__ = "Aziel Eliab"
__all__ = [
    "LIMITATION",
    "MODES",
    "LIVE_MODES",
    "MODE_ALIASES",
    "STUB_MODES",
    "LENSES",
    "TARGETS",
    "ROSETTA_WEIGHTS",
    "ZEN_WEIGHTS",
    "CHAOS_WEIGHTS",
    "INJECT_NOTE",
    "OverlayResult",
    "analyze",
    "apply_mode",
    "apply_target",
    "compose_lenses",
    "gate_inband",
    "inject_applied_for",
    "list_modes",
    "list_lenses",
    "list_targets",
    "make_receipt",
    "normalize_lenses",
    "normalize_target",
    "parse_inject",
    "resolve_inject",
    "resolve_mode",
    "png_bytes",
    "sha256_hex",
    "write_sidecar",
    "PLAIN_NOT_IMAGE",
    "__version__",
]
