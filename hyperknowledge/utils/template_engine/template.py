"""Template API - Unified interface for template operations.

Provides a clean API for searching and creating knowledge extraction templates.
"""

from typing import Any
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from hyperknowledge.methods import get_method_cfg
from hyperknowledge.types.base import BaseAutoType

from .gallery import Gallery
from .parsers import TemplateCfg


class Template:
    """Template API - Unified interface for template operations.

    Usage Examples:
        from hyperknowledge.utils.template_engine import Template

        # Create template instance (2 ways)
        template = Template.create("general/graph", llm, emb)
        template = Template.create("/path/to/template.yaml", llm, emb)

        # Get template config by path
        config = Template.get("general/graph")

        # List all templates (returns Dict[str, TemplateCfg])
        all_templates = Template.list()

        # List templates with filters
        graph_templates = Template.list(filter_by_type="graph")
        zh_templates = Template.list(filter_by_language="zh")
    """

    @staticmethod
    def create(
        source: str,
        language: str | None = None,
        llm_client: BaseChatModel | None = None,
        embedder: Embeddings | None = None,
        **kwargs: Any,
    ) -> "BaseAutoType":
        """Create template instance.

        Args:
            source: Template path (e.g., "general/graph", "method/light_rag") or file path
            language: Language code (e.g., "zh", "en")
                - Required for knowledge templates
                - Ignored for method templates (always uses "en")
            llm_client: LLM client (reads from global config if not provided)
            embedder: Embedder client (reads from global config if not provided)
            **kwargs: Additional parameters

        Returns:
            AutoType instance

        Examples:
            # Knowledge template (language required)
            template = Template.create("general/graph", "zh", llm, emb)

            # Method template (language ignored, always "en")
            template = Template.create("method/light_rag", llm_client=llm, embedder=embedder)

            # By file path (language required)
            template = Template.create("/path/to/template.yaml", "zh", llm, emb)

            # For temporal/spatial templates
            template = Template.create(
                "finance/event_timeline",
                "zh",
                llm,
                emb,
                observation_time="2024-06-15"
            )
        """
        from .factory import TemplateFactory

        if llm_client is None or embedder is None:
            from hyperknowledge.utils import get_client

            default_llm, default_emb = get_client()
            llm_client = llm_client or default_llm
            embedder = embedder or default_emb

        return TemplateFactory.create(source, language, llm_client, embedder, **kwargs)

    @staticmethod
    def get(path: str) -> TemplateCfg | None:
        """Get template configuration by path.

        Args:
            path: Template path (e.g., "general/graph" or "method/light_rag")

        Returns:
            TemplateCfg or None if not found
        """
        if path.startswith("method/"):
            method_name = path[7:]
            return get_method_cfg(method_name)

        candidate = Path(path).expanduser()
        if candidate.is_file():
            from .parsers import load_template

            return load_template(candidate)

        return Gallery.get(path)

    @staticmethod
    def list(
        filter_by_query: str | None = None,
        filter_by_type: str | None = None,
        filter_by_tag: str | None = None,
        filter_by_language: str | None = None,
        include_methods: bool = True,
    ) -> dict[str, TemplateCfg]:
        """List templates with optional filters.

        Args:
            filter_by_query: Search in template name/description
            filter_by_type: Filter by autotype (e.g., "graph", "list", "model")
            filter_by_tag: Filter by tag
            filter_by_language: Filter by language (e.g., "zh", "en")
            include_methods: Whether to include method templates (default: True)

        Returns:
            Dict mapping template name to TemplateCfg
        """
        templates = Gallery.list(
            filter_by_query=filter_by_query,
            filter_by_type=filter_by_type,
            filter_by_tag=filter_by_tag,
            filter_by_language=filter_by_language,
        )

        if include_methods:
            from hyperknowledge.methods import list_method_cfgs

            method_templates = list_method_cfgs()
            templates.update(method_templates)

        return templates
