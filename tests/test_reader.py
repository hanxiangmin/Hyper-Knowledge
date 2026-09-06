"""Execute single-hyperedge reader and global structural-metric contracts."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def test_single_hyperedge_reader_regressions():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for executable renderer reader tests")
    result = subprocess.run(
        [node, str(Path(__file__).with_name("renderer_reader.cjs"))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=30,
    )
    report = json.loads(result.stdout)
    assert len(report["passed"]) == 13
    assert report["geometryCases"] == 66
