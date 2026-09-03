"""Hypergraph Knowledge Pattern - extracts hypergraphs where edges connect multiple nodes.

Key Difference from AutoGraph:
- Edges are "Hyperedges" that connect arbitrary numbers of nodes (not just source/target).
- Consistency validation checks if *ALL* participants in a hyperedge exist in the node registry.
"""

from collections.abc import Callable
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from ontomem import OMem
from ontomem.merger import BaseMerger, MergeStrategy, create_merger
from ontosight import view_hypergraph
from pydantic import BaseModel, Field, create_model

from hyperknowledge.utils.index_security import (
    verify_index_manifest,
    write_index_manifest,
)
from hyperknowledge.utils.logging import get_logger

from .base import BaseAutoType

logger = get_logger(__name__)


NodeSchema = TypeVar("NodeSchema", bound=BaseModel)
EdgeSchema = TypeVar("EdgeSchema", bound=BaseModel)  # Represents a Hyperedge


# ============================================================================
# Default Extraction Prompts
# ============================================================================

DEFAULT_HYPERGRAPH_PROMPT = """You are an expert hypergraph knowledge extraction assistant. 
Extract all entities (nodes) and their complex relationships (hyperedges) from the following text.

CRITICAL RULES:
1. Extract comprehensive Nodes (entities).
2. Extract Hyperedges that connect multiple (2 or more) nodes simultaneously.
3. STRUCTURAL CONSISTENCY: Every participant in a hyperedge MUST be present in the extracted Nodes list.
4. Do not create hyperedges involving entities that are not in the Nodes list.
5. A Hyperedge represents a Grouping, Event, or Complex Relation involving the listed participants.

### Source Text:
{source_text}
"""

DEFAULT_NODE_PROMPT = """Extract all distinct entities from the text. 
Entities will serve as participants in complex events later.

### Source Text:
{source_text}
"""

DEFAULT_EDGE_PROMPT = """You are an expert hypergraph extraction assistant. 
Extract complex relationships (hyperedges) that involve MULTIPLE entities simultaneously.

CRITICAL RULES:
1. A hyperedge can connect 2, 3, or more entities (e.g., a meeting with multiple people).
2. Identify ALL participants for each relationship.
3. ONLY use entities from the provided 'Known Entities' list.
4. If an entity is not in the list, exclude it from the hyperedge.

# Provided Entities
{known_nodes}

# Source Text:
{source_text}
"""


class AutoHypergraphSchema(BaseModel, Generic[NodeSchema, EdgeSchema]):
    """Generic schema container for hypergraph data."""

    nodes: list[NodeSchema] = Field(
        default_factory=list, description="Graph nodes/entities"
    )
    edges: list[EdgeSchema] = Field(
        default_factory=list, description="Hyperedges connecting multiple entities"
    )


class NodeListSchema(BaseModel, Generic[NodeSchema]):
    """Intermediate schema for batch node extraction."""

    items: list[NodeSchema] = Field(
        default_factory=list,
        description="List of identified entities or nodes found in the text.",
    )


class EdgeListSchema(BaseModel, Generic[EdgeSchema]):
    """Intermediate schema for batch hyperedge extraction."""

    items: list[EdgeSchema] = Field(
        default_factory=list,
        description="List of identified hyperedges found in the text.",
    )


class AutoHypergraph(
    BaseAutoType[AutoHypergraphSchema[NodeSchema, EdgeSchema]],
    Generic[NodeSchema, EdgeSchema],
):
    """AutoHypergraph - Node-First extraction: Extract entities first, then relationships.

    Extraction Strategy: Two-Stage (Node-First)
    1. Stage 1: Extract all Nodes (entities) from text.
    2. Stage 2: Extract Edges (relationships) using identified Nodes as context.

    Suitable for:
    - Events with multiple participants (e.g., meetings, transactions)
    - Group memberships
    - Complex dependencies

    The `nodes_in_edge_extractor` must return a Tuple of ALL node keys involved in the edge.
    Validation uses 'Strict Mode': checks if ALL nodes in that tuple exist.

    Example:
        >>> class Person(BaseModel):
        ...     name: str
        ...
        >>> class Event(BaseModel):
        ...     label: str  # e.g., "meeting", "collaboration"
        ...     participants: List[str]  # IDs of people involved
        ...
        >>> hypergraph = AutoHypergraph(
        ...     node_schema=Person,
        ...     edge_schema=Event,
        ...     node_key_extractor=lambda x: x.name,
        ...     # CRITICAL: Sort participants to ensure {A, B} and {B, A} map to same key
        ...     edge_key_extractor=lambda x: f"{x.label}_{sorted(x.participants)}",
        ...     nodes_in_edge_extractor=lambda x: tuple(x.participants),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     extraction_mode="two_stage"
        ... )
    """

    if TYPE_CHECKING:
        graph_schema: type[AutoHypergraphSchema[NodeSchema, EdgeSchema]]

    def __init__(
        self,
        node_schema: type[NodeSchema],
        edge_schema: type[EdgeSchema],
        node_key_extractor: Callable[[NodeSchema], str],
        edge_key_extractor: Callable[[EdgeSchema], str],
        # Returns a tuple of ALL node keys involved in this hyperedge
        nodes_in_edge_extractor: Callable[[EdgeSchema], tuple[str, ...]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",  # Recommended for complex relations
        node_strategy_or_merger: MergeStrategy
        | BaseMerger = MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger: MergeStrategy
        | BaseMerger = MergeStrategy.LLM.BALANCED,
        prompt: str = "",
        prompt_for_node_extraction: str = "",
        prompt_for_edge_extraction: str = "",
        node_label_extractor: Callable[[NodeSchema], str] | None = None,
        edge_label_extractor: Callable[[EdgeSchema], str] | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        node_fields_for_index: list[str] | None = None,
        edge_fields_for_index: list[str] | None = None,
        **kwargs: Any,
    ):
        """Initialize AutoHypergraph with node/edge schemas and configuration.

        Args:
            node_schema: Pydantic BaseModel for nodes/entities.
            edge_schema: Pydantic BaseModel for hyperedges/relationships.
            node_key_extractor: Function to extract unique key from node.
            edge_key_extractor: Function to extract unique key from hyperedge.
                CRITICAL: Since hyperedges are unordered sets of nodes (i.e., {A, B} == {B, A}),
                you MUST sort the participating node keys in this function to ensure consistent
                deduplication. For example:
                    lambda x: f"{x.relation_type}_{sorted(x.participants)}"
                Without sorting, two hyperedges with the same nodes in different order will
                be treated as different edges, breaking the deduplication mechanism.
            nodes_in_edge_extractor: Function to extract ALL node keys from a hyperedge
                as a tuple (e.g., lambda x: tuple(x.participants)).
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            extraction_mode: "two_stage" (recommended) or "one_stage".
            node_strategy_or_merger: Merge strategy for duplicate nodes.
            edge_strategy_or_merger: Merge strategy for duplicate hyperedges.
            prompt: Custom extraction prompt for one-stage mode.
            prompt_for_node_extraction: Custom extraction prompt for node extraction.
            prompt_for_edge_extraction: Custom extraction prompt for hyperedge extraction.
            node_label_extractor: Optional function to extract label from node for visualization.
            edge_label_extractor: Optional function to extract label from edge for visualization.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlapping characters between chunks.
            max_workers: Maximum concurrent extraction tasks.
            verbose: Whether to display detailed execution logs and progress information.
            node_fields_for_index: Optional list of field names in node_schema to include in vector index.
                                   If None, all text fields are indexed by default.
                                   Example: ['name', 'properties'] (only index these node fields)
            edge_fields_for_index: Optional list of field names in edge_schema to include in vector index.
                                   If None, all text fields are indexed by default.
                                   Example: ['summary', 'type'] (only index these edge fields)
            **kwargs: Additional arguments for merger creation.
        """

        # Store schemas and extractors
        self.node_schema = node_schema
        self.edge_schema = edge_schema
        self.node_key_extractor = node_key_extractor
        self.edge_key_extractor = edge_key_extractor
        self.nodes_in_edge_extractor = nodes_in_edge_extractor
        self.extraction_mode = extraction_mode
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose
        self.node_fields_for_index = node_fields_for_index
        self.edge_fields_for_index = edge_fields_for_index

        self.max_workers = max_workers
        self.verbose = verbose

        graph_prompt = prompt or DEFAULT_HYPERGRAPH_PROMPT

        # Create dynamic HypergraphSchema
        graph_schema_name = f"{node_schema.__name__}{edge_schema.__name__}Hypergraph"
        self.graph_schema = create_model(
            graph_schema_name,
            nodes=(list[node_schema], Field(default_factory=list)),
            edges=(list[edge_schema], Field(default_factory=list)),
        )

        # Helper Schemas for Batch Extraction
        self.node_list_schema = create_model(
            f"{node_schema.__name__}List",
            items=(list[node_schema], Field(default_factory=list)),
        )
        self.edge_list_schema = create_model(
            f"{edge_schema.__name__}List",
            items=(list[edge_schema], Field(default_factory=list)),
        )

        # Initialize Node Merger
        if isinstance(node_strategy_or_merger, BaseMerger):
            self.node_merger = node_strategy_or_merger
        else:
            self.node_merger = create_merger(
                strategy=node_strategy_or_merger,
                key_extractor=node_key_extractor,
                llm_client=llm_client,
                item_schema=node_schema,
                **kwargs,
            )

        # Initialize Edge Merger
        if isinstance(edge_strategy_or_merger, BaseMerger):
            self.edge_merger = edge_strategy_or_merger
        else:
            self.edge_merger = create_merger(
                strategy=edge_strategy_or_merger,
                key_extractor=edge_key_extractor,
                llm_client=llm_client,
                item_schema=edge_schema,
                **kwargs,
            )

        # Initialize OMem instances
        self._node_memory = OMem(
            memory_schema=node_schema,
            key_extractor=node_key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self.node_merger,
            verbose=verbose,
            fields_for_index=node_fields_for_index,  # Pass node field selection to OMem
        )

        self._edge_memory = OMem(
            memory_schema=edge_schema,
            key_extractor=edge_key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self.edge_merger,
            verbose=verbose,
            fields_for_index=edge_fields_for_index,  # Pass edge field selection to OMem
        )

        # Store label extractors for visualization
        self._node_label_extractor = node_label_extractor
        self._edge_label_extractor = edge_label_extractor

        # Initialize Base Class
        super().__init__(
            data_schema=self.graph_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=graph_prompt,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

        # Initialize prompts
        self.node_prompt = prompt_for_node_extraction or DEFAULT_NODE_PROMPT
        self.edge_prompt = prompt_for_edge_extraction or DEFAULT_EDGE_PROMPT

        # Two-stage mode: validate prompts and initialize extractors
        self.prompt_template = ChatPromptTemplate.from_template(self.node_prompt)
        self.node_extractor = (
            self.prompt_template
            | self.llm_client.with_structured_output(
                self.node_list_schema, method="function_calling"
            )
        )

        self.edge_prompt_template = ChatPromptTemplate.from_template(self.edge_prompt)
        self.edge_extractor = (
            self.edge_prompt_template
            | self.llm_client.with_structured_output(
                self.edge_list_schema, method="function_calling"
            )
        )

    # ==================== Prompts ====================

    def _default_prompt(self) -> str:
        """Returns the default prompt for one-stage hypergraph extraction.

        This is the primary prompt used when extraction_mode is 'one_stage'.
        """
        return DEFAULT_HYPERGRAPH_PROMPT

    def _create_empty_instance(self) -> "AutoHypergraph[NodeSchema, EdgeSchema]":
        """Creates a new empty AutoHypergraph instance with the same configuration.

        Overrides parent method to handle AutoHypergraph-specific parameters.

        Returns:
            A new empty AutoHypergraph instance with identical configuration.
        """
        return self.__class__(
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_key_extractor=self.node_key_extractor,
            edge_key_extractor=self.edge_key_extractor,
            nodes_in_edge_extractor=self.nodes_in_edge_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            extraction_mode=self.extraction_mode,
            node_strategy_or_merger=self.node_merger,
            edge_strategy_or_merger=self.edge_merger,
            prompt=self.prompt,
            prompt_for_node_extraction=self.node_prompt,
            prompt_for_edge_extraction=self.edge_prompt,
            node_label_extractor=self._node_label_extractor,
            edge_label_extractor=self._edge_label_extractor,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            node_fields_for_index=self.node_fields_for_index,  # Persist node index field configuration
            edge_fields_for_index=self.edge_fields_for_index,  # Persist edge index field configuration
        )

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """Initialize or reset hypergraph data structures."""
        self._node_memory.clear()
        self._edge_memory.clear()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._node_memory.clear_index()
        self._edge_memory.clear_index()

    def _set_data_state(self, data: AutoHypergraphSchema) -> None:
        """Replace hypergraph data with new data (full reset)."""
        self._node_memory.clear()
        self._edge_memory.clear()

        if data.nodes:
            self._node_memory.add(data.nodes)
        if data.edges:
            self._edge_memory.add(data.edges)

        self.clear_index()

    def _update_data_state(self, incoming_data: AutoHypergraphSchema) -> None:
        """Merge incoming hypergraph data into current state."""
        if self.empty():
            self._set_data_state(incoming_data)
        else:
            if incoming_data.nodes:
                self._node_memory.add(incoming_data.nodes)
            if incoming_data.edges:
                self._edge_memory.add(incoming_data.edges)
            self.clear_index()

    @property
    def data(self) -> AutoHypergraphSchema:
        """Returns the current hypergraph state."""
        return self.graph_schema(
            nodes=self._node_memory.items, edges=self._edge_memory.items
        )

    @property
    def nodes(self) -> list[NodeSchema]:
        """Returns the current node collection."""
        return self._node_memory.items

    @property
    def edges(self) -> list[EdgeSchema]:
        """Returns the current hyperedge collection."""
        return self._edge_memory.items

    def empty(self) -> bool:
        """Checks if the hypergraph is empty."""
        return self._node_memory.empty()

    # ==================== Extraction Pipeline ====================

    def _extract_data(self, text: str) -> AutoHypergraphSchema:
        """Main extraction logic dispatcher."""
        if self.extraction_mode == "two_stage":
            raw_graph = self._extract_data_by_two_stage(text)
        elif self.extraction_mode == "one_stage":
            raw_graph = self._extract_data_by_one_stage(text)
        else:
            raise ValueError(f"Invalid extraction_mode: {self.extraction_mode}")

        # Prune dangling hyperedges to ensure consistency
        return self._prune_dangling_edges(raw_graph)

    def _extract_data_by_one_stage(self, text: str) -> AutoHypergraphSchema:
        """Extract nodes and edges simultaneously using single LLM call.

        Args:
            text: Input text.

        Returns:
            Raw extracted hypergraph data.
        """
        # Extract from single chunk or multiple chunks
        if len(text) <= self.chunk_size:
            graph = self.data_extractor.invoke({"source_text": text})
            graph_list = [graph]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"source_text": chunk} for chunk in chunks]
            graph_list = self.data_extractor.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )
            graph_list = self._filter_none_results(
                graph_list,
                default_factory=lambda: self.graph_schema(nodes=[], edges=[]),
            )

        # Merge multiple hypergraphs
        return self.merge_batch_data(graph_list)

    def _extract_data_by_two_stage(self, text: str) -> AutoHypergraphSchema:
        """Extract nodes first, then hyperedges with node context (batch processing).

        Process:
        1. Split text into chunks.
        2. Batch extract nodes for all chunks.
        3. Batch extract hyperedges for all chunks (using chunk-specific nodes as context).
        4. Merge all partial results into one global hypergraph.
        """
        # 1. Prepare chunks
        if len(text) <= self.chunk_size:
            chunks = [text]
        else:
            chunks = self.text_splitter.split_text(text)

        if self.verbose:
            logger.info(f"Extracting from {len(chunks)} chunks...")

        # 2. Batch Extract Nodes
        chunk_node_lists = self._extract_nodes_batch(chunks)

        # 3. Batch Extract Hyperedges (Context-aware)
        chunk_edge_lists = self._extract_edges_batch(chunks, chunk_node_lists)

        # 4. Construct Partial Graphs (Tuple format for merge optimization)
        partial_hypergraphs = (
            [node_list.items for node_list in chunk_node_lists],
            [edge_list.items for edge_list in chunk_edge_lists],
        )

        # 5. Global Merge
        return self.merge_batch_data(partial_hypergraphs)

    def _extract_nodes_batch(
        self, chunks: list[str]
    ) -> list[NodeListSchema[NodeSchema]]:
        """Batch extract nodes from multiple text chunks."""
        inputs = [{"source_text": chunk} for chunk in chunks]
        results = self.node_extractor.batch(
            inputs, config={"max_concurrency": self.max_workers}
        )
        return self._filter_none_results(
            results,
            default_factory=lambda: self.node_list_schema(items=[]),
        )

    def _extract_edges_batch(
        self, chunks: list[str], node_lists: list[NodeListSchema[NodeSchema]]
    ) -> list[EdgeListSchema[EdgeSchema]]:
        """Batch extract hyperedges using corresponding node lists as context."""
        inputs = []
        for chunk, node_list in zip(chunks, node_lists):
            nodes = node_list.items if node_list else []
            if not nodes:
                known_nodes = "No entities identified in this chunk."
            else:
                node_keys = [self.node_key_extractor(n) for n in nodes]
                known_nodes = "\n- ".join(node_keys)

            inputs.append({"source_text": chunk, "known_nodes": known_nodes})

        results = self.edge_extractor.batch(
            inputs, config={"max_concurrency": self.max_workers}
        )
        return self._filter_none_results(
            results,
            default_factory=lambda: self.edge_list_schema(items=[]),
        )

    def _prune_dangling_edges(
        self, graph: AutoHypergraphSchema
    ) -> AutoHypergraphSchema:
        """Prune hyperedges where ANY participating node does not exist (Strict Consistency).

        Args:
            graph: Raw hypergraph that may contain dangling hyperedges.

        Returns:
            Hypergraph with only valid hyperedges (ALL participants must exist in nodes).
        """
        valid_nodes = graph.nodes
        valid_node_keys = {self.node_key_extractor(n) for n in valid_nodes}

        # Also check long-term memory
        if self._node_memory:
            valid_node_keys.update(self._node_memory.keys)

        refined_edges = []
        dropped_count = 0

        for edge in graph.edges:
            # Get tuple of all participant node keys
            participant_keys = self.nodes_in_edge_extractor(edge)

            # Strict mode: ALL participants must exist
            is_valid = True
            for pk in participant_keys:
                if pk not in valid_node_keys:
                    is_valid = False
                    break

            # Keep edge only if all participants exist and there's at least one participant
            if is_valid and len(participant_keys) > 0:
                refined_edges.append(edge)
            else:
                dropped_count += 1
                logger.debug(
                    f"Pruning dangling hyperedge with participants: {participant_keys}"
                )

        if dropped_count > 0:
            logger.info(
                f"Pruned {dropped_count} dangling hyperedges to ensure consistency."
            )

        return self.graph_schema(nodes=valid_nodes, edges=refined_edges)

    # ==================== Merge Logic ====================

    def merge_batch_data(
        self,
        data_list_or_tuple: list[AutoHypergraphSchema]
        | tuple[list[list[NodeSchema]], list[list[EdgeSchema]]],
    ) -> AutoHypergraphSchema:
        """Merge multiple hypergraphs or node/edge tuples into one.

        Supports two input formats:
        - List of AutoHypergraphSchema objects (standard format)
        - Tuple of (List[List[Node]], List[List[Edge]]) (optimization for batch processing)

        Args:
            data_list_or_tuple: Either a list of AutoHypergraphSchema objects or a tuple of
                (nodes_lists, edges_lists) where each list contains items from multiple chunks.

        Returns:
            Merged hypergraph.
        """
        # Handle empty input (all batch results were None/filtered out)
        if not data_list_or_tuple:
            logger.warning("stage=merge_batch_empty input_is_empty")
            return self.graph_schema(nodes=[], edges=[])

        # Drop failed (None) chunk results from the list form; otherwise a single
        # failed invoke() ([None]) falls through to the tuple branch and asserts.
        if isinstance(data_list_or_tuple, list):
            data_list_or_tuple = [g for g in data_list_or_tuple if g is not None]
            if not data_list_or_tuple:
                return self.graph_schema(nodes=[], edges=[])

        if isinstance(data_list_or_tuple, list) and isinstance(
            data_list_or_tuple[0], self.graph_schema
        ):
            # Format: List of AutoHypergraphSchema
            all_nodes, all_edges = [], []
            for graph in data_list_or_tuple:
                all_nodes.extend(graph.nodes)
                all_edges.extend(graph.edges)

        else:
            # Format: Tuple of (nodes_lists, edges_lists)
            assert len(data_list_or_tuple) == 2, (
                "Invalid input format for batch merging"
            )
            nodes_lists, edges_lists = data_list_or_tuple[0], data_list_or_tuple[1]

            # Handle empty nodes/edges lists
            if not nodes_lists and not edges_lists:
                logger.warning("stage=merge_batch_empty_tuple nodes_and_edges_empty")
                return self.graph_schema(nodes=[], edges=[])

            # Guard against an empty first chunk: nodes_lists[0] (or edges_lists[0])
            # can be an empty list when a chunk produced no nodes/edges, so
            # indexing [0][0] without the inner check raises IndexError.
            if nodes_lists and nodes_lists[0]:
                assert isinstance(nodes_lists[0][0], self.node_schema), (
                    "Invalid node list format for batch merging"
                )
            if edges_lists and edges_lists[0]:
                assert isinstance(edges_lists[0][0], self.edge_schema), (
                    "Invalid edge list format for batch merging"
                )

            all_nodes, all_edges = [], []
            for node_list, edge_list in zip(nodes_lists, edges_lists):
                all_nodes.extend(node_list)
                all_edges.extend(edge_list)

        merged_nodes = self.node_merger.merge(all_nodes) if all_nodes else []
        merged_edges = self.edge_merger.merge(all_edges) if all_edges else []
        return self.graph_schema(nodes=merged_nodes, edges=merged_edges)

    # ==================== Indexing & Search ====================

    def build_index(self, index_nodes: bool = True, index_edges: bool = True):
        """Build vector index for hypergraph search.

        By default, builds indices for both nodes and hyperedges to support comprehensive search.

        Args:
            index_nodes: Whether to index nodes (default: True).
            index_edges: Whether to index hyperedges (default: True).
        """
        if index_nodes:
            self.build_node_index()

        if index_edges:
            self.build_edge_index()

    def build_node_index(self) -> None:
        """Build vector index specifically for nodes."""
        if not self.empty():
            self._node_memory.build_index()

    def build_edge_index(self) -> None:
        """Build vector index specifically for hyperedges."""
        if not self.empty():
            self._edge_memory.build_index()

    def search(
        self,
        query: str,
        top_k_nodes: int = 3,
        top_k_edges: int = 3,
        top_k: int | None = None,
    ) -> tuple[list[NodeSchema], list[EdgeSchema]]:
        """Unified hypergraph search interface.

        Retrieves nodes and hyperedges semantically related to the query.
        Always returns a tuple of (nodes, edges). If a count is 0, the corresponding list will be empty.

        Args:
            query: Search query string.
            top_k_nodes: Number of node results to return (default: 3). Set to 0 to disable node search.
            top_k_edges: Number of hyperedge results to return (default: 3). Set to 0 to disable hyperedge search.
            top_k: If provided, sets both top_k_nodes and top_k_edges to this value.

        Returns:
            Tuple[List[Node], List[Edge]]: A tuple containing:
                - List of matching nodes (empty if top_k_nodes <= 0)
                - List of matching hyperedges (empty if top_k_edges <= 0)

        Raises:
            ValueError: If both top_k_nodes and top_k_edges are <= 0.
            ValueError: If search is requested (top_k > 0) but the corresponding index is not built.
        """
        if top_k is not None:
            top_k_nodes = top_k
            top_k_edges = top_k

        if top_k_nodes <= 0 and top_k_edges <= 0:
            raise ValueError(
                "At least one of top_k_nodes or top_k_edges must be positive."
            )

        nodes: list[NodeSchema] = []
        edges: list[EdgeSchema] = []

        if top_k_nodes > 0:
            if not self._node_memory.has_index():
                raise ValueError("Node index not built. Call build_index() first.")
            nodes = self.search_nodes(query, top_k=top_k_nodes)

        if top_k_edges > 0:
            if not self._edge_memory.has_index():
                raise ValueError("Edge index not built. Call build_index() first.")
            edges = self.search_edges(query, top_k=top_k_edges)

        return nodes, edges

    def search_nodes(self, query: str, top_k: int = 3) -> list[NodeSchema]:
        """Semantic search for nodes/entities only."""
        return self._node_memory.search(query=query, top_k=top_k)

    def search_edges(self, query: str, top_k: int = 3) -> list[EdgeSchema]:
        """Semantic search for hyperedges/relationships only."""
        return self._edge_memory.search(query=query, top_k=top_k)

    def chat(
        self,
        query: str,
        top_k_nodes: int = 3,
        top_k_edges: int = 3,
        top_k: int | None = None,
    ) -> AIMessage:
        """Performs a chat-like interaction using hypergraph knowledge.

        Retrieves relevant nodes and/or hyperedges based on the query and retrieval counts,
        formats them into a structured context with clear headers, and generates an answer.

        Args:
            query: User query string.
            top_k_nodes: Number of relevant nodes to retrieve (default: 3). Set to 0 to disable node context.
            top_k_edges: Number of relevant hyperedges to retrieve (default: 3). Set to 0 to disable edge context.
            top_k: If provided, sets both top_k_nodes and top_k_edges to this value.

        Returns:
            An AIMessage object containing the LLM-generated response.
            Access the text content via response.content.

        Example:
            >>> # Chat using 5 nodes and 2 hyperedges as context
            >>> response = hg.chat("What participates in X?", top_k_nodes=5, top_k_edges=2)
            >>> print(response.content)  # Print the generated answer
        """
        if top_k is not None:
            top_k_nodes = top_k
            top_k_edges = top_k

        if top_k_nodes <= 0 and top_k_edges <= 0:
            raise ValueError(
                "At least one of top_k_nodes or top_k_edges must be positive."
            )

        context_parts = []

        # Step 2: Retrieve and format nodes context
        nodes = []
        if top_k_nodes > 0:
            nodes = self.search_nodes(query, top_k=top_k_nodes)
            if nodes:
                context_parts.append("=== Relevant Nodes ===")
                for node in nodes:
                    assert isinstance(node, BaseModel), (
                        "Node must be a Pydantic BaseModel"
                    )
                    context_parts.append(node.model_dump_json(indent=2))

        # Step 3: Retrieve and format edges context
        edges = []
        if top_k_edges > 0:
            edges = self.search_edges(query, top_k=top_k_edges)
            if edges:
                context_parts.append("=== Relevant Edges ===")
                for edge in edges:
                    assert isinstance(edge, BaseModel), (
                        "Edge must be a Pydantic BaseModel"
                    )
                    context_parts.append(edge.model_dump_json(indent=2))

        # Step 4: Combine context or use fallback
        if not context_parts:
            context = "No relevant information found in the knowledge abstract."
        else:
            context = "\n\n".join(context_parts)

        # Step 5: Invoke LLM with structured context
        qa_prompt = ChatPromptTemplate.from_template(
            "Based on the following Hypergraph Knowledge answer the user's question.\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

        qa_chain = qa_prompt | self.llm_client
        response = qa_chain.invoke({"context": context, "question": query})

        # Step 6: Inject retrieved nodes and edges into response metadata
        if not response.additional_kwargs:
            response.additional_kwargs = {}
        response.additional_kwargs["retrieved_nodes"] = nodes
        response.additional_kwargs["retrieved_edges"] = edges

        return response

    # ==================== Serialization ====================

    def dump_index(self, folder_path: str | Path) -> None:
        """Save indices to disk."""
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # Save node index
        node_index_path = folder / "node_index"
        node_index_path.mkdir(exist_ok=True)
        try:
            self._node_memory.dump_index(str(node_index_path))
        except Exception as e:
            logger.warning(f"Failed to save node index: {e}")

        # Save edge index
        edge_index_path = folder / "edge_index"
        edge_index_path.mkdir(exist_ok=True)
        try:
            self._edge_memory.dump_index(str(edge_index_path))
        except Exception as e:
            logger.warning(f"Failed to save edge index: {e}")
        write_index_manifest(folder)

    def load_index(self, folder_path: str | Path) -> None:
        """Load indices from disk."""
        folder = Path(folder_path)
        verify_index_manifest(folder)

        # Load node index
        node_index_path = folder / "node_index"
        if node_index_path.exists():
            try:
                self._node_memory.load_index(str(node_index_path))
            except Exception as e:
                logger.warning(f"Failed to load node index: {e}")

        # Load edge index
        edge_index_path = folder / "edge_index"
        if edge_index_path.exists():
            try:
                self._edge_memory.load_index(str(edge_index_path))
            except Exception as e:
                logger.warning(f"Failed to load edge index: {e}")

    def show(
        self,
        node_label_extractor: Callable[[NodeSchema], str] | None = None,
        edge_label_extractor: Callable[[EdgeSchema], str] | None = None,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """Visualize the hypergraph using OntoSight.

        Args:
            node_label_extractor: Optional function to extract label from node for visualization.
                If not provided, uses the one from __init__.
            edge_label_extractor: Optional function to extract label from edge for visualization.
                If not provided, uses the one from __init__.
            top_k_nodes_for_search: Number of nodes to retrieve for search callback (default: 3).
            top_k_edges_for_search: Number of edges to retrieve for search callback (default: 3).
            top_k_nodes_for_chat: Number of nodes to retrieve for chat callback (default: 3).
            top_k_edges_for_chat: Number of edges to retrieve for chat callback (default: 3).
        """
        if node_label_extractor is None:
            node_label_extractor = self._node_label_extractor
        if edge_label_extractor is None:
            edge_label_extractor = self._edge_label_extractor

        if self._node_memory.has_index() and self._edge_memory.has_index():
            logger.info(
                "Visualizing hypergraph with search and chat capabilities (indices detected)."
            )

            def search_callback(query: str) -> None:
                return self.search(
                    query,
                    top_k_nodes=top_k_nodes_for_search,
                    top_k_edges=top_k_edges_for_search,
                )

            def chat_callback(question: str) -> None:
                response = self.chat(
                    question,
                    top_k_nodes=top_k_nodes_for_chat,
                    top_k_edges=top_k_edges_for_chat,
                )
                content = response.content
                retrieved_nodes = response.additional_kwargs.get("retrieved_nodes", [])
                retrieved_edges = response.additional_kwargs.get("retrieved_edges", [])
                return content, (retrieved_nodes, retrieved_edges)
        else:
            logger.info(
                "Visualizing hypergraph without search and chat capabilities (no indices detected)."
            )
            search_callback = None
            chat_callback = None

        view_hypergraph(
            node_list=self.nodes,
            edge_list=self.edges,
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_id_extractor=self.node_key_extractor,
            node_ids_in_edge_extractor=self.nodes_in_edge_extractor,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            on_search=search_callback,
            on_chat=chat_callback,
        )

    # ==================== Obsidian Export ====================

    def export_obsidian(
        self,
        folder_path: str | Path,
        *,
        node_label_extractor: Callable[[NodeSchema], str] | None = None,
        edge_label_extractor: Callable[[EdgeSchema], str] | None = None,
        vault_name: str = "Knowledge Vault",
        include_index: bool = True,
        overwrite: bool = False,
    ) -> Path:
        """Export the hypergraph as an Obsidian vault.

        Writes one Markdown note per node (fields stored as YAML front-matter).
        Each N-ary hyperedge is rendered under its first incident node, linking
        out to the remaining members via ``[[wikilinks]]``, so the relationship
        is browsable in Obsidian's graph view.

        Args:
            folder_path: Destination vault directory.
            node_label_extractor: Optional node -> display title. Defaults to the
                one from ``__init__``, then common fields, then the node id.
            edge_label_extractor: Optional edge -> relationship label. Defaults to
                the one from ``__init__``, then common fields, then "related to".
            vault_name: Title used for the generated index note.
            include_index: Whether to write an index/map-of-content note.
            overwrite: Allow writing into an existing, non-empty directory.

        Returns:
            The vault directory :class:`~pathlib.Path`.
        """
        from hyperknowledge.utils.obsidian import export_to_obsidian

        if node_label_extractor is None:
            node_label_extractor = self._node_label_extractor
        if edge_label_extractor is None:
            edge_label_extractor = self._edge_label_extractor

        return export_to_obsidian(
            nodes=self.nodes,
            edges=self.edges,
            node_id_extractor=self.node_key_extractor,
            incident_nodes_extractor=self.nodes_in_edge_extractor,
            folder_path=folder_path,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            vault_name=vault_name,
            include_index=include_index,
            overwrite=overwrite,
        )
