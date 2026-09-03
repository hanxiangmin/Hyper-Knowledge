"""Unit tests for AutoGraph extraction functionality."""

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


class TestAutoGraphExtraction:
    """Test cases for AutoGraph extraction functionality."""

    def test_init_with_schemas(self, llm_client, embedder):
        """Test initialization with node and edge schemas."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert graph.empty() is True
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_node_schema_property(self, llm_client, embedder):
        """Test that node_schema property returns correct schema."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert graph.node_schema == Entity

    def test_edge_schema_property(self, llm_client, embedder):
        """Test that edge_schema property returns correct schema."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert graph.edge_schema == Relation

    def test_feed_text_adds_nodes_directly(self, llm_client, embedder):
        """Test that we can add nodes directly to memory without LLM call."""
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

        assert len(graph._node_memory.items) == 2
        assert graph.empty() is False

    def test_feed_text_returns_self(self, llm_client, embedder):
        """Test that adding data returns self for method chaining."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        graph._node_memory.add([Entity(name="Apple", type="ORGANIZATION", properties={})])

        assert graph.empty() is False

    def test_clear_resets_state(self, llm_client, embedder):
        """Test that clear resets the graph to empty state."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        graph._node_memory.add([Entity(name="Apple", type="ORGANIZATION", properties={})])

        graph.clear()

        assert graph.empty() is True
        assert len(graph._node_memory.items) == 0

    def test_two_stage_extraction_mode(self, llm_client, embedder):
        """Test two-stage extraction mode initialization."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        assert graph.extraction_mode == "two_stage"


class TestAutoGraphInternal:
    """Test cases for AutoGraph internal state management."""

    def test_nodes_property(self, llm_client, embedder):
        """Test nodes property."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert isinstance(graph.nodes, list)

    def test_edges_property(self, llm_client, embedder):
        """Test edges property."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert isinstance(graph.edges, list)

    def test_metadata_initialized(self, llm_client, embedder):
        """Test that metadata is initialized correctly."""
        graph = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert "created_at" in graph.metadata
        assert "updated_at" in graph.metadata
