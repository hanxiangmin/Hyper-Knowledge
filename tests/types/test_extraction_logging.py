"""Tests for debug logging during knowledge extraction."""

import logging
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel, Field

from hyperknowledge.types.base import BaseAutoType
from hyperknowledge.types.graph import AutoGraph


class SimpleNode(BaseModel):
    name: str = Field(description="Entity name")
    description: str = Field(description="Entity description")


class SimpleEdge(BaseModel):
    source: str = Field(description="Source node key")
    target: str = Field(description="Target node key")
    relation: str = Field(description="Relation type")


def _make_mock_llm_and_embedder():
    """Create mock LLM and embedder for testing."""
    mock_llm = MagicMock()
    mock_llm.with_structured_output = MagicMock(return_value=mock_llm)
    mock_llm.invoke = MagicMock()
    mock_llm.batch = MagicMock(return_value=[])
    mock_embedder = MagicMock()
    mock_embedder.embed_documents = MagicMock(return_value=[])
    mock_embedder.embed_query = MagicMock(return_value=[])
    return mock_llm, mock_embedder


class LogCapture(logging.Handler):
    """Custom logging handler that captures log records."""

    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))


class TestBaseExtractionLogging:
    """Test that BaseAutoType._extract_data emits debug logs."""

    def test_extract_data_emits_debug_logs(self):
        """_extract_data should emit debug log messages at each stage."""
        handler = LogCapture()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("hyperknowledge.types.base")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        try:
            mock_llm, mock_embedder = _make_mock_llm_and_embedder()

            class TestSchema(BaseModel):
                items: list = []

            class TestAutoType(BaseAutoType):
                def _default_prompt(self):
                    return "Extract: {source_text}"

                @property
                def data(self):
                    return TestSchema()

                def empty(self):
                    return True

                def _init_data_state(self):
                    pass

                def _set_data_state(self, data):
                    pass

                def _update_data_state(self, data):
                    pass

                def _init_index_state(self):
                    pass

                def merge_batch_data(self, data_list):
                    return TestSchema()

                def build_index(self):
                    pass

                def search(self, query, top_k=3):
                    return []

                def dump_index(self, folder_path):
                    pass

                def load_index(self, folder_path):
                    pass

            mock_llm.invoke.return_value = TestSchema()
            ka = TestAutoType(
                data_schema=TestSchema,
                llm_client=mock_llm,
                embedder=mock_embedder,
                chunk_size=2048,
            )
            ka.feed_text("Test input text")
        finally:
            logger.removeHandler(handler)

        log_text = "\n".join(handler.messages)
        assert "stage=feed_text_start" in log_text
        assert "stage=extract_start" in log_text
        assert "stage=extract_complete" in log_text
        assert "stage=data_merged" in log_text


class TestGraphExtractionLogging:
    """Test that AutoGraph extraction emits debug logs."""

    def test_merge_batch_emits_debug_logs(self):
        """merge_batch_data should emit debug logs about merge stats."""
        handler = LogCapture()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("hyperknowledge.types.graph")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        try:
            mock_llm, mock_embedder = _make_mock_llm_and_embedder()

            ag = AutoGraph(
                node_schema=SimpleNode,
                edge_schema=SimpleEdge,
                node_key_extractor=lambda x: x.name,
                edge_key_extractor=lambda x: f"{x.source}-{x.relation}-{x.target}",
                nodes_in_edge_extractor=lambda x: (x.source, x.target),
                llm_client=mock_llm,
                embedder=mock_embedder,
                extraction_mode="one_stage",
                chunk_size=2048,
            )

            graph1 = ag.graph_schema(
                nodes=[SimpleNode(name="A", description="Node A")],
                edges=[SimpleEdge(source="A", target="B", relation="relates")],
            )
            graph2 = ag.graph_schema(
                nodes=[SimpleNode(name="B", description="Node B")],
                edges=[],
            )

            ag.merge_batch_data([graph1, graph2])
        finally:
            logger.removeHandler(handler)

        log_text = "\n".join(handler.messages)
        assert "stage=merge_batch_start" in log_text
        assert "stage=merge_batch_raw" in log_text
        assert "stage=merge_batch_complete" in log_text
