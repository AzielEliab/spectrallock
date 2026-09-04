"""CLI: version, modes, overlay --json, JPEG in, loopback UI."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from spectrallock import LIMITATION, __version__
from spectrallock.cli import main
from spectrallock.engine import LIVE_MODES, synthetic_page
from spectrallock.ui import LOOPBACK, make_server


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"spectrallock {__version__}"


def test_cli_lenses_alias(capsys) -> None:
    assert main(["lenses"]) == 0
    out = capsys.readouterr().out
    for mode in LIVE_MODES:
        assert mode in out
    assert "targets: ink" in out


def test_cli_modes_lists_all_live(capsys) -> None:
    assert main(["modes"]) == 0
    out = capsys.readouterr().out
    for mode in LIVE_MODES:
        assert mode in out
    assert "ZSA-1.0" in out
    assert "TSA-1.0" in out
    assert "VSA-1.0" in out
    assert "UVSA-1.0" in out
    assert "RSA-2.0" in out
    assert "ZENA-1.0" in out
    assert "CSA-1.0" in out
    assert "BSA" in out
    assert "live" in out
    assert "reserved" not in out.lower() or "not" in LIMITATION.lower()


def test_cli_modes_json(capsys) -> None:
    assert main(["modes", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    ids = [m["id"] for m in payload["modes"]]
    assert ids == list(LIVE_MODES)
    assert all(m["status"] == "live" for m in payload["modes"])
    assert "rosetta" in payload["advisory"].lower()
    assert payload["targets"]
    assert payload["lenses"]


def test_cli_overlay_png_and_json(tmp_path: Path, capsys) -> None:
    import numpy as np
    from spectrallock.engine import save_rgb

    src = tmp_path / "page.png"
    dst = tmp_path / "out.png"
    save_rgb(synthetic_page(32, 32), str(src))
    assert main(["overlay", "--mode", "tazel", str(src), str(dst), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "tazel"
    assert payload["width"] == 32 and payload["height"] == 32
    assert "com" in payload and "x" in payload["com"]
    assert dst.is_file()
    img = Image.open(dst)
    assert img.size == (32, 32)


def test_cli_overlay_jpeg_in(tmp_path: Path) -> None:
    from spectrallock.engine import save_rgb

    src = tmp_path / "page.jpg"
    dst = tmp_path / "out.png"
    arr = synthetic_page(40, 24)
    Image.fromarray((arr * 255).astype("uint8"), "RGB").save(src, quality=90)
    assert main(["overlay", "--mode", "zero", str(src), str(dst)]) == 0
    assert dst.is_file()


def test_ui_rejects_non_loopback() -> None:
    import pytest

    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK



def test_cli_doctor_runs_eight_modes(capsys) -> None:
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    for mode in LIVE_MODES:
        assert f"lens {mode} ink: ok" in out
        assert f"lens {mode} page: ok" in out
    assert "loopback: 127.0.0.1 only" in out
    assert "telemetry: none" in out
    assert out.strip().endswith("ok")
    assert "spectrallock " + __version__ in out


def test_cli_overlay_target_page(tmp_path: Path, capsys) -> None:
    from spectrallock.engine import save_rgb

    src = tmp_path / "page.png"
    dst = tmp_path / "out.png"
    save_rgb(synthetic_page(24, 24), str(src))
    assert main(["overlay", "--lens", "rosetta", "--target", "page", str(src), str(dst), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["target"] == "page"
    assert payload["lenses"] == ["rosetta"]
    assert dst.is_file()


def test_cli_overlay_verify_prints_hashes(tmp_path: Path, capsys) -> None:
    from spectrallock.engine import save_rgb, sha256_hex

    src = tmp_path / "page.png"
    dst = tmp_path / "out.png"
    save_rgb(synthetic_page(32, 32), str(src))
    assert main(["overlay", "--mode", "uv", str(src), str(dst), "--verify"]) == 0
    out = capsys.readouterr().out
    assert "mode: uv" in out
    assert "paper: UVSA-1.0" in out
    assert "sha256_in: " + sha256_hex(src.read_bytes()) in out
    assert "sha256_out: " + sha256_hex(dst.read_bytes()) in out
    assert "size_in: " in out
    assert "rosetta" in out.lower() or "ink" in out.lower()


def test_cli_rejects_non_image_plainly(tmp_path: Path, capsys) -> None:
    src = tmp_path / "notes.txt"
    src.write_text("hello", encoding="utf-8")
    dst = tmp_path / "out.png"
    assert main(["overlay", "--mode", "zero", str(src), str(dst)]) == 2
    err = capsys.readouterr().err
    assert "not a picture" in err.lower()
    assert "png" in err.lower() or "jpeg" in err.lower()
