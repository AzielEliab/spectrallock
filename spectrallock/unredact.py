"""Honest unredact / lift-overlay / leftover-bytes recovery.

Operator lock — NO-LIE. SpectralLock does not invent letters.

Locate reports what is still in the file. Lift enhances a non-opaque
cover with inject OFF (gray of the same gate). Opaque clipped black
without leftover container bytes refuses (SL-UNREDACT-OPAQUE).

Recovery is allowed only when the producer left old bytes in the
container (incremental update, unused objects, prior streams,
attachments, soft-delete / un-garbage-collected objects). That is
reading leftover bytes — not guessing a black box.

Author: Aziel Eliab. Lamb Lens: Service → Clarity → Peace.
"""

from __future__ import annotations

import hashlib
import io
import re
import zlib
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from spectrallock.debug import debug
from spectrallock.engine import (
    INJECT_NOTE,
    LIMITATION,
    equalize,
    finite01,
    gate_gray,
    is_achromatic,
    luminance,
    png_bytes,
    unsharp,
)

UNREDACT_FAMILY = ("unredact", "lift", "redact-locate")
UNREDACT_OPS = ("locate", "lift", "recover", "refuse")
REFUSE_OPAQUE = "SL-UNREDACT-OPAQUE"

UNREDACT_NOTE = (
    "Unredact / lift-overlay is locate + leftover-bytes + residual only. "
    "Locate reports text still in the file, metadata, attachments, "
    "twin-page residual, and leftover container bytes. "
    "It does not invent letters. "
    "Opaque replace (clipped solid black / true rewrite) with no leftover "
    "bytes refuses (" + REFUSE_OPAQUE + "). "
    "That is the only honest switch for visual unredact. "
    "Non-opaque cover on a file the operator owns may use contrast / residual "
    "enhancement with inject OFF (gray of the same gate). No guessed letters. "
    "A heatmap of ghosts is not a transcript. "
    "A flattened screenshot of a box is treated as replace. "
    "Leftover-bytes recovery reads prior objects / unused streams / "
    "attachments / incremental revisions that are still in the container. "
    "That is not guessing letters from a black box. "
    "If the container was rewritten and old bytes are gone, leftover_bytes "
    "is false and recovery is refused. "
    "Never claim pigment recovery, ESDA, chemical, lab, or forensic "
    "certification. Empty gate ≠ broken lens. "
    "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE."
)

OPAQUE_LUMA_MAX = 0.045
OPAQUE_STD_MAX = 0.018
COVER_LUMA_MAX = 0.42
RESIDUAL_STD_MIN = 0.028
MIN_COVER_FRAC = 0.012
MIN_COVER_PIXELS = 24

_PDF_OBJ_RE = re.compile(rb"(?m)(?<![0-9])(\d+)\s+(\d+)\s+obj\b")
_PDF_STARTXREF_RE = re.compile(rb"startxref\s+(\d+)")
_PDF_EOF_RE = re.compile(rb"%%EOF")
_PDF_INFO_RE = re.compile(
    rb"/(Title|Author|Subject|Keywords|Creator|Producer|CreationDate|ModDate)\s*"
    rb"(?:\((?:\\.|[^\\)])*\)|<[^>]*>)"
)
_PDF_NAME_RE = re.compile(rb"/([A-Za-z][A-Za-z0-9._-]*)")
_PDF_REF_RE = re.compile(rb"(\d+)\s+(\d+)\s+R")
_PDF_HEX_STR_RE = re.compile(rb"<([0-9A-Fa-f \t\r\n]+)>")
_PDF_LIT_STR_RE = re.compile(rb"\((?:\\.|[^\\)])*\)")
_PDF_TJ_RE = re.compile(rb"(?:\((?:\\.|[^\\)])*\)|\[[^\]]*\])\s*T[jJ]")

_PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _package_version() -> str:
    from spectrallock import __version__

    return __version__


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_unredact_op(value: object, default: str = "locate") -> str:
    key = str(value or default).strip().lower().replace("_", "-")
    aliases = {
        "redact-locate": "locate",
        "locate": "locate",
        "lift": "lift",
        "lift-overlay": "lift",
        "recover": "recover",
        "leftover": "recover",
        "leftover-bytes": "recover",
        "refuse": "refuse",
        "unredact": "locate",
    }
    if key not in aliases:
        known = ", ".join(UNREDACT_OPS)
        raise ValueError(f"unknown unredact op {value!r}. Known: {known}")
    return aliases[key]


def list_unredact() -> dict[str, Any]:
    return {
        "family": list(UNREDACT_FAMILY),
        "ops": list(UNREDACT_OPS),
        "refuse_code": REFUSE_OPAQUE,
        "leftover_bytes_recovery": True,
        "pigment_recovery": False,
        "guessed_letters": False,
        "heatmap_is_transcript": False,
        "esda": False,
        "forensic_certification": False,
        "inject_default": False,
        "note": UNREDACT_NOTE,
        "author": "Aziel Eliab",
        "status": "live",
    }


def _base_finding(*, op: str) -> dict[str, Any]:
    return {
        "product": "spectrallock",
        "version": _package_version(),
        "author": "Aziel Eliab",
        "family": "unredact",
        "aliases": list(UNREDACT_FAMILY),
        "op": op,
        "opaque_replace": False,
        "residual_usable": False,
        "leftover_bytes": False,
        "refuse_code": None,
        "recovered_from": [],
        "locations": [],
        "metadata_hits": [],
        "attachments": [],
        "twin_diff": None,
        "name_hits": [],
        "recovered": [],
        "cover_regions": [],
        "text_layer": [],
        "inject": False,
        "inject_applied": False,
        "pigment_recovery": False,
        "guessed_letters": False,
        "heatmap_is_transcript": False,
        "residual_is_transcript": False,
        "esda": False,
        "chemical_recovery": False,
        "forensic_certification": False,
        "flattened_screenshot_replace": False,
        "empty_gate_not_broken_lens": True,
        "inject_note": INJECT_NOTE,
        "unredact_note": UNREDACT_NOTE,
        "advisory": UNREDACT_NOTE,
        "limitation": LIMITATION,
        "rosetta_spectral_analysis": True,
        "lamb_lens": "Service → Clarity → Peace",
        "identity": "Aziel Eliab",
    }


def _unescape_pdf_literal(raw: bytes) -> str:
    inner = raw[1:-1] if raw.startswith(b"(") and raw.endswith(b")") else raw
    out = bytearray()
    i = 0
    while i < len(inner):
        if inner[i] == 0x5C and i + 1 < len(inner):  # backslash
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
    return bytes(out).decode("latin-1", errors="replace")


def _decode_pdf_hex(raw: bytes) -> str:
    hexed = re.sub(rb"\s+", b"", raw)
    if len(hexed) % 2:
        hexed += b"0"
    try:
        return bytes.fromhex(hexed.decode("ascii")).decode("latin-1", errors="replace")
    except ValueError:
        return ""


def _printable_preview(text: str, limit: int = 240) -> str:
    cleaned = "".join(ch if (32 <= ord(ch) < 127 or ch in "\n\t") else " " for ch in text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
    if len(cleaned) > limit:
        return cleaned[:limit] + "…"
    return cleaned


def _looks_like_text(text: str) -> bool:
    if not text or len(text.strip()) < 2:
        return False
    printable = sum(1 for ch in text if 32 <= ord(ch) < 127)
    return printable / max(1, len(text)) >= 0.55


def _extract_pdf_strings(blob: bytes) -> list[str]:
    found: list[str] = []
    for match in _PDF_LIT_STR_RE.finditer(blob):
        text = _unescape_pdf_literal(match.group(0))
        if _looks_like_text(text):
            found.append(text)
    for match in _PDF_HEX_STR_RE.finditer(blob):
        text = _decode_pdf_hex(match.group(1))
        if _looks_like_text(text):
            found.append(text)
    return found


def _inflate_stream(data: bytes) -> bytes | None:
    for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS, zlib.MAX_WBITS | 16):
        try:
            return zlib.decompress(data, wbits)
        except zlib.error:
            continue
    return None


def _stream_payload(obj_body: bytes) -> tuple[bytes | None, str | None]:
    idx = obj_body.find(b"stream")
    if idx < 0:
        return None, None
    after = obj_body[idx + 6 :]
    if after.startswith(b"\r\n"):
        after = after[2:]
    elif after.startswith(b"\n") or after.startswith(b"\r"):
        after = after[1:]
    end = after.rfind(b"endstream")
    if end < 0:
        return None, None
    payload = after[:end]
    if payload.endswith(b"\r\n"):
        payload = payload[:-2]
    elif payload.endswith(b"\n") or payload.endswith(b"\r"):
        payload = payload[:-1]
    filt = None
    fm = re.search(rb"/Filter\s*/([A-Za-z0-9]+)", obj_body[:idx])
    if fm:
        filt = fm.group(1).decode("ascii", errors="replace")
    if filt in {"FlateDecode", "Fl"}:
        inflated = _inflate_stream(payload)
        return (inflated if inflated is not None else payload), filt
    return payload, filt


def _parse_pdf_objects(data: bytes) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for match in _PDF_OBJ_RE.finditer(data):
        obj_id = int(match.group(1))
        gen = int(match.group(2))
        start = match.start()
        end = data.find(b"endobj", match.end())
        if end < 0:
            continue
        end += 6
        body = data[match.end() : end - 6]
        stream, filt = _stream_payload(body)
        objects.append({
            "id": obj_id,
            "gen": gen,
            "offset": start,
            "end": end,
            "body": body,
            "stream": stream,
            "filter": filt,
            "has_stream": stream is not None,
        })
    return objects


def _parse_classic_xref_live(data: bytes) -> dict[int, int]:
    """Walk every classic xref (including incremental). Last n-entry wins."""
    live: dict[int, int] = {}
    for marker in re.finditer(rb"\bxref\b", data):
        pos = marker.end()
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
                except ValueError:
                    continue
                flag = parts[2][:1]
                obj_id = first + i
                if flag == b"n":
                    live[obj_id] = off
                elif flag == b"f":
                    live.pop(obj_id, None)
    return live


def _info_hits_from_blob(blob: bytes, *, source: str, offset: int | None = None) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for match in _PDF_INFO_RE.finditer(blob):
        key = match.group(1).decode("ascii")
        token = match.group(0).split(None, 1)[-1]
        if token.startswith(b"("):
            value = _unescape_pdf_literal(token)
        elif token.startswith(b"<"):
            value = _decode_pdf_hex(token[1:-1])
        else:
            value = token.decode("latin-1", errors="replace")
        preview = _printable_preview(value)
        if not preview:
            continue
        hits.append({
            "key": key,
            "value": preview,
            "source": source,
            "offset": offset,
            "invented": False,
        })
    return hits


def _attachment_hits(objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for obj in objects:
        body = obj["body"]
        if b"/EmbeddedFile" not in body and b"/Filespec" not in body and b"/EF" not in body:
            continue
        names = []
        for match in re.finditer(rb"/(?:F|UF|Desc)\s*(\((?:\\.|[^\\)])*\))", body):
            names.append(_unescape_pdf_literal(match.group(1)))
        payload = obj["stream"] if obj["has_stream"] else None
        preview = _printable_preview(payload.decode("latin-1", errors="replace")) if payload else ""
        hits.append({
            "object_id": f"{obj['id']} {obj['gen']}",
            "offset": obj["offset"],
            "names": [n for n in names if n],
            "has_stream": bool(obj["has_stream"]),
            "preview": preview,
            "recovered_from": "attachment",
            "invented": False,
        })
    return hits


def locate_pdf(data: bytes) -> dict[str, Any]:
    """Report text/metadata/attachments/leftover objects still in the PDF."""
    if not data.startswith(b"%PDF"):
        return {
            "is_pdf": False,
            "text_layer": [],
            "metadata_hits": [],
            "attachments": [],
            "recovered": [],
            "leftover_bytes": False,
            "recovered_from": [],
            "locations": [],
            "incremental_updates": 0,
        }
    objects = _parse_pdf_objects(data)
    live_xref = _parse_classic_xref_live(data)
    eof_count = len(_PDF_EOF_RE.findall(data))
    startxrefs = [int(m.group(1)) for m in _PDF_STARTXREF_RE.finditer(data)]
    incremental = eof_count > 1 or len(startxrefs) > 1

    seen_ids: dict[int, list[dict[str, Any]]] = {}
    for obj in objects:
        seen_ids.setdefault(obj["id"], []).append(obj)

    text_layer: list[dict[str, Any]] = []
    recovered: list[dict[str, Any]] = []
    recovered_from: list[str] = []
    locations: list[dict[str, Any]] = []
    metadata_hits = _info_hits_from_blob(data, source="pdf-bytes")

    def _record_strings(obj: dict[str, Any], *, leftover: bool, kind: str) -> None:
        blobs = [obj["body"]]
        if obj["stream"] is not None:
            blobs.append(obj["stream"])
        texts: list[str] = []
        for blob in blobs:
            texts.extend(_extract_pdf_strings(blob))
            if obj["stream"] is blob:
                # content-stream operators often keep readable literals
                for match in _PDF_TJ_RE.finditer(blob):
                    texts.extend(_extract_pdf_strings(match.group(0)))
        # unique preserve order
        uniq: list[str] = []
        for t in texts:
            p = _printable_preview(t)
            if p and p not in uniq:
                uniq.append(p)
        if not uniq and not leftover:
            return
        loc = {
            "object_id": f"{obj['id']} {obj['gen']}",
            "offset": obj["offset"],
            "stream": bool(obj["has_stream"]),
            "filter": obj["filter"],
            "leftover": leftover,
            "kind": kind,
            "strings": uniq,
            "invented": False,
        }
        locations.append(loc)
        if leftover:
            item = {
                "object_id": f"{obj['id']} {obj['gen']}",
                "offset": obj["offset"],
                "stream": bool(obj["has_stream"]),
                "filter": obj["filter"],
                "recovered_from": kind,
                "preview": " | ".join(uniq) if uniq else "",
                "sha256": sha256_hex(obj["stream"] if obj["stream"] is not None else obj["body"]),
                "in_latest_xref": obj["id"] in live_xref and abs(live_xref[obj["id"]] - obj["offset"]) <= 4,
                "invented": False,
            }
            recovered.append(item)
            if kind not in recovered_from:
                recovered_from.append(kind)
        elif uniq:
            text_layer.append({
                "object_id": f"{obj['id']} {obj['gen']}",
                "offset": obj["offset"],
                "strings": uniq,
                "under_visual_box_possible": True,
                "invented": False,
                "note": "Text still in the PDF object. Not guessed from a black rectangle.",
            })

    for obj_id, versions in seen_ids.items():
        versions_sorted = sorted(versions, key=lambda o: o["offset"])
        live_off = live_xref.get(obj_id)
        for i, obj in enumerate(versions_sorted):
            is_latest = True
            if live_off is not None:
                is_latest = abs(live_off - obj["offset"]) <= 4
            elif i != len(versions_sorted) - 1:
                is_latest = False
            leftover = not is_latest
            if leftover:
                kind = "prior-stream" if obj["has_stream"] else "pdf-object"
                if incremental:
                    kind = "prior-stream" if obj["has_stream"] else "incremental-revision"
            elif live_off is None and live_xref:
                leftover = True
                kind = "unused-object"
            else:
                kind = "pdf-object"
            _record_strings(obj, leftover=leftover, kind=kind)

        if len(versions_sorted) > 1:
            if "incremental-revision" not in recovered_from and incremental:
                recovered_from.append("incremental-revision")

    attachments = _attachment_hits(objects)
    if attachments:
        recovered_from.append("attachment")
        for att in attachments:
            if att.get("preview") or att.get("has_stream"):
                recovered.append({
                    "object_id": att["object_id"],
                    "offset": att["offset"],
                    "stream": att["has_stream"],
                    "recovered_from": "attachment",
                    "preview": att.get("preview") or "",
                    "names": att.get("names") or [],
                    "invented": False,
                })

    # XMP / metadata streams
    for obj in objects:
        body = obj["body"]
        if b"/Metadata" in body or (obj["stream"] and obj["stream"].lstrip().startswith(b"<?xpacket")):
            meta_blob = obj["stream"] or body
            extra = _info_hits_from_blob(meta_blob, source="xmp", offset=obj["offset"])
            metadata_hits.extend(extra)
            if extra and "metadata-stream" not in recovered_from:
                recovered_from.append("metadata-stream")

    leftover_bytes = bool(recovered)
    debug(
        f"locate_pdf objects={len(objects)} leftover={leftover_bytes} "
        f"text_layer={len(text_layer)} eof={eof_count}"
    )
    return {
        "is_pdf": True,
        "object_count": len(objects),
        "incremental_updates": max(0, eof_count - 1),
        "startxref_count": len(startxrefs),
        "text_layer": text_layer,
        "metadata_hits": metadata_hits,
        "attachments": attachments,
        "recovered": recovered,
        "leftover_bytes": leftover_bytes,
        "recovered_from": recovered_from,
        "locations": locations,
    }


def locate_png_chunks(data: bytes) -> dict[str, Any]:
    """Leftover / ancillary text still in a PNG container."""
    if not data.startswith(_PNG_SIG):
        return {"is_png": False, "metadata_hits": [], "recovered": [], "leftover_bytes": False, "recovered_from": []}
    hits: list[dict[str, Any]] = []
    recovered: list[dict[str, Any]] = []
    recovered_from: list[str] = []
    off = 8
    while off + 8 <= len(data):
        length = int.from_bytes(data[off : off + 4], "big")
        ctype = data[off + 4 : off + 8]
        chunk = data[off + 8 : off + 8 + length]
        name = ctype.decode("latin-1", errors="replace")
        if name in {"tEXt", "zTXt", "iTXt"}:
            text = ""
            if name == "tEXt":
                text = chunk.replace(b"\x00", b"=").decode("latin-1", errors="replace")
            elif name == "zTXt":
                nul = chunk.find(b"\x00")
                key = chunk[:nul].decode("latin-1", errors="replace") if nul >= 0 else "zTXt"
                payload = chunk[nul + 2 :] if nul >= 0 else chunk
                inflated = _inflate_stream(payload) or payload
                text = f"{key}={inflated.decode('latin-1', errors='replace')}"
            else:
                text = chunk.replace(b"\x00", b" ").decode("utf-8", errors="replace")
            preview = _printable_preview(text)
            if preview:
                hits.append({"key": name, "value": preview, "source": "png-chunk", "offset": off, "invented": False})
                recovered.append({
                    "object_id": name,
                    "offset": off,
                    "stream": name != "tEXt",
                    "recovered_from": "png-chunk",
                    "preview": preview,
                    "invented": False,
                })
                if "png-chunk" not in recovered_from:
                    recovered_from.append("png-chunk")
        off += 12 + length
        if name == "IEND":
            break
    leftover = bool(recovered)
    return {
        "is_png": True,
        "metadata_hits": hits,
        "recovered": recovered,
        "leftover_bytes": leftover,
        "recovered_from": recovered_from,
    }


def classify_cover(rgb: np.ndarray) -> dict[str, Any]:
    """Covered vs removed. Opaque clipped black → refuse. Residual ≠ transcript."""
    arr = finite01(rgb)
    lum = luminance(arr)
    h, w = lum.shape
    dark = lum <= COVER_LUMA_MAX
    dark_frac = float(dark.mean()) if dark.size else 0.0
    regions: list[dict[str, Any]] = []
    opaque = False
    residual = False
    flattened = False

    boxes: list[tuple[int, int, int, int]] = []
    if dark_frac >= MIN_COVER_FRAC and int(dark.sum()) >= MIN_COVER_PIXELS:
        ys, xs = np.where(dark)
        boxes = [(int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)]

    for (x0, y0, x1, y1) in boxes:
        patch = lum[y0:y1, x0:x1]
        if patch.size < MIN_COVER_PIXELS:
            continue
        mean = float(patch.mean())
        std = float(patch.std())
        mx = float(patch.max())
        mn = float(patch.min())
        near_black = float((patch <= OPAQUE_LUMA_MAX).mean())
        is_opaque = bool(near_black >= 0.72 and std <= 0.045 and mx <= 0.12)
        is_residual = bool((not is_opaque) and std >= RESIDUAL_STD_MIN and (mx - mn) >= 0.08)
        if is_opaque:
            opaque = True
        if is_residual:
            residual = True
        regions.append({
            "x0": int(x0),
            "y0": int(y0),
            "x1": int(x1),
            "y1": int(y1),
            "mean": round(mean, 4),
            "std": round(std, 4),
            "opaque": is_opaque,
            "residual_usable": is_residual,
            "invented": False,
        })

    if opaque and not residual:
        flattened = True

    return {
        "opaque_replace": opaque and not residual,
        "residual_usable": residual,
        "flattened_screenshot_replace": flattened,
        "cover_regions": regions,
        "dark_frac": round(dark_frac, 4),
        "width": int(w),
        "height": int(h),
    }


def residual_enhance(rgb: np.ndarray) -> np.ndarray:
    """Contrast / residual of existing pixels. Inject OFF. Not a transcript."""
    arr = finite01(rgb)
    gray = luminance(arr)
    stretched = equalize(gray)
    sharp = unsharp(stretched, amount=0.9, radius=1.0)
    out = np.stack([sharp, sharp, sharp], axis=-1)
    return gate_gray(out)


def twin_residual(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    """Same page issued twice — residual compare. No invented letters."""
    aa = finite01(a)
    bb = finite01(b)
    if aa.shape != bb.shape:
        return {
            "comparable": False,
            "note": "Twin pages differ in size. Residual compare needs the same raster.",
            "invented": False,
        }
    da = np.abs(luminance(aa) - luminance(bb))
    mask = da >= 0.08
    ys, xs = np.where(mask)
    box = None
    if len(ys):
        box = {
            "x0": int(xs.min()),
            "y0": int(ys.min()),
            "x1": int(xs.max()) + 1,
            "y1": int(ys.max()) + 1,
        }
    return {
        "comparable": True,
        "changed_frac": round(float(mask.mean()), 4),
        "max_abs": round(float(da.max()), 4),
        "bbox": box,
        "heatmap_is_transcript": False,
        "invented": False,
        "note": "Pixel residual of two rasters. Not a transcript of redacted letters.",
    }


def _load_any_rgb(raw: bytes) -> np.ndarray | None:
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
        if img.mode != "RGB":
            img = img.convert("RGB")
        return finite01(np.asarray(img, dtype=np.float32) / 255.0)
    except Exception:  # noqa: BLE001
        return None


def _cite_names(query: str, haystacks: list[tuple[str, str]]) -> list[dict[str, Any]]:
    q = query.strip()
    if not q:
        return []
    hits: list[dict[str, Any]] = []
    low = q.lower()
    for where, text in haystacks:
        idx = text.lower().find(low)
        if idx < 0:
            continue
        start = max(0, idx - 24)
        end = min(len(text), idx + len(q) + 24)
        hits.append({
            "query": q,
            "where": where,
            "excerpt": _printable_preview(text[start:end], 160),
            "invented": False,
            "note": "Cited from bytes already in the production set. Not fabricated.",
        })
    return hits


def _merge_container(find: dict[str, Any], scanned: dict[str, Any]) -> None:
    find["text_layer"].extend(scanned.get("text_layer") or [])
    find["metadata_hits"].extend(scanned.get("metadata_hits") or [])
    find["attachments"].extend(scanned.get("attachments") or [])
    find["recovered"].extend(scanned.get("recovered") or [])
    find["locations"].extend(scanned.get("locations") or [])
    for kind in scanned.get("recovered_from") or []:
        if kind not in find["recovered_from"]:
            find["recovered_from"].append(kind)
    if scanned.get("leftover_bytes"):
        find["leftover_bytes"] = True
    if scanned.get("is_pdf"):
        find["container"] = "pdf"
        find["incremental_updates"] = scanned.get("incremental_updates", 0)
        find["pdf_object_count"] = scanned.get("object_count", 0)
    elif scanned.get("is_png"):
        find["container"] = find.get("container") or "png"


def analyze_unredact(
    raw: bytes,
    *,
    op: str = "locate",
    twin: bytes | None = None,
    query: str | None = None,
    production: list[tuple[str, bytes]] | None = None,
    inject: bool = False,
    filename: str = "",
) -> dict[str, Any]:
    """Run locate / lift / recover / refuse. Never invent letters."""
    op_key = parse_unredact_op(op)
    find = _base_finding(op=op_key)
    find["filename"] = filename or None
    find["size_in"] = len(raw)
    find["sha256_in"] = sha256_hex(raw)
    find["inject"] = False
    if inject:
        find["inject_ignored"] = True
        find["inject_note"] = (
            "Lift-overlay forces inject OFF (gray of the same gate). "
            + INJECT_NOTE
        )

    is_pdf = raw.startswith(b"%PDF")
    rgb = None if is_pdf else _load_any_rgb(raw)
    if is_pdf:
        _merge_container(find, locate_pdf(raw))
    elif raw.startswith(_PNG_SIG):
        _merge_container(find, locate_png_chunks(raw))
        rgb = rgb if rgb is not None else _load_any_rgb(raw)
    elif rgb is None and not is_pdf:
        find["error"] = "Need a PDF, PNG, or JPEG the operator owns."
        find["refuse_code"] = REFUSE_OPAQUE if op_key in {"lift", "refuse"} else None
        return find

    if rgb is not None:
        cover = classify_cover(rgb)
        find["opaque_replace"] = bool(cover["opaque_replace"])
        find["residual_usable"] = bool(cover["residual_usable"])
        find["flattened_screenshot_replace"] = bool(cover["flattened_screenshot_replace"])
        find["cover_regions"] = cover["cover_regions"]
        find["width"] = cover["width"]
        find["height"] = cover["height"]
        find["dark_frac"] = cover["dark_frac"]
        if find["flattened_screenshot_replace"] and not find["leftover_bytes"]:
            find["opaque_replace"] = True
            find["residual_usable"] = False

    if twin:
        twin_rgb = _load_any_rgb(twin)
        if rgb is not None and twin_rgb is not None:
            find["twin_diff"] = twin_residual(rgb, twin_rgb)
        elif twin.startswith(b"%PDF") and is_pdf:
            a = locate_pdf(raw)
            b = locate_pdf(twin)
            a_set = {s for loc in a["text_layer"] for s in loc.get("strings") or []}
            b_set = {s for loc in b["text_layer"] for s in loc.get("strings") or []}
            only_a = sorted(a_set - b_set)
            only_b = sorted(b_set - a_set)
            find["twin_diff"] = {
                "comparable": True,
                "only_in_first": only_a,
                "only_in_second": only_b,
                "heatmap_is_transcript": False,
                "invented": False,
                "note": "String-set residual of two PDFs. Cited from bytes present. Not guessed.",
            }

    hay: list[tuple[str, str]] = []
    for hit in find["metadata_hits"]:
        hay.append((f"metadata:{hit.get('key')}", str(hit.get("value") or "")))
    for loc in find["text_layer"]:
        hay.append((f"object:{loc.get('object_id')}", " ".join(loc.get("strings") or [])))
    for rec in find["recovered"]:
        hay.append((f"leftover:{rec.get('object_id')}", str(rec.get("preview") or "")))
    if production:
        for name, blob in production:
            scanned = locate_pdf(blob) if blob.startswith(b"%PDF") else locate_png_chunks(blob)
            for hit in scanned.get("metadata_hits") or []:
                hay.append((f"{name}:metadata:{hit.get('key')}", str(hit.get("value") or "")))
            for loc in scanned.get("text_layer") or []:
                hay.append((f"{name}:object:{loc.get('object_id')}", " ".join(loc.get("strings") or [])))
            for rec in scanned.get("recovered") or []:
                hay.append((f"{name}:leftover:{rec.get('object_id')}", str(rec.get("preview") or "")))
    if query:
        find["name_hits"] = _cite_names(query, hay)

    leftover = bool(find["leftover_bytes"])
    opaque = bool(find["opaque_replace"])
    residual = bool(find["residual_usable"])

    # Honest recover: leftover bytes still in the container.
    can_recover = leftover and bool(find["recovered"])
    # Visual lift only when cover is non-opaque.
    can_lift = residual and not opaque
    # Refuse visual unredact when clipped black and nothing leftover.
    must_refuse = (opaque or find["flattened_screenshot_replace"]) and not leftover

    if op_key == "refuse" or must_refuse and op_key in {"lift", "locate", "refuse"}:
        if must_refuse:
            find["refuse_code"] = REFUSE_OPAQUE
            find["op"] = "refuse" if op_key in {"lift", "refuse"} else op_key
            find["stop"] = True
            find["note"] = (
                "Opaque replace / flattened box and no leftover container bytes. "
                "Lift-overlay refuses. Residual heatmaps are not a transcript. "
                + REFUSE_OPAQUE
            )
            if op_key == "lift":
                return find

    if op_key == "recover":
        if can_recover:
            find["op"] = "recover"
            find["note"] = (
                "Recovered leftover bytes still in the container. "
                "Provenance is object id / offset / stream. Not guessed letters."
            )
            return find
        find["refuse_code"] = REFUSE_OPAQUE
        find["stop"] = True
        find["note"] = (
            "No leftover container bytes. Opaque rewrite or flattened screenshot "
            "cannot be recovered. " + REFUSE_OPAQUE
        )
        return find

    if op_key == "lift":
        if can_lift and rgb is not None:
            enhanced = residual_enhance(rgb)
            find["residual_png_b64"] = __import__("base64").b64encode(png_bytes(enhanced)).decode("ascii")
            find["residual_achromatic"] = is_achromatic(enhanced)
            find["residual_usable"] = True
            find["note"] = (
                "Non-opaque cover: residual / contrast with inject OFF. "
                "Heatmap is not a transcript. No guessed letters."
            )
            return find
        if can_recover:
            find["op"] = "recover"
            find["note"] = (
                "Visual lift refused on clipped black. Leftover container bytes "
                "were extracted instead (reading present bytes, not guessing)."
            )
            find["refuse_code"] = None
            return find
        find["refuse_code"] = REFUSE_OPAQUE
        find["stop"] = True
        find["op"] = "refuse"
        find["note"] = (
            "Lift-overlay refuses on clipped black / flattened box with no leftover bytes. "
            + REFUSE_OPAQUE
        )
        return find

    # locate (default): report; recover leftover if present; do not invent.
    if can_recover:
        find["note"] = (
            "Locate + leftover-bytes. Recovered content is still in the container. "
            "Not guessed from a black box."
        )
    elif residual:
        find["note"] = (
            "Locate: non-opaque cover. Residual may be enhanced with --no-inject. "
            "Heatmap is not a transcript."
        )
    elif must_refuse:
        find["refuse_code"] = REFUSE_OPAQUE
        find["stop"] = True
        find["note"] = (
            "Locate: opaque replace and no leftover bytes. Visual unredact refuses. "
            + REFUSE_OPAQUE
        )
    else:
        find["note"] = "Locate complete. No invented letters."
    return find


def load_unredact_path(path: str | Path) -> bytes:
    p = Path(path)
    return p.read_bytes()


def analyze_unredact_path(
    path: str | Path,
    *,
    op: str = "locate",
    twin: str | Path | None = None,
    query: str | None = None,
    production: list[str | Path] | None = None,
    inject: bool = False,
) -> dict[str, Any]:
    raw = load_unredact_path(path)
    twin_bytes = load_unredact_path(twin) if twin else None
    prod = None
    if production:
        prod = [(str(Path(item).name), load_unredact_path(item)) for item in production]
    return analyze_unredact(
        raw,
        op=op,
        twin=twin_bytes,
        query=query,
        production=prod,
        inject=inject,
        filename=str(Path(path).name),
    )
