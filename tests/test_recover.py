"""Universal recover family — present bytes only. NO-LIE."""

from __future__ import annotations

import io
import json
import sqlite3
import zipfile
from email.message import EmailMessage
from pathlib import Path

from PIL import Image

from spectrallock.cli import main
from spectrallock.recover import (
    RECOVER_OPS,
    analyze_recover,
    analyze_recover_path,
    format_matrix,
    list_recover,
    parse_recover_op,
)
from spectrallock.recover.detect import detect_bytes
from tests.test_unredact import pdf_incremental_leftover


def _png(color: tuple[int, int, int], size: tuple[int, int] = (32, 24)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


def _docx_tracked() -> bytes:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Visible Alice</w:t></w:r></w:p>
    <w:p><w:del w:author="Clerk"><w:r><w:delText>ALICE SMITH</w:delText></w:r></w:del></w:p>
    <w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>HIDDEN-VANISH</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    core = """<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:creator>Clerk</dc:creator>
  <dc:title>Production Set</dc:title>
</cp:coreProperties>
"""
    types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", types)
        zf.writestr("word/document.xml", document)
        zf.writestr("docProps/core.xml", core)
        zf.writestr("word/comments.xml", "<w:comments xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:comment><w:p><w:r><w:t>sidebar note</w:t></w:r></w:p></w:comment></w:comments>")
    return buf.getvalue()


def _json_tombstone() -> bytes:
    return json.dumps({
        "records": [{"person": {"name": "Visible"}}],
        "_deleted": {"person": {"name": "ALICE SMITH"}},
        "_old": "prior-value",
        "nested": {"token": "should-not-print-secret"},
    }).encode("utf-8")


def _png_with_thumb_tail() -> bytes:
    main = _png((200, 10, 10), (48, 32))
    thumb = _png((10, 200, 10), (8, 8))
    # Append a second PNG after IEND (carve). Keep IEND of main intact.
    return main + thumb


def _eml_alt() -> bytes:
    msg = EmailMessage()
    msg["From"] = "clerk@example.test"
    msg["To"] = "desk@example.test"
    msg["Subject"] = "Docket"
    msg["Message-ID"] = "<docket-1@example.test>"
    msg.set_content("PLAIN ALICE SMITH remains in the text part.")
    msg.add_alternative("<html><body><p>HTML redacted</p></body></html>", subtype="html")
    msg.add_attachment(b"SECRET NOTES", maintype="text", subtype="plain", filename="notes.txt")
    return msg.as_bytes()


def _sqlite_deleted(tmp: Path) -> bytes:
    db = tmp / "tiny.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO people (name) VALUES ('ALICE SMITH')")
    conn.execute("INSERT INTO people (name) VALUES ('Visible')")
    for i in range(40):
        conn.execute("INSERT INTO people (name) VALUES (?)", ("PAD-" + ("X" * 200) + str(i),))
    conn.execute("DELETE FROM people WHERE name LIKE 'PAD-%'")
    conn.execute("DELETE FROM people WHERE name = 'ALICE SMITH'")
    conn.commit()
    conn.close()
    return db.read_bytes()


def _zip_nested() -> bytes:
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as zf:
        zf.writestr("draft/old_final2.txt", "PRIOR-DRAFT ALICE")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.txt", "current")
        zf.writestr("backup/old_copy.txt", "NESTED-FLAG")
        zf.writestr("archive/inner.zip", inner.getvalue())
    return buf.getvalue()


def _secret_env() -> bytes:
    return b"API_KEY=super-secret-value-do-not-print\nPASSWORD=also-secret\n"


def test_ops_and_matrix() -> None:
    card = list_recover()
    assert card["no_lie"] is True
    assert card["guessed_letters"] is False
    assert card["context_reconstruction"] is False
    for op in RECOVER_OPS:
        assert op in card["ops"]
    matrix = format_matrix()
    assert matrix["pdf"]["status"] == "live"
    assert matrix["7z"]["status"] == "slot"
    assert matrix["heic"]["status"] == "slot"
    assert parse_recover_op("deep") == "deep-recover"
    assert parse_recover_op("compare") == "cross-compare"


def test_detect_magic_not_extension() -> None:
    pdf = pdf_incremental_leftover()
    det = detect_bytes(pdf, filename="notes.docx")
    assert det["kind"] == "pdf"
    assert det["confirmed"] is True
    png = _png((1, 2, 3))
    det = detect_bytes(png, filename="file.pdf")
    assert det["kind"] == "png"


def test_pdf_incremental_via_recover() -> None:
    data = pdf_incremental_leftover()
    out = analyze_recover(data, op="revision-graph", filename="inc.pdf")
    assert out["no_lie"] is True
    assert out["type"] == "pdf"
    assert out["revision_graph"]["edges"]
    assert len(out["revision_graph"]["revisions"]) == 2
    copies = [r["copy"]["sha256"] for r in out["revision_graph"]["revisions"] if r.get("copy")]
    assert len(copies) == 2 and copies[0] != copies[1]
    deep = analyze_recover(data, op="deep-recover", filename="inc.pdf")
    blob = json.dumps(deep)
    assert "ALICE" in blob
    assert deep["guessed_letters"] is False


def test_docx_tracked_and_hidden() -> None:
    data = _docx_tracked()
    det = detect_bytes(data, filename="set.docx")
    assert det["kind"] == "docx"
    out = analyze_recover(data, op="deep-recover", filename="set.docx")
    blob = json.dumps(out)
    assert "ALICE SMITH" in blob
    assert "HIDDEN-VANISH" in blob or "hidden-text" in blob
    assert any(r.get("kind") == "tracked-deletion" for r in out["recovered"])
    assert any("Clerk" in (m.get("preview") or "") or "Production" in (m.get("preview") or "") for m in out["metadata"])


def test_json_tombstone_pointer() -> None:
    out = analyze_recover(_json_tombstone(), op="locate", filename="rec.json")
    pointers = [r.get("path") or r.get("json_pointer") for r in out["recovered"]]
    assert any("/_deleted" in str(p) or r.get("kind") == "json-tombstone" for r, p in zip(out["recovered"], pointers) for _ in [0])
    assert any(r.get("kind") == "json-tombstone" for r in out["recovered"])
    assert out["secret_material_present"] is True
    dumped = json.dumps(out)
    assert "super-secret" not in dumped
    assert "should-not-print-secret" not in dumped


def test_png_thumbnail_carve() -> None:
    data = _png_with_thumb_tail()
    out = analyze_recover(data, op="extract-embedded", filename="page.png")
    assert out["type"] == "png"
    blob = json.dumps(out)
    assert "after-iend" in blob or "carved-signature" in blob or out["carved"] or out["embedded"]
    # Second PNG signature after IEND must be cited, not invented pixels.
    assert any((c.get("offset") or 0) > 8 for c in (out.get("carved") or out.get("embedded") or []))


def test_eml_alternate_mime(tmp_path: Path) -> None:
    data = _eml_alt()
    out = analyze_recover(data, op="locate", filename="note.eml")
    blob = json.dumps(out)
    assert "ALICE SMITH" in blob
    assert any(r.get("kind") == "alternate-mime-diff" or "plain" in str(r.get("kind")) for r in out["recovered"] + out["redaction_regions"])
    assert any(e.get("kind") == "email-attachment" for e in out["embedded"] + out["recovered"])


def test_sqlite_freelist(tmp_path: Path) -> None:
    data = _sqlite_deleted(tmp_path)
    out = analyze_recover(data, op="scan-orphans", filename="tiny.sqlite")
    assert out["type"] == "sqlite"
    blob = json.dumps(out)
    assert "sqlite-freelist" in blob or "present_database_freelist" in blob
    # Live row still present
    locate = analyze_recover(data, op="locate", filename="tiny.sqlite")
    assert "Visible" in json.dumps(locate)


def test_zip_nested_flag_names() -> None:
    out = analyze_recover(_zip_nested(), op="locate", filename="bundle.zip")
    blob = json.dumps(out)
    assert "flag-name" in blob
    assert "backup/old_copy.txt" in blob
    assert any(e.get("path") == "archive/inner.zip" for e in out["embedded"] + out["recovered"])


def test_secret_suppressed() -> None:
    out = analyze_recover(_secret_env(), op="locate", filename=".env")
    assert out["secret_material_present"] is True
    dumped = json.dumps(out)
    assert "super-secret-value-do-not-print" not in dumped
    assert "also-secret" not in dumped
    assert any(s.get("value_suppressed") for s in out["secrets"])


def test_cross_compare_and_production(tmp_path: Path) -> None:
    old = tmp_path / "docket-0001.json"
    new = tmp_path / "docket-0002.json"
    old.write_bytes(_json_tombstone())
    new.write_text(json.dumps({"records": [{"person": {"name": "Visible"}}]}), encoding="utf-8")
    out = analyze_recover_path(old, op="compare", twin=new)
    assert out["cross_compare"] or out.get("revision_diff")
    assert "ALICE SMITH" in json.dumps(out.get("cross_compare") or {})
    prod = analyze_recover_path(old, op="locate", production_dir=tmp_path)
    assert prod["cross_file_matches"]


def test_cli_recover_json(tmp_path: Path, capsys) -> None:
    src = tmp_path / "rec.json"
    src.write_bytes(_json_tombstone())
    assert main(["recover", "locate", str(src), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["no_lie"] is True
    assert payload["family"] == "recover"
    assert payload["type"] == "json"


def test_heic_is_slot_not_fake_live() -> None:
    # ftyp + heic brand, no parser
    data = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic" + b"\x00" * 32
    det = detect_bytes(data, filename="pic.heic")
    assert det["kind"] == "heic"
    assert det["status"] == "slot"
    out = analyze_recover(data, op="locate", filename="pic.heic")
    assert out["format_status"] == "slot"
    assert out.get("refuse_code") == "SL-RECOVER-UNSUPPORTED" or any(
        r.get("code") == "SL-RECOVER-UNSUPPORTED" for r in out["refused"]
    )


def test_unredact_calls_into_recover() -> None:
    from spectrallock.unredact import analyze_unredact

    out = analyze_unredact(pdf_incremental_leftover(), op="locate", filename="inc.pdf")
    assert out.get("recover", {}).get("type") == "pdf"
    assert out["recover"]["revision_graph"]["edges"]
    assert out["recover"]["no_lie"] is True
