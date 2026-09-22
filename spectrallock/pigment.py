"""Restore lost pigment from pixels that still carry a signal.

Operator lock 2026-09-22. LIVE SpectralLock capability (lenses + ink/page + inject
stay in place). Estimates faded pigment only where the photograph still differs
from the page in a supported cluster. When that evidence is gone the op refuses
SL-PIGMENT-GONE and does not paint a mark.

Author: Aziel Eliab. Lamb Lens: Service → Clarity → Peace. NO-LIE.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import numpy as np

from spectrallock.engine import (
    finite01,
    gate_gray,
    luminance,
    parchment_estimate,
    png_bytes,
    sha256_hex,
)

PIGMENT_FAMILY = ("pigment", "restore-pigment")
PIGMENT_OPS = ("restore", "estimate", "refuse")
REFUSE_GONE = "SL-PIGMENT-GONE"
THRESH_FLOOR = 0.045
NOISE_K = 3.0
LUMA_GAP_MAX = 0.22
LUMA_GAP_MIN = 0.02
CHROMA_MIN = 0.03
MIN_SUPPORT_PIXELS = 24
MIN_SUPPORT_FRAC = 0.004
MAX_SUPPORT_FRAC = 0.85
NEIGHBOR_MIN = 3
GAIN = 1.7

PIGMENT_NOTE = (
    "Restore lost pigment estimates faded signal where pixels still differ from "
    "the page in a supported cluster. "
    "Visible dark ink is reported separately and is left as already-present pigment. "
    "When the faded signal is gone the op refuses " + REFUSE_GONE + " and writes no new marks. "
    "Invented marks stay false. "
    "pigment_recovery is true on this path because the path ran. "
    "Overlay, inject, and unredact receipts keep pigment_recovery false. "
    "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE."
)


def _package_version() -> str:
    from spectrallock import __version__

    return __version__


def parse_pigment_op(value: object, default: str = "restore") -> str:
    key = str(value or default).strip().lower().replace("_", "-")
    aliases = {
        "pigment": "restore",
        "restore": "restore",
        "restore-pigment": "restore",
        "lost-pigment": "restore",
        "restore-lost-pigment": "restore",
        "estimate": "estimate",
        "estimate-pigment": "estimate",
        "refuse": "refuse",
    }
    if key not in aliases:
        known = ", ".join(PIGMENT_OPS)
        raise ValueError(f"unknown pigment op {value!r}. Known: {known}")
    return aliases[key]


def pigment_mode_card() -> dict[str, Any]:
    return {
        "id": "pigment",
        "kid_label": "Restore pigment",
        "kid_hint": "Estimates faded pigment still in the pixels. Refuses when the signal is gone.",
        "paper": "PIGMENT",
        "status": "live",
        "hue": None,
        "hex": None,
        "aliases": ["restore-pigment", "lost-pigment", "restore-lost-pigment"],
        "summary": (
            "Restore lost pigment from supported pixel evidence. "
            "Refuses " + REFUSE_GONE + " when the signal is gone."
        ),
        "family": list(PIGMENT_FAMILY),
        "ops": list(PIGMENT_OPS),
        "refuse_code": REFUSE_GONE,
    }


def list_pigment() -> dict[str, Any]:
    return {
        "family": list(PIGMENT_FAMILY),
        "ops": list(PIGMENT_OPS),
        "status": "live",
        "refuse_code": REFUSE_GONE,
        "invented_marks": False,
        "note": PIGMENT_NOTE,
        "author": "Aziel Eliab",
        "mode": pigment_mode_card(),
    }


def _neighbor_support(faded: np.ndarray) -> np.ndarray:
    f = faded.astype(np.uint8)
    h, w = f.shape
    pad = np.pad(f, 1, mode="constant")
    acc = np.zeros((h, w), dtype=np.int16)
    for dy in range(3):
        for dx in range(3):
            acc += pad[dy : dy + h, dx : dx + w]
    return faded & (acc >= NEIGHBOR_MIN)


def _evidence(rgb: np.ndarray) -> dict[str, Any]:
    rgb = finite01(rgb)
    parch = parchment_estimate(rgb).astype(np.float32)
    lum = luminance(rgb)
    parch_lum = float(np.dot(parch, np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)))
    residual = parch.reshape(1, 1, 3) - rgb
    mag = np.linalg.norm(residual, axis=-1).astype(np.float32)
    bright = lum >= float(np.quantile(lum, 0.80))
    samples = mag[bright]
    if samples.size < 8:
        noise = 0.02
        base = 0.0
    else:
        noise = float(np.std(samples))
        base = float(np.mean(samples))
    thresh = max(THRESH_FLOOR, base + NOISE_K * noise)
    gap = parch_lum - lum
    chroma = residual.max(axis=-1) - residual.min(axis=-1)
    strong = gap > LUMA_GAP_MAX
    faded = (mag >= thresh) & (gap >= LUMA_GAP_MIN) & (gap <= LUMA_GAP_MAX) & (chroma >= CHROMA_MIN)
    support = _neighbor_support(faded)
    n = int(support.size)
    count = int(support.sum())
    frac = float(count) / float(n) if n else 0.0
    supported = count >= MIN_SUPPORT_PIXELS and MIN_SUPPORT_FRAC <= frac <= MAX_SUPPORT_FRAC
    return {
        "rgb": rgb,
        "parch": parch,
        "residual": residual,
        "mag": mag,
        "support": support,
        "strong": strong,
        "thresh": float(thresh),
        "count": count,
        "fraction": frac,
        "supported": supported,
        "visible_ink_pixels": int(strong.sum()),
        "parch_lum": parch_lum,
    }


def _restore_color(ev: dict[str, Any]) -> np.ndarray:
    rgb = ev["rgb"]
    out = rgb.copy()
    mask = ev["support"]
    if not np.any(mask):
        return out
    extra = (GAIN - 1.0) * ev["residual"][mask]
    out[mask] = np.clip(rgb[mask] - extra, 0.0, 1.0)
    return out.astype(np.float32)


def _density(ev: dict[str, Any]) -> np.ndarray:
    mag = ev["mag"]
    mask = ev["support"]
    out = np.zeros(mag.shape, dtype=np.float32)
    if not np.any(mask):
        return out
    peak = float(mag[mask].max())
    if peak <= 1e-6:
        return out
    out[mask] = np.clip(mag[mask] / peak, 0.0, 1.0)
    return out


def analyze_pigment(
    rgb: np.ndarray,
    *,
    op: str = "restore",
    inject: bool = True,
    filename: str = "",
    source_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Run the pigment path. pigment_recovery is true because this path ran."""
    key = parse_pigment_op(op)
    ev = _evidence(np.asarray(rgb, dtype=np.float32))
    src = ev["rgb"]
    color = _restore_color(ev) if ev["supported"] and key != "refuse" else src.copy()
    changed = int(np.count_nonzero(np.any(np.abs(color - src) > 1e-6, axis=-1)))
    recovered = bool(ev["supported"] and key != "refuse" and changed > 0)
    refuse = None if recovered else REFUSE_GONE
    if key == "refuse":
        refuse = REFUSE_GONE
        recovered = False
        color = src.copy()
        changed = 0
    visual = color if inject else gate_gray(color)
    # Gray inject must not be described as a new pigment mark off the support.
    if not recovered:
        visual = src if inject else gate_gray(src)
    density = _density(ev) if recovered else np.zeros(src.shape[:2], dtype=np.float32)
    mean_residual = [0.0, 0.0, 0.0]
    if recovered:
        mean_residual = [float(x) for x in ev["residual"][ev["support"]].mean(axis=0)]
    if recovered and key == "estimate":
        png = png_bytes(np.stack([density, density, density], axis=-1))
    elif recovered:
        png = png_bytes(visual)
    else:
        png = b""
    finding: dict[str, Any] = {
        "product": "spectrallock",
        "version": _package_version(),
        "author": "Aziel Eliab",
        "family": "pigment",
        "aliases": list(PIGMENT_FAMILY),
        "op": key,
        "mode": "pigment",
        "status": "live",
        "filename": filename,
        "width": int(src.shape[1]),
        "height": int(src.shape[0]),
        "pigment_recovery": True,
        "recovered": recovered,
        "refuse_code": refuse,
        "stop": refuse == REFUSE_GONE and not recovered,
        "evidence_pixels": int(ev["count"]) if key != "refuse" else 0,
        "evidence_fraction": float(ev["fraction"]) if key != "refuse" else 0.0,
        "visible_ink_pixels": int(ev["visible_ink_pixels"]),
        "threshold": float(ev["thresh"]),
        "parchment_rgb": [float(x) for x in ev["parch"]],
        "mean_residual_rgb": mean_residual,
        "pixels_changed": changed if recovered else 0,
        "unchanged_outside_support": True,
        "invented_marks": False,
        "wheel_paint_used": False,
        "spectral_triad_used_for_restore": False,
        "inject": bool(inject),
        "inject_applied": bool(inject) and recovered,
        "gain": GAIN if recovered else 0.0,
        "sha256_in": sha256_hex(source_bytes) if source_bytes is not None else sha256_hex(png_bytes(src)),
        "note": PIGMENT_NOTE,
        "advisory": PIGMENT_NOTE,
        "no_lie": True,
        "identity": "Aziel Eliab",
        "lamb_lens": "Service → Clarity → Peace",
    }
    if png:
        finding["png_b64"] = base64.b64encode(png).decode("ascii")
        finding["sha256_out"] = sha256_hex(png)
    else:
        finding["png_b64"] = None
        finding["sha256_out"] = None
    if recovered and key == "restore":
        # Prove off-support pixels were not rewritten on the color plane.
        off = ~ev["support"]
        finding["unchanged_outside_support"] = bool(np.array_equal(color[off], src[off]))
    return finding


def analyze_pigment_path(
    path: str,
    *,
    op: str = "restore",
    inject: bool = True,
) -> dict[str, Any]:
    from spectrallock.engine import load_rgb

    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(path)
    raw = src.read_bytes()
    rgb = load_rgb(str(src))
    return analyze_pigment(rgb, op=op, inject=inject, filename=src.name, source_bytes=raw)


def analyze_pigment_bytes(
    data: bytes,
    *,
    op: str = "restore",
    inject: bool = True,
    filename: str = "",
) -> dict[str, Any]:
    from spectrallock.engine import load_rgb_bytes

    rgb = load_rgb_bytes(data)
    return analyze_pigment(rgb, op=op, inject=inject, filename=filename, source_bytes=data)
