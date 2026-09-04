"""Normalized bundle and offline visualization tests."""

import json
from pathlib import Path

from hyperknowledge.bundle import export_bundle, read_bundle, validate_bundle
from hyperknowledge.skill_manager import bundled_skill_path
from hyperknowledge.visualization import render_bundle_html

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _write_ka(path, *, template, topology_type, data):
    path.mkdir()
    (path / "data.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )
    (path / "metadata.json").write_text(
        json.dumps(
            {
                "template": template,
                "lang": "en",
                "type": topology_type,
                "sources": [{"path": "sample.md", "sha256": "abc"}],
            }
        ),
        encoding="utf-8",
    )


def test_bundle_canonicalizes_undirected_pairwise_endpoints(tmp_path):
    ka = tmp_path / "graph-ka"
    _write_ka(
        ka,
        template="general/base_graph",
        topology_type="graph",
        data={
            "nodes": [
                {"name": "zeta", "type": "entity"},
                {"name": "alpha", "type": "entity"},
            ],
            "edges": [{"source": "zeta", "target": "alpha", "type": "directs"}],
        },
    )
    output = tmp_path / "bundle"

    export_bundle(ka, output)
    bundle = read_bundle(output)

    assert "directed" not in bundle["assertions"][0]
    assert [(m["role"], m["node_id"]) for m in bundle["members"]] == [
        ("endpoint", "alpha"),
        ("endpoint", "zeta"),
    ]

    html = output / "default.html"
    result = render_bundle_html(output, html)
    page = html.read_text(encoding="utf-8")

    assert result["view"] == "contour"
    assert result["default_representation"] == "regularized_enclosure"
    assert result["representation_order"] == [
        "incidence_matrix",
        "incidence_bipartite",
        "regularized_enclosure",
        "native_pairwise_relations",
    ]
    assert result["pairwise_view_available"] is True
    assert result["pairwise_view"] == "native_relations_only"
    assert 'data-representation="pairwise"' in page
    assert page.index('data-representation="matrix"') < page.index(
        'data-representation="incidence"'
    )
    assert page.index('data-representation="incidence"') < page.index(
        'data-representation="contour"'
    )
    assert page.index('data-representation="contour"') < page.index(
        'data-representation="pairwise"'
    )
    assert 'let currentView="hypergraph"' in page
    assert 'let hyperMode="contour"' in page
    assert "pairwise-line-explanation" in page
    assert "not a hyperedge boundary" in page
    assert "不是超边边界" in page
    # Source and installed wheels must use the same self-contained Skill icon.
    icon = (bundled_skill_path() / "assets" / "icon-small.svg").read_text(
        encoding="utf-8"
    )
    assert icon.strip() in page
    assert "__BRAND_ICON__" not in page
    assert "M6 8l10-4 10 4v11l-10 9-10-9z" not in page


def test_hypergraph_bundle_and_offline_workbench(tmp_path):
    ka = tmp_path / "hyper-ka"
    _write_ka(
        ka,
        template="general/base_hypergraph",
        topology_type="hypergraph",
        data={
            "nodes": [
                {"name": "Alice", "type": "person"},
                {"name": "Bob", "type": "person"},
                {"name": "Carol", "type": "person"},
            ],
            "edges": [
                {
                    "name": "Working group",
                    "type": "collaboration",
                    "participants": ["Alice", "Bob", "Carol"],
                }
            ],
        },
    )
    output = tmp_path / "bundle"
    export_bundle(ka, output)

    html = output / "views" / "compare.html"
    result = render_bundle_html(output, html)
    page = html.read_text(encoding="utf-8")
    bundle = read_bundle(output)

    assert bundle["assertions"][0]["topology"] == "hyperedge"
    assert len(bundle["members"]) == 3
    assert "Hyper-Knowledge Workbench" in page
    assert "Higher-order graph · incidence view" in page
    assert "Clique expansion" not in page
    assert "Native pairwise relations" in page
    assert "Higher-order view (incidence)" in page
    assert 'testId:"native-pairwise"' in page
    assert 'testId:"hypergraph-incidence"' in page
    assert "noticeRow.dataset.testid" not in page
    assert 'id="bundle-line"' not in page
    assert 'data-action="reset"' in page
    assert 'id="clear-focus"' not in page
    assert "Role annotations" in page
    assert "Relation Details &amp; Sources" in page
    assert "Switch color theme" in page
    assert "Scroll to zoom" in page
    assert 'data-language="zh"' in page
    assert 'data-language="en"' in page
    assert 'type="button" data-representation="pairwise"' not in page
    assert 'data-representation="matrix"' in page
    assert 'data-representation="incidence"' in page
    assert 'data-representation="contour"' in page
    assert 'data-representation="compare"' not in page
    assert page.index('data-representation="matrix"') < page.index(
        'data-representation="incidence"'
    )
    assert page.index('data-representation="incidence"') < page.index(
        'data-representation="contour"'
    )
    assert 'testId:"hypergraph-contour"' in page
    assert "membershipBoundaryPath" in page
    assert "contourMembershipLayout" in page
    assert "balancedBoundaryAngles" in page
    assert "contourRelationCenters" in page
    assert "orbitalEnclosureGeometry" in page
    assert "orbitalMembershipBoundaryPath" in page
    assert "orbitalMemberPositions" in page
    assert "orbitalSharedPositions" in page
    assert "petal" not in page.lower()
    assert "花瓣" not in page
    assert "twoHyperedgeIntersectionLayout" in page
    assert "incidenceMatrixPanel" in page
    assert "nodeMembershipSummaryPanel" in page
    assert "节点—超边归属" in page
    assert "independent_interactive_incidence_matrix" in json.dumps(result)
    assert "shared_boundary_dual_lobe" in json.dumps(result)
    assert "contourLabelPlacements" not in page
    assert "contourDenseLabelNotice" in page
    assert "graph-lod-label" in page
    assert "button.dataset.expansion=mode" not in page
    assert "Star representation" not in page
    assert "starProjectionData" not in page
    assert "starProjectionPositions" not in page
    assert "edgeRolePoint" not in page
    assert "projection-hub" not in page
    assert "超边中心（派生）" not in page
    assert "localizedNodeType" in page
    assert "hyper-envelope-glow" not in page
    assert "hyper-envelope-accent" not in page
    assert "linearGradient" not in page
    assert "stroke:url" not in page
    assert ".node-inside-label" in page
    assert ".assertion-mark .label-block-bg,.hyperedge-label .label-block-bg" in page
    assert "legend-node-swatch" in page
    assert "legend-hyperedge-swatch" in page
    assert "legend-envelope-line" in page
    assert 'addRoleLegend(panel.legend,"roles"' not in page
    assert page.count("panel.foot.remove()") == 2
    assert 'addRoleLegend(panel.legend,"contour")' in page
    assert "setContourHover" in page
    assert "is-hover-muted" in page
    assert "statusModelPredicted" in page
    assert "关系详情与来源" in page
    assert "来源记录" in page
    assert "关联断言" not in page
    assert (
        result["selection_policy"]
        == "stable_matrix_or_node_to_incident_hyperedge_summary_or_single_relation_expansion"
    )
    assert result["schema_version"] == "hk.view/v29"
    assert result["layout"] == "undirected_force_or_membership_boundary"
    assert result["contour_geometry"] == "circle_first_then_ellipse_membership_boundary"
    assert result["contour_spacing"] == "balanced_angular_gap_distribution"
    assert result["contour_separation"] == (
        "shared_relation_spring_and_nonincident_repulsion"
    )
    assert result["contour_dense_strategy"] == (
        "dominant_shared_node_space_filling_orbital_enclosures"
    )
    assert result["enclosure_shape_policy"] == (
        "circle_when_feasible_else_oriented_ellipse"
    )
    assert result["enclosure_space_policy"] == "aspect_aware_outer_frame_fill"
    assert (
        result["enclosure_order_policy"] == "descending_member_count_clockwise_from_top"
    )
    assert result["enclosure_hub_policy"] == "highest_membership_node_at_center"
    assert (
        result["enclosure_shared_node_policy"]
        == "regular_boundary_intersection_before_local_adjustment"
    )
    assert (
        result["enclosure_corner_policy"]
        == "distance_limited_tangent_continuous_smoothing"
    )
    assert result["enclosure_selection_policy"] == (
        "fill_boundary_or_label_click_to_single_hyperedge_members"
    )
    assert result["enclosure_drag_policy"] == (
        "regular_shape_refit_and_member_redistribution"
    )
    assert result["single_hyperedge_layout"] == "exact_regular_circle_or_ellipse"
    assert result["reset_icon"] == "counterclockwise_arrow"
    assert result["visual_grammar"] == (
        "normalized_display_text_inside_degree_aware_circles_and_relation_framed_hyperedges"
    )
    assert result["node_card_policy"] == "adaptive_filled_circle_with_internal_name"
    assert result["node_shape_policy"] == (
        "text_fit_primary_bounded_hyperedge_degree_secondary"
    )
    assert result["node_naming_policy"] == (
        "atomic_entity_concept_or_value_event_phrases_as_predicates"
    )
    assert result["node_label_overflow_policy"] == (
        "wrap_then_ellipsis_with_full_tooltip"
    )
    assert result["node_display_punctuation_policy"] == (
        "strip_outer_title_marks_in_glyph_preserve_source_label"
    )
    assert result["shared_node_indicator_policy"] == (
        "dashed_outer_ring_for_multiple_native_hyperedges"
    )
    assert result["hyperedge_card_policy"] == "relation_hue_matched_framed"
    assert result["secondary_label_policy"] == "hidden_for_nodes_and_hyperedges"
    assert result["chrome_text_policy"] == ("hide_bundle_metadata_and_panel_explainer")
    assert result["enclosure_line_policy"] == (
        "single_uniform_relation_color_fixed_thick_width"
    )
    assert result["enclosure_width_control"] == "omitted_fixed_thick"
    assert result["enclosure_fill_policy"] == "low_opacity_relation_tint"
    assert result["enclosure_hover_policy"] == (
        "isolate_member_nodes_and_dim_unrelated_scene"
    )
    assert result["enclosure_hover_fill_policy"] == (
        "light_relation_tint_on_fill_boundary_or_label_hover"
    )
    assert (
        result["dense_incidence_strategy"] == "independent_interactive_incidence_matrix"
    )
    assert (
        result["matrix_selection_policy"]
        == "stable_row_column_cell_highlight_without_view_switch"
    )
    assert (
        result["incidence_node_focus_strategy"]
        == "selected_node_and_incident_hyperedges_only"
    )
    assert (
        result["incidence_relation_focus_strategy"]
        == "single_hyperedge_complete_membership_expansion"
    )
    assert result["two_hyperedge_strategy"] == "shared_boundary_dual_lobe"
    assert result["responsive_canvas"] == ("aspect_aware_width_and_height_viewbox")
    assert result["overview_space_usage"] == (
        "adaptive_horizontal_coordinate_expansion"
    )
    assert result["drawer_policy"] == "auto_collapse_when_idle"
    assert result["incidence_focus_layout"] == (
        "semantic_type_ellipse_with_reserved_sectors"
    )
    assert result["incidence_role_labels"] == (
        "collision_aware_duplicate_role_disambiguation"
    )
    assert result["label_policy"] == (
        "node_names_inside_adaptive_circles_and_wrapped_relation_blocks"
    )
    assert result["label_placement"] == (
        "node_centered_and_relation_collision_avoidance"
    )
    assert result["label_lod_policy"] == (
        "two_or_three_line_circle_labels_with_full_tooltip"
    )
    assert result["fit_policy"] == ("content_bounds_on_initial_focus_reset_and_resize")
    assert result["pairwise_edge_labels"] == "native_predicate_labels"
    assert result["interaction_policy"] == (
        "draggable_nodes_with_live_edge_and_enclosure_reflow"
    )
    assert result["pairwise_expansion_modes"] == []
    assert result["pairwise_view_available"] is False
    assert result["representations"] == [
        "incidence_matrix",
        "incidence_bipartite",
        "regularized_enclosure",
    ]
    assert result["hypergraph_views"] == [
        "incidence_matrix",
        "incidence_bipartite",
        "regularized_enclosure",
    ]
    assert "incidenceLayout" in page
    assert "focusedIncidencePositions" in page
    assert "placeSector" in page
    assert "computeViewFrame" in page
    assert "fitContent" in page
    assert "widenPositions" in page
    assert "incidenceRolePlacements" in page
    assert "incidenceRoleText" in page
    assert "addSvgLabelBlock" in page
    assert "enableNodeDrag" in page
    assert "interactiveContourHypergraphPanel" in page
    assert "hyper-envelope-hit" in page
    assert "pointer-events:visiblePainted" in page
    assert "singleRegularEnclosureLayout" in page
    assert "regularEnclosureBoundaryPath" in page
    assert "refitAnchoredEnclosure" in page
    assert "reflowContourGeometry" in page
    assert 'clearPositionOverrides("contour:")' in page
    assert 'closest?.(".mark,.link,.hyper-envelope-layer")' in page
    assert 't("resetInitial"),"↺"' in page
    assert "button.title=label" in page
    assert "⛶" not in page
    assert "marker-end" not in page
    assert "dragPositionOverrides.clear()" in page
    assert "addEnclosureWidthControl" not in page
    assert "ENCLOSURE_WIDTH_PRESETS" not in page
    assert "enclosureStrokePreset" not in page
    assert "包络线粗细" not in page
    assert "原生无向高阶结构" not in page
    assert "无向高阶结构" in page
    assert "圆形优先" not in page
    assert 'badge=layout.dominantNodeId?""' in page
    assert (
        ".hyper-envelope{fill:none;stroke:var(--hyper-color);stroke-width:2.4px" in page
    )
    assert ".hyper-envelope.is-related{opacity:.82;stroke-width:3.2px}" in page
    assert ".hyper-envelope.is-hover-focus{opacity:1;stroke-width:3.2px}" in page
    assert "nodeCircleMetrics" in page
    assert "addEntityNodeGlyph" in page
    assert "nodeDisplayLabel" in page
    assert "nativeHyperedgeDegree" in page
    assert "membershipCount" in page
    assert "hyperedgeDegree" in page
    assert "legend-shared-node-swatch" in page
    assert (
        'panel.viewport.querySelectorAll(".entity-mark,.hyper-envelope-layer,.hyperedge-label,.link")'
        in page
    )
    assert "memberIds.has" in page
    assert "is-hover-focus" in page
    assert ".hyper-envelope-fill.is-hover-focus" in page
    assert "stroke:var(--hyper-color" in page
    assert 'nameOnly=parent.classList?.contains("entity-mark")' in page
    assert 'layout.classList.add("drawer-idle")' in page
    assert 'layout.classList.remove("drawer-idle")' in page
    assert "https://" not in page
    assert "<script src=" not in page
    assert result["offline"] is True
    assert (html.parent / "view-manifest.json").is_file()

    matrix_html = output / "matrix.html"
    matrix_result = render_bundle_html(output, matrix_html, view="hypergraph")
    matrix_page = matrix_html.read_text(encoding="utf-8")
    assert matrix_result["default_representation"] == "incidence_matrix"
    assert 'let hyperMode="matrix"' in matrix_page
    assert 'hyperMode==="matrix"' in matrix_page
    assert "nodeMembershipSummaryPanel" in matrix_page

    validation = validate_bundle(output, quality="showcase")
    assert validation["status"] == "passed", validation["diagnostics"]
    assert validation["summary"]["unresolved_members"] == 0


def test_sushi_trajectory_preserves_time_place_stage_correspondence():
    bundle = read_bundle(
        REPOSITORY_ROOT / "examples" / "sushi-document-test" / "bundle"
    )
    members_by_assertion = {}
    for member in bundle["members"]:
        members_by_assertion.setdefault(member["assertion_id"], {})[member["role"]] = (
            member["node_id"]
        )

    assert members_by_assertion["assertion:huizhou-exile-1094"] == {
        "被贬者": "person:su-shi",
        "时间": "time:1094",
        "贬谪地": "place:huizhou",
    }
    assert members_by_assertion["assertion:danzhou-exile-1097"] == {
        "被贬者": "person:su-shi",
        "时间": "time:1097",
        "贬谪地": "place:danzhou",
    }
    assert members_by_assertion["assertion:changzhou-return-1101"] == {
        "北归者": "person:su-shi",
        "时间": "time:1101",
        "到达地": "place:changzhou",
    }
    assert "assertion:exile-trajectory" not in members_by_assertion
    node_ids = {node["id"] for node in bundle["nodes"]}
    assert not any(node_id.startswith("stage:") for node_id in node_ids)
    assert "event:imperial-exam-1057" not in node_ids
    assert "time:1057" in node_ids
    predicates = {
        assertion["id"]: assertion["predicate"] for assertion in bundle["assertions"]
    }
    assert predicates["assertion:imperial-exam-1057"] == "科举考试"
    assert predicates["assertion:changzhou-return-1101"] == "北归"


def test_compare_view_is_hidden_from_public_controls(tmp_path):
    ka = tmp_path / "semantic-ka"
    _write_ka(
        ka,
        template="general/base_hypergraph",
        topology_type="hypergraph",
        data={
            "nodes": [
                {"name": "Biomarker", "type": "biomarker"},
                {"name": "Intervention", "type": "intervention"},
                {"name": "Outcome", "type": "outcome"},
            ],
            "edges": [
                {
                    "name": "Evidence tuple",
                    "type": "reported_association",
                    "participants": ["Biomarker", "Intervention", "Outcome"],
                }
            ],
        },
    )
    output = tmp_path / "bundle"
    export_bundle(ka, output)

    html = output / "compare.html"
    render_bundle_html(output, html, view="compare")
    page = html.read_text(encoding="utf-8")

    assert 'data-representation="compare"' not in page
    assert "Hyperedges stay intact" in page
    assert "No hyperedge is flattened" in page
    assert "native hyperedge" in page
    assert "native pairwise relations only" in page
    assert "roleStyle(member.role)" in page
    assert 'selection.kind==="assertion"' in page
    assert "focusRelation(id)" in page
    assert "focusSharedNode(id)" in page
    assert "focusAssertionIds=new Set" in page
    assert "activeNodes()" in page
    assert "高阶视图（关联）" in page
    assert "高阶视图（包络）" in page
    assert "超边团扩展" not in page
    assert "团扩展" not in page
    assert "星形表示" not in page
    assert "超边中心（派生）" not in page
    assert 'type="button" data-representation="pairwise"' not in page
    assert "复位并适配全部内容" in page
    assert "拖动节点重排" in page


def test_bundle_validation_rejects_missing_member_reference(tmp_path):
    ka = tmp_path / "invalid-ka"
    _write_ka(
        ka,
        template="general/base_graph",
        topology_type="graph",
        data={
            "nodes": [{"name": "known", "type": "entity"}],
            "edges": [{"source": "known", "target": "missing", "type": "links"}],
        },
    )
    output = tmp_path / "bundle"
    export_bundle(ka, output)

    standard = validate_bundle(output, quality="standard")
    showcase = validate_bundle(output, quality="showcase")

    assert standard["status"] == "passed"
    assert standard["summary"]["warnings"] >= 1
    assert any(
        item["code"] == "bundle.member_node_ref" for item in standard["diagnostics"]
    )
    assert showcase["status"] == "failed"
    assert any(
        item["code"] == "bundle.member_node_ref" for item in showcase["diagnostics"]
    )
