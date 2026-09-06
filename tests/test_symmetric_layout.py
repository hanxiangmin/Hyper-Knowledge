"""Executable geometry invariants for opt-in symmetric hyperedge circles."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def test_symmetric_circle_layout_regressions():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for executable renderer geometry tests")
    result = subprocess.run(
        [node, str(Path(__file__).with_name("renderer_symmetric.cjs"))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=30,
    )
    report = json.loads(result.stdout)
    assert report["gridCases"] == 32
    assert len(report["passed"]) == 9
