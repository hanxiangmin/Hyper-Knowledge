"""Every documented dataset-template pairing must remain executable offline."""

from pathlib import Path
from typing import Any, get_args

import pytest
import yaml

from hyperknowledge import Template
from tests.mocks import MockChatModel, MockEmbeddings, MockStructuredRunnable


PROJECT = Path(__file__).parents[2]
MATRIX_PATH = PROJECT / "examples" / "template_dataset_matrix.yaml"
MATRIX = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
CASES = [
    {**case, "language": language}
    for case in MATRIX["cases"]
    for language in ("en", "zh")
]


class ConsistentStructuredRunnable(MockStructuredRunnable):
    """Produce compatible node and relation identifiers for topology smoke tests."""

    def _generate_value_for_type(
        self, field_type: type, origin: Any, field_name: str
    ) -> Any:
        if origin is list:
            args = get_args(field_type)
            if args and args[0] is str:
                return ["mock_entity", "mock_entity"]
        if field_type is str:
            return "mock_entity"
        return super()._generate_value_for_type(field_type, origin, field_name)


class ConsistentMockChatModel(MockChatModel):
    def with_structured_output(self, schema: type, **kwargs: Any):
        return ConsistentStructuredRunnable(schema=schema)


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=lambda case: f"{case['language']}:{case['template']}",
)
def test_each_documented_template_dataset_case_runs_without_network(case):
    dataset = PROJECT / "tests" / "test_data" / case["language"] / case["dataset"]
    assert dataset.is_file()
    extractor = Template.create(
        case["template"],
        language=case["language"],
        llm_client=ConsistentMockChatModel(),
        embedder=MockEmbeddings(dim=8),
    )
    extractor.feed_text(dataset.read_text(encoding="utf-8"))
    assert extractor.metadata["template"] == case["template"]

    if extractor.metadata["type"] == "hypergraph":
        assert len(extractor.edges) >= 1
        assert all(
            len(extractor.nodes_in_edge_extractor(edge)) >= 2
            for edge in extractor.edges
        )


def test_matrix_is_versioned_and_has_thirty_unique_cases():
    assert MATRIX["schema_version"] == "hk.template-dataset-matrix/v1"
    assert len(MATRIX["cases"]) == 30
    assert len({(case["template"], case["dataset"]) for case in MATRIX["cases"]}) == 30
