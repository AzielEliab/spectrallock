#!/usr/bin/env python3
"""Write a synthetic page overlay. Rosetta spectral analysis. Author Aziel Eliab."""

from __future__ import annotations

from pathlib import Path

from spectrallock.engine import LIMITATION, analyze, save_rgb, synthetic_page


def main() -> None:
    out = Path(__file__).resolve().parent / "_out"
    out.mkdir(exist_ok=True)
    page = synthetic_page(128, 96)
    save_rgb(page, str(out / "page.png"))
    for mode in ("zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance"):
        for target in ("ink", "page"):
            result = analyze(page, mode, target=target)
            dest = out / f"{mode}-{target}.png"
            save_rgb(result.rgb, str(dest))
            print(f"{mode:8} {target:4} {result.paper:10} -> {dest.name}")
    print(LIMITATION)


if __name__ == "__main__":
    main()
