"""Unit tests for template parsers - loader."""

import pytest
import tempfile
import yaml
from pathlib import Path

from hyperknowledge.utils.template_engine.parsers import (
    load_template,
)
from hyperknowledge.utils.template_engine.parsers.loader import _localize_data


class TestLocalizeData:
    """_localize_data always returns a str, even for a missing language."""

    def test_missing_language_falls_back_to_en(self):
        assert _localize_data({"en": "Hello"}, "zh") == "Hello"

    def test_missing_language_and_no_en_returns_empty(self):
        assert _localize_data({"fr": "Bonjour"}, "zh") == ""

    def test_present_language_used(self):
        assert _localize_data({"en": "Hello", "zh": "你好"}, "zh") == "你好"


class TestLoadTemplate:
    """Test cases for load_template function."""

    def test_load_nonexistent_file_raises(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_template("/nonexistent/path/to/template.yaml")

    def test_load_existing_template(self):
        """Test loading an existing template from the gallery."""
        from hyperknowledge.utils.template_engine import Gallery

        template = Gallery.get("general/model")

        assert template is not None
        assert hasattr(template, "name")
        assert hasattr(template, "type")
        assert hasattr(template, "output")
