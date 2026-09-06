"""Every documented dataset-template pairing must remain executable offline."""

from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin

import pytest
import yaml
from pydantic import BaseModel
from ontomem.merger import create_merger

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

    def _generate_mock_instance(self, model_cls: type[BaseModel]) -> BaseModel:
        # This fixture exercises optional member fields too. The general mock
        # intentionally leaves Optional[T] empty, which cannot exercise a
        # role-aware event whose individual roles are all optional.
        return model_cls(
            **{
                name: self._generate_value_for_type(
                    field.annotation, get_origin(field.annotation), name
                )
                for name, field in model_cls.model_fields.items()
            }
        )

    def _generate_value_for_type(
        self, field_type: type, origin: Any, field_name: str
    ) -> Any:
        if origin in (Union, UnionType):
            concrete = next(
                (arg for arg in get_args(field_type) if arg is not type(None)), str
            )
            return self._generate_value_for_type(
                concrete, get_origin(concrete), field_name
            )
        if origin is list:
            args = get_args(field_type)
            if args and args[0] is str:
                return ["mock_entity", "mock_entity_alt"]
            if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                first = self._generate_mock_instance(args[0])
                second = first.model_copy(
                    update={
                        name: "mock_entity_alt"
                        for name, value in first.model_dump().items()
                        if value == "mock_entity"
                    }
                )
                return [first, second]
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
    if extractor.metadata["type"] == "hypergraph":
        # The generic canned model cannot preserve a requested identity during
        # LLM merge prompts. This topology smoke test uses exact-key merging;
        # merger strategies have their own tests.
        extractor.node_merger = create_merger(
            strategy="keep_existing",
            item_schema=extractor.node_schema,
            key_extractor=extractor.node_key_extractor,
        )
        extractor.edge_merger = create_merger(
            strategy="keep_existing",
            item_schema=extractor.edge_schema,
            key_extractor=extractor.edge_key_extractor,
        )
    extractor.feed_text(dataset.read_text(encoding="utf-8"))
    assert extractor.metadata["template"] == case["template"]

    if extractor.metadata["type"] == "hypergraph":
        assert len(extractor.edges) >= 1
        assert all(
            len(set(extractor.nodes_in_edge_extractor(edge))) >= 2
            for edge in extractor.edges
        )


def test_matrix_is_versioned_and_has_thirty_unique_cases():
    assert MATRIX["schema_version"] == "hk.template-dataset-matrix/v1"
    assert len(MATRIX["cases"]) == 30
    assert len({(case["template"], case["dataset"]) for case in MATRIX["cases"]}) == 30
