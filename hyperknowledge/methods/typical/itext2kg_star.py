"""iText2KG_Star implementation using AutoGraph as the core engine.

This module provides a specialized implementation of the iText2KG_Star algorithm
using the AutoGraph framework, designed for extracting high-quality,
standardized triple-based knowledge graphs.

Prompts and schemas are adapted from the original iText2KG_Star implementation.
"""

from datetime import datetime

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import MergeStrategy
from pydantic import BaseModel, Field
from semhash import SemHash

from hyperknowledge.types.graph import AutoGraph, AutoGraphSchema
from hyperknowledge.utils.logging import get_logger

logger = get_logger(__name__)

# ==============================================================================
# 1. Schema Definition - Consistent with original iText2KG_Star implementation
# ==============================================================================


class NodeSchema(BaseModel):
    """Knowledge Graph Node: Standard node structure"""

    label: str = Field(
        description=(
            "The semantic category of the entity (e.g., 'Person', 'Event', 'Location', 'Methodology', 'Position'). "
            "Use 'Relationship' objects if the concept is inherently relational or verbal (e.g., 'plans'). "
            "Prefer consistent, single-word categories where possible (e.g., 'Person', not 'Person_Entity'). "
        )
    )
    name: str = Field(
        description=(
            "The unique name or title identifying this entity, representing exactly one concept. "
            "For example, 'Yassir', 'CEO', or 'X'. Avoid combining multiple concepts (e.g., 'CEO of X'), "
            "since linking them should be done via Relationship objects. "
            "Verbs or multi-concept phrases (e.g., 'plans an escape') typically belong in Relationship objects. "
        )
    )


class EdgeProperties(BaseModel):
    """Properties for Knowledge Graph Edge"""

    observation_date: str | None = Field(
        default=None,
        description=(
            "The date when the relationship was observed or recorded. "
            "This field is populated manually by the user after extraction. "
            "If multiple observation dates exist, use the latest date."
        ),
    )


class EdgeSchema(BaseModel):
    """Knowledge Graph Edge: Standard edge structure representing relationships between nodes"""

    startNode: NodeSchema = Field(
        description=(
            "The 'subject' or source entity of this relationship, which must appear in the known entities."
        )
    )
    endNode: NodeSchema = Field(
        description=(
            "The 'object' or target entity of this relationship, which must also appear in the known entities."
        )
    )
    name: str = Field(
        description=(
            "A single, canonical predicate capturing how the startNode and endNode relate (e.g., 'is_CEO', "
            "'holds_position', 'located_in'). Avoid compound verbs (e.g., 'plans_and_executes'). "
            "AVOID relation names as prepositions 'of', 'in' or similar."
        )
    )
    properties: EdgeProperties = Field(
        description="Additional properties describing the relationship."
    )


# ==============================================================================
# 2. Prompt Definition - Adapted from original iText2KG_Star implementation
# ==============================================================================


iText2KG_Star_EDGE_EXTRACTION_PROMPT = """
# DIRECTIVES : 
- Extract all meaningful relationships directly from the provided context.
- For each relationship, identify the start entity and end entity involved.
- Each entity should have a clear name and appropriate label/type.
- Avoid reflexive relations (entity relating to itself).
- IMPORTANT: Set 'observation_date' to null in all cases. Do NOT extract or infer dates from the context.
- The observation_date field should be populated by the user manually after extraction.

### Source Text:
{source_text}
"""


# ==============================================================================
# 3. iText2KG_Star Implementation - Inherits from AutoGraph
# ==============================================================================


class iText2KG_Star(AutoGraph[NodeSchema, EdgeSchema]):
    """
    iText2KG_Star: A specialized AutoGraph for extracting high-quality triple-based KGs.

    Features:
    - One-stage extraction: Extracts edges directly, then derives nodes automatically
    - Customized prompts from original iText2KG_Star implementation
    - Semantic Deduplication: Includes `match_nodes_and_update_edges` using SemHash with embeddings
    - Automatic date tracking: Observation date set to extraction time
    - Nested node schema: Maintains rich semantic information (name + label)

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>> kg = iText2KG_Star(llm_client=llm, embedder=embedder)

        >>> # 1. Extract relationships and derive nodes
        >>> kg.feed_text("Elon Musk is the CEO of SpaceX. Musk leads Tesla.")
        >>> print(f"Before dedup - Nodes: {len(kg.nodes)}, Edges: {len(kg.edges)}")

        >>> # 2. Deduplicate: Merges 'Elon Musk' and 'Musk'
        >>> kg.match_nodes_and_update_edges(threshold=0.85)
        >>> print(f"After dedup - Nodes: {len(kg.nodes)}, Edges: {len(kg.edges)}")
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        observation_date: str | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        """Initialize iText2KG_Star.

        Args:
            llm_client: Language model for extraction
            embedder: Embedding model for vector indexing
            observation_date: Date when the extraction was performed, like '1997-10-10' or '1997-10-10 23:59:59'.
                If None, uses current date and time.
            chunk_size: Characters per chunk
            chunk_overlap: Overlapping characters between chunks
            max_workers: Max concurrent extraction workers
            verbose: Display detailed execution logs and progress information
        """

        self.observation_date = observation_date

        # 1. Define Key Extractors (critical for deduplication)
        # Node deduplication: exact match by name
        node_key_fn = lambda x: x.name

        # Edge deduplication: combination of subject-predicate-object triple
        edge_key_fn = lambda x: f"{x.startNode.name}|{x.name}|{x.endNode.name}"

        # 2. Edge consistency check: tell AutoGraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: (x.startNode.name, x.endNode.name)

        # 3. Call parent class initialization
        logger.info("🔧 Initializing iText2KG_Star")
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Inject customized prompts
            prompt_for_edge_extraction=iText2KG_Star_EDGE_EXTRACTION_PROMPT,
            # Configure deduplication strategy
            node_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
            edge_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
            # Optimize indexing: only index name field
            node_fields_for_index=["name", "label"],
            edge_fields_for_index=["startNode", "name", "endNode"],
            # Display labels
            node_label_extractor=lambda x: x.name,
            edge_label_extractor=lambda x: x.name,
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    # ==================== Extraction Pipeline ====================

    def _extract_data(self, text: str) -> AutoGraphSchema:
        """Extract edges directly, then derive nodes (One-stage extraction).

        Process:
        1. Split text into chunks.
        2. Batch extract edges directly from chunks (Edges contain node info).
        3. Post-process: Set observation date to current date and time.
        4. Derive nodes from edges.
        5. Merge all partial graphs into one global graph.

        Args:
            text: Input text.

        Returns:
            Extracted and validated graph.
        """
        # 1. Prepare chunks
        if len(text) <= self.chunk_size:
            chunks = [text]
        else:
            chunks = self.text_splitter.split_text(text)

        # 2. Batch Extract Edges directly
        inputs = [{"source_text": chunk} for chunk in chunks]
        chunk_edge_lists = self.edge_extractor.batch(
            inputs, config={"max_concurrency": self.max_workers}
        )

        # 3. Post-process: Derive Nodes & Set Observation Date
        all_nodes_lists, all_edges_lists = [], []

        for edge_list in chunk_edge_lists:
            derived_nodes, processed_edges = [], []

            if edge_list and edge_list.items:
                for edge in edge_list.items:
                    # Post-process: Set observation date to current extraction time
                    edge: EdgeSchema
                    observation_date = self.observation_date or datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    edge.properties.observation_date = observation_date

                    # Derive nodes from edges
                    derived_nodes.append(edge.startNode)
                    derived_nodes.append(edge.endNode)
                    processed_edges.append(edge)

            all_nodes_lists.append(derived_nodes)
            all_edges_lists.append(processed_edges)

        # 4. Construct Partial Graphs (Tuple format for merge optimization)
        partial_graphs = (all_nodes_lists, all_edges_lists)

        # 5. Global Merge (passes tuples to merge_batch_data)
        raw_graph = self.merge_batch_data(partial_graphs)

        # Prune dangling edges to ensure graph consistency
        return self._prune_dangling_edges(raw_graph)

    # ==================== Node Deduplication ====================

    def match_nodes_and_update_edges(self, threshold: float = 0.8) -> "iText2KG_Star":
        """Match nodes in the graph and update edges accordingly using SemHash with embeddings.

        This method identifies and merges similar nodes based on semantic similarity
        using embeddings from the instance's embedder. It updates edges to reflect
        any changes in node identities.

        Args:
            threshold: Similarity threshold for matching nodes (0.0 to 1.0). Defaults to 0.8.

        Returns:
            The updated iText2KG_Star instance with matched nodes and updated edges.
        """
        logger.info(
            f"🚀 Starting node matching and edge update (threshold={threshold})..."
        )

        nodes, edges = self.nodes, self.edges

        if not nodes:
            logger.warning("⚠️ No nodes to match; skipping matching.")
            return self

        # 1. Generate Embeddings using self.embedder.embed_documents
        node_names = [n.name for n in nodes]
        logger.info(f"🔄 Generating embeddings for {len(node_names)} nodes...")

        try:
            embeddings = self.embedder.embed_documents(node_names)
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            return self

        # 2. Initialize SemHash from embeddings
        semhash = SemHash.from_embeddings(
            embeddings=embeddings,
            records=node_names,
            model=None,  # Embeddings already provided
        )

        # 3. Run Deduplication
        result = semhash.self_deduplicate(threshold=threshold)

        # 4. Build Mapping from duplicates result
        mapping = {}  # old_name -> new_name
        for record in result.filtered:
            if record.duplicates and len(record.duplicates) > 0:
                # Map the record to the first duplicate (representative)
                mapping[record.record] = record.duplicates[0][0]

        if not mapping:
            logger.info("✅ No similar nodes found above threshold.")
            return self

        logger.info(f"🔗 Found {len(mapping)} nodes to merge.")

        # 5. Apply mapping to graph data
        # Update Node names
        for node in nodes:
            if node.name in mapping:
                node.name = mapping[node.name]

        # Update Edge references (startNode and endNode are nested NodeSchema objects)
        for edge in edges:
            if edge.startNode.name in mapping:
                edge.startNode.name = mapping[edge.startNode.name]
            if edge.endNode.name in mapping:
                edge.endNode.name = mapping[edge.endNode.name]

        # 6. Update internal state
        new_data = AutoGraphSchema(nodes=nodes, edges=edges)
        self._set_data_state(new_data)

        logger.info(
            f"✅ Node matching complete: Nodes {len(nodes)} -> {len(self.nodes)}, Edges: {len(edges)}"
        )
        return self
