"""
Light-RAG: Lightweight Graph-based Retrieval-Augmented Generation
Extracts and manages entity-relationship knowledge graphs with standard binary edges.
"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import CustomRuleMerger
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoGraph

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
    """Represents an undirected relationship between two entities."""

    source: str = Field(description="First serialized endpoint; not an origin")
    target: str = Field(description="Second serialized endpoint; not a destination")
    description: str = Field(
        description="Detailed explanation of the relationship or event connection"
    )
    keywords: str = Field(
        description="Keywords summarizing the relationship (e.g., 'conflict, trade')",
    )
    strength: int = Field(
        ge=1,
        le=10,
        description="Numerical score indicating relationship strength (1-10)",
    )


# ============================================================================
# Extraction Prompts
# ============================================================================

Light_RAG_NODE_EXTRACTION_PROMPT = """
-Goal-
Identify relevant entities from the text.
Entities will serve as nodes in the knowledge graph.

### Source Text:
{source_text}
"""

Light_RAG_EDGE_EXTRACTION_PROMPT = """
-Goal-
You are an expert knowledge graph extraction assistant.
Extract binary "Edges" that represent relationships between exactly TWO entities.

-Definition-
An Edge represents one symmetric, undirected association between two entities. The Source and Target fields are serialization slots only.

-Constraints-
1. You MUST ONLY use names from the "Allowed Entities" list provided below.
2. Ensure every edge has exactly two endpoints and canonicalize their names in lexicographic order.
3. Provide a clear, comprehensive description for each edge.

# Provided Entities
{known_nodes}

### Source Text:
{source_text}
"""

# ============================================================================
# Merge Templates for LLM.CUSTOM_RULE Strategy
# ============================================================================

Light_RAG_NODE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Entity.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **name/type**: Keep the most frequent or precise value.
2. **description**: Synthesize a single, comprehensive description containing all unique details from the input descriptions. Write it in the third person. Resolve any contradictions coherently.
"""

Light_RAG_EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Relationship (Edge).

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **source/target**: Store the two endpoints in lexicographic order. The fields do not encode direction.
2. **description**: Synthesize a single, comprehensive description covering the relationship dynamics from all inputs. Write it in the third person.
3. **keywords**: Merge keywords from all inputs into a single comma-separated string, removing duplicates.
4. **strength**: Calculate the average of the input strengths (round to nearest integer).
"""

# ============================================================================
# Light_RAG Class
# ============================================================================


class Light_RAG(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Light-RAG: Standard Graph-based Retrieval-Augmented Generation

    Extracts entity-relationship graphs (nodes and binary edges) from text documents.
    Optimized for standard Knowledge Graph construction and traversal.

    Features:
    - Two-stage extraction: Entities first, then binary relationships.
    - Custom Key Extractors: Precise deduplication using name-based node keys and canonical endpoint pairs for edges.
    - Structured Knowledge Representation: Pydantic-based schemas.
    - Specialized Merging: Custom LLM rules for merging duplicate entities and relationships.
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
        """
        Initialize Light_RAG engine.

        Args:
            llm_client (BaseChatModel): LLM client for text generation.
            embedder (Embeddings): Embedding model for text embeddings.
            chunk_size (int): Size of text chunks for indexing.
            chunk_overlap (int): Overlap between text chunks for indexing.
            max_workers (int): Maximum number of workers for indexing.
            verbose (bool): Display detailed execution logs and progress information.
        """
        # 1. Define Key Extractors
        # Node key: exact match by name
        node_key_fn = lambda x: x.name

        # Edge key: canonical undirected endpoint pair
        edge_key_fn = lambda x: "|".join(sorted((x.source, x.target)))

        # 2. Edge consistency check: tell AutoGraph which nodes this edge connects
        # Returns (source, target) tuple
        nodes_in_edge_fn = lambda x: (x.source, x.target)

        # 3. Create custom Mergers
        # Node merger
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=Light_RAG_NODE_MERGE_RULE,
        )

        # Edge merger
        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=Light_RAG_EDGE_MERGE_RULE,
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
            prompt_for_node_extraction=Light_RAG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=Light_RAG_EDGE_EXTRACTION_PROMPT,
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
