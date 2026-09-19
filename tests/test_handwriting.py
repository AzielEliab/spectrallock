"""Handwriting family — synthetic scan heuristics. Not a lab."""

from __future__ import annotations

import json

import numpy as np

from spectrallock.cli import main
from spectrallock.engine import png_bytes
from spectrallock.handwriting import (
    HANDWRITING_OPS,
    REFUSE_NO_INK,
    REFUSE_UNSUPPORTED,
    analyze_handwriting,
    list_handwriting,
    parse_handwriting_op,
)


def _page(h: int = 64, w: int = 96, paper: float = 0.92) -> np.ndarray:
    return np.ones((h, w, 3), dtype=np.float32) * paper


def _stroke(img: np.ndarray, x0: int, x1: int, y: int, *, width: int = 2, dark: float = 0.12) -> None:
    img[max(0, y - width) : y + width + 1, x0:x1] = dark


def _png(rgb: np.ndarray) -> bytes:
    return png_bytes(rgb)


def _heavy() -> bytes:
    img = _page()
    _stroke(img, 8, 80, 28, width=4, dark=0.08)
    _stroke(img, 10, 70, 40, width=3, dark=0.10)
    return _png(img)


def _light() -> bytes:
    img = _page()
    _stroke(img, 10, 78, 30, width=1, dark=0.42)
    return _png(img)


def _whiteout() -> bytes:
    img = _page()
    _stroke(img, 6, 88, 32, width=3, dark=0.10)
    img[24:42, 36:62] = 0.995
    return _png(img)


def _cloned() -> bytes:
    img = _page(80, 120)
    _stroke(img, 8, 40, 22, width=3, dark=0.10)
    img[18:28, 70:102] = img[18:28, 8:40]
    img[40:50, 70:102] = img[18:28, 8:40]
    return _png(img)


def test_ops_and_card() -> None:
    card = list_handwriting()
    assert card["no_lie"] is True
    assert card["esda"] is False
    assert card["writer_identification_as_fact"] is False
    assert card["forensic_certification"] is False
    for op in HANDWRITING_OPS:
        assert op in card["ops"]
    assert card["feature_matrix"]["esda"]["status"] == "slot"
    assert card["feature_matrix"]["stroke_weight"]["status"] == "live"
    assert parse_handwriting_op("handwrite") == "analyze"
    assert parse_handwriting_op("forgery-scan") == "forgery-indicators"


def test_heavy_vs_light_weight() -> None:
    heavy = analyze_handwriting(_heavy(), op="analyze", filename="heavy.png")
    light = analyze_handwriting(_light(), op="analyze", filename="light.png")
    assert heavy["no_lie"] is True
    assert heavy.get("refuse_code") != REFUSE_NO_INK
    assert light.get("refuse_code") != REFUSE_NO_INK
    hw = heavy["features"]["weight"][0]["mean_px"]
    lw = light["features"]["weight"][0]["mean_px"]
    assert hw > lw
    both = analyze_handwriting(_heavy(), op="compare", filename="q.png", twin=_light(), twin_name="k.png")
    assert both["side_by_side"]
    assert both["compare"]["weight_delta"] != 0
    assert "not a same-writer" in both["compare"]["note"].lower() or "not a" in both["compare"]["note"].lower()


def test_whiteout_erasure_candidate() -> None:
    out = analyze_handwriting(_whiteout(), op="analyze", filename="wo.png")
    kinds = [e.get("kind") for e in out["features"]["erasures"]]
    assert "abrasion-brightening" in kinds
    assert all(o.get("heatmap_is_transcript") is False for o in out["overlays"])
    assert all(o.get("heatmap_is_court_finding") is False for o in out["overlays"])
    assert "human verification required" in json.dumps(out["forgery_indicators"]).lower() or out["warnings"]


def test_cloned_patch_flag() -> None:
    out = analyze_handwriting(_cloned(), op="forgery-indicators", filename="clone.png")
    kinds = [i["kind"] for i in out["forgery_indicators"]]
    assert "clone-stamp" in kinds
    for ind in out["forgery_indicators"]:
        assert ind["invented"] is False
        assert "human verification required" in ind["phrasing"]
        assert "not a finding that this is forged" in ind["confidence_means"]


def test_graph_nodes_and_edges() -> None:
    out = analyze_handwriting(_heavy(), op="graph", filename="g.png")
    assert out["graph"]["nodes"]
    assert out["graph"]["invented"] is False
    assert out["strokes"]


def test_blank_refuses_no_ink() -> None:
    out = analyze_handwriting(_png(_page()), op="analyze", filename="blank.png")
    assert out["refuse_code"] == REFUSE_NO_INK
    assert out["no_lie"] is True


def test_corrupt_refuses_unsupported() -> None:
    out = analyze_handwriting(b"not-an-image", op="analyze")
    assert out["refuse_code"] == REFUSE_UNSUPPORTED


def test_helpers_cited_not_esda() -> None:
    out = analyze_handwriting(_heavy(), op="analyze", filename="h.png")
    modes = {m["mode"] for m in out["helper_modes"]}
    assert "indent" in modes
    assert any("not ESDA" in (m.get("note") or "") for m in out["helper_modes"])
    assert out["esda"] is False


def test_cli_handwriting_json(tmp_path, capsys) -> None:
    src = tmp_path / "ink.png"
    src.write_bytes(_heavy())
    assert main(["handwriting", "analyze", str(src), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["family"] == "handwriting"
    assert payload["no_lie"] is True
    assert payload["forensic_certification"] is False


def test_cli_forgery_scan_alias(tmp_path, capsys) -> None:
    src = tmp_path / "clone.png"
    src.write_bytes(_cloned())
    assert main(["forgery-scan", str(src), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["op"] == "forgery-indicators"
    kinds = [i["kind"] for i in payload["forgery_indicators"]]
    assert "clone-stamp" in kinds
