# Universal recover audit (NO-LIE)

Operator lock 2026-09-19. Author: Aziel Eliab only.
Lamb Lens: Service → Clarity → Peace.

This audit is a coverage and honesty checklist, not a forensic certification.
If a parser is not real, it is marked **SLOT**. SLOT is never advertised as LIVE.

## Honesty checklist

| Rule | Status |
|------|--------|
| Recover present bytes / documented structure only | PASS — recovered items cite path/offset/object; `invented: false` |
| Never infer covered letters from context | PASS — no linguistic reconstruction path; OCR still after structural only on PDF |
| If bytes are not there, say so | PASS — `SL-RECOVER-NO-BYTES` / `SL-RECOVER-SANITIZED` / `SL-RECOVER-UNSUPPORTED` |
| Secrets never printed | PASS — `secret_material_present` + path/offset; values `<suppressed>` |
| Extension is not type | PASS — magic + container confirmation (`detect_bytes`) |
| Hosted does not invent copy bytes | PASS — revision-copy cap + sha256 cites |
| Catalog door not invented | PASS — recover is Worker `/v1/recover` + CLI; not a FragGate LIVE_OP |
| Worker overlay digest not invented | PASS — GitBaby CLEAR after merge; do not forward `3427dbcf…` |

## Format matrix (package)

| Kind | Status | What is real | Gap |
|------|--------|--------------|-----|
| pdf | LIVE | pdfhist 14-cap + revision graph + tip-cut copies | — |
| docx/xlsx/pptx | LIVE | ZIP parts, tracked `w:del`, vanish, hidden sheets, core props, comments | Full drawingML shape overlay geometry is partial |
| odt/ods/odp / epub | LIVE | ZIP + XML text + meta | Style-hidden text beyond XML attrs is partial |
| doc/xls/ppt | LIVE | OLE CFB directory + stream names + printable leftovers | Property-set decode and VBA disassembly are shallow |
| msg | LIVE-ole | CFB streams + text | Not a full MSG named-property map |
| rtf | LIVE | `\v` hidden + literals | Complex destinations unread |
| txt/csv/tsv/md/source/log | LIVE | encoding + comments + conflict markers | — |
| html/htm/xml/svg | LIVE | comments, hidden CSS/attrs, script JSON, data-URIs | No JS runtime / layout engine |
| json/jsonl/ipynb | LIVE | duplicate keys, tombstones, JSON Pointer, base64-in-strings | — |
| yaml/yml | LIVE-scan | comments + tombstone keys | PyYAML AST is **SLOT** (no PyYAML dep) |
| zip/tar/gz | LIVE | members, flag names, nested cite, timestamps | Nested recurse depth capped |
| 7z | **SLOT** | magic cite only | no py7zr |
| png/jpeg/gif/bmp/tiff/webp | LIVE | chunks/APP, EXIF, extra frames/pages, after-IEND carve | EXIF thumbnail pixels need Pillow EXIF blob |
| heic/heif | **SLOT** | ftyp cite | no pillow-heif |
| eml/mbox | LIVE | headers, alternate bodies, attachments | TNEF **SLOT** |
| sqlite/db | LIVE | schema, rows, freelist trunk page/offset | WAL/SHM only if those files are supplied |
| git | LIVE | when `.git` / objects supplied (HEAD, reflog, object files) | No remotes / credential hunting |
| bin | LIVE-carve | bounded signatures inside supplied bytes | Not disk forensics |

## Worker overlay honesty

Hosted `/v1/recover` is a **preview port**: PDF history + JSON tombstones + ZIP names + EML headers + PNG after-IEND + secret suppression.
Full OOXML/OLE/SQLite/Git lives in the Python package. Worker `listRecover().slot_kinds` includes `7z`, `heic`, `heif`. It does not claim package LIVE coverage it does not run.

## Refusal codes

| Code | When |
|------|------|
| SL-RECOVER-NO-BYTES | Nothing present to cite |
| SL-RECOVER-SANITIZED | Rewrite with no leftover / prior representation |
| SL-RECOVER-OPAQUE | Reserved (visual path still uses SL-UNREDACT-OPAQUE) |
| SL-UNREDACT-OPAQUE | PDF/PNG visual leftover-bytes compat |
| SL-RECOVER-UNSUPPORTED | SLOT / unbound parser |
| SL-RECOVER-CORRUPT | Container failed to parse |
| SL-RECOVER-ENCRYPTED | Encrypted container (not opened) |
| SL-RECOVER-LIMIT | Nest/size cap |

## Known gaps (do not paper over)

1. YAML AST without PyYAML — LIVE-scan only.
2. 7z / HEIC / TNEF / Brotli / full MSG property set — SLOT.
3. OLE slack sectors are printable leftovers, not a certified slack carve.
4. SQLite deleted-row payload is only cited when freelist/WAL/journal bytes exist.
5. Hosted Worker does not run the full Python scanner.
6. No FragGate `recover` door until GitBaby patterns it — Worker + CLI only.
7. Confidence is provenance quality, never guessed correctness.

## Tests that lock this

`tests/test_recover.py`: PDF incremental graph+copies, DOCX tracked/hidden, JSON tombstone + secret suppress, PNG after-IEND carve, EML alternate MIME, SQLite freelist, ZIP flag names, HEIC SLOT, CLI recover, unredact→recover attach.
`tests/test_pdfhist.py` / `tests/test_unredact.py` remain the PDF 14-cap + revision-graph lock.
