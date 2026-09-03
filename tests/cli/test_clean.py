"""Tests for the `hk clean` command."""

import json

from typer.testing import CliRunner

from hyperknowledge.cli.cli import app

runner = CliRunner()


def _make_ka(tmp_path, with_index=True):
    """Create a minimal Knowledge Abstract directory on disk."""
    ka = tmp_path / "ka"
    ka.mkdir()
    (ka / "data.json").write_text(
        json.dumps({"nodes": [], "edges": []}), encoding="utf-8"
    )
    (ka / "metadata.json").write_text(json.dumps({"template": "x"}), encoding="utf-8")
    if with_index:
        index = ka / "index"
        index.mkdir()
        (index / "node_index").mkdir()
        (index / "node_index" / "index.faiss").write_text("x", encoding="utf-8")
    return ka


class TestClean:
    def test_clean_index_only(self, tmp_path):
        ka = _make_ka(tmp_path)
        result = runner.invoke(app, ["clean", str(ka), "--yes"])
        assert result.exit_code == 0
        assert not (ka / "index").exists()
        # Data is preserved — only the index was cleaned.
        assert (ka / "data.json").exists()

    def test_clean_all_removes_whole_ka(self, tmp_path):
        ka = _make_ka(tmp_path)
        result = runner.invoke(app, ["clean", str(ka), "--all", "--yes"])
        assert result.exit_code == 0
        assert not ka.exists()

    def test_clean_aborts_without_confirmation(self, tmp_path):
        ka = _make_ka(tmp_path)
        result = runner.invoke(app, ["clean", str(ka)], input="n\n")
        assert result.exit_code == 0
        assert (ka / "index").exists()  # nothing deleted

    def test_clean_confirms_with_yes_input(self, tmp_path):
        ka = _make_ka(tmp_path)
        result = runner.invoke(app, ["clean", str(ka)], input="y\n")
        assert result.exit_code == 0
        assert not (ka / "index").exists()

    def test_clean_no_index(self, tmp_path):
        ka = _make_ka(tmp_path, with_index=False)
        result = runner.invoke(app, ["clean", str(ka), "--yes"])
        assert result.exit_code == 0
        assert "Nothing to clean" in result.output
        assert ka.exists()

    def test_clean_nonexistent_path(self, tmp_path):
        result = runner.invoke(app, ["clean", str(tmp_path / "nope"), "--yes"])
        assert result.exit_code == 1

    def test_clean_refuses_non_ka_directory(self, tmp_path):
        # A directory without data.json must not be deletable via clean.
        plain = tmp_path / "plain"
        plain.mkdir()
        (plain / "important.txt").write_text("keep", encoding="utf-8")
        result = runner.invoke(app, ["clean", str(plain), "--all", "--yes"])
        assert result.exit_code == 1
        assert plain.exists()
