"""Integration tests for real LLM extraction using OpenAI API."""

import os

import pytest
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoModel, AutoList, AutoSet, AutoGraph


# Skip all tests if no API key
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    ),
]


@pytest.fixture
def llm_client():
    """Provide real OpenAI LLM client."""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


@pytest.fixture
def embedder():
    """Provide real OpenAI embeddings client."""
    return OpenAIEmbeddings(model="text-embedding-3-small")


class PersonInfo(BaseModel):
    """Schema for person information."""
    name: str = Field(description="The person's name")
    age: int = Field(description="The person's age")
    occupation: str = Field(description="The person's job or occupation")


class TestAutoModelIntegration:
    """Integration tests for AutoModel with real API."""

    def test_extract_person_info(self, llm_client, embedder):
        """Test extracting structured person information."""
        text = "Alice is a 28-year-old software engineer living in San Francisco."

        automodel = AutoModel(
            data_schema=PersonInfo,
            llm_client=llm_client,
            embedder=embedder,
        )

        result = automodel.parse(text)

        assert result is not None
        assert result.data.name == "Alice"
        assert result.data.age == 28
        assert result.data.occupation == "software engineer"

    def test_real_extraction_not_mock(self, llm_client, embedder):
        """Verify that real extraction returns actual values, not mocks."""
        text = "Dr. Sarah Johnson is a 45-year-old cardiologist working at Mayo Clinic."

        automodel = AutoModel(
            data_schema=PersonInfo,
            llm_client=llm_client,
            embedder=embedder,
        )

        result = automodel.parse(text)

        # Verify real extraction (not mock values)
        assert "Sarah" in result.data.name
        assert result.data.age == 45
        assert "cardiologist" in result.data.occupation.lower()


class TestAutoListIntegration:
    """Integration tests for AutoList with real API."""

    def test_extract_multiple_items(self, llm_client, embedder):
        """Test extracting a list of items."""
        text = """
        The conference featured several keynote speakers:
        - Dr. Jane Smith, Chief Scientist at AI Labs
        - Prof. Michael Chen, Director of Research at Tech Institute
        - Sarah Williams, CEO of StartupCo
        """

        autolist = AutoList(
            item_schema=PersonInfo,
            llm_client=llm_client,
            embedder=embedder,
        )

        result = autolist.parse(text)

        assert len(result.items) >= 2
        for item in result.items:
            assert item.name
            assert item.age >= 0  # Age might be 0 if not specified
            assert item.occupation


class TestAutoSetIntegration:
    """Integration tests for AutoSet with real API."""

    def test_deduplication_with_real_embeddings(self, llm_client, embedder):
        """Test that deduplication works with real semantic embeddings."""
        from pydantic import BaseModel
        from ontomem.merger import MergeStrategy

        class KeywordItem(BaseModel):
            term: str
            category: str = None

        autoset = AutoSet(
            item_schema=KeywordItem,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.term.lower(),
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )

        # Add same term with different cases
        autoset.add(KeywordItem(term="Python", category="Language"))
        autoset.add(KeywordItem(term="python", category="Programming"))
        autoset.add(KeywordItem(term="JavaScript", category="Language"))

        # Should dedupe "Python" and "python"
        assert len(autoset) == 2
        assert "python" in autoset or "Python" in autoset
        assert "JavaScript" in autoset or "javascript" in autoset


class NodeSchema(BaseModel):
    """Node schema for knowledge graph."""
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type")


class EdgeSchema(BaseModel):
    """Edge schema for knowledge graph."""
    source: str = Field(description="Source entity name")
    target: str = Field(description="Target entity name")
    relation: str = Field(description="Relationship type")


class TestAutoGraphIntegration:
    """Integration tests for AutoGraph with real API."""

    def test_extract_knowledge_graph(self, llm_client, embedder):
        """Test extracting entities and relationships."""
        text = """
        Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.
        Steve Jobs served as CEO of Apple and introduced the iPhone.
        """

        autograph = AutoGraph(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        result = autograph.parse(text)

        # Should extract some entities
        assert len(result.nodes) > 0

        # Should have some relationships
        if len(result.edges) > 0:
            edge = result.edges[0]
            assert edge.source
            assert edge.target
            assert edge.relation

    def test_search_with_real_embeddings(self, llm_client, embedder):
        """Test semantic search with real embeddings."""
        text = """
        Tesla was founded by Elon Musk. The company produces electric vehicles
        and is headquartered in Austin, Texas. SpaceX, also founded by Musk,
        focuses on space exploration and rocket technology.
        """

        autograph = AutoGraph(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        result = autograph.parse(text)
        result.build_index()

        # Search should work with real embeddings
        nodes = result.search_nodes("electric cars", top_k=3)
        # Just verify search doesn't crash
        assert isinstance(nodes, (list, tuple))
