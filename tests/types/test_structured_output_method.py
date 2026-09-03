"""Structured extraction must request method="function_calling" (issue #52).

langchain-openai defaults to method="json_schema", which only OpenAI supports;
DeepSeek / vLLM / Ollama and other OpenAI-compatible endpoints reject it.
"""

from pydantic import BaseModel

from tests.mocks import MockEmbeddings, MockStructuredRunnable
from hyperknowledge.types import AutoModel, AutoGraph


class _Person(BaseModel):
    name: str


class _Entity(BaseModel):
    name: str
    type: str = "x"


class _Relation(BaseModel):
    source: str
    target: str


class _SpyLLM:
    """Records the `method` passed to each with_structured_output call."""

    def __init__(self):
        self.captured = []

    def with_structured_output(self, schema, **kwargs):
        self.captured.append(kwargs.get("method"))
        return MockStructuredRunnable(schema=schema)


def test_automodel_requests_function_calling():
    spy = _SpyLLM()
    AutoModel(data_schema=_Person, llm_client=spy, embedder=MockEmbeddings())
    assert spy.captured
    assert all(m == "function_calling" for m in spy.captured)


def test_autograph_two_stage_requests_function_calling():
    spy = _SpyLLM()
    AutoGraph(
        node_schema=_Entity,
        edge_schema=_Relation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=spy,
        embedder=MockEmbeddings(),
        extraction_mode="two_stage",
    )
    assert spy.captured
    assert all(m == "function_calling" for m in spy.captured)
