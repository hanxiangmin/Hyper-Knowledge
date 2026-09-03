"""Unit tests for AutoHypergraph batch merge."""

from typing import List

from pydantic import BaseModel, Field

from hyperknowledge.types import AutoHypergraph


class Entity(BaseModel):
    """Simple node schema for testing."""

    name: str
    type: str
    properties: dict = Field(default_factory=dict)


class HyperRelation(BaseModel):
    """Simple hyperedge schema for testing."""

    participants: List[str]
    relation_type: str


class TestAutoHypergraphMerge:
    """Test cases for AutoHypergraph merge functionality."""

    def _make_graph(self, llm_client, embedder):
        return AutoHypergraph(
            node_schema=Entity,
            edge_schema=HyperRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.relation_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

    def test_merge_batch_data_empty_first_chunk(self, llm_client, embedder):
        """merge_batch_data tolerates a chunk that produced no nodes/edges.

        Previously the first sublist being empty raised IndexError via
        nodes_lists[0][0] / edges_lists[0][0].
        """
        graph = self._make_graph(llm_client, embedder)

        # First chunk produced nothing; the second carries the real data.
        nodes_lists = [
            [],
            [Entity(name="Apple", type="ORGANIZATION", properties={})],
        ]
        edges_lists = [
            [],
            [HyperRelation(participants=["Apple", "Steve"], relation_type="founded_by")],
        ]

        result = graph.merge_batch_data((nodes_lists, edges_lists))

        assert {n.name for n in result.nodes} == {"Apple"}
        assert len(result.edges) == 1

    def test_merge_batch_data_filters_none(self, llm_client, embedder):
        """A failed single-chunk invoke ([None]) yields an empty hypergraph."""
        graph = self._make_graph(llm_client, embedder)

        result = graph.merge_batch_data([None])

        assert result.nodes == []
        assert result.edges == []
