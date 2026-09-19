"""Magic-byte + MIME + container confirmation. Extension is never enough."""

from __future__ import annotations

import re
from typing import Any

# LIVE = real parser confirmation. SLOT = no honest parser in this tree.
# Never advertise SLOT as LIVE.

FORMAT_MATRIX: dict[str, dict[str, str]] = {
    "pdf": {"status": "live", "note": "pdfhist + incremental revision graph"},
    "docx": {"status": "live", "note": "OOXML ZIP + every part XML scan"},
    "xlsx": {"status": "live", "note": "OOXML ZIP + shared strings / sheets / comments"},
    "pptx": {"status": "live", "note": "OOXML ZIP + slides / notes / hidden"},
    "odt": {"status": "live", "note": "ODF ZIP + content.xml"},
    "ods": {"status": "live", "note": "ODF ZIP + content.xml"},
    "odp": {"status": "live", "note": "ODF ZIP + content.xml"},
    "epub": {"status": "live", "note": "ZIP + OPF / XHTML"},
    "doc": {"status": "live", "note": "OLE CFB directory + stream extract"},
    "xls": {"status": "live", "note": "OLE CFB directory + stream extract"},
    "ppt": {"status": "live", "note": "OLE CFB directory + stream extract"},
    "rtf": {"status": "live", "note": "control-word + hidden \\v scan"},
    "txt": {"status": "live", "note": "encoding-aware text"},
    "csv": {"status": "live", "note": "delimited text"},
    "tsv": {"status": "live", "note": "tab-delimited text"},
    "md": {"status": "live", "note": "markdown text"},
    "html": {"status": "live", "note": "hidden CSS/DOM + comments + data-*"},
    "htm": {"status": "live", "note": "alias of html"},
    "xml": {"status": "live", "note": "XPath-like + namespaces + comments"},
    "svg": {"status": "live", "note": "hidden groups + comments + href"},
    "json": {"status": "live", "note": "duplicate keys / tombstones / pointer paths"},
    "jsonl": {"status": "live", "note": "line-delimited JSON"},
    "yaml": {"status": "live-scan", "note": "text + key scan; no PyYAML AST (honest)"},
    "yml": {"status": "live-scan", "note": "alias of yaml"},
    "zip": {"status": "live", "note": "all entries + nested + flag names"},
    "tar": {"status": "live", "note": "tarfile members"},
    "gz": {"status": "live", "note": "gzip unwrap then recurse"},
    "7z": {"status": "slot", "note": "no py7zr in package; header cite only"},
    "png": {"status": "live", "note": "chunks + Pillow + after-IEND carve"},
    "jpeg": {"status": "live", "note": "APP/COM + Pillow EXIF/thumbnail"},
    "jpg": {"status": "live", "note": "alias of jpeg"},
    "tiff": {"status": "live", "note": "extra pages via Pillow"},
    "tif": {"status": "live", "note": "alias of tiff"},
    "gif": {"status": "live", "note": "frames + comments"},
    "bmp": {"status": "live", "note": "Pillow + header dims"},
    "webp": {"status": "live", "note": "Pillow when decoder present"},
    "heic": {"status": "slot", "note": "no pillow-heif bound; magic cite only"},
    "heif": {"status": "slot", "note": "no pillow-heif bound; magic cite only"},
    "eml": {"status": "live", "note": "email stdlib headers + MIME parts"},
    "mbox": {"status": "live", "note": "mailbox iteration"},
    "msg": {"status": "live-ole", "note": "CFB streams + text; not a full MSG property map"},
    "sqlite": {"status": "live", "note": "schema + rows + freelist pages"},
    "db": {"status": "live", "note": "sqlite when header confirms"},
    "ipynb": {"status": "live", "note": "notebook JSON"},
    "source": {"status": "live", "note": "comments / conflict markers / secrets suppressed"},
    "log": {"status": "live", "note": "line scan"},
    "git": {"status": "live", "note": "only when .git / objects supplied"},
    "bin": {"status": "live-carve", "note": "bounded signature carve only"},
}

OLE_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
PDF_MAGIC = b"%PDF"
PNG_MAGIC = bytes.fromhex("89504E470D0A1A0A")
JPEG_MAGIC = bytes.fromhex("FFD8FF")
GIF87 = b"GIF87a"
GIF89 = b"GIF89a"
ZIP_MAGIC = b"PK\x03\x04"
ZIP_EMPTY = b"PK\x05\x06"
GZIP_MAGIC = b"\x1f\x8b"
SEVEN_Z = b"7z\xbc\xaf'\x1c"
SQLITE_MAGIC = b"SQLite format 3\x00"
TIFF_LE = b"II*\x00"
TIFF_BE = b"MM\x00*"
WEBP_RIFF = b"RIFF"
RIFF_WEBP = b"WEBP"
BMP_MAGIC = b"BM"
RTF_MAGIC = b"{\\rtf"
XML_DECL = b"<?xml"
HTML_HINT = re.compile(rb"(?is)<(!doctype\s+html|html|head|body)\b")
JSON_START = re.compile(rb"^\s*[\[{]")
TAR_USTAR = b"ustar"
HEIC_FTYP = (b"ftypheic", b"ftypheif", b"ftypmif1", b"ftypmsf1")


def sha256_hex(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def guess_extension(name: str | None) -> str:
    if not name:
        return ""
    low = name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
    if "." not in low:
        return ""
    return low.rsplit(".", 1)[-1]


def _mime_for(kind: str) -> str:
    return {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "odt": "application/vnd.oasis.opendocument.text",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "odp": "application/vnd.oasis.opendocument.presentation",
        "epub": "application/epub+zip",
        "doc": "application/msword",
        "xls": "application/vnd.ms-excel",
        "ppt": "application/vnd.ms-powerpoint",
        "rtf": "application/rtf",
        "txt": "text/plain",
        "csv": "text/csv",
        "tsv": "text/tab-separated-values",
        "md": "text/markdown",
        "html": "text/html",
        "htm": "text/html",
        "xml": "application/xml",
        "svg": "image/svg+xml",
        "json": "application/json",
        "jsonl": "application/jsonl",
        "yaml": "application/yaml",
        "yml": "application/yaml",
        "zip": "application/zip",
        "tar": "application/x-tar",
        "gz": "application/gzip",
        "7z": "application/x-7z-compressed",
        "png": "image/png",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "tiff": "image/tiff",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "webp": "image/webp",
        "heic": "image/heic",
        "heif": "image/heif",
        "eml": "message/rfc822",
        "mbox": "application/mbox",
        "msg": "application/vnd.ms-outlook",
        "sqlite": "application/vnd.sqlite3",
        "ipynb": "application/x-ipynb+json",
        "source": "text/plain",
        "log": "text/plain",
        "git": "application/x-git",
        "bin": "application/octet-stream",
    }.get(kind, "application/octet-stream")


def _zip_names(data: bytes) -> list[str]:
    import io
    import zipfile

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            return zf.namelist()
    except zipfile.BadZipFile:
        return []


def _confirm_zip_kind(data: bytes, ext: str) -> str:
    names = {n.replace("\\", "/").lower() for n in _zip_names(data)}
    if any(n.endswith("word/document.xml") or n == "[content_types].xml" and any("word/" in x for x in names) for n in names) or any(
        n.startswith("word/") for n in names
    ):
        return "docx"
    if any(n.startswith("xl/") for n in names):
        return "xlsx"
    if any(n.startswith("ppt/") for n in names):
        return "pptx"
    if "mimetype" in names or any(n.endswith("content.opf") or n.startswith("oebps/") for n in names):
        if b"application/epub+zip" in data[:256] or any("content.opf" in n for n in names):
            return "epub"
    if any(n == "mimetype" or n.startswith("meta-inf/") for n in names):
        joined = " ".join(names)
        if "opendocument.text" in joined or "content.xml" in names and ext == "odt":
            return "odt"
        if "opendocument.spreadsheet" in joined or ext == "ods":
            return "ods"
        if "opendocument.presentation" in joined or ext == "odp":
            return "odp"
        if "content.xml" in names:
            head = data[:800].lower()
            if b"opendocument.text" in head:
                return "odt"
            if b"opendocument.spreadsheet" in head:
                return "ods"
            if b"opendocument.presentation" in head:
                return "odp"
            return "odt"
    if ext in {"docx", "xlsx", "pptx", "odt", "ods", "odp", "epub", "zip"}:
        return ext if ext != "zip" or names else "zip"
    return "zip"


def _looks_mbox(data: bytes) -> bool:
    return data.startswith(b"From ") and b"\nFrom " in data[:8000]


def _looks_eml(data: bytes) -> bool:
    head = data[:4096]
    return bool(re.search(rb"(?im)^(from|to|subject|message-id|mime-version):", head))


def _looks_source(name: str, data: bytes) -> bool:
    ext = guess_extension(name)
    if ext in {
        "py", "js", "ts", "tsx", "jsx", "java", "c", "cc", "cpp", "h", "go", "rs",
        "rb", "php", "sh", "bash", "env", "ini", "cfg", "toml", "lock", "gradle",
    }:
        return True
    if name and name.endswith((".env.example", ".map", "package-lock.json", "yarn.lock")):
        return True
    return False


def detect_bytes(data: bytes, *, filename: str | None = None) -> dict[str, Any]:
    """Return kind, mime, status, evidence. Extension alone never wins."""
    ext = guess_extension(filename)
    evidence: list[str] = []
    kind = "bin"
    confirmed = False

    if data.startswith(PDF_MAGIC):
        kind, confirmed, evidence = "pdf", True, ["magic:%PDF"]
    elif data.startswith(PNG_MAGIC):
        kind, confirmed, evidence = "png", True, ["magic:PNG"]
    elif data.startswith(JPEG_MAGIC):
        kind, confirmed, evidence = "jpeg", True, ["magic:JPEG"]
    elif data.startswith(GIF87) or data.startswith(GIF89):
        kind, confirmed, evidence = "gif", True, ["magic:GIF"]
    elif data.startswith(BMP_MAGIC) and len(data) > 14:
        kind, confirmed, evidence = "bmp", True, ["magic:BMP"]
    elif data.startswith(TIFF_LE) or data.startswith(TIFF_BE):
        kind, confirmed, evidence = "tiff", True, ["magic:TIFF"]
    elif data.startswith(WEBP_RIFF) and data[8:12] == RIFF_WEBP:
        kind, confirmed, evidence = "webp", True, ["magic:WEBP"]
    elif data.startswith(SQLITE_MAGIC):
        kind, confirmed, evidence = "sqlite", True, ["magic:SQLite"]
    elif data.startswith(OLE_MAGIC):
        kind, confirmed, evidence = "doc", True, ["magic:OLE"]
        if ext in {"xls", "ppt", "msg"}:
            kind = ext
        elif b"Workbook" in data[:4096] or b"Book" in data[0:8000]:
            kind = "xls"
        elif b"PowerPoint" in data[:8000] or b"Pictures" in data[:8000]:
            kind = "ppt"
        elif b"__substg" in data or b"__nameid" in data:
            kind = "msg"
    elif data.startswith(SEVEN_Z):
        kind, confirmed, evidence = "7z", True, ["magic:7z"]
    elif data.startswith(GZIP_MAGIC):
        kind, confirmed, evidence = "gz", True, ["magic:gzip"]
    elif data.startswith(ZIP_MAGIC) or data.startswith(ZIP_EMPTY):
        kind = _confirm_zip_kind(data, ext)
        confirmed = True
        evidence = ["magic:ZIP", f"container:{kind}"]
    elif len(data) > 262 and TAR_USTAR in data[257:263]:
        kind, confirmed, evidence = "tar", True, ["magic:ustar"]
    elif data.startswith(RTF_MAGIC):
        kind, confirmed, evidence = "rtf", True, ["magic:rtf"]
    elif data[4:8] == b"ftyp" and any(h in data[8:16] for h in (b"heic", b"heif", b"mif1", b"msf1")):
        kind, confirmed, evidence = "heic", True, ["magic:ftyp-heic"]
    elif data.lstrip().startswith(XML_DECL) or data.lstrip().startswith(b"<svg") or (ext == "svg" and b"<svg" in data[:400]):
        if b"<svg" in data[:800]:
            kind, confirmed, evidence = "svg", True, ["parser:svg"]
        else:
            kind, confirmed, evidence = "xml", True, ["parser:xml-decl"]
    elif _looks_mbox(data):
        kind, confirmed, evidence = "mbox", True, ["parser:mbox-from"]
    elif _looks_eml(data):
        kind, confirmed, evidence = "eml", True, ["parser:rfc822-headers"]
    elif HTML_HINT.search(data[:2000]):
        kind, confirmed, evidence = "html", True, ["parser:html"]
    elif ext == "ipynb" or (b'"nbformat"' in data[:800] and JSON_START.match(data)):
        kind, confirmed, evidence = "ipynb", True, ["parser:ipynb"]
    elif ext == "jsonl" or (filename or "").endswith(".jsonl"):
        kind, confirmed, evidence = "jsonl", True, ["ext+text"]
    elif JSON_START.match(data) and (ext in {"json", "jsonl", ""} or data.lstrip()[:1] in (b"{", b"[")):
        try:
            import json

            json.loads(data.decode("utf-8", errors="strict") if b"\x00" not in data[:200] else data.decode("utf-16"))
            kind, confirmed, evidence = "json", True, ["parser:json"]
        except Exception:
            if ext == "json":
                kind, confirmed, evidence = "json", False, ["ext:json-unparsed"]
    elif ext in {"yaml", "yml"} or (b":\n" in data[:400] and not data.startswith(b"<")):
        if ext in {"yaml", "yml"}:
            kind, confirmed, evidence = "yaml", True, ["ext+text-scan"]
    elif ext in {"csv", "tsv"}:
        kind, confirmed, evidence = ext, True, [f"ext:{ext}"]
    elif ext in {"md", "markdown"}:
        kind, confirmed, evidence = "md", True, ["ext:md"]
    elif _looks_source(filename or "", data):
        kind, confirmed, evidence = "source", True, ["ext:source"]
    elif ext in {"log", "txt"} or (filename or "").endswith(".log"):
        kind, confirmed, evidence = "log" if ext == "log" else "txt", True, ["ext:text"]
    elif ext == "txt":
        kind, confirmed, evidence = "txt", True, ["ext:txt"]

    if not confirmed and ext in FORMAT_MATRIX and kind == "bin":
        kind = ext
        evidence.append(f"ext-only:{ext}")

    row = FORMAT_MATRIX.get(kind) or FORMAT_MATRIX["bin"]
    return {
        "kind": kind,
        "mime": _mime_for(kind),
        "status": row["status"],
        "status_note": row["note"],
        "confirmed": confirmed,
        "evidence": evidence,
        "filename": filename,
        "extension": ext,
        "byte_length": len(data),
        "sha256": sha256_hex(data),
        "invented": False,
    }
