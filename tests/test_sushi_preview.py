"""The local Su Shi preview preserves source-grounded role-aware hyperedges."""

import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "examples/sushi-local-preview/build_preview.py"
SOURCE_SHA256 = "65869e3042b4a3b7a83695f1a053f8a2d99a09d031167770d4636e433442c0ed"
TWO_MEMBER_ASSERTIONS = {
    "assertion:su-huang-poetry-name": {"person:su-shi", "person:huang-tingjian"},
    "assertion:su-xin-ci-name": {"person:su-shi", "person:xin-qiji"},
    "assertion:su-shi-song-four-membership": {"person:su-shi", "group:song-four"},
    "assertion:cold-food-calligraphy-authorship": {
        "person:su-shi",
        "work:huangzhou-cold-food",
    },
}


def read_table(directory, name):
    return [
        json.loads(line)
        for line in (directory / name).read_text(encoding="utf-8").splitlines()
    ]


@pytest.fixture
def builder(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("sushi_preview", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Keep every test write in pytest's temporary directory. ORIGINAL retains
    # its resolved, read-only source location in the real example.
    monkeypatch.setattr(module, "ROOT", tmp_path / "preview")
    return module


@pytest.fixture
def preview(builder):
    summary = builder.build()
    return builder, summary


def test_preview_preserves_supported_hyperedges_including_two_members(preview):
    builder, summary = preview
    bundle = builder.ROOT / "bundle"
    assertions = read_table(bundle, "assertions.jsonl")
    members = read_table(bundle, "members.jsonl")
    node_ids = {node["id"] for node in read_table(bundle, "nodes.jsonl")}
    membership = defaultdict(set)
    for member in members:
        membership[member["assertion_id"]].add(member["node_id"])
    assert summary["status"] == "passed"
    assert (summary["nodes"], summary["assertions"], summary["members"]) == (39, 18, 65)
    assert summary["hyperedges"] == 18
    assert summary["native_pairwise"] == 0
    assert {member["node_id"] for member in members} == node_ids
    for assertion in assertions:
        assert assertion["topology"] == "hyperedge"
        assert len(membership[assertion["id"]]) >= 2
    assert {
        assertion_id: node_ids
        for assertion_id, node_ids in membership.items()
        if len(node_ids) == 2
    } == TWO_MEMBER_ASSERTIONS
    # Retained assertions have exactly their declared source-grounded members,
    # not padded or topic-merged replacements of two-member assertions.
    for relation in builder.RELATIONS:
        assert membership["assertion:" + relation["id"]] == {
            node_id for node_id, _ in relation["members"]
        }
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["presentation"]["contour_layout"] == "single_hyperedge"
    assert manifest["presentation"]["overview_layout"] == "radial_hypergraph"


@pytest.mark.parametrize(
    ("view", "mode", "representation"),
    [
        ("contour", "overview", "radial_hypergraph_overview"),
        ("incidence", "incidence", "incidence_bipartite"),
        ("hypergraph", "matrix", "incidence_matrix"),
    ],
)
def test_preview_overview_is_available_without_overriding_explicit_views(
    preview, view, mode, representation
):
    from hyperknowledge.visualization.html import render_bundle_html

    builder, _ = preview
    output = builder.ROOT / "views" / f"{view}.html"
    result = render_bundle_html(builder.ROOT / "bundle", output, view=view)
    html = output.read_text(encoding="utf-8")
    assert result["default_representation"] == representation
    assert result["representation_order"][0] == "radial_hypergraph_overview"
    assert f'let hyperMode="{mode}"' in html
    assert 'data-representation="overview"' in html
    assert 'data-representation="pairwise" aria-pressed=' not in html
    assert result["overview_focus_policy"] == (
        "stable_full_graph_dim_only_never_remove_members"
    )
    assert result["overview_hyperedge_policy"] == "one_capsule_per_source_hyperedge"
    assert result["overview_hyperedge_label_policy"] == (
        "internal_name_and_stable_global_E_code_compartment"
    )
    assert result["overview_role_policy"] == (
        "focused_edge_all_members_or_focused_node_own_incidences"
    )


def test_preview_quotes_match_unchanged_source(preview):
    builder, _ = preview
    original = (builder.ORIGINAL / builder.SOURCE_PATH).read_bytes()
    copied = (builder.ROOT / builder.SOURCE_PATH).read_bytes()
    assert original == copied
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA256
    lines = original.decode("utf-8").splitlines()
    bundle = builder.ROOT / "bundle"
    evidence = {row["id"]: row for row in read_table(bundle, "evidence.jsonl")}
    for assertion in read_table(bundle, "assertions.jsonl"):
        assert assertion["evidence_refs"]
        for reference in assertion["evidence_refs"]:
            record = evidence[reference]
            assert record["quote"] == "\n".join(
                lines[record["line_start"] - 1 : record["line_end"]]
            )
            assert record["source_sha256"] == SOURCE_SHA256


def test_preview_provenance_does_not_claim_extraction_or_human_confirmation(preview):
    builder, _ = preview
    for assertion in read_table(builder.ROOT / "bundle", "assertions.jsonl"):
        assert assertion["epistemic_status"] == "editorial_candidate"
        properties = assertion["properties"]
        assert properties["construction_method"] == "editorial_source_mapping"
        assert properties["review_status"] == "pending_human_review"
        assert properties["remote_provider"] is False
        assert "extractor" not in properties


def test_preview_rejects_single_member_assertion_before_writing(builder, monkeypatch):
    singleton = {**builder.RELATIONS[0], "members": builder.RELATIONS[0]["members"][:1]}
    monkeypatch.setattr(builder, "RELATIONS", [singleton])
    with pytest.raises(ValueError, match="at least two distinct members"):
        builder.build()
    assert not builder.ROOT.exists()


def test_preview_duplicate_role_members_do_not_increase_arity(builder, monkeypatch):
    member = builder.RELATIONS[0]["members"][0]
    false_binary = {
        **builder.RELATIONS[0],
        "members": [member, (member[0], "another role")],
    }
    monkeypatch.setattr(builder, "RELATIONS", [false_binary])
    with pytest.raises(ValueError, match="at least two distinct members"):
        builder.build()
    assert not builder.ROOT.exists()


def test_preview_accepts_two_distinct_members_with_multiple_roles(builder, monkeypatch):
    members = builder.RELATIONS[0]["members"][:2]
    two_member = {
        **builder.RELATIONS[0],
        "members": [*members, (members[0][0], "another role")],
    }
    monkeypatch.setattr(builder, "RELATIONS", [two_member])
    summary = builder.build()
    assert summary["status"] == "passed"
    assert (summary["nodes"], summary["assertions"], summary["members"]) == (2, 1, 3)
    assert summary["hyperedges"] == 1
    assert summary["native_pairwise"] == 0
    assert summary["shared_nodes"] == {}


def test_two_member_assertions_are_supported_by_the_original_source(preview):
    builder, _ = preview
    bundle = builder.ROOT / "bundle"
    evidence = {row["id"]: row for row in read_table(bundle, "evidence.jsonl")}
    for assertion in read_table(bundle, "assertions.jsonl"):
        if assertion["id"] not in TWO_MEMBER_ASSERTIONS:
            continue
        assert assertion["epistemic_status"] == "editorial_candidate"
        assert len(assertion["evidence_refs"]) == 1
        source_span = evidence[assertion["evidence_refs"][0]]
        assert (source_span["line_start"], source_span["line_end"]) == (59, 59)
