"""Identifier parsing canonicalizes graph endpoints and hypergraph membership."""

from pydantic import BaseModel

from hyperknowledge.utils.template_engine.parsers.identifiers import _members_extractor


class CustomPairwiseRelation(BaseModel):
    origin: str
    destination: str


class GroupedHyperedge(BaseModel):
    leaders: list[str]
    participants: list[str] | None


class SingleFieldHyperedge(BaseModel):
    members: list[str] | None


def test_graph_member_mapping_canonicalizes_undirected_endpoints():
    extractor = _members_extractor({"source": "origin", "target": "destination"})
    relation = CustomPairwiseRelation(origin="zeta", destination="alpha")

    assert extractor(relation) == ("alpha", "zeta")


def test_grouped_hypergraph_members_are_flattened_for_validation():
    extractor = _members_extractor(["leaders", "participants"])
    relation = GroupedHyperedge(leaders=["Alice"], participants=["Bob", "Carol"])

    assert extractor(relation) == ("Alice", "Bob", "Carol")


def test_optional_hypergraph_member_lists_skip_none():
    extractor = _members_extractor(["leaders", "participants"])
    relation = GroupedHyperedge(leaders=["Alice", "Bob"], participants=None)

    assert extractor(relation) == ("Alice", "Bob")


def test_optional_single_hypergraph_member_field_accepts_none():
    extractor = _members_extractor("members")

    assert extractor(SingleFieldHyperedge(members=None)) == ()
