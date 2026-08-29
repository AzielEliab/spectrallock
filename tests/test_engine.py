"""Engine: synthetic page, tazel/vyrn lifts, composite pixel math, UV honesty."""

from __future__ import annotations

import numpy as np

from spectrallock.engine import (
    CHAOS_WEIGHTS,
    EPS,
    LIMITATION,
    LIVE_MODES,
    MODES,
    ROSETTA_WEIGHTS,
    ZEN_WEIGHTS,
    apply_mode,
    balance_blend,
    blend_channels,
    chaos_overlay,
    luminance,
    normalize01,
    rosetta_overlay,
    synthetic_page,
    tazel_overlay,
    uv_overlay,
    vyrn_overlay,
    zen_overlay,
    zero_overlay,
)


def test_all_eight_modes_live() -> None:
    assert tuple(MODES) == ("zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance")
    assert LIVE_MODES == tuple(MODES)
    for row in MODES.values():
        assert row["status"] == "live"
        assert row["paper"]


def test_limitation_is_honest() -> None:
    low = LIMITATION.lower()
    for word in ("spectrometer", "forensic", "uv photography", "scribal truth", "ocr"):
        assert word in low
    assert "not" in low


def test_synthetic_page_regions() -> None:
    img = synthetic_page(96, 96)
    assert img.shape == (96, 96, 3)
    cream = img[5, 5]
    assert cream[0] > 0.85 and cream[1] > 0.8
    dark = img[45, 40]
    assert dark.mean() < 0.2
    cyan = img[64, 40]
    assert cyan[1] > cyan[0]  # green-ish faint
    mag = img[26, 40]
    assert mag[0] > mag[1] and mag[2] > mag[1]


def test_tazel_lifts_faint_cyan_vs_zero() -> None:
    img = synthetic_page(96, 96)
    z = luminance(zero_overlay(img))
    t = luminance(tazel_overlay(img))
    faint = (slice(62, 67), slice(10, 84))
    bg = (slice(2, 10), slice(2, 10))
    z_contrast = float(z[faint].mean() - z[bg].mean())
    t_contrast = float(t[faint].mean() - t[bg].mean())
    # Tazel should separate the faint turquoise stroke from parchment more than Zero.
    assert abs(t_contrast) > abs(z_contrast) * 1.05 or t[faint].mean() > z[faint].mean()
    # Green channel on the faint region is lifted relative to zero gray.
    t_rgb = tazel_overlay(img)
    assert float(t_rgb[faint][..., 1].mean()) > float(zero_overlay(img)[faint].mean()) * 0.9


def test_vyrn_emphasizes_magenta_stroke() -> None:
    img = synthetic_page(96, 96)
    v = vyrn_overlay(img)
    z = zero_overlay(img)
    mag = (slice(24, 30), slice(20, 78))
    bg = (slice(2, 10), slice(2, 10))
    v_r = float(v[mag][..., 0].mean())
    z_r = float(z[mag][..., 0].mean())
    v_bg = float(v[bg].mean())
    assert v_r > z_r
    assert (v_r - v_bg) > 0.02


def test_rosetta_weighted_mix_pixel_math() -> None:
    img = synthetic_page(64, 64)
    out, ch = rosetta_overlay(img, tint=False)
    expected = blend_channels(ch, ROSETTA_WEIGHTS)
    got = luminance(out)
    assert np.allclose(got, expected, atol=1e-5)
    assert abs(sum(ROSETTA_WEIGHTS.values()) - 1.0) < 1e-9
    assert ROSETTA_WEIGHTS == {"zero": 0.40, "tazel": 0.35, "vyrn": 0.25}


def test_zen_equal_four_channel_mix() -> None:
    img = synthetic_page(64, 64)
    out, ch = zen_overlay(img, tint=False)
    expected = blend_channels(ch, ZEN_WEIGHTS)
    assert np.allclose(luminance(out), expected, atol=1e-5)
    assert all(abs(w - 0.25) < 1e-9 for w in ZEN_WEIGHTS.values())
    assert set(ZEN_WEIGHTS) == {"zero", "tazel", "uv", "vyrn"}


def test_chaos_weighted_mix_pixel_math() -> None:
    img = synthetic_page(64, 64)
    out, ch = chaos_overlay(img, tint=False)
    expected = blend_channels(ch, CHAOS_WEIGHTS)
    assert np.allclose(luminance(out), expected, atol=1e-5)
    assert CHAOS_WEIGHTS == {"uv": 0.40, "vyrn": 0.35, "tazel": 0.20, "zero": 0.05}
    assert abs(sum(CHAOS_WEIGHTS.values()) - 1.0) < 1e-9


def test_balance_formula_pixel_math() -> None:
    img = synthetic_page(64, 64)
    zen_rgb, _ = zen_overlay(img, tint=False)
    chaos_rgb, _ = chaos_overlay(img, tint=False)
    out, b, alpha = balance_blend(zen_rgb, chaos_rgb)
    zn = normalize01(luminance(zen_rgb))
    cn = normalize01(luminance(chaos_rgb))
    b_exp = (zn - cn) / (zn + cn + EPS)
    a_exp = (1.0 + b_exp) / 2.0
    rgb_exp = a_exp[..., None] * zen_rgb + (1.0 - a_exp[..., None]) * chaos_rgb
    assert np.allclose(b, b_exp, atol=1e-5)
    assert np.allclose(alpha, a_exp, atol=1e-5)
    assert np.allclose(out, rgb_exp, atol=1e-5)
    # never invent marks: output is a convex combination of existing pixels
    assert np.all(out >= np.minimum(zen_rgb, chaos_rgb) - 1e-5)
    assert np.all(out <= np.maximum(zen_rgb, chaos_rgb) + 1e-5)


def test_uv_boosts_parchment_darkens_ink() -> None:
    img = synthetic_page(96, 96)
    u = uv_overlay(img)
    parchment = luminance(u[2:10, 2:10])
    ink = luminance(u[42:50, 20:70])
    assert float(parchment.mean()) > float(ink.mean())
    # blue-violet weight: parchment B channel leading
    assert float(u[5, 5, 2]) >= float(u[5, 5, 1]) - 0.02
    low = LIMITATION.lower()
    assert "365" in LIMITATION or "synthetic" in low


def test_apply_mode_roundtrip_all_live() -> None:
    img = synthetic_page(48, 48)
    for mode in LIVE_MODES:
        result = apply_mode(img, mode)
        assert result.mode == mode
        assert result.rgb.shape == (48, 48, 3)
        assert result.rgb.dtype == np.float32
        assert 0.0 <= float(result.rgb.min()) and float(result.rgb.max()) <= 1.0 + 1e-5
        assert result.width == 48 and result.height == 48
        assert "x" in result.to_meta()["com"]


def test_center_of_mass_on_bright_corner() -> None:
    img = np.zeros((20, 30, 3), dtype=np.float32)
    img[0:4, 0:4] = 1.0
    result = apply_mode(img, "zero")
    assert result.com[0] < 8
    assert result.com[1] < 8
