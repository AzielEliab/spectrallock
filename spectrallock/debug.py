"""Debug traces to stderr when SPECTRALLOCK_DEBUG=1. Never logs image bytes."""

from __future__ import annotations

import os
import sys


def debug_enabled() -> bool:
    return os.environ.get("SPECTRALLOCK_DEBUG") == "1"


def debug(msg: str) -> None:
    """Print a short trace to stderr. Callers must never pass image bytes or b64."""
    if debug_enabled():
        print(f"spectrallock-debug: {msg}", file=sys.stderr)
