"""Format scanners. Present bytes and documented structure only."""

from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import mailbox
import os
import re
import sqlite3
import struct
import tarfile
import tempfile
import zipfile
import zlib
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

from spectrallock.recover.detect import (
    FORMAT_MATRIX,
    OLE_MAGIC,
    PNG_MAGIC,
    detect_bytes,
    sha256_hex,
)

MAX_NEST = 4
MAX_SCAN = 8_000_000
MAX_ENTRIES = 256
MAX_PREVIEW = 240
HOSTED_COPY_MAX = 24_000

TOMBSTONE_KEYS = (
    "_deleted", "_old", "_previous", "_history", "_backup", "_draft",
    "deleted", "previous", "tombstone", "isDeleted", "hidden",
)
FLAG_NAMES = re.compile(
    r"(?i)(backup|old|final2?|copy|draft|original|tmp|autosave|recovered|previous|archive)"
)
SECRET_KEY = re.compile(
    r"(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|\btoken\b|auth(orization)?|"
    r"cookie|private[_-]?key|aws_secret|bearer|session[_-]?id)"
)
SECRET_VALUE = re.compile(
    r"(?i)((?:password|passwd|secret|api[_-]?key|access[_-]?token|\btoken\b|"
    r"authorization|cookie|private[_-]?key|aws_secret|bearer|session[_-]?id)"
    r"[^\s:=]*)\s*[:=]\s*\S+"
)
PEM_PRIVATE = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")
HIDDEN_CSS = re.compile(
    r"(?i)(display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\.0+)?\b)"
)
NS_STRIP = re.compile(r"\{[^}]+\}")


def _preview(text: str, limit: int = MAX_PREVIEW) -> str:
    cleaned = "".join(ch if 32 <= ord(ch) < 127 or ch in "\n\t" else " " for ch in text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
    return cleaned[:limit] + ("…" if len(cleaned) > limit else "")


def _decode_bytes(data: bytes) -> tuple[str, str]:
    if data.startswith(b"\xff\xfe"):
        return data.decode("utf-16-le", errors="replace"), "utf-16-le"
    if data.startswith(b"\xfe\xff"):
        return data.decode("utf-16-be", errors="replace"), "utf-16-be"
    if data.startswith(b"\xff\xfe\x00\x00"):
        return data.decode("utf-32-le", errors="replace"), "utf-32-le"
    if data.startswith(b"\x00\x00\xfe\xff"):
        return data.decode("utf-32-be", errors="replace"), "utf-32-be"
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", errors="replace"), "utf-8-bom"
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        return data.decode("utf-8", errors="strict"), "utf-8"
    except UnicodeDecodeError:
        pass
    text = data.decode("latin-1", errors="replace")
    return text, "latin-1"


def suppress_secret_text(text: str) -> str:
    text = SECRET_VALUE.sub(lambda m: m.group(1) + "=<suppressed>", text)
    text = re.sub(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
                  "[private-key-suppressed]", text)
    return text


def secret_hit(text: str | bytes, *, path: str, offset: int = 0) -> dict[str, Any] | None:
    raw = text if isinstance(text, bytes) else text.encode("utf-8", errors="replace")
    if PEM_PRIVATE.search(raw):
        return {
            "secret_material_present": True,
            "kind": "private-key-pem",
            "path": path,
            "offset": offset,
            "value_suppressed": True,
            "invented": False,
        }
    sample = text if isinstance(text, str) else text.decode("latin-1", errors="replace")
    for match in SECRET_KEY.finditer(sample):
        window = sample[match.start() : match.start() + 80]
        if re.search(r"[:=]\s*\S", window) or "bearer " in window.lower():
            return {
                "secret_material_present": True,
                "kind": "credential-key",
                "path": path,
                "offset": offset + match.start(),
                "value_suppressed": True,
                "invented": False,
            }
    return None


def ledger(
    *,
    file_sha256: str,
    container: str,
    path: str,
    artifact_id: str,
    method: str,
    raw: bytes | None = None,
    offset: int | None = None,
    encoding: str | None = None,
    parent: str | None = None,
    state: str = "present_current",
    revision_id: str | None = None,
    object_id: str | None = None,
    confidence: float = 1.00,
) -> dict[str, Any]:
    return {
        "file_sha256": file_sha256,
        "container_type": container,
        "file_path": path,
        "artifact_id": artifact_id,
        "revision_id": revision_id,
        "object_id": object_id,
        "byte_offset": offset,
        "decoded_offset": None,
        "source_encoding": encoding,
        "parent_object": parent,
        "recovery_method": method,
        "recovered_bytes_sha256": sha256_hex(raw) if raw is not None else None,
        "state": state,
        "confidence": confidence,
        "human_verification_required": True,
        "invented": False,
    }


def _item(
    *,
    kind: str,
    preview: str,
    path: str,
    offset: int | None = None,
    state: str = "present_current",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rec = {
        "kind": kind,
        "preview": _preview(suppress_secret_text(preview)) if preview else "",
        "path": path,
        "offset": offset,
        "state": state,
        "invented": False,
    }
    if extra:
        rec.update(extra)
    return rec


# ---------------------------------------------------------------------------
# Raw-byte carving (supplied bytes only)
# ---------------------------------------------------------------------------

_SIGS = (
    (b"%PDF", "pdf"),
    (PNG_MAGIC, "png"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"PK\x03\x04", "zip"),
    (b"<?xml", "xml"),
    (b"SQLite format 3\x00", "sqlite"),
    (OLE_MAGIC, "ole"),
)


def carve_signatures(data: bytes, *, container: str, limit: int = 16) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for magic, kind in _SIGS:
        start = 1 if data.startswith(magic) else 0
        pos = start
        while len(hits) < limit:
            at = data.find(magic, pos)
            if at < 0:
                break
            hits.append(_item(
                kind="carved-signature",
                preview=f"{kind} at {at}",
                path=f"carve:{kind}",
                offset=at,
                state="present_orphan",
                extra={"carved_type": kind},
            ))
            pos = at + 1
    return hits


# ---------------------------------------------------------------------------
# JSON / structured
# ---------------------------------------------------------------------------

def _walk_json(value: Any, pointer: str, hits: list[dict[str, Any]], secrets: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_ptr = pointer + "/" + str(key).replace("~", "~0").replace("/", "~1")
            low = str(key)
            if any(tok in low for tok in TOMBSTONE_KEYS):
                hits.append(_item(
                    kind="json-tombstone",
                    preview=f"{child_ptr}={child!r}"[:240],
                    path=child_ptr,
                    state="present_prior_revision",
                    extra={"json_pointer": child_ptr, "key": key},
                ))
            if SECRET_KEY.search(str(key)):
                hit = secret_hit(f"{key}=x", path=child_ptr)
                if hit:
                    secrets.append(hit)
            if isinstance(child, str) and len(child) >= 16:
                if re.fullmatch(r"[A-Za-z0-9+/=\s]+", child) and len(child) % 4 == 0:
                    try:
                        raw = base64.b64decode(child, validate=True)
                        if raw and (raw[:1] in (b"{", b"<", b"%") or raw[:2] == b"PK"):
                            hits.append(_item(
                                kind="json-base64",
                                preview=_preview(raw[:80].decode("latin-1", errors="replace")),
                                path=child_ptr,
                                state="present_embedded",
                                extra={"json_pointer": child_ptr},
                            ))
                    except Exception:
                        pass
            _walk_json(child, child_ptr, hits, secrets)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _walk_json(child, f"{pointer}/{i}", hits, secrets)


def scan_json(data: bytes, *, filename: str, file_sha: str) -> dict[str, Any]:
    text, enc = _decode_bytes(data)
    duplicates: list[str] = []

    def hook(pairs: list[tuple[Any, Any]]) -> dict[str, Any]:
        seen: set[str] = set()
        out: dict[str, Any] = {}
        for key, val in pairs:
            if key in seen and key not in duplicates:
                duplicates.append(str(key))
            seen.add(key)
            out[key] = val
        return out

    parsed = None
    corrupt = False
    try:
        parsed = json.loads(text, object_pairs_hook=hook)
    except json.JSONDecodeError:
        corrupt = True
    hits: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    if parsed is not None:
        _walk_json(parsed, "", hits, secrets)
        for key in duplicates:
            hits.append(_item(kind="json-duplicate-key", preview=key, path=f"/{key}", extra={"key": key}))
    else:
        for tok in TOMBSTONE_KEYS:
            if tok in text:
                hits.append(_item(kind="json-tombstone-text", preview=tok, path=filename, state="present_prior_revision"))
    sec = secret_hit(text, path=filename)
    if sec:
        secrets.append(sec)
    return {
        "parsed": not corrupt,
        "encoding": enc,
        "hits": hits,
        "secrets": secrets,
        "corrupt": corrupt,
        "duplicates": duplicates,
    }


def scan_jsonl(data: bytes, *, filename: str, file_sha: str) -> dict[str, Any]:
    text, enc = _decode_bytes(data)
    hits: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    for i, line in enumerate(text.splitlines()[:MAX_ENTRIES]):
        if not line.strip():
            continue
        part = scan_json(line.encode("utf-8"), filename=f"{filename}:{i}", file_sha=file_sha)
        for h in part["hits"]:
            h["path"] = f"{filename}#{i}{h.get('path') or ''}"
            hits.append(h)
        secrets.extend(part["secrets"])
    return {"encoding": enc, "hits": hits, "secrets": secrets, "parsed": True, "corrupt": False}


# ---------------------------------------------------------------------------
# XML / HTML / SVG
# ---------------------------------------------------------------------------

def _local(tag: str) -> str:
    return NS_STRIP.sub("", tag)


def scan_markup(data: bytes, *, filename: str, kind: str) -> dict[str, Any]:
    text, enc = _decode_bytes(data)
    hits: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    for m in re.finditer(r"<!--(.*?)-->", text, flags=re.S):
        hits.append(_item(kind="markup-comment", preview=m.group(1), path=filename, offset=m.start(), state="present_orphan"))
    for m in HIDDEN_CSS.finditer(text):
        hits.append(_item(kind="hidden-css", preview=m.group(0), path=filename, offset=m.start(), state="present_current"))
    for attr in ("hidden", "aria-hidden", "data-hidden"):
        for m in re.finditer(rf"(?i)\b{attr}\s*=\s*['\"][^'\"]*['\"]|\b{attr}\b", text):
            hits.append(_item(kind="hidden-attr", preview=m.group(0), path=filename, offset=m.start()))
    for m in re.finditer(r"(?is)<script[^>]*>(.*?)</script>", text):
        body = m.group(1)
        if body.strip().startswith("{") or "application/ld+json" in text[max(0, m.start() - 80) : m.start()]:
            hits.append(_item(kind="json-script", preview=body, path=filename, offset=m.start(), state="present_embedded"))
        sec = secret_hit(body, path=filename, offset=m.start())
        if sec:
            secrets.append(sec)
    for m in re.finditer(r"(?i)data:[^;]+;base64,([A-Za-z0-9+/=]+)", text):
        hits.append(_item(kind="inline-base64", preview="data-uri", path=filename, offset=m.start(), state="present_embedded"))
    for m in re.finditer(r'(?is)<(title|alt|textarea|input)[^>]*>(.*?)</\1>|(?:alt|title|aria-label|value)="([^"]+)"', text):
        val = next((g for g in m.groups() if g), "")
        if val and not HIDDEN_CSS.search(val):
            hits.append(_item(kind="a11y-or-form", preview=val, path=filename, offset=m.start()))
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        root = None
    if root is not None:
        def walk(el: ET.Element, path: str) -> None:
            name = _local(el.tag)
            here = path + "/" + name
            if (el.attrib.get("display") == "none") or el.attrib.get("visibility") == "hidden":
                hits.append(_item(kind="hidden-element", preview=here, path=here, state="present_current"))
            if el.text and el.text.strip():
                hits.append(_item(kind="xml-text", preview=el.text, path=here))
            for child in list(el):
                walk(child, here)
        walk(root, "")
    sec = secret_hit(text, path=filename)
    if sec:
        secrets.append(sec)
    return {"encoding": enc, "hits": hits, "secrets": secrets, "kind": kind}


def scan_yaml_text(data: bytes, *, filename: str) -> dict[str, Any]:
    text, enc = _decode_bytes(data)
    hits: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    for i, line in enumerate(text.splitlines()):
        if line.lstrip().startswith("#"):
            hits.append(_item(kind="yaml-comment", preview=line, path=f"{filename}:{i}", state="present_orphan"))
        for tok in TOMBSTONE_KEYS:
            if tok in line:
                hits.append(_item(kind="yaml-tombstone", preview=line, path=f"{filename}:{i}", state="present_prior_revision"))
        sec = secret_hit(line, path=f"{filename}:{i}")
        if sec:
            secrets.append(sec)
    return {"encoding": enc, "hits": hits, "secrets": secrets, "ast": False, "note": "live-scan only; PyYAML AST is SLOT"}


def scan_rtf(data: bytes, *, filename: str) -> dict[str, Any]:
    text, enc = _decode_bytes(data)
    hits: list[dict[str, Any]] = []
    for m in re.finditer(r"\\v\s+(.+?)(?:\\v0|})", text, flags=re.S):
        hits.append(_item(kind="rtf-hidden", preview=m.group(1), path=filename, offset=m.start(), state="present_current"))
    literals = re.findall(r"(?:^|[{}\s])([A-Za-z][A-Za-z0-9 .:_-]{3,})", text)
    for lit in literals[:40]:
        if lit.lower() not in {"rtf", "ansi", "fonttbl", "colortbl"}:
            hits.append(_item(kind="rtf-text", preview=lit, path=filename))
    return {"encoding": enc, "hits": hits, "secrets": []}


def scan_text(data: bytes, *, filename: str, kind: str) -> dict[str, Any]:
    text, enc = _decode_bytes(data)
    hits = [_item(kind="text", preview=text[:400], path=filename)]
    secrets = []
    sec = secret_hit(text, path=filename)
    if sec:
        secrets.append(sec)
    if "<<<<<<<" in text or ">>>>>>> " in text:
        hits.append(_item(kind="conflict-marker", preview="git-conflict", path=filename, state="present_prior_revision"))
    for i, line in enumerate(text.splitlines()):
        if line.lstrip().startswith("#") or line.lstrip().startswith("//"):
            hits.append(_item(kind="commented-value", preview=line, path=f"{filename}:{i}", state="present_orphan"))
            if len(hits) > 80:
                break
    return {"encoding": enc, "hits": hits, "secrets": secrets, "kind": kind}


# ---------------------------------------------------------------------------
# OOXML / ODF / EPUB (ZIP parts)
# ---------------------------------------------------------------------------

OOXML_HIDE_RE = re.compile(
    r"(?is)<w:del\b.*?</w:del>|<w:vanish/?>|<w:color w:val=\"(?:FFFFFF|ffffff)\"|"
    r"<w:highlight w:val=\"[^\"]+\"|hidden=\"1\"|visibility=\"hidden\"|"
    r"state=\"(?:hidden|veryHidden)\""
)


def _xml_texts(blob: bytes) -> list[str]:
    texts: list[str] = []
    try:
        root = ET.fromstring(blob)
    except ET.ParseError:
        text, _ = _decode_bytes(blob)
        texts.extend(re.findall(r">([^<]{2,200})<", text))
        return texts

    def walk(el: ET.Element) -> None:
        if el.text and el.text.strip():
            texts.append(el.text.strip())
        for child in list(el):
            walk(child)
        if el.tail and el.tail.strip():
            texts.append(el.tail.strip())

    walk(root)
    return texts


def scan_zip_office(data: bytes, *, filename: str, kind: str) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    embeds: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return {"hits": [], "secrets": [], "embeds": [], "metadata": [], "corrupt": True}
    names = zf.namelist()[:MAX_ENTRIES]
    for name in names:
        raw = zf.read(name)
        if len(raw) > MAX_SCAN:
            raw = raw[:MAX_SCAN]
        low = name.lower()
        if FLAG_NAMES.search(name):
            hits.append(_item(kind="flag-name", preview=name, path=name, state="present_prior_revision"))
        if low.endswith((".xml", ".rels", ".html", ".xhtml", ".opf", ".svg")):
            texts = _xml_texts(raw)
            blob = raw.decode("utf-8", errors="replace")
            if OOXML_HIDE_RE.search(blob):
                hits.append(_item(kind="ooxml-hidden-or-deleted", preview=name, path=name, state="present_prior_revision"))
            if "w:del" in blob or "<w:del " in blob:
                for m in re.finditer(r"(?is)<w:del\b[^>]*>(.*?)</w:del>", blob):
                    inner = re.sub(r"<[^>]+>", "", m.group(1))
                    hits.append(_item(
                        kind="tracked-deletion",
                        preview=inner,
                        path=name,
                        offset=m.start(),
                        state="present_prior_revision",
                        extra={"part": name},
                    ))
            if "w:vanish" in blob:
                hits.append(_item(kind="hidden-text-attr", preview=name, path=name, state="present_current"))
            if "veryHidden" in blob or 'state="hidden"' in blob:
                hits.append(_item(kind="hidden-sheet-or-slide", preview=name, path=name, state="present_current"))
            if any(k in low for k in ("core.xml", "app.xml", "custom.xml", "meta.xml")):
                for t in texts:
                    metadata.append(_item(kind="office-prop", preview=t, path=name, state="present_metadata"))
            elif any(k in low for k in ("comment", "footnote", "endnote", "header", "footer", "notesSlide", "glossary")):
                for t in texts[:40]:
                    hits.append(_item(kind="office-ancillary", preview=t, path=name, state="present_embedded"))
            elif "sharedstrings" in low:
                for t in texts[:80]:
                    hits.append(_item(kind="shared-string", preview=t, path=name, state="present_current"))
            else:
                for t in texts[:40]:
                    hits.append(_item(kind="office-text", preview=t, path=name))
            sec = secret_hit(blob, path=name)
            if sec:
                secrets.append(sec)
        elif low.endswith((".png", ".jpg", ".jpeg", ".gif", ".emf", ".wmf", ".bin", ".xlsx", ".docx")):
            embeds.append(_item(
                kind="office-media",
                preview=name,
                path=name,
                state="present_embedded",
                extra={"byte_length": len(raw), "sha256": sha256_hex(raw)},
            ))
    zf.close()
    return {
        "hits": hits,
        "secrets": secrets,
        "embeds": embeds,
        "metadata": metadata,
        "parts": names,
        "corrupt": False,
    }


# ---------------------------------------------------------------------------
# OLE CFB
# ---------------------------------------------------------------------------

def _ole_short(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def _ole_int(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def scan_ole(data: bytes, *, filename: str, kind: str) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    streams: list[dict[str, Any]] = []
    if not data.startswith(OLE_MAGIC) or len(data) < 512:
        return {"hits": [], "secrets": [], "streams": [], "corrupt": True}
    shift = _ole_short(data, 0x1E)
    sector = 1 << shift if shift in {7, 8, 9, 12} else 512
    dir_first = _ole_int(data, 0x30)

    def sector_offset(index: int) -> int:
        return 512 + index * sector

    # Directory is an array of 128-byte entries starting at dir_first sector.
    visited = 0
    idx = dir_first
    names: list[str] = []
    while idx < 0xFFFFFFFE and visited < 256:
        off = sector_offset(idx)
        if off + sector > len(data):
            break
        chunk = data[off : off + sector]
        for e in range(0, len(chunk), 128):
            entry = chunk[e : e + 128]
            if len(entry) < 128:
                break
            name_len = _ole_short(entry, 64)
            if 2 <= name_len <= 64:
                raw_name = entry[0 : name_len - 2]
                try:
                    name = raw_name.decode("utf-16-le", errors="replace").strip("\x00")
                except Exception:
                    name = raw_name.decode("latin-1", errors="replace")
                typ = entry[66]
                start = _ole_int(entry, 116)
                size = _ole_int(entry, 120)
                if name:
                    names.append(name)
                    streams.append({
                        "name": name,
                        "type": typ,
                        "start_sector": start,
                        "size": size,
                        "invented": False,
                    })
                    if name in {"SummaryInformation", "\x05SummaryInformation", "DocumentSummaryInformation", "\x05DocumentSummaryInformation"}:
                        hits.append(_item(kind="ole-summary", preview=name, path=name, state="present_metadata"))
                    if "VBA" in name.upper() or name.endswith(".bas"):
                        hits.append(_item(kind="ole-vba", preview=name, path=name, state="present_embedded"))
        # Walk FAT naively: next sector index at FAT — for unused we still stop after a few.
        visited += 1
        idx = 0xFFFFFFFE
    # Extract printable leftovers from unused tail / slack-ish bytes after last used sector.
    text, _ = _decode_bytes(data)
    for m in re.finditer(r"[ -~]{8,80}", text):
        if m.start() > 512:
            hits.append(_item(kind="ole-printable", preview=m.group(0), path=filename, offset=m.start(), state="present_orphan"))
            if len(hits) > 40:
                break
    sec = secret_hit(data, path=filename)
    if sec:
        secrets.append(sec)
    return {
        "hits": hits,
        "secrets": secrets,
        "streams": streams,
        "directory": names,
        "corrupt": False,
        "kind": kind,
    }


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------

def _png_chunks(data: bytes) -> list[tuple[str, int, bytes]]:
    out: list[tuple[str, int, bytes]] = []
    if not data.startswith(PNG_MAGIC):
        return out
    pos = 8
    while pos + 12 <= len(data) and len(out) < 80:
        length = struct.unpack_from(">I", data, pos)[0]
        ctype = data[pos + 4 : pos + 8].decode("latin-1", errors="replace")
        start = pos + 8
        payload = data[start : start + length]
        out.append((ctype, pos, payload))
        pos = start + length + 4
        if ctype == "IEND":
            break
    return out


def scan_image(data: bytes, *, filename: str, kind: str) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    thumbs: list[dict[str, Any]] = []
    if kind == "png":
        for ctype, off, payload in _png_chunks(data):
            if ctype in {"tEXt", "iTXt", "zTXt"}:
                if ctype == "zTXt":
                    nul = payload.find(b"\x00")
                    label = payload[:nul].decode("latin-1", errors="replace") if nul >= 0 else "zTXt"
                    rest = payload[nul + 2 :] if nul >= 0 else payload
                    try:
                        text = zlib.decompress(rest).decode("latin-1", errors="replace")
                    except Exception:
                        text = rest.decode("latin-1", errors="replace")
                else:
                    parts = payload.split(b"\x00", 1)
                    label = parts[0].decode("latin-1", errors="replace")
                    text = parts[1].decode("utf-8", errors="replace") if len(parts) > 1 else ""
                metadata.append(_item(kind=f"png-{ctype}", preview=f"{label}={text}", path=filename, offset=off, state="present_metadata"))
            elif ctype in {"eXIf", "iCCP", "tIME", "pHYs"}:
                metadata.append(_item(kind=f"png-{ctype}", preview=ctype, path=filename, offset=off, state="present_metadata"))
        iend = data.find(b"IEND")
        if iend >= 0 and iend + 8 < len(data):
            tail = data[iend + 8 :]
            if tail.strip():
                hits.append(_item(kind="after-iend", preview=_preview(tail[:80].decode("latin-1", errors="replace")), path=filename, offset=iend + 8, state="present_orphan"))
                for carved in carve_signatures(tail, container="png"):
                    carved["offset"] = (iend + 8) + (carved.get("offset") or 0)
                    thumbs.append(carved)
    try:
        from PIL import Image, ImageSequence
        from PIL.ExifTags import TAGS

        img = Image.open(io.BytesIO(data))
        hits.append(_item(
            kind="image-dims",
            preview=f"{img.size[0]}x{img.size[1]} {img.format}",
            path=filename,
            extra={"width": img.size[0], "height": img.size[1], "format": img.format, "mode": img.mode},
        ))
        exif = getattr(img, "getexif", lambda: None)()
        if exif:
            for tag, val in exif.items():
                name = TAGS.get(tag, str(tag))
                if name == "JPEGInterchangeFormat" or "Thumbnail" in str(name):
                    thumbs.append(_item(kind="exif-thumbnail-offset", preview=str(name), path=filename, state="present_thumbnail"))
                metadata.append(_item(kind="exif", preview=f"{name}={val}", path=filename, state="present_metadata"))
        n_frames = getattr(img, "n_frames", 1)
        if n_frames and n_frames > 1:
            hits.append(_item(kind="extra-frames", preview=str(n_frames), path=filename, state="present_embedded"))
            for i, frame in enumerate(ImageSequence.Iterator(img)):
                if i == 0:
                    continue
                thumbs.append(_item(
                    kind="extra-page",
                    preview=f"frame {i} {frame.size}",
                    path=filename,
                    state="present_thumbnail",
                    extra={"width": frame.size[0], "height": frame.size[1], "index": i},
                ))
                if i > 8:
                    break
        info = getattr(img, "info", {}) or {}
        for key, val in info.items():
            metadata.append(_item(kind="pillow-info", preview=f"{key}={val}", path=filename, state="present_metadata"))
            if key.lower() in {"exif", "xmp", "icc_profile", "comment"}:
                hits.append(_item(kind="image-ancillary", preview=str(key), path=filename, state="present_metadata"))
    except Exception:
        hits.append(_item(kind="image-undecoded", preview=kind, path=filename))
    if kind == "jpeg":
        pos = 2
        while pos + 4 < len(data) and pos < 200_000:
            if data[pos] != 0xFF:
                break
            marker = data[pos + 1]
            if marker in {0xD8, 0xD9}:
                pos += 2
                continue
            if marker == 0xDA:
                break
            seglen = struct.unpack_from(">H", data, pos + 2)[0]
            payload = data[pos + 4 : pos + 2 + seglen]
            if marker == 0xFE:
                metadata.append(_item(kind="jpeg-com", preview=payload.decode("latin-1", errors="replace"), path=filename, offset=pos, state="present_metadata"))
            elif 0xE0 <= marker <= 0xEF:
                metadata.append(_item(kind="jpeg-app", preview=f"APP{marker - 0xE0}", path=filename, offset=pos, state="present_metadata"))
            pos += 2 + seglen
    sec = secret_hit(data, path=filename)
    if sec:
        secrets.append(sec)
    return {"hits": hits, "metadata": metadata, "secrets": secrets, "thumbs": thumbs}


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def scan_email(data: bytes, *, filename: str, kind: str) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    embeds: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    bodies: list[dict[str, Any]] = []

    def handle_msg(msg: Any, prefix: str) -> None:
        for key in ("from", "to", "cc", "subject", "message-id", "references", "in-reply-to", "date"):
            val = msg.get(key)
            if val:
                metadata.append(_item(kind="email-header", preview=f"{key}: {val}", path=prefix, state="present_metadata"))
        if msg.is_multipart():
            for i, part in enumerate(msg.walk()):
                ctype = part.get_content_type()
                disp = str(part.get_content_disposition() or "")
                fname = part.get_filename()
                payload = part.get_payload(decode=True)
                if part is msg:
                    continue
                if payload is None:
                    continue
                if fname or disp == "attachment":
                    embeds.append(_item(
                        kind="email-attachment",
                        preview=fname or ctype,
                        path=f"{prefix}/part{i}",
                        state="present_attachment",
                        extra={"media_type": ctype, "sha256": sha256_hex(payload), "byte_length": len(payload)},
                    ))
                elif ctype in {"text/plain", "text/html"}:
                    text, enc = _decode_bytes(payload)
                    bodies.append(_item(
                        kind="email-body",
                        preview=text,
                        path=f"{prefix}/{ctype}",
                        state="present_current",
                        extra={"media_type": ctype, "encoding": enc},
                    ))
                    sec = secret_hit(text, path=f"{prefix}/{ctype}")
                    if sec:
                        secrets.append(sec)
        else:
            payload = msg.get_payload(decode=True) or b""
            text, enc = _decode_bytes(payload)
            bodies.append(_item(kind="email-body", preview=text, path=prefix, extra={"encoding": enc}))

    if kind == "mbox":
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        try:
            box = mailbox.mbox(tmp_path)
            for i, msg in enumerate(box):
                handle_msg(msg, f"{filename}#{i}")
                if i >= 32:
                    break
        finally:
            os.unlink(tmp_path)
    else:
        msg = BytesParser(policy=policy.default).parsebytes(data)
        handle_msg(msg, filename)
    plains = [b["preview"] for b in bodies if (b.get("extra") or {}).get("media_type") == "text/plain" or b["path"].endswith("text/plain")]
    htmls = [b["preview"] for b in bodies if "html" in (b.get("path") or "")]
    if plains and htmls and plains[0] != htmls[0]:
        hits.append(_item(
            kind="alternate-mime-diff",
            preview="plain≠html",
            path=filename,
            state="present_current",
            extra={"plain": _preview(plains[0]), "html": _preview(htmls[0])},
        ))
    hits.extend(bodies)
    return {"hits": hits, "metadata": metadata, "embeds": embeds, "secrets": secrets}


# ---------------------------------------------------------------------------
# SQLite (user-supplied bytes only)
# ---------------------------------------------------------------------------

def scan_sqlite(data: bytes, *, filename: str) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    if not data.startswith(b"SQLite format 3\x00"):
        return {"hits": [], "corrupt": True, "secrets": [], "metadata": []}
    page_size = struct.unpack_from(">H", data, 16)[0]
    if page_size == 1:
        page_size = 65536
    freelist = struct.unpack_from(">I", data, 32)[0]
    metadata.append(_item(kind="sqlite-header", preview=f"page_size={page_size} freelist={freelist}", path=filename, state="present_metadata"))
    if freelist:
        hits.append(_item(
            kind="sqlite-freelist",
            preview=f"trunk_page={freelist}",
            path=filename,
            state="present_database_freelist",
            extra={"page": freelist, "page_size": page_size},
        ))
        trunk_off = (freelist - 1) * page_size
        if 0 <= trunk_off < len(data):
            hits.append(_item(
                kind="sqlite-freelist-bytes",
                preview=_preview(data[trunk_off : trunk_off + 80].decode("latin-1", errors="replace")),
                path=filename,
                offset=trunk_off,
                state="present_database_freelist",
            ))
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    try:
        tmp.write(data)
        tmp.close()
        conn = sqlite3.connect(f"file:{tmp.name}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        tables = list(cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'"))
        for row in tables:
            metadata.append(_item(kind="sqlite-schema", preview=f"{row[0]} {row[1] or ''}", path=row[0], state="present_metadata"))
            try:
                rows = list(cur.execute(f'SELECT * FROM "{row[0]}" LIMIT 32'))
            except sqlite3.Error:
                continue
            cols = [d[0] for d in cur.description] if cur.description else []
            for rec in rows:
                mapping = {cols[i]: rec[i] for i in range(len(cols))}
                hits.append(_item(
                    kind="sqlite-row",
                    preview=_preview(json.dumps(mapping, default=str)),
                    path=row[0],
                    state="present_current",
                    extra={"table": row[0], "columns": cols},
                ))
                blob = json.dumps(mapping, default=str)
                sec = secret_hit(blob, path=row[0])
                if sec:
                    secrets.append(sec)
        conn.close()
    except sqlite3.Error as exc:
        hits.append(_item(kind="sqlite-error", preview=type(exc).__name__, path=filename))
    finally:
        os.unlink(tmp.name)
    return {"hits": hits, "metadata": metadata, "secrets": secrets, "corrupt": False}


# ---------------------------------------------------------------------------
# Archives
# ---------------------------------------------------------------------------

def scan_archive(data: bytes, *, filename: str, kind: str, depth: int = 0) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    embeds: list[dict[str, Any]] = []
    secrets: list[dict[str, Any]] = []
    if depth > MAX_NEST:
        return {"hits": [_item(kind="limit", preview="nest", path=filename)], "embeds": [], "secrets": [], "limit": True}
    if kind == "gz":
        try:
            inner = gzip.decompress(data)
        except OSError:
            return {"hits": [], "embeds": [], "secrets": [], "corrupt": True}
        inner_det = detect_bytes(inner, filename=filename.removesuffix(".gz"))
        embeds.append(_item(kind="gzip-member", preview=inner_det["kind"], path=filename, state="present_embedded", extra=inner_det))
        return {"hits": hits, "embeds": embeds, "secrets": secrets, "inner": inner, "inner_detect": inner_det}
    if kind == "tar":
        try:
            tf = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
        except tarfile.TarError:
            return {"hits": [], "corrupt": True, "embeds": [], "secrets": []}
        for member in tf.getmembers()[:MAX_ENTRIES]:
            info = _item(
                kind="tar-member",
                preview=member.name,
                path=member.name,
                state="present_embedded",
                extra={"mtime": member.mtime, "size": member.size, "sha256": None},
            )
            if FLAG_NAMES.search(member.name or ""):
                info["state"] = "present_prior_revision"
                hits.append(_item(kind="flag-name", preview=member.name, path=member.name, state="present_prior_revision"))
            embeds.append(info)
        return {"hits": hits, "embeds": embeds, "secrets": secrets}
    if kind == "7z":
        return {
            "hits": [_item(kind="slot", preview="7z parser unbound", path=filename)],
            "embeds": [],
            "secrets": [],
            "slot": True,
        }
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return {"hits": [], "corrupt": True, "embeds": [], "secrets": []}
    seen_names: dict[str, int] = {}
    for info in zf.infolist()[:MAX_ENTRIES]:
        seen_names[info.filename] = seen_names.get(info.filename, 0) + 1
        raw = zf.read(info.filename)
        rec = _item(
            kind="zip-member",
            preview=info.filename,
            path=info.filename,
            state="present_embedded",
            extra={
                "date_time": list(info.date_time),
                "byte_length": info.file_size,
                "sha256": sha256_hex(raw),
                "comment": info.comment.decode("latin-1", errors="replace") if info.comment else "",
            },
        )
        if FLAG_NAMES.search(info.filename):
            rec["state"] = "present_prior_revision"
            hits.append(_item(kind="flag-name", preview=info.filename, path=info.filename, state="present_prior_revision"))
        if info.filename.startswith(".") or "/." in info.filename:
            hits.append(_item(kind="dotfile", preview=info.filename, path=info.filename, state="present_orphan"))
        embeds.append(rec)
        sec = secret_hit(raw, path=info.filename)
        if sec:
            secrets.append(sec)
    for name, count in seen_names.items():
        if count > 1:
            hits.append(_item(kind="duplicate-name", preview=name, path=name, state="present_prior_revision"))
    return {"hits": hits, "embeds": embeds, "secrets": secrets, "parts": list(seen_names)}


# ---------------------------------------------------------------------------
# Git (supplied tree only)
# ---------------------------------------------------------------------------

def scan_git(root: Path) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    git_dir = root / ".git" if (root / ".git").exists() else root
    if not git_dir.exists():
        return {"hits": [], "slot": False, "present": False}
    head = git_dir / "HEAD"
    if head.is_file():
        hits.append(_item(kind="git-head", preview=head.read_text(encoding="utf-8", errors="replace"), path=str(head), state="present_current"))
    reflog = git_dir / "logs" / "HEAD"
    if reflog.is_file():
        hits.append(_item(kind="git-reflog", preview=reflog.read_text(encoding="utf-8", errors="replace")[:400], path=str(reflog), state="present_prior_revision"))
    objects = git_dir / "objects"
    if objects.is_dir():
        count = 0
        for p in objects.rglob("*"):
            if p.is_file() and not p.name.startswith("pack") and len(p.name) >= 2:
                count += 1
                if count <= 24:
                    hits.append(_item(kind="git-object", preview=p.name, path=str(p), state="present_prior_revision"))
        hits.append(_item(kind="git-object-count", preview=str(count), path=str(objects)))
    return {"hits": hits, "present": True}


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def scan_bytes(
    data: bytes,
    *,
    filename: str = "artifact",
    depth: int = 0,
    hosted: bool = False,
) -> dict[str, Any]:
    det = detect_bytes(data, filename=filename)
    kind = det["kind"]
    file_sha = det["sha256"]
    out: dict[str, Any] = {
        "detect": det,
        "hits": [],
        "metadata": [],
        "embeds": [],
        "secrets": [],
        "orphans": [],
        "thumbs": [],
        "carved": [],
        "directory": [],
        "parts": [],
        "revision_like": [],
    }
    if det["status"] == "slot":
        out["slot"] = True
        out["hits"].append(_item(kind="slot", preview=det["status_note"], path=filename))
        out["carved"] = carve_signatures(data, container=kind)
        return out

    if kind == "json":
        part = scan_json(data, filename=filename, file_sha=file_sha)
    elif kind == "jsonl" or kind == "ipynb":
        part = scan_json(data, filename=filename, file_sha=file_sha) if kind == "ipynb" else scan_jsonl(data, filename=filename, file_sha=file_sha)
    elif kind in {"xml", "html", "htm", "svg"}:
        part = scan_markup(data, filename=filename, kind=kind)
    elif kind in {"yaml", "yml"}:
        part = scan_yaml_text(data, filename=filename)
    elif kind == "rtf":
        part = scan_rtf(data, filename=filename)
    elif kind in {"txt", "csv", "tsv", "md", "source", "log"}:
        part = scan_text(data, filename=filename, kind=kind)
    elif kind in {"docx", "xlsx", "pptx", "odt", "ods", "odp", "epub"}:
        part = scan_zip_office(data, filename=filename, kind=kind)
    elif kind in {"doc", "xls", "ppt", "msg"}:
        part = scan_ole(data, filename=filename, kind=kind)
    elif kind in {"png", "jpeg", "jpg", "tiff", "tif", "gif", "bmp", "webp"}:
        part = scan_image(data, filename=filename, kind="jpeg" if kind == "jpg" else kind)
    elif kind in {"eml", "mbox"}:
        part = scan_email(data, filename=filename, kind=kind)
    elif kind in {"sqlite", "db"}:
        part = scan_sqlite(data, filename=filename)
    elif kind in {"zip", "tar", "gz", "7z"}:
        part = scan_archive(data, filename=filename, kind=kind, depth=depth)
        if kind == "gz" and part.get("inner") is not None and depth < MAX_NEST:
            inner = scan_bytes(part["inner"], filename=filename.removesuffix(".gz"), depth=depth + 1, hosted=hosted)
            part.setdefault("embeds", []).append(_item(kind="gzip-inner", preview=inner["detect"]["kind"], path=filename, state="present_embedded"))
            for key in ("hits", "metadata", "embeds", "secrets"):
                out[key].extend(inner.get(key) or [])
    else:
        part = scan_text(data, filename=filename, kind=kind) if det["confirmed"] else {"hits": [], "secrets": []}
        out["carved"] = carve_signatures(data, container=kind)

    for key in ("hits", "metadata", "embeds", "secrets", "thumbs"):
        out[key].extend(part.get(key) or [])
    if part.get("directory"):
        out["directory"] = part["directory"]
    if part.get("parts"):
        out["parts"] = part["parts"]
    if part.get("streams"):
        out["directory"] = part["streams"]
    if part.get("carved"):
        out["carved"].extend(part["carved"])
    out["carved"].extend(carve_signatures(data, container=kind)[:8])
    # de-dup carved that is just the file itself
    out["carved"] = [c for c in out["carved"] if (c.get("offset") or 0) > 0]
    for h in out["hits"]:
        if h.get("state") in {"present_orphan", "present_prior_revision", "present_database_freelist"}:
            out["orphans"].append(h)
            out["revision_like"].append(h)
    return out
