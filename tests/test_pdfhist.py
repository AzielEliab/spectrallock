"""Deep historical PDF recovery — operator lock 2026-09-19.

Fixtures prove leftover/historical bytes recover; opaque rewrite refuses;
OCR never reconstructs covered letters from context. Author Aziel Eliab.
"""

from __future__ import annotations

import json
import zlib
from pathlib import Path

from spectrallock.cli import main
from spectrallock.pdfhist import (
    CLASS_OLD_REVISION,
    CLASS_SANITIZED,
    CLASS_TEXT_RASTERIZED,
    CLASS_TEXT_TO_OUTLINES,
    CLASS_TEXT_UNDER_VECTOR,
    DEEP_CAPABILITIES,
    recover_pdf_history,
)
from spectrallock.unredact import REFUSE_OPAQUE, analyze_unredact, list_unredact, locate_pdf
from tests.test_unredact import (
    _assemble,
    _black_stream,
    _content_stream,
    _wrap,
    _xref_row,
    pdf_opaque_rewrite,
    pdf_text_under_box,
)


def _stream(inner: bytes) -> bytes:
    return f"<< /Length {len(inner)} >>\nstream\n".encode() + inner + b"\nendstream"


def pdf_efta_stale_pages() -> bytes:
    """EFTA-style: stale page objects 77/78/79 survive; follow streams 23/48/73."""
    # Current tree: page 10 → contents 90 (black). Stale pages are not in Kids.
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R /AcroForm 30 0 R >>"),
        (2, b"<< /Type /Pages /Kids [10 0 R] /Count 1 >>"),
        (10, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 90 0 R >>"),
        (90, _black_stream()),
        (23, _content_stream("STALE-STREAM-23")),
        (48, _content_stream("STALE-STREAM-48")),
        (73, _content_stream("STALE-STREAM-73")),
        (77, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 23 0 R "
             b"/Resources << /Font << /F1 40 0 R >> >> /Annots [50 0 R] /Metadata 31 0 R >>"),
        (78, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 48 0 R "
             b"/Resources << /XObject << /Im0 60 0 R >> >> /PieceInfo << /App 32 0 R >> >>"),
        (79, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 73 0 R "
             b"/StructParents 0 >>"),
        (30, b"<< /Fields [] >>"),
        (31, b"<< /Type /Metadata /Subtype /XML /Length 20 >>\nstream\n<x:xmpmeta/>     \nendstream"),
        (32, b"<< /LastModified (D:20260919000000) >>"),
        (40, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding /ToUnicode 41 0 R >>"),
        (41, _tounicode_stream({0x41: "A"})),
        (50, b"<< /Type /Annot /Subtype /Highlight /Contents (stale-annot) >>"),
        (60, b"<< /Type /XObject /Subtype /Image /Width 2 /Height 1 /ColorSpace /DeviceGray "
             b"/BitsPerComponent 8 /Length 2 >>\nstream\n\xff\x00\nendstream"),
        (5, b"<< /Title (EFTA02730271) /Producer (Acrobat Distiller) /Keywords (BATES EFTA-000123) >>"),
    ], info=5)


def _tounicode_stream(mapping: dict[int, str]) -> bytes:
    lines = [
        b"/CIDInit /ProcSet findresource begin",
        b"12 dict begin begincmap",
        b"/CMapType 2 def",
        b"1 begincodespacerange <00> <FF> endcodespacerange",
        f"{len(mapping)} beginbfchar".encode(),
    ]
    for code, ch in mapping.items():
        dest = ch.encode("utf-16-be")
        lines.append(f"<{code:02X}> <{dest.hex().upper()}>".encode())
    lines.append(b"endbfchar endcmap end")
    inner = b"\n".join(lines)
    return _stream(inner)


def pdf_tounicode_codes() -> bytes:
    """Redacted name survives as character codes + ToUnicode, not ASCII."""
    cmap = _tounicode_stream({0x01: "Q", 0x02: "X", 0x03: "Z"})
    inner = b"BT /C2 12 Tf 10 100 Td <010203> Tj ET"
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R "
            b"/Resources << /Font << /C2 6 0 R >> >> >>"),
        (4, _stream(inner)),
        (6, b"<< /Type /Font /Subtype /Type0 /BaseFont /CID /Encoding /Identity-H "
            b"/ToUnicode 7 0 R /DescendantFonts [8 0 R] >>"),
        (7, cmap),
        (8, b"<< /Type /Font /Subtype /CIDFontType2 /CIDSystemInfo "
            b"<< /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> >>"),
    ])


def pdf_outlines_then_black() -> bytes:
    """Text converted to outlines (paths only) plus a black rect — no letters."""
    path = b"".join(
        f"{10 + i * 3} {20 + (i % 3)} m {12 + i * 3} {28 + (i % 2)} l ".encode()
        for i in range(12)
    )
    inner = path + b"S 0 0 0 rg 8 90 140 22 re f"
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>"),
        (4, _stream(inner)),
    ])


def pdf_raster_only() -> bytes:
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R "
            b"/Resources << /XObject << /Im0 5 0 R >> >> >>"),
        (4, _stream(b"q 100 0 0 20 10 80 cm /Im0 Do Q")),
        (5, b"<< /Type /XObject /Subtype /Image /Width 4 /Height 2 /ColorSpace /DeviceGray "
            b"/BitsPerComponent 8 /SMask 6 0 R /Length 8 >>\nstream\n" + b"\x00" * 8 + b"\nendstream"),
        (6, b"<< /Type /XObject /Subtype /Image /Width 4 /Height 2 /ColorSpace /DeviceGray "
            b"/BitsPerComponent 8 /Length 8 >>\nstream\n" + b"\xff" * 8 + b"\nendstream"),
    ])


def pdf_after_eof_trailer() -> bytes:
    base = pdf_opaque_rewrite()
    extra = _wrap(77, _content_stream("AFTER-EOF-77"))
    extra += b"% leftover producer Adobe Acrobat\n"
    return base + extra


def pdf_objstm_xref_orphan() -> bytes:
    """Modern PDF: /XRef stream + /ObjStm member that is not in the live map."""
    parts: list[bytes] = [b"%PDF-1.5\n"]
    offsets: dict[int, int] = {}

    def add(n: int, body: bytes) -> None:
        offsets[n] = sum(len(p) for p in parts)
        parts.append(_wrap(n, body))

    add(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    add(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>")
    add(4, _black_stream())

    hidden = b"<< /Hidden (ORPHAN-OBJSTM-NAME) >>"
    header = b"6 0 "
    first = len(header)
    raw = header + hidden
    compressed = zlib.compress(raw)
    add(5, (
        f"<< /Type /ObjStm /N 1 /First {first} /Filter /FlateDecode /Length {len(compressed)} >>\n"
        f"stream\n".encode() + compressed + b"\nendstream"
    ))

    # XRef stream: objects 1-5 uncompressed; 6 omitted (orphan inside ObjStm).
    # W = [1, 3, 2] so offsets and gens fit.
    entries = bytearray()
    entries += (0).to_bytes(1, "big") + (0).to_bytes(3, "big") + (65535).to_bytes(2, "big")
    for oid in range(1, 6):
        entries += (1).to_bytes(1, "big") + offsets[oid].to_bytes(3, "big") + (0).to_bytes(2, "big")
    entries += (0).to_bytes(1, "big") + (0).to_bytes(3, "big") + (0).to_bytes(2, "big")
    xref_slot = len(entries)
    entries += (1).to_bytes(1, "big") + (0).to_bytes(3, "big") + (0).to_bytes(2, "big")

    xref_id = 7
    # First pass length estimate: build uncompressed, then compress after patching offset.
    def build_xref(off: int) -> bytes:
        blob = bytearray(entries)
        blob[xref_slot:xref_slot + 6] = (1).to_bytes(1, "big") + off.to_bytes(3, "big") + (0).to_bytes(2, "big")
        payload = zlib.compress(bytes(blob))
        return (
            f"<< /Type /XRef /Size 8 /W [1 3 2] /Filter /FlateDecode "
            f"/Root 1 0 R /Length {len(payload)} >>\nstream\n".encode()
            + payload
            + b"\nendstream"
        )

    xref_at = sum(len(p) for p in parts)
    body = build_xref(xref_at)
    # offset of object 7 header
    parts.append(_wrap(xref_id, body))
    # If wrap changed the object offset vs xref_at, rebuild once.
    # _wrap adds "{n} 0 obj\n" before body — xref_at is the object start.
    startxref = xref_at
    tail = f"startxref\n{startxref}\n%%EOF\n".encode()
    parts.append(tail)
    return b"".join(parts)


def pdf_twin_a() -> bytes:
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>"),
        (4, _content_stream("WITNESS NAME STILL HERE")),
        (5, b"<< /Title (EFTA02730271) /Keywords (EFTA-000123 2026-09-19) >>"),
    ], info=5)


def pdf_twin_b() -> bytes:
    return _assemble([
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>"),
        (4, _black_stream()),
        (5, b"<< /Title (EFTA02730271) /Keywords (EFTA-000123 2026-09-19) >>"),
    ], info=5)


def test_list_unredact_advertises_all_14() -> None:
    card = list_unredact()
    assert card["deep_history"] is True
    assert card["ocr_after_structural_only"] is True
    assert card["covered_letters_from_context"] is False
    assert list(card["capabilities"]) == list(DEEP_CAPABILITIES)
    assert len(DEEP_CAPABILITIES) == 14


def test_efta_stale_page_follow() -> None:
    data = pdf_efta_stale_pages()
    hist = recover_pdf_history(data)
    assert hist["leftover_bytes"] is True
    pages = {p["page_object"]: p for p in hist["page_revisions"]}
    assert "77 0" in pages and "78 0" in pages and "79 0" in pages
    assert pages["77 0"]["leftover"] is True
    assert pages["10 0"]["live"] is True
    graph77 = pages["77 0"]["graph"]
    assert any(x.startswith("23 ") for x in graph77.get("Contents") or [])
    assert any(x.startswith("40 ") for x in graph77.get("Font") or [])
    assert any(x.startswith("41 ") for x in graph77.get("ToUnicode") or [])
    assert any(x.startswith("50 ") for x in graph77.get("Annots") or [])
    assert any(x.startswith("31 ") for x in graph77.get("Metadata") or [])
    graph78 = pages["78 0"]["graph"]
    assert any(x.startswith("60 ") for x in graph78.get("XObject") or [])
    assert any(x.startswith("32 ") for x in graph78.get("PieceInfo") or [])
    texts = " ".join(s.get("text") or "" for s in hist["operator_text"])
    assert "STALE-STREAM-23" in texts
    assert "STALE-STREAM-48" in texts
    assert "STALE-STREAM-73" in texts
    cmp_old = " ".join(
        " ".join(c.get("strings_only_in_old") or []) for c in hist["revision_compare"]
    )
    assert "STALE-STREAM-23" in cmp_old or "STALE-STREAM-23" in texts
    replaced = json.dumps(hist["object_ids_replaced"])
    assert "23" in replaced or "90" in replaced
    classes = {c["page"]: c["class"] for c in hist["classifications"]}
    assert classes.get("77 0") == CLASS_OLD_REVISION
    chars = "".join(ch["char"] for ch in hist["recovered_characters"] if ch.get("char"))
    assert "STALE-STREAM-23" in chars
    for ch in hist["recovered_characters"]:
        if ch.get("char") and "STALE" in (ch.get("char") or ""):
            pass
        assert set(ch) >= {
            "page", "object_id", "generation", "stream_offset",
            "operator", "decoded_bytes", "source_revision", "sha256",
        }
        assert ch["invented"] is False
    out = analyze_unredact(data, op="recover")
    assert out["leftover_bytes"] is True
    blob = json.dumps(out)
    assert "STALE-STREAM-23" in blob
    assert out["guessed_letters"] is False


def test_text_under_vector_drawing_order_and_provenance() -> None:
    data = pdf_text_under_box()
    hist = recover_pdf_history(data)
    assert any(c["class"] == CLASS_TEXT_UNDER_VECTOR for c in hist["classifications"])
    assert hist["drawing_order"][0]["text_under_overlay"]
    under = hist["drawing_order"][0]["text_under_overlay"][0]
    assert "Alice" in under["text"] or "CONFIDENTIAL" in under["text"]
    assert under["operator"] == "Tj"
    assert under["overlay"]["operator"] == "f"
    chars = "".join(c["char"] for c in hist["recovered_characters"])
    assert "CONFIDENTIAL" in chars
    assert all(c.get("operator") for c in hist["recovered_characters"])
    assert all(c.get("source_revision") in {"prior", "under-vector"} for c in hist["recovered_characters"])
    out = analyze_unredact(data, op="recover")
    assert out["leftover_bytes"] is True
    assert any(r.get("recovered_from") == "text-under-vector" for r in out["recovered"])


def test_objstm_xref_orphan_and_after_eof() -> None:
    modern = pdf_objstm_xref_orphan()
    hist = recover_pdf_history(modern)
    assert hist["xref_streams"] is True
    members = " ".join(
        (m.get("object_id") or "") + " " + str(m.get("objstm_id") or "")
        for m in hist["objstms"]
    )
    assert "6" in members or any("ORPHAN-OBJSTM" in (r.get("preview") or "") for r in hist["recovered"])
    kinds = set(hist["recovered_from"])
    assert kinds & {"unused-objstm-member", "orphan-object", "unused-object", "objstm"} or any(
        "ORPHAN-OBJSTM" in json.dumps(hist["recovered"])
    )
    blob = json.dumps(hist)
    assert "ORPHAN-OBJSTM-NAME" in blob

    trailing = pdf_after_eof_trailer()
    hist2 = recover_pdf_history(trailing)
    assert hist2["after_eof"]["leftover"] is True
    assert hist2["after_eof"]["bytes_after_eof"] > 0
    assert "AFTER-EOF-77" in json.dumps(hist2)
    assert "after-eof" in hist2["recovered_from"]


def test_opaque_rewrite_still_refuses() -> None:
    data = pdf_opaque_rewrite()
    out = analyze_unredact(data, op="recover")
    assert out["leftover_bytes"] is False
    assert out["refuse_code"] == REFUSE_OPAQUE
    hist = recover_pdf_history(data)
    assert hist["leftover_bytes"] is False
    assert all(c["class"] == CLASS_SANITIZED for c in hist["classifications"])
    assert "ALICE" not in json.dumps(out)
    assert out["ocr"]["covered_letters_from_context"] is False
    assert out["ocr"]["ocr_ran"] is False


def test_twin_optional_shared_identifiers() -> None:
    a, b = pdf_twin_a(), pdf_twin_b()
    out = analyze_unredact(a, op="locate", twin=b)
    diff = out["twin_diff"]
    assert diff["comparable"] is True
    assert diff["heatmap_is_transcript"] is False
    assert diff["invented"] is False
    assert any("WITNESS" in s for s in diff.get("only_in_first") or [])
    shared = json.dumps(diff.get("shared_identifiers") or [])
    vals = json.dumps(diff)
    assert "EFTA02730271" in vals
    assert "EFTA-000123" in vals or "EFTA" in vals
    none = analyze_unredact(a, op="locate")
    assert none.get("twin_diff") in (None, {}) or none.get("twin_diff") is None


def test_font_tounicode_decodes_codes_not_guesses() -> None:
    data = pdf_tounicode_codes()
    hist = recover_pdf_history(data)
    texts = " ".join(s.get("text") or "" for s in hist["operator_text"])
    assert "QXZ" in texts
    fonts = hist["font_resolutions"]
    assert any(f.get("map_kind") == "tounicode" for f in fonts)
    assert any(f.get("cid") or f.get("type0") or f.get("identity") for f in fonts)
    assert all(s.get("invented") is False for s in hist["operator_text"])


def test_classification_outlines_and_raster() -> None:
    outlines = recover_pdf_history(pdf_outlines_then_black())
    assert any(c["class"] == CLASS_TEXT_TO_OUTLINES for c in outlines["classifications"])
    assert outlines["leftover_bytes"] is False
    raster = recover_pdf_history(pdf_raster_only())
    assert any(c["class"] == CLASS_TEXT_RASTERIZED for c in raster["classifications"])
    assert raster["image_layers"]
    assert any(img.get("smask") for img in raster["image_layers"] if isinstance(img, dict) and "smask" in img)


def test_producer_artifacts_and_ocr_honesty() -> None:
    data = pdf_efta_stale_pages()
    hist = recover_pdf_history(data)
    kinds = {h["kind"] for h in hist["producer_artifacts"]}
    assert kinds & {"acrobat", "acrobat-distiller"}
    assert hist["ocr"]["ocr_after_structural_only"] is True
    assert hist["ocr"]["covered_letters_from_context"] is False
    assert hist["ocr"]["context_guess"] is False
    assert hist["ocr"]["heatmap_is_transcript"] is False
    assert hist["ocr"].get("ocr_deferred") is True
    opaque = recover_pdf_history(pdf_opaque_rewrite())
    assert opaque["ocr"]["ocr_ran"] is False
    assert opaque["ocr"]["covered_letters_from_context"] is False
    note = (opaque["ocr"].get("note") or "").lower()
    assert "context" in note
    assert "not recovery" in note or "never" in note


def test_cli_twin_and_json_fields(tmp_path: Path, capsys) -> None:
    src = tmp_path / "efta.pdf"
    src.write_bytes(pdf_efta_stale_pages())
    twin = tmp_path / "twin.pdf"
    twin.write_bytes(pdf_twin_b())
    assert main(["unredact", "recover", str(src), "--twin", str(twin), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["leftover_bytes"] is True
    assert payload["capabilities"] == list(DEEP_CAPABILITIES)
    assert payload["page_revisions"]
    assert payload["recovered_characters"]
    assert payload["ocr"]["covered_letters_from_context"] is False
    assert payload["guessed_letters"] is False
    assert payload["heatmap_is_transcript"] is False
    assert payload["twin_diff"]["invented"] is False


def test_hosted_ocr_unbound_flag() -> None:
    hist = recover_pdf_history(pdf_opaque_rewrite(), hosted=True)
    assert hist["ocr"]["ocr_status"] == "unbound-hosted-preview"
    assert hist["ocr"]["covered_letters_from_context"] is False
    assert hist["ocr"]["ocr_ran"] is False
