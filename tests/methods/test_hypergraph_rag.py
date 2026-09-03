"""Unit tests for HyperGraph_RAG extraction edge cases."""

from unittest.mock import MagicMock

from hyperknowledge.methods.rag import HyperGraph_RAG


class TestHyperGraphRAGExtract:
    """Test cases for HyperGraph_RAG._extract_data."""

    def test_extract_data_handles_none_chunk(self, llm_client, embedder):
        """A None result from the edge extractor must not crash extraction.

        batch()/invoke() can return None when LLM extraction fails for a chunk.
        Previously `_extract_data` accessed `raw_hyperedges.items` directly,
        raising AttributeError on None.
        """
        graph = HyperGraph_RAG(llm_client=llm_client, embedder=embedder)

        # Simulate the extractor failing for the (single) chunk.
        graph.edge_extractor = MagicMock()
        graph.edge_extractor.invoke.return_value = None

        result = graph._extract_data("A short sentence.")

        assert result.nodes == []
        assert result.edges == []
