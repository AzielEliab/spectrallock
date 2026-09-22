"""Restore lost pigment: evidence recovers, empty pages refuse, overlay stays false."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from spectrallock.engine import analyze, png_bytes, save_rgb, synthetic_page
from spectrallock.pigment import (
    REFUSE_GONE,
    analyze_pigment,
    list_pigment,
)
from spectrallock.cli import main


def _cream(h: int = 32, w: int = 32) -> np.ndarray:
    img = np.empty((h, w, 3), dtype=np.float32)
    img[:] = (0.93, 0.88, 0.76)
    return img


def _faded() -> np.ndarray:
    img = _cream(64, 64)
    parch = np.array([0.93, 0.88, 0.76], dtype=np.float32)
    cue = np.array([0.45, 0.62, 0.28], dtype=np.float32)
    img[20:36, 12:48] = 0.72 * parch + 0.28 * cue
    return img


def test_list_pigment_is_live() -> None:
    card = list_pigment()
    assert card["status"] == "live"
    assert card["refuse_code"] == REFUSE_GONE
    assert "restore" in card["ops"]
    assert card["invented_marks"] is False
    assert "pigment" in card["family"]
    assert "restore-pigment" in card["family"]


def test_faded_signal_restores_and_blank_refuses() -> None:
    hit = analyze_pigment(_faded(), op="restore")
    assert hit["pigment_recovery"] is True
    assert hit["recovered"] is True
    assert hit["refuse_code"] is None
    assert hit["evidence_pixels"] >= 24
    assert hit["invented_marks"] is False
    assert hit["unchanged_outside_support"] is True
    assert hit["png_b64"]
    assert hit["wheel_paint_used"] is False
    assert hit["pixels_changed"] > 0

    gone = analyze_pigment(_cream(), op="restore")
    assert gone["pigment_recovery"] is True
    assert gone["recovered"] is False
    assert gone["refuse_code"] == REFUSE_GONE
    assert gone["png_b64"] is None
    assert gone["pixels_changed"] == 0
    assert gone["invented_marks"] is False


def test_overlay_receipt_does_not_claim_pigment_recovery() -> None:
    rec = analyze(synthetic_page(32, 32), "tazel")
    assert rec.to_meta()["pigment_recovery"] is False


def test_visible_ink_alone_is_not_lost_pigment() -> None:
    img = _cream(48, 48)
    img[16:28, 8:40] = (0.08, 0.06, 0.05)
    out = analyze_pigment(img, op="restore")
    assert out["pigment_recovery"] is True
    assert out["recovered"] is False
    assert out["refuse_code"] == REFUSE_GONE
    assert out["visible_ink_pixels"] > 0


def test_cli_pigment_and_restore_alias(tmp_path: Path, capsys) -> None:
    src = tmp_path / "faded.png"
    blank = tmp_path / "blank.png"
    out = tmp_path / "restored.png"
    save_rgb(_faded(), str(src))
    save_rgb(_cream(), str(blank))
    assert main(["pigment", "restore", str(src), "-o", str(out), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pigment_recovery"] is True
    assert payload["recovered"] is True
    assert out.is_file()
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    assert main(["restore-pigment", str(blank), "--json"]) == 2
    refused = json.loads(capsys.readouterr().out)
    assert refused["refuse_code"] == REFUSE_GONE
    assert refused["pigment_recovery"] is True
    assert refused["recovered"] is False

    modes = main(["modes", "--json"])
    assert modes == 0
    listed = json.loads(capsys.readouterr().out)
    assert "pigment" in listed["live_modes"]


def test_estimate_returns_density_without_inventing() -> None:
    est = analyze_pigment(_faded(), op="estimate")
    assert est["recovered"] is True
    assert est["op"] == "estimate"
    raw = __import__("base64").b64decode(est["png_b64"])
    assert raw[:8] == png_bytes(np.zeros((1, 1, 3), dtype=np.float32))[:8]
