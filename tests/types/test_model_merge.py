"""Unit tests for AutoModel merge functionality."""

import os
import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoModel
from tests.fixtures import BiographySchema


class SimpleSchema(BaseModel):
    """Simple schema for testing merge functionality."""

    name: str
    age: Optional[int] = None
    occupation: Optional[str] = None


class TestAutoModelMerge:
    """Test cases for AutoModel merge functionality."""

    def test_merge_batch_data_single_item(self, llm_client, embedder):
        """Test merge_batch_data with a single item."""
        model = AutoModel(
            data_schema=SimpleSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        item = SimpleSchema(name="John", age=30)
        result = model.merge_batch_data([item])

        assert result.name == "John"
        assert result.age == 30

    def test_merge_batch_data_empty_list(self, llm_client, embedder):
        """Test merge_batch_data with empty list."""
        model = AutoModel(
            data_schema=SimpleSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        result = model.merge_batch_data([])

        assert result is None

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires real LLM")
    def test_merge_batch_data_multiple_items(self, llm_client, embedder):
        """Test merge_batch_data with multiple items."""
        model = AutoModel(
            data_schema=SimpleSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        item1 = SimpleSchema(name="John", age=30)
        item2 = SimpleSchema(name="John", age=31, occupation="Engineer")
        item3 = SimpleSchema(name="John", occupation="Developer")

        result = model.merge_batch_data([item1, item2, item3])

        assert result.name == "John"

    def test_feed_text_multiple_times(self, llm_client, embedder):
        """Test that feeding text multiple times updates the data."""
        model = AutoModel(
            data_schema=SimpleSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John is 30 years old.")
        first_data = model.data

        model.feed_text("John works as an engineer.")
        second_data = model.data

        assert second_data is not None

    def test_parse_creates_separate_instance(self, llm_client, embedder):
        """Test that parse() creates instances that don't share state."""
        model = AutoModel(
            data_schema=SimpleSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        parsed1 = model.parse("John is 30 years old.")
        parsed2 = model.parse("Jane is 25 years old.")

        assert parsed1.data is not parsed2.data


class TestAutoModelWithComplexSchema:
    """Test AutoModel with more complex schemas."""

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires real LLM")
    def test_with_biography_schema(self, llm_client, embedder):
        """Test AutoModel with BiographySchema."""
        model = AutoModel(
            data_schema=BiographySchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        result = model.parse(
            "Albert Einstein was born in 1879 in Ulm, Germany. "
            "He was a theoretical physicist who developed the theory of relativity."
        )

        assert result.empty() is False
        assert result.data.name == "Albert Einstein"

    def test_empty_optional_fields(self, llm_client, embedder):
        """Test that empty optional fields are handled correctly."""

        class MinimalSchema(BaseModel):
            name: str
            description: Optional[str] = None

        model = AutoModel(
            data_schema=MinimalSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        parsed = model.parse("Someone named John.")

        assert parsed.empty() is False
        assert parsed.data.name is not None
