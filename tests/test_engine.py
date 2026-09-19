"""Engine: synthetic page, tazel/vyrn lifts, composite pixel math, UV honesty."""

from __future__ import annotations

import numpy as np

import pytest

from spectrallock.engine import (
    CHAOS_WEIGHTS,
    EPS,
    LENSES,
    LIMITATION,
    LIVE_MODES,
    MODE_ALIASES,
    MODES,
    ROSETTA_WEIGHTS,
    STUB_MODES,
    TARGETS,
    ZEN_WEIGHTS,
    analyze,
    apply_mode,
    apply_target,
    balance_blend,
    blend_channels,
    candle_overlay,
    chaos_overlay,
    indent_overlay,
    lemon_overlay,
    luminance,
    normalize01,
    normalize_lenses,
    normalize_target,
    resolve_mode,
    rosetta_overlay,
    synthetic_page,
    tazel_overlay,
    uv_overlay,
    vyrn_overlay,
    zen_overlay,
    zero_overlay,
)


def test_all_live_modes() -> None:
    assert tuple(MODES) == (
        "zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance",
        "candle", "indent", "lemon",
    )
    assert LIVE_MODES == tuple(MODES)
    for row in MODES.values():
        assert row["status"] == "live"
        assert row["paper"]
    assert MODES["uv"]["aliases"] == ["ultraviolet", "uv-light", "uvsa"]
    assert "Ultraviolet light analysis (synthetic)" in MODES["uv"]["summary"]
    assert MODES["candle"]["paper"] == "CLSA-1.0"
    assert MODES["indent"]["paper"] == "ISA-1.0"
    assert MODES["indent"]["preferred_target"] == "page"
    assert MODES["lemon"]["paper"] == "LISA-1.0"


def test_limitation_is_rosetta() -> None:
    low = LIMITATION.lower()
    for word in ("rosetta spectral analysis", "ocr", "ink", "page", "aziel eliab"):
        assert word in low
    assert "spectrometer" not in low
    assert LENSES == LIVE_MODES
    assert tuple(TARGETS) == ("ink", "page")


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



def test_normalize_lenses_and_targets() -> None:
    assert normalize_lenses() == ["rosetta"]
    assert normalize_lenses(lens="tazel") == ["tazel"]
    assert normalize_lenses(lenses=["zero", "tazel", "zero"]) == ["zero", "tazel"]
    assert normalize_lenses(mode="rosetta+vyrn") == ["rosetta", "vyrn"]
    assert normalize_lenses(mode="ultraviolet") == ["uv"]
    assert normalize_lenses(lenses=["candlelight", "ink-suppress", "hidden-lemon"]) == [
        "candle", "indent", "lemon",
    ]
    assert normalize_target("PAGE") == "page"
    assert normalize_target("parchment") == "page"
    assert normalize_target(None) == "ink"


def test_analyze_ink_vs_page_on_synthetic() -> None:
    img = synthetic_page(64, 64)
    ink = analyze(img, "rosetta", target="ink")
    page = analyze(img, "rosetta", target="page")
    assert ink.target == "ink" and page.target == "page"
    assert ink.lenses == ("rosetta",)
    assert page.lenses == ("rosetta",)
    stroke = (slice(42, 50), slice(8, 56))
    parchment = (slice(2, 10), slice(2, 10))
    # ink target keeps strokes darker than page target on the same stroke
    assert float(luminance(ink.rgb)[stroke].mean()) < float(luminance(page.rgb)[stroke].mean())
    # page target lifts the stroke toward parchment vs ink target
    assert float(luminance(page.rgb)[stroke].mean()) > float(luminance(ink.rgb)[stroke].mean())
    assert float(luminance(page.rgb)[parchment].mean()) > 0.2
    assert ink.to_meta()["rosetta_spectral_analysis"] is True
    assert ink.to_meta()["corpus_ocr_aligned"] is True


def test_analyze_multi_lens_compose() -> None:
    img = synthetic_page(32, 32)
    result = analyze(img, lenses=["zero", "tazel"], target="ink")
    assert result.mode == "zero+tazel"
    assert result.paper == "MULTI"
    assert list(result.lenses) == ["zero", "tazel"]
    assert result.rgb.shape == (32, 32, 3)
    assert np.isfinite(result.rgb).all()


def test_apply_target_never_invents_outside_source_range() -> None:
    img = synthetic_page(32, 32)
    base = apply_mode(img, "zero").rgb
    for dest in ("ink", "page"):
        out = apply_target(base, dest)
        assert np.isfinite(out).all()
        assert 0.0 <= float(out.min()) and float(out.max()) <= 1.0 + 1e-5


def test_apply_mode_no_nan_on_bad_pixels() -> None:
    img = synthetic_page(24, 24)
    img[0, 0, 0] = np.nan
    img[1, 1, 1] = np.inf
    for mode in LIVE_MODES:
        result = apply_mode(img, mode)
        assert np.isfinite(result.rgb).all()
        assert 0.0 <= float(result.rgb.min())
        assert float(result.rgb.max()) <= 1.0 + 1e-5


def test_mode_aliases_resolve_to_canonical() -> None:
    expected = {
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
    assert MODE_ALIASES == expected
    img = synthetic_page(24, 24)
    for alias, canonical in expected.items():
        assert resolve_mode(alias) == canonical
        result = apply_mode(img, alias)
        assert result.mode == canonical
        assert result.paper == MODES[canonical]["paper"]


def test_stub_modes_refuse() -> None:
    img = synthetic_page(16, 16)
    for stub in ("spectrometer", "forensic", "invent_mark"):
        assert stub in STUB_MODES
        with pytest.raises(ValueError, match="stub"):
            apply_mode(img, stub)
        with pytest.raises(ValueError, match="stub"):
            normalize_lenses(mode=stub)


def test_candle_warm_parchment_readable_ink() -> None:
    img = synthetic_page(96, 96)
    c = candle_overlay(img)
    parchment = c[2:10, 2:10]
    ink = c[42:50, 20:70]
    assert float(parchment[..., 0].mean()) > float(parchment[..., 2].mean())
    assert float(luminance(parchment).mean()) > float(luminance(ink).mean())
    assert float(parchment[..., 2].mean()) < float(img[2:10, 2:10, 2].mean()) + 0.02
    rec = apply_mode(img, "candle")
    assert rec.paper == "CLSA-1.0"


def test_indent_suppresses_ink_lifts_relief() -> None:
    img = synthetic_page(96, 96)
    ind = indent_overlay(img)
    z = zero_overlay(img)
    stroke = (slice(42, 50), slice(8, 88))
    # visible ink is washed toward parchment vs zero grayscale
    assert float(luminance(ind)[stroke].mean()) > float(luminance(z)[stroke].mean())
    groove = (slice(84, 86), slice(8, 88))
    parch = (slice(2, 10), slice(2, 10))
    # pressure groove remains a luma dip vs nearby parchment
    assert float(luminance(ind)[groove].mean()) < float(luminance(ind)[parch].mean())
    rec = apply_mode(img, "indent")
    assert rec.paper == "ISA-1.0"
    page = analyze(img, "indent", target="page")
    assert page.target == "page"
    assert page.lenses == ("indent",)


def test_lemon_boosts_existing_brown_never_invents() -> None:
    img = synthetic_page(96, 96)
    lem = lemon_overlay(img)
    brown = (slice(74, 79), slice(14, 82))
    parch = (slice(2, 10), slice(2, 10))
    assert float(lem[brown][..., 0].mean()) > float(lem[brown][..., 2].mean())
    # brown cue stays darker / warmer than parchment; no invented bright marks
    assert float(luminance(lem)[brown].mean()) < float(luminance(lem)[parch].mean()) + 0.15
    assert np.isfinite(lem).all()
    assert 0.0 <= float(lem.min()) and float(lem.max()) <= 1.0 + 1e-5
    rec = apply_mode(img, "lemon")
    assert rec.paper == "LISA-1.0"
    assert "never invents" in MODES["lemon"]["summary"].lower() or "never invent" in LIMITATION.lower()
