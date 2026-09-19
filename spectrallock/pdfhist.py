"""Deep historical PDF revision recovery for SpectralLock unredact.

Operator lock 2026-09-19. Fourteen capabilities on the existing
locate / lift / recover / refuse family. NO-LIE:

- Leftover / historical bytes = recover.
- Opaque sanitized rewrite with nothing left = SL-UNREDACT-OPAQUE.
- Never invent letters.
- Heatmap ≠ transcript.
- OCR only AFTER structural recovery, and never reconstructs covered
  letters from context alone.

Author: Aziel Eliab. Lamb Lens: Service → Clarity → Peace.
No FragGate invent. No forensic certification claims.
"""

from __future__ import annotations

import hashlib
import io
import re
import shutil
import zlib
from typing import Any

DEEP_CAPABILITIES = (
    "historical_page_dereference",
    "revision_stream_compare",
    "operator_text_recovery",
    "font_encoding_resolve",
    "drawing_order_overlay",
    "redaction_classification",
    "orphan_object_scan",
    "xref_objstm",
    "after_eof_scan",
    "image_layer_recovery",
    "twin_page_compare",
    "producer_artifact_search",
    "ocr_after_structural",
    "character_provenance",
)

CLASS_TEXT_UNDER_VECTOR = "text_under_vector_overlay"
CLASS_TEXT_TO_OUTLINES = "text_converted_to_outlines"
CLASS_TEXT_RASTERIZED = "text_rasterized_into_image"
CLASS_OLD_REVISION = "old_revision_survives"
CLASS_DELETED_BYTES = "object_deleted_bytes_remain"
CLASS_SANITIZED = "sanitized_rewrite"

PAGE_FOLLOW_KEYS = (
    "Contents",
    "Resources",
    "XObject",
    "Font",
    "ToUnicode",
    "Annots",
    "Metadata",
    "PieceInfo",
    "StructParents",
    "AcroForm",
    "EmbeddedFiles",
    "EF",
    "F",
    "UF",
    "Thumb",
    "Alternates",
    "SMask",
    "Mask",
)

_OBJ_RE = re.compile(rb"(?m)(?<![0-9])(\d+)\s+(\d+)\s+obj\b")
_EOF_RE = re.compile(rb"%%EOF")
_STARTXREF_RE = re.compile(rb"startxref\s+(\d+)")
_REF_RE = re.compile(rb"(\d+)\s+(\d+)\s+R")
_NAME_RE = re.compile(rb"/([A-Za-z*][A-Za-z0-9*._-]*)")

# Common PDF glyph names → Unicode. Unknown names stay codes, never guesses.
_GLYPH_NAMES: dict[str, str] = {
    "space": " ",
    "exclam": "!",
    "quotedbl": "\"",
    "numbersign": "#",
    "dollar": "$",
    "percent": "%",
    "ampersand": "&",
    "quotesingle": "'",
    "parenleft": "(",
    "parenright": ")",
    "asterisk": "*",
    "plus": "+",
    "comma": ",",
    "hyphen": "-",
    "period": ".",
    "slash": "/",
    "colon": ":",
    "semicolon": ";",
    "less": "<",
    "equal": "=",
    "greater": ">",
    "question": "?",
    "at": "@",
    "bracketleft": "[",
    "backslash": "\\",
    "bracketright": "]",
    "asciicircum": "^",
    "underscore": "_",
    "grave": "`",
    "braceleft": "{",
    "bar": "|",
    "braceright": "}",
    "asciitilde": "~",
    "quoteleft": "‘",
    "quoteright": "’",
    "quotedblleft": "“",
    "quotedblright": "”",
    "endash": "–",
    "emdash": "—",
    "bullet": "•",
    "ellipsis": "…",
    "copyright": "©",
    "registered": "®",
    "trademark": "™",
    "AE": "Æ",
    "OE": "Œ",
    "ae": "æ",
    "oe": "œ",
    "ss": "ß",
    "fi": "fi",
    "fl": "fl",
}
for _ch in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
    _GLYPH_NAMES[_ch] = _ch
for _i in range(10):
    _GLYPH_NAMES[f"zero" if _i == 0 else ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")[_i - 1]] = str(_i)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _inflate(data: bytes) -> bytes | None:
    for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS, zlib.MAX_WBITS | 16):
        try:
            return zlib.decompress(data, wbits)
        except zlib.error:
            continue
    return None


def unescape_pdf_literal(raw: bytes) -> bytes:
    inner = raw[1:-1] if raw.startswith(b"(") and raw.endswith(b")") else raw
    out = bytearray()
    i = 0
    while i < len(inner):
        if inner[i] == 0x5C and i + 1 < len(inner):
            nxt = inner[i + 1]
            mapping = {0x6E: 0x0A, 0x72: 0x0D, 0x74: 0x09, 0x62: 0x08, 0x66: 0x0C}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if nxt in (0x28, 0x29, 0x5C):
                out.append(nxt)
                i += 2
                continue
            if 0x30 <= nxt <= 0x37:
                j = i + 1
                octal = b""
                while j < len(inner) and len(octal) < 3 and 0x30 <= inner[j] <= 0x37:
                    octal += bytes([inner[j]])
                    j += 1
                out.append(int(octal.decode("ascii"), 8) & 0xFF)
                i = j
                continue
            i += 2
            continue
        out.append(inner[i])
        i += 1
    return bytes(out)


def decode_pdf_hex(raw: bytes) -> bytes:
    hexed = re.sub(rb"\s+", b"", raw)
    if len(hexed) % 2:
        hexed += b"0"
    try:
        return bytes.fromhex(hexed.decode("ascii"))
    except ValueError:
        return b""


def printable_preview(text: str, limit: int = 240) -> str:
    cleaned = "".join(ch if (32 <= ord(ch) < 127 or ch in "\n\t") else " " for ch in text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
    if len(cleaned) > limit:
        return cleaned[:limit] + "…"
    return cleaned


def looks_like_text(text: str) -> bool:
    if not text or len(text.strip()) < 2:
        return False
    printable = sum(1 for ch in text if 32 <= ord(ch) < 127)
    return printable / max(1, len(text)) >= 0.55


def _latin(data: bytes) -> str:
    return data.decode("latin-1", errors="replace")


def _stream_payload(obj_body: bytes) -> tuple[bytes | None, str | None, int | None]:
    idx = obj_body.find(b"stream")
    if idx < 0:
        return None, None, None
    after = obj_body[idx + 6 :]
    consumed = 6
    if after.startswith(b"\r\n"):
        after = after[2:]
        consumed += 2
    elif after.startswith(b"\n") or after.startswith(b"\r"):
        after = after[1:]
        consumed += 1
    end = after.rfind(b"endstream")
    if end < 0:
        return None, None, None
    payload = after[:end]
    if payload.endswith(b"\r\n"):
        payload = payload[:-2]
    elif payload.endswith(b"\n") or payload.endswith(b"\r"):
        payload = payload[:-1]
    filt = None
    fm = re.search(rb"/Filter\s*/([A-Za-z0-9]+)", obj_body[:idx])
    if fm:
        filt = fm.group(1).decode("ascii", errors="replace")
    else:
        arr = re.search(rb"/Filter\s*\[\s*/([A-Za-z0-9]+)", obj_body[:idx])
        if arr:
            filt = arr.group(1).decode("ascii", errors="replace")
    stream_offset = idx + consumed
    if filt in {"FlateDecode", "Fl"}:
        inflated = _inflate(payload)
        return (inflated if inflated is not None else payload), filt, stream_offset
    return payload, filt, stream_offset


# ---------------------------------------------------------------------------
# Tokenizer / value parser
# ---------------------------------------------------------------------------

_WS = b" \t\r\n\f\x00"


def tokenize_pdf(data: bytes) -> list[tuple[str, Any, int]]:
    """Return (kind, value, offset) tokens. Comments discarded."""
    tokens: list[tuple[str, Any, int]] = []
    i = 0
    n = len(data)
    while i < n:
        ch = data[i]
        if ch in _WS:
            i += 1
            continue
        if ch == 0x25:  # %
            while i < n and data[i] not in b"\r\n":
                i += 1
            continue
        if data.startswith(b"<<", i):
            tokens.append(("dict_start", "<<", i))
            i += 2
            continue
        if data.startswith(b">>", i):
            tokens.append(("dict_end", ">>", i))
            i += 2
            continue
        if ch == 0x5B:
            tokens.append(("array_start", "[", i))
            i += 1
            continue
        if ch == 0x5D:
            tokens.append(("array_end", "]", i))
            i += 1
            continue
        if ch == 0x28:
            start = i
            depth = 0
            i += 1
            while i < n:
                if data[i] == 0x5C and i + 1 < n:
                    i += 2
                    continue
                if data[i] == 0x28:
                    depth += 1
                    i += 1
                    continue
                if data[i] == 0x29:
                    if depth == 0:
                        i += 1
                        break
                    depth -= 1
                i += 1
            tokens.append(("string", unescape_pdf_literal(data[start:i]), start))
            continue
        if ch == 0x3C and not data.startswith(b"<<", i):
            start = i
            i += 1
            while i < n and data[i] != 0x3E:
                i += 1
            hex_body = data[start + 1 : i]
            i = min(n, i + 1)
            tokens.append(("hex", decode_pdf_hex(hex_body), start))
            continue
        if ch == 0x2F:
            start = i
            i += 1
            while i < n and data[i] not in _WS and data[i] not in b"()<>[]{}/%":
                i += 1
            tokens.append(("name", data[start + 1 : i].decode("latin-1", errors="replace"), start))
            continue
        if ch in b"+-.0123456789":
            start = i
            i += 1
            while i < n and data[i] in b"+-.0123456789":
                i += 1
            raw = data[start:i]
            try:
                if b"." in raw:
                    tokens.append(("number", float(raw), start))
                else:
                    tokens.append(("number", int(raw), start))
            except ValueError:
                tokens.append(("op", raw.decode("latin-1", errors="replace"), start))
            continue
        start = i
        while i < n and data[i] not in _WS and data[i] not in b"()<>[]{}/%":
            i += 1
        word = data[start:i].decode("latin-1", errors="replace")
        tokens.append(("op", word, start))
    return tokens


def parse_pdf_value(tokens: list[tuple[str, Any, int]], idx: int = 0) -> tuple[Any, int]:
    if idx >= len(tokens):
        return None, idx
    kind, val, _off = tokens[idx]
    if kind == "dict_start":
        out: dict[str, Any] = {}
        idx += 1
        while idx < len(tokens) and tokens[idx][0] != "dict_end":
            if tokens[idx][0] != "name":
                idx += 1
                continue
            key = tokens[idx][1]
            value, idx = parse_pdf_value(tokens, idx + 1)
            out[key] = value
        if idx < len(tokens) and tokens[idx][0] == "dict_end":
            idx += 1
        return out, idx
    if kind == "array_start":
        arr: list[Any] = []
        idx += 1
        while idx < len(tokens) and tokens[idx][0] != "array_end":
            item, idx = parse_pdf_value(tokens, idx)
            arr.append(item)
        if idx < len(tokens) and tokens[idx][0] == "array_end":
            idx += 1
        return arr, idx
    if kind in {"string", "hex"}:
        return ("bytes", val), idx + 1
    if kind == "name":
        return ("name", val), idx + 1
    if kind == "number":
        if (
            idx + 2 < len(tokens)
            and tokens[idx + 1][0] == "number"
            and tokens[idx + 2][0] == "op"
            and tokens[idx + 2][1] == "R"
        ):
            return ("ref", int(val), int(tokens[idx + 1][1])), idx + 3
        return val, idx + 1
    if kind == "op" and val in {"true", "false", "null"}:
        return {"true": True, "false": False, "null": None}[val], idx + 1
    return ("op", val), idx + 1


def parse_pdf_dict(blob: bytes) -> dict[str, Any]:
    start = blob.find(b"<<")
    if start < 0:
        return {}
    tokens = tokenize_pdf(blob[start:])
    value, _ = parse_pdf_value(tokens, 0)
    return value if isinstance(value, dict) else {}


def _as_refs(value: Any) -> list[tuple[int, int]]:
    refs: list[tuple[int, int]] = []
    if isinstance(value, tuple) and value and value[0] == "ref":
        refs.append((int(value[1]), int(value[2])))
    elif isinstance(value, list):
        for item in value:
            refs.extend(_as_refs(item))
    elif isinstance(value, dict):
        for item in value.values():
            refs.extend(_as_refs(item))
    return refs


def _name_of(value: Any) -> str | None:
    if isinstance(value, tuple) and value and value[0] == "name":
        return str(value[1])
    return None


def _bytes_of(value: Any) -> bytes | None:
    if isinstance(value, tuple) and value and value[0] == "bytes":
        return bytes(value[1])
    return None


# ---------------------------------------------------------------------------
# Container: objects, xref tables/streams, ObjStm, after-EOF
# ---------------------------------------------------------------------------

def _raw_objects(data: bytes) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for match in _OBJ_RE.finditer(data):
        obj_id = int(match.group(1))
        gen = int(match.group(2))
        start = match.start()
        end = data.find(b"endobj", match.end())
        if end < 0:
            continue
        end += 6
        body = data[match.end() : end - 6]
        stream, filt, stream_off = _stream_payload(body)
        header = body[: body.find(b"stream")] if b"stream" in body else body
        objects.append({
            "id": obj_id,
            "gen": gen,
            "offset": start,
            "end": end,
            "body": body,
            "header": header,
            "dict": parse_pdf_dict(header if header.strip() else body),
            "stream": stream,
            "raw_stream": None,
            "filter": filt,
            "stream_offset": stream_off,
            "has_stream": stream is not None,
            "from_objstm": False,
            "source": "raw",
        })
    return objects


def _parse_classic_xrefs(data: bytes) -> list[dict[str, Any]]:
    revisions: list[dict[str, Any]] = []
    for marker in re.finditer(rb"\bxref\b", data):
        pos = marker.end()
        live: dict[int, dict[str, Any]] = {}
        freed: list[dict[str, Any]] = []
        while pos < len(data):
            while pos < len(data) and data[pos] in b" \t\r\n":
                pos += 1
            if data[pos : pos + 7] == b"trailer" or data[pos : pos + 9] == b"startxref":
                break
            hm = re.match(rb"(\d+)\s+(\d+)\s+", data[pos:])
            if not hm:
                break
            first = int(hm.group(1))
            count = int(hm.group(2))
            pos += hm.end()
            for i in range(count):
                while pos < len(data) and data[pos] in b"\r\n":
                    pos += 1
                line = data[pos : pos + 20]
                pos += min(20, max(0, len(data) - pos))
                parts = line.split()
                if len(parts) < 3:
                    continue
                try:
                    off = int(parts[0])
                    gen = int(parts[1])
                except ValueError:
                    continue
                flag = parts[2][:1]
                obj_id = first + i
                if flag == b"n":
                    live[obj_id] = {"offset": off, "gen": gen, "kind": "n"}
                elif flag == b"f":
                    live.pop(obj_id, None)
                    freed.append({"id": obj_id, "gen": gen, "next": off})
        trailer = {}
        tpos = data.find(b"trailer", marker.end())
        if tpos >= 0 and (not revisions or tpos < (revisions[-1].get("_next_xref") or tpos + 1) or True):
            nxt = data.find(b"startxref", tpos)
            chunk = data[tpos + 7 : nxt if nxt > tpos else tpos + 800]
            trailer = parse_pdf_dict(chunk)
        revisions.append({
            "kind": "classic",
            "offset": marker.start(),
            "live": live,
            "freed": freed,
            "trailer": trailer,
        })
    return revisions


def _parse_xref_stream(obj: dict[str, Any]) -> dict[str, Any] | None:
    d = obj.get("dict") or {}
    if _name_of(d.get("Type")) != "XRef" and b"/Type /XRef" not in (obj.get("header") or b""):
        return None
    raw = obj.get("stream")
    if raw is None:
        return None
    w = d.get("W") if isinstance(d.get("W"), list) else [1, 2, 1]
    widths = [int(x) for x in w[:3]]
    while len(widths) < 3:
        widths.append(0)
    size = int(d.get("Size") or 0)
    index = d.get("Index") if isinstance(d.get("Index"), list) else [0, size]
    pairs = []
    vals = [int(x) for x in index]
    for i in range(0, len(vals) - 1, 2):
        pairs.append((vals[i], vals[i + 1]))
    entry_len = sum(widths)
    if entry_len <= 0:
        return None
    live: dict[int, dict[str, Any]] = {}
    freed: list[dict[str, Any]] = []
    compressed: list[dict[str, Any]] = []
    cursor = 0
    for first, count in pairs:
        for i in range(count):
            chunk = raw[cursor : cursor + entry_len]
            cursor += entry_len
            if len(chunk) < entry_len:
                break
            fields = []
            p = 0
            for width in widths:
                if width == 0:
                    fields.append(0)
                    continue
                fields.append(int.from_bytes(chunk[p : p + width], "big"))
                p += width
            typ = fields[0] if widths[0] else 1
            obj_id = first + i
            if typ == 0:
                freed.append({"id": obj_id, "next": fields[1], "gen": fields[2]})
            elif typ == 1:
                live[obj_id] = {"offset": fields[1], "gen": fields[2], "kind": "n"}
            elif typ == 2:
                live[obj_id] = {
                    "offset": None,
                    "gen": 0,
                    "kind": "objstm",
                    "objstm": fields[1],
                    "index": fields[2],
                }
                compressed.append({"id": obj_id, "objstm": fields[1], "index": fields[2]})
    return {
        "kind": "xref-stream",
        "offset": obj["offset"],
        "live": live,
        "freed": freed,
        "compressed": compressed,
        "trailer": d,
        "object_id": obj["id"],
    }


def _unpack_objstm(obj: dict[str, Any]) -> list[dict[str, Any]]:
    d = obj.get("dict") or {}
    if _name_of(d.get("Type")) != "ObjStm" and b"/Type /ObjStm" not in (obj.get("header") or b""):
        return []
    raw = obj.get("stream")
    if raw is None:
        return []
    try:
        count = int(d.get("N") or 0)
        first = int(d.get("First") or 0)
    except (TypeError, ValueError):
        return []
    header = raw[:first]
    tokens = tokenize_pdf(header)
    pairs: list[tuple[int, int]] = []
    i = 0
    while i + 1 < len(tokens) and len(pairs) < count:
        if tokens[i][0] == "number" and tokens[i + 1][0] == "number":
            pairs.append((int(tokens[i][1]), int(tokens[i + 1][1])))
            i += 2
        else:
            i += 1
    members: list[dict[str, Any]] = []
    for idx, (oid, off) in enumerate(pairs):
        start = first + off
        end = first + pairs[idx + 1][1] if idx + 1 < len(pairs) else len(raw)
        body = raw[start:end]
        members.append({
            "id": oid,
            "gen": 0,
            "offset": obj["offset"],
            "end": obj.get("end"),
            "body": body,
            "header": body,
            "dict": parse_pdf_dict(body),
            "stream": None,
            "filter": None,
            "stream_offset": None,
            "has_stream": False,
            "from_objstm": True,
            "objstm_id": obj["id"],
            "objstm_index": idx,
            "source": "objstm",
        })
    return members


def _logical_eof(data: bytes) -> int:
    matches = list(_EOF_RE.finditer(data))
    if not matches:
        return len(data)
    return matches[-1].end()


def scan_after_eof(data: bytes) -> dict[str, Any]:
    eof_at = _logical_eof(data)
    tail = data[eof_at:]
    hits: list[dict[str, Any]] = []
    if not tail.strip():
        return {"bytes_after_eof": 0, "hits": [], "leftover": False}
    if b" obj" in tail or _OBJ_RE.search(tail):
        hits.append({"kind": "trailing-objects", "offset": eof_at, "invented": False})
    if b"%PDF" in tail:
        hits.append({"kind": "appended-revision", "offset": eof_at + tail.find(b"%PDF"), "invented": False})
    if b"\xff\xd8\xff" in tail:
        hits.append({"kind": "trailing-jpeg", "offset": eof_at + tail.find(b"\xff\xd8\xff"), "invented": False})
    if tail.find(b"\x89PNG") >= 0:
        hits.append({"kind": "trailing-png", "offset": eof_at + tail.find(b"\x89PNG"), "invented": False})
    for label, needle in (
        ("embedded-file", b"/EmbeddedFile"),
        ("thumbnail", b"/Thumb"),
        ("alternate-image", b"/Alternates"),
        ("preview", b"/Preview"),
        ("producer-leftover", b"/Producer"),
    ):
        at = tail.find(needle)
        if at >= 0:
            hits.append({"kind": label, "offset": eof_at + at, "invented": False})
    preview = printable_preview(_latin(tail[:400]))
    if preview:
        hits.append({"kind": "raw-tail", "offset": eof_at, "preview": preview, "invented": False})
    return {
        "bytes_after_eof": len(tail),
        "hits": hits,
        "leftover": bool(hits),
        "sha256": sha256_hex(tail) if tail else None,
    }


def load_pdf_container(data: bytes) -> dict[str, Any]:
    objects = _raw_objects(data)
    classic = _parse_classic_xrefs(data)
    xref_streams: list[dict[str, Any]] = []
    objstm_members: list[dict[str, Any]] = []
    for obj in objects:
        xr = _parse_xref_stream(obj)
        if xr:
            xref_streams.append(xr)
        for mem in _unpack_objstm(obj):
            objstm_members.append(mem)
    seen = {(o["id"], o["gen"], o["offset"], o.get("from_objstm")) for o in objects}
    for mem in objstm_members:
        key = (mem["id"], mem["gen"], mem["offset"], True)
        if key not in seen:
            objects.append(mem)
            seen.add(key)
    revisions = list(classic) + list(xref_streams)
    revisions.sort(key=lambda r: int(r.get("offset") or 0))
    for i, rev in enumerate(revisions):
        rev["xref_revision"] = i
    live: dict[int, dict[str, Any]] = {}
    freed_all: list[dict[str, Any]] = []
    for rev in revisions:
        live.update(rev.get("live") or {})
        for gone in rev.get("live") and [] or []:
            pass
        # apply this revision's live map (n wins, missing stays unless freed)
        for item in rev.get("freed") or []:
            live.pop(item.get("id"), None)
            freed_all.append({**item, "xref_revision": rev.get("xref_revision")})
        for oid, meta in (rev.get("live") or {}).items():
            live[oid] = {**meta, "xref_revision": rev.get("xref_revision")}
    eof_count = len(_EOF_RE.findall(data))
    startxrefs = [int(m.group(1)) for m in _STARTXREF_RE.finditer(data)]
    after = scan_after_eof(data)
    by_id: dict[int, list[dict[str, Any]]] = {}
    for obj in objects:
        by_id.setdefault(obj["id"], []).append(obj)
    for versions in by_id.values():
        versions.sort(key=lambda o: (o["offset"], 0 if o.get("from_objstm") else 1))
    return {
        "objects": objects,
        "by_id": by_id,
        "revisions": revisions,
        "live": live,
        "freed": freed_all,
        "xref_streams": xref_streams,
        "objstm_members": objstm_members,
        "eof_count": eof_count,
        "startxref_count": len(startxrefs),
        "incremental": eof_count > 1 or len(startxrefs) > 1 or len(revisions) > 1,
        "after_eof": after,
    }


def _is_live_instance(obj: dict[str, Any], live: dict[int, dict[str, Any]]) -> bool:
    meta = live.get(obj["id"])
    if meta is None:
        return False
    if meta.get("kind") == "objstm":
        return bool(obj.get("from_objstm")) and meta.get("objstm") == obj.get("objstm_id")
    off = meta.get("offset")
    if off is None:
        return False
    return abs(int(off) - int(obj["offset"])) <= 8


def _xref_rev_for(obj: dict[str, Any], revisions: list[dict[str, Any]]) -> int | None:
    chosen = None
    for rev in revisions:
        meta = (rev.get("live") or {}).get(obj["id"])
        if not meta:
            continue
        if meta.get("kind") == "objstm" and obj.get("from_objstm") and meta.get("objstm") == obj.get("objstm_id"):
            chosen = rev.get("xref_revision")
        elif meta.get("offset") is not None and abs(int(meta["offset"]) - int(obj["offset"])) <= 8:
            chosen = rev.get("xref_revision")
    return chosen


# ---------------------------------------------------------------------------
# Font encodings / ToUnicode
# ---------------------------------------------------------------------------

def _winansi_char(code: int) -> str:
    try:
        return bytes([code & 0xFF]).decode("cp1252", errors="replace")
    except Exception:  # noqa: BLE001
        return ""


def _macroman_char(code: int) -> str:
    try:
        return bytes([code & 0xFF]).decode("mac_roman", errors="replace")
    except Exception:  # noqa: BLE001
        return ""


def parse_tounicode_cmap(blob: bytes) -> dict[int, str]:
    mapping: dict[int, str] = {}
    text = blob
    for m in re.finditer(rb"beginbfchar(.*?)endbfchar", text, re.S):
        pairs = re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1))
        for src, dst in pairs:
            mapping[int(src, 16)] = decode_pdf_hex(dst).decode("utf-16-be", errors="replace")
    for m in re.finditer(rb"beginbfrange(.*?)endbfrange", text, re.S):
        block = m.group(1)
        for src1, src2, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            a, b = int(src1, 16), int(src2, 16)
            base = decode_pdf_hex(dst)
            if len(base) >= 2:
                start_cp = int.from_bytes(base[-2:], "big")
                prefix = base[:-2]
                for i, code in enumerate(range(a, b + 1)):
                    mapping[code] = (prefix + (start_cp + i).to_bytes(2, "big")).decode("utf-16-be", errors="replace")
        for src1, src2, arr in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]", block, re.S):
            dests = re.findall(rb"<([0-9A-Fa-f]+)>", arr)
            a = int(src1, 16)
            for i, dest in enumerate(dests):
                mapping[a + i] = decode_pdf_hex(dest).decode("utf-16-be", errors="replace")
    return mapping


def _parse_differences(value: Any) -> dict[int, str]:
    if not isinstance(value, list):
        return {}
    out: dict[int, str] = {}
    code = 0
    for item in value:
        if isinstance(item, (int, float)):
            code = int(item)
            continue
        name = _name_of(item)
        if name is None:
            continue
        out[code] = _GLYPH_NAMES.get(name, "")
        code += 1
    return out


def resolve_font(font_obj: dict[str, Any] | None, get_obj) -> dict[str, Any]:
    info: dict[str, Any] = {
        "subtype": None,
        "base_encoding": None,
        "differences": {},
        "tounicode": {},
        "cid": False,
        "type0": False,
        "identity": False,
        "embedded_font": False,
        "map_kind": "none",
        "invented": False,
    }
    if not font_obj:
        return info
    d = font_obj.get("dict") or {}
    subtype = _name_of(d.get("Subtype"))
    info["subtype"] = subtype
    info["type0"] = subtype == "Type0"
    encoding = d.get("Encoding")
    enc_name = _name_of(encoding)
    if isinstance(encoding, dict):
        enc_name = _name_of(encoding.get("BaseEncoding")) or enc_name
        info["differences"] = _parse_differences(encoding.get("Differences"))
    if isinstance(encoding, tuple) and encoding[0] == "ref":
        enc_obj = get_obj(encoding[1], encoding[2])
        if enc_obj:
            ed = enc_obj.get("dict") or {}
            enc_name = _name_of(ed.get("BaseEncoding")) or _name_of(ed.get("Type"))
            info["differences"] = _parse_differences(ed.get("Differences"))
    info["base_encoding"] = enc_name
    info["identity"] = enc_name in {"Identity-H", "Identity-V"}
    info["cid"] = subtype in {"Type0", "CIDFontType0", "CIDFontType2"} or bool(d.get("DescendantFonts"))
    touni = d.get("ToUnicode")
    cmap_blob = None
    if isinstance(touni, tuple) and touni[0] == "ref":
        tu_obj = get_obj(touni[1], touni[2])
        if tu_obj and tu_obj.get("stream") is not None:
            cmap_blob = tu_obj["stream"]
    elif font_obj.get("stream") and b"begincmap" in (font_obj.get("stream") or b""):
        cmap_blob = font_obj["stream"]
    if cmap_blob:
        info["tounicode"] = parse_tounicode_cmap(cmap_blob)
        info["map_kind"] = "tounicode"
    elif info["differences"]:
        info["map_kind"] = "differences"
    elif enc_name == "WinAnsiEncoding":
        info["map_kind"] = "winansi"
    elif enc_name == "MacRomanEncoding":
        info["map_kind"] = "macroman"
    elif enc_name == "StandardEncoding":
        info["map_kind"] = "standard"
    elif enc_name in {"Identity-H", "Identity-V"}:
        info["map_kind"] = "identity-codes"
    desc = d.get("FontDescriptor")
    if isinstance(desc, tuple) and desc[0] == "ref":
        dobj = get_obj(desc[1], desc[2])
        if dobj:
            dd = dobj.get("dict") or {}
            if any(k in dd for k in ("FontFile", "FontFile2", "FontFile3")):
                info["embedded_font"] = True
    kids = d.get("DescendantFonts")
    if isinstance(kids, list):
        for kid in kids:
            if isinstance(kid, tuple) and kid[0] == "ref":
                child = resolve_font(get_obj(kid[1], kid[2]), get_obj)
                if child.get("embedded_font"):
                    info["embedded_font"] = True
                if child.get("tounicode") and not info["tounicode"]:
                    info["tounicode"] = child["tounicode"]
                    info["map_kind"] = "tounicode"
                if child.get("cid"):
                    info["cid"] = True
    return info


def decode_codes(codes: bytes, font: dict[str, Any], *, two_byte: bool | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Decode character codes with a resolved font. Codes-only when no map."""
    chars: list[dict[str, Any]] = []
    text_parts: list[str] = []
    touni_keys = font.get("tounicode") or {}
    if two_byte is not None:
        use_two = two_byte
    elif touni_keys:
        use_two = max(touni_keys) > 255
    else:
        use_two = bool(font.get("cid") or font.get("identity"))
    i = 0
    while i < len(codes):
        if use_two and i + 1 < len(codes):
            code = (codes[i] << 8) | codes[i + 1]
            raw = codes[i : i + 2]
            step = 2
        else:
            code = codes[i]
            raw = codes[i : i + 1]
            step = 1
        decoded = None
        touni = font.get("tounicode") or {}
        diffs = font.get("differences") or {}
        if code in touni and touni[code]:
            decoded = touni[code]
        elif code in diffs and diffs[code]:
            decoded = diffs[code]
        elif font.get("map_kind") == "winansi":
            decoded = _winansi_char(code)
        elif font.get("map_kind") == "macroman":
            decoded = _macroman_char(code)
        elif font.get("map_kind") in {"standard", "none"} and 32 <= code < 127:
            decoded = chr(code)
        elif not use_two and 32 <= code < 127 and font.get("map_kind") not in {"identity-codes"}:
            decoded = chr(code)
        chars.append({
            "code": code,
            "decoded_bytes": raw.hex(),
            "char": decoded,
            "invented": False,
        })
        if decoded:
            text_parts.append(decoded)
        i += step
    return "".join(text_parts), chars


# ---------------------------------------------------------------------------
# Content-stream operators
# ---------------------------------------------------------------------------

TEXT_OPS = {"Tj", "TJ", "'", '"', "Tm", "Td", "TD", "Tf", "Tc", "Tw", "Tz", "Ts", "T*", "BT", "ET"}
PATH_OPS = {"re", "m", "l", "c", "v", "y", "h"}
FILL_OPS = {"f", "F", "f*"}
STROKE_OPS = {"S", "s", "B", "B*", "b", "b*"}
COLOR_OPS = {"rg", "RG", "g", "G", "k", "K"}
CLIP_OPS = {"W", "W*"}
STATE_OPS = {"q", "Q", "cm", "gs"}


def parse_content_ops(stream: bytes) -> list[dict[str, Any]]:
    tokens = tokenize_pdf(stream)
    ops: list[dict[str, Any]] = []
    buf: list[tuple[str, Any, int]] = []
    for kind, val, off in tokens:
        if kind != "op":
            buf.append((kind, val, off))
            continue
        args = buf
        buf = []
        ops.append({"op": val, "args": args, "offset": off})
    return ops


def extract_operator_text(stream: bytes, font_resolver) -> dict[str, Any]:
    """Parse BT/ET and text showing operators. Decode hex / TJ arrays."""
    ops = parse_content_ops(stream)
    spans: list[dict[str, Any]] = []
    glyphs: list[str] = []
    chars: list[dict[str, Any]] = []
    in_text = False
    font_name = None
    font_info: dict[str, Any] = {"map_kind": "none", "tounicode": {}, "differences": {}}
    tm = [1, 0, 0, 1, 0, 0]
    drawing: list[dict[str, Any]] = []
    fill = (0.0, 0.0, 0.0)
    stack: list[tuple] = []
    path: list[dict[str, Any]] = []
    overlays: list[dict[str, Any]] = []
    text_boxes: list[dict[str, Any]] = []
    xobjects: list[str] = []
    path_ops = 0

    def _arg_nums(args: list[tuple[str, Any, int]]) -> list[float]:
        return [float(a[1]) for a in args if a[0] == "number"]

    def _show(payload: bytes, operator: str, offset: int, *, hexed: bool) -> None:
        nonlocal font_info, font_name
        touni = font_info.get("tounicode") or {}
        if touni:
            two = max(touni) > 255
        elif font_info.get("cid") or font_info.get("identity"):
            two = True
        else:
            two = None
        text, decoded_chars = decode_codes(payload, font_info, two_byte=two)
        # Literal ASCII fallback when the font map is none and payload is already text.
        if not text and not two:
            guess = _latin(payload)
            if looks_like_text(guess) or (guess and all(32 <= ord(c) < 127 or c in "\r\n\t" for c in guess)):
                text = guess
                decoded_chars = [{
                    "code": ord(c),
                    "decoded_bytes": bytes([ord(c) & 0xFF]).hex() if ord(c) < 256 else "",
                    "char": c if 32 <= ord(c) < 127 else None,
                    "invented": False,
                } for c in guess]
        preview = printable_preview(text) if text else ""
        span = {
            "operator": operator,
            "stream_offset": offset,
            "font": font_name,
            "text": preview,
            "hex_source": hexed,
            "char_codes": payload.hex(),
            "invented": False,
        }
        spans.append(span)
        if preview:
            glyphs.append(preview)
        x, y = float(tm[4]), float(tm[5])
        text_boxes.append({
            "text": preview,
            "x": x,
            "y": y,
            "offset": offset,
            "operator": operator,
            "font": font_name,
        })
        for ch in decoded_chars:
            if ch.get("char") is None:
                continue
            chars.append({
                "char": ch["char"],
                "decoded_bytes": ch["decoded_bytes"],
                "stream_offset": offset,
                "operator": operator,
                "font": font_name,
                "invented": False,
            })

    for item in ops:
        op = item["op"]
        args = item["args"]
        off = item["offset"]
        if op == "BT":
            in_text = True
            continue
        if op == "ET":
            in_text = False
            continue
        if op == "q":
            stack.append((fill, tm[:], font_name, dict(font_info)))
            continue
        if op == "Q" and stack:
            fill, tm, font_name, font_info = stack.pop()
            continue
        if op == "rg" and len(_arg_nums(args)) >= 3:
            nums = _arg_nums(args)
            fill = (nums[0], nums[1], nums[2])
            continue
        if op == "RG":
            continue
        if op in {"g", "G"} and _arg_nums(args):
            g = _arg_nums(args)[0]
            if op == "g":
                fill = (g, g, g)
            continue
        if op == "Tf" and args:
            names = [a[1] for a in args if a[0] == "name"]
            if names:
                font_name = "/" + str(names[0])
                font_info = font_resolver(str(names[0]))
            continue
        if op == "Tm" and len(_arg_nums(args)) >= 6:
            tm = _arg_nums(args)[:6]
            continue
        if op == "Td" and len(_arg_nums(args)) >= 2:
            nums = _arg_nums(args)
            tm[4] += nums[0]
            tm[5] += nums[1]
            continue
        if op == "TD" and len(_arg_nums(args)) >= 2:
            nums = _arg_nums(args)
            tm[4] += nums[0]
            tm[5] += nums[1]
            continue
        if op == "T*":
            tm[5] -= 12
            continue
        if op == "Do":
            names = [a[1] for a in args if a[0] == "name"]
            if names:
                xobjects.append("/" + str(names[0]))
            continue
        if op == "re" and len(_arg_nums(args)) >= 4:
            nums = _arg_nums(args)
            path.append({"op": "re", "x": nums[0], "y": nums[1], "w": nums[2], "h": nums[3], "offset": off})
            continue
        if op in PATH_OPS:
            path_ops += 1
            continue
        if op in FILL_OPS or op in STROKE_OPS:
            dark = max(fill) <= 0.08
            for rect in path:
                if rect.get("op") == "re" and dark and op in FILL_OPS:
                    overlays.append({
                        "x": rect["x"],
                        "y": rect["y"],
                        "w": rect["w"],
                        "h": rect["h"],
                        "offset": rect["offset"],
                        "paint_offset": off,
                        "operator": op,
                        "fill": fill,
                        "invented": False,
                    })
            drawing.append({"op": op, "offset": off, "dark": dark, "invented": False})
            path = []
            continue
        if op in CLIP_OPS:
            drawing.append({"op": op, "offset": off, "clip": True, "invented": False})
            path = []
            continue
        if op in {"Tj", "'", '"'}:
            for kind, val, aoff in args:
                if kind in {"string", "hex"}:
                    _show(bytes(val), op, aoff, hexed=(kind == "hex"))
            continue
        if op == "TJ":
            for kind, val, aoff in args:
                if kind != "array_start" and not isinstance(val, (bytes, bytearray)) and kind != "hex":
                    continue
            # Reconstruct TJ array from args: tokens were flattened; parse nested via raw window.
            # Args collected before TJ include the whole array as parsed tokens.
            for kind, val, aoff in args:
                if kind in {"string", "hex"}:
                    _show(bytes(val), "TJ", aoff, hexed=(kind == "hex"))
            continue

    # If TJ args were stored as a parsed array (from tokenize, array tokens), recover them.
    if not any(s.get("operator") == "TJ" for s in spans):
        for item in ops:
            if item["op"] != "TJ":
                continue
            for kind, val, aoff in item["args"]:
                if kind in {"string", "hex"}:
                    _show(bytes(val), "TJ", aoff, hexed=(kind == "hex"))

    under = []
    for box in text_boxes:
        if not box.get("text"):
            continue
        for ov in overlays:
            if ov["paint_offset"] > box["offset"]:
                under.append({
                    "text": box["text"],
                    "object_stream_offset": box["offset"],
                    "operator": box["operator"],
                    "font": box["font"],
                    "overlay": ov,
                    "invented": False,
                    "note": "Text operators appear before an opaque vector rectangle in the same stream.",
                })
                break

    return {
        "ops": [o["op"] for o in ops],
        "spans": spans,
        "glyphs": glyphs,
        "characters": chars,
        "overlays": overlays,
        "text_under_overlay": under,
        "xobjects": xobjects,
        "path_ops": path_ops,
        "has_text_ops": any(o["op"] in {"Tj", "TJ", "'", '"'} for o in ops),
        "has_image_ops": bool(xobjects),
        "invented": False,
    }


# ---------------------------------------------------------------------------
# Historical page dereference
# ---------------------------------------------------------------------------

def _get_obj_factory(container: dict[str, Any], prefer_live: bool = False):
    by_id = container["by_id"]
    live = container["live"]

    def get_obj(oid: int, gen: int | None = None, *, instance: dict[str, Any] | None = None):
        versions = by_id.get(int(oid)) or []
        if instance is not None:
            return instance
        if prefer_live:
            for obj in versions:
                if _is_live_instance(obj, live) and (gen is None or obj["gen"] == gen):
                    return obj
        if gen is not None:
            for obj in reversed(versions):
                if obj["gen"] == gen:
                    return obj
        return versions[-1] if versions else None

    def get_all(oid: int, gen: int | None = None) -> list[dict[str, Any]]:
        versions = list(by_id.get(int(oid)) or [])
        if gen is not None:
            matched = [v for v in versions if v["gen"] == gen]
            return matched or versions
        return versions

    get_obj.all = get_all  # type: ignore[attr-defined]
    return get_obj


def dereference_page(page: dict[str, Any], get_obj, seen: set[tuple[int, int]] | None = None) -> dict[str, Any]:
    """Recursively follow historical /Page keys. Capability 1."""
    seen = seen if seen is not None else set()
    d = page.get("dict") or {}
    graph: dict[str, list[str]] = {k: [] for k in PAGE_FOLLOW_KEYS}
    followed: list[dict[str, Any]] = []

    def walk(obj: dict[str, Any], via: str) -> None:
        key = (obj["id"], obj["gen"], obj["offset"], via)
        if key in seen:
            return
        seen.add(key)
        followed.append({
            "via": via,
            "object_id": f"{obj['id']} {obj['gen']}",
            "offset": obj["offset"],
            "from_objstm": bool(obj.get("from_objstm")),
            "has_stream": bool(obj.get("has_stream")),
            "invented": False,
        })
        od = obj.get("dict") or {}
        targets = {
            "Contents": od.get("Contents"),
            "Resources": od.get("Resources"),
            "XObject": None,
            "Font": None,
            "ToUnicode": od.get("ToUnicode"),
            "Annots": od.get("Annots"),
            "Metadata": od.get("Metadata"),
            "PieceInfo": od.get("PieceInfo"),
            "StructParents": od.get("StructParents"),
            "AcroForm": od.get("AcroForm"),
            "Thumb": od.get("Thumb"),
            "SMask": od.get("SMask"),
            "Mask": od.get("Mask"),
            "Alternates": od.get("Alternates"),
            "EF": od.get("EF"),
            "F": od.get("F") if _name_of(od.get("Type")) in {"Filespec", "EmbeddedFile"} or "EF" in od else None,
        }
        res = od.get("Resources")
        res_obj = None
        if isinstance(res, tuple) and res[0] == "ref":
            res_obj = get_obj(res[1], res[2])
            res = (res_obj.get("dict") if res_obj else None) or {}
        if isinstance(res, dict):
            targets["XObject"] = res.get("XObject")
            targets["Font"] = res.get("Font")
            if via == "Resources" or True:
                targets["Properties"] = res.get("Properties")
        for name, val in targets.items():
            refs = _as_refs(val)
            if isinstance(val, dict):
                refs.extend(_as_refs(val))
            for rid, rgen in refs:
                label = f"{rid} {rgen}"
                if name in graph and label not in graph[name]:
                    graph[name].append(label)
                children = get_obj.all(rid, rgen) if hasattr(get_obj, "all") else [get_obj(rid, rgen)]
                for child in children:
                    if not child:
                        continue
                    walk(child, name)
                    if child.get("has_stream") and name in {"XObject", "Contents"}:
                        cd = child.get("dict") or {}
                        if _name_of(cd.get("Subtype")) == "Form" or cd.get("Resources"):
                            walk(child, "XObject")

    walk(page, "Page")
    contents_refs = _as_refs(d.get("Contents"))
    content_streams = []
    seen_streams: set[tuple[int, int, int]] = set()
    for rid, rgen in contents_refs:
        children = get_obj.all(rid, rgen) if hasattr(get_obj, "all") else [get_obj(rid, rgen)]
        for obj in children:
            if obj and obj.get("stream") is not None:
                key = (obj["id"], obj["gen"], obj["offset"])
                if key in seen_streams:
                    continue
                seen_streams.add(key)
                content_streams.append(obj)
    if page.get("stream") is not None and _name_of(d.get("Type")) != "Page":
        content_streams.append(page)
    named_fonts: dict[str, tuple[int, int]] = {}
    res = d.get("Resources")
    if isinstance(res, tuple) and res[0] == "ref":
        res_obj = get_obj(res[1], res[2])
        res = (res_obj.get("dict") if res_obj else None) or {}
    if isinstance(res, dict):
        fonts = res.get("Font")
        if isinstance(fonts, tuple) and fonts[0] == "ref":
            fobj = get_obj(fonts[1], fonts[2])
            fonts = (fobj.get("dict") if fobj else None) or {}
        if isinstance(fonts, dict):
            for fname, fval in fonts.items():
                refs = _as_refs(fval)
                if refs:
                    named_fonts[str(fname)] = refs[0]

    return {
        "page_object": f"{page['id']} {page['gen']}",
        "offset": page["offset"],
        "graph": graph,
        "followed": followed,
        "content_streams": content_streams,
        "named_fonts": named_fonts,
        "invented": False,
    }


def live_page_ids(container: dict[str, Any], get_obj) -> set[int]:
    """Page object IDs reachable from the live Catalog → Pages → Kids tree."""
    live = container["live"]
    catalogs = [
        o for o in container["objects"]
        if _name_of((o.get("dict") or {}).get("Type")) == "Catalog"
    ]
    root = None
    for cat in catalogs:
        if not live or _is_live_instance(cat, live) or cat["id"] in live:
            root = cat
            break
    if root is None and catalogs:
        root = catalogs[-1]
    found: set[int] = set()
    if not root:
        return found

    def walk_pages(obj: dict[str, Any] | None, depth: int = 0) -> None:
        if obj is None or depth > 32:
            return
        d = obj.get("dict") or {}
        typ = _name_of(d.get("Type"))
        if typ == "Page":
            found.add(obj["id"])
            return
        kids = d.get("Kids")
        for rid, rgen in _as_refs(kids if kids is not None else d.get("Pages")):
            child = get_obj(rid, rgen)
            walk_pages(child, depth + 1)
        if typ == "Catalog":
            for rid, rgen in _as_refs(d.get("Pages")):
                walk_pages(get_obj(rid, rgen), depth + 1)

    walk_pages(root)
    return found


# ---------------------------------------------------------------------------
# Orphans, images, producer artifacts
# ---------------------------------------------------------------------------

def scan_orphans(container: dict[str, Any]) -> dict[str, Any]:
    objects = container["objects"]
    live = container["live"]
    referenced: set[tuple[int, int]] = set()
    for obj in objects:
        for m in _REF_RE.finditer(obj.get("header") or obj.get("body") or b""):
            referenced.add((int(m.group(1)), int(m.group(2))))
        if obj.get("stream"):
            for m in _REF_RE.finditer(obj["stream"]):
                referenced.add((int(m.group(1)), int(m.group(2))))
    orphans = []
    unused_fonts = []
    deleted_images = []
    detached_annots = []
    unused_objstm = []
    old_compressed = []
    duplicate_gens = []
    for oid, versions in container["by_id"].items():
        gens = {v["gen"] for v in versions}
        if len(versions) > 1:
            duplicate_gens.append({
                "id": oid,
                "count": len(versions),
                "generations": sorted(gens),
                "offsets": [v["offset"] for v in versions],
                "invented": False,
            })
        for obj in versions:
            live_hit = _is_live_instance(obj, live)
            in_xref = oid in live
            kind = None
            d = obj.get("dict") or {}
            typ = _name_of(d.get("Type"))
            sub = _name_of(d.get("Subtype"))
            if obj.get("from_objstm") and not live_hit:
                unused_objstm.append({
                    "object_id": f"{obj['id']} {obj['gen']}",
                    "objstm_id": obj.get("objstm_id"),
                    "offset": obj["offset"],
                    "invented": False,
                })
                kind = "unused-objstm-member"
            elif not in_xref and live:
                kind = "orphan-stream" if obj.get("has_stream") else "orphan-object"
            elif in_xref and not live_hit:
                kind = "prior-generation"
            if kind:
                item = {
                    "object_id": f"{obj['id']} {obj['gen']}",
                    "offset": obj["offset"],
                    "kind": kind,
                    "type": typ,
                    "subtype": sub,
                    "from_objstm": bool(obj.get("from_objstm")),
                    "invented": False,
                }
                orphans.append(item)
                if sub == "Image" or typ == "XObject" and sub == "Image":
                    deleted_images.append(item)
                if typ == "Font" or sub in {"Type1", "TrueType", "Type0", "Type3", "CIDFontType0", "CIDFontType2"}:
                    unused_fonts.append(item)
                if typ == "Annot" or sub in {"Highlight", "Redact", "Square", "Stamp"}:
                    detached_annots.append(item)
            if obj.get("from_objstm") and not live_hit:
                old_compressed.append({
                    "object_id": f"{obj['id']} {obj['gen']}",
                    "objstm_id": obj.get("objstm_id"),
                    "invented": False,
                })
    freed = container.get("freed") or []
    return {
        "orphans": orphans,
        "freed_xref": freed,
        "duplicate_generations": duplicate_gens,
        "unreferenced_fonts": unused_fonts,
        "deleted_images": deleted_images,
        "detached_annotations": detached_annots,
        "unused_objstm_members": unused_objstm,
        "old_compressed_objects": old_compressed,
        "referenced_count": len(referenced),
        "invented": False,
    }


def extract_images(obj: dict[str, Any]) -> dict[str, Any] | None:
    d = obj.get("dict") or {}
    if _name_of(d.get("Subtype")) != "Image" and not (
        _name_of(d.get("Type")) == "XObject" and obj.get("has_stream")
        and d.get("Width") is not None
    ):
        if _name_of(d.get("Subtype")) != "Image":
            return None
    payload = obj.get("stream")
    width = int(d["Width"]) if isinstance(d.get("Width"), (int, float)) else None
    height = int(d["Height"]) if isinstance(d.get("Height"), (int, float)) else None
    smask = _as_refs(d.get("SMask"))
    mask = _as_refs(d.get("Mask"))
    alts = _as_refs(d.get("Alternates"))
    return {
        "object_id": f"{obj['id']} {obj['gen']}",
        "offset": obj["offset"],
        "width": width,
        "height": height,
        "filter": obj.get("filter"),
        "smask": [f"{a} {b}" for a, b in smask],
        "mask": [f"{a} {b}" for a, b in mask],
        "alternates": [f"{a} {b}" for a, b in alts],
        "sha256": sha256_hex(payload) if payload is not None else None,
        "bytes": len(payload) if payload is not None else 0,
        "native_resolution": {"width": width, "height": height},
        "invented": False,
    }


def compare_images(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    aligned = old.get("width") == new.get("width") and old.get("height") == new.get("height")
    same = old.get("sha256") and old.get("sha256") == new.get("sha256")
    return {
        "aligned": bool(aligned),
        "same_bytes": bool(same),
        "old": {k: old[k] for k in ("object_id", "width", "height", "sha256", "smask") if k in old},
        "new": {k: new[k] for k in ("object_id", "width", "height", "sha256", "smask") if k in new},
        "unredacted_raster_in_old": bool(old.get("sha256") and not same),
        "invented": False,
        "note": "Native-stream compare. Registration uses matching width/height. Not a transcript.",
    }


_PRODUCER_NEEDLES = (
    (b"Acrobat", "acrobat"),
    (b"Distiller", "acrobat-distiller"),
    (b"PDFMaker", "acrobat-pdfmaker"),
    (b"Microsoft Word", "microsoft-word"),
    (b"Word for", "microsoft-word"),
    (b"Mac OS X", "macos-quartz"),
    (b"Tesseract", "tesseract-ocr"),
    (b"ABBYY", "abbyy"),
    (b"OmniPage", "omnipage"),
    (b"ScanSnap", "scanner"),
    (b"HP Scan", "scanner"),
    (b"Canon", "scanner"),
    (b"iText", "itext"),
    (b"ReportLab", "reportlab"),
    (b"/OCG", "ocg-layer"),
    (b"/OCProperties", "ocg-properties"),
    (b"/StructTreeRoot", "structure-tree"),
    (b"/MarkInfo", "markinfo"),
    (b"/PieceInfo", "pieceinfo"),
    (b".tmp", "temp-filename"),
    (b".TMP", "temp-filename"),
    (b"~$", "temp-filename"),
    (b"/LastModified", "revision-id"),
    (b"/PieceInfo", "pieceinfo"),
)


def search_producer_artifacts(data: bytes, objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for needle, kind in _PRODUCER_NEEDLES:
        start = 0
        while True:
            at = data.find(needle, start)
            if at < 0:
                break
            window = data[max(0, at - 24) : at + 48]
            hits.append({
                "kind": kind,
                "offset": at,
                "excerpt": printable_preview(_latin(window), 80),
                "invented": False,
            })
            start = at + len(needle)
            if len(hits) > 80:
                break
        if len(hits) > 80:
            break
    for obj in objects:
        d = obj.get("dict") or {}
        typ = _name_of(d.get("Type"))
        if typ in {"OCG", "OCMD"} or _name_of(d.get("Subtype")) == "OCG":
            name = _bytes_of(d.get("Name"))
            hits.append({
                "kind": "ocg-layer",
                "object_id": f"{obj['id']} {obj['gen']}",
                "name": printable_preview(_latin(name)) if name else None,
                "offset": obj["offset"],
                "invented": False,
            })
        if typ == "StructElem" or d.get("S") is not None and typ == "StructElem":
            hits.append({
                "kind": "structure-tree",
                "object_id": f"{obj['id']} {obj['gen']}",
                "offset": obj["offset"],
                "invented": False,
            })
        if b"/PieceInfo" in (obj.get("header") or b""):
            hits.append({
                "kind": "pieceinfo",
                "object_id": f"{obj['id']} {obj['gen']}",
                "offset": obj["offset"],
                "invented": False,
            })
    # unique by kind+offset
    uniq = []
    seen = set()
    for h in hits:
        key = (h.get("kind"), h.get("offset"), h.get("object_id"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(h)
    return uniq[:64]


_ID_PATTERNS = (
    ("fbi-doc-id", re.compile(rb"\b(?:FBI|EFTA|FOIA)[-_A-Z0-9]{4,}\b")),
    ("bates", re.compile(rb"\b[A-Z]{2,10}[-_ ]?\d{5,}\b")),
    ("iso-date", re.compile(rb"\b\d{4}-\d{2}-\d{2}\b")),
    ("pdf-date", re.compile(rb"D:\d{8,14}")),
    ("serial", re.compile(rb"\b[A-Z]{1,4}\d{6,}\b")),
)


def extract_identifiers(data: bytes) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for kind, cre in _ID_PATTERNS:
        for m in cre.finditer(data):
            found.append({
                "kind": kind,
                "value": m.group(0).decode("ascii", errors="replace"),
                "offset": m.start(),
                "invented": False,
            })
            if len(found) >= 40:
                return found
    return found


# ---------------------------------------------------------------------------
# Revision compare + classification
# ---------------------------------------------------------------------------

def _token_sig(stream: bytes) -> list[str]:
    return [t[1] if t[0] == "op" else "" for t in tokenize_pdf(stream) if t[0] == "op"]


def compare_streams(old: bytes, new: bytes, *, old_id: str, new_id: str) -> dict[str, Any]:
    old_ops = extract_operator_text(old, lambda _n: {"map_kind": "none", "tounicode": {}, "differences": {}})
    new_ops = extract_operator_text(new, lambda _n: {"map_kind": "none", "tounicode": {}, "differences": {}})
    old_strings = [s["text"] for s in old_ops["spans"] if s.get("text")]
    new_strings = [s["text"] for s in new_ops["spans"] if s.get("text")]
    old_set, new_set = set(old_strings), set(new_strings)
    old_text_ops = [o for o in old_ops["ops"] if o in {"Tj", "TJ", "'", '"'}]
    new_text_ops = [o for o in new_ops["ops"] if o in {"Tj", "TJ", "'", '"'}]
    old_xo, new_xo = set(old_ops["xobjects"]), set(new_ops["xobjects"])
    return {
        "old_object": old_id,
        "new_object": new_id,
        "bytes_only_in_old": old != new,
        "byte_len_old": len(old),
        "byte_len_new": len(new),
        "sha256_old": sha256_hex(old),
        "sha256_new": sha256_hex(new),
        "text_operators_only_in_old": [o for o in old_text_ops if o not in new_text_ops] if old_text_ops != new_text_ops else [],
        "strings_only_in_old": sorted(old_set - new_set),
        "strings_only_in_new": sorted(new_set - old_set),
        "glyph_sequences_only_in_old": sorted(set(old_ops["glyphs"]) - set(new_ops["glyphs"])),
        "xobject_refs_only_in_old": sorted(old_xo - new_xo),
        "invented": False,
    }


def classify_redaction(
    *,
    leftover: bool,
    under_vector: list[Any],
    has_text: bool,
    path_ops: int,
    images: list[Any],
    old_revision: bool,
    deleted_bytes: bool,
) -> str:
    if under_vector:
        return CLASS_TEXT_UNDER_VECTOR
    if old_revision:
        return CLASS_OLD_REVISION
    if deleted_bytes or leftover:
        return CLASS_DELETED_BYTES
    if not has_text and path_ops >= 8:
        return CLASS_TEXT_TO_OUTLINES
    if not has_text and images:
        return CLASS_TEXT_RASTERIZED
    if not leftover and not has_text:
        return CLASS_SANITIZED
    if has_text and under_vector:
        return CLASS_TEXT_UNDER_VECTOR
    if leftover:
        return CLASS_DELETED_BYTES
    return CLASS_SANITIZED if not has_text else CLASS_TEXT_UNDER_VECTOR


# ---------------------------------------------------------------------------
# OCR after structural recovery (capability 13)
# ---------------------------------------------------------------------------

def _ocr_engine_name() -> str | None:
    if shutil.which("tesseract"):
        return "tesseract"
    try:
        import pytesseract  # noqa: F401
        return "pytesseract"
    except Exception:  # noqa: BLE001
        return None


def ocr_after_structural(
    *,
    structural_hidden: bool,
    surrounding_text: list[str],
    historical_rasters: list[dict[str, Any]],
    hosted: bool = False,
) -> dict[str, Any]:
    """OCR unredacted surround / historical rasters only. Never covered letters."""
    base = {
        "ocr_ran": False,
        "ocr_after_structural_only": True,
        "covered_letters_from_context": False,
        "context_guess": False,
        "heatmap_is_transcript": False,
        "invented": False,
        "surrounding_text": [t for t in surrounding_text if t],
        "historical_raster_ocr": [],
        "note": (
            "OCR only after structural recovery. Unredacted surrounding text and "
            "historical raster differences may be read. Covered letters are never "
            "reconstructed from context. Context guesses are not recovery."
        ),
    }
    if structural_hidden:
        base["ocr_deferred"] = True
        base["reason"] = "structural leftover / operator / revision bytes recovered first"
        return base
    if hosted:
        base["ocr_engine"] = None
        base["ocr_status"] = "unbound-hosted-preview"
        base["note"] += " Hosted preview has no OCR engine bound."
        return base
    engine = _ocr_engine_name()
    if engine is None:
        base["ocr_engine"] = None
        base["ocr_status"] = "unavailable"
        base["note"] += " No OCR engine bound on this host."
        return base
    # Engine present: still refuse to reconstruct covered letters.
    # Surrounding operator text is already structural. Historical rasters
    # with leftover pixels may be OCR'd; we only record that the engine
    # is available and that any result would be labeled ocr_surrounding.
    base["ocr_engine"] = engine
    base["ocr_status"] = "ready-surround-and-historical-raster-only"
    base["ocr_ran"] = False
    base["note"] += (
        f" Engine {engine} is present but covered-box OCR is refused. "
        "Historical unredacted rasters are surfaced via image-layer recovery, not guessed."
    )
    for img in historical_rasters:
        if img.get("unredacted_raster_in_old"):
            base["historical_raster_ocr"].append({
                "object_id": img.get("old", {}).get("object_id"),
                "status": "raster-available-not-context-guess",
                "invented": False,
            })
    return base


# ---------------------------------------------------------------------------
# Twin-page / neighboring document
# ---------------------------------------------------------------------------

def twin_compare_pdfs(a: dict[str, Any], b: dict[str, Any], raw_a: bytes, raw_b: bytes) -> dict[str, Any]:
    a_strings = set()
    b_strings = set()
    for span in a.get("operator_text") or []:
        if span.get("text"):
            a_strings.add(span["text"])
    for span in b.get("operator_text") or []:
        if span.get("text"):
            b_strings.add(span["text"])
    for loc in a.get("text_layer") or []:
        a_strings.update(loc.get("strings") or [])
    for loc in b.get("text_layer") or []:
        b_strings.update(loc.get("strings") or [])
    ids_a = extract_identifiers(raw_a)
    ids_b = extract_identifiers(raw_b)
    shared_ids = []
    b_vals = {(i["kind"], i["value"]) for i in ids_b}
    for item in ids_a:
        if (item["kind"], item["value"]) in b_vals:
            shared_ids.append(item)
    geo_a = a.get("page_geometry") or []
    geo_b = b.get("page_geometry") or []
    return {
        "comparable": True,
        "only_in_first": sorted(a_strings - b_strings),
        "only_in_second": sorted(b_strings - a_strings),
        "shared_identifiers": shared_ids,
        "identifiers_first": ids_a,
        "identifiers_second": ids_b,
        "page_geometry_first": geo_a,
        "page_geometry_second": geo_b,
        "geometry_match": geo_a == geo_b,
        "heatmap_is_transcript": False,
        "invented": False,
        "note": (
            "Twin / neighboring-document compare of operator text, identifiers "
            "(FBI / Bates / serial / timestamp), and page geometry. Cited from "
            "bytes present. Not guessed. Heatmap is not a transcript."
        ),
    }


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def recover_pdf_history(data: bytes, *, hosted: bool = False) -> dict[str, Any]:
    """Run all 14 deep-history capabilities. Never invent letters."""
    empty = {
        "is_pdf": False,
        "capabilities": list(DEEP_CAPABILITIES),
        "text_layer": [],
        "metadata_hits": [],
        "attachments": [],
        "recovered": [],
        "leftover_bytes": False,
        "recovered_from": [],
        "locations": [],
        "incremental_updates": 0,
        "page_revisions": [],
        "revision_compare": [],
        "operator_text": [],
        "font_resolutions": [],
        "drawing_order": [],
        "classifications": [],
        "orphans": {},
        "xref_streams": False,
        "objstms": [],
        "after_eof": {"bytes_after_eof": 0, "hits": [], "leftover": False},
        "image_layers": [],
        "producer_artifacts": [],
        "ocr": {
            "ocr_ran": False,
            "covered_letters_from_context": False,
            "invented": False,
        },
        "recovered_characters": [],
        "page_geometry": [],
        "object_ids_replaced": [],
    }
    if not data.startswith(b"%PDF"):
        return empty

    container = load_pdf_container(data)
    objects = container["objects"]
    live = container["live"]
    get_obj = _get_obj_factory(container, prefer_live=False)
    get_live = _get_obj_factory(container, prefer_live=True)
    tree_pages = live_page_ids(container, get_live if live else get_obj)

    pages = [o for o in objects if _name_of((o.get("dict") or {}).get("Type")) == "Page"]
    catalogs = [o for o in objects if _name_of((o.get("dict") or {}).get("Type")) == "Catalog"]

    page_revisions = []
    operator_text = []
    font_resolutions = []
    drawing_order = []
    recovered_characters: list[dict[str, Any]] = []
    recovered: list[dict[str, Any]] = []
    recovered_from: list[str] = []
    locations: list[dict[str, Any]] = []
    text_layer: list[dict[str, Any]] = []
    classifications: list[dict[str, Any]] = []
    image_layers: list[dict[str, Any]] = []
    revision_compare: list[dict[str, Any]] = []
    object_ids_replaced: list[dict[str, Any]] = []
    page_geometry: list[dict[str, Any]] = []

    def font_resolver_for(page_graph_fonts: dict[str, dict[str, Any]]):
        def _resolve(name: str) -> dict[str, Any]:
            key = name[1:] if name.startswith("/") else name
            return page_graph_fonts.get(key) or page_graph_fonts.get("/" + key) or {
                "map_kind": "none",
                "tounicode": {},
                "differences": {},
            }
        return _resolve

    extra_follow: list[dict[str, Any]] = []
    for cat in catalogs:
        cd = cat.get("dict") or {}
        for key in ("AcroForm", "Metadata", "StructTreeRoot", "Names", "OCProperties"):
            for rid, rgen in _as_refs(cd.get(key)):
                extra_follow.append({
                    "via": key,
                    "object_id": f"{rid} {rgen}",
                    "invented": False,
                })
                child = get_obj(rid, rgen)
                if not child:
                    continue
                chd = child.get("dict") or {}
                if key == "Names":
                    for nest in ("EmbeddedFiles", "JavaScript", "Dests"):
                        for nid, ngen in _as_refs(chd.get(nest)):
                            extra_follow.append({
                                "via": nest,
                                "object_id": f"{nid} {ngen}",
                                "invented": False,
                            })

    current_contents: dict[int, dict[str, Any]] = {}
    stale_contents: list[dict[str, Any]] = []

    def _instance_is_current(obj: dict[str, Any]) -> bool:
        versions = container["by_id"].get(obj["id"]) or [obj]
        if live:
            if obj["id"] not in live:
                return False
            return _is_live_instance(obj, live)
        return obj["offset"] == versions[-1]["offset"] and not obj.get("from_objstm")

    for page in pages:
        deref = dereference_page(page, get_obj)
        in_tree = (not tree_pages) or (page["id"] in tree_pages)
        live_page = _instance_is_current(page) and in_tree
        leftover_page = not live_page
        xref_rev = _xref_rev_for(page, container["revisions"])
        box = (page.get("dict") or {}).get("MediaBox")
        if isinstance(box, list) and len(box) >= 4:
            page_geometry.append({
                "page_object": f"{page['id']} {page['gen']}",
                "mediabox": [float(x) if isinstance(x, (int, float)) else x for x in box[:4]],
                "live": live_page,
                "invented": False,
            })

        font_maps: dict[str, dict[str, Any]] = {}
        for label in deref["graph"].get("Font") or []:
            try:
                fid, fgen = label.split()
                fobj = get_obj(int(fid), int(fgen))
            except ValueError:
                fobj = None
            resolved = resolve_font(fobj, get_obj)
            resolved["object_id"] = label
            font_maps[label] = resolved
            font_maps[label.split()[0]] = resolved
            font_resolutions.append({**resolved, "page": f"{page['id']} {page['gen']}"})
        for fname, (fid, fgen) in (deref.get("named_fonts") or {}).items():
            fobj = get_obj(fid, fgen)
            resolved = resolve_font(fobj, get_obj)
            resolved["object_id"] = f"{fid} {fgen}"
            font_maps[fname] = resolved
            font_maps["/" + fname] = resolved

        resolver = font_resolver_for(font_maps)
        page_ops_bundle = []
        under_all = []
        has_text = False
        path_ops = 0
        page_images = []
        for stream_obj in deref["content_streams"]:
            payload = stream_obj.get("stream")
            if payload is None:
                continue
            parsed = extract_operator_text(payload, resolver)
            page_ops_bundle.append(parsed)
            under_all.extend(parsed["text_under_overlay"])
            has_text = has_text or parsed["has_text_ops"]
            path_ops += int(parsed["path_ops"])
            source_rev = "current" if live_page and _is_live_instance(stream_obj, live) else "prior"
            if leftover_page or not _instance_is_current(stream_obj):
                source_rev = "prior"
            for span in parsed["spans"]:
                record = {
                    **span,
                    "page": f"{page['id']} {page['gen']}",
                    "object_id": stream_obj["id"],
                    "generation": stream_obj["gen"],
                    "xref_revision": _xref_rev_for(stream_obj, container["revisions"]),
                    "source_revision": source_rev,
                    "sha256": sha256_hex(payload),
                    "invented": False,
                }
                operator_text.append(record)
            under_here = bool(parsed["text_under_overlay"])
            for ch in parsed["characters"]:
                if source_rev != "prior" and not under_here:
                    continue
                recovered_characters.append({
                    "char": ch["char"],
                    "page": f"{page['id']} {page['gen']}",
                    "object_id": stream_obj["id"],
                    "generation": stream_obj["gen"],
                    "xref_revision": _xref_rev_for(stream_obj, container["revisions"]),
                    "stream_offset": ch["stream_offset"],
                    "operator": ch["operator"],
                    "font": ch.get("font"),
                    "decoded_bytes": ch["decoded_bytes"],
                    "source_revision": "prior" if source_rev == "prior" else "under-vector",
                    "sha256": sha256_hex(payload),
                    "invented": False,
                })
            if leftover_page or source_rev == "prior":
                stale_contents.append({
                    "page": f"{page['id']} {page['gen']}",
                    "stream": f"{stream_obj['id']} {stream_obj['gen']}",
                    "obj": stream_obj,
                    "parsed": parsed,
                })
            elif live_page:
                current_contents[page["id"]] = {
                    "page": f"{page['id']} {page['gen']}",
                    "stream": f"{stream_obj['id']} {stream_obj['gen']}",
                    "obj": stream_obj,
                    "parsed": parsed,
                }

        for label in deref["graph"].get("XObject") or []:
            try:
                xid, xgen = label.split()
                xobjs = get_obj.all(int(xid), int(xgen)) if hasattr(get_obj, "all") else [get_obj(int(xid), int(xgen))]
            except ValueError:
                xobjs = []
            for xobj in xobjs:
                img = extract_images(xobj) if xobj else None
                if img:
                    img["page"] = f"{page['id']} {page['gen']}"
                    img["live"] = live_page and _instance_is_current(xobj)
                    page_images.append(img)
                    image_layers.append(img)

        drawing_order.append({
            "page": f"{page['id']} {page['gen']}",
            "text_under_overlay": under_all,
            "overlays": [o for bundle in page_ops_bundle for o in bundle["overlays"]],
            "invented": False,
        })

        cls = classify_redaction(
            leftover=leftover_page,
            under_vector=under_all,
            has_text=has_text,
            path_ops=path_ops,
            images=page_images,
            old_revision=leftover_page,
            deleted_bytes=leftover_page,
        )
        if any(not _instance_is_current(s) for s in deref["content_streams"] if s.get("stream") is not None):
            leftover_page = leftover_page or True
            if cls != CLASS_TEXT_UNDER_VECTOR:
                cls = CLASS_OLD_REVISION
        if live_page and not leftover_page and not under_all and not has_text and not page_images and path_ops < 8:
            cls = CLASS_SANITIZED
        classifications.append({
            "page": f"{page['id']} {page['gen']}",
            "class": cls,
            "live": live_page,
            "leftover": leftover_page,
            "invented": False,
        })
        page_revisions.append({
            "page_object": f"{page['id']} {page['gen']}",
            "offset": page["offset"],
            "live": live_page,
            "leftover": leftover_page,
            "xref_revision": xref_rev,
            "graph": deref["graph"],
            "followed": deref["followed"],
            "extra_catalog_follow": extra_follow,
            "classification": cls,
            "invented": False,
        })

    # Same-ID incremental stream compare + stale page vs current
    for oid, versions in container["by_id"].items():
        streams = [v for v in versions if v.get("stream") is not None]
        if len(streams) >= 2:
            old, new = streams[0], streams[-1]
            cmp = compare_streams(
                old["stream"], new["stream"],
                old_id=f"{old['id']} {old['gen']}",
                new_id=f"{new['id']} {new['gen']}",
            )
            cmp["object_ids_replaced"] = [{
                "old": f"{old['id']} {old['gen']}",
                "new": f"{new['id']} {new['gen']}",
                "old_offset": old["offset"],
                "new_offset": new["offset"],
            }]
            object_ids_replaced.extend(cmp["object_ids_replaced"])
            revision_compare.append(cmp)
        images = [extract_images(v) for v in versions]
        images = [i for i in images if i]
        if len(images) >= 2:
            image_layers.append(compare_images(images[0], images[-1]))

    current_list = list(current_contents.values())
    for stale in stale_contents:
        target = current_list[0] if current_list else None
        if target and stale["obj"].get("stream") is not None and target["obj"].get("stream") is not None:
            cmp = compare_streams(
                stale["obj"]["stream"],
                target["obj"]["stream"],
                old_id=stale["stream"],
                new_id=target["stream"],
            )
            cmp["stale_page"] = stale["page"]
            cmp["current_page"] = target["page"]
            cmp["object_ids_replaced"] = [{
                "old": stale["stream"],
                "new": target["stream"],
                "kind": "stale-page-follow",
            }]
            object_ids_replaced.extend(cmp["object_ids_replaced"])
            revision_compare.append(cmp)

    # Per-object leftover / text-layer (compat with locate_pdf)
    for oid, versions in container["by_id"].items():
        live_meta = live.get(oid) if live else None
        for i, obj in enumerate(versions):
            if live:
                if live_meta is not None:
                    is_latest = _is_live_instance(obj, live)
                else:
                    is_latest = True
            else:
                is_latest = i == len(versions) - 1
            leftover = not is_latest
            if leftover:
                if obj.get("from_objstm"):
                    kind = "unused-objstm-member"
                elif container["incremental"]:
                    kind = "prior-stream" if obj.get("has_stream") else "incremental-revision"
                else:
                    kind = "prior-stream" if obj.get("has_stream") else "pdf-object"
            elif live and live_meta is None:
                leftover = True
                kind = "unused-object" if not obj.get("from_objstm") else "unused-objstm-member"
            else:
                kind = "pdf-object"
            blobs = [obj.get("body") or b""]
            if obj.get("stream") is not None:
                blobs.append(obj["stream"])
            strings: list[str] = []
            for blob in blobs:
                for tok in tokenize_pdf(blob):
                    if tok[0] in {"string", "hex"}:
                        text = printable_preview(_latin(bytes(tok[1])))
                        if text and text not in strings and (looks_like_text(text) or len(text) >= 2):
                            strings.append(text)
            if obj.get("stream") is not None:
                parsed = extract_operator_text(obj["stream"], lambda _n: {"map_kind": "none", "tounicode": {}, "differences": {}})
                for span in parsed["spans"]:
                    if span.get("text") and span["text"] not in strings:
                        strings.append(span["text"])
            loc = {
                "object_id": f"{obj['id']} {obj['gen']}",
                "offset": obj["offset"],
                "stream": bool(obj.get("has_stream")),
                "filter": obj.get("filter"),
                "leftover": leftover,
                "kind": kind,
                "strings": strings,
                "from_objstm": bool(obj.get("from_objstm")),
                "invented": False,
            }
            locations.append(loc)
            if leftover:
                recovered.append({
                    "object_id": f"{obj['id']} {obj['gen']}",
                    "generation": obj["gen"],
                    "offset": obj["offset"],
                    "stream": bool(obj.get("has_stream")),
                    "stream_offset": obj.get("stream_offset"),
                    "filter": obj.get("filter"),
                    "recovered_from": kind,
                    "preview": " | ".join(strings) if strings else "",
                    "sha256": sha256_hex(obj["stream"] if obj.get("stream") is not None else obj.get("body") or b""),
                    "in_latest_xref": is_latest,
                    "xref_revision": _xref_rev_for(obj, container["revisions"]),
                    "source_revision": "prior",
                    "invented": False,
                })
                if kind not in recovered_from:
                    recovered_from.append(kind)
            elif strings:
                text_layer.append({
                    "object_id": f"{obj['id']} {obj['gen']}",
                    "offset": obj["offset"],
                    "strings": strings,
                    "under_visual_box_possible": True,
                    "invented": False,
                    "note": "Text still in the PDF object. Not guessed from a black rectangle.",
                })

    # Attachments
    attachments: list[dict[str, Any]] = []
    for obj in objects:
        body = obj.get("body") or b""
        header = obj.get("header") or b""
        if b"/EmbeddedFile" not in body and b"/Filespec" not in body and b"/EF" not in header + body:
            continue
        names = []
        for match in re.finditer(rb"/(?:F|UF|Desc)\s*(\((?:\\.|[^\\)])*\))", body):
            names.append(printable_preview(_latin(unescape_pdf_literal(match.group(1)))))
        payload = obj.get("stream")
        preview = printable_preview(_latin(payload)) if payload else ""
        att = {
            "object_id": f"{obj['id']} {obj['gen']}",
            "offset": obj["offset"],
            "names": [n for n in names if n],
            "has_stream": bool(obj.get("has_stream")),
            "preview": preview,
            "recovered_from": "attachment",
            "invented": False,
        }
        attachments.append(att)
        recovered.append({
            "object_id": att["object_id"],
            "offset": att["offset"],
            "stream": att["has_stream"],
            "recovered_from": "attachment",
            "preview": preview,
            "names": att["names"],
            "invented": False,
        })
        if "attachment" not in recovered_from:
            recovered_from.append("attachment")

    metadata_hits: list[dict[str, Any]] = []
    info_re = re.compile(
        rb"/(Title|Author|Subject|Keywords|Creator|Producer|CreationDate|ModDate)\s*"
        rb"(?:\((?:\\.|[^\\)])*\)|<[^>]*>)"
    )
    for match in info_re.finditer(data):
        key = match.group(1).decode("ascii")
        token = match.group(0).split(None, 1)[-1]
        if token.startswith(b"("):
            value = _latin(unescape_pdf_literal(token))
        elif token.startswith(b"<"):
            value = _latin(decode_pdf_hex(token[1:-1]))
        else:
            value = _latin(token)
        preview = printable_preview(value)
        if preview:
            metadata_hits.append({
                "key": key,
                "value": preview,
                "source": "pdf-bytes",
                "offset": match.start(),
                "invented": False,
            })

    for obj in objects:
        if b"/Metadata" in (obj.get("header") or b"") or (
            obj.get("stream") and obj["stream"].lstrip().startswith(b"<?xpacket")
        ):
            extra = []
            blob = obj.get("stream") or obj.get("body") or b""
            for match in info_re.finditer(blob):
                extra.append(match)
            if extra or (obj.get("stream") and b"xpacket" in obj["stream"][:40]):
                if "metadata-stream" not in recovered_from:
                    recovered_from.append("metadata-stream")

    orphans = scan_orphans(container)
    if orphans.get("orphans") or orphans.get("unused_objstm_members"):
        if "orphan-object" not in recovered_from:
            recovered_from.append("orphan-object")
        for item in orphans.get("orphans") or []:
            if any(r.get("object_id") == item["object_id"] for r in recovered):
                continue
            obj_id = item["object_id"]
            recovered.append({
                "object_id": obj_id,
                "offset": item.get("offset"),
                "recovered_from": item.get("kind") or "orphan-object",
                "preview": "",
                "invented": False,
            })

    after = container["after_eof"]
    if after.get("leftover"):
        recovered_from.append("after-eof")
        recovered.append({
            "object_id": "after-eof",
            "offset": _logical_eof(data),
            "recovered_from": "after-eof",
            "preview": "",
            "bytes": after.get("bytes_after_eof"),
            "sha256": after.get("sha256"),
            "invented": False,
        })

    producer = search_producer_artifacts(data, objects)
    identifiers = extract_identifiers(data)

    # Stale-page leftover classification
    if any(p.get("leftover") for p in page_revisions):
        if "old-revision" not in recovered_from:
            recovered_from.append("old-revision")
        for p in page_revisions:
            if p.get("leftover") and p.get("classification") != CLASS_OLD_REVISION:
                p["classification"] = CLASS_OLD_REVISION
        for c in classifications:
            if c.get("leftover"):
                c["class"] = CLASS_OLD_REVISION
        for span in operator_text:
            if span.get("source_revision") != "prior" or not span.get("text"):
                continue
            recovered.append({
                "object_id": f"{span.get('object_id')} {span.get('generation')}",
                "generation": span.get("generation"),
                "offset": span.get("stream_offset"),
                "operator": span.get("operator"),
                "font": span.get("font"),
                "recovered_from": "old-revision",
                "preview": span.get("text") or "",
                "sha256": span.get("sha256"),
                "xref_revision": span.get("xref_revision"),
                "source_revision": "prior",
                "invented": False,
            })

    leftover_bytes = bool(recovered) or bool(after.get("leftover")) or any(
        p.get("leftover") for p in page_revisions
    )
    if any(d.get("text_under_overlay") for d in drawing_order):
        leftover_bytes = True
        if "text-under-vector" not in recovered_from:
            recovered_from.append("text-under-vector")
        for drow in drawing_order:
            for item in drow.get("text_under_overlay") or []:
                recovered.append({
                    "object_id": drow["page"],
                    "offset": item.get("object_stream_offset"),
                    "operator": item.get("operator"),
                    "font": item.get("font"),
                    "recovered_from": "text-under-vector",
                    "preview": item.get("text") or "",
                    "invented": False,
                    "note": item.get("note"),
                })

    surrounding = []
    for span in operator_text:
        if span.get("source_revision") == "current" and span.get("text"):
            surrounding.append(span["text"])
    historical_rasters = [img for img in image_layers if img.get("unredacted_raster_in_old")]
    structural_hidden = bool(
        leftover_bytes
        or any(s.get("source_revision") == "prior" and s.get("text") for s in operator_text)
        or any(d.get("text_under_overlay") for d in drawing_order)
    )
    ocr = ocr_after_structural(
        structural_hidden=structural_hidden,
        surrounding_text=surrounding,
        historical_rasters=historical_rasters,
        hosted=hosted,
    )

    # If nothing leftover and only sanitized live pages, classify sanitized.
    if not leftover_bytes:
        for c in classifications:
            if c.get("live") and c.get("class") not in {
                CLASS_TEXT_UNDER_VECTOR,
                CLASS_TEXT_TO_OUTLINES,
                CLASS_TEXT_RASTERIZED,
                CLASS_OLD_REVISION,
            }:
                c["class"] = CLASS_SANITIZED

    return {
        "is_pdf": True,
        "capabilities": list(DEEP_CAPABILITIES),
        "object_count": len(objects),
        "incremental_updates": max(0, container["eof_count"] - 1),
        "startxref_count": container["startxref_count"],
        "text_layer": text_layer,
        "metadata_hits": metadata_hits,
        "attachments": attachments,
        "recovered": recovered,
        "leftover_bytes": leftover_bytes,
        "recovered_from": recovered_from,
        "locations": locations,
        "page_revisions": page_revisions,
        "revision_compare": revision_compare,
        "operator_text": operator_text,
        "font_resolutions": font_resolutions,
        "drawing_order": drawing_order,
        "classifications": classifications,
        "orphans": orphans,
        "xref_streams": bool(container["xref_streams"]),
        "objstms": [
            {
                "object_id": f"{m['id']} {m['gen']}",
                "objstm_id": m.get("objstm_id"),
                "offset": m["offset"],
                "invented": False,
            }
            for m in container["objstm_members"]
        ],
        "after_eof": after,
        "image_layers": image_layers,
        "producer_artifacts": producer,
        "identifiers": identifiers,
        "ocr": ocr,
        "recovered_characters": recovered_characters,
        "page_geometry": page_geometry,
        "object_ids_replaced": object_ids_replaced,
        "extra_catalog_follow": extra_follow,
        "invented": False,
        "guessed_letters": False,
        "heatmap_is_transcript": False,
        "forensic_certification": False,
    }


def merge_history_into_locate(scanned: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    """Overlay deep-history fields onto a locate_pdf-shaped dict."""
    out = dict(scanned)
    for key in (
        "capabilities",
        "page_revisions",
        "revision_compare",
        "operator_text",
        "font_resolutions",
        "drawing_order",
        "classifications",
        "orphans",
        "xref_streams",
        "objstms",
        "after_eof",
        "image_layers",
        "producer_artifacts",
        "identifiers",
        "ocr",
        "recovered_characters",
        "page_geometry",
        "object_ids_replaced",
        "extra_catalog_follow",
    ):
        out[key] = history.get(key)
    # Prefer history leftover/recovered when it found more.
    if history.get("leftover_bytes"):
        out["leftover_bytes"] = True
    if history.get("recovered"):
        seen = {(r.get("object_id"), r.get("offset"), r.get("recovered_from")) for r in out.get("recovered") or []}
        merged = list(out.get("recovered") or [])
        for rec in history["recovered"]:
            key = (rec.get("object_id"), rec.get("offset"), rec.get("recovered_from"))
            if key not in seen:
                merged.append(rec)
                seen.add(key)
        out["recovered"] = merged
    for kind in history.get("recovered_from") or []:
        if kind not in (out.get("recovered_from") or []):
            out.setdefault("recovered_from", []).append(kind)
    if history.get("text_layer"):
        have = {(t.get("object_id"), tuple(t.get("strings") or [])) for t in out.get("text_layer") or []}
        extra = []
        for loc in history["text_layer"]:
            key = (loc.get("object_id"), tuple(loc.get("strings") or []))
            if key not in have:
                extra.append(loc)
        out["text_layer"] = list(out.get("text_layer") or []) + extra
    if history.get("locations"):
        out["locations"] = history["locations"] or out.get("locations")
    if history.get("attachments"):
        out["attachments"] = history["attachments"] or out.get("attachments")
    if history.get("metadata_hits"):
        out["metadata_hits"] = history["metadata_hits"] or out.get("metadata_hits")
    if history.get("object_count"):
        out["object_count"] = history["object_count"]
    return out
