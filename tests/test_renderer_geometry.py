"""Behavioral geometry regressions using the exact offline JavaScript renderer."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def geometry_results():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for executable renderer geometry tests")
    result = subprocess.run(
        [node, str(Path(__file__).with_name("renderer_geometry.cjs"))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=30,
    )
    return json.loads(result.stdout)


def test_mixed_single_hyperedge_keeps_binary_endpoints_and_isolates(geometry_results):
    result = geometry_results["mixed"]
    assert result["missing"] == []
    assert result["links"] == [[True, True]]
    assert result["finite"]


def test_components_never_anchor_nonmember_hub(geometry_results):
    result = geometry_results["partial"]
    assert result["missing"] == []
    assert result["falseAnchors"] == []
    assert result["unrelatedFree"]
    assert result["finite"]


def test_partial_hub_in_connected_component_is_not_forced_into_all_edges(
    geometry_results,
):
    assert geometry_results["connected"] == {"hub": None, "finite": True}


def test_center_drag_is_rejected_without_mutating_valid_boundary(geometry_results):
    result = geometry_results["drag"]
    assert result["rejected"] is False
    assert result["unchanged"]
    assert result["validRefit"]
    assert result["boundaryRadius"] == pytest.approx(1)


def test_long_unbroken_identifier_wraps_inside_node(geometry_results):
    result = geometry_results["text"]
    assert len(result["lines"]) > 1
    assert max(result["widths"]) < result["diameter"] - 12


def test_contour_title_placement_avoids_nodes_and_other_titles(geometry_results):
    assert geometry_results["labels"] == {"nodeCollisions": 0, "labelCollision": False}
