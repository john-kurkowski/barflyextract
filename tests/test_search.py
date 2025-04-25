"""Unit tests for recipe search."""

import sys
import textwrap
from pathlib import Path

import pytest
import syrupy

from barflyextract import search as search_module

SAMPLE_HTML = textwrap.dedent(
    """
    <h2>Negroni</h2>
    <ul>
      <li>Gin</li>
      <li>Sweet Vermouth</li>
      <li>Campari</li>
    </ul>
    <h2>Martini</h2>
    <ul>
      <li>Gin</li>
      <li>Dry Vermouth</li>
    </ul>
    """
).strip()


def test_search_matches_title(
    snapshot: syrupy.assertion.SnapshotAssertion,
) -> None:
    """Test that a recipe title is included in search."""
    hits = list(search_module.search(SAMPLE_HTML, "negroni"))
    assert hits == snapshot


def test_search_matches_multiple_tokens_case_insensitive(
    snapshot: syrupy.assertion.SnapshotAssertion,
) -> None:
    """Test that search applies case-insensitive AND matching."""
    hits = list(search_module.search(SAMPLE_HTML, "DRY", "gin"))
    assert hits == snapshot


def test_search_no_matches(
    snapshot: syrupy.assertion.SnapshotAssertion,
) -> None:
    """Test that search returns no matches."""
    hits = list(search_module.search(SAMPLE_HTML, "vermouth", "vodka"))
    assert hits == snapshot


def test_main_validates_args(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    snapshot: syrupy.assertion.SnapshotAssertion,
) -> None:
    """Test that the CLI fails fast on missing args."""
    monkeypatch.setattr(sys, "argv", ["search.py"])
    with pytest.raises(SystemExit) as excinfo:
        search_module.main()
    assert excinfo.value.code == 2
    out, err = capsys.readouterr()
    assert {"stdout": out, "stderr": err} == snapshot


def test_main_emits_results(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    snapshot: syrupy.assertion.SnapshotAssertion,
) -> None:
    """Test that the CLI prints search hits."""
    html_path = tmp_path / "recipes.html"
    html_path.write_text(SAMPLE_HTML, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["search.py", str(html_path), "dry"])
    search_module.main()
    out, err = capsys.readouterr()
    assert {"stdout": out, "stderr": err} == snapshot
