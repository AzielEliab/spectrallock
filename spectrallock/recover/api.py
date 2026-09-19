"""Universal recover family: locate · deep-recover · revision-graph · …"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from spectrallock.recover.detect import FORMAT_MATRIX, detect_bytes, sha256_hex
from spectrallock.recover.scan import (
    FLAG_NAMES,
    HOSTED_COPY_MAX,
    carve_signatures,
    ledger,
    scan_bytes,
    scan_git,
)

RECOVER_FAMILY = "recover"
RECOVER_OPS = (
    "locate",
    "deep-recover",
    "revision-graph",
    "cross-compare",
    "extract-embedded",
    "scan-orphans",
    "scan-metadata",
    "scan-sidecars",
    "scan-history",
    "refuse",
)
REFUSE_CODES = (
    "SL-RECOVER-NO-BYTES",
    "SL-RECOVER-SANITIZED",
    "SL-RECOVER-OPAQUE",
    "SL-RECOVER-UNSUPPORTED",
    "SL-RECOVER-CORRUPT",
    "SL-RECOVER-ENCRYPTED",
    "SL-RECOVER-LIMIT",
    "SL-UNREDACT-OPAQUE",
)
SIDECAR_SUFFIXES = (
    ".json", ".xml", ".xmp", ".txt", ".csv", ".log", ".bak", ".old",
    ".tmp", ".autosave", ".manifest", ".rels",
)

RECOVER_NOTE = (
    "Universal artifact recovery. Present bytes and documented structure only. "
    "Never infer covered letters from context and call that recovery. "
    "If bytes are not there, say they are not there. "
    "Secrets are cited as secret_material_present with path/offset; values suppressed. "
    "SLOT means the parser is not bound — never advertised as LIVE. "
    "Unredact remains the PDF visual leftover-bytes path. "
    "Lamb Lens: Service → Clarity → Peace. Author Aziel Eliab. NO-LIE."
)

_OP_ALIASES = {
    "locate": "locate",
    "deep": "deep-recover",
    "deep-recover": "deep-recover",
    "revision-graph": "revision-graph",
    "revision_graph": "revision-graph",
    "compare": "cross-compare",
    "cross-compare": "cross-compare",
    "cross_compare": "cross-compare",
    "extract-embedded": "extract-embedded",
    "extract_embedded": "extract-embedded",
    "scan-orphans": "scan-orphans",
    "scan_orphans": "scan-orphans",
    "scan-metadata": "scan-metadata",
    "scan_metadata": "scan-metadata",
    "scan-sidecars": "scan-sidecars",
    "scan_sidecars": "scan-sidecars",
    "scan-history": "scan-history",
    "scan_history": "scan-history",
    "refuse": "refuse",
    "production": "locate",
    "redactions": "deep-recover",
}


def parse_recover_op(value: object, default: str = "locate") -> str:
    key = str(value or default).strip().lower().replace("_", "-")
    if key not in _OP_ALIASES:
        known = ", ".join(RECOVER_OPS)
        raise ValueError(f"unknown recover op {value!r}. Known: {known}")
    return _OP_ALIASES[key]


def format_matrix() -> dict[str, dict[str, str]]:
    return {k: dict(v) for k, v in FORMAT_MATRIX.items()}


def list_recover() -> dict[str, Any]:
    live = sorted(k for k, v in FORMAT_MATRIX.items() if v["status"].startswith("live"))
    slot = sorted(k for k, v in FORMAT_MATRIX.items() if v["status"] == "slot")
    return {
        "family": RECOVER_FAMILY,
        "ops": list(RECOVER_OPS),
        "refuse_codes": list(REFUSE_CODES),
        "format_matrix": format_matrix(),
        "live_kinds": live,
        "slot_kinds": slot,
        "guessed_letters": False,
        "context_reconstruction": False,
        "no_lie": True,
        "note": RECOVER_NOTE,
        "author": "Aziel Eliab",
        "status": "live",
        "catalog_door": False,
        "worker_path": "/v1/recover",
    }


def _empty_envelope(*, op: str, filename: str | None = None) -> dict[str, Any]:
    return {
        "product": "spectrallock",
        "author": "Aziel Eliab",
        "family": RECOVER_FAMILY,
        "op": op,
        "artifact": {"filename": filename, "invented": False},
        "type": None,
        "revisions": [],
        "metadata": [],
        "embedded": [],
        "orphans": [],
        "prior_content": [],
        "redaction_regions": [],
        "recovered": [],
        "refused": [],
        "cross_file_matches": [],
        "provenance": [],
        "warnings": [],
        "secrets": [],
        "carved": [],
        "revision_graph": {"revisions": [], "edges": [], "invented": False},
        "no_lie": True,
        "guessed_letters": False,
        "heatmap_is_transcript": False,
        "forensic_certification": False,
        "lamb_lens": "Service → Clarity → Peace",
        "identity": "Aziel Eliab",
        "note": RECOVER_NOTE,
        "invented": False,
    }


def _confidence_for(state: str, encoding: str | None = None) -> float:
    if state == "present_current":
        return 1.00 if not encoding or encoding in {"utf-8", "latin-1", "utf-8-bom"} else 0.95
    if state == "present_prior_revision":
        return 0.90
    if state in {"present_sidecar", "present_attachment"}:
        return 0.85
    if state in {"present_embedded", "present_thumbnail", "present_metadata", "present_orphan", "present_database_freelist"}:
        return 0.95
    return 1.00


def _pdf_bridge(data: bytes, filename: str, *, hosted: bool) -> dict[str, Any]:
    from spectrallock.pdfhist import recover_pdf_history

    hist = recover_pdf_history(data, hosted=hosted)
    recovered = []
    for rec in hist.get("recovered") or []:
        recovered.append({
            **rec,
            "state": "present_prior_revision" if rec.get("source_revision") in {"prior", "old-revision"} else "present_current",
            "invented": False,
        })
    return {
        "hist": hist,
        "recovered": recovered,
        "revision_graph": hist.get("revision_graph") or {"revisions": [], "edges": []},
        "metadata": hist.get("producer_artifacts") or [],
        "embedded": hist.get("attachments") or [],
        "orphans": (hist.get("orphans") or {}).get("items") if isinstance(hist.get("orphans"), dict) else [],
        "prior_content": [r for r in recovered if r.get("state") == "present_prior_revision"],
        "identifiers": hist.get("identifiers") or [],
    }


def _revision_diff(old_scan: dict[str, Any], new_scan: dict[str, Any]) -> dict[str, Any]:
    def texts(scan: dict[str, Any]) -> set[str]:
        out: set[str] = set()
        for bucket in ("hits", "metadata", "embeds"):
            for item in scan.get(bucket) or []:
                prev = (item.get("preview") or "").strip()
                if prev:
                    out.add(prev)
        return out

    a, b = texts(old_scan), texts(new_scan)
    return {
        "removed_content": sorted(a - b)[:80],
        "added_content": sorted(b - a)[:80],
        "changed_content": [],
        "covered_but_present": [t for t in sorted(a - b) if t][:40],
        "deleted_but_recoverable": [t for t in sorted(a - b) if t][:40],
        "sanitized": not (a - b) and not (old_scan.get("orphans") or new_scan.get("orphans")),
        "invented": False,
    }


def _sidecar_name_match(stem: str, other: str) -> bool:
    o = other.lower()
    s = stem.lower()
    return o.startswith(s) or s in o


def discover_sidecars(paths: Iterable[Path]) -> list[dict[str, Any]]:
    files = [Path(p) for p in paths]
    found: list[dict[str, Any]] = []
    for src in files:
        stem = src.stem
        for other in files:
            if other == src:
                continue
            suf = "".join(other.suffixes).lower() or other.suffix.lower()
            if any(other.name.lower().endswith(ext) for ext in SIDECAR_SUFFIXES) or FLAG_NAMES.search(other.name):
                if _sidecar_name_match(stem, other.name):
                    found.append({
                        "primary": src.name,
                        "sidecar": other.name,
                        "reason": "basename/suffix",
                        "invented": False,
                    })
    return found


def production_correlate(files: list[tuple[str, bytes]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    dets = [(name, detect_bytes(raw, filename=name), raw) for name, raw in files]
    for i, (na, da, ra) in enumerate(dets):
        for nb, db, rb in dets[i + 1 :]:
            reasons = []
            if da["kind"] == db["kind"]:
                reasons.append("same-kind")
            if da["sha256"] == db["sha256"]:
                reasons.append("same-sha256")
            # Bates-ish stem
            sa, sb = Path(na).stem, Path(nb).stem
            if sa[:8] and sa[:8] == sb[:8] and sa != sb:
                reasons.append("bates-stem")
            if FLAG_NAMES.search(na) or FLAG_NAMES.search(nb):
                reasons.append("flag-name")
            if reasons:
                matches.append({
                    "a": na,
                    "b": nb,
                    "reasons": reasons,
                    "invented": False,
                })
    return matches


def envelope_from_pdf_finding(find: dict[str, Any], raw: bytes, filename: str) -> dict[str, Any]:
    """Slim recover view attached onto an unredact finding (no re-parse required)."""
    graph = find.get("revision_graph") or {"revisions": [], "edges": []}
    recovered = []
    for rec in find.get("recovered") or []:
        recovered.append({
            **rec,
            "state": "present_prior_revision" if "old" in str(rec.get("recovered_from") or "") or rec.get("source_revision") == "prior" else "present_current",
        })
    return {
        "artifact": {
            "filename": filename,
            "kind": "pdf",
            "sha256": sha256_hex(raw),
            "byte_length": len(raw),
            "invented": False,
        },
        "type": "pdf",
        "revisions": (graph.get("revisions") or []),
        "prior_content": [r for r in recovered if r.get("state") == "present_prior_revision"],
        "recovered": recovered,
        "revision_graph": graph,
        "no_lie": True,
    }


def analyze_recover(
    raw: bytes,
    *,
    op: str = "locate",
    filename: str = "artifact",
    twin: bytes | None = None,
    twin_name: str = "twin",
    query: str | None = None,
    production: list[tuple[str, bytes]] | None = None,
    sidecars: list[tuple[str, bytes]] | None = None,
    hosted: bool = False,
    all_metadata: bool = False,
    scan_orphans: bool = False,
    extract_embedded: bool = False,
    cross_compare: bool = False,
    deep: bool = False,
    git_root: str | Path | None = None,
) -> dict[str, Any]:
    op_key = parse_recover_op(op)
    env = _empty_envelope(op=op_key, filename=filename)
    if not raw and not production and not git_root:
        env["refused"].append({
            "code": "SL-RECOVER-NO-BYTES",
            "note": "No supplied bytes.",
            "invented": False,
        })
        env["refuse_code"] = "SL-RECOVER-NO-BYTES"
        return env

    det = detect_bytes(raw, filename=filename) if raw else {
        "kind": None, "sha256": None, "mime": None, "status": "slot",
        "byte_length": 0, "confirmed": False, "evidence": [],
    }
    env["artifact"] = {
        "filename": filename,
        "kind": det.get("kind"),
        "mime": det.get("mime"),
        "status": det.get("status"),
        "status_note": det.get("status_note"),
        "confirmed": det.get("confirmed"),
        "evidence": det.get("evidence"),
        "sha256": det.get("sha256"),
        "byte_length": det.get("byte_length") or len(raw or b""),
        "invented": False,
    }
    env["type"] = det.get("kind")
    env["format_status"] = det.get("status")

    if det.get("status") == "slot":
        env["refused"].append({
            "code": "SL-RECOVER-UNSUPPORTED",
            "note": det.get("status_note") or "Parser unbound (SLOT).",
            "invented": False,
        })
        env["refuse_code"] = "SL-RECOVER-UNSUPPORTED"
        env["warnings"].append("SLOT: parser not bound. Not advertised as LIVE.")
        if raw:
            env["carved"] = carve_signatures(raw, container=str(det.get("kind")))
        if op_key == "refuse":
            return env

    scan = scan_bytes(raw, filename=filename, hosted=hosted) if raw else {
        "hits": [], "metadata": [], "embeds": [], "secrets": [], "orphans": [],
        "thumbs": [], "carved": [], "detect": det,
    }
    pdf_extra = None
    if det.get("kind") == "pdf" and raw:
        pdf_extra = _pdf_bridge(raw, filename, hosted=hosted)
        env["revision_graph"] = pdf_extra["revision_graph"]
        env["revisions"] = (pdf_extra["revision_graph"] or {}).get("revisions") or []
        env["pdf_history"] = {
            "leftover_bytes": pdf_extra["hist"].get("leftover_bytes"),
            "recovered_from": pdf_extra["hist"].get("recovered_from"),
            "classifications": pdf_extra["hist"].get("classifications"),
            "invented": False,
        }

    env["metadata"].extend(scan.get("metadata") or [])
    env["embedded"].extend(scan.get("embeds") or [])
    env["embedded"].extend(scan.get("thumbs") or [])
    env["orphans"].extend(scan.get("orphans") or [])
    env["carved"].extend(scan.get("carved") or [])
    env["secrets"].extend(scan.get("secrets") or [])
    if pdf_extra:
        env["embedded"].extend(pdf_extra.get("embedded") or [])
        env["orphans"].extend(pdf_extra.get("orphans") or [])

    recovered = []
    for bucket, default_state in (
        (scan.get("hits") or [], "present_current"),
        (scan.get("thumbs") or [], "present_thumbnail"),
        (scan.get("carved") or [], "present_orphan"),
        (pdf_extra["recovered"] if pdf_extra else [], "present_prior_revision"),
    ):
        if isinstance(bucket, dict):
            continue
        for item in bucket:
            if not isinstance(item, dict):
                continue
            rec = dict(item)
            rec.setdefault("state", default_state if default_state != [] else "present_current")
            rec["invented"] = False
            recovered.append(rec)
    if pdf_extra:
        recovered.extend(pdf_extra["recovered"])

    # de-dup recovered by preview+path+kind
    seen: set[tuple[Any, ...]] = set()
    uniq = []
    for rec in recovered:
        key = (rec.get("kind"), rec.get("path"), rec.get("preview"), rec.get("offset"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(rec)
    recovered = uniq
    env["recovered"] = recovered
    env["prior_content"] = [r for r in recovered if r.get("state") in {
        "present_prior_revision", "present_orphan", "present_database_freelist",
        "present_thumbnail", "present_embedded",
    }]

    for rec in recovered[:200]:
        env["provenance"].append(ledger(
            file_sha256=det.get("sha256") or sha256_hex(raw or b""),
            container=str(det.get("kind")),
            path=str(rec.get("path") or filename),
            artifact_id=str(rec.get("kind") or "item"),
            method=str(rec.get("kind") or "scan"),
            offset=rec.get("offset"),
            state=str(rec.get("state") or "present_current"),
            revision_id=rec.get("source_revision"),
            object_id=rec.get("object_id"),
            confidence=_confidence_for(str(rec.get("state") or "present_current")),
        ))

    if twin:
        twin_scan = scan_bytes(twin, filename=twin_name, hosted=hosted)
        env["cross_compare"] = _revision_diff(scan, twin_scan)
        env["revision_diff"] = env["cross_compare"]
        if det.get("kind") == "pdf":
            from spectrallock.pdfhist import twin_compare_pdfs

            env["twin_diff"] = twin_compare_pdfs(raw, twin)
        cross_compare = True

    if production:
        env["cross_file_matches"].extend(production_correlate([(filename, raw), *production] if raw else list(production)))
        side_paths = [Path(filename)]
        payloads: dict[str, bytes] = {filename: raw} if raw else {}
        for name, blob in production:
            payloads[name] = blob
            side_paths.append(Path(name))
            other = detect_bytes(blob, filename=name)
            if other.get("sha256") == det.get("sha256") and name != filename:
                env["cross_file_matches"].append({
                    "a": filename, "b": name, "reasons": ["same-sha256"], "invented": False,
                })
        env["sidecars"] = discover_sidecars(side_paths)

    if sidecars:
        env.setdefault("sidecars", [])
        for name, blob in sidecars:
            env["sidecars"].append({"primary": filename, "sidecar": name, "reason": "supplied", "invented": False})
            extra = scan_bytes(blob, filename=name, hosted=hosted)
            env["embedded"].extend(extra.get("hits") or [])
            env["metadata"].extend(extra.get("metadata") or [])

    if git_root:
        env["git"] = scan_git(Path(git_root))
        env["recovered"].extend(env["git"].get("hits") or [])

    if query:
        q = query.lower()
        env["query_hits"] = [
            r for r in recovered
            if q in str(r.get("preview") or "").lower() or q in str(r.get("path") or "").lower()
        ]

    # Redaction-region sketch from PDF classifications + office hidden
    regions = []
    if pdf_extra:
        for cls in (pdf_extra["hist"].get("classifications") or []):
            regions.append({
                "page": cls.get("page"),
                "covering_kind": cls.get("class"),
                "prior_revisions": bool(cls.get("leftover")),
                "recovery_route": "old-revision" if cls.get("leftover") else None,
                "invented": False,
            })
    for rec in recovered:
        if rec.get("kind") in {"tracked-deletion", "ooxml-hidden-or-deleted", "hidden-css", "rtf-hidden", "json-tombstone"}:
            regions.append({
                "path": rec.get("path"),
                "covering_kind": rec.get("kind"),
                "prior_revisions": rec.get("state") == "present_prior_revision",
                "recovery_route": rec.get("kind"),
                "preview": rec.get("preview"),
                "invented": False,
            })
    env["redaction_regions"] = regions

    leftover = bool(recovered) or bool(env["prior_content"]) or bool(env["carved"])
    sanitized = det.get("kind") == "pdf" and pdf_extra and not pdf_extra["hist"].get("leftover_bytes") and not leftover
    if det.get("kind") == "pdf" and pdf_extra and not pdf_extra["hist"].get("leftover_bytes") and not env["prior_content"]:
        # visual path compat — only when recover asked to refuse
        if op_key in {"refuse", "deep-recover", "locate"} and not leftover:
            sanitized = True

    if op_key == "refuse":
        if leftover:
            env["note"] = "Refuse requested but leftover/present bytes exist. Reported, not invented."
        else:
            env["refuse_code"] = "SL-RECOVER-SANITIZED" if sanitized else "SL-RECOVER-NO-BYTES"
            env["refused"].append({"code": env["refuse_code"], "invented": False})
            env["stop"] = True
        return env

    if op_key == "revision-graph":
        if det.get("kind") != "pdf":
            env["revision_graph"] = {
                "revisions": [{"index": 0, "copy": None, "note": "single supplied blob; no incremental xref chain", "invented": False}],
                "edges": [],
                "invented": False,
            }
            if env.get("git"):
                env["revision_graph"]["source"] = "git-supplied"
        env["op"] = "revision-graph"
        return env

    if op_key == "extract-embedded" or extract_embedded:
        env["recovered"] = [r for r in recovered if r.get("state") in {
            "present_embedded", "present_attachment", "present_thumbnail",
        }] or env["embedded"]
        env["op"] = "extract-embedded"

    if op_key == "scan-orphans" or scan_orphans:
        env["recovered"] = env["orphans"] + env["carved"]
        env["op"] = "scan-orphans" if op_key == "scan-orphans" else env["op"]

    if op_key == "scan-metadata" or all_metadata:
        if op_key == "scan-metadata":
            env["recovered"] = env["metadata"]
        env["op"] = "scan-metadata" if op_key == "scan-metadata" else env["op"]

    if op_key == "scan-sidecars":
        env["recovered"] = env.get("sidecars") or []
        if not env["recovered"]:
            env["warnings"].append("No sidecars supplied. Use --production-dir or extra files.")
        env["op"] = "scan-sidecars"

    if op_key == "scan-history":
        env["recovered"] = env["prior_content"]
        env["op"] = "scan-history"

    if op_key == "cross-compare":
        if not twin and not production:
            env["warnings"].append("cross-compare needs --twin or a second file.")
        env["op"] = "cross-compare"

    if op_key == "deep-recover" or deep:
        env["op"] = "deep-recover"
        env["deep"] = True

    if hosted:
        for rev in env.get("revisions") or []:
            copy = rev.get("copy") if isinstance(rev, dict) else None
            if isinstance(copy, dict) and copy.get("b64") and (copy.get("byte_length") or 0) > HOSTED_COPY_MAX:
                copy["b64"] = None
                copy["omitted"] = "hosted-preview-cap"
                copy["invented"] = False

    if not leftover and op_key in {"deep-recover", "locate"}:
        if det.get("status") == "slot":
            env["refuse_code"] = env.get("refuse_code") or "SL-RECOVER-UNSUPPORTED"
        elif sanitized:
            env["refuse_code"] = "SL-RECOVER-SANITIZED"
            env["refused"].append({"code": "SL-RECOVER-SANITIZED", "invented": False})
        elif not recovered:
            env["refuse_code"] = "SL-RECOVER-NO-BYTES"
            env["refused"].append({
                "code": "SL-RECOVER-NO-BYTES",
                "note": "No leftover / historical / embedded / metadata bytes were present.",
                "invented": False,
            })

    env["recovered_count"] = len(env["recovered"])
    env["secret_material_present"] = bool(env["secrets"])
    return env


def analyze_recover_path(
    path: str | Path | None = None,
    *,
    op: str = "locate",
    twin: str | Path | None = None,
    query: str | None = None,
    production_dir: str | Path | None = None,
    production: list[str | Path] | None = None,
    recursive: bool = False,
    hosted: bool = False,
    all_metadata: bool = False,
    scan_orphans: bool = False,
    extract_embedded: bool = False,
    cross_compare: bool = False,
    deep: bool = False,
) -> dict[str, Any]:
    src = Path(path) if path else None
    raw = b""
    filename = src.name if src else "artifact"
    git_root = None
    if src and src.exists():
        if src.is_dir():
            if (src / ".git").exists() or src.name == ".git":
                git_root = src
            if production_dir is None:
                production_dir = src
        else:
            raw = src.read_bytes()
            if src.parent.joinpath(".git").exists():
                git_root = src.parent

    prod: list[tuple[str, bytes]] = []
    sidecar_blobs: list[tuple[str, bytes]] = []
    extra_paths: list[Path] = []
    if production:
        for item in production:
            p = Path(item)
            extra_paths.append(p)
            prod.append((p.name, p.read_bytes()))
    if production_dir:
        root = Path(production_dir)
        walker = root.rglob("*") if recursive else root.glob("*")
        for p in walker:
            if not p.is_file():
                continue
            if src and p.resolve() == src.resolve():
                continue
            blob = p.read_bytes()
            rel = str(p.relative_to(root)) if recursive else p.name
            prod.append((rel, blob))
            extra_paths.append(p)
            if any(p.name.lower().endswith(ext) for ext in SIDECAR_SUFFIXES):
                sidecar_blobs.append((rel, blob))

    twin_bytes = Path(twin).read_bytes() if twin else None
    twin_name = Path(twin).name if twin else "twin"
    return analyze_recover(
        raw,
        op=op,
        filename=filename,
        twin=twin_bytes,
        twin_name=twin_name,
        query=query,
        production=prod or None,
        sidecars=sidecar_blobs or None,
        hosted=hosted,
        all_metadata=all_metadata,
        scan_orphans=scan_orphans,
        extract_embedded=extract_embedded,
        cross_compare=cross_compare,
        deep=deep,
        git_root=git_root,
    )
