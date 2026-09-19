#!/usr/bin/env python3
"""SpectralLock color inject switch — operator card CLI (19 Sep 2026).

    python3 spectrallock_inject.py page.jpg --mode vyrn --inject -o vyrn_on.jpg
    python3 spectrallock_inject.py page.jpg --mode vyrn --no-inject -o vyrn_off.jpg
    python3 spectrallock_inject.py page.jpg --all --inject --outdir out/
    python3 spectrallock_inject.py page.jpg --all --no-inject --outdir out_plain/
    python3 spectrallock_inject.py page.jpg --mode zero --target ink --no-inject

ON paints membership (false color). OFF is the same gate as gray.
ON is not recovered pigment. Zero ignores the switch.
Prefer this local package path over the hosted Worker overlay.
Author: Aziel Eliab. Lamb Lens: Service → Clarity → Peace. NO-LIE.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python3 spectrallock_inject.py` from a checkout without install.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from spectrallock.inject import main

if __name__ == "__main__":
    raise SystemExit(main())
