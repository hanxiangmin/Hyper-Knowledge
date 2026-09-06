"""Behavioral regressions for role-aware, source-grounded hypergraph bundles."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from hyperknowledge.bundle import (
    _members,
    _value,
    export_bundle,
    read_bundle,
    validate_bundle,
)
from hyperknowledge.utils.template_engine import Gallery, localize_template
from hyperknowledge.utils.template_engine.parsers import parse_identifiers, parse_output
from hyperknowledge.utils.template_engine.parsers.identifiers import _members_extractor


def write_ka(path, *, template="general/hypergraph", edges=None, source=None):
    path.mkdir()
    nodes = [
        {"name": name, "type": kind}
        for name, kind in [("苏轼", "person"), ("1101年", "time"), ("常州", "place")]
    ]
    (path / "data.json").write_text(
        json.dumps(
            {
                "nodes": nodes,
                "edges": edges
                or [
                    {
                        "name": "北归常州",
                        "type": "北归",
                        "actors": ["苏轼"],
                        "times": ["1101年"],
                        "places": ["常州"],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (path / "metadata.json").write_text(
        json.dumps(
            {"template": template, "type": "hypergraph", "sources": source or []}
        ),
        encoding="utf-8",
    )
    return path


def write_table(bundle, name, rows):
    (bundle / f"{name}.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


@pytest.fixture
def bundle(tmp_path):
    ka = write_ka(tmp_path / "ka")
    output = tmp_path / "bundle"
    export_bundle(ka, output)
    return output


def test_default_template_extracts_atomic_members_and_preserves_legacy_input(tmp_path):
    config = localize_template(Gallery.get("general/hypergraph"), "zh")
    _, relation_schema = parse_output(config.output, config.type)
    _, relation_id, node_ids = parse_identifiers(config.identifiers, config.type)
    role_aware = relation_schema(
        name="北归常州", type="北归", actors=["苏轼"], times=["1101年"], places=["常州"]
    )
    assert set(node_ids(role_aware)) == {"苏轼", "1101年", "常州"}
    legacy = relation_schema(
        name="北归常州", type="北归", participants=["苏轼", "1101年", "常州"]
    )
    assert set(node_ids(legacy)) == set(node_ids(role_aware))
    ka = write_ka(tmp_path / "ka", edges=[role_aware.model_dump()])
    export_bundle(ka, tmp_path / "bundle")
    data = read_bundle(tmp_path / "bundle")
    assert data["assertions"][0]["id"] == relation_id(role_aware)
    assert {(member["role"], member["node_id"]) for member in data["members"]} == {
        ("actor", "苏轼"),
        ("time", "1101年"),
        ("place", "常州"),
    }
    assert len(data["nodes"]) == 3
    assert data["assertions"][0]["predicate"] == "北归"
    assert (
        validate_bundle(tmp_path / "bundle", quality="showcase")["status"] == "passed"
    )


def test_role_map_flattens_lists_and_keeps_additional_endpoint_roles():
    mapping = {
        "source": "people",
        "target": "places",
        "time": "year",
        "member": "participants",
    }
    raw = {
        "people": ["苏轼", "苏轼"],
        "places": ["常州"],
        "year": "1101年",
        "participants": ["苏轼", "常州", "1101年", "其他人"],
    }
    members = _members(raw, mapping)
    assert members == [
        ("source", "苏轼", None),
        ("target", "常州", None),
        ("time", "1101年", None),
        ("member", "其他人", None),
    ]
    assert set(_members_extractor(mapping)(SimpleNamespace(**raw))) == {
        "苏轼",
        "常州",
        "1101年",
        "其他人",
    }
    assert _members({"participants": "苏轼"}, None) == [("member", "苏轼", None)]


def test_qualified_treatment_identity_separates_conditions_and_outcomes():
    config = localize_template(Gallery.get("medicine/treatment_map"), "en")
    _, schema = parse_output(config.output, config.type)
    _, relation_id, members = parse_identifiers(config.identifiers, config.type)
    first = schema(
        diagnosis="D",
        treatment="T",
        type="indicated_for",
        conditions=["C2", "C1"],
        outcome="O1",
    )
    reordered = first.model_copy(update={"conditions": ["C1", "C2"]})
    different_condition = first.model_copy(update={"conditions": ["C3"]})
    different_outcome = first.model_copy(update={"outcome": "O2"})
    assert relation_id(first) == relation_id(reordered)
    assert (
        len(
            {
                relation_id(first),
                relation_id(different_condition),
                relation_id(different_outcome),
            }
        )
        == 3
    )
    assert relation_id(first) == _value(
        first.model_dump(), config.identifiers.relation_id
    )
    assert set(members(first)) == {"D", "T", "C1", "C2", "O1"}


@pytest.mark.parametrize(
    "field,value",
    [
        ("role", None),
        ("role", ""),
        ("role", []),
        ("ordinal", "0"),
        ("ordinal", None),
        ("ordinal", -1),
        ("ordinal", False),
    ],
)
def test_invalid_members_are_reported_without_crashing(bundle, field, value):
    data = read_bundle(bundle)
    data["members"][0][field] = value
    write_table(bundle, "members", data["members"])
    report = validate_bundle(bundle)
    assert report["status"] == "failed"
    assert any(
        item["code"] == f"bundle.member_{field}" for item in report["diagnostics"]
    )


def test_duplicate_members_do_not_inflate_arity(bundle):
    data = read_bundle(bundle)
    first = data["members"][0]
    write_table(bundle, "members", [first, {**first, "ordinal": 1}])
    codes = {item["code"] for item in validate_bundle(bundle)["diagnostics"]}
    assert "bundle.topology_arity" in codes
    assert "bundle.member_unique_role_node" in codes


def test_one_node_can_hold_two_different_roles(bundle):
    data = read_bundle(bundle)
    data["members"].append({**data["members"][0], "role": "author", "ordinal": 3})
    write_table(bundle, "members", data["members"])
    manifest = data["manifest"]
    manifest["counts"]["members"] = 4
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert validate_bundle(bundle)["status"] == "passed"


@pytest.mark.parametrize("field", ["predicate", "semantics", "epistemic_status"])
def test_assertion_semantics_required(bundle, field):
    data = read_bundle(bundle)
    del data["assertions"][0][field]
    write_table(bundle, "assertions", data["assertions"])
    assert any(
        item["code"] == "bundle.assertion_required_field"
        for item in validate_bundle(bundle)["diagnostics"]
    )


def attach_evidence(
    bundle,
    *,
    quote="苏轼于1101年北归常州。",
    summary=None,
    start=1,
    end=1,
    available=True,
):
    source = bundle.parent / "source.md"
    content = "苏轼于1101年北归常州。\n这是第二行。\n".encode()
    if available:
        source.write_bytes(content)
    data = read_bundle(bundle)
    data["manifest"]["sources"] = [
        {"path": "source.md", "sha256": hashlib.sha256(content).hexdigest()}
    ]
    data["manifest"]["counts"]["assertions_with_evidence"] = 1
    data["assertions"][0]["evidence_refs"] = ["e1"]
    (bundle / "manifest.json").write_text(
        json.dumps(data["manifest"]), encoding="utf-8"
    )
    write_table(bundle, "assertions", data["assertions"])
    evidence = {
        "id": "e1",
        "type": "source_text_span",
        "source": "source.md",
        "line_start": start,
        "line_end": end,
    }
    if quote is not None:
        evidence["quote"] = quote
    if summary is not None:
        evidence["summary"] = summary
    write_table(bundle, "evidence", [evidence])


def test_literal_evidence_passes_and_paraphrase_is_not_a_quote(bundle):
    attach_evidence(bundle)
    assert validate_bundle(bundle, quality="showcase")["summary"]["warnings"] == 0
    attach_evidence(bundle, quote="1101年苏轼回到常州。")
    assert validate_bundle(bundle, quality="standard")["status"] == "passed"
    assert validate_bundle(bundle, quality="showcase")["status"] == "failed"
    attach_evidence(bundle, quote=None, summary="1101年苏轼回到常州。")
    assert validate_bundle(bundle, quality="showcase")["status"] == "passed"


def test_unavailable_source_is_warning_not_forgery(bundle):
    attach_evidence(bundle, available=False)
    report = validate_bundle(bundle, quality="showcase")
    assert report["status"] == "passed"
    assert {item["code"] for item in report["diagnostics"]} == {
        "bundle.evidence_source_available"
    }


@pytest.mark.parametrize("start,end", [(3, 1), (0, 1), (1, 99), ("1", 2)])
def test_invalid_evidence_span_fails(bundle, start, end):
    attach_evidence(bundle, start=start, end=end)
    assert validate_bundle(bundle, quality="showcase")["status"] == "failed"


def test_undeclared_source_is_not_read_and_fails_reference(bundle):
    attach_evidence(bundle)
    data = read_bundle(bundle)
    data["evidence"][0]["source"] = "unregistered.md"
    write_table(bundle, "evidence", data["evidence"])
    report = validate_bundle(bundle)
    assert any(
        item["code"] == "bundle.evidence_source_ref" for item in report["diagnostics"]
    )


@pytest.mark.parametrize("source_name", ["../outside.md", "absolute"])
def test_metadata_cannot_authorize_external_source_reads(
    bundle, tmp_path_factory, monkeypatch, source_name
):
    attach_evidence(bundle)
    outside = tmp_path_factory.mktemp("unrelated") / "outside.md"
    outside.write_text("Not a project source", encoding="utf-8")
    if source_name == "absolute":
        source_name = str(outside)
    data = read_bundle(bundle)
    data["manifest"]["sources"][0]["path"] = source_name
    data["evidence"][0]["source"] = source_name
    (bundle / "manifest.json").write_text(
        json.dumps(data["manifest"]), encoding="utf-8"
    )
    write_table(bundle, "evidence", data["evidence"])
    original_read = Path.read_bytes

    def guarded_read(path):
        assert path.resolve().is_relative_to(bundle.parent.resolve())
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    report = validate_bundle(bundle)
    codes = {item["code"] for item in report["diagnostics"]}
    assert codes & {"bundle.evidence_source_path", "bundle.evidence_source_available"}


def test_invalid_source_inventory_reports_diagnostic(bundle):
    attach_evidence(bundle)
    data = read_bundle(bundle)
    data["manifest"]["sources"] = "not a source inventory"
    (bundle / "manifest.json").write_text(
        json.dumps(data["manifest"]), encoding="utf-8"
    )
    assert any(
        item["code"] == "bundle.source_inventory"
        for item in validate_bundle(bundle)["diagnostics"]
    )


def test_enriched_ka_evidence_and_status_survive_export(tmp_path):
    ka = write_ka(tmp_path / "ka")
    data = json.loads((ka / "data.json").read_text(encoding="utf-8"))
    data["edges"][0].update(
        semantics="human_assertion",
        epistemic_status="human_reviewed",
        evidence_refs=["e1"],
    )
    data["evidence"] = [
        {"id": "e1", "type": "human_annotation", "summary": "Reviewed offline"}
    ]
    (ka / "data.json").write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "bundle"
    export_bundle(ka, output)
    bundle = read_bundle(output)
    assert bundle["assertions"][0]["semantics"] == "human_assertion"
    assert bundle["assertions"][0]["epistemic_status"] == "human_reviewed"
    assert bundle["assertions"][0]["evidence_refs"] == ["e1"]
    assert bundle["evidence"] == data["evidence"]
    assert bundle["manifest"]["counts"]["assertions_with_evidence"] == 1
