"""iText2KG implementation using AutoGraph as the core engine.

This module provides a specialized implementation of the iText2KG algorithm
using the AutoGraph framework, designed for extracting high-quality,
standardized triple-based knowledge graphs.

Prompts and schemas are adapted from the original iText2KG* implementation.
"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import MergeStrategy
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoGraph
from hyperknowledge.utils.logging import get_logger

logger = get_logger(__name__)

# ==============================================================================
# 1. Schema Definition - Consistent with original iText2KG implementation
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


# ==============================================================================
# 2. Prompt Definition - Adapted from original iText2KG implementation
# ==============================================================================

iText2KG_NODE_EXTRACTION_PROMPT = """
Extract entities from the source text. Each entity encoding exactly one concept 
(e.g., Person('Yassir'), Position('CEO'), Organization('X')). 
If verbs or actions appear, place them in a Relationship object rather than as an Entity. 
For instance, 'haira plans an escape' should yield separate Entities for Person('Haira'), Event('Escape'), 
and possibly a Relationship('Haira' -> 'plans' -> 'Escape')."

# DIRECTIVES : 
    - Act like an experienced knowledge graph builder.

### Source Text:
{source_text}
"""

iText2KG_EDGE_EXTRACTION_PROMPT = """
Based on the provided entities and context, identify the predicates that define relationships between these entities. 
The predicates should be chosen with precision to accurately reflect the expressed relationships.

# DIRECTIVES : 
    - Extract relationships between the provided entities based on the context.
    - Adhere completely to the provided entities list.
    - Do not change the name or label of the provided entities list.
    - Do not add any entity outside the provided list.
    - Avoid reflexive relations.

# Provided Entities
{known_nodes}

### Source Text:
{source_text}
"""


# ==============================================================================
# 3. iText2KG Implementation - Inherits from AutoGraph
# ==============================================================================


class iText2KG(AutoGraph[NodeSchema, EdgeSchema]):
    """
    iText2KG: A specialized AutoGraph for extracting high-quality triple-based KGs.

    Features:
    - Fixed Schema (NodeSchema, EdgeSchema) optimized for triple extraction
    - Customized prompts from original iText2KG* implementation
    - Automatic deduplication and consistency checking via AutoGraph's OMem
    - Two-stage extraction: entities first, then relationships

    Example:
        >>> llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>> kg = iText2KG(llm_client=llm, embedder=embedder)
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
        """Initialize iText2KG.

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
        edge_key_fn = lambda x: f"{x.startNode.name}|{x.name}|{x.endNode.name}"

        # 2. Edge consistency check: tell AutoGraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: (x.startNode.name, x.endNode.name)

        # 3. Call parent class initialization
        logger.info("🚀 Initializing iText2KG")
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
            prompt_for_node_extraction=iText2KG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=iText2KG_EDGE_EXTRACTION_PROMPT,
            # Configure deduplication strategy
            node_strategy_or_merger=MergeStrategy.LLM.BALANCED,
            edge_strategy_or_merger=MergeStrategy.LLM.BALANCED,
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
