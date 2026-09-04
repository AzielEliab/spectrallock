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
    "rosetta_overlay",
    "zen_overlay",
    "chaos_overlay",
    "balance_overlay",
    "synthetic_page",
]

LIMITATION = (
    "Rosetta spectral analysis (RSA-2.0 family). SpectralLock lenses match "
    "Aziel Corpus Library OCR — overlays plus ink/page targets "
    "(zero, tazel, vyrn, uv, rosetta, zen, chaos, balance). "
    "Synthetic UV is a 365–400 nm look from an ordinary photograph. "
    "Balance never invents marks. The human still reads the page. "
    "Author Aziel Eliab."
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
) -> dict:
    lens_list = [str(x) for x in (lenses or [mode]) if str(x).strip()]
    return {
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
        "limitation": LIMITATION,
        "advisory": LIMITATION,
        "rosetta_spectral_analysis": True,
        "corpus_ocr_aligned": True,
        "author": "Aziel Eliab",
    }


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


def zero_overlay(rgb: np.ndarray) -> np.ndarray:
    """ZSA-1.0: grayscale, hist-eq, mild band-pass, unsharp grooves."""
    gray = luminance(rgb)
    gray = equalize(gray)
    # band-pass: medium-scale curvature (blur-subtract)
    fine = blur_gray(gray, 0.8)
    coarse = blur_gray(gray, 7.0)
    band = np.clip(0.5 + (fine - coarse) * 1.35, 0.0, 1.0)
    mixed = np.clip(0.55 * gray + 0.45 * band, 0.0, 1.0)
    sharp = unsharp(mixed, amount=0.85, radius=1.0)
    return gray_to_rgb(sharp)


def tazel_overlay(rgb: np.ndarray) -> np.ndarray:
    """TSA-1.0: boost hue ~170° (#1EC9A5), lift midtones, fine lines, parchment smooth."""
    h, s, v = rgb_to_hsv(rgb)
    w = np.exp(-0.5 * (hue_distance(h, TAZEL_HUE) / 24.0) ** 2)
    s2 = np.clip(s * (1.0 + 0.65 * w) + 0.10 * w, 0.0, 1.0)
    v2 = np.clip(v * (1.0 + 0.28 * w) + 0.06 * w, 0.0, 1.0)
    v2 = _midtone_lift(v2, amount=0.16)
    v2 = unsharp(v2, amount=0.55, radius=0.8)
    low = blur_gray(v2, 11.0)
    detail = v2 - low
    v2 = np.clip(low * 0.88 + 0.06 + detail * 1.55, 0.0, 1.0)
    out = hsv_to_rgb(h, s2, v2)
    # extra turquoise pull on weighted pixels
    tint = np.asarray(TAZEL_RGB, dtype=np.float32)
    out = np.clip(out * (1.0 - 0.18 * w[..., None]) + tint * (v2 * 0.18 * w)[..., None], 0.0, 1.0)
    return out.astype(np.float32)


def vyrn_overlay(rgb: np.ndarray) -> np.ndarray:
    """VSA-1.0: boost hue ~350° (#C00066), suppress green/cyan, edge/pressure, wash bg."""
    h, s, v = rgb_to_hsv(rgb)
    w = np.exp(-0.5 * (hue_distance(h, VYRN_HUE) / 28.0) ** 2)
    cyan = np.exp(-0.5 * (hue_distance(h, 160.0) / 32.0) ** 2)
    s2 = np.clip(s * (1.0 + 0.7 * w) * (1.0 - 0.55 * cyan) + 0.08 * w, 0.0, 1.0)
    v2 = np.clip(v * (1.0 + 0.22 * w) * (1.0 - 0.18 * cyan), 0.0, 1.0)
    v2 = unsharp(v2, amount=0.95, radius=0.9)
    # wash background: compress large-scale parchment
    low = blur_gray(v2, 10.0)
    v2 = np.clip((v2 - low) * 1.45 + 0.42 + 0.25 * v2, 0.0, 1.0)
    out = hsv_to_rgb(h, s2, v2)
    tint = np.asarray(VYRN_RGB, dtype=np.float32)
    out = np.clip(out * (1.0 - 0.22 * w[..., None]) + tint * (np.clip(v2, 0, 1) * 0.22 * w)[..., None], 0.0, 1.0)
    # suppress residual green
    out[..., 1] = np.clip(out[..., 1] * (1.0 - 0.25 * cyan), 0.0, 1.0)
    return out.astype(np.float32)


def uv_overlay(rgb: np.ndarray) -> np.ndarray:
    """UVSA-1.0: synthetic 365–400 nm look. Boost parchment, blue-violet, microtexture, ink darker."""
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
    return np.clip(out, 0.0, 1.0).astype(np.float32)


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


def rosetta_overlay(rgb: np.ndarray, *, tint: bool = True) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """RSA-2.0 = 0.40·Z′ + 0.35·T′ + 0.25·V′ after per-channel normalize."""
    ch = _base_channels(rgb)
    mix = blend_channels(ch, ROSETTA_WEIGHTS)
    color = (0.40 * np.array(ZERO_RGB) + 0.35 * np.array(TAZEL_RGB) + 0.25 * np.array(VYRN_RGB))
    out = _composite_from_luma(mix, tuple(color) if tint else None)
    return out, ch


def zen_overlay(rgb: np.ndarray, *, tint: bool = True) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """ZENA-1.0 = (Z′ + T′ + U′ + V′) / 4 after normalize."""
    ch = _base_channels(rgb)
    mix = blend_channels(ch, ZEN_WEIGHTS)
    color = tuple((np.array(ZERO_RGB) + np.array(TAZEL_RGB) + np.array(VYRN_RGB) + np.array([0.55, 0.45, 0.85])) / 4.0)
    out = _composite_from_luma(mix, color if tint else None)
    return out, ch


def chaos_overlay(rgb: np.ndarray, *, tint: bool = True) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """CSA-1.0 = 0.40·U′ + 0.35·V′ + 0.20·T′ + 0.05·Z′ after normalize."""
    ch = _base_channels(rgb)
    mix = blend_channels(ch, CHAOS_WEIGHTS)
    color = (0.55, 0.22, 0.38)
    out = _composite_from_luma(mix, color if tint else None)
    return out, ch


def balance_overlay(rgb: np.ndarray, *, tint: bool = True) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """BSA: α·Zen + (1-α)·Chaos. Never invents marks."""
    zen_rgb, ch = zen_overlay(rgb, tint=tint)
    chaos_rgb, _ = chaos_overlay(rgb, tint=tint)
    out, _b, _a = balance_blend(zen_rgb, chaos_rgb)
    return out, ch


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
    return img


def _pack(
    mode: str,
    rgb_out: np.ndarray,
    paper: str,
    channels=None,
    *,
    source: np.ndarray | None = None,
    target: str = "ink",
    lenses: list[str] | tuple[str, ...] | None = None,
) -> OverlayResult:
    clean = finite01(rgb_out)
    h, w = clean.shape[:2]
    lum = luminance(finite01(source) if source is not None else clean)
    lens_tuple = tuple(lenses) if lenses else (mode,)
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
        if key not in MODES:
            known = ", ".join(MODES)
            raise ValueError(f"unknown lens {key!r}. Known: {known}")
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


def compose_lenses(rgb: np.ndarray, lenses: list[str], *, tint: bool = True) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Equal mix of selected lens luma — same multi-lens checkbox family as Corpus OCR."""
    rgb = finite01(rgb)
    selected = normalize_lenses(lenses=lenses)
    channels: dict[str, np.ndarray] = {}
    for name in selected:
        result = apply_mode(rgb, name, tint=tint)
        channels[name] = normalize01(luminance(result.rgb))
    if len(selected) == 1:
        return apply_mode(rgb, selected[0], tint=tint).rgb, channels
    weight = 1.0 / float(len(selected))
    mix = blend_channels(channels, {name: weight for name in selected})
    return gray_to_rgb(np.clip(mix, 0.0, 1.0)), channels


def analyze(
    rgb: np.ndarray,
    mode: str | list[str] | tuple[str, ...] | None = None,
    *,
    lens: str | list[str] | tuple[str, ...] | None = None,
    lenses: str | list[str] | tuple[str, ...] | None = None,
    target: str = "ink",
    tint: bool = True,
) -> OverlayResult:
    """Rosetta spectral analysis: lens overlay(s) then ink/page target."""
    selected = normalize_lenses(mode=mode, lens=lens, lenses=lenses)
    dest = normalize_target(target)
    rgb = finite01(rgb)
    debug(f"analyze lenses={selected} target={dest} size={rgb.shape[1]}x{rgb.shape[0]}")
    if len(selected) == 1:
        base = apply_mode(rgb, selected[0], tint=tint)
        out = apply_target(base.rgb, dest)
        paper = base.paper
        channels = base.channels
        key = selected[0]
    else:
        mixed, channels = compose_lenses(rgb, selected, tint=tint)
        out = apply_target(mixed, dest)
        paper = "MULTI"
        key = "+".join(selected)
    return _pack(key, out, paper, channels, source=rgb, target=dest, lenses=selected)


def apply_mode(rgb: np.ndarray, mode: str, *, tint: bool = True) -> OverlayResult:
    key = (mode or "").strip().lower()
    if key not in MODES:
        known = ", ".join(MODES)
        raise ValueError(f"unknown mode {mode!r}. Known: {known}")
    rgb = finite01(rgb)
    debug(f"apply_mode mode={key} size={rgb.shape[1]}x{rgb.shape[0]}")
    info = MODES[key]
    if key == "zero":
        return _pack(key, zero_overlay(rgb), info["paper"], source=rgb)
    if key == "tazel":
        return _pack(key, tazel_overlay(rgb), info["paper"], source=rgb)
    if key == "vyrn":
        return _pack(key, vyrn_overlay(rgb), info["paper"], source=rgb)
    if key == "uv":
        return _pack(key, uv_overlay(rgb), info["paper"], source=rgb)
    if key == "rosetta":
        out, ch = rosetta_overlay(rgb, tint=tint)
        return _pack(key, out, info["paper"], ch, source=rgb)
    if key == "zen":
        out, ch = zen_overlay(rgb, tint=tint)
        return _pack(key, out, info["paper"], ch, source=rgb)
    if key == "chaos":
        out, ch = chaos_overlay(rgb, tint=tint)
        return _pack(key, out, info["paper"], ch, source=rgb)
    if key == "balance":
        out, ch = balance_overlay(rgb, tint=tint)
        return _pack(key, out, info["paper"], ch, source=rgb)
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
        "kid_hint": "A 365–400 nm look from an ordinary photo. Not a real UV lamp.",
        "paper": "UVSA-1.0",
        "status": "live",
        "hue": None,
        "hex": None,
        "summary": "Synthetic 365–400 nm simulation. Not a real UV lamp.",
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
}

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
