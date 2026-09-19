"""SpectralLock overlay engines (Pillow + numpy). Rosetta spectral analysis.

RSA-2.0 family. Same SpectralLock lenses as Aziel Corpus Library OCR:
overlays plus ink/page targets. Balance never invents marks — it only
reweights existing readings. The human still reads the page.
"""

from __future__ import annotations

import hashlib
import io
import json
from dataclasses import dataclass
from typing import Callable

import numpy as np
from PIL import Image, ImageFilter

from spectrallock.debug import debug

__all__ = [
    "LIMITATION",
    "MODES",
    "LIVE_MODES",
    "LENSES",
    "TARGETS",
    "ROSETTA_WEIGHTS",
    "ZEN_WEIGHTS",
    "CHAOS_WEIGHTS",
    "TAZEL_HEX",
    "VYRN_HEX",
    "ZERO_HEX",
    "TAZEL_HUE",
    "VYRN_HUE",
    "ZERO_HUE",
    "OverlayResult",
    "apply_mode",
    "analyze",
    "apply_target",
    "compose_lenses",
    "normalize_lenses",
    "normalize_target",
    "list_modes",
    "list_lenses",
    "list_targets",
    "load_rgb",
    "save_rgb",
    "png_bytes",
    "sha256_hex",
    "make_receipt",
    "write_sidecar",
    "load_rgb_bytes",
    "finite01",
    "PLAIN_NOT_IMAGE",
    "MAX_IMAGE_PIXELS",
    "luminance",
    "normalize01",
    "center_of_mass",
    "blend_channels",
    "balance_blend",
    "zero_overlay",
    "tazel_overlay",
    "vyrn_overlay",
    "uv_overlay",
    "candle_overlay",
    "indent_overlay",
    "lemon_overlay",
    "rosetta_overlay",
    "zen_overlay",
    "chaos_overlay",
    "balance_overlay",
    "synthetic_page",
    "MODE_ALIASES",
    "STUB_MODES",
    "resolve_mode",
    "INJECT_NOTE",
    "TAZEL_INBAND_SIGMA",
    "VYRN_INBAND_SIGMA",
    "resolve_inject",
    "parse_inject",
    "inject_applied_for",
    "gate_gray",
    "inband_mask",
    "inband_pct",
    "gate_inband",
    "is_achromatic",
]

LIMITATION = (
    "Rosetta spectral analysis (RSA-2.0 family). SpectralLock lenses match "
    "Aziel Corpus Library OCR — overlays plus ink/page targets "
    "(zero, tazel, vyrn, uv, rosetta, zen, chaos, balance, candle, indent, lemon). "
    "Synthetic UV is a 365–400 nm look from an ordinary photograph. "
    "Candlelight is a warm flame-side look from an ordinary photo. "
    "Indent is an image-enhancement heuristic for surface relief. "
    "Lemon enhances heat-/acid-style browning already in the pixels; it never invents marks. "
    "Balance never invents marks. "
    "Inject ON is false-color membership tint (paint). "
    "OFF is luminance of the same gate. Zero ignores the switch. "
    "An empty gate is a valid reading. Copy-of-copy works only if the hue is still in-band. "
    "Unredact / lift-overlay locates leftover bytes and residual only — never invents letters. "
    "Opaque replace with no leftover container bytes refuses (SL-UNREDACT-OPAQUE). "
    "Heatmaps are residual overlays. "
    "Handwriting analysis is synthetic scan heuristics of ink-on-paper photos. "
    "Lamb Lens: Service → Clarity → Peace. "
    "The human still reads the page. Author Aziel Eliab."
)

INJECT_NOTE = (
    "ON paints membership (false color). OFF is the same gate as gray. "
    "Zero ignores the switch. "
    "UV is a synthetic 365–400 nm look from an ordinary photograph. Balance never invents marks. "
    "Report tazel_inband_pct and vyrn_inband_pct before claiming a hit. "
    "An empty gate is a valid reading. Copy-of-copy works only if the hue is still in-band."
)

TAZEL_HEX = "#1EC9A5"
VYRN_HEX = "#C00066"
ZERO_HEX = "#6F6485"
TAZEL_HUE = 170.0
VYRN_HUE = 350.0
ZERO_HUE = 260.0
TAZEL_RGB = (0x1E / 255.0, 0xC9 / 255.0, 0xA5 / 255.0)
VYRN_RGB = (0xC0 / 255.0, 0x00 / 255.0, 0x66 / 255.0)
ZERO_RGB = (0x6F / 255.0, 0x64 / 255.0, 0x85 / 255.0)
UV_RGB = (0.55, 0.45, 0.85)
CANDLE_RGB = (1.00, 0.62, 0.22)
INDENT_RGB = (0.72, 0.68, 0.58)
LEMON_RGB = (0.62, 0.38, 0.14)
CHAOS_RGB = (0.55, 0.22, 0.38)
TAZEL_INBAND_SIGMA = 24.0
VYRN_INBAND_SIGMA = 28.0
INBAND_SAT_MIN = 0.12
INBAND_VAL_MIN = 0.08
EPS = 1e-6
PLAIN_NOT_IMAGE = "That file is not a picture. Use a PNG or JPEG photo."
MAX_IMAGE_PIXELS = 40_000_000
ALLOWED_FORMATS = frozenset({"PNG", "JPEG"})

ROSETTA_WEIGHTS = {"zero": 0.40, "tazel": 0.35, "vyrn": 0.25}
ZEN_WEIGHTS = {"zero": 0.25, "tazel": 0.25, "uv": 0.25, "vyrn": 0.25}
CHAOS_WEIGHTS = {"uv": 0.40, "vyrn": 0.35, "tazel": 0.20, "zero": 0.05}


@dataclass(frozen=True)
class OverlayResult:
    rgb: np.ndarray
    mode: str
    com: tuple[float, float]
    width: int
    height: int
    paper: str
    channels: dict[str, np.ndarray] | None = None
    target: str = "ink"
    lenses: tuple[str, ...] = ()
    inject: bool = True
    inject_applied: bool = True
    tazel_inband_pct: float = 0.0
    vyrn_inband_pct: float = 0.0

    def to_meta(self) -> dict:
        lenses = list(self.lenses) or [self.mode]
        return {
            "mode": self.mode,
            "lens": lenses[0] if len(lenses) == 1 else "+".join(lenses),
            "lenses": lenses,
            "target": self.target,
            "com": {"x": self.com[0], "y": self.com[1]},
            "width": self.width,
            "height": self.height,
            "paper": self.paper,
            "inject": self.inject,
            "inject_applied": self.inject_applied,
            "inject_ignored": bool(self.inject) and not bool(self.inject_applied),
            "tazel_inband_pct": float(self.tazel_inband_pct),
            "vyrn_inband_pct": float(self.vyrn_inband_pct),
            "pigment_recovery": False,
            "empty_gate_not_broken_lens": True,
            "inject_note": INJECT_NOTE,
            "product": "spectrallock",
            "version": _package_version(),
            "rosetta_spectral_analysis": True,
            "corpus_ocr_aligned": True,
            "advisory": LIMITATION,
        }


def _package_version() -> str:
    from spectrallock import __version__

    return __version__


def finite01(arr: np.ndarray) -> np.ndarray:
    """Replace NaN/Inf, clip to 0–1. Never crash on a bad numeric pixel."""
    a = np.nan_to_num(np.asarray(arr, dtype=np.float32), nan=0.0, posinf=1.0, neginf=0.0)
    return np.clip(a, 0.0, 1.0).astype(np.float32)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def png_bytes(rgb: np.ndarray) -> bytes:
    arr = np.clip(np.round(finite01(rgb) * 255.0), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr, "RGB").save(buf, format="PNG")
    return buf.getvalue()


def make_receipt(
    *,
    mode: str,
    paper: str,
    sha256_in: str,
    sha256_out: str,
    size_in: int,
    size_out: int,
    width: int,
    height: int,
    target: str = "ink",
    lenses: list[str] | tuple[str, ...] | None = None,
    inject: bool = True,
    inject_applied: bool | None = None,
    tazel_inband_pct: float | None = None,
    vyrn_inband_pct: float | None = None,
) -> dict:
    lens_list = [str(x) for x in (lenses or [mode]) if str(x).strip()]
    applied = inject_applied_for(lens_list, inject) if inject_applied is None else bool(inject_applied)
    rec = {
        "product": "spectrallock",
        "version": _package_version(),
        "mode": mode,
        "lens": lens_list[0] if len(lens_list) == 1 else "+".join(lens_list),
        "lenses": lens_list,
        "target": normalize_target(target),
        "paper": paper,
        "sha256_in": sha256_in,
        "sha256_out": sha256_out,
        "size_in": int(size_in),
        "size_out": int(size_out),
        "width": int(width),
        "height": int(height),
        "inject": bool(inject),
        "inject_applied": applied,
        "inject_ignored": bool(inject) and not applied,
        "tazel_inband_pct": 0.0 if tazel_inband_pct is None else float(tazel_inband_pct),
        "vyrn_inband_pct": 0.0 if vyrn_inband_pct is None else float(vyrn_inband_pct),
        "pigment_recovery": False,
        "empty_gate_not_broken_lens": True,
        "inject_note": INJECT_NOTE,
        "limitation": LIMITATION,
        "advisory": LIMITATION,
        "rosetta_spectral_analysis": True,
        "corpus_ocr_aligned": True,
        "author": "Aziel Eliab",
    }
    return rec


def write_sidecar(png_path: str, payload: dict) -> str:
    lower = png_path.lower()
    if lower.endswith(".png") or lower.endswith(".jpg") or lower.endswith(".jpeg"):
        dest = png_path[: png_path.rfind(".")] + ".json"
    else:
        dest = png_path + ".json"
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    debug(f"sidecar path={dest} keys={sorted(payload)}")
    return dest


def _open_rgb_image(img: Image.Image) -> np.ndarray:
    fmt = (img.format or "").upper()
    if fmt not in ALLOWED_FORMATS:
        raise ValueError(PLAIN_NOT_IMAGE)
    width, height = img.size
    if width <= 0 or height <= 0 or (width * height) > MAX_IMAGE_PIXELS:
        raise ValueError("That picture is too big to open safely.")
    if img.mode != "RGB":
        img = img.convert("RGB")
    return finite01(np.asarray(img, dtype=np.float32) / 255.0)


def load_rgb(path: str) -> np.ndarray:
    try:
        img = Image.open(path)
        img.load()
    except Exception as exc:  # noqa: BLE001
        debug(f"load_rgb failed type={type(exc).__name__}")
        raise ValueError(PLAIN_NOT_IMAGE) from exc
    rgb = _open_rgb_image(img)
    debug(f"load_rgb format={(img.format or '').upper()} size={rgb.shape[1]}x{rgb.shape[0]}")
    return rgb


def load_rgb_bytes(raw: bytes) -> np.ndarray:
    if not raw:
        raise ValueError("No picture in the upload.")
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception as exc:  # noqa: BLE001
        debug(f"load_rgb_bytes failed type={type(exc).__name__} nbytes={len(raw)}")
        raise ValueError(PLAIN_NOT_IMAGE) from exc
    rgb = _open_rgb_image(img)
    debug(f"load_rgb_bytes format={(img.format or '').upper()} size={rgb.shape[1]}x{rgb.shape[0]} nbytes={len(raw)}")
    return rgb


def save_rgb(rgb: np.ndarray, path: str) -> None:
    with open(path, "wb") as fh:
        fh.write(png_bytes(rgb))


def luminance(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def normalize01(arr: np.ndarray) -> np.ndarray:
    a = arr.astype(np.float32)
    lo = float(a.min())
    hi = float(a.max())
    if hi - lo < EPS:
        return np.zeros_like(a, dtype=np.float32)
    return ((a - lo) / (hi - lo)).astype(np.float32)


def center_of_mass(lum: np.ndarray) -> tuple[float, float]:
    h, w = lum.shape
    y_idx, x_idx = np.indices((h, w), dtype=np.float64)
    weights = np.clip(lum.astype(np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= EPS:
        return (w / 2.0, h / 2.0)
    cx = float((x_idx * weights).sum() / total)
    cy = float((y_idx * weights).sum() / total)
    return (cx, cy)


def _as_image(arr: np.ndarray, mode: str) -> Image.Image:
    if mode == "L":
        u8 = np.clip(np.round(arr * 255.0), 0, 255).astype(np.uint8)
        return Image.fromarray(u8, "L")
    u8 = np.clip(np.round(arr * 255.0), 0, 255).astype(np.uint8)
    return Image.fromarray(u8, "RGB")


def blur_gray(gray: np.ndarray, radius: float) -> np.ndarray:
    img = _as_image(gray, "L").filter(ImageFilter.GaussianBlur(radius=radius))
    return np.asarray(img, dtype=np.float32) / 255.0


def blur_rgb(rgb: np.ndarray, radius: float) -> np.ndarray:
    img = _as_image(rgb, "RGB").filter(ImageFilter.GaussianBlur(radius=radius))
    return np.asarray(img, dtype=np.float32) / 255.0


def equalize(gray: np.ndarray) -> np.ndarray:
    g = np.clip(gray, 0.0, 1.0)
    hist, _ = np.histogram(g.ravel(), bins=256, range=(0.0, 1.0))
    cdf = hist.cumsum().astype(np.float64)
    if cdf[-1] <= 0:
        return g.astype(np.float32)
    cdf = cdf / cdf[-1]
    idx = np.clip((g * 255.0).astype(np.int32), 0, 255)
    return cdf[idx].astype(np.float32)


def unsharp(gray: np.ndarray, amount: float = 0.7, radius: float = 1.2) -> np.ndarray:
    low = blur_gray(gray, radius)
    return np.clip(gray + amount * (gray - low), 0.0, 1.0).astype(np.float32)


def gray_to_rgb(gray: np.ndarray) -> np.ndarray:
    g = gray.astype(np.float32)
    return np.stack([g, g, g], axis=-1)


def tint_gray(gray: np.ndarray, color: tuple[float, float, float], amount: float = 0.28) -> np.ndarray:
    g = gray[..., None]
    c = np.asarray(color, dtype=np.float32)
    return np.clip(g * ((1.0 - amount) + amount * c * 1.6), 0.0, 1.0).astype(np.float32)


def resolve_inject(*, inject: bool | None = None, tint: bool | None = None) -> bool:
    """Public switch is inject. tint is a back-compat alias."""
    if inject is not None:
        return bool(inject)
    if tint is not None:
        return bool(tint)
    return True


def parse_inject(value: object, default: bool = True) -> bool:
    """Parse CLI / JSON / form inject flags. ON paints; OFF is gray."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return bool(value)
    key = str(value).strip().lower()
    if key in {"0", "false", "off", "no", "no-inject", "n"}:
        return False
    if key in {"1", "true", "on", "yes", "inject", "y"}:
        return True
    return default


def inject_applied_for(lenses: str | list[str] | tuple[str, ...], inject: bool) -> bool:
    """Zero ignores the switch. Applied only when a non-zero lens is painted."""
    if not inject:
        return False
    if isinstance(lenses, str):
        keys = [part.strip().lower() for part in lenses.replace("+", ",").split(",") if part.strip()]
    else:
        keys = [str(part).strip().lower() for part in lenses if str(part).strip()]
    if not keys:
        return True
    return any(key != "zero" for key in keys)


def gate_gray(rgb: np.ndarray) -> np.ndarray:
    """Luminance of the same gate — inject OFF."""
    return gray_to_rgb(luminance(finite01(rgb)))


def maybe_gate_paint(gate_rgb: np.ndarray, *, inject: bool, mode: str = "") -> np.ndarray:
    if mode == "zero" or not inject:
        return gate_gray(gate_rgb)
    return finite01(gate_rgb)


def inband_mask(rgb: np.ndarray, hue: float, sigma: float) -> np.ndarray:
    """In-band membership: hue within σ and enough chroma. Empty ≠ broken."""
    h, s, v = rgb_to_hsv(finite01(rgb))
    return (hue_distance(h, hue) <= sigma) & (s >= INBAND_SAT_MIN) & (v >= INBAND_VAL_MIN)


def inband_pct(rgb: np.ndarray, hue: float, sigma: float) -> float:
    mask = inband_mask(rgb, hue, sigma)
    return round(100.0 * float(mask.mean()), 2)


def gate_inband(rgb: np.ndarray) -> dict[str, float]:
    """tazel 170° / vyrn 350° in-band percents from the source photo."""
    return {
        "tazel_inband_pct": inband_pct(rgb, TAZEL_HUE, TAZEL_INBAND_SIGMA),
        "vyrn_inband_pct": inband_pct(rgb, VYRN_HUE, VYRN_INBAND_SIGMA),
    }


def is_achromatic(rgb: np.ndarray, atol: float = 2e-3) -> bool:
    """True when R≈G≈B (inject OFF / zero)."""
    arr = finite01(rgb)
    return bool(
        np.allclose(arr[..., 0], arr[..., 1], atol=atol)
        and np.allclose(arr[..., 1], arr[..., 2], atol=atol)
    )


def hue_distance(h: np.ndarray, target: float) -> np.ndarray:
    d = np.abs(h - target)
    return np.minimum(d, 360.0 - d)


def rgb_to_hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rgb = np.clip(rgb, 0.0, 1.0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    v = maxc
    delta = maxc - minc
    s = np.divide(delta, maxc, out=np.zeros_like(maxc), where=maxc > EPS)
    h = np.zeros_like(maxc)
    mask_r = (delta > EPS) & (maxc == r)
    mask_g = (delta > EPS) & (maxc == g) & ~mask_r
    mask_b = (delta > EPS) & (maxc == b) & ~mask_r & ~mask_g
    h = np.where(mask_r, np.mod((g - b) / np.maximum(delta, EPS), 6.0), h)
    h = np.where(mask_g, (b - r) / np.maximum(delta, EPS) + 2.0, h)
    h = np.where(mask_b, (r - g) / np.maximum(delta, EPS) + 4.0, h)
    return h * 60.0, s, v


def hsv_to_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    h = np.mod(h, 360.0)
    c = v * s
    hp = h / 60.0
    x = c * (1.0 - np.abs(np.mod(hp, 2.0) - 1.0))
    m = v - c
    z = np.zeros_like(h)
    i = np.floor(hp).astype(np.int32) % 6
    rp = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [c, x, z, z, x, c], default=z)
    gp = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [x, c, c, x, z, z], default=z)
    bp = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [z, z, x, c, c, x], default=z)
    return np.clip(np.stack([rp + m, gp + m, bp + m], axis=-1), 0.0, 1.0).astype(np.float32)


def blend_channels(channels: dict[str, np.ndarray], weights: dict[str, float]) -> np.ndarray:
    """Weighted sum of already-normalized 0–1 arrays (broadcast-safe)."""
    acc = None
    for name, w in weights.items():
        arr = channels[name].astype(np.float32)
        term = w * arr
        acc = term if acc is None else acc + term
    assert acc is not None
    return acc.astype(np.float32)


def balance_blend(
    zen_rgb: np.ndarray,
    chaos_rgb: np.ndarray,
    eps: float = EPS,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """BSA: B=(Zn-Cn)/(Zn+Cn+ε), α=(1+B)/2, RGB = α·Zen + (1-α)·Chaos."""
    zn = normalize01(luminance(zen_rgb))
    cn = normalize01(luminance(chaos_rgb))
    b = (zn - cn) / (zn + cn + eps)
    alpha = (1.0 + b) / 2.0
    out = alpha[..., None] * zen_rgb + (1.0 - alpha[..., None]) * chaos_rgb
    return np.clip(out, 0.0, 1.0).astype(np.float32), b.astype(np.float32), alpha.astype(np.float32)


def _midtone_lift(gray: np.ndarray, amount: float = 0.12) -> np.ndarray:
    mid = 4.0 * gray * (1.0 - gray)
    return np.clip(gray + amount * mid, 0.0, 1.0).astype(np.float32)


def zero_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """ZSA-1.0: grayscale, hist-eq, mild band-pass, unsharp grooves.

    Inject is ignored — zero stays gray either way.
    """
    del inject
    gray = luminance(rgb)
    gray = equalize(gray)
    # band-pass: medium-scale curvature (blur-subtract)
    fine = blur_gray(gray, 0.8)
    coarse = blur_gray(gray, 7.0)
    band = np.clip(0.5 + (fine - coarse) * 1.35, 0.0, 1.0)
    mixed = np.clip(0.55 * gray + 0.45 * band, 0.0, 1.0)
    sharp = unsharp(mixed, amount=0.85, radius=1.0)
    return gray_to_rgb(sharp)


def tazel_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """TSA-1.0: 170° #1EC9A5 teal heat on in-band pixels when inject ON.

    OFF is luminance of the same gate (gray). Not recovered pigment.
    """
    h, s, v = rgb_to_hsv(rgb)
    w = np.exp(-0.5 * (hue_distance(h, TAZEL_HUE) / TAZEL_INBAND_SIGMA) ** 2)
    s2 = np.clip(s * (1.0 + 0.65 * w) + 0.10 * w, 0.0, 1.0)
    v2 = np.clip(v * (1.0 + 0.28 * w) + 0.06 * w, 0.0, 1.0)
    v2 = _midtone_lift(v2, amount=0.16)
    v2 = unsharp(v2, amount=0.55, radius=0.8)
    low = blur_gray(v2, 11.0)
    detail = v2 - low
    v2 = np.clip(low * 0.88 + 0.06 + detail * 1.55, 0.0, 1.0)
    out = hsv_to_rgb(h, s2, v2)
    if not inject:
        return gate_gray(out)
    # teal heat on in-band pixels — paint, not pigment
    tint = np.asarray(TAZEL_RGB, dtype=np.float32)
    out = np.clip(out * (1.0 - 0.18 * w[..., None]) + tint * (v2 * 0.18 * w)[..., None], 0.0, 1.0)
    return out.astype(np.float32)


def vyrn_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """VSA-1.0: 350° #C00066 magenta heat on in-band pixels when inject ON.

    OFF is luminance of the same gate (gray). Not recovered pigment.
    """
    h, s, v = rgb_to_hsv(rgb)
    w = np.exp(-0.5 * (hue_distance(h, VYRN_HUE) / VYRN_INBAND_SIGMA) ** 2)
    cyan = np.exp(-0.5 * (hue_distance(h, 160.0) / 32.0) ** 2)
    s2 = np.clip(s * (1.0 + 0.7 * w) * (1.0 - 0.55 * cyan) + 0.08 * w, 0.0, 1.0)
    v2 = np.clip(v * (1.0 + 0.22 * w) * (1.0 - 0.18 * cyan), 0.0, 1.0)
    v2 = unsharp(v2, amount=0.95, radius=0.9)
    # wash background: compress large-scale parchment
    low = blur_gray(v2, 10.0)
    v2 = np.clip((v2 - low) * 1.45 + 0.42 + 0.25 * v2, 0.0, 1.0)
    out = hsv_to_rgb(h, s2, v2)
    if not inject:
        return gate_gray(out)
    tint = np.asarray(VYRN_RGB, dtype=np.float32)
    out = np.clip(out * (1.0 - 0.22 * w[..., None]) + tint * (np.clip(v2, 0, 1) * 0.22 * w)[..., None], 0.0, 1.0)
    # suppress residual green
    out[..., 1] = np.clip(out[..., 1] * (1.0 - 0.25 * cyan), 0.0, 1.0)
    return out.astype(np.float32)


def uv_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """UVSA-1.0: synthetic 365–400 nm look. Boost parchment, blue-violet, microtexture, ink darker.

    Still synthetic, not a lamp. Inject OFF is gray of the same UV gate.
    """
    lum = luminance(rgb)
    t = normalize01(lum)
    # parchment glow (high luma), ink absorbs (low luma)
    glow = np.clip(np.power(np.clip(t, 0.0, 1.0), 0.72) * 1.18, 0.0, 1.0)
    glow = glow * (1.0 - 0.42 * (1.0 - t))
    hp = lum - blur_gray(lum, 1.15)
    glow = np.clip(glow + hp * 0.9, 0.0, 1.0)
    # blue-violet weighting
    r = np.clip(glow * 0.70 + 0.04, 0.0, 1.0)
    g = np.clip(glow * 0.62 + 0.03, 0.0, 1.0)
    b = np.clip(glow * 1.18 + hp * 0.35, 0.0, 1.0)
    out = np.stack([r, g, b], axis=-1)
    # ink darker
    ink = (t < 0.42).astype(np.float32)
    out = out * (1.0 - 0.35 * ink[..., None])
    out = np.clip(out, 0.0, 1.0).astype(np.float32)
    return out if inject else gate_gray(out)


def candle_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """CLSA-1.0: warm flame-side look (~1800–2700K) from an ordinary photo.

    Not real multispectral capture. Amber parchment glow; ink stays readable.
    """
    rgb = finite01(rgb)
    h, w = rgb.shape[:2]
    lum = luminance(rgb)
    t = normalize01(lum)
    # left = flame side (brighter / warmer)
    flame = np.broadcast_to(np.linspace(1.0, 0.58, w, dtype=np.float32), (h, w))
    glow = np.clip(np.power(np.clip(t, 0.0, 1.0), 0.82) * (0.78 + 0.28 * flame), 0.0, 1.0)
    ink = np.clip((0.44 - t) / 0.44, 0.0, 1.0)
    r = np.clip(rgb[..., 0] * 0.42 + glow * 1.16 + 0.05, 0.0, 1.0)
    g = np.clip(rgb[..., 1] * 0.40 + glow * 0.70 + 0.02, 0.0, 1.0)
    b = np.clip(rgb[..., 2] * 0.22 + glow * 0.26, 0.0, 1.0)
    out = np.stack([r, g, b], axis=-1)
    # keep dark strokes readable from the source pixels
    out = out * (1.0 - 0.40 * ink[..., None]) + rgb * (0.28 * ink[..., None])
    out = np.clip(out, 0.0, 1.0).astype(np.float32)
    return out if inject else gate_gray(out)


def indent_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """ISA-1.0: suppress visible ink; lift fiber / pressure relief.

    Image-enhancement heuristic from an ordinary photo. Not ESDA / electrostatic
    detection, and not a claim of recovering invisible writing with certainty.
    Prefer target=page; ink|page both allowed.
    """
    rgb = finite01(rgb)
    lum = luminance(rgb)
    t = normalize01(lum)
    parchment = parchment_estimate(rgb)
    ink = np.clip((0.52 - t) / 0.52, 0.0, 1.0)
    washed = rgb * (1.0 - 0.84 * ink[..., None]) + parchment * (0.84 * ink[..., None])
    fine = blur_gray(lum, 0.7)
    coarse = blur_gray(lum, 5.5)
    relief = normalize01(np.abs(fine - coarse))
    hp = lum - blur_gray(lum, 1.3)
    gray = luminance(washed)
    mixed = np.clip(gray * 0.58 + relief * 0.62 + hp * 0.90 + 0.16, 0.0, 1.0)
    mixed = unsharp(mixed, amount=0.78, radius=0.9)
    out = washed * 0.42 + gray_to_rgb(mixed) * 0.58
    out = np.clip(out, 0.0, 1.0).astype(np.float32)
    return out if inject else gate_gray(out)


def lemon_overlay(rgb: np.ndarray, *, inject: bool = True) -> np.ndarray:
    """LISA-1.0: heat-/acid-style lemon (citrus) invisible-ink cues.

    Reweights warm browning already in the pixels. Not a chemical test.
    Never invents marks that are not supported by the photograph.
    """
    rgb = finite01(rgb)
    h, s, v = rgb_to_hsv(rgb)
    brown = np.exp(-0.5 * (hue_distance(h, 36.0) / 22.0) ** 2)
    warm = np.exp(-0.5 * (hue_distance(h, 28.0) / 30.0) ** 2)
    w = np.clip(0.65 * brown + 0.35 * warm, 0.0, 1.0)
    # support: existing chroma near midtones — no invented strokes
    mid = np.clip(1.0 - np.abs(v - 0.42) / 0.45, 0.0, 1.0)
    support = np.clip(s * 1.85, 0.0, 1.0) * mid
    gain = w * support
    s2 = np.clip(s * (1.0 + 0.58 * gain) + 0.04 * gain, 0.0, 1.0)
    v2 = unsharp(np.clip(v * (1.0 + 0.10 * gain) - 0.07 * gain, 0.0, 1.0), amount=0.42, radius=1.0)
    out = hsv_to_rgb(h, s2, v2)
    tint = np.array(LEMON_RGB, dtype=np.float32)
    out = np.clip(out * (1.0 - 0.22 * gain[..., None]) + tint * (v2 * 0.22 * gain)[..., None], 0.0, 1.0)
    out = out.astype(np.float32)
    return out if inject else gate_gray(out)


def _channel_luma(rgb: np.ndarray, fn: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
    return normalize01(luminance(fn(rgb)))


def _composite_from_luma(
    luma: np.ndarray,
    tint: tuple[float, float, float] | None,
) -> np.ndarray:
    if tint is None:
        return gray_to_rgb(np.clip(luma, 0.0, 1.0))
    return tint_gray(np.clip(luma, 0.0, 1.0), tint)


def _base_channels(rgb: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "zero": _channel_luma(rgb, zero_overlay),
        "tazel": _channel_luma(rgb, tazel_overlay),
        "vyrn": _channel_luma(rgb, vyrn_overlay),
        "uv": _channel_luma(rgb, uv_overlay),
    }


def _composite_paint(*, inject: bool | None = None, tint: bool | None = None) -> bool:
    return resolve_inject(inject=inject, tint=tint)


def rosetta_overlay(
    rgb: np.ndarray,
    *,
    inject: bool | None = None,
    tint: bool | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """RSA-2.0 = 0.40·Z′ + 0.35·T′ + 0.25·V′ after per-channel normalize.

    Inject ON = composite tint. OFF = gray of the same mix. Not pigment.
    """
    ch = _base_channels(rgb)
    mix = blend_channels(ch, ROSETTA_WEIGHTS)
    color = (0.40 * np.array(ZERO_RGB) + 0.35 * np.array(TAZEL_RGB) + 0.25 * np.array(VYRN_RGB))
    out = _composite_from_luma(mix, tuple(color) if _composite_paint(inject=inject, tint=tint) else None)
    return out, ch


def zen_overlay(
    rgb: np.ndarray,
    *,
    inject: bool | None = None,
    tint: bool | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """ZENA-1.0 = (Z′ + T′ + U′ + V′) / 4 after normalize."""
    ch = _base_channels(rgb)
    mix = blend_channels(ch, ZEN_WEIGHTS)
    color = tuple((np.array(ZERO_RGB) + np.array(TAZEL_RGB) + np.array(VYRN_RGB) + np.array(UV_RGB)) / 4.0)
    out = _composite_from_luma(mix, color if _composite_paint(inject=inject, tint=tint) else None)
    return out, ch


def chaos_overlay(
    rgb: np.ndarray,
    *,
    inject: bool | None = None,
    tint: bool | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """CSA-1.0 = 0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′ after normalize."""
    ch = _base_channels(rgb)
    mix = blend_channels(ch, CHAOS_WEIGHTS)
    out = _composite_from_luma(mix, CHAOS_RGB if _composite_paint(inject=inject, tint=tint) else None)
    return out, ch


def balance_overlay(
    rgb: np.ndarray,
    *,
    inject: bool | None = None,
    tint: bool | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """BSA: α·Zen + (1-α)·Chaos. Never invents marks. Inject OFF is gray of that mix."""
    paint = _composite_paint(inject=inject, tint=tint)
    zen_rgb, ch = zen_overlay(rgb, inject=paint)
    chaos_rgb, _ = chaos_overlay(rgb, inject=paint)
    out, _b, _a = balance_blend(zen_rgb, chaos_rgb)
    return out if paint else gate_gray(out), ch


def synthetic_page(width: int = 96, height: int = 96) -> np.ndarray:
    """Cream parchment, dark strokes, faint cyan understroke, magenta correction."""
    img = np.empty((height, width, 3), dtype=np.float32)
    img[:] = (0.93, 0.88, 0.76)
    # dark main strokes
    img[42:50, 8 : width - 8] = (0.12, 0.09, 0.06)
    img[18:22, 12 : width // 2] = (0.16, 0.12, 0.08)
    # faint cyan understroke (tazel target)
    parchment = np.array([0.93, 0.88, 0.76], dtype=np.float32)
    cyan = np.array([0.10, 0.72, 0.62], dtype=np.float32)
    img[62:67, 10 : width - 12] = 0.78 * parchment + 0.22 * cyan
    # magenta correction (vyrn target)
    img[24:30, 20 : width - 18] = (0.78, 0.08, 0.42)
    # faint heat-style brown (lemon cue) — only when the canvas is tall enough
    if height >= 80 and width >= 28:
        brown = np.array([0.58, 0.36, 0.16], dtype=np.float32)
        img[74:79, 14 : width - 14] = 0.70 * parchment + 0.30 * brown
    # pressure groove: slight luma dip, not ink
    if height >= 88 and width >= 16:
        img[84:86, 8 : width - 8] *= 0.88
    return img


INJECT_RGB: dict[str, tuple[float, float, float]] = {
    "zero": ZERO_RGB,
    "tazel": TAZEL_RGB,
    "vyrn": VYRN_RGB,
    "uv": UV_RGB,
    "rosetta": tuple(
        0.40 * np.array(ZERO_RGB) + 0.35 * np.array(TAZEL_RGB) + 0.25 * np.array(VYRN_RGB)
    ),
    "zen": tuple((np.array(ZERO_RGB) + np.array(TAZEL_RGB) + np.array(VYRN_RGB) + np.array(UV_RGB)) / 4.0),
    "chaos": CHAOS_RGB,
    "balance": tuple((np.array(UV_RGB) + np.array(CHAOS_RGB)) / 2.0),
    "candle": CANDLE_RGB,
    "indent": INDENT_RGB,
    "lemon": LEMON_RGB,
}


def _pack(
    mode: str,
    rgb_out: np.ndarray,
    paper: str,
    channels=None,
    *,
    source: np.ndarray | None = None,
    target: str = "ink",
    lenses: list[str] | tuple[str, ...] | None = None,
    inject: bool = True,
) -> OverlayResult:
    clean = finite01(rgb_out)
    h, w = clean.shape[:2]
    src = finite01(source) if source is not None else clean
    lum = luminance(src)
    lens_tuple = tuple(lenses) if lenses else (mode,)
    inband = gate_inband(src)
    applied = inject_applied_for(lens_tuple, inject)
    return OverlayResult(
        rgb=clean,
        mode=mode,
        com=center_of_mass(lum),
        width=w,
        height=h,
        paper=paper,
        channels=channels,
        target=normalize_target(target),
        lenses=lens_tuple,
        inject=bool(inject),
        inject_applied=applied,
        tazel_inband_pct=inband["tazel_inband_pct"],
        vyrn_inband_pct=inband["vyrn_inband_pct"],
    )


def normalize_target(target: str | None) -> str:
    key = str(target or "ink").strip().lower()
    if key in {"page", "parchment", "substrate", "folio"}:
        return "page"
    return "ink"


def normalize_lenses(
    mode: str | list[str] | tuple[str, ...] | None = None,
    lens: str | list[str] | tuple[str, ...] | None = None,
    lenses: str | list[str] | tuple[str, ...] | None = None,
) -> list[str]:
    raw: list[object] = []
    for item in (lenses, lens, mode):
        if item is None or item == "":
            continue
        if isinstance(item, (list, tuple)):
            raw.extend(item)
        else:
            raw.extend(str(item).replace("+", ",").split(","))
    out: list[str] = []
    for item in raw:
        key = str(item or "").strip().lower()
        if not key:
            continue
        key = resolve_mode(key, kind="lens")
        if key not in out:
            out.append(key)
    return out or ["rosetta"]


def parchment_estimate(rgb: np.ndarray) -> np.ndarray:
    """Mean color of the brightest quintile — from the photo, not invented."""
    lum = luminance(rgb)
    q = float(np.quantile(lum, 0.80))
    mask = lum >= q
    if not np.any(mask):
        return rgb.reshape(-1, 3).mean(axis=0).astype(np.float32)
    return rgb[mask].mean(axis=0).astype(np.float32)


def apply_target(rgb: np.ndarray, target: str = "ink") -> np.ndarray:
    """Ink isolates writing; page isolates parchment/substrate. Reweights only."""
    key = normalize_target(target)
    rgb = finite01(rgb)
    lum = luminance(rgb)
    t = normalize01(lum)
    parchment = parchment_estimate(rgb)
    if key == "page":
        ink = np.clip((0.50 - t) / 0.50, 0.0, 1.0)
        out = rgb * (1.0 - 0.72 * ink[..., None]) + parchment * (0.72 * ink[..., None])
        hp = lum - blur_gray(lum, 1.4)
        out = np.clip(out + hp[..., None] * 0.35, 0.0, 1.0)
        return out.astype(np.float32)
    page = np.clip((t - 0.38) / 0.40, 0.0, 1.0)
    ink = (t < 0.48).astype(np.float32)
    washed = rgb * (1.0 - 0.50 * page[..., None]) + parchment * (0.50 * page[..., None])
    out = washed * (1.0 - 0.28 * ink[..., None])
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def compose_lenses(
    rgb: np.ndarray,
    lenses: list[str],
    *,
    inject: bool | None = None,
    tint: bool | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Equal mix of selected lens luma — same multi-lens checkbox family as Corpus OCR."""
    paint = resolve_inject(inject=inject, tint=tint)
    rgb = finite01(rgb)
    selected = normalize_lenses(lenses=lenses)
    channels: dict[str, np.ndarray] = {}
    for name in selected:
        result = apply_mode(rgb, name, inject=paint)
        channels[name] = normalize01(luminance(result.rgb))
    if len(selected) == 1:
        return apply_mode(rgb, selected[0], inject=paint).rgb, channels
    weight = 1.0 / float(len(selected))
    mix = blend_channels(channels, {name: weight for name in selected})
    mix = np.clip(mix, 0.0, 1.0)
    if paint and inject_applied_for(selected, True):
        colors = [np.asarray(INJECT_RGB.get(name, (0.70, 0.70, 0.70)), dtype=np.float32) for name in selected]
        avg = tuple(float(x) for x in sum(colors) / float(len(colors)))
        return tint_gray(mix, avg), channels
    return gray_to_rgb(mix), channels


def analyze(
    rgb: np.ndarray,
    mode: str | list[str] | tuple[str, ...] | None = None,
    *,
    lens: str | list[str] | tuple[str, ...] | None = None,
    lenses: str | list[str] | tuple[str, ...] | None = None,
    target: str = "ink",
    inject: bool | None = None,
    tint: bool | None = None,
) -> OverlayResult:
    """Rosetta spectral analysis: lens overlay(s) then ink/page target."""
    selected = normalize_lenses(mode=mode, lens=lens, lenses=lenses)
    dest = normalize_target(target)
    paint = resolve_inject(inject=inject, tint=tint)
    rgb = finite01(rgb)
    debug(f"analyze lenses={selected} target={dest} inject={paint} size={rgb.shape[1]}x{rgb.shape[0]}")
    if len(selected) == 1:
        base = apply_mode(rgb, selected[0], inject=paint)
        out = apply_target(base.rgb, dest)
        paper = base.paper
        channels = base.channels
        key = selected[0]
    else:
        mixed, channels = compose_lenses(rgb, selected, inject=paint)
        out = apply_target(mixed, dest)
        paper = "MULTI"
        key = "+".join(selected)
    return _pack(key, out, paper, channels, source=rgb, target=dest, lenses=selected, inject=paint)


def apply_mode(
    rgb: np.ndarray,
    mode: str,
    *,
    inject: bool | None = None,
    tint: bool | None = None,
) -> OverlayResult:
    key = resolve_mode(mode)
    paint = resolve_inject(inject=inject, tint=tint)
    rgb = finite01(rgb)
    debug(f"apply_mode mode={key} inject={paint} size={rgb.shape[1]}x{rgb.shape[0]}")
    info = MODES[key]
    if key == "zero":
        return _pack(key, zero_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "tazel":
        return _pack(key, tazel_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "vyrn":
        return _pack(key, vyrn_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "uv":
        return _pack(key, uv_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "candle":
        return _pack(key, candle_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "indent":
        return _pack(key, indent_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "lemon":
        return _pack(key, lemon_overlay(rgb, inject=paint), info["paper"], source=rgb, inject=paint)
    if key == "rosetta":
        out, ch = rosetta_overlay(rgb, inject=paint)
        return _pack(key, out, info["paper"], ch, source=rgb, inject=paint)
    if key == "zen":
        out, ch = zen_overlay(rgb, inject=paint)
        return _pack(key, out, info["paper"], ch, source=rgb, inject=paint)
    if key == "chaos":
        out, ch = chaos_overlay(rgb, inject=paint)
        return _pack(key, out, info["paper"], ch, source=rgb, inject=paint)
    if key == "balance":
        out, ch = balance_overlay(rgb, inject=paint)
        return _pack(key, out, info["paper"], ch, source=rgb, inject=paint)
    raise ValueError(f"unknown mode {mode!r}")


MODES: dict[str, dict] = {
    "zero": {
        "id": "zero",
        "kid_label": "Clearer lines",
        "kid_hint": "Grayscale that shows grooves already in the photo. Not hidden-ink magic.",
        "paper": "ZSA-1.0",
        "status": "live",
        "hue": ZERO_HUE,
        "hex": ZERO_HEX,
        "summary": "Equilibrium / geometry. Grayscale, hist-eq, band-pass, unsharp.",
    },
    "tazel": {
        "id": "tazel",
        "kid_label": "Lift green-gold",
        "kid_hint": "Boosts turquoise marks that are already there.",
        "paper": "TSA-1.0",
        "status": "live",
        "hue": TAZEL_HUE,
        "hex": TAZEL_HEX,
        "summary": "Revelation. Boost green–gold–turquoise (~170°, #1EC9A5).",
    },
    "vyrn": {
        "id": "vyrn",
        "kid_label": "Lift magenta",
        "kid_hint": "Boosts red-violet marks that are already there.",
        "paper": "VSA-1.0",
        "status": "live",
        "hue": VYRN_HUE,
        "hex": VYRN_HEX,
        "summary": "Purification / pressure. Boost magenta–red-violet (~350°, #C00066).",
    },
    "uv": {
        "id": "uv",
        "kid_label": "Fake UV look",
        "kid_hint": "Ultraviolet light analysis (synthetic). A 365–400 nm look from an ordinary photo.",
        "paper": "UVSA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "aliases": ["ultraviolet", "uv-light", "uvsa"],
        "summary": "Ultraviolet light analysis (synthetic). 365–400 nm look from an ordinary photograph.",
    },
    "rosetta": {
        "id": "rosetta",
        "kid_label": "Rosetta",
        "kid_hint": "RSA-2.0 decoding composite: zero + tazel + vyrn. Same Rosetta lens as Corpus OCR.",
        "paper": "RSA-2.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "summary": "Rosetta spectral analysis RSA-2.0 = 0.40·Z′ + 0.35·T′ + 0.25·V′ after normalize.",
    },
    "zen": {
        "id": "zen",
        "kid_label": "Even mix of four",
        "kid_hint": "Averages four overlays. Advisory only.",
        "paper": "ZENA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "summary": "(Z′ + T′ + U′ + V′) / 4 after normalize.",
    },
    "chaos": {
        "id": "chaos",
        "kid_label": "Strong mix",
        "kid_hint": "Heavier UV and magenta mix. Advisory only.",
        "paper": "CSA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "summary": "0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′ after normalize.",
    },
    "balance": {
        "id": "balance",
        "kid_label": "Blend two mixes",
        "kid_hint": "Mixes zen and chaos. Never invents marks.",
        "paper": "BSA",
        "status": "live",
        "hue": None,
        "hex": None,
        "summary": "B=(Zn-Cn)/(Zn+Cn+ε), α=(1+B)/2, RGB=α·Zen+(1-α)·Chaos. Never invents marks.",
    },
    "candle": {
        "id": "candle",
        "kid_label": "Candlelight",
        "kid_hint": "Warm flame-side look from an ordinary photo.",
        "paper": "CLSA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "aliases": ["candlelight", "candle-light"],
        "summary": "Candlelight analysis (synthetic). Amber ~1800–2700K flame-side look; parchment glow; ink readable.",
    },
    "indent": {
        "id": "indent",
        "kid_label": "Ink-suppress / indent",
        "kid_hint": "Washes visible ink so paper fibers and pressure dents are easier to look at. Prefer Page.",
        "paper": "ISA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "aliases": ["indentation", "suppress-ink", "ink-suppress", "revealer-indent"],
        "preferred_target": "page",
        "summary": "Ink-suppress / indentation reveal (synthetic). Image-enhancement heuristic for fiber and pressure relief. Prefer target=page.",
    },
    "lemon": {
        "id": "lemon",
        "kid_label": "Hidden lemon ink",
        "kid_hint": "Boosts warm browning already in the photo. Never invents marks.",
        "paper": "LISA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "aliases": ["lemon-ink", "hidden-lemon", "invisible-ink-lemon"],
        "summary": "Hidden lemon ink analysis (synthetic). Heat-/acid-style citrus browning from existing pixels. Not a chemical test. Never invents marks.",
    },
}

MODE_ALIASES: dict[str, str] = {
    "candlelight": "candle",
    "candle-light": "candle",
    "ultraviolet": "uv",
    "uv-light": "uv",
    "uvsa": "uv",
    "indentation": "indent",
    "suppress-ink": "indent",
    "ink-suppress": "indent",
    "revealer-indent": "indent",
    "lemon-ink": "lemon",
    "hidden-lemon": "lemon",
    "invisible-ink-lemon": "lemon",
}

STUB_MODES: dict[str, dict] = {
    "spectrometer": {
        "id": "spectrometer",
        "status": "stub",
        "refuse": "spectrometer is a stub. SpectralLock is synthetic image analysis from an ordinary photograph, not a lab instrument.",
    },
    "forensic": {
        "id": "forensic",
        "status": "stub",
        "refuse": "forensic is a stub. SpectralLock is not forensic certification.",
    },
    "invent_mark": {
        "id": "invent_mark",
        "status": "stub",
        "refuse": "invent_mark is a stub and stays refused. SpectralLock never invents marks.",
    },
}


def resolve_mode(name: str, *, kind: str = "mode") -> str:
    """Map a lens id or alias to a canonical LIVE mode. Stubs refuse honestly."""
    key = str(name or "").strip().lower()
    if key in MODES:
        return key
    alias = MODE_ALIASES.get(key)
    if alias:
        return alias
    if key in STUB_MODES:
        raise ValueError(STUB_MODES[key]["refuse"])
    known = ", ".join(MODES)
    raise ValueError(f"unknown {kind} {name!r}. Known: {known}")

LIVE_MODES = tuple(MODES.keys())
LENSES = LIVE_MODES

TARGETS: dict[str, dict] = {
    "ink": {
        "id": "ink",
        "kid_label": "Ink",
        "kid_hint": "Isolate writing. Same ink target as Aziel Corpus Library OCR.",
        "summary": "Ink mode: crush parchment, keep strokes. Reweights existing pixels only.",
        "status": "live",
    },
    "page": {
        "id": "page",
        "kid_label": "Page",
        "kid_hint": "Isolate parchment and substrate. Same page target as Aziel Corpus Library OCR.",
        "summary": "Page mode: lift substrate, wash ink. Reweights existing pixels only.",
        "status": "live",
    },
}


def list_modes() -> list[dict]:
    return [dict(v) for v in MODES.values()]


def list_lenses() -> list[dict]:
    return list_modes()


def list_targets() -> list[dict]:
    return [dict(v) for v in TARGETS.values()]
