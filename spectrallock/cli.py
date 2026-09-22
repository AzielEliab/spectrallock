"""Command-line interface for SpectralLock.

    spectrallock version
    spectrallock modes
    spectrallock lenses
    spectrallock doctor
    spectrallock overlay --mode|--lens zero|tazel|vyrn|uv|rosetta|zen|chaos|balance|candle|indent|lemon
                         --target ink|page --inject|--no-inject IN.png OUT.png
    spectrallock overlay --verify --sidecar
    spectrallock inject  # operator-card CLI (also spectrallock_inject.py)
    spectrallock unredact locate|lift|recover FILE
    spectrallock recover locate|deep|compare|revision-graph FILE
    spectrallock handwriting analyze|compare|graph FILE
    spectrallock pigment restore|estimate|refuse FILE
    spectrallock restore-pigment FILE
    spectrallock lift FILE          # alias: non-opaque residual, leftover recover
    spectrallock redact-locate FILE # alias: locate
    spectrallock ui
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from spectrallock import (
    LIMITATION,
    __version__,
    list_lenses,
    list_modes,
    list_targets,
    list_unredact,
)
from spectrallock.handwriting import list_handwriting
from spectrallock.pigment import list_pigment, pigment_mode_card
from spectrallock.recover import list_recover
from spectrallock.debug import debug
from spectrallock.engine import (
    LIVE_MODES,
    PLAIN_NOT_IMAGE,
    analyze,
    load_rgb,
    make_receipt,
    png_bytes,
    resolve_mode,
    sha256_hex,
    write_sidecar,
)


def _overlay_mode(name: str) -> str:
    key = str(name or "").strip().lower().replace("_", "-")
    if key in {"pigment", "restore-pigment", "lost-pigment", "restore-lost-pigment"}:
        return "pigment"
    return resolve_mode(name)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spectrallock",
        description=(
            "SpectralLock — Rosetta spectral analysis (Aziel Eliab, 2026). "
            "Same SpectralLock lenses as Aziel Corpus Library OCR: overlays "
            "plus ink/page targets. "
            f"Local UI: `spectrallock ui` at http://127.0.0.1:8861. {LIMITATION}"
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")
    sub.add_parser(
        "doctor",
        help="Check Python, Pillow, numpy, live lenses × ink/page, no NaN, loopback, no telemetry.",
    )

    p_modes = sub.add_parser("modes", help="List SpectralLock lenses (live papers + ids).")
    p_modes.add_argument("--json", action="store_true", dest="as_json", help="JSON list.")
    p_lenses = sub.add_parser("lenses", help="Alias for modes — Corpus OCR lens names.")
    p_lenses.add_argument("--json", action="store_true", dest="as_json", help="JSON list.")

    p_ov = sub.add_parser("overlay", help="Apply Rosetta spectral analysis. PNG/JPEG in, PNG out.")
    p_ov.add_argument(
        "--mode",
        "--lens",
        dest="mode",
        required=True,
        type=_overlay_mode,
        metavar="MODE",
        help=(
            "SpectralLock lens id or alias "
            "(zero|tazel|vyrn|uv|rosetta|zen|chaos|balance|candle|indent|lemon) "
            "or pigment / restore-pigment."
        ),
    )
    p_ov.add_argument(
        "--target",
        default="ink",
        choices=["ink", "page"],
        help="Ink isolates writing; page isolates parchment. Default ink.",
    )
    p_ov.add_argument("src", metavar="IN", help="Input photograph (PNG or JPEG).")
    p_ov.add_argument("dst", metavar="OUT", help="Output overlay PNG.")
    p_ov.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print metadata JSON (mode, hashes, sizes) after writing the image.",
    )
    p_ov.add_argument(
        "--verify",
        action="store_true",
        help="Print a receipt: mode, paper, sha256 in/out, size.",
    )
    p_ov.add_argument(
        "--sidecar",
        action="store_true",
        help="Write a JSON sidecar next to OUT (mode, hashes, limitation).",
    )
    inj = p_ov.add_mutually_exclusive_group()
    inj.add_argument(
        "--inject",
        dest="inject",
        action="store_true",
        help="False-color membership tint (paint). Not recovered pigment. Default.",
    )
    inj.add_argument(
        "--no-inject",
        dest="inject",
        action="store_false",
        help="Luminance of the same gate (gray). Zero ignores the switch.",
    )
    p_ov.set_defaults(inject=None)
    p_ov.add_argument(
        "--no-tint",
        action="store_true",
        help="Alias for --no-inject. Composites and all modes as gray of the same gate.",
    )

    p_inj = sub.add_parser(
        "inject",
        help="Color inject switch (operator card). Same as spectrallock_inject.py.",
    )
    p_inj.add_argument("rest", nargs=argparse.REMAINDER, help="Arguments for spectrallock_inject.py")

    p_ui = sub.add_parser("ui", help="Serve the local overlay UI on 127.0.0.1.")
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8861, help="Port (default 8861).")

    p_serve = sub.add_parser("serve", help="Alias for ui. Bind 127.0.0.1 only.")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8861)

    def _add_unredact_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "src",
            metavar="IN",
            help="PDF / PNG / JPEG the operator owns.",
        )
        p.add_argument(
            "--twin",
            default=None,
            help="Same page issued twice (less redacted). Residual compare only.",
        )
        p.add_argument(
            "--query",
            default=None,
            help="Cite this name if it appears elsewhere in --set / the file. Do not invent.",
        )
        p.add_argument(
            "--set",
            dest="production",
            action="append",
            default=[],
            help="Other files in the same production. Repeatable.",
        )
        p.add_argument(
            "-o",
            "--output",
            dest="output",
            default=None,
            help="Optional residual PNG (inject OFF). Never a transcript.",
        )
        p.add_argument("--json", action="store_true", dest="as_json", help="Print findings JSON.")
        inj = p.add_mutually_exclusive_group()
        inj.add_argument(
            "--inject",
            dest="inject",
            action="store_true",
            help="Ignored. Lift-overlay forces inject OFF (gray of the same gate).",
        )
        inj.add_argument(
            "--no-inject",
            dest="inject",
            action="store_false",
            help="Gray of the same gate (required honesty for residual).",
        )
        p.set_defaults(inject=False)

    p_un = sub.add_parser(
        "unredact",
        help="Honest locate / leftover-bytes recover / non-opaque lift. No guessed letters.",
    )
    p_un.add_argument(
        "op_or_src",
        help="Op (locate|lift|recover|refuse) or the input file if op is omitted.",
    )
    p_un.add_argument(
        "src_opt",
        nargs="?",
        default=None,
        help="Input file when the first token is an op.",
    )
    p_un.add_argument(
        "--twin",
        default=None,
        help="Same page issued twice (less redacted). Residual compare only.",
    )
    p_un.add_argument(
        "--query",
        default=None,
        help="Cite this name if it appears elsewhere in --set / the file. Do not invent.",
    )
    p_un.add_argument(
        "--set",
        dest="production",
        action="append",
        default=[],
        help="Other files in the same production. Repeatable.",
    )
    p_un.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Optional residual PNG (inject OFF). Never a transcript.",
    )
    p_un.add_argument("--json", action="store_true", dest="as_json", help="Print findings JSON.")
    un_inj = p_un.add_mutually_exclusive_group()
    un_inj.add_argument(
        "--inject",
        dest="inject",
        action="store_true",
        help="Ignored. Lift-overlay forces inject OFF (gray of the same gate).",
    )
    un_inj.add_argument(
        "--no-inject",
        dest="inject",
        action="store_false",
        help="Gray of the same gate (required honesty for residual).",
    )
    p_un.set_defaults(inject=False)

    p_lift = sub.add_parser(
        "lift",
        help="Alias for unredact lift. Non-opaque residual only; leftover bytes may recover.",
    )
    _add_unredact_args(p_lift)

    p_loc = sub.add_parser(
        "redact-locate",
        help="Alias for unredact locate. Report leftover bytes and text still in the file.",
    )
    _add_unredact_args(p_loc)

    p_rec = sub.add_parser(
        "recover",
        help="Universal artifact recovery. Present bytes only. Never invent letters.",
    )
    p_rec.add_argument(
        "op_or_src",
        help="Op (locate|deep|revision-graph|compare|…) or the input file if op is omitted.",
    )
    p_rec.add_argument(
        "src_opt",
        nargs="?",
        default=None,
        help="Input file when the first token is an op. Second file for compare.",
    )
    p_rec.add_argument(
        "src_opt2",
        nargs="?",
        default=None,
        help="New file for recover compare OLD NEW.",
    )
    p_rec.add_argument("--twin", default=None, help="Second artifact for cross-compare.")
    p_rec.add_argument("--query", default=None, help="Cite this string if present. Do not invent.")
    p_rec.add_argument(
        "--production-dir",
        default=None,
        help="Directory of sibling/production files.",
    )
    p_rec.add_argument(
        "--set",
        dest="production",
        action="append",
        default=[],
        help="Other files in the same production. Repeatable.",
    )
    p_rec.add_argument("--recursive", action="store_true", help="Walk --production-dir recursively.")
    p_rec.add_argument("--all-metadata", action="store_true", help="Include metadata sweep.")
    p_rec.add_argument("--scan-orphans", action="store_true", help="Surface orphans / carved leftovers.")
    p_rec.add_argument("--extract-embedded", action="store_true", help="Prefer embedded/attachment copies.")
    p_rec.add_argument("--cross-compare", action="store_true", help="Compare twin / second file.")
    p_rec.add_argument("--deep", action="store_true", help="Deep recover (all present representations).")
    p_rec.add_argument("--json", action="store_true", dest="as_json", help="Print recover JSON.")

    def _add_hand_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "op_or_src",
            help="Op (analyze|compare|side-by-side|graph|forgery-indicators|refuse) or the scan.",
        )
        p.add_argument("src_opt", nargs="?", default=None, help="Scan when the first token is an op.")
        p.add_argument("src_opt2", nargs="?", default=None, help="Known sample for compare.")
        p.add_argument("--twin", default=None, help="Known / second scan for compare or side-by-side.")
        p.add_argument("--json", action="store_true", dest="as_json", help="Print handwriting JSON.")

    for alias, help_txt in (
        ("handwriting", "Handwriting / ink-on-paper scan heuristics. Not a lab. Not a court finding."),
        ("handwrite", "Alias for handwriting."),
        ("ink-hand", "Alias for handwriting."),
        ("forgery-scan", "Alias for handwriting forgery-indicators."),
    ):
        ph = sub.add_parser(alias, help=help_txt)
        _add_hand_args(ph)

    def _add_pigment_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "op_or_src",
            help="Op (restore|estimate|refuse) or the photograph if op is omitted.",
        )
        p.add_argument("src_opt", nargs="?", default=None, help="Photograph when the first token is an op.")
        p.add_argument("-o", "--output", dest="output", default=None, help="Restored PNG when evidence remains.")
        p.add_argument("--json", action="store_true", dest="as_json", help="Print pigment JSON.")
        inj = p.add_mutually_exclusive_group()
        inj.add_argument("--inject", dest="inject", action="store_true", help="Keep the pigment's own residual color. Default.")
        inj.add_argument("--no-inject", dest="inject", action="store_false", help="Gray of the restored gate.")
        p.set_defaults(inject=True)

    for alias, help_txt in (
        ("pigment", "Restore lost pigment from supported pixel evidence. Refuses SL-PIGMENT-GONE when the signal is gone."),
        ("restore-pigment", "Alias for pigment restore."),
    ):
        pp = sub.add_parser(alias, help=help_txt)
        _add_pigment_args(pp)

    return parser


def _run_doctor() -> int:
    import numpy as np

    lines: list[str] = []
    ok = True
    lines.append(f"spectrallock {__version__}")
    lines.append(f"python {sys.version.split()[0]}")
    try:
        import numpy as np  # noqa: F401
        import PIL

        lines.append(f"numpy {np.__version__}")
        lines.append(f"Pillow {PIL.__version__}")
    except Exception as exc:  # noqa: BLE001
        ok = False
        lines.append(f"imports: fail ({type(exc).__name__})")
        debug(f"doctor import fail type={type(exc).__name__}")

    from spectrallock.engine import synthetic_page
    from spectrallock.ui import LOOPBACK

    page = synthetic_page(32, 32)
    from spectrallock.engine import is_achromatic

    for mode in LIVE_MODES:
        for target in ("ink", "page"):
            try:
                result = analyze(page, mode, target=target)
                finite = bool(np.isfinite(result.rgb).all())
                if not finite or result.rgb.shape != (32, 32, 3) or result.target != target:
                    ok = False
                    lines.append(f"lens {mode} {target}: fail")
                    debug(f"doctor lens={mode} target={target} finite={finite} shape={result.rgb.shape}")
                else:
                    lines.append(f"lens {mode} {target}: ok ({result.paper})")
            except Exception as exc:  # noqa: BLE001
                ok = False
                lines.append(f"lens {mode} {target}: fail")
                debug(f"doctor lens={mode} target={target} error={type(exc).__name__}")
        try:
            on = analyze(page, mode, target="ink", inject=True)
            off = analyze(page, mode, target="ink", inject=False)
            if "tazel_inband_pct" not in on.to_meta() or "vyrn_inband_pct" not in on.to_meta():
                ok = False
                lines.append(f"inject {mode}: fail (inband)")
            elif mode == "zero":
                same = bool(np.allclose(on.rgb, off.rgb, atol=1e-5))
                gray = is_achromatic(on.rgb) and is_achromatic(off.rgb)
                if not same or not gray or on.inject_applied or off.inject_applied:
                    ok = False
                    lines.append("inject zero ignore: fail")
                else:
                    lines.append("inject zero ignore: ok")
            elif not is_achromatic(off.rgb):
                ok = False
                lines.append(f"inject {mode} off: fail (not gray)")
            else:
                lines.append(f"inject {mode} on/off: ok")
        except Exception as exc:  # noqa: BLE001
            ok = False
            lines.append(f"inject {mode}: fail")
            debug(f"doctor inject mode={mode} error={type(exc).__name__}")

    if "127.0.0.1" not in LOOPBACK:
        ok = False
        lines.append("loopback: fail")
    else:
        lines.append("loopback: 127.0.0.1 only")
    from spectrallock.unredact import (
        REFUSE_OPAQUE,
        analyze_unredact,
        residual_enhance,
    )
    from spectrallock.engine import png_bytes

    cream = np.ones((32, 48, 3), dtype=np.float32) * 0.92
    cream[8:22, 6:42] = 0.0
    opaque_png = png_bytes(cream)
    ghost = np.ones((32, 48, 3), dtype=np.float32) * 0.90
    yy, xx = np.indices((32, 48))
    ghost[8:22, 6:42] = (0.22 + 0.18 * ((xx[8:22, 6:42] % 7) / 7.0))[..., None]
    residual_png = png_bytes(ghost)
    try:
        refused = analyze_unredact(opaque_png, op="lift")
        leftover_empty = analyze_unredact(opaque_png, op="recover")
        lifted = analyze_unredact(residual_png, op="lift")
        if refused.get("refuse_code") != REFUSE_OPAQUE or leftover_empty.get("leftover_bytes"):
            ok = False
            lines.append("unredact opaque refuse: fail")
        elif not lifted.get("residual_usable") or not lifted.get("residual_png_b64"):
            ok = False
            lines.append("unredact residual lift: fail")
        else:
            lines.append("unredact opaque refuse: ok")
            lines.append("unredact residual lift: ok")
            enhanced = residual_enhance(ghost)
            if not np.isfinite(enhanced).all():
                ok = False
                lines.append("unredact residual finite: fail")
    except Exception as exc:  # noqa: BLE001
        ok = False
        lines.append("unredact doctor: fail")
        debug(f"doctor unredact error={type(exc).__name__}")

    try:
        from spectrallock.recover import analyze_recover, list_recover

        card = list_recover()
        tomb = analyze_recover(b'{"_deleted":{"name":"ALICE"}}', op="locate", filename="t.json")
        if not card.get("no_lie") or card.get("guessed_letters") or "7z" not in (card.get("slot_kinds") or []):
            ok = False
            lines.append("recover card: fail")
        elif not any(r.get("kind") == "json-tombstone" for r in tomb.get("recovered") or []):
            ok = False
            lines.append("recover json tombstone: fail")
        else:
            lines.append("recover family: ok")
    except Exception as exc:  # noqa: BLE001
        ok = False
        lines.append("recover doctor: fail")
        debug(f"doctor recover error={type(exc).__name__}")

    try:
        from spectrallock.handwriting import REFUSE_NO_INK, analyze_handwriting, list_handwriting

        card = list_handwriting()
        ink_page = np.ones((32, 48, 3), dtype=np.float32) * 0.92
        ink_page[12:20, 6:40] = 0.08
        inked = analyze_handwriting(png_bytes(ink_page), op="analyze", filename="doc.png")
        blank = analyze_handwriting(png_bytes(np.ones((24, 24, 3), dtype=np.float32) * 0.92), op="analyze")
        if (
            not card.get("no_lie")
            or card.get("esda")
            or card.get("writer_identification_as_fact")
            or card.get("forensic_certification")
        ):
            ok = False
            lines.append("handwriting card: fail")
        elif inked.get("refuse_code") == REFUSE_NO_INK or not (inked.get("features") or {}).get("weight"):
            ok = False
            lines.append("handwriting ink: fail")
        elif blank.get("refuse_code") != REFUSE_NO_INK:
            ok = False
            lines.append("handwriting no-ink: fail")
        else:
            lines.append("handwriting family: ok")
    except Exception as exc:  # noqa: BLE001
        ok = False
        lines.append("handwriting doctor: fail")
        debug(f"doctor handwriting error={type(exc).__name__}")

    try:
        from spectrallock.pigment import REFUSE_GONE, analyze_pigment

        card = list_pigment()
        faded = synthetic_page(96, 96)
        blank = np.ones((32, 32, 3), dtype=np.float32)
        blank[:] = (0.93, 0.88, 0.76)
        hit = analyze_pigment(faded, op="restore")
        gone = analyze_pigment(blank, op="restore")
        if card.get("status") != "live" or card.get("refuse_code") != REFUSE_GONE or card.get("invented_marks"):
            ok = False
            lines.append("pigment card: fail")
        elif not hit.get("pigment_recovery") or not hit.get("recovered") or hit.get("invented_marks"):
            ok = False
            lines.append("pigment evidence: fail")
        elif gone.get("pigment_recovery") is not True or gone.get("recovered") or gone.get("refuse_code") != REFUSE_GONE:
            ok = False
            lines.append("pigment gone: fail")
        elif gone.get("png_b64"):
            ok = False
            lines.append("pigment gone image: fail")
        else:
            lines.append("pigment restore: ok")
    except Exception as exc:  # noqa: BLE001
        ok = False
        lines.append("pigment doctor: fail")
        debug(f"doctor pigment error={type(exc).__name__}")

    lines.append("telemetry: none")
    lines.append("ok" if ok else "fail")
    print("\n".join(lines))
    debug(f"doctor ok={ok} modes={len(LIVE_MODES)}")
    return 0 if ok else 1


def _print_receipt(rec: dict) -> None:
    print(f"mode: {rec['mode']}")
    print(f"lenses: {','.join(rec.get('lenses') or [rec['mode']])}")
    print(f"target: {rec.get('target', 'ink')}")
    print(f"paper: {rec['paper']}")
    print(f"inject: {str(rec.get('inject', True)).lower()}")
    print(f"inject_applied: {str(rec.get('inject_applied', rec.get('inject', True))).lower()}")
    print(f"tazel_inband_pct: {float(rec.get('tazel_inband_pct', 0.0)):.2f}")
    print(f"vyrn_inband_pct: {float(rec.get('vyrn_inband_pct', 0.0)):.2f}")
    print(f"sha256_in: {rec['sha256_in']}")
    print(f"sha256_out: {rec['sha256_out']}")
    print(f"size_in: {rec['size_in']}")
    print(f"size_out: {rec['size_out']}")
    print(LIMITATION)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "version":
        print(f"spectrallock {__version__}")
        return 0

    if args.cmd == "doctor":
        return _run_doctor()

    if args.cmd in {"modes", "lenses"}:
        rows = list_lenses() if args.cmd == "lenses" else list_modes()
        mode_rows = list(rows)
        if args.cmd == "modes":
            mode_rows = mode_rows + [pigment_mode_card()]
        if args.as_json:
            print(json.dumps({
                "product": "spectrallock",
                "version": __version__,
                "author": "Aziel Eliab",
                "rosetta_spectral_analysis": True,
                "corpus_ocr_aligned": True,
                "advisory": LIMITATION,
                "modes": mode_rows,
                "lenses": list_lenses(),
                "targets": list_targets(),
                "unredact": list_unredact(),
                "recover": list_recover(),
                "handwriting": list_handwriting(),
                "pigment": list_pigment(),
                "live_modes": [row["id"] for row in mode_rows],
            }, indent=2))
        else:
            print(LIMITATION)
            print(f"{'id':10} {'paper':10} {'status':8} summary")
            for row in mode_rows:
                print(f"{row['id']:10} {row['paper']:10} {row['status']:8} {row['summary']}")
            print("targets: ink (writing) · page (parchment)")
            print("unredact family: locate · lift · recover · refuse (leftover bytes only)")
            print("recover family: locate · deep-recover · revision-graph · cross-compare · extract-embedded · scan-orphans · scan-metadata · scan-sidecars · scan-history · refuse")
            print("handwriting family: analyze · compare · side-by-side · graph · forgery-indicators · refuse (synthetic scan heuristics)")
            print("pigment family: restore · estimate · refuse (LIVE restore lost pigment; SL-PIGMENT-GONE when the signal is gone)")
        return 0

    if args.cmd == "overlay":
        src = Path(args.src)
        try:
            src_bytes = src.read_bytes()
        except FileNotFoundError:
            print(f"input not found: {args.src}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001
            debug(f"overlay read type={type(exc).__name__}")
            print(PLAIN_NOT_IMAGE, file=sys.stderr)
            return 2
        try:
            rgb = load_rgb(args.src)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001
            debug(f"overlay decode type={type(exc).__name__}")
            print(PLAIN_NOT_IMAGE, file=sys.stderr)
            return 2
        inject = False if args.no_tint else (True if args.inject is None else bool(args.inject))
        if args.mode == "pigment":
            from spectrallock.pigment import REFUSE_GONE, analyze_pigment

            finding = analyze_pigment(rgb, op="restore", inject=inject, filename=src.name, source_bytes=src_bytes)
            if finding.get("png_b64"):
                import base64

                Path(args.dst).write_bytes(base64.b64decode(finding["png_b64"]))
                finding["dst"] = args.dst
            if args.as_json:
                print(json.dumps(finding, indent=2))
            else:
                print(f"op: {finding.get('op')}")
                print(f"pigment_recovery: {str(finding.get('pigment_recovery')).lower()}")
                print(f"recovered: {str(finding.get('recovered')).lower()}")
                print(f"refuse_code: {finding.get('refuse_code') or 'none'}")
                print(f"evidence_pixels: {finding.get('evidence_pixels')}")
            if finding.get("refuse_code") == REFUSE_GONE and not finding.get("recovered"):
                return 2
            return 0
        try:
            result = analyze(rgb, args.mode, target=args.target, inject=inject)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        out_bytes = png_bytes(result.rgb)
        Path(args.dst).write_bytes(out_bytes)
        rec = make_receipt(
            mode=result.mode,
            paper=result.paper,
            sha256_in=sha256_hex(src_bytes),
            sha256_out=sha256_hex(out_bytes),
            size_in=len(src_bytes),
            size_out=len(out_bytes),
            width=result.width,
            height=result.height,
            target=result.target,
            lenses=result.lenses,
            inject=inject,
            inject_applied=result.inject_applied,
            tazel_inband_pct=result.tazel_inband_pct,
            vyrn_inband_pct=result.vyrn_inband_pct,
        )
        debug(
            f"overlay mode={result.mode} target={result.target} paper={result.paper} "
            f"size_in={rec['size_in']} size_out={rec['size_out']} "
            f"sha256_in={rec['sha256_in']} sha256_out={rec['sha256_out']}"
        )
        meta = result.to_meta()
        meta["src"] = args.src
        meta["dst"] = args.dst
        meta.update({k: rec[k] for k in (
            "sha256_in", "sha256_out", "size_in", "size_out", "limitation",
        )})
        if args.sidecar:
            write_sidecar(args.dst, rec)
        if args.as_json:
            print(json.dumps(meta, indent=2))
        elif args.verify:
            _print_receipt(rec)
        else:
            print(
                f"{result.mode} {result.target} {result.paper} {result.width}x{result.height} "
                f"com=({result.com[0]:.1f},{result.com[1]:.1f}) -> {args.dst}"
            )
            print(LIMITATION)
        return 0

    if args.cmd == "inject":
        from spectrallock.inject import main as inject_main

        rest = list(args.rest or [])
        if rest and rest[0] == "--":
            rest = rest[1:]
        return inject_main(rest)

    if args.cmd in {"ui", "serve"}:
        from spectrallock.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    if args.cmd in {"unredact", "lift", "redact-locate"}:
        from spectrallock.unredact import (
            REFUSE_OPAQUE,
            UNREDACT_NOTE,
            analyze_unredact_path,
            parse_unredact_op,
        )

        if args.cmd == "unredact":
            token = str(args.op_or_src)
            known = {"locate", "lift", "recover", "refuse", "leftover", "leftover-bytes",
                     "lift-overlay", "redact-locate", "unredact"}
            if token.lower() in known:
                op = token
                src = args.src_opt
                if not src:
                    print("unredact: missing input file", file=sys.stderr)
                    return 2
            else:
                op = "locate"
                src = token
        elif args.cmd == "lift":
            op = "lift"
            src = args.src
        else:
            op = "locate"
            src = args.src
        try:
            parse_unredact_op(op)
            finding = analyze_unredact_path(
                src,
                op=op,
                twin=args.twin,
                query=args.query,
                production=args.production or None,
                inject=False,
            )
        except FileNotFoundError:
            print(f"input not found: {src}", file=sys.stderr)
            return 2
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        residual_b64 = finding.get("residual_png_b64")
        if args.output and residual_b64:
            import base64

            Path(args.output).write_bytes(base64.b64decode(residual_b64))
            finding["dst"] = args.output
        if args.as_json:
            print(json.dumps(finding, indent=2, ensure_ascii=False))
        else:
            print(f"op: {finding.get('op')}")
            print(f"opaque_replace: {str(finding.get('opaque_replace')).lower()}")
            print(f"residual_usable: {str(finding.get('residual_usable')).lower()}")
            print(f"leftover_bytes: {str(finding.get('leftover_bytes')).lower()}")
            print(f"refuse_code: {finding.get('refuse_code') or 'none'}")
            recovered_from = finding.get("recovered_from") or []
            print(f"recovered_from: {','.join(recovered_from) if recovered_from else 'none'}")
            print(f"note: {finding.get('note')}")
            print(UNREDACT_NOTE)
        if finding.get("refuse_code") == REFUSE_OPAQUE and op in {"lift", "recover", "refuse"}:
            return 2
        return 0

    if args.cmd == "recover":
        from spectrallock.recover import (
            RECOVER_NOTE,
            analyze_recover_path,
            parse_recover_op,
        )

        token = str(args.op_or_src)
        known = {
            "locate", "deep", "deep-recover", "revision-graph", "compare",
            "cross-compare", "extract-embedded", "scan-orphans", "scan-metadata",
            "scan-sidecars", "scan-history", "refuse", "production", "redactions",
        }
        twin = args.twin
        src = args.src_opt
        if token.lower() in known:
            op = token
            if not src:
                print("recover: missing input file", file=sys.stderr)
                return 2
            if args.src_opt2 and op in {"compare", "cross-compare"}:
                twin = twin or args.src_opt2
        else:
            op = "locate"
            src = token
            if args.src_opt and not twin:
                # recover compare old new (op omitted)
                try:
                    parse_recover_op("compare")
                    op = "cross-compare"
                    twin = args.src_opt
                except ValueError:
                    pass
        try:
            parse_recover_op(op)
            finding = analyze_recover_path(
                src,
                op=op,
                twin=twin,
                query=args.query,
                production_dir=args.production_dir,
                production=args.production or None,
                recursive=args.recursive,
                all_metadata=args.all_metadata,
                scan_orphans=args.scan_orphans,
                extract_embedded=args.extract_embedded,
                cross_compare=args.cross_compare or op in {"compare", "cross-compare"},
                deep=args.deep or op in {"deep", "deep-recover", "redactions"},
            )
        except FileNotFoundError:
            print(f"input not found: {src}", file=sys.stderr)
            return 2
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.as_json:
            print(json.dumps(finding, indent=2, ensure_ascii=False))
        else:
            print(f"op: {finding.get('op')}")
            print(f"type: {finding.get('type')}")
            print(f"format_status: {finding.get('format_status')}")
            print(f"recovered_count: {finding.get('recovered_count')}")
            print(f"refuse_code: {finding.get('refuse_code') or 'none'}")
            print(f"secret_material_present: {finding.get('secret_material_present')}")
            print(f"no_lie: {finding.get('no_lie')}")
            print(RECOVER_NOTE)
        if finding.get("refuse_code") and finding.get("stop") and op == "refuse":
            return 2
        return 0

    if args.cmd in {"handwriting", "handwrite", "ink-hand", "forgery-scan"}:
        from spectrallock.handwriting import (
            HANDWRITING_NOTE,
            REFUSE_NO_INK,
            REFUSE_UNSUPPORTED,
            analyze_handwriting_path,
            parse_handwriting_op,
        )

        token = str(args.op_or_src)
        known = {
            "analyze", "compare", "side-by-side", "sidebyside", "graph",
            "forgery-indicators", "forgery", "refuse", "handwriting",
            "handwrite", "ink-hand", "forgery-scan",
        }
        twin = args.twin
        src = args.src_opt
        key = token.lower().replace("_", "-")
        if key in known:
            op = token
            if not src:
                print("handwriting: missing input scan", file=sys.stderr)
                return 2
            if args.src_opt2 and parse_handwriting_op(op) in {"compare", "side-by-side"}:
                twin = twin or args.src_opt2
        else:
            op = "forgery-indicators" if args.cmd == "forgery-scan" else "analyze"
            src = token
            if args.src_opt and not twin:
                op = "compare"
                twin = args.src_opt
        try:
            parse_handwriting_op(op)
            finding = analyze_handwriting_path(src, op=op, twin=twin)
        except FileNotFoundError:
            print(f"input not found: {src}", file=sys.stderr)
            return 2
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.as_json:
            print(json.dumps(finding, indent=2, ensure_ascii=False))
        else:
            print(f"op: {finding.get('op')}")
            print(f"refuse_code: {finding.get('refuse_code') or 'none'}")
            print(f"strokes: {len(finding.get('strokes') or [])}")
            print(f"forgery_indicators: {len(finding.get('forgery_indicators') or [])}")
            print(f"no_lie: {finding.get('no_lie')}")
            print(HANDWRITING_NOTE)
        if finding.get("refuse_code") in {REFUSE_NO_INK, REFUSE_UNSUPPORTED} and op == "refuse":
            return 2
        return 0

    if args.cmd in {"pigment", "restore-pigment"}:
        from spectrallock.pigment import (
            PIGMENT_NOTE,
            REFUSE_GONE,
            analyze_pigment_path,
            parse_pigment_op,
        )

        token = str(args.op_or_src)
        known = {
            "restore", "estimate", "refuse", "pigment", "restore-pigment",
            "lost-pigment", "restore-lost-pigment", "estimate-pigment",
        }
        key = token.lower().replace("_", "-")
        src = args.src_opt
        if key in known:
            op = token
            if not src:
                print("pigment: missing input photograph", file=sys.stderr)
                return 2
        else:
            op = "restore"
            src = token
        try:
            parse_pigment_op(op)
            finding = analyze_pigment_path(src, op=op, inject=bool(args.inject))
        except FileNotFoundError:
            print(f"input not found: {src}", file=sys.stderr)
            return 2
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.output and finding.get("png_b64"):
            import base64

            Path(args.output).write_bytes(base64.b64decode(finding["png_b64"]))
            finding["dst"] = args.output
        if args.as_json:
            print(json.dumps(finding, indent=2, ensure_ascii=False))
        else:
            print(f"op: {finding.get('op')}")
            print(f"pigment_recovery: {str(finding.get('pigment_recovery')).lower()}")
            print(f"recovered: {str(finding.get('recovered')).lower()}")
            print(f"refuse_code: {finding.get('refuse_code') or 'none'}")
            print(f"evidence_pixels: {finding.get('evidence_pixels')}")
            print(PIGMENT_NOTE)
        if finding.get("refuse_code") == REFUSE_GONE and not finding.get("recovered"):
            return 2
        return 0

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
