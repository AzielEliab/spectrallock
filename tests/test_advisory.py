"""Honesty: docs, package, UI copy refuse forensic / hardware claims."""

from __future__ import annotations

from pathlib import Path

from spectrallock.engine import LIMITATION

ROOT = Path(__file__).resolve().parents[1]


def test_readme_and_whitepaper_are_honest() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    paper = (ROOT / "docs" / "whitepaper.md").read_text(encoding="utf-8").lower()
    blob = readme + "\n" + paper + "\n" + LIMITATION.lower()
    assert "not a lab spectrometer" in blob or "not a spectrometer" in blob
    assert "forensic" in blob
    assert "not real uv" in blob or "synthetic uv" in blob
    assert "never invent" in blob or "never invents" in blob
    for mode in ("zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance"):
        assert mode in readme
