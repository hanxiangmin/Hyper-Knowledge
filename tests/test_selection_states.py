"""Execute state and drawer regressions against the real renderer JavaScript."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


def test_renderer_selection_state_regressions():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for executable renderer state tests")
    result = subprocess.run(
        [node, str(Path(__file__).with_name("renderer_selection.cjs"))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=30,
    )
    assert len(json.loads(result.stdout)["passed"]) == 12
