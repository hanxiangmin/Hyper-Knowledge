"""Template Factory - Dynamically creates template instances from configuration.

Supports all 8 AutoType dynamic generation.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from .parsers import (
    TemplateCfg,
    localize_template,
    parse_display,
    parse_guideline,
    parse_identifiers,
    parse_option,
    parse_output,
)

if TYPE_CHECKING:
    from hyperknowledge.types import (
        AutoGraph,
        AutoHypergraph,
        AutoList,
        AutoModel,
        AutoSet,
        AutoSpatialGraph,
        AutoSpatioTemporalGraph,
        AutoTemporalGraph,
    )


class TemplateFactory:
    @classmethod
    def create_method(
        cls,
        method_name: str,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ):
        """Create method template instance.

        Note: Method templates use English prompts only.
        Language is hardcoded to "en" in metadata.

        Args:
            method_name: Method name (e.g., "light_rag", "hyper_rag")
            llm_client: LLM client
            embedder: Embedding model
            **kwargs: Additional parameters passed to the method constructor

        Returns:
            AutoType instance

        Examples:
            # Create Light_RAG method
            template = TemplateFactory.create_method("light_rag", llm, embedder)

            # Create Atom method with observation_time
            template = TemplateFactory.create_method(
                "atom", llm, embedder, observation_time="2024-06-15"
            )
        """
        from hyperknowledge.methods.registry import get_method

        method_info = get_method(method_name)
        if method_info is None:
            raise ValueError(f"Unknown method: {method_name}")

        method_class = method_info["class"]
        autotype = method_info["type"]

        instance = method_class(
            llm_client=llm_client,
            embedder=embedder,
            **kwargs,
        )

        instance.metadata["template"] = f"method/{method_name}"
        instance.metadata["lang"] = "en"
        instance.metadata["type"] = autotype

        return instance

    @classmethod
    def create_model(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoModel":
        """Create AutoModel template."""
        from hyperknowledge.types import AutoModel

        data_schema = parse_output(config.output, config.type)
        prompt = parse_guideline(config.guideline, config.type, config.language)
        options = parse_option(config.options, config.type, override=kwargs)
        label_extractor = parse_display(config.display, config.type)

        return AutoModel(
            data_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            label_extractor=label_extractor,
            **options,
        )

    @classmethod
    def create_list(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoList":
        """Create AutoList template."""
        from hyperknowledge.types import AutoList

        data_schema = parse_output(config.output, config.type)
        prompt = parse_guideline(config.guideline, config.type, config.language)
        options = parse_option(config.options, config.type, override=kwargs)
        item_label_extractor = parse_display(config.display, config.type)

        return AutoList(
            item_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            item_label_extractor=item_label_extractor,
            **options,
        )

    @classmethod
    def create_set(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoSet":
        """Create AutoSet template."""
        from hyperknowledge.types import AutoSet

        data_schema = parse_output(config.output, config.type)
        item_id_extractor = parse_identifiers(config.identifiers, config.type)
        prompt = parse_guideline(config.guideline, config.type, config.language)
        options = parse_option(config.options, config.type, override=kwargs)
        item_label_extractor = parse_display(config.display, config.type)

        return AutoSet(
            item_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=item_id_extractor,
            item_label_extractor=item_label_extractor,
            prompt=prompt,
            **options,
        )

    @classmethod
    def create_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoGraph":
        """Create AutoGraph template."""
        from hyperknowledge.types import AutoGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        entity_key_extractor, relation_key_extractor, entities_in_relation_extractor = (
            identifiers
        )
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type, config.language)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_hypergraph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoHypergraph":
        """Create AutoHypergraph template."""
        from hyperknowledge.types import AutoHypergraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        entity_key_extractor, relation_key_extractor, entities_in_relation_extractor = (
            identifiers
        )
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type, config.language)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoHypergraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_temporal_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoTemporalGraph":
        from hyperknowledge.types import AutoTemporalGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        (
            entity_key_extractor,
            relation_key_extractor,
            entities_in_relation_extractor,
            time_in_edge_extractor,
        ) = parse_identifiers(config.identifiers, config.type)

        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type, config.language)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoTemporalGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            llm_client=llm_client,
            embedder=embedder,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            time_in_edge_extractor=time_in_edge_extractor,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_spatial_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoSpatialGraph":
        """Create AutoSpatialGraph template."""
        from hyperknowledge.types import AutoSpatialGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        (
            entity_key_extractor,
            relation_key_extractor,
            entities_in_relation_extractor,
            location_in_edge_extractor,
        ) = identifiers
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type, config.language)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoSpatialGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            location_in_edge_extractor=location_in_edge_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_spatio_temporal_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoSpatioTemporalGraph":
        """Create AutoSpatioTemporalGraph template."""
        from hyperknowledge.types import AutoSpatioTemporalGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        (
            entity_key_extractor,
            relation_key_extractor,
            entities_in_relation_extractor,
            time_in_edge_extractor,
            location_in_edge_extractor,
        ) = identifiers
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type, config.language)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoSpatioTemporalGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            time_in_edge_extractor=time_in_edge_extractor,
            location_in_edge_extractor=location_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create(
        cls,
        source: str | TemplateCfg,
        language: str | None = None,
        llm_client: BaseChatModel = None,
        embedder: Embeddings = None,
        **kwargs,
    ):
        """Create template instance based on configuration.

        Supports both knowledge templates and method templates:
        - Knowledge templates: "general/graph", "/path/to/template.yaml"
        - Method templates: "method/light_rag", "method/hyper_rag"

        Args:
            source: Template source - can be:
                - str: Template name (e.g., "graph", "method/light_rag") or file path
                - TemplateCfg: Template configuration instance
            language: Language code for localization (e.g., 'zh', 'en')
                - Required for knowledge templates
                - Ignored for method templates (always uses "en")
            llm_client: LLM client
            embedder: Embedding model
            **kwargs: Additional parameters to override config parameters
                e.g., observation_time="2024-06-15", observation_location="Beijing"

        Returns:
            AutoType instance

        Examples:
            # Knowledge template by name (language required)
            template = TemplateFactory.create("general/graph", "zh", llm, embedder)

            # Method template (language ignored, always "en")
            template = TemplateFactory.create("method/light_rag", llm=llm, embedder=embedder)

            # By file path (language required)
            template = TemplateFactory.create("/path/to/template.yaml", "zh", llm, embedder)

            # By TemplateCfg instance (language required)
            template = TemplateFactory.create(config, "zh", llm, embedder)

            # For spatio-temporal templates, pass observation_time etc.
            template = TemplateFactory.create(
                "FinancialTemporalGraph",
                "zh",
                llm,
                embedder,
                observation_time="2024-06-15",
                observation_location="Beijing"
            )

            # For method templates with specific parameters
            template = TemplateFactory.create(
                "method/atom",
                llm=llm,
                embedder=embedder,
                observation_time="2024-06-15"
            )
        """
        if isinstance(source, str) and source.startswith("method/"):
            method_name = source[7:]
            return cls.create_method(method_name, llm_client, embedder, **kwargs)

        if language is None:
            raise ValueError(
                "language is required for knowledge templates. "
                "Provide a language code (e.g., 'zh', 'en')."
            )

        from .gallery import Gallery
        from .parsers import load_template

        match source:
            case str() as s if s.endswith(".yaml") or Path(s).exists():
                template_cfg = load_template(s)
            case str() as s:
                template_cfg = Gallery.get(s)
            case TemplateCfg() as cfg:
                template_cfg = cfg
            case _:
                raise ValueError("Invalid source: must be a template path or file path")

        if template_cfg is None:
            raise ValueError(f"Template not found: {source}")

        template_cfg = localize_template(template_cfg, language)

        match template_cfg.type:
            case "model":
                template = cls.create_model(
                    template_cfg, llm_client, embedder, **kwargs
                )
            case "list":
                template = cls.create_list(template_cfg, llm_client, embedder, **kwargs)
            case "set":
                template = cls.create_set(template_cfg, llm_client, embedder, **kwargs)
            case "graph":
                template = cls.create_graph(
                    template_cfg, llm_client, embedder, **kwargs
                )
            case "hypergraph":
                template = cls.create_hypergraph(
                    template_cfg, llm_client, embedder, **kwargs
                )
            case "temporal_graph":
                template = cls.create_temporal_graph(
                    template_cfg, llm_client, embedder, **kwargs
                )
            case "spatial_graph":
                template = cls.create_spatial_graph(
                    template_cfg, llm_client, embedder, **kwargs
                )
            case "spatio_temporal_graph":
                template = cls.create_spatio_temporal_graph(
                    template_cfg, llm_client, embedder, **kwargs
                )

        if isinstance(source, str):
            template.metadata["template"] = (
                Path(source).stem if source.endswith(".yaml") else source
            )
        else:
            template.metadata["template"] = source.name
        template.metadata["lang"] = language
        template.metadata["type"] = template_cfg.type

        return template
