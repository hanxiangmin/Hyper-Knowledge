"""Generic temporal graph implementation supporting custom schemas with time-aware deduplication."""

from collections.abc import Callable
from datetime import datetime
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
# Prompt Definition - Split for "Sandwich" Injection (Role -> User -> Rules)
# ==============================================================================

# Node Extraction Prompts
DEFAULT_TEMPORAL_NODE_ROLE_PREFIX = """
You are a professional entity extraction specialist.
Your task is to extract all important entities (Nodes) from the text.
"""

DEFAULT_TEMPORAL_NODE_RULES_SUFFIX = """
# Core Principles
1. **Comprehensiveness**: Extract persons, organizations, locations, events, concepts, and other noun-based entities.
2. **Accuracy**: Keep entity names consistent with the source text.
3. **Exclude Time Expressions**: **NEVER** extract dates, years, or time periods (e.g., "2023", "last year", "today") as entity nodes!
   Time is an attribute of relationships, not a node.
4. **Exclude Pure Numbers**: Do not extract standalone amounts or numeric values as independent nodes.

### Source Text:
{source_text}
"""

# Edge Extraction Prompts
DEFAULT_TEMPORAL_EDGE_ROLE_PREFIX = """
You are an expert temporal knowledge extraction specialist.
Extract meaningful relationships (edges) between the provided entities.
"""

DEFAULT_TEMPORAL_EDGE_RULES_SUFFIX = """
### Temporal Extraction Rules
Current Observation Date: {observation_time}

1. **Relative Time Resolution**: You MUST resolve relative time expressions based on the Observation Date.
   - "last year" -> Calculate the year before {observation_time}
   - "yesterday" -> Calculate the date before {observation_time}
   - "currently" -> The relationship is active (implies no end date)
   - "this month" -> First day of the month in {observation_time}
   - "last month" -> First day of the month before {observation_time}

2. **Explicit Dates**: Keep explicit dates (e.g., "2023", "2024-01-01") exactly as written.

3. **Missing Time**: If no time information is present, leave time fields empty. DO NOT hallucinate dates.

### General Constraints
1. ONLY extract edges connecting entities from the known entity list provided below.
2. DO NOT create edges involving entities that are not listed.
3. Use the defined schema fields for time as specified in the output format.

# Provided Entities
{known_nodes}

# Source Text:
{source_text}
"""

# One-Stage Graph Extraction Prompts
DEFAULT_TEMPORAL_GRAPH_ROLE_PREFIX = """
You are a professional temporal knowledge graph extraction specialist.
Your task is to extract entities (Nodes) and temporal relationships (Edges) from the text.
"""

DEFAULT_TEMPORAL_GRAPH_RULES_SUFFIX = """
# Core Principles for Nodes
1. Extract persons, organizations, locations, events, concepts, and other noun-based entities.
2. **NEVER** extract dates/times as independent nodes. Time is an attribute of relationships, not a node.
3. Keep entity names consistent with the source text.

# Core Principles for Edges
Current Observation Date: {observation_time}

1. **Relative Time Resolution**: You MUST resolve relative time expressions based on the Observation Date.
   - "last year" -> Calculate the year before {observation_time}
   - "yesterday" -> Calculate the date before {observation_time}
   - "currently" -> The relationship is active (implies no end date)
   - "this month" -> First day of the month in {observation_time}
   - "last month" -> First day of the month before {observation_time}

2. **Explicit Dates**: Keep explicit dates (e.g., "2023", "2024-01-01") exactly as written.

3. **Missing Time**: If no time information is present, leave time fields empty. DO NOT hallucinate dates.

### Source Text:
{source_text}
"""


class AutoTemporalGraph(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Generic Temporal Graph Extractor (AutoTemporalGraph).

    A flexible implementation supporting user-defined Node and Edge schemas with temporal awareness:
    - **Schema Agnosticism**: Support any user-defined Node and Edge Pydantic models.
    - **Temporal-Aware Deduplication**: Time information is integrated into edge deduplication logic.
    - **Dynamic Time Injection**: Observation Date is injected during extraction for relative time resolution.

    Key Design:
    - `temporal_edge_key_extractor`: A unified function to extract the unique key for an edge,
      including temporal components (e.g., lambda x: f"{x.src}|{x.relation}|{x.dst}|{x.year}").
      This ensures (A, rel, B) @ 2020 and (A, rel, B) @ 2021 are treated as different edges.
    - Unified Prompt Management: Temporal system prompts are prepended to any user-provided prompts.

    Example:
        >>> from pydantic import BaseModel, Field
        >>>
        >>> class MyEntity(BaseModel):
        ...     name: str
        ...     category: str = "Unknown"
        >>>
        >>> class MyTemporalEdge(BaseModel):
        ...     src: str
        ...     dst: str
        ...     relation: str
        ...     year: Optional[str] = None
        >>>
        >>> kg = AutoTemporalGraph(
        ...     node_schema=MyEntity,
        ...     edge_schema=MyTemporalEdge,
        ...     node_key_extractor=lambda x: x.name,
        ...     edge_key_extractor=lambda x: f"{x.src}|{x.relation}|{x.dst}",
        ...     time_in_edge_extractor=lambda x: x.year or "",
        ...     nodes_in_edge_extractor=lambda x: (x.src, x.dst),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     observation_time="2024-01-15"
        ... )
    """

    def __init__(
        self,
        node_schema: type[NodeSchema],
        edge_schema: type[EdgeSchema],
        node_key_extractor: Callable[[NodeSchema], str],
        edge_key_extractor: Callable[[EdgeSchema], str],
        time_in_edge_extractor: Callable[[EdgeSchema], str],
        nodes_in_edge_extractor: Callable[[EdgeSchema], tuple[str, str]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        observation_time: str | None = None,
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
        Initialize AutoTemporalGraph.

        Args:
            node_schema: User-defined Node Pydantic model.
            edge_schema: User-defined Edge Pydantic model with time fields.
            node_key_extractor: Function to extract unique key from node (e.g., lambda x: x.name).
            edge_key_extractor: Function to extract the base unique identifier for an edge purely based on
                                entities and relation (e.g., lambda x: f"{x.src}|{x.relation}|{x.dst}").
            time_in_edge_extractor: Function to extract the time component from an edge
                                   (e.g., lambda x: x.year or "permanent").
                This ensures (A, rel, B) @ 2020 and (A, rel, B) @ 2021 are treated as different edges.
            nodes_in_edge_extractor: Function to extract (source_key, target_key) from edge.
            llm_client: LangChain BaseChatModel for extraction.
            embedder: LangChain Embeddings for semantic operations.
            observation_time: Date context for relative time resolution (default: today in YYYY-MM-DD format).
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
        # Set observation date (default: today)
        self.observation_time = observation_time or datetime.now().strftime("%Y-%m-%d")

        # Store for instance recreation
        self.raw_edge_key_extractor = edge_key_extractor
        self.time_in_edge_extractor = time_in_edge_extractor
        self._constructor_kwargs = kwargs

        # Create combined extractor for unique identification in memory
        def temporal_edge_key_extractor(edge: EdgeSchema) -> str:
            raw_key = self.raw_edge_key_extractor(edge)
            time_val = self.time_in_edge_extractor(edge)
            return f"{raw_key} @ {time_val}" if time_val else raw_key

        # -----------------------------------------------------------
        # Construct Prompts: Role -> User Context -> System Rules
        # ("Sandwich" structure for optimal LLM instruction sequencing)
        # -----------------------------------------------------------

        # 1. Node Extraction Prompt
        full_node_prompt = DEFAULT_TEMPORAL_NODE_ROLE_PREFIX
        if prompt_for_node_extraction:
            full_node_prompt += (
                f"\n### Context & Instructions:\n{prompt_for_node_extraction}\n"
            )
        full_node_prompt += DEFAULT_TEMPORAL_NODE_RULES_SUFFIX

        # 2. Edge Extraction Prompt
        full_edge_prompt = DEFAULT_TEMPORAL_EDGE_ROLE_PREFIX
        if prompt_for_edge_extraction:
            full_edge_prompt += (
                f"\n### Context & Instructions:\n{prompt_for_edge_extraction}\n"
            )
        full_edge_prompt += DEFAULT_TEMPORAL_EDGE_RULES_SUFFIX

        # 3. One-Stage Graph Extraction Prompt
        full_graph_prompt = DEFAULT_TEMPORAL_GRAPH_ROLE_PREFIX
        if prompt:
            full_graph_prompt += f"\n### Context & Instructions:\n{prompt}\n"
        full_graph_prompt += DEFAULT_TEMPORAL_GRAPH_RULES_SUFFIX
        # Initialize parent AutoGraph
        super().__init__(
            node_schema=node_schema,
            edge_schema=edge_schema,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=temporal_edge_key_extractor,
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
    # Override Extraction Methods to Dynamically Inject Observation Date
    # ==============================================================================

    def _extract_edges_batch(
        self, chunks: list[str], node_lists: list[NodeListSchema[NodeSchema]]
    ) -> list[EdgeListSchema[EdgeSchema]]:
        """Override: Inject observation_time into edge extraction during two-stage extraction."""
        inputs = []
        for chunk, node_list in zip(chunks, node_lists):
            nodes = node_list.items if node_list else []
            if not nodes:
                known_nodes = "No specific entities identified in this chunk."
            else:
                node_keys = [self.node_key_extractor(n) for n in nodes]
                known_nodes = "\n- ".join(node_keys)

            inputs.append(
                {
                    "source_text": chunk,
                    "known_nodes": known_nodes,
                    "observation_time": self.observation_time,
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
        """Override: Inject observation_time into one-stage extraction."""

        if len(text) <= self.chunk_size:
            inp = {"source_text": text, "observation_time": self.observation_time}
            graph = self.data_extractor.invoke(inp)
            graph_list = [graph]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [
                {"source_text": chunk, "observation_time": self.observation_time}
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

    def _create_empty_instance(self) -> "AutoTemporalGraph[NodeSchema, EdgeSchema]":
        """
        Override: Recreate instance with all temporal-specific attributes.
        """
        return self.__class__(
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_key_extractor=self.node_key_extractor,
            edge_key_extractor=self.raw_edge_key_extractor,
            time_in_edge_extractor=self.time_in_edge_extractor,
            nodes_in_edge_extractor=self.nodes_in_edge_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            observation_time=self.observation_time,
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
            **self._constructor_kwargs,  # Propagate additional arguments
        )
