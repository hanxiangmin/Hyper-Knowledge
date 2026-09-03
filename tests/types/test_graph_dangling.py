"""Unit tests for AutoGraph dangling edge pruning."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional, List

from hyperknowledge.types import AutoGraph


class Entity(BaseModel):
    """Simple entity schema for testing."""

    name: str
    type: str
    properties: dict = Field(default_factory=dict)


class Relation(BaseModel):
    """Simple relation schema for testing."""

    source: str
    target: str
    relation_type: str


class TestAutoGraphDangling:
    """Test cases for AutoGraph dangling edge handling."""

    def test_graph_with_dangling_edges(self, llm_client, embedder):
        """Test that graph can contain dangling edges (no automatic pruning)."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        graph._node_memory.add([
            Entity(name="Apple", type="ORGANIZATION", properties={}),
        ])
        graph._edge_memory.add([
            Relation(source="Apple", target="Steve Jobs", relation_type="founded_by"),
        ])

        graph.build_index()

        nodes, edges = graph.search("Apple", top_k_nodes=2, top_k_edges=2)

        assert len(nodes) >= 1


class TestAutoGraphMerge:
    """Test cases for AutoGraph merge functionality."""

    def test_merge_batch_data_single_graph(self, llm_client, embedder):
        """Test merging single graph."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        graph._node_memory.add([
            Entity(name="Apple", type="ORGANIZATION", properties={}),
        ])

        assert len(graph.nodes) == 1

    def test_merge_batch_data_filters_none(self, llm_client, embedder):
        """A failed single-chunk invoke ([None]) yields an empty graph.

        Previously [None] fell through to the tuple branch and raised
        AssertionError instead of degrading gracefully.
        """
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        result = graph.merge_batch_data([None])

        assert result.nodes == []
        assert result.edges == []

    def test_merge_batch_data_empty_first_chunk(self, llm_client, embedder):
        """merge_batch_data tolerates a chunk that produced no nodes/edges.

        Previously the first sublist being empty raised IndexError via
        nodes_lists[0][0] / edges_lists[0][0].
        """
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        # First chunk produced nothing; the second carries the real data.
        nodes_lists = [
            [],
            [Entity(name="Apple", type="ORGANIZATION", properties={})],
        ]
        edges_lists = [
            [],
            [Relation(source="Apple", target="Steve", relation_type="founded_by")],
        ]

        result = graph.merge_batch_data((nodes_lists, edges_lists))

        assert {n.name for n in result.nodes} == {"Apple"}
        assert len(result.edges) == 1
