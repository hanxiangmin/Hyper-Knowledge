"""Tests for the export_obsidian() methods on graph AutoTypes.

Graphs are populated directly via the OMem stores (no LLM calls needed), so
these run deterministically under the mock fixtures.
"""

from typing import List

from pydantic import BaseModel, Field

from hyperknowledge.types import AutoGraph, AutoHypergraph, AutoTemporalGraph


class Entity(BaseModel):
    name: str
    type: str = "ENTITY"


class Relation(BaseModel):
    source: str
    target: str
    relation_type: str


class Event(BaseModel):
    label: str
    participants: List[str] = Field(default_factory=list)


def _make_graph(llm_client, embedder):
    return AutoGraph(
        node_schema=Entity,
        edge_schema=Relation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=llm_client,
        embedder=embedder,
    )


class TestAutoGraphExportObsidian:
    def test_export_creates_vault(self, tmp_path, llm_client, embedder):
        graph = _make_graph(llm_client, embedder)
        graph._node_memory.add(
            [Entity(name="Apple", type="ORG"), Entity(name="Steve Jobs", type="PERSON")]
        )
        graph._edge_memory.add(
            [Relation(source="Apple", target="Steve Jobs", relation_type="founded_by")]
        )

        vault = graph.export_obsidian(tmp_path / "vault", vault_name="MyKB")

        assert vault == tmp_path / "vault"
        assert (vault / "Apple.md").exists()
        assert (vault / "Steve Jobs.md").exists()
        assert (vault / "MyKB.md").exists()
        assert "[[Steve Jobs]]" in (vault / "Apple.md").read_text(encoding="utf-8")

    def test_empty_graph_exports_index_only(self, tmp_path, llm_client, embedder):
        graph = _make_graph(llm_client, embedder)
        vault = graph.export_obsidian(tmp_path / "vault", vault_name="Empty")
        assert (vault / "Empty.md").exists()
        assert len(list(vault.glob("*.md"))) == 1

    def test_temporal_graph_inherits_method(self, llm_client, embedder):
        # AutoTemporalGraph subclasses AutoGraph, so it inherits export_obsidian.
        assert hasattr(AutoTemporalGraph, "export_obsidian")


class TestAutoHypergraphExportObsidian:
    def test_export_nary_edge(self, tmp_path, llm_client, embedder):
        hg = AutoHypergraph(
            node_schema=Entity,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.label}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            edge_label_extractor=lambda x: x.label,
            llm_client=llm_client,
            embedder=embedder,
        )
        hg._node_memory.add([Entity(name="A"), Entity(name="B"), Entity(name="C")])
        hg._edge_memory.add([Event(label="meeting", participants=["A", "B", "C"])])

        vault = hg.export_obsidian(tmp_path / "vault")

        source = (vault / "A.md").read_text(encoding="utf-8")
        assert "meeting" in source
        assert "[[B]]" in source
        assert "[[C]]" in source
