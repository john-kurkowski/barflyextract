"""Integration tests for the entire project.

Keep to a minimum.
https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html.
"""

import io
import os

import pytest
import syrupy

import barflyextract.datasource
import barflyextract.extract


@pytest.mark.skipif(not os.environ.get("API_KEY"), reason="API_KEY not set")
def test_entire_pipeline(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    snapshot: syrupy.SnapshotAssertion,
) -> None:
    """Test the pipeline from upstream source to printing to the console.

    This test is slow, incurs API quota costs, and is brittle to upstream
    changes. It is skipped (and does not fail) without an API_KEY set. It
    should not be run frequently or in CI.
    """
    monkeypatch.setattr("sys.argv", ["my_cmd"])
    barflyextract.datasource.run()
    step_one_output, _ = capsys.readouterr()
    assert step_one_output

    monkeypatch.setattr("sys.argv", ["my_cmd", "-"])
    monkeypatch.setattr("sys.stdin", io.StringIO(step_one_output))
    barflyextract.extract.run()
    step_two_output, _ = capsys.readouterr()
    assert step_two_output
    assert step_two_output.splitlines()[:10] == snapshot
