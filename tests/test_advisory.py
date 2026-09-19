"""Identity: Rosetta spectral analysis aligned with Corpus OCR lenses."""

from __future__ import annotations

import ast
import re
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
    for mode in ("zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance", "candle", "indent", "lemon"):
        assert mode in readme
    assert "clsa-1.0" in readme or "candlelight" in readme
    assert "runtime-sync" in readme or "runtime sync" in readme


FULL_AI_CLIENTS = (
    "ChatGPT (GPT Actions / OpenAI)",
    "Grok (xAI)",
    "Venice",
    "Claude (Anthropic)",
    "Cursor (MCP)",
    "Glama (MCP)",
    "Perplexity",
    "Microsoft Copilot / Bing",
    "Google Gemini / Vertex",
    "Mistral",
    "Meta AI",
    "Apple Intelligence surfaces",
    "Amazon Q tooling",
    "DuckAssist",
    "You.com",
    "Cohere",
    "other MCP/OpenAPI-capable assistants",
)


def _copy_surfaces() -> dict[str, str]:
    worker = ROOT / "workers" / "download-tracker"
    return {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "SKILL.md": (ROOT / "SKILL.md").read_text(encoding="utf-8"),
        "workers/download-tracker/README.md": (worker / "README.md").read_text(encoding="utf-8"),
        "workers/download-tracker/src/index.js": (worker / "src" / "index.js").read_text(encoding="utf-8"),
    }


def test_copy_lists_full_ai_clients_not_exclusive_trio() -> None:
    exclusive_headings = (
        "use with grok / chatgpt / venice",
        "use with grok, chatgpt, venice",
    )
    for path, text in _copy_surfaces().items():
        lower = text.lower()
        for heading in exclusive_headings:
            assert heading not in lower, f"{path} still has exclusive heading {heading!r}"
        for name in FULL_AI_CLIENTS:
            assert name in text, f"{path} missing AI client {name!r}"
        assert "Aziel Eliab" in text
        assert "Grok / ChatGPT / Venice" not in text


def test_worker_hosts_default_asset() -> None:
    js = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text(encoding="utf-8")
    match = re.search(r'const DEFAULT_ASSET = "([^"]+)";', js)
    assert match, "DEFAULT_ASSET constant missing from Worker"
    asset = match.group(1)
    path = ROOT / "workers" / "download-tracker" / "public" / asset
    assert path.is_file(), f"Worker DEFAULT_ASSET {asset} is not hosted in public/"
    data = path.read_bytes()
    assert data[:2] == b"\x1f\x8b", f"{asset} is not gzip"
    assert len(data) > 1024, f"{asset} is too small to be a release sdist"


def test_worker_skill_embed_matches_skill_md() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    js = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text(encoding="utf-8")
    match = re.search(r"const SKILL_MARKDOWN = (\".*?\");", js, flags=re.S)
    assert match, "SKILL_MARKDOWN constant missing from Worker"
    embedded = ast.literal_eval(match.group(1))
    assert embedded.rstrip() == skill.rstrip()
