"""Honest unredact: opaque refuse, residual lift, leftover-bytes recover, locate."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from spectrallock.cli import main
from spectrallock.engine import png_bytes
from spectrallock.unredact import (
    REFUSE_OPAQUE,
    UNREDACT_NOTE,
    analyze_unredact,
    classify_cover,
    locate_pdf,
)


def _xref_row(offset: int, gen: int = 0, used: bool = True) -> bytes:
    flag = b"n" if used else b"f"
    return f"{offset:010d} {gen:05d} ".encode() + flag + b" \n"


def _wrap(n: int, body: bytes) -> bytes:
    return f"{n} 0 obj\n".encode() + body + b"\nendobj\n"


def _assemble(objs: list[tuple[int, bytes]], *, info: int | None = None, prev: int | None = None) -> bytes:
    parts: list[bytes] = [b"%PDF-1.4\n"]
    offsets: dict[int, int] = {}
    for n, body in objs:
        offsets[n] = sum(len(p) for p in parts)
        parts.append(_wrap(n, body))
    xref_at = sum(len(p) for p in parts)
    max_id = max(n for n, _ in objs)
    xref = [b"xref\n", f"0 {max_id + 1}\n".encode(), _xref_row(0, 65535, False)]
    for i in range(1, max_id + 1):
        xref.append(_xref_row(offsets[i]) if i in offsets else _xref_row(0, 0, False))
    parts.extend(xref)
    trail = f"trailer << /Size {max_id + 1} /Root 1 0 R".encode()
    if info is not None:
        trail += f" /Info {info} 0 R".encode()
    if prev is not None:
        trail += f" /Prev {prev}".encode()
    trail += f" >>\nstartxref\n{xref_at}\n%%EOF\n".encode()
    parts.append(trail)
    return b"".join(parts)


def _content_stream(text: str) -> bytes:
    inner = f"BT /F1 12 Tf 10 100 Td ({text}) Tj ET".encode("latin-1")
    return f"<< /Length {len(inner)} >>\nstream\n".encode() + inner + b"\nendstream"


def _black_stream() -> bytes:
    inner = b"0 0 0 rg 10 80 120 24 re f"
    return f"<< /Length {len(inner)} >>\nstream\n".encode() + inner + b"\nendstream"


def pdf_text_under_box() -> bytes:
    """Live text layer plus a drawn rectangle in the same stream."""
    inner = b"BT /F1 12 Tf 10 100 Td (CONFIDENTIAL Alice Smith) Tj ET\n0 0 0 rg 8 90 140 22 re f"
    stream = f"<< /Length {len(inner)} >>\nstream\n".encode() + inner + b"\nendstream"
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>"),
        (4, stream),
        (5, b"<< /Title (Docket-12) /Author (Clerk) /Keywords (redact-context Alice) >>"),
    ], info=5)


def pdf_opaque_rewrite() -> bytes:
    """Single revision: black only. No leftover text objects."""
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>"),
        (4, _black_stream()),
    ])


def pdf_incremental_leftover() -> bytes:
    """Two-revision incremental update: rev1 replaces object 4; prior ALICE SMITH stream remains.

    /Prev points at the previous xref byte offset (the startxref value), not
    the ``startxref`` token. Used as the hash-stable revision-graph + copy fixture.
    """
    first = _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>"),
        (4, _content_stream("ALICE SMITH")),
        (5, b"<< /Title (Production Set) /Author (Clerk) >>"),
    ], info=5)
    prev_match = re.search(rb"startxref\s+(\d+)", first)
    prev = int(prev_match.group(1)) if prev_match else first.find(b"\nxref\n") + 1
    new_body = _black_stream()
    new_off = len(first)
    tail = _wrap(4, new_body)
    xref_at = new_off + len(tail)
    tail += b"xref\n4 1\n" + _xref_row(new_off)
    tail += f"trailer << /Size 6 /Root 1 0 R /Info 5 0 R /Prev {prev} >>\nstartxref\n{xref_at}\n%%EOF\n".encode()
    return first + tail


def pdf_unused_and_attachment() -> bytes:
    base = _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>"),
        (4, _black_stream()),
        (5, b"<< /Title (Docket-12) /Keywords (Alice) >>"),
    ], info=5)
    hidden = b"<< /Length 28 >>\nstream\nBT (HIDDEN NAME) Tj ET\nendstream"
    embed = b"<< /Type /EmbeddedFile /Length 12 >>\nstream\nSECRET NOTES\nendstream"
    spec = b"<< /Type /Filespec /F (notes.txt) /EF << /F 8 0 R >> >>"
    return base + _wrap(6, hidden) + _wrap(8, embed) + _wrap(9, spec)


def opaque_png() -> bytes:
    img = np.ones((32, 48, 3), dtype=np.float32) * 0.93
    img[8:24, 6:42] = 0.0
    return png_bytes(img)


def residual_png() -> bytes:
    img = np.ones((32, 48, 3), dtype=np.float32) * 0.90
    yy, xx = np.indices((32, 48))
    img[8:24, 6:42] = (0.18 + 0.22 * ((xx[8:24, 6:42] % 9) / 9.0))[..., None]
    return png_bytes(img)


def test_opaque_image_lift_refuses() -> None:
    from spectrallock.engine import load_rgb_bytes

    cover = classify_cover(load_rgb_bytes(opaque_png()))
    assert cover["opaque_replace"] is True
    assert cover["residual_usable"] is False
    out = analyze_unredact(opaque_png(), op="lift")
    assert out["refuse_code"] == REFUSE_OPAQUE
    assert out["leftover_bytes"] is False
    assert out["residual_usable"] is False
    assert out["guessed_letters"] is False
    assert "SL-UNREDACT-OPAQUE" in (out.get("note") or "")
    rec = analyze_unredact(opaque_png(), op="recover")
    assert rec["leftover_bytes"] is False
    assert rec["refuse_code"] == REFUSE_OPAQUE


def test_non_opaque_residual_lift_no_letters() -> None:
    raw = residual_png()
    out = analyze_unredact(raw, op="lift")
    assert out["residual_usable"] is True
    assert out["opaque_replace"] is False
    assert out["leftover_bytes"] is False
    assert out.get("residual_png_b64")
    assert out["heatmap_is_transcript"] is False
    assert out["guessed_letters"] is False
    assert out["pigment_recovery"] is False
    png = __import__("base64").b64decode(out["residual_png_b64"])
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_locate_pdf_text_and_metadata() -> None:
    data = pdf_text_under_box()
    scanned = locate_pdf(data)
    assert scanned["is_pdf"] is True
    blob = " ".join(
        s for loc in scanned["text_layer"] for s in loc.get("strings") or []
    ) + " " + " ".join(h.get("value") or "" for h in scanned["metadata_hits"])
    assert "Alice" in blob or "ALICE" in blob.upper() or "CONFIDENTIAL" in blob
    keys = {h["key"] for h in scanned["metadata_hits"]}
    assert "Title" in keys
    out = analyze_unredact(data, op="locate")
    assert out["guessed_letters"] is False
    assert any("Alice" in (h.get("value") or "") or "Docket" in (h.get("value") or "") for h in out["metadata_hits"])


def test_leftover_incremental_recover() -> None:
    data = pdf_incremental_leftover()
    out = analyze_unredact(data, op="recover")
    assert out["leftover_bytes"] is True
    kinds = set(out["recovered_from"])
    assert kinds & {"prior-stream", "incremental-revision", "pdf-object"}
    previews = " ".join(r.get("preview") or "" for r in out["recovered"])
    assert "ALICE" in previews.upper()
    assert all(r.get("invented") is False for r in out["recovered"])
    assert any("offset" in r and "object_id" in r for r in out["recovered"])
    assert out["refuse_code"] is None
    assert out["guessed_letters"] is False


def test_unused_object_and_attachment_leftover() -> None:
    data = pdf_unused_and_attachment()
    out = analyze_unredact(data, op="locate")
    assert out["leftover_bytes"] is True
    kinds = set(out["recovered_from"])
    assert "unused-object" in kinds or "attachment" in kinds
    blob = " ".join(r.get("preview") or "" for r in out["recovered"])
    blob += " ".join(" ".join(a.get("names") or []) for a in out["attachments"])
    assert "HIDDEN" in blob or "SECRET" in blob or "notes.txt" in blob
    named = analyze_unredact(data, op="locate", query="Alice")
    assert named["name_hits"]
    assert all(h.get("invented") is False for h in named["name_hits"])


def test_opaque_rewrite_pdf_no_leftover_refuses_recover() -> None:
    data = pdf_opaque_rewrite()
    out = analyze_unredact(data, op="recover")
    assert out["leftover_bytes"] is False
    assert out["refuse_code"] == REFUSE_OPAQUE
    assert "ALICE" not in json.dumps(out)


def test_honesty_copy_never_claims_transcript() -> None:
    low = UNREDACT_NOTE.lower()
    for phrase in (
        "not invent",
        "leftover",
        "heatmap",
        "transcript",
        "sl-unredact-opaque",
        "esda",
        "aziel eliab",
        "lamb lens",
    ):
        assert phrase in low
    assert "guess" in low or "invent" in low


def test_cli_unredact_json(tmp_path: Path, capsys) -> None:
    src = tmp_path / "page.pdf"
    src.write_bytes(pdf_text_under_box())
    assert main(["unredact", "locate", str(src), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["op"] == "locate"
    assert payload["guessed_letters"] is False
    assert payload["heatmap_is_transcript"] is False
    rec = tmp_path / "inc.pdf"
    rec.write_bytes(pdf_incremental_leftover())
    assert main(["unredact", "recover", str(rec), "--json"]) == 0
    recovered = json.loads(capsys.readouterr().out)
    assert recovered["leftover_bytes"] is True
    dead = tmp_path / "opaque.pdf"
    dead.write_bytes(pdf_opaque_rewrite())
    assert main(["unredact", "recover", str(dead), "--json"]) == 2
    dead_payload = json.loads(capsys.readouterr().out)
    assert dead_payload["leftover_bytes"] is False
    assert dead_payload["refuse_code"] == REFUSE_OPAQUE
    img = tmp_path / "box.png"
    img.write_bytes(opaque_png())
    assert main(["lift", str(img), "--json"]) == 2
    refused = json.loads(capsys.readouterr().out)
    assert refused["refuse_code"] == REFUSE_OPAQUE


def test_cli_modes_lists_unredact_family(capsys) -> None:
    assert main(["modes"]) == 0
    out = capsys.readouterr().out
    assert "unredact" in out
    assert main(["modes", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["unredact"]["refuse_code"] == REFUSE_OPAQUE
    assert "locate" in payload["unredact"]["ops"]
    assert payload["unredact"]["leftover_bytes_recovery"] is True


def test_twin_pdf_string_residual() -> None:
    a = pdf_text_under_box()
    b = pdf_opaque_rewrite()
    out = analyze_unredact(a, op="locate", twin=b)
    assert out["twin_diff"]
    assert out["twin_diff"]["heatmap_is_transcript"] is False
    assert out["twin_diff"]["invented"] is False
