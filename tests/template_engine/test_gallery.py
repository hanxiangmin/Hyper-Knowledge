"""Unit tests for Gallery."""

import pytest

from hyperknowledge.utils.template_engine import Gallery


class TestGalleryGet:
    """Test cases for Gallery.get() method."""

    def test_get_existing_template_by_path(self):
        """Test getting an existing template by full path."""
        template = Gallery.get("general/model")

        assert template is not None
        assert hasattr(template, "name")
        assert hasattr(template, "type")

    def test_get_existing_template_by_name(self):
        """Test getting an existing template by name only."""
        template = Gallery.get("model")

        assert template is not None

    def test_get_nonexistent_template(self):
        """Test getting a nonexistent template."""
        template = Gallery.get("nonexistent/template/that/does/not/exist")

        assert template is None

    def test_get_template_preserves_config(self):
        """Test that getting a template preserves its configuration."""
        template = Gallery.get("general/model")

        assert template is not None
        assert hasattr(template, "type")
        assert hasattr(template, "output")
        assert hasattr(template, "guideline")


class TestGalleryList:
    """Test cases for Gallery.list() method."""

    def test_list_all_templates(self):
        """Test listing all templates."""
        templates = Gallery.list()

        assert isinstance(templates, dict)
        assert len(templates) > 0

    def test_filter_by_type_model(self):
        """Test filtering templates by model type."""
        templates = Gallery.list(filter_by_type="model")

        assert isinstance(templates, dict)
        for template in templates.values():
            assert template.type == "model"

    def test_filter_by_type_list(self):
        """Test filtering templates by list type."""
        templates = Gallery.list(filter_by_type="list")

        assert isinstance(templates, dict)
        for template in templates.values():
            assert template.type == "list"

    def test_filter_by_type_set(self):
        """Test filtering templates by set type."""
        templates = Gallery.list(filter_by_type="set")

        assert isinstance(templates, dict)
        for template in templates.values():
            assert template.type == "set"

    def test_filter_by_type_graph(self):
        """Test filtering templates by graph type."""
        templates = Gallery.list(filter_by_type="graph")

        assert isinstance(templates, dict)
        for template in templates.values():
            assert template.type == "graph"

    def test_filter_by_language_en(self):
        """Test filtering templates by English language."""
        templates = Gallery.list(filter_by_language="en")

        assert isinstance(templates, dict)

    def test_filter_by_language_zh(self):
        """Test filtering templates by Chinese language."""
        templates = Gallery.list(filter_by_language="zh")

        assert isinstance(templates, dict)

    def test_filter_by_query(self):
        """Test filtering templates by query."""
        templates = Gallery.list(filter_by_query="model")

        assert isinstance(templates, dict)

    def test_filter_by_type_and_language(self):
        """Test filtering by both type and language."""
        templates = Gallery.list(filter_by_type="model", filter_by_language="en")

        assert isinstance(templates, dict)
        for template in templates.values():
            assert template.type == "model"

    def test_filter_by_tag(self):
        """Test filtering templates by tag."""
        templates = Gallery.list(filter_by_tag="general")

        assert isinstance(templates, dict)


class TestGalleryMultiple:
    """Test cases for Gallery with multiple templates."""

    def test_multiple_template_types(self):
        """Test that multiple template types are available."""
        model_templates = Gallery.list(filter_by_type="model")
        list_templates = Gallery.list(filter_by_type="list")
        set_templates = Gallery.list(filter_by_type="set")
        graph_templates = Gallery.list(filter_by_type="graph")

        total_templates = (
            len(model_templates)
            + len(list_templates)
            + len(set_templates)
            + len(graph_templates)
        )

        all_templates = Gallery.list()
        assert total_templates <= len(all_templates)

    def test_preserves_original_config(self):
        """Test that template config is preserved when filtering."""
        template = Gallery.get("general/model")

        if template is None:
            pytest.skip("Template not available")

        templates = Gallery.list(filter_by_type=template.type)

        assert len(templates) > 0
        for key, t in templates.items():
            assert t.type == template.type
