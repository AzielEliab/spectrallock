"""Color inject switch: ON paint / OFF gray / zero ignore / in-band percents."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from spectrallock.engine import (
    INJECT_NOTE,
    LIVE_MODES,
    analyze,
    apply_mode,
    gate_inband,
    is_achromatic,
    parse_inject,
    resolve_inject,
    synthetic_page,
    tazel_overlay,
    vyrn_overlay,
    zero_overlay,
)
from spectrallock.inject import main as inject_main


def test_parse_and_resolve_inject() -> None:
    assert resolve_inject() is True
    assert resolve_inject(inject=False) is False
    assert resolve_inject(tint=False) is False
    assert resolve_inject(inject=True, tint=False) is True
    assert parse_inject("no-inject") is False
    assert parse_inject("ON") is True
    assert parse_inject(0) is False


def test_zero_ignores_inject_switch() -> None:
    img = synthetic_page(48, 48)
    on = apply_mode(img, "zero", inject=True)
    off = apply_mode(img, "zero", inject=False)
    assert is_achromatic(on.rgb)
    assert is_achromatic(off.rgb)
    assert np.allclose(on.rgb, off.rgb, atol=1e-5)
    assert on.inject is True and on.inject_applied is False
    assert off.inject is False and off.inject_applied is False
    assert on.to_meta()["inject_ignored"] is True
    z_on = zero_overlay(img, inject=True)
    z_off = zero_overlay(img, inject=False)
    assert np.allclose(z_on, z_off, atol=1e-5)


def test_tazel_vyrn_inject_on_paints_off_gray() -> None:
    img = synthetic_page(96, 96)
    t_on = tazel_overlay(img, inject=True)
    t_off = tazel_overlay(img, inject=False)
    v_on = vyrn_overlay(img, inject=True)
    v_off = vyrn_overlay(img, inject=False)
    assert is_achromatic(t_off)
    assert is_achromatic(v_off)
    assert not is_achromatic(t_on)
    assert not is_achromatic(v_on)
    cyan = (slice(62, 67), slice(10, 84))
    mag = (slice(24, 30), slice(20, 78))
    # ON is teal / magenta heat on in-band pixels — paint, not pigment
    assert float(t_on[cyan][..., 1].mean()) > float(t_on[cyan][..., 0].mean())
    assert float(v_on[mag][..., 0].mean()) > float(v_on[mag][..., 1].mean())


def test_named_modes_inject_off_is_gray_of_same_gate() -> None:
    img = synthetic_page(48, 48)
    for mode in LIVE_MODES:
        off = apply_mode(img, mode, inject=False)
        assert is_achromatic(off.rgb), mode
        assert off.inject is False
        assert off.inject_applied is False
        on = apply_mode(img, mode, inject=True)
        if mode == "zero":
            assert is_achromatic(on.rgb)
            assert np.allclose(on.rgb, off.rgb, atol=1e-5)
        else:
            assert on.inject_applied is True
            # same gate: OFF luma tracks ON luma
            from spectrallock.engine import luminance

            assert np.corrcoef(luminance(on.rgb).ravel(), luminance(off.rgb).ravel())[0, 1] > 0.85


def test_inband_pct_fields_before_hit_claim() -> None:
    img = synthetic_page(96, 96)
    rec = analyze(img, "vyrn", inject=True)
    meta = rec.to_meta()
    assert "tazel_inband_pct" in meta
    assert "vyrn_inband_pct" in meta
    assert meta["pigment_recovery"] is False
    assert meta["empty_gate_not_broken_lens"] is True
    assert "paints membership" in INJECT_NOTE.lower() or "false color" in INJECT_NOTE.lower()
    # magenta stroke is in-band for vyrn; the faint "cyan" understroke is ~110°
    # (same class as Voynich leaves) so tazel may be 0.00 — empty gate is a valid reading
    assert meta["vyrn_inband_pct"] > 0.0
    empty = np.empty((32, 32, 3), dtype=np.float32)
    empty[:] = (0.93, 0.88, 0.76)
    band = gate_inband(empty)
    assert band["tazel_inband_pct"] == 0.0
    assert band["vyrn_inband_pct"] == 0.0
    dead = analyze(empty, "tazel", inject=True)
    assert dead.tazel_inband_pct == 0.0
    assert dead.rgb.shape == (32, 32, 3)
    assert np.isfinite(dead.rgb).all()
    teal = np.empty((16, 16, 3), dtype=np.float32)
    teal[:] = (0x1E / 255.0, 0xC9 / 255.0, 0xA5 / 255.0)
    assert gate_inband(teal)["tazel_inband_pct"] == 100.0
    assert analyze(teal, "tazel").tazel_inband_pct == 100.0


def test_composites_and_newer_modes_respect_inject() -> None:
    img = synthetic_page(64, 64)
    for mode in ("rosetta", "zen", "chaos", "balance", "uv", "candle", "indent", "lemon"):
        on = apply_mode(img, mode, inject=True)
        off = apply_mode(img, mode, inject=False)
        assert is_achromatic(off.rgb), mode
        assert not is_achromatic(on.rgb), mode
        assert on.inject_applied is True


def test_tint_alias_still_maps_to_inject() -> None:
    img = synthetic_page(24, 24)
    a = apply_mode(img, "rosetta", tint=False)
    b = apply_mode(img, "rosetta", inject=False)
    assert np.allclose(a.rgb, b.rgb, atol=1e-5)
    assert is_achromatic(a.rgb)


def test_spectrallock_inject_cli_on_off_all(tmp_path: Path, capsys) -> None:
    from spectrallock.engine import save_rgb

    src = tmp_path / "page.jpg"
    save_rgb(synthetic_page(32, 32), str(src))
    on = tmp_path / "vyrn_on.jpg"
    off = tmp_path / "vyrn_off.jpg"
    assert inject_main([str(src), "--mode", "vyrn", "--inject", "-o", str(on), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "vyrn"
    assert payload["inject"] is True
    assert payload["inject_applied"] is True
    assert "tazel_inband_pct" in payload
    assert "vyrn_inband_pct" in payload
    assert payload["pigment_recovery"] is False
    assert on.is_file()

    assert inject_main([str(src), "--mode", "vyrn", "--no-inject", "-o", str(off), "--json"]) == 0
    payload_off = json.loads(capsys.readouterr().out)
    assert payload_off["inject"] is False
    assert payload_off["inject_applied"] is False
    assert off.is_file()

    outdir = tmp_path / "all_on"
    assert inject_main([str(src), "--all", "--inject", "--outdir", str(outdir)]) == 0
    capsys.readouterr()
    for mode in LIVE_MODES:
        assert (outdir / f"{mode}.png").is_file()

    zero_out = tmp_path / "zero.png"
    assert inject_main([
        str(src), "--mode", "zero", "--target", "ink", "--no-inject",
        "-o", str(zero_out), "--json",
    ]) == 0
    z = json.loads(capsys.readouterr().out)
    assert z["mode"] == "zero"
    assert z["inject_applied"] is False
    assert z["inject_ignored"] is False  # requested off, so not "ignored on"
    assert zero_out.is_file()


def test_overlay_cli_inject_json(tmp_path: Path, capsys) -> None:
    from spectrallock.cli import main
    from spectrallock.engine import save_rgb

    src = tmp_path / "page.png"
    dst = tmp_path / "out.png"
    save_rgb(synthetic_page(24, 24), str(src))
    assert main(["overlay", "--mode", "tazel", "--no-inject", str(src), str(dst), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["inject"] is False
    assert payload["tazel_inband_pct"] >= 0.0
    assert payload["vyrn_inband_pct"] >= 0.0
    assert main(["overlay", "--mode", "tazel", "--inject", str(src), str(dst), "--verify"]) == 0
    out = capsys.readouterr().out
    assert "tazel_inband_pct:" in out
    assert "vyrn_inband_pct:" in out
    assert "inject:" in out
