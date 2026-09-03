"""Extraction tolerates LLM parse failures instead of crashing (issue #45)."""

from pydantic import BaseModel

from tests.mocks import MockChatModel, MockEmbeddings
from hyperknowledge.types import AutoModel


class _Person(BaseModel):
    name: str = ""


class _BoomExtractor:
    """Stands in for a data_extractor whose LLM returns unparseable output."""

    def invoke(self, _input, config=None):
        raise ValueError("Invalid JSON: expected value at line 1 column 1")

    def batch(self, inputs, config=None, return_exceptions=False, **kwargs):
        errs = [ValueError("Invalid JSON") for _ in inputs]
        if return_exceptions:
            return errs
        raise errs[0]


def _model():
    m = AutoModel(
        data_schema=_Person, llm_client=MockChatModel(), embedder=MockEmbeddings()
    )
    m.data_extractor = _BoomExtractor()
    return m


def test_parse_survives_single_chunk_failure():
    # text <= chunk_size -> invoke() path; a parse error yields an empty result
    result = _model().parse("short text")
    assert result.empty()


def test_parse_survives_multi_chunk_failure():
    # text > chunk_size -> batch() path
    result = _model().parse("sentence. " * 400)
    assert result.empty()
