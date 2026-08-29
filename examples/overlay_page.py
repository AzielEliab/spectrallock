#!/usr/bin/env python3
"""Write a synthetic page overlay. Advisory, not forensic proof."""

from __future__ import annotations

from pathlib import Path

from spectrallock.engine import LIMITATION, apply_mode, save_rgb, synthetic_page


def main() -> None:
    out = Path(__file__).resolve().parent / "_out"
    out.mkdir(exist_ok=True)
    page = synthetic_page(128, 96)
    save_rgb(page, str(out / "page.png"))
    for mode in ("zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance"):
        result = apply_mode(page, mode)
        dest = out / f"{mode}.png"
        save_rgb(result.rgb, str(dest))
        print(f"{mode:8} {result.paper:10} -> {dest.name}")
    print(LIMITATION)


if __name__ == "__main__":
    main()
