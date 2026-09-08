"""Execute the published no-key Python examples, not only their syntax."""

import re
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("locale", ["en", "zh"])
@pytest.mark.parametrize("page", ["api", "python"])
def test_keyless_documentation_examples(tmp_path, monkeypatch, locale, page):
    document = REPO / f"docs/{locale}/guide/{page}.md"
    blocks = re.findall(
        r"```python\n(.*?)```", document.read_text(encoding="utf-8"), re.S
    )
    blocks = [
        block
        for block in blocks
        if block.startswith("from hyperknowledge import import_graph")
    ]
    assert len(blocks) == 1
    shutil.copytree(REPO / "examples/python", tmp_path / "examples/python")
    monkeypatch.chdir(tmp_path)
    namespace = {}
    exec(compile(blocks[0], str(document), "exec"), namespace)
    result = namespace["result"]
    assert result.bundle_path.is_dir()
    assert result.hyperedge_count >= 1
