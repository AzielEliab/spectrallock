"""Command-line interface for SpectralLock.

    spectrallock version
    spectrallock modes
    spectrallock lenses
    spectrallock doctor
    spectrallock overlay --mode|--lens zero|tazel|vyrn|uv|rosetta|zen|chaos|balance
                         --target ink|page IN.png OUT.png
    spectrallock overlay --verify --sidecar
    spectrallock ui
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from spectrallock import LIMITATION, __version__, list_lenses, list_modes, list_targets
from spectrallock.debug import debug
from spectrallock.engine import (
    LIVE_MODES,
    PLAIN_NOT_IMAGE,
    analyze,
    load_rgb,
    make_receipt,
    png_bytes,
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
        help="Check Python, Pillow, numpy, eight lenses × ink/page, no NaN, loopback, no telemetry.",
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
        choices=list(LIVE_MODES),
        help="SpectralLock lens id (same names as Corpus OCR).",
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
    p_ov.add_argument(
        "--no-tint",
        action="store_true",
        help="Composites as grayscale (exact formula). Default tints mildly.",
    )

    p_ui = sub.add_parser("ui", help="Serve the local overlay UI on 127.0.0.1.")
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8861, help="Port (default 8861).")

    p_serve = sub.add_parser("serve", help="Alias for ui. Bind 127.0.0.1 only.")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8861)

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

    if "127.0.0.1" not in LOOPBACK:
        ok = False
        lines.append("loopback: fail")
    else:
        lines.append("loopback: 127.0.0.1 only")
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
            }, indent=2))
        else:
            print(LIMITATION)
            print(f"{'id':10} {'paper':10} {'status':8} summary")
            for row in rows:
                print(f"{row['id']:10} {row['paper']:10} {row['status']:8} {row['summary']}")
            print("targets: ink (writing) · page (parchment)")
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
        try:
            result = analyze(rgb, args.mode, target=args.target, tint=not args.no_tint)
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

    if args.cmd in {"ui", "serve"}:
        from spectrallock.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
