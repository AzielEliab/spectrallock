"""SpectralLock color inject switch (operator card 19 Sep 2026).

ON paints membership (false color). OFF is the same gate as gray.
ON is not recovered pigment. Zero ignores the switch.

    python3 spectrallock_inject.py page.jpg --mode vyrn --inject -o vyrn_on.jpg
    python3 spectrallock_inject.py page.jpg --mode vyrn --no-inject -o vyrn_off.jpg
    python3 spectrallock_inject.py page.jpg --all --inject --outdir out/
    python3 spectrallock_inject.py page.jpg --all --no-inject --outdir out_plain/
    python3 spectrallock_inject.py page.jpg --mode zero --target ink --no-inject

Author: Aziel Eliab. Lamb Lens: Service → Clarity → Peace. NO-LIE.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from spectrallock import LIMITATION, __version__
from spectrallock.debug import debug
from spectrallock.engine import (
    INJECT_NOTE,
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
        prog="spectrallock_inject.py",
        description=(
            "SpectralLock color inject switch. ON paints membership "
            "(false color, not recovered pigment). OFF is luminance of the "
            "same gate. Zero ignores the switch. Author Aziel Eliab."
        ),
    )
    parser.add_argument("src", metavar="PAGE", help="Input photograph (PNG or JPEG).")
    parser.add_argument(
        "--mode",
        "--lens",
        dest="mode",
        default=None,
        type=resolve_mode,
        metavar="MODE",
        help="Named SpectralLock mode (or alias).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run every live mode into --outdir.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--inject",
        dest="inject",
        action="store_true",
        help="False-color membership tint (paint). Default.",
    )
    group.add_argument(
        "--no-inject",
        dest="inject",
        action="store_false",
        help="Luminance of the same gate (gray).",
    )
    parser.set_defaults(inject=True)
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="Output image path (single mode).",
    )
    parser.add_argument(
        "--outdir",
        help="Output directory for --all (or default single-mode name).",
    )
    parser.add_argument(
        "--target",
        default="ink",
        choices=["ink", "page"],
        help="Ink isolates writing; page isolates parchment. Default ink.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print overlay/verify JSON (includes in-band percents).",
    )
    parser.add_argument(
        "--sidecar",
        action="store_true",
        help="Write a JSON sidecar next to each output.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Print a receipt. In-band percents print before any hit claim.",
    )
    return parser


def _receipt_from_result(result, src_bytes: bytes, out_bytes: bytes, inject: bool) -> dict:
    return make_receipt(
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


def _print_receipt(rec: dict) -> None:
    print(f"mode: {rec['mode']}")
    print(f"lenses: {','.join(rec.get('lenses') or [rec['mode']])}")
    print(f"target: {rec.get('target', 'ink')}")
    print(f"paper: {rec['paper']}")
    print(f"inject: {str(rec.get('inject', True)).lower()}")
    print(f"inject_applied: {str(rec.get('inject_applied', True)).lower()}")
    print(f"tazel_inband_pct: {rec.get('tazel_inband_pct', 0.0):.2f}")
    print(f"vyrn_inband_pct: {rec.get('vyrn_inband_pct', 0.0):.2f}")
    print(f"sha256_in: {rec['sha256_in']}")
    print(f"sha256_out: {rec['sha256_out']}")
    print(f"size_in: {rec['size_in']}")
    print(f"size_out: {rec['size_out']}")
    print(INJECT_NOTE)
    print(LIMITATION)


def _run_one(rgb, src_bytes: bytes, mode: str, target: str, inject: bool, dest: Path) -> tuple[dict, dict]:
    result = analyze(rgb, mode, target=target, inject=inject)
    out_bytes = png_bytes(result.rgb)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(out_bytes)
    rec = _receipt_from_result(result, src_bytes, out_bytes, inject)
    meta = result.to_meta()
    meta["src"] = str(dest)
    meta["dst"] = str(dest)
    meta.update({
        k: rec[k]
        for k in (
            "sha256_in", "sha256_out", "size_in", "size_out", "limitation",
            "inject", "inject_applied", "inject_ignored",
            "tazel_inband_pct", "vyrn_inband_pct",
            "pigment_recovery", "empty_gate_not_broken_lens", "inject_note",
        )
        if k in rec
    })
    debug(
        f"inject mode={result.mode} applied={result.inject_applied} "
        f"tazel={result.tazel_inband_pct} vyrn={result.vyrn_inband_pct} dest={dest}"
    )
    return meta, rec


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.all and not args.outdir:
        parser.error("--all requires --outdir")
    if not args.all and not args.mode:
        parser.error("specify --mode or --all")
    if not args.all and not args.output and not args.outdir:
        parser.error("specify -o/--output (or --outdir)")

    src = Path(args.src)
    try:
        src_bytes = src.read_bytes()
    except FileNotFoundError:
        print(f"input not found: {args.src}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        debug(f"inject read type={type(exc).__name__}")
        print(PLAIN_NOT_IMAGE, file=sys.stderr)
        return 2
    try:
        rgb = load_rgb(args.src)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        debug(f"inject decode type={type(exc).__name__}")
        print(PLAIN_NOT_IMAGE, file=sys.stderr)
        return 2

    inject = bool(args.inject)
    modes = list(LIVE_MODES) if args.all else [args.mode]
    written: list[dict] = []
    last_rec = None
    for mode in modes:
        if args.all:
            dest = Path(args.outdir) / f"{mode}.png"
        elif args.output:
            dest = Path(args.output)
        else:
            dest = Path(args.outdir) / f"{mode}.png"
        try:
            meta, rec = _run_one(rgb, src_bytes, mode, args.target, inject, dest)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        last_rec = rec
        written.append(meta)
        if args.sidecar:
            write_sidecar(str(dest), rec)
        if not args.as_json and not args.verify:
            print(
                f"{rec['mode']} inject={'on' if rec['inject_applied'] else 'off'} "
                f"tazel_inband_pct={rec['tazel_inband_pct']:.2f} "
                f"vyrn_inband_pct={rec['vyrn_inband_pct']:.2f} "
                f"{rec['target']} {rec['paper']} -> {dest}"
            )

    if args.as_json:
        payload = written[0] if len(written) == 1 else {
            "product": "spectrallock",
            "version": __version__,
            "author": "Aziel Eliab",
            "inject": inject,
            "target": args.target,
            "overlays": written,
            "inject_note": INJECT_NOTE,
            "advisory": LIMITATION,
        }
        print(json.dumps(payload, indent=2))
    elif args.verify and last_rec is not None and not args.all:
        _print_receipt(last_rec)
    elif args.verify and args.all:
        for row in written:
            print(
                f"{row['mode']}: tazel_inband_pct={row['tazel_inband_pct']:.2f} "
                f"vyrn_inband_pct={row['vyrn_inband_pct']:.2f} "
                f"inject_applied={str(row['inject_applied']).lower()}"
            )
        print(INJECT_NOTE)
        print(LIMITATION)
    elif not args.as_json:
        print(INJECT_NOTE)
        print(LIMITATION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
