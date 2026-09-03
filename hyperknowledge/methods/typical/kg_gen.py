"""Knowledge Graph Generator using AutoGraph as the core engine.

This module provides a simplified wrapper around AutoGraph specifically designed for
extracting simple triple-based knowledge graphs (subject-predicate-object).

Prompts are adapted from kg_gen/steps to ensure consistency with the original
knowledge graph extraction logic.
"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import MergeStrategy
from pydantic import BaseModel, Field
from semhash import SemHash

from hyperknowledge.types.graph import AutoGraph, AutoGraphSchema
from hyperknowledge.utils.logging import get_logger

logger = get_logger(__name__)

# ==============================================================================
# 1. Schema Definition - Consistent with original kg_gen
# ==============================================================================


class NodeSchema(BaseModel):
    """Knowledge Graph Node: Minimal entity with only a name field"""

    name: str = Field(
        description="The unique name or identifier of the entity. Must be thorough and accurate to the source text.",
    )


class EdgeSchema(BaseModel):
    """Knowledge Graph Edge: Standard triple structure (Subject-Predicate-Object)"""

    subject: str = Field(
        description="Subject entity name. Must be an exact match from the extracted entities list.",
    )
    predicate: str = Field(
        description="The relationship/predicate between subject and object. Should be concise and descriptive.",
    )
    object: str = Field(
        description="Object entity name. Must be an exact match from the extracted entities list.",
    )


# ==============================================================================
# 2. Prompt Definition - Adapted from original kg_gen/steps implementation
# ==============================================================================

KG_Gen_NODE_EXTRACTION_PROMPT = """
Extract key entities from the source text. Extracted entities are subjects or objects in a knowledge graph.
This is for an extraction task, please be THOROUGH and accurate to the reference text.

Requirements:
- Extract ALL important entities (people, organizations, locations, concepts, events)
- Be comprehensive - don't miss any entity
- Entity names should be exact matches from the source text
- Each entity should be a single name or brief identifier

### Source Text:
{source_text}
"""

KG_Gen_EDGE_EXTRACTION_PROMPT = """
Extract subject-predicate-object triples from the source text.

CRITICAL RULES:
1. Subject and Object MUST be exact names from the provided entities list
2. If an entity is not in the provided list, do NOT use it
3. Predicates should be concise and descriptive (e.g., "founded", "located_in", "works_for")
4. Each triple must be faithful to the source text
5. Be thorough - extract all relationships mentioned

# Provided Entities
{known_nodes}

### Source Text:
{source_text}
"""


# ==============================================================================
# 3. KGGenGraph Implementation - Inherits from AutoGraph
# ==============================================================================


class KG_Gen(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Knowledge Graph Generator: A specialized AutoGraph for extracting simple triple-based KGs.

    Features:
    - Fixed Schema (NodeSchema, EdgeSchema) optimized for triple extraction
    - Customized prompts from original kg_gen implementation
    - Automatic deduplication and consistency checking via AutoGraph's OMem
    - Two-stage extraction: entities first, then relationships

    Example:
        >>> llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>> kg = KG_Gen(llm_client=llm, embedder=embedder)
        >>> kg.feed_text(text)
        >>> print(f"Extracted {len(kg.nodes)} entities and {len(kg.edges)} relationships.")
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        """Initialize KGGenGraph.

        Args:
            llm_client: Language model for extraction
            embedder: Embedding model for vector indexing
            chunk_size: Characters per chunk
            chunk_overlap: Overlapping characters between chunks
            max_workers: Max concurrent extraction workers
            verbose: Display detailed execution logs and progress information
        """

        # 1. Define Key Extractors (critical for deduplication)
        # Node deduplication: exact match by name
        node_key_fn = lambda x: x.name

        # Edge deduplication: combination of subject-predicate-object triple
        edge_key_fn = lambda x: f"{x.subject}|{x.predicate}|{x.object}"

        # 2. Edge consistency check: tell AutoGraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: (x.subject, x.object)

        # 3. Call parent class initialization
        logger.info("🔧 Initializing KGGenGraph (Knowledge Graph Generator)")
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Enforce two-stage extraction (nodes first, then edges)
            extraction_mode="two_stage",
            # Inject customized prompts
            prompt_for_node_extraction=KG_Gen_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=KG_Gen_EDGE_EXTRACTION_PROMPT,
            # Configure deduplication strategy
            node_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
            edge_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
            # Optimize indexing: only index name field
            node_fields_for_index=["name"],
            edge_fields_for_index=["subject", "predicate", "object"],
            # Display labels
            node_label_extractor=lambda x: x.name,
            edge_label_extractor=lambda x: x.predicate,
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    def _deduplicate_graph(
        self,
        graph_data: AutoGraphSchema[NodeSchema, EdgeSchema],
        threshold: float = 0.9,
    ) -> AutoGraphSchema[NodeSchema, EdgeSchema]:
        """Internal helper to apply SemHash deduplication on a graph data object.

        Args:
            graph_data: The graph data object (nodes/edges) to process in-place.
            threshold: SemHash similarity threshold (0.0 to 1.0).

        Returns:
            The modified graph_data object.
        """

        nodes, edges = graph_data.nodes, graph_data.edges

        if len(nodes) == 0:
            logger.warning("⚠️ No nodes to deduplicate; skipping deduplication.")
            return graph_data

        # 1. Prepare data and run SemHash
        node_names = [n.name for n in nodes]

        try:
            embeddings = self.embedder.embed_documents(node_names)
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            return graph_data

        semhash = SemHash.from_records(
            embeddings=embeddings,
            records=node_names,
            model=None,  # Embeddings already provided
        )
        result = semhash.self_deduplicate(threshold=threshold)

        # 2. Build mapping from duplicates result
        mapping = {}
        for record in result.filtered:
            if record.duplicates and len(record.duplicates) > 0:
                mapping[record.record] = record.duplicates[0][0]

        # 3. Apply mapping to graph data (in-place modification)
        # Remap nodes
        for node in nodes:
            if node.name in mapping:
                node.name = mapping[node.name]

        # Remap edges
        for edge in edges:
            if edge.subject in mapping:
                edge.subject = mapping[edge.subject]
            if edge.object in mapping:
                edge.object = mapping[edge.object]

        return graph_data

    def deduplicate(
        self,
        threshold: float = 0.9,
    ) -> "KG_Gen":
        """Return a NEW KG_Gen instance with deduplicated entities and edges.
        Does not modify the current instance.

        Args:
            threshold: Similarity threshold for SemHash (0.0 to 1.0). Higher means stricter.

        Returns:
            A new, deduplicated KG_Gen instance.
        """
        logger.info(f"📋 Creating deduplicated copy (threshold={threshold})...")

        # 1. Deep copy current data
        graph_data = self.data.model_copy(deep=True)
        original_node_count = len(self.nodes)
        original_edge_count = len(self.edges)

        # 2. Process deduplication
        graph_data = self._deduplicate_graph(graph_data, threshold)

        # 3. Populate new instance - let OMem handle merging
        new_instance = self._create_empty_instance()
        new_instance._set_data_state(graph_data)

        logger.info(
            f"✅ Deduplication Complete: "
            f"Nodes {original_node_count} -> {len(new_instance.nodes)}, "
            f"Edges {original_edge_count} -> {len(new_instance.edges)}"
        )

        return new_instance

    def self_deduplicate(
        self,
        threshold: float = 0.9,
    ) -> "KG_Gen":
        """Deduplicate the current graph IN-PLACE using SemHash.

        Args:
            threshold: Similarity threshold (0.0 to 1.0).

        Returns:
            self (modified in-place)
        """
        logger.info(
            f"🚀 Starting in-place SemHash deduplication (threshold={threshold})..."
        )

        graph_data = self.data.model_copy()

        original_node_count = len(graph_data.nodes)
        original_edge_count = len(graph_data.edges)

        # 1. Process deduplication directly on current data
        graph_data = self._deduplicate_graph(graph_data, threshold)

        # 2. Atomic swap: re-index and rebuild OMem
        self._set_data_state(graph_data)

        logger.info(
            f"✅ In-place deduplication complete: "
            f"Nodes {original_node_count} -> {len(self.nodes)}, "
            f"Edges {original_edge_count} -> {len(self.edges)}"
        )
        return self
