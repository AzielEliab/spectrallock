"""Import PNG/JPEG, export overlay PNG + JSON sidecar. Hashes match files."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from spectrallock.cli import main
from spectrallock.engine import LIVE_MODES, save_rgb, sha256_hex, synthetic_page


def test_import_export_roundtrip_png_sidecar(tmp_path: Path) -> None:
    src = tmp_path / "page.png"
    dst = tmp_path / "out.png"
    save_rgb(synthetic_page(48, 32), str(src))
    assert main(["overlay", "--mode", "balance", str(src), str(dst), "--sidecar", "--json"]) == 0
    sidecar = tmp_path / "out.json"
    assert dst.is_file() and sidecar.is_file()
    rec = json.loads(sidecar.read_text(encoding="utf-8"))
    assert rec["mode"] == "balance"
    assert rec["paper"] == "BSA"
    assert rec["sha256_in"] == sha256_hex(src.read_bytes())
    assert rec["sha256_out"] == sha256_hex(dst.read_bytes())
    assert rec["size_in"] == src.stat().st_size
    assert rec["size_out"] == dst.stat().st_size
    assert "limitation" in rec
    assert "forensic" in rec["limitation"].lower()
    img = Image.open(dst)
    assert img.size == (48, 32)


def test_import_jpeg_export_png_sidecar(tmp_path: Path) -> None:
    src = tmp_path / "page.jpg"
    dst = tmp_path / "out.png"
    arr = synthetic_page(40, 24)
    Image.fromarray((arr * 255).astype("uint8"), "RGB").save(src, quality=90)
    assert main(["overlay", "--mode", "tazel", str(src), str(dst), "--sidecar"]) == 0
    rec = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    assert rec["mode"] == "tazel"
    assert rec["sha256_in"] == sha256_hex(src.read_bytes())
    assert rec["sha256_out"] == sha256_hex(dst.read_bytes())
    assert Image.open(dst).format == "PNG"


def test_roundtrip_all_eight_modes_write_png(tmp_path: Path) -> None:
    src = tmp_path / "page.png"
    save_rgb(synthetic_page(24, 24), str(src))
    for mode in LIVE_MODES:
        dst = tmp_path / f"{mode}.png"
        assert main(["overlay", "--mode", mode, str(src), str(dst)]) == 0
        assert dst.is_file()
        assert Image.open(dst).size == (24, 24)
