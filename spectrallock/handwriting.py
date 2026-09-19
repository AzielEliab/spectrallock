"""SpectralLock handwriting analysis — synthetic scan heuristics.

Physical ink on paper, from user-supplied scans/photos only.
NOT a lab instrument. NOT ESDA. NOT chemical dating. NOT a court
examiner opinion. NOT writer identification as identity fact.

Indicators / heuristics / candidates — human verification required.
Confidence is signal quality from present pixels, not “this is forged.”

Author: Aziel Eliab. Lamb Lens: Service → Clarity → Peace. NO-LIE.
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from spectrallock.engine import (
    INJECT_NOTE,
    LIMITATION,
    apply_mode,
    blur_gray,
    candle_overlay,
    finite01,
    indent_overlay,
    lemon_overlay,
    load_rgb_bytes,
    luminance,
    normalize01,
    png_bytes,
    uv_overlay,
)

HANDWRITING_FAMILY = ("handwriting", "handwrite", "ink-hand", "forgery-scan")
HANDWRITING_OPS = (
    "analyze",
    "compare",
    "side-by-side",
    "graph",
    "forgery-indicators",
    "refuse",
)
REFUSE_NO_INK = "SL-HANDWRITING-NO-INK"
REFUSE_UNSUPPORTED = "SL-HANDWRITING-UNSUPPORTED"
REFUSE_LIMIT = "SL-HANDWRITING-LIMIT"

HOSTED_MAX_SIDE = 256
LOCAL_ANALYZE_SIDE = 640

HANDWRITING_NOTE = (
    "Handwriting analysis is synthetic image analysis of a user-supplied "
    "scan or photo of paper. Stroke weight, speed cues, bleed, erasures, "
    "tracing, and forgery indicators are heuristics from present pixels. "
    "They are candidates — human verification required. "
    "Not ESDA, not chemical ink dating, not a court-qualified examiner "
    "opinion, and not writer identification as an identity fact. "
    "Heatmaps are not transcripts and not court findings. "
    "Empty gate ≠ broken lens. Balance/lemon never invent marks. "
    "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE."
)

FEATURE_MATRIX = {
    "stroke_weight": {"status": "live", "note": "width from ink mask + chamfer distance"},
    "speed_cues": {"status": "live", "note": "taper / tremor / ballistic vs controlled — heuristic only"},
    "ink_density": {"status": "live", "note": "darkness of ink-mask pixels"},
    "bleed_feathering": {"status": "live", "note": "edge gradient width / capillary-spread proxy"},
    "handwriting_shifts": {"status": "live", "note": "baseline drift, slant, size change"},
    "erasures": {"status": "live", "note": "abrasion brightening + mid-gray ghosts"},
    "tracing": {"status": "live", "note": "doubled ridges, width uniformity, lift clustering"},
    "tremor_copy": {"status": "live", "note": "high-frequency path wobble + slow uniform width"},
    "pen_lifts": {"status": "live", "note": "connected-component breaks"},
    "retouch_overwrite": {"status": "live", "note": "dark-on-dark intersections"},
    "dual_ink": {"status": "live", "note": "hue clusters in stroke pixels"},
    "baseline_misalign": {"status": "live", "note": "row centroid drift"},
    "indent_helper": {"status": "live", "note": "existing indent mode inject-OFF; not ESDA"},
    "clone_stamp": {"status": "live", "note": "repeated block hashes far apart"},
    "compression_paste": {"status": "live", "note": "8×8 block energy discontinuities"},
    "ductus": {"status": "live", "note": "gradient-direction consistency"},
    "style_shift": {"status": "live", "note": "component aspect-ratio regime change — heuristic flag only"},
    "pressure_newtons": {"status": "slot", "note": "no force sensor; width/darkness is a proxy only"},
    "speed_mm_s": {"status": "slot", "note": "no temporal capture; taper/tremor are shape cues"},
    "writer_identity": {"status": "slot", "note": "never claimed as identity fact"},
    "esda": {"status": "slot", "note": "not electrostatic detection"},
    "chemical_ink_dating": {"status": "slot", "note": "not a lab assay"},
    "court_examiner_opinion": {"status": "slot", "note": "not a qualified examiner finding"},
}


def parse_handwriting_op(value: object, default: str = "analyze") -> str:
    key = str(value or default).strip().lower().replace("_", "-")
    aliases = {
        "analyze": "analyze",
        "handwriting": "analyze",
        "handwrite": "analyze",
        "ink-hand": "analyze",
        "forgery-scan": "forgery-indicators",
        "compare": "compare",
        "side-by-side": "side-by-side",
        "sidebyside": "side-by-side",
        "graph": "graph",
        "forgery-indicators": "forgery-indicators",
        "forgery": "forgery-indicators",
        "refuse": "refuse",
    }
    if key not in aliases:
        raise ValueError(f"unknown handwriting op {value!r}. Known: {', '.join(HANDWRITING_OPS)}")
    return aliases[key]


def list_handwriting() -> dict[str, Any]:
    live = sorted(k for k, v in FEATURE_MATRIX.items() if v["status"] == "live")
    slot = sorted(k for k, v in FEATURE_MATRIX.items() if v["status"] == "slot")
    return {
        "family": "handwriting",
        "aliases": list(HANDWRITING_FAMILY),
        "ops": list(HANDWRITING_OPS),
        "refuse_codes": [REFUSE_NO_INK, REFUSE_UNSUPPORTED, REFUSE_LIMIT],
        "feature_matrix": {k: dict(v) for k, v in FEATURE_MATRIX.items()},
        "live_signals": live,
        "slot_signals": slot,
        "no_lie": True,
        "guessed_letters": False,
        "forensic_certification": False,
        "esda": False,
        "chemical_ink_dating": False,
        "writer_identification_as_fact": False,
        "heatmap_is_transcript": False,
        "heatmap_is_court_finding": False,
        "catalog_door": False,
        "worker_path": "/v1/handwriting",
        "note": HANDWRITING_NOTE,
        "author": "Aziel Eliab",
        "status": "live",
    }


def _sha(arr: np.ndarray) -> str:
    raw = np.clip(np.round(finite01(arr) * 255.0), 0, 255).astype(np.uint8).tobytes()
    return hashlib.sha256(raw).hexdigest()


def _cap(rgb: np.ndarray, max_side: int) -> tuple[np.ndarray, float]:
    h, w = rgb.shape[:2]
    side = max(h, w)
    if side <= max_side:
        return rgb, 1.0
    scale = max_side / float(side)
    try:
        from PIL import Image

        img = Image.fromarray(np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8), "RGB")
        nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
        img = img.resize((nw, nh), Image.Resampling.BILINEAR)
        return np.asarray(img, dtype=np.float32) / 255.0, scale
    except Exception:
        return rgb, 1.0


def _ink_mask(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    lum = luminance(finite01(rgb))
    paper = float(np.percentile(lum, 88))
    thresh = max(0.08, paper - 0.16)
    ink = lum < thresh
    # drop isolated speckles
    pad = np.pad(ink.astype(np.uint8), 1)
    neigh = (
        pad[:-2, :-2] + pad[:-2, 1:-1] + pad[:-2, 2:]
        + pad[1:-1, :-2] + pad[1:-1, 2:]
        + pad[2:, :-2] + pad[2:, 1:-1] + pad[2:, 2:]
    )
    ink = ink & (neigh >= 2)
    frac = float(ink.mean()) if ink.size else 0.0
    return ink, lum, frac


def _chamfer(mask: np.ndarray) -> np.ndarray:
    """Cheap 2-pass chamfer distance (pixels) inside the ink mask."""
    h, w = mask.shape
    inf = h + w + 2
    dt = np.where(mask, 0.0, inf).astype(np.float32)
    # inside-mask distance to background: invert first
    inside = mask
    dt = np.where(inside, inf, 0.0).astype(np.float32)
    dt[~inside] = 0.0
    dt[inside] = inf
    for y in range(h):
        for x in range(w):
            if not inside[y, x]:
                continue
            best = dt[y, x]
            if y:
                best = min(best, dt[y - 1, x] + 1.0)
                if x:
                    best = min(best, dt[y - 1, x - 1] + 1.414)
            if x:
                best = min(best, dt[y, x - 1] + 1.0)
            dt[y, x] = best
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if not inside[y, x]:
                continue
            best = dt[y, x]
            if y + 1 < h:
                best = min(best, dt[y + 1, x] + 1.0)
                if x + 1 < w:
                    best = min(best, dt[y + 1, x + 1] + 1.414)
            if x + 1 < w:
                best = min(best, dt[y, x + 1] + 1.0)
            dt[y, x] = best
    dt[~inside] = 0.0
    return dt


def _label(mask: np.ndarray, limit: int = 48) -> list[dict[str, Any]]:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=np.uint8)
    comps: list[dict[str, Any]] = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(y, x)]
            seen[y, x] = 1
            ys = [y]
            xs = [x]
            while stack and len(ys) < 80_000:
                cy, cx = stack.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = 1
                            stack.append((ny, nx))
                            ys.append(ny)
                            xs.append(nx)
            if len(ys) < 8:
                continue
            y0, y1 = min(ys), max(ys)
            x0, x1 = min(xs), max(xs)
            comps.append({
                "id": f"s{len(comps)}",
                "bbox": [int(x0), int(y0), int(x1), int(y1)],
                "area": int(len(ys)),
                "cx": float(np.mean(xs)),
                "cy": float(np.mean(ys)),
                "width": float(x1 - x0 + 1),
                "height": float(y1 - y0 + 1),
                "aspect": float((x1 - x0 + 1) / max(1, y1 - y0 + 1)),
            })
            if len(comps) >= limit:
                return comps
    comps.sort(key=lambda c: (c["cx"], c["cy"]))
    for i, c in enumerate(comps):
        c["id"] = f"s{i}"
    return comps


def _sobel(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    pad = np.pad(gray, 1, mode="edge")
    gx = (
        kx[0, 0] * pad[:-2, :-2] + kx[0, 1] * pad[:-2, 1:-1] + kx[0, 2] * pad[:-2, 2:]
        + kx[1, 0] * pad[1:-1, :-2] + kx[1, 1] * pad[1:-1, 1:-1] + kx[1, 2] * pad[1:-1, 2:]
        + kx[2, 0] * pad[2:, :-2] + kx[2, 1] * pad[2:, 1:-1] + kx[2, 2] * pad[2:, 2:]
    )
    gy = (
        ky[0, 0] * pad[:-2, :-2] + ky[0, 1] * pad[:-2, 1:-1] + ky[0, 2] * pad[:-2, 2:]
        + ky[1, 0] * pad[1:-1, :-2] + ky[1, 1] * pad[1:-1, 1:-1] + ky[1, 2] * pad[1:-1, 2:]
        + ky[2, 0] * pad[2:, :-2] + ky[2, 1] * pad[2:, 1:-1] + ky[2, 2] * pad[2:, 2:]
    )
    return gx, gy


def _block_hashes(lum: np.ndarray, size: int = 8) -> list[tuple[int, int, int]]:
    h, w = lum.shape
    out = []
    for y in range(0, h - size + 1, size):
        for x in range(0, w - size + 1, size):
            tile = lum[y : y + size, x : x + size]
            q = np.clip((tile * 15).astype(np.int32), 0, 15)
            digest = int(hashlib.blake2s(q.tobytes(), digest_size=4).hexdigest(), 16)
            out.append((x, y, digest))
    return out


def _heatmap(arr: np.ndarray) -> dict[str, Any]:
    png = png_bytes(np.stack([arr, arr, arr], axis=-1))
    import base64

    return {
        "media_type": "image/png",
        "b64": base64.b64encode(png).decode("ascii"),
        "sha256": hashlib.sha256(png).hexdigest(),
        "heatmap_is_transcript": False,
        "heatmap_is_court_finding": False,
        "invented": False,
    }


def _indicator(kind: str, note: str, *, confidence: float, bbox=None, extra=None) -> dict[str, Any]:
    rec = {
        "kind": kind,
        "note": note,
        "phrasing": "indicator / heuristic / candidate — human verification required",
        "confidence": round(float(np.clip(confidence, 0.0, 1.0)), 3),
        "confidence_means": "pixel signal quality, not a finding that this is forged",
        "invented": False,
    }
    if bbox is not None:
        rec["bbox"] = [int(v) for v in bbox]
    if extra:
        rec.update(extra)
    return rec


def analyze_handwriting_rgb(
    rgb: np.ndarray,
    *,
    filename: str = "scan.png",
    hosted: bool = False,
    helpers: bool = True,
) -> dict[str, Any]:
    rgb = finite01(rgb)
    src_h, src_w = int(rgb.shape[0]), int(rgb.shape[1])
    max_side = HOSTED_MAX_SIDE if hosted else LOCAL_ANALYZE_SIDE
    work, scale = _cap(rgb, max_side)
    limited = scale < 1.0
    ink, lum, frac = _ink_mask(work)
    env: dict[str, Any] = {
        "product": "spectrallock",
        "author": "Aziel Eliab",
        "family": "handwriting",
        "op": "analyze",
        "artifact": {
            "filename": filename,
            "width": src_w,
            "height": src_h,
            "analyze_width": int(work.shape[1]),
            "analyze_height": int(work.shape[0]),
            "scale": scale,
            "sha256": _sha(rgb),
            "invented": False,
        },
        "strokes": [],
        "features": {
            "weight": [],
            "speed_cues": [],
            "density": [],
            "bleed": [],
            "shifts": [],
            "erasures": [],
            "tracing": [],
        },
        "forgery_indicators": [],
        "side_by_side": [],
        "graph": {"nodes": [], "edges": [], "invented": False},
        "overlays": [],
        "provenance": [],
        "refused": [],
        "warnings": [
            "synthetic_image_analysis_not_lab",
            "not_forensic_certification",
            "heatmap_is_not_transcript",
            "heatmap_is_not_court_finding",
            "human_verification_required",
        ],
        "helper_modes": [],
        "no_lie": True,
        "guessed_letters": False,
        "esda": False,
        "chemical_ink_dating": False,
        "writer_identification_as_fact": False,
        "forensic_certification": False,
        "lamb_lens": "Service → Clarity → Peace",
        "identity": "Aziel Eliab",
        "note": HANDWRITING_NOTE,
        "inject_note": INJECT_NOTE,
        "limitation": LIMITATION,
        "invented": False,
    }
    if limited and hosted:
        env["warnings"].append(REFUSE_LIMIT)
        env["hosted_cap"] = HOSTED_MAX_SIDE

    if frac < 0.004:
        env["refuse_code"] = REFUSE_NO_INK
        env["refused"].append({
            "code": REFUSE_NO_INK,
            "note": "No writable ink-like strokes found in the supplied pixels.",
            "invented": False,
        })
        env["stop"] = True
        return env

    dt = _chamfer(ink)
    widths = dt[ink] * 2.0
    weight_mean = float(widths.mean()) if widths.size else 0.0
    weight_std = float(widths.std()) if widths.size else 0.0
    env["features"]["weight"].append({
        "mean_px": round(weight_mean, 3),
        "std_px": round(weight_std, 3),
        "cv": round(weight_std / max(weight_mean, 1e-3), 3),
        "note": "pressure proxy from stroke width. Not a force measurement.",
        "invented": False,
    })

    density = 1.0 - lum
    ink_density = float(density[ink].mean()) if ink.any() else 0.0
    env["features"]["density"].append({
        "mean": round(ink_density, 4),
        "note": "darkness of ink-mask pixels. Not pigment mass.",
        "invented": False,
    })

    gx, gy = _sobel(lum)
    mag = np.hypot(gx, gy)
    # bleed: gradient width just outside the mask
    dil = ink.copy()
    pad = np.pad(ink, 1)
    dil = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:] | ink)
    ring = dil & ~ink
    bleed = float(mag[ring].mean()) if ring.any() else 0.0
    env["features"]["bleed"].append({
        "edge_grad_mean": round(bleed, 4),
        "note": "capillary-spread / feathering proxy from edge gradient. Not a paper assay.",
        "invented": False,
    })

    # tremor: high-frequency residual along ink
    wobble = np.abs(lum - blur_gray(lum, 1.2))
    tremor = float(wobble[ink].mean()) if ink.any() else 0.0
    taper = float(widths.max() - widths.min()) if widths.size else 0.0
    env["features"]["speed_cues"].append({
        "tremor": round(tremor, 4),
        "taper_px": round(taper, 3),
        "ballistic_vs_controlled": "controlled-candidate" if tremor > 0.035 and weight_std < 0.6 else "fluent-or-unclear",
        "note": "shape cues only. Speed in mm/s is SLOT.",
        "invented": False,
    })

    # baseline / slant / size
    ys, xs = np.where(ink)
    shifts = []
    if ys.size:
        rows = {}
        for y, x in zip(ys.tolist(), xs.tolist()):
            rows.setdefault(y // 4, []).append((x, y))
        cents = [(k, float(np.mean([p[1] for p in v]))) for k, v in sorted(rows.items()) if len(v) > 6]
        if len(cents) >= 3:
            drift = float(np.std([c[1] for c in cents]))
            env["features"]["shifts"].append({
                "baseline_drift_px": round(drift, 3),
                "note": "row-centroid drift. Not proof of a second writer.",
                "invented": False,
            })
            shifts.append(drift)
        angles = np.degrees(np.arctan2(gy[ink], gx[ink] + 1e-6))
        env["features"]["shifts"].append({
            "slant_deg_std": round(float(np.std(angles)), 3),
            "note": "gradient-angle spread. Heuristic only.",
            "invented": False,
        })

    # erasures: bright patches near ink
    paper = float(np.percentile(lum, 90))
    bright = (lum > min(0.97, paper + 0.04)) & ~ink
    ghost = ((lum > 0.55) & (lum < 0.78) & (mag > 0.08)) & ~ink
    if bright.any():
        by, bx = np.where(bright)
        env["features"]["erasures"].append({
            "kind": "abrasion-brightening",
            "frac": round(float(bright.mean()), 4),
            "bbox": [int(bx.min()), int(by.min()), int(bx.max()), int(by.max())],
            "note": "candidate white-out / abrasion. Human verification required.",
            "invented": False,
        })
    if ghost.any() and float(ghost.mean()) > 0.002:
        gy_, gx_ = np.where(ghost)
        env["features"]["erasures"].append({
            "kind": "residual-ghost",
            "frac": round(float(ghost.mean()), 4),
            "bbox": [int(gx_.min()), int(gy_.min()), int(gx_.max()), int(gy_.max())],
            "note": "mid-gray residual near strokes. Not recovered letters.",
            "invented": False,
        })

    comps = _label(ink)
    env["strokes"] = [
        {
            "id": c["id"],
            "bbox": c["bbox"],
            "area": c["area"],
            "center": [round(c["cx"], 1), round(c["cy"], 1)],
            "aspect": round(c["aspect"], 3),
            "invented": False,
        }
        for c in comps
    ]
    nodes = [{
        "id": c["id"],
        "kind": "stroke-segment",
        "bbox": c["bbox"],
        "area": c["area"],
        "invented": False,
    } for c in comps]
    edges = []
    for i in range(len(comps) - 1):
        a, b = comps[i], comps[i + 1]
        dist = ((a["cx"] - b["cx"]) ** 2 + (a["cy"] - b["cy"]) ** 2) ** 0.5
        anomalous = dist > max(work.shape) * 0.35 or abs(a["aspect"] - b["aspect"]) > 2.2
        edges.append({
            "from": a["id"],
            "to": b["id"],
            "kind": "sequence",
            "distance_px": round(dist, 2),
            "anomalous": bool(anomalous),
            "note": "anomalous edge is a heuristic flag, not a forgery finding" if anomalous else "sequence",
            "invented": False,
        })
    env["graph"] = {"nodes": nodes, "edges": edges, "invented": False}

    # tracing: width uniformity + many tiny lifts
    if weight_mean > 0 and weight_std / max(weight_mean, 1e-3) < 0.18 and len(comps) >= 4:
        env["features"]["tracing"].append({
            "kind": "unnatural-width-uniformity",
            "cv": round(weight_std / max(weight_mean, 1e-3), 3),
            "note": "candidate careful tracing / guide. Heuristic only.",
            "invented": False,
        })
    # doubled ridge: high Laplacian energy at mask interior
    lap = np.abs(lum - blur_gray(lum, 0.8))
    if float(lap[ink].mean()) > 0.06 and weight_mean >= 2.2:
        env["features"]["tracing"].append({
            "kind": "doubled-edge-candidate",
            "note": "interior high-frequency along thick strokes. Heuristic.",
            "invented": False,
        })

    indicators = []
    if tremor > 0.04 and weight_std < 0.85:
        indicators.append(_indicator(
            "tremor-slow-copy",
            "High-frequency wobble with relatively uniform width — careful-copy candidate.",
            confidence=min(0.85, 0.35 + tremor * 8),
        ))
    if len(comps) >= 8:
        indicators.append(_indicator(
            "pen-lifts",
            f"{len(comps)} disconnected ink components — lifts or fragmentation. Unnatural only in context.",
            confidence=min(0.7, 0.25 + len(comps) * 0.03),
        ))
    # overwrite: very dark cores
    if ink.any() and float((lum < 0.12).mean()) > 0.01 and ink_density > 0.55:
        indicators.append(_indicator(
            "retouch-overwrite",
            "Very dark cores inside the ink mask — retouch / patching candidate.",
            confidence=0.55,
        ))
    # dual ink: hue spread on ink pixels
    try:
        from spectrallock.engine import rgb_to_hsv

        h, s, _v = rgb_to_hsv(work)
        if ink.any() and float(s[ink].mean()) > 0.08:
            hue_std = float(np.std(h[ink]))
            if hue_std > 28:
                indicators.append(_indicator(
                    "dual-ink-patch",
                    "Stroke-pixel hue clusters differ — dual-ink / later addition candidate.",
                    confidence=min(0.75, 0.3 + hue_std / 80.0),
                    extra={"hue_std": round(hue_std, 2)},
                ))
    except Exception:
        pass
    if shifts and shifts[0] > 3.5:
        indicators.append(_indicator(
            "baseline-misalign",
            "Baseline centroids drift across the line — not continuous-writing proof, a pixel flag.",
            confidence=min(0.7, 0.3 + shifts[0] / 20.0),
        ))

    # clone stamps
    hashes = _block_hashes(lum, 8)
    seen: dict[int, list[tuple[int, int]]] = {}
    clones = []
    for x, y, digest in hashes:
        seen.setdefault(digest, []).append((x, y))
    for digest, pts in seen.items():
        if len(pts) < 2:
            continue
        for i, (x0, y0) in enumerate(pts):
            for x1, y1 in pts[i + 1 :]:
                if abs(x0 - x1) + abs(y0 - y1) >= 16:
                    clones.append((x0, y0, x1, y1))
                    break
            if len(clones) >= 6:
                break
        if len(clones) >= 6:
            break
    if clones:
        indicators.append(_indicator(
            "clone-stamp",
            "Repeated 8×8 luminance hashes far apart — digital copy-paste / clone-stamp candidate on the scan.",
            confidence=min(0.9, 0.5 + 0.06 * len(clones)),
            bbox=[clones[0][0], clones[0][1], clones[0][2] + 8, clones[0][3] + 8],
            extra={"pair_count": len(clones)},
        ))

    # compression discontinuities
    block_std = []
    hh, ww = lum.shape
    for y in range(0, hh - 8, 8):
        for x in range(0, ww - 8, 8):
            block_std.append(float(lum[y : y + 8, x : x + 8].std()))
    if block_std and float(np.std(block_std)) > 0.045:
        indicators.append(_indicator(
            "compression-paste",
            "8×8 block-energy spread — compression / composite paste-up candidate.",
            confidence=min(0.65, 0.25 + float(np.std(block_std)) * 4),
        ))

    # ductus
    if ink.any():
        ang = np.arctan2(gy[ink], gx[ink] + 1e-6)
        circ = float(np.abs(np.exp(1j * ang).mean()))
        env["features"]["speed_cues"].append({
            "ductus_consistency": round(circ, 3),
            "note": "mean resultant of stroke gradients. Inconsistency is a flag, not identity.",
            "invented": False,
        })
        if circ < 0.18 and frac > 0.02:
            indicators.append(_indicator(
                "ductus-inconsistent",
                "Stroke-direction resultant is low — mixed ductus / later patching candidate.",
                confidence=0.45,
            ))

    aspects = [c["aspect"] for c in comps]
    if len(aspects) >= 6 and (max(aspects) - min(aspects)) > 3.5:
        indicators.append(_indicator(
            "style-shift",
            "Component aspect ratios jump (print↔cursive heuristic). Not a single-writer fact.",
            confidence=0.4,
        ))

    if helpers:
        try:
            ind = indent_overlay(work, inject=False)
            lemon = lemon_overlay(work, inject=False)
            uv = uv_overlay(work, inject=False)
            candle = candle_overlay(work, inject=False)
            residual = apply_mode(work, "indent", inject=False)
            ind_lum = luminance(ind)
            relief = float(np.abs(ind_lum - lum)[ink].mean()) if ink.any() else 0.0
            env["helper_modes"].append({
                "mode": "indent",
                "inject": False,
                "contributed": relief > 0.02,
                "note": "ISA-1.0 inject OFF. Surface-relief heuristic, not ESDA.",
                "invented": False,
            })
            if relief > 0.035:
                indicators.append(_indicator(
                    "indent-mismatch",
                    "Indent helper (inject OFF) differs from surface ink — indentation vs wet-ink mismatch candidate. Not ESDA.",
                    confidence=min(0.6, 0.25 + relief * 4),
                    extra={"helper_mode": "indent"},
                ))
            lemon_w = float(np.abs(luminance(lemon) - lum).mean())
            env["helper_modes"].append({
                "mode": "lemon",
                "inject": False,
                "contributed": lemon_w > 0.01,
                "note": "LISA-1.0 inject OFF. Does not invent marks.",
                "invented": False,
            })
            env["helper_modes"].append({
                "mode": "uv",
                "inject": False,
                "contributed": float(np.abs(luminance(uv) - lum).mean()) > 0.01,
                "note": "Synthetic UV look. Not a lamp.",
                "invented": False,
            })
            env["helper_modes"].append({
                "mode": "candle",
                "inject": False,
                "contributed": float(np.abs(luminance(candle) - lum).mean()) > 0.01,
                "note": "Synthetic candle look. Not a flame test.",
                "invented": False,
            })
            env["helper_modes"].append({
                "mode": "residual-lift",
                "inject": False,
                "contributed": True,
                "note": "Residual / contrast with inject OFF. Heatmap ≠ transcript.",
                "paper": getattr(residual, "paper", None),
                "invented": False,
            })
        except Exception:
            env["warnings"].append("helper-modes-skipped")

    env["forgery_indicators"] = indicators
    # overlays (small)
    dens_map = normalize01(np.where(ink, density, 0.0))
    bleed_map = normalize01(np.where(ring, mag, 0.0))
    erase_map = normalize01(bright.astype(np.float32) + 0.5 * ghost.astype(np.float32))
    env["overlays"] = [
        {"kind": "density", "note": "heatmap ≠ transcript", **_heatmap(dens_map)},
        {"kind": "bleed", "note": "heatmap ≠ transcript", **_heatmap(bleed_map)},
        {"kind": "erasure-candidates", "note": "heatmap ≠ transcript", **_heatmap(erase_map)},
    ]
    env["provenance"].append({
        "file_path": filename,
        "recovery_method": "ink-mask-luminance",
        "ink_frac": round(frac, 5),
        "state": "present_current",
        "human_verification_required": True,
        "invented": False,
    })
    return env


def _compare_pair(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    def take(env: dict[str, Any], key: str) -> float:
        feats = env.get("features") or {}
        rows = feats.get(key) or []
        if not rows:
            return 0.0
        row = rows[0]
        for k in ("mean_px", "mean", "edge_grad_mean", "baseline_drift_px", "tremor"):
            if k in row:
                return float(row[k])
        return 0.0

    return {
        "weight_delta": round(take(a, "weight") - take(b, "weight"), 4),
        "density_delta": round(take(a, "density") - take(b, "density"), 4),
        "bleed_delta": round(take(a, "bleed") - take(b, "bleed"), 4),
        "indicator_kinds_a": [i["kind"] for i in a.get("forgery_indicators") or []],
        "indicator_kinds_b": [i["kind"] for i in b.get("forgery_indicators") or []],
        "note": "Pixel-feature delta only. Not a same-writer or forgery verdict.",
        "invented": False,
    }


def analyze_handwriting(
    raw: bytes,
    *,
    op: str = "analyze",
    filename: str = "scan.png",
    twin: bytes | None = None,
    twin_name: str = "known.png",
    hosted: bool = False,
) -> dict[str, Any]:
    try:
        op_key = parse_handwriting_op(op)
    except ValueError as exc:
        return {
            "family": "handwriting",
            "error": str(exc),
            "known": list(HANDWRITING_OPS),
            "no_lie": True,
            "note": HANDWRITING_NOTE,
        }
    try:
        rgb = load_rgb_bytes(raw)
    except ValueError:
        return {
            "family": "handwriting",
            "op": op_key,
            "refuse_code": REFUSE_UNSUPPORTED,
            "refused": [{"code": REFUSE_UNSUPPORTED, "note": "Not a readable scan/photo.", "invented": False}],
            "warnings": ["synthetic_image_analysis_not_lab", "not_forensic_certification"],
            "no_lie": True,
            "note": HANDWRITING_NOTE,
            "invented": False,
        }

    env = analyze_handwriting_rgb(rgb, filename=filename, hosted=hosted)
    env["op"] = op_key

    twin_env = None
    if twin:
        try:
            twin_rgb = load_rgb_bytes(twin)
            twin_env = analyze_handwriting_rgb(twin_rgb, filename=twin_name, hosted=hosted)
        except ValueError:
            env["warnings"].append("twin-unreadable")

    if twin_env:
        env["side_by_side"] = [
            {"role": "questioned", "filename": filename, "artifact": env["artifact"], "invented": False},
            {"role": "known", "filename": twin_name, "artifact": twin_env["artifact"], "invented": False},
        ]
        env["compare"] = _compare_pair(env, twin_env)
        env["twin"] = {
            "filename": twin_name,
            "forgery_indicators": twin_env.get("forgery_indicators"),
            "features": twin_env.get("features"),
            "refuse_code": twin_env.get("refuse_code"),
            "invented": False,
        }
        # revision-like raster graph when two scans of “same” page differ
        try:
            qa = finite01(load_rgb_bytes(raw))
            qb = finite01(load_rgb_bytes(twin))
            if qa.shape == qb.shape:
                d = np.abs(luminance(qa) - luminance(qb))
                env["revision_compare"] = {
                    "mean_abs_delta": round(float(d.mean()), 5),
                    "changed_frac": round(float((d > 0.08).mean()), 5),
                    "note": "Same-raster delta. Ink added later / white-out / paste candidate if changed_frac is high. Not a verdict.",
                    "invented": False,
                }
        except Exception:
            pass

    if op_key == "refuse":
        if env.get("refuse_code"):
            env["stop"] = True
        else:
            env["note"] = "Refuse requested but ink-like strokes are present. Reported as candidates, not invented."
        return env
    if op_key == "forgery-indicators":
        env["recovered_view"] = env["forgery_indicators"]
    if op_key == "graph":
        env["recovered_view"] = env["graph"]
    if op_key in {"compare", "side-by-side"} and not twin:
        env["warnings"].append("compare/side-by-side needs a second scan (--twin).")
    return env


def analyze_handwriting_path(
    path: str,
    *,
    op: str = "analyze",
    twin: str | None = None,
    hosted: bool = False,
) -> dict[str, Any]:
    from pathlib import Path

    raw = Path(path).read_bytes()
    twin_bytes = Path(twin).read_bytes() if twin else None
    return analyze_handwriting(
        raw,
        op=op,
        filename=Path(path).name,
        twin=twin_bytes,
        twin_name=Path(twin).name if twin else "known.png",
        hosted=hosted,
    )
