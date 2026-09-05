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


def test_worker_skill_embed_matches_skill_md() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    js = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text(encoding="utf-8")
    for line in skill.splitlines():
        if line.strip():
            assert line in js, f"Worker SKILL_MARKDOWN missing {line!r}"
