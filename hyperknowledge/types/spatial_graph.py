"""Generic spatial graph implementation supporting custom schemas with location-aware extraction."""

from collections.abc import Callable
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import BaseMerger, MergeStrategy

from .graph import (
    AutoGraph,
    EdgeListSchema,
    EdgeSchema,
    NodeListSchema,
    NodeSchema,
)

# ==============================================================================
# Prompt Definition - Spatial "Sandwich" Injection
# ==============================================================================

# Node Extraction Prompts
DEFAULT_SPATIAL_NODE_ROLE_PREFIX = """
You are a professional entity extraction specialist.
Your task is to extract all important entities (Nodes) from the text.
"""

DEFAULT_SPATIAL_NODE_RULES_SUFFIX = """
# Core Principles
1. **Comprehensiveness**: Extract persons, organizations, facilities, events, and objects.
2. **Accuracy**: Keep entity names consistent with the source text.
3. **Exclude Spatial Markers**: **NEVER** extract locations or directions (e.g., "Room 101", "North") as entity nodes!
   Spatial context belongs to the relationships between entities.

### Source Text:
{source_text}
"""

# Edge Extraction Prompts
DEFAULT_SPATIAL_EDGE_ROLE_PREFIX = """
You are an expert spatial knowledge extraction specialist.
Extract meaningful relationships (edges) between the provided entities, specifically capturing WHERE they occur.
"""

DEFAULT_SPATIAL_EDGE_RULES_SUFFIX = """
### Spatial Extraction Rules
Current Observation Location: {observation_location}

1. **Relative Location Resolution**: You MUST resolve relative location expressions based on the Observation Location.
   - "here", "local", "this place" -> {observation_location}
   - "nearby", "adjacent" -> In the vicinity of {observation_location}
   - "north of here" -> North of {observation_location}

2. **Explicit Locations**: Keep explicit addresses or room names consistent with the source text.

3. **Missing Location**: If no location information is present, leave location fields empty. DO NOT hallucinate.

### General Constraints
1. ONLY extract edges connecting entities from the known entity list provided below.
2. DO NOT create edges involving entities that are not listed.
3. Use the defined schema fields for location as specified in the output format.

# Provided Entities
{known_nodes}

# Source Text:
{source_text}
"""

# One-Stage Graph Extraction Prompts
DEFAULT_SPATIAL_GRAPH_ROLE_PREFIX = """
You are a professional spatial knowledge graph extraction specialist.
Your task is to extract entities (Nodes) and spatial relationships (Edges) from the text.
"""

DEFAULT_SPATIAL_GRAPH_RULES_SUFFIX = """
# Core Principles for Nodes
1. Extract persons, organizations, facilities, and objects.
2. **NEVER** extract locations as independent nodes. Location is an attribute of the relationship.

# Core Principles for Edges
Current Observation Location: {observation_location}

1. **Relative Location Resolution**: Resolve relative location expressions based on {observation_location}.
2. **Explicit Locations**: Keep explicit locations exactly as written.
3. **Missing Space**: Leave location fields empty if not present.

### Source Text:
{source_text}
"""


class AutoSpatialGraph(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Generic Spatial Graph Extractor (AutoSpatialGraph).

    A flexible implementation supporting user-defined Node and Edge schemas with spatial awareness:
    - **Schema Agnosticism**: Support any user-defined Node and Edge Pydantic models.
    - **Location-Aware Deduplication**: Spatial information is integrated into edge deduplication.
    - **Dynamic Localization**: Observation Location is injected during extraction for relative resolution.

    Key Design:
    - Decoupled Extractors: `location_in_edge_extractor` is a separate function.
    - Spatial Identity: Edges are uniquely identified by (source, relation, target) + location.

    Example:
        >>> from pydantic import BaseModel, Field
        >>>
        >>> class MyEntity(BaseModel):
        ...     name: str
        ...
        >>> class MySpatialEdge(BaseModel):
        ...     src: str
        ...     dst: str
        ...     relation: str
        ...     place: Optional[str] = None
        >>>
        >>> kg = AutoSpatialGraph(
        ...     node_schema=MyEntity,
        ...     edge_schema=MySpatialEdge,
        ...     node_key_extractor=lambda x: x.name,
        ...     edge_key_extractor=lambda x: f"{x.src}|{x.relation}|{x.dst}",
        ...     location_in_edge_extractor=lambda x: x.place or "",
        ...     nodes_in_edge_extractor=lambda x: (x.src, x.dst),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     observation_location="Main Hall"
        ... )
    """

    def __init__(
        self,
        node_schema: type[NodeSchema],
        edge_schema: type[EdgeSchema],
        node_key_extractor: Callable[[NodeSchema], str],
        edge_key_extractor: Callable[[EdgeSchema], str],
        location_in_edge_extractor: Callable[[EdgeSchema], str],
        nodes_in_edge_extractor: Callable[[EdgeSchema], tuple[str, str]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_location: str | None = None,
        extraction_mode: str = "two_stage",
        node_strategy_or_merger: "MergeStrategy | BaseMerger" = MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger: "MergeStrategy | BaseMerger" = MergeStrategy.LLM.BALANCED,
        prompt_for_node_extraction: str = "",
        prompt_for_edge_extraction: str = "",
        prompt: str = "",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        node_fields_for_index: list[str] | None = None,
        edge_fields_for_index: list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize AutoSpatialGraph.

        Args:
            node_schema: User-defined Node Pydantic model.
            edge_schema: User-defined Edge Pydantic model with location fields.
            node_key_extractor: Function to extract unique key from node.
            edge_key_extractor: Function to extract the base unique identifier for an edge.
            location_in_edge_extractor: Function to extract the spatial component from an edge.
            nodes_in_edge_extractor: Function to extract (source_key, target_key) from edge.
            llm_client: LangChain BaseChatModel for extraction.
            embedder: LangChain Embeddings for semantic operations.
            observation_location: Location context for spatial resolution (default: "Unknown Location").
            extraction_mode: "one_stage" or "two_stage" (default: "two_stage").
            node_strategy_or_merger: Merge strategy for duplicate nodes (default: LLM.BALANCED).
            edge_strategy_or_merger: Merge strategy for duplicate edges (default: LLM.BALANCED).
            prompt_for_node_extraction: Additional user prompt to append to node extraction system prompt.
            prompt_for_edge_extraction: Additional user prompt to append to edge extraction system prompt.
            prompt: Additional user prompt to append to one-stage graph extraction system prompt.
            chunk_size: Size of text chunks for processing (default: 2048).
            chunk_overlap: Overlap between text chunks (default: 256).
            max_workers: Maximum number of concurrent LLM calls (default: 10).
            verbose: Whether to print verbose output (default: False).
            node_fields_for_index: List of node fields to include in vector index (optional).
            edge_fields_for_index: List of edge fields to include in vector index (optional).
            **kwargs: Additional arguments passed to create_merger() when strategy_or_merger is
                      a MergeStrategy enum. Ignored if strategy_or_merger is a BaseMerger instance.
        """
        # Set observation location
        self.observation_location = observation_location or "Unknown Location"
        self._constructor_kwargs = kwargs

        # Store extractors
        self.raw_edge_key_extractor = edge_key_extractor
        self.location_in_edge_extractor = location_in_edge_extractor

        # Create composite extractor for unique identification in memory
        def spatial_edge_key_extractor(edge: EdgeSchema) -> str:
            raw_key = self.raw_edge_key_extractor(edge)
            loc_val = self.location_in_edge_extractor(edge)
            return f"{raw_key} at {loc_val}" if loc_val else raw_key

        # -----------------------------------------------------------
        # Construct Prompts
        # -----------------------------------------------------------

        # 1. Node Extraction Prompt
        full_node_prompt = DEFAULT_SPATIAL_NODE_ROLE_PREFIX
        if prompt_for_node_extraction:
            full_node_prompt += (
                f"\n### Context & Instructions:\n{prompt_for_node_extraction}\n"
            )
        full_node_prompt += DEFAULT_SPATIAL_NODE_RULES_SUFFIX

        # 2. Edge Extraction Prompt
        full_edge_prompt = DEFAULT_SPATIAL_EDGE_ROLE_PREFIX
        if prompt_for_edge_extraction:
            full_edge_prompt += (
                f"\n### Context & Instructions:\n{prompt_for_edge_extraction}\n"
            )
        full_edge_prompt += DEFAULT_SPATIAL_EDGE_RULES_SUFFIX

        # 3. One-Stage Graph Extraction Prompt
        full_graph_prompt = DEFAULT_SPATIAL_GRAPH_ROLE_PREFIX
        if prompt:
            full_graph_prompt += f"\n### Context & Instructions:\n{prompt}\n"
        full_graph_prompt += DEFAULT_SPATIAL_GRAPH_RULES_SUFFIX

        # Initialize parent AutoGraph
        super().__init__(
            node_schema=node_schema,
            edge_schema=edge_schema,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=spatial_edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            node_strategy_or_merger=node_strategy_or_merger,
            edge_strategy_or_merger=edge_strategy_or_merger,
            prompt_for_node_extraction=full_node_prompt,
            prompt_for_edge_extraction=full_edge_prompt,
            prompt=full_graph_prompt,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            node_fields_for_index=node_fields_for_index,
            edge_fields_for_index=edge_fields_for_index,
            **kwargs,
        )

    # ==============================================================================
    # Override Extraction Methods to Dynamically Inject Observation Location
    # ==============================================================================

    def _extract_edges_batch(
        self, chunks: list[str], node_lists: list[NodeListSchema[NodeSchema]]
    ) -> list[EdgeListSchema[EdgeSchema]]:
        """Override: Inject observation_location into edge extraction during two-stage extraction."""
        inputs = []
        for chunk, node_list in zip(chunks, node_lists):
            nodes = node_list.items if node_list else []
            known_nodes = (
                "\n- ".join([self.node_key_extractor(n) for n in nodes])
                if nodes
                else "No specific entities identified."
            )

            inputs.append(
                {
                    "source_text": chunk,
                    "known_nodes": known_nodes,
                    "observation_location": self.observation_location,
                }
            )

        results = self.edge_extractor.batch(
            inputs, config={"max_concurrency": self.max_workers}
        )
        return self._filter_none_results(
            results,
            default_factory=lambda: self.edge_list_schema(items=[]),
        )

    def _extract_data_by_one_stage(self, text: str) -> Any:
        """Override: Inject observation_location into one-stage extraction."""

        if len(text) <= self.chunk_size:
            inp = {
                "source_text": text,
                "observation_location": self.observation_location,
            }
            graph = self.data_extractor.invoke(inp)
            graph_list = [graph]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [
                {
                    "source_text": chunk,
                    "observation_location": self.observation_location,
                }
                for chunk in chunks
            ]
            graph_list = self.data_extractor.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )
            graph_list = self._filter_none_results(
                graph_list,
                default_factory=lambda: self.graph_schema(nodes=[], edges=[]),
            )

        return self.merge_batch_data(graph_list)

    def _create_empty_instance(self) -> "AutoSpatialGraph[NodeSchema, EdgeSchema]":
        """
        Override: Recreate instance with spatial attributes preserved.
        """
        return self.__class__(
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_key_extractor=self.node_key_extractor,
            edge_key_extractor=self.raw_edge_key_extractor,
            location_in_edge_extractor=self.location_in_edge_extractor,
            nodes_in_edge_extractor=self.nodes_in_edge_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            observation_location=self.observation_location,
            extraction_mode=self.extraction_mode,
            node_strategy_or_merger=self.node_merger,
            edge_strategy_or_merger=self.edge_merger,
            node_label_extractor=self._node_label_extractor,
            edge_label_extractor=self._edge_label_extractor,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            node_fields_for_index=self.node_fields_for_index,
            edge_fields_for_index=self.edge_fields_for_index,
            **self._constructor_kwargs,
        )
