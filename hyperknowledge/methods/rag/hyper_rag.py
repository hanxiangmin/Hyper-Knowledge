"""
Hyper-RAG: Hypergraph-based Retrieval-Augmented Generation
Extracts and manages multi-entity relationships with support for n-ary hyperedges.
"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import CustomRuleMerger
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoHypergraph

# ============================================================================
# Node Schema
# ============================================================================


class NodeSchema(BaseModel):
    """Represents an entity extracted from the source text."""

    name: str = Field(description="Name of the entity")
    type: str = Field(
        description="Entity type (person, organization, geo, event, role, concept, etc.)",
    )
    description: str = Field(
        description="Comprehensive description of the entity's attributes and activities",
    )


# ============================================================================
# Edge Schema
# ============================================================================


class EdgeSchema(BaseModel):
    """Represents a relationship or event connecting multiple entities (low-order or high-order)."""

    participants: list[str] = Field(
        description="Names of entities involved in this relationship"
    )
    description: str = Field(
        description="Detailed explanation of the relationship or event"
    )
    keywords: list[str] = Field(
        description="List of keywords summarizing the relationship themes (e.g., ['conflict', 'trade', 'alliance'])",
    )
    strength: int = Field(
        ge=1,
        le=10,
        description="Numerical score indicating relationship strength (1-10)",
    )


# ============================================================================
# Extraction Prompts
# ============================================================================

Hyper_RAG_NODE_EXTRACTION_PROMPT = """
-Goal-
Identify relevant entities from the text.
Entities will serve as participants in complex events later.

### Source Text:
{source_text}
"""

Hyper_RAG_EDGE_EXTRACTION_PROMPT = """
-Goal-
You are an expert hypergraph knowledge extraction assistant. 
Extract "Hyperedges" that represent relationships, events, or thematic groupings involving MULTIPLE entities (2 or more) simultaneously.

-Definition-
A Hyperedge is a unified concept for any connection. 
It treats all involved entities as **participants** in a shared context 
(e.g., a conversation, a joint mission, a conflict, or a shared concept).

-Constraints-
1. You MUST ONLY use names from the "Allowed Entities" list provided below.
2. Do NOT create edges for entities that represent strictly different concepts with no interaction.
3. Ensure every edge has at least 2 participants.

# Provided Entities
{known_nodes}

### Source Text:
{source_text}
"""

# ============================================================================
# Merge Templates for LLM.CUSTOM_RULE Strategy
# ============================================================================

Hyper_RAG_NODE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Entity.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **name/type**: Keep the most frequent or precise value.
2. **description**: Synthesize a single, comprehensive description containing all unique details from the input descriptions. Write it in the third person. Resolve any contradictions coherently.
"""

Hyper_RAG_EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Hyperedge (Relationship/Event).

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **participants**: Keep the list (they should be identical for the same hyperedge key).
2. **description**: Synthesize a single, comprehensive description covering the relationship dynamics from all inputs. Write it in the third person.
3. **keywords**: Combine keyword lists from all inputs, removing duplicates.
4. **strength**: Calculate the average of the input strengths (round to nearest integer).
"""

# ============================================================================
# Hyper_RAG Class
# ============================================================================


class Hyper_RAG(AutoHypergraph[NodeSchema, EdgeSchema]):
    """
    Hyper-RAG: Hypergraph-based Retrieval-Augmented Generation

    Extracts multi-entity relationships (hyperedges) from text documents.

    Features:
    - Two-stage extraction: Entities first, then low-order (binary) and high-order (n-ary) relationships.
    - Custom Key Extractors: Precise deduplication using name-based node keys and sorted participant tuples for edges.
    - Hyperedge Support: Handles complex n-ary relationships connecting multiple entities simultaneously.
    - Structured Knowledge Representation: Pydantic-based Node and Edge schemas with comprehensive attributes.
    - Advanced Indexing: Optimized field-level indexing for efficient semantic search and retrieval."""

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        """
        Initialize Hyper_RAG engine.

        Args:
            llm_client (BaseChatModel): LLM client for text generation.
            embedder (Embeddings): Embedding model for text embeddings.
            chunk_size (int): Size of text chunks for indexing.
            chunk_overlap (int): Overlap between text chunks for indexing.
            max_workers (int): Maximum number of workers for indexing.
            verbose (bool): Display detailed execution logs and progress information.
        """
        # 1. Define Key Extractors (critical for deduplication)
        # Node key: exact match by name
        node_key_fn = lambda x: x.name

        # Edge key: sorted tuple of participants (set-like behavior for hyperedges)
        edge_key_fn = lambda x: tuple(sorted(x.participants))

        # 2. Edge consistency check: tell AutoHypergraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: x.participants

        # 3. Create custom Mergers with LLM.CUSTOM_RULE strategy
        # Node merger: merges entity descriptions using NODE_MERGE_RULE
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=Hyper_RAG_NODE_MERGE_RULE,
        )

        # Edge merger: merges relationship descriptions using EDGE_MERGE_RULE
        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=Hyper_RAG_EDGE_MERGE_RULE,
        )

        # 4. Call parent class initialization
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
            # Inject customized prompts for extraction
            prompt_for_node_extraction=Hyper_RAG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=Hyper_RAG_EDGE_EXTRACTION_PROMPT,
            # Pass custom merger instances
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            # Optimize indexing
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["keywords", "description"],
            # Display labels
            node_label_extractor=lambda x: x.name,
            edge_label_extractor=lambda x: f"{x.description[:5]}...",
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )
