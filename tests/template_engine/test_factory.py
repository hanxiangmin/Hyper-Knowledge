"""Unit tests for TemplateFactory."""

import pytest
from pathlib import Path

from hyperknowledge.utils.template_engine import TemplateFactory, Gallery


class TestTemplateFactoryCreate:
    """Test cases for TemplateFactory create methods."""

    def test_get_existing_template(self):
        """Test getting an existing template from gallery."""
        template = Gallery.get("general/model")

        assert template is not None
        assert template.name == "model"
        assert template.type in ["model", "list", "set", "graph"]

    def test_get_nonexistent_template(self):
        """Test getting a nonexistent template returns None."""
        template = Gallery.get("nonexistent/template")

        assert template is None


class TestTemplateFactoryCreateMethod:
    """Test cases for TemplateFactory create method."""

    def test_create_with_language(self, llm_client, embedder):
        """Test create() with language parameter."""
        result = TemplateFactory.create(
            source="general/model",
            language="en",
            llm_client=llm_client,
            embedder=embedder,
        )

        assert result is not None
        assert result.metadata.get("lang") == "en"

    def test_create_without_source_raises(self, llm_client, embedder):
        """Test that create() raises error without source."""
        with pytest.raises((ValueError, TypeError)):
            TemplateFactory.create(
                llm_client=llm_client,
                embedder=embedder,
            )

    def test_create_from_templatecfg_instance(self, llm_client, embedder):
        """create() accepts a TemplateCfg instance (documented + typed source)."""
        cfg = Gallery.get("general/model")

        result = TemplateFactory.create(cfg, "en", llm_client, embedder)

        assert result is not None
        assert result.metadata["template"] == cfg.name
        assert result.metadata["lang"] == "en"

    def test_create_method_template(self, llm_client, embedder):
        """Test creating a method template."""
        result = TemplateFactory.create(
            source="method/light_rag",
            llm_client=llm_client,
            embedder=embedder,
        )

        assert result is not None


class TestTemplateFactoryCreateAllTypes:
    """Test cases for creating all AutoType types."""

    def test_create_model_type(self, llm_client, embedder):
        """Test create() with model type template."""
        result = TemplateFactory.create(
            source="general/model",
            language="en",
            llm_client=llm_client,
            embedder=embedder,
        )

        from hyperknowledge.types import AutoModel
        assert isinstance(result, AutoModel)
        assert result.metadata.get("type") == "model"

    def test_create_list_type(self, llm_client, embedder):
        """Test create() with list type template."""
        result = TemplateFactory.create(
            source="general/list",
            language="en",
            llm_client=llm_client,
            embedder=embedder,
        )

        from hyperknowledge.types import AutoList
        assert isinstance(result, AutoList)
        assert result.metadata.get("type") == "list"

    def test_create_set_type(self, llm_client, embedder):
        """Test create() with set type template."""
        result = TemplateFactory.create(
            source="general/set",
            language="en",
            llm_client=llm_client,
            embedder=embedder,
        )

        from hyperknowledge.types import AutoSet
        assert isinstance(result, AutoSet)
        assert result.metadata.get("type") == "set"

    def test_create_graph_type(self, llm_client, embedder):
        """Test create() with graph type template."""
        result = TemplateFactory.create(
            source="general/graph",
            language="en",
            llm_client=llm_client,
            embedder=embedder,
        )

        from hyperknowledge.types import AutoGraph
        assert isinstance(result, AutoGraph)
        assert result.metadata.get("type") == "graph"
