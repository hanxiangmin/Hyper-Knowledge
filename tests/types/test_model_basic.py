"""Unit tests for AutoModel basic functionality."""

from datetime import datetime, timedelta

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoModel
from tests.fixtures import PersonSchema, SHORT_TEXT


class TestAutoModelBasic:
    """Test cases for AutoModel basic functionality."""

    def test_init_and_empty_state(self, llm_client, embedder):
        """Test that AutoModel initializes correctly and reports empty state."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert model.empty() is True
        assert model.data is None

    def test_data_schema_property(self, llm_client, embedder):
        """Test that data_schema property returns correct schema."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert model.data_schema == PersonSchema

    def test_parse_returns_new_instance(self, llm_client, embedder):
        """Test that parse() returns a new instance with data."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        parsed = model.parse(SHORT_TEXT)

        assert parsed is not model
        assert parsed.empty() is False
        assert parsed.data is not None

    def test_feed_text_updates_state(self, llm_client, embedder):
        """Test that feed_text() updates the internal state."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert model.empty() is True

        model.feed_text(SHORT_TEXT)

        assert model.empty() is False
        assert model.data is not None

    def test_feed_text_returns_self(self, llm_client, embedder):
        """Test that feed_text() returns self for method chaining."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        result = model.feed_text(SHORT_TEXT)

        assert result is model

    def test_clear_resets_state(self, llm_client, embedder):
        """Test that clear() resets the model to empty state."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text(SHORT_TEXT)
        assert model.empty() is False

        model.clear()
        assert model.empty() is True

    def test_metadata_initialized(self, llm_client, embedder):
        """Test that metadata is initialized correctly."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert "created_at" in model.metadata
        assert "updated_at" in model.metadata
        assert model.metadata["created_at"] <= model.metadata["updated_at"]

    def test_metadata_updated_on_feed(self, llm_client, embedder):
        """Test that metadata is updated when feeding text."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        # Seed a known-past timestamp so the assertion does not depend on the
        # resolution of datetime.now(): with mocked clients feed_text can finish
        # within the same clock tick as construction, making the new timestamp
        # equal (not greater) and the test intermittently fail.
        past = datetime.now() - timedelta(seconds=1)
        model.metadata["updated_at"] = past

        model.feed_text(SHORT_TEXT)

        assert model.metadata["updated_at"] > past

    def test_create_empty_instance(self, llm_client, embedder):
        """Test that _create_empty_instance creates a properly configured instance."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=1024,
        )

        empty_instance = model._create_empty_instance()

        assert empty_instance.data_schema == model.data_schema
        assert empty_instance.chunk_size == model.chunk_size
        assert empty_instance.empty() is True
