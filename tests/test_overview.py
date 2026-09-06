"""Execute canonical radial overview geometry and membership contracts."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def test_radial_hypergraph_overview_regressions():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for executable overview geometry tests")
    result = subprocess.run(
        [node, str(Path(__file__).with_name("renderer_overview.cjs"))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=30,
    )
    report = json.loads(result.stdout)
    assert len(report["passed"]) == 25
    assert report["roleFocusCases"] == 171
    assert report["clippedLinkCases"] == 195
    assert report["currentNodes"] == 39
    assert report["currentHyperedges"] == 18
    assert report["currentIncidences"] == 65
