"""Wheel paint plane stays separate from the spectral triad."""

from __future__ import annotations

import numpy as np

from spectrallock.engine import (
    INJECT_RGB,
    SPECTRAL_TRIAD_HEX,
    TAZEL_HEX,
    TAZEL_HUE,
    TAZEL_RGB,
    VYRN_HEX,
    VYRN_HUE,
    VYRN_RGB,
    WHEEL_PAINT_HEX,
    WHEEL_PAINT_RGB,
    ZERO_HEX,
    ZERO_RGB,
    gate_inband,
    paint_rgb,
    rosetta_overlay,
    synthetic_page,
    tazel_overlay,
    vyrn_overlay,
)


def test_spectral_triad_hexes_unchanged() -> None:
    assert TAZEL_HEX == "#1EC9A5"
    assert VYRN_HEX == "#C00066"
    assert ZERO_HEX == "#6F6485"
    assert SPECTRAL_TRIAD_HEX == {"tazel": "#1EC9A5", "vyrn": "#C00066", "zero": "#6F6485"}
    assert TAZEL_HUE == 170.0
    assert VYRN_HUE == 350.0
    teal = np.empty((8, 8, 3), dtype=np.float32)
    teal[:] = TAZEL_RGB
    assert gate_inband(teal)["tazel_inband_pct"] == 100.0
    magenta = np.empty((8, 8, 3), dtype=np.float32)
    magenta[:] = VYRN_RGB
    assert gate_inband(magenta)["vyrn_inband_pct"] == 100.0


def test_wheel_paint_hexes_are_authoritative_and_separate() -> None:
    assert WHEEL_PAINT_HEX == {
        "zero": "#325767",
        "chaos": "#8D223D",
        "vyrn": "#A22639",
        "uv": "#9F3B2B",
        "tazel": "#797A2D",
        "rosetta": "#467542",
        "zen": "#DFD2B5",
    }
    for name in WHEEL_PAINT_HEX:
        assert paint_rgb(name) == WHEEL_PAINT_RGB[name]
        assert INJECT_RGB[name] == WHEEL_PAINT_RGB[name]
    assert WHEEL_PAINT_RGB["tazel"] != TAZEL_RGB
    assert WHEEL_PAINT_RGB["vyrn"] != VYRN_RGB
    assert WHEEL_PAINT_RGB["zero"] != ZERO_RGB


def test_membership_tint_uses_wheel_not_triad_mix() -> None:
    img = synthetic_page(48, 48)
    rosetta, _ = rosetta_overlay(img, inject=True)
    # Wheel Rosetta #467542 is leaf green: G leads R and B.
    assert float(rosetta[..., 1].mean()) > float(rosetta[..., 0].mean())
    assert float(rosetta[..., 1].mean()) > float(rosetta[..., 2].mean())
    flat = np.empty((12, 12, 3), dtype=np.float32)
    flat[:] = TAZEL_RGB
    painted = tazel_overlay(flat, inject=True)
    # Wheel olive #797A2D pulls blue down from triad teal #1EC9A5.
    assert float(painted[..., 2].mean()) < float(TAZEL_RGB[2])
    mag = np.empty((12, 12, 3), dtype=np.float32)
    mag[:] = VYRN_RGB
    vyrn = vyrn_overlay(mag, inject=True)
    assert float(vyrn[..., 0].mean()) > float(vyrn[..., 1].mean())
