"""Identity: Rosetta spectral analysis aligned with Corpus OCR lenses."""

from __future__ import annotations

from pathlib import Path

from spectrallock.engine import LIMITATION

ROOT = Path(__file__).resolve().parents[1]


def test_readme_and_whitepaper_are_rosetta() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    paper = (ROOT / "docs" / "whitepaper.md").read_text(encoding="utf-8").lower()
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
    blob = readme + "\n" + paper + "\n" + skill + "\n" + LIMITATION.lower()
    assert "rosetta spectral analysis" in blob
    assert "aziel corpus library ocr" in blob or "corpus ocr" in blob
    assert "ink" in blob and "page" in blob
    assert "never invent" in blob or "never invents" in blob
    assert "not a spectrometer" not in blob
    assert "not a lab spectrometer" not in blob
    for mode in ("zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance"):
        assert mode in readme
