"""Unit tests for AutoGraph search functionality."""

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


class TestAutoGraphSearch:
    """Test cases for AutoGraph search functionality."""

    def test_build_index_nodes_only(self, llm_client, embedder):
        """Test building index for nodes only."""
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
            Entity(name="Steve Jobs", type="PERSON", properties={}),
        ])

        graph.build_index(index_nodes=True, index_edges=False)

        assert graph._node_memory.has_index()

    def test_build_index_both(self, llm_client, embedder):
        """Test building index for both nodes and edges."""
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

        graph.build_index(index_nodes=True, index_edges=True)

        assert graph._node_memory.has_index()
        assert graph._edge_memory.has_index()

    def test_build_node_index(self, llm_client, embedder):
        """Test building node index specifically."""
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

        graph.build_node_index()

        assert graph._node_memory.has_index()

    def test_search_nodes(self, llm_client, embedder):
        """Test searching nodes."""
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
            Entity(name="Steve Jobs", type="PERSON", properties={}),
        ])
        graph.build_node_index()

        results = graph.search_nodes("technology company", top_k=2)

        assert isinstance(results, list)

    def test_search_edges(self, llm_client, embedder):
        """Test searching edges."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        graph._edge_memory.add([
            Relation(source="Apple", target="Steve Jobs", relation_type="founded_by"),
            Relation(source="Apple", target="Tim Cook", relation_type="led_by"),
        ])
        graph.build_edge_index()

        results = graph.search_edges("founder", top_k=2)

        assert isinstance(results, list)

    def test_search_unified(self, llm_client, embedder):
        """Test unified search interface."""
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

        nodes, edges = graph.search("Apple company", top_k_nodes=1, top_k_edges=1)

        assert isinstance(nodes, list)
        assert isinstance(edges, list)

    def test_search_with_top_k(self, llm_client, embedder):
        """Test search with top_k parameter."""
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

        nodes, edges = graph.search("company", top_k=2)

        assert isinstance(nodes, list)
        assert isinstance(edges, list)
