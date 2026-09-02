"""SPECTRALLOCK_DEBUG=1 writes traces to stderr and never image bytes."""

from __future__ import annotations

from pathlib import Path

from spectrallock.cli import main
from spectrallock.engine import save_rgb, synthetic_page


def test_debug_stderr_has_mode_not_image_bytes(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("SPECTRALLOCK_DEBUG", "1")
    src = tmp_path / "page.png"
    dst = tmp_path / "out.png"
    save_rgb(synthetic_page(16, 16), str(src))
    assert main(["overlay", "--mode", "rosetta", str(src), str(dst), "--verify"]) == 0
    err = capsys.readouterr().err
    assert "spectrallock-debug:" in err
    assert "mode=rosetta" in err
    assert "sha256_in=" in err
    assert "sha256_out=" in err
    assert "\x89PNG" not in err
    assert "iVBORw0" not in err
    # no raw pixel dump
    assert "0.93" not in err
