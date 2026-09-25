"""Human CLI welcome, plain errors, and local UI layout."""

from __future__ import annotations

from pathlib import Path

import pytest

from spectrallock.cli import main
from spectrallock.ui import WEB

ROOT = Path(__file__).resolve().parents[1]


def test_bare_command_welcomes(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "faint marks" in out.lower()
    assert "spectrallock ui" in out
    assert "spectrallock doctor" in out
    assert "Aziel Eliab" in out
    assert "arguments are required" not in out
    assert "what this is not" not in out.lower()


def test_help_is_short_and_groups_advanced(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "usage:" in out
    assert "overlay" in out
    assert "Advanced" in out
    assert "restore-pigment" in out
    assert "Examples" in out
    assert "--json" in out
    assert "Aziel Eliab" in out
    assert "changelog" not in out.lower()
    assert "arguments are required" not in out


def test_unknown_command_has_next_step(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["bogus"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "spectrallock ui" in err
    assert "spectrallock --help" in err
    assert "the following arguments are required" not in err


def test_overlay_missing_args_has_next_step(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["overlay"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Overlay needs a lens" in err
    assert "spectrallock overlay --mode rosetta page.png out.png" in err


def test_local_ui_puts_power_features_under_advanced() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    css = (WEB / "style.css").read_text(encoding="utf-8")
    low = html.lower()
    assert "<details" in html
    head, advanced = low.split("<summary>advanced</summary>", 1)
    assert "restore pigment" in advanced
    assert "inject" in advanced
    assert "verify" in advanced
    assert "add file" in head
    assert "sample page" in head
    assert "rosetta spectral analysis" in low
    assert "spectrallock lenses" in low
    assert "prefers-color-scheme" in css
    assert ":focus-visible" in css
    assert "#c9a227" in css.lower()
    assert "viewport" in low
    run = (ROOT / "RUN.txt").read_text(encoding="utf-8")
    assert "spectrallock ui" in run
    assert "Aziel Eliab" in run
