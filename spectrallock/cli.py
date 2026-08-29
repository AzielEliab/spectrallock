"""Command-line interface for SpectralLock.

    spectrallock version
    spectrallock modes
    spectrallock overlay --mode zero|tazel|vyrn|uv|rosetta|zen|chaos|balance IN.png OUT.png
    spectrallock ui
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from spectrallock import LIMITATION, __version__, list_modes
from spectrallock.engine import LIVE_MODES, apply_mode, load_rgb, save_rgb


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spectrallock",
        description=(
            "SpectralLock — digital overlays on photographs of manuscript pages "
            "(Aziel Eliab, 2026). Advisory visualization. Not a lab spectrometer, "
            "not real UV hardware, not forensic proof, not OCR, not scribal truth. "
            f"Local UI: `spectrallock ui` at http://127.0.0.1:8861. {LIMITATION}"
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_modes = sub.add_parser("modes", help="List overlay modes (live papers + ids).")
    p_modes.add_argument("--json", action="store_true", dest="as_json", help="JSON list.")

    p_ov = sub.add_parser("overlay", help="Apply one mode. PNG/JPEG in, PNG out.")
    p_ov.add_argument(
        "--mode",
        required=True,
        choices=list(LIVE_MODES),
        help="Overlay mode id.",
    )
    p_ov.add_argument("src", metavar="IN", help="Input photograph (PNG or JPEG).")
    p_ov.add_argument("dst", metavar="OUT", help="Output overlay PNG.")
    p_ov.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print metadata JSON (mode, com, sizes) after writing the image.",
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "version":
        print(f"spectrallock {__version__}")
        return 0

    if args.cmd == "modes":
        rows = list_modes()
        if args.as_json:
            print(json.dumps({"product": "spectrallock", "version": __version__,
                              "advisory": LIMITATION, "modes": rows}, indent=2))
        else:
            print(LIMITATION)
            print(f"{'id':10} {'paper':10} {'status':8} summary")
            for row in rows:
                print(f"{row['id']:10} {row['paper']:10} {row['status']:8} {row['summary']}")
        return 0

    if args.cmd == "overlay":
        try:
            rgb = load_rgb(args.src)
        except FileNotFoundError:
            print(f"input not found: {args.src}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001
            print(f"could not read image: {exc}", file=sys.stderr)
            return 2
        result = apply_mode(rgb, args.mode, tint=not args.no_tint)
        save_rgb(result.rgb, args.dst)
        meta = result.to_meta()
        meta["src"] = args.src
        meta["dst"] = args.dst
        if args.as_json:
            print(json.dumps(meta, indent=2))
        else:
            print(
                f"{result.mode} {result.paper} {result.width}x{result.height} "
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
