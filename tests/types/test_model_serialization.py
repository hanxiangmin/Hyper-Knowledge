"""Unit tests for AutoModel serialization functionality."""

import json
import os
import tempfile
import shutil
from pathlib import Path

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoModel
from tests.fixtures import PersonSchema


class TestAutoModelSerialization:
    """Test cases for AutoModel serialization and deserialization."""

    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary directory after each test."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_dump_data_creates_file(self, llm_client, embedder):
        """Test that dump_data() creates a JSON file."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John Smith is a software engineer at TechCorp.")

        file_path = Path(self.temp_dir) / "data.json"
        model.dump_data(file_path)

        assert file_path.exists()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires real LLM")
    def test_dump_data_contains_correct_data(self, llm_client, embedder):
        """Test that dumped data contains correct information."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John Smith is a software engineer at TechCorp.")

        file_path = Path(self.temp_dir) / "data.json"
        model.dump_data(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "name" in data
        assert data["name"] == "John Smith"

    def test_load_data_restores_state(self, llm_client, embedder):
        """Test that load_data() restores the model state."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John Smith is a software engineer at TechCorp.")

        data_file = Path(self.temp_dir) / "data.json"
        model.dump_data(data_file)

        new_model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert new_model.empty() is True

        new_model.load_data(data_file)

        assert new_model.empty() is False

    def test_load_data_raises_on_missing_file(self, llm_client, embedder):
        """Test that load_data() raises FileNotFoundError for missing files."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        with pytest.raises(FileNotFoundError):
            model.load_data(Path(self.temp_dir) / "nonexistent.json")

    def test_dump_metadata(self, llm_client, embedder):
        """Test that dump_metadata() works correctly."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        file_path = Path(self.temp_dir) / "metadata.json"
        model.dump_metadata(file_path)

        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        assert "created_at" in metadata
        assert "updated_at" in metadata

    def test_load_metadata(self, llm_client, embedder):
        """Test that load_metadata() restores metadata."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John Smith is a software engineer at TechCorp.")

        metadata_file = Path(self.temp_dir) / "metadata.json"
        model.dump_metadata(metadata_file)

        new_model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        new_model.load_metadata(metadata_file)

        assert "created_at" in new_model.metadata
        assert "updated_at" in new_model.metadata

    def test_load_metadata_restores_datetime_type(self, llm_client, embedder):
        """Loaded timestamps are datetime objects, not ISO strings.

        dump_metadata serializes datetimes via default=str; without conversion
        on load, a loaded instance keeps strings while a fresh one holds
        datetimes, so min(created_at, ...) in __add__ would raise TypeError.
        """
        from datetime import datetime

        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        metadata_file = Path(self.temp_dir) / "metadata.json"
        model.dump_metadata(metadata_file)

        new_model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )
        new_model.load_metadata(metadata_file)

        assert isinstance(new_model.metadata["created_at"], datetime)
        assert isinstance(new_model.metadata["updated_at"], datetime)
        # The real-world manifestation: comparing loaded vs fresh must not raise.
        assert min(new_model.metadata["created_at"], datetime.now())

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires real LLM")
    def test_dump_and_load_full(self, llm_client, embedder):
        """Test full dump/load cycle."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John Smith is a software engineer at TechCorp.")

        model.dump(self.temp_dir)

        new_model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        new_model.load(self.temp_dir)

        assert new_model.empty() is False
        assert new_model.data.name == "John Smith"

    def test_dump_creates_directory(self, llm_client, embedder):
        """Test that dump() creates the directory if it doesn't exist."""
        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        model.feed_text("John Smith is a software engineer.")

        new_dir = Path(self.temp_dir) / "new_subdir" / "nested"
        model.dump(new_dir)

        assert new_dir.exists()
        assert (new_dir / "data.json").exists()
