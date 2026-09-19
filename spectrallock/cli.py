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
        type=resolve_mode,
        metavar="MODE",
        help=(
            "SpectralLock lens id or alias "
            "(zero|tazel|vyrn|uv|rosetta|zen|chaos|balance|candle|indent|lemon)."
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
        if args.as_json:
            print(json.dumps({
                "product": "spectrallock",
                "version": __version__,
                "author": "Aziel Eliab",
                "rosetta_spectral_analysis": True,
                "corpus_ocr_aligned": True,
                "advisory": LIMITATION,
                "modes": rows,
                "lenses": list_lenses(),
                "targets": list_targets(),
                "unredact": list_unredact(),
            }, indent=2))
        else:
            print(LIMITATION)
            print(f"{'id':10} {'paper':10} {'status':8} summary")
            for row in rows:
                print(f"{row['id']:10} {row['paper']:10} {row['status']:8} {row['summary']}")
            print("targets: ink (writing) · page (parchment)")
            print("unredact family: locate · lift · recover · refuse (not a lens; leftover bytes only)")
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

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
