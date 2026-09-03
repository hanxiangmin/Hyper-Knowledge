"""HyperGraph_RAG implementation using AutoHypergraph as the core engine.

This module provides a specialized implementation of the HyperGraphRAG algorithm
using the AutoHypergraph framework, designed for extracting semantic knowledge
represented as hypergraphs where hyperedges ("knowledge segments") connect
multiple entities within specific contexts or events.

The HyperGraphRAG approach represents knowledge as contextual relationships where
each hyperedge encodes a complete semantic unit (sentence or event), maintaining
the natural information flow and contextual dependencies of the source material.
"""

from hashlib import md5

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import MergeStrategy
from pydantic import BaseModel, Field

from hyperknowledge.types.hypergraph import AutoHypergraph, AutoHypergraphSchema

# ============================================================================
# Node Schema
# ============================================================================


class NodeSchema(BaseModel):
    """Represents an entity extracted from the source text within a specific context."""

    name: str = Field(
        description="Name of the entity. Use the same language as the input text. If English, capitalize the name."
    )
    type: str = Field(
        description="Type of the entity (e.g., organization, person, geo, event, category, concept, object)."
    )
    description: str = Field(
        description="Comprehensive description of the entity's attributes and activities strictly within the current knowledge segment."
    )
    key_score: int = Field(
        description="A score from 0 to 100 indicating the importance of the entity within this context."
    )


# ============================================================================
# Edge Schema
# ============================================================================


class EdgeSchema(BaseModel):
    """Represents a knowledge segment (hyper-edge) that connects multiple entities through a specific context or event."""

    knowledge_segment: str = Field(
        description="A complete sentence or phrase from the text that captures a specific relationship, event, or context connecting the entities."
    )
    completeness_score: int = Field(
        description="A score from 0 to 10 indicating how complete and meaningful this knowledge segment is on its own."
    )
    # related_entities: List[str] = Field(
    #     description="A list of all entity names involved in or referenced by this knowledge segment."
    # )
    related_entities: list[NodeSchema] = Field(
        description="A list of all entities involved in or referenced by this knowledge segment."
    )


# ============================================================================
# Extraction Prompts
# ============================================================================

HyperGraph_RAG_EDGE_EXTRACTION_PROMPT = """
You are an expert information extraction system specializing in Hypergraph RAG.
Your goal is to extract "Hyper-edges" from the provided text. 

A **Hyper-edge** represents a specific "knowledge segment" (a sentence or event context) that connects multiple entities together.

# Instructions
1. **Analyze the Text**: Break the text down into complete, meaningful knowledge segments (sentences or clauses describing an event/relationship).
2. **Extract Entities**: For *each* segment, identify all relevant entities involved.
3. **Structure the Output**: For each segment, output an `EdgeSchema` containing:
    - The `knowledge_segment` text.
    - A `completeness_score` (0-10).
    - A list of `related_entities` found strictly within that segment.

# Extraction Rules
- **Entity Name**: Keep original language. Capitalize if English.
- **Entity Description**: Describe what the entity is doing or how it represents within *that specific segment*.
- **Entity Type**: Common types include organization, person, geo, event, category, concept, object.

# Few-Shot Examples

## Example 1
**Input Text**: 
"Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty."

**Output**:
[
  {{
    "knowledge_segment": "Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty.",
    "completeness_score": 8,
    "related_entities": [
      {{
        "name": "Alex",
        "type": "person",
        "description": "Alex is a person displaying frustration by clenching his jaw.",
        "key_score": 90
      }},
      {{
        "name": "Taylor",
        "type": "person",
        "description": "Taylor is a person exhibiting authoritarian certainty causing Alex's frustration.",
        "key_score": 85
      }}
    ]
  }}
]

## Example 2
**Input Text**: 
"The device could change the game for us," Taylor said, observing the machine with reverence.

**Output**:
[
  {{
    "knowledge_segment": "\"The device could change the game for us,\" Taylor said, observing the machine with reverence.",
    "completeness_score": 9,
    "related_entities": [
      {{
        "name": "Taylor",
        "type": "person",
        "description": "Taylor is a person who believes the device is game-changing and observes it with reverence.",
        "key_score": 95
      }},
      {{
        "name": "device",
        "type": "object",
        "description": "An object that Taylor believes could change the game.",
        "key_score": 90
      }}
    ]
  }}
]

## Source Text:
{source_text}
"""

# ============================================================================
# HyperGraph_RAG Class
# ============================================================================


class HyperGraph_RAG(AutoHypergraph[NodeSchema, EdgeSchema]):
    """HyperGraphRAG extractor using semantic knowledge segments as hyperedges.

    This class implements the HyperGraphRAG algorithm which models knowledge as a hypergraph
    where each hyperedge represents a complete "knowledge segment" (atomic semantic unit)
    that connects multiple related entities. Unlike traditional knowledge graphs that represent
    pairwise relationships, hypergraphs can naturally express n-ary relationships and maintain
    the original context and semantic integrity of information.

    The extraction process simultaneously identifies both knowledge segments (hyperedges) and
    the entities involved within each segment, followed by deduplication and merging across
    multiple text chunks.

    **Schema Components:**

    - **NodeSchema**: Represents an entity (node) extracted from the source text within a specific context.
        - `name` (str): The entity name, maintaining original language and capitalization.
        - `type` (str): Entity type such as 'person', 'organization', 'event', 'location', 'concept', etc.
        - `description` (str): Comprehensive description of the entity's attributes and activities within the knowledge segment.
        - `key_score` (int): Importance score (0-100) indicating the entity's significance in context.

    - **EdgeSchema**: Represents a knowledge segment (hyper-edge) that connects multiple entities through
      a specific context or event.
        - `knowledge_segment` (str): The actual text span (sentence or phrase) from source material capturing
          the relationship, event, or context connecting entities.
        - `completeness_score` (int): Quality score (0-10) indicating how complete and meaningful the segment
          is as a standalone knowledge unit.
        - `related_entities` (List[str]): Names of all entities involved in or referenced by this knowledge segment.
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
        """Initialize HyperGraph_RAG extraction engine.

        Configures the hypergraph extraction pipeline with LLM-based knowledge segment
        and entity identification, along with semantic embeddings for vector-based retrieval.

        Args:
            llm_client (BaseChatModel): Language model client for structured extraction.
            embedder (Embeddings): Embedding model for semantic vector representation.
            chunk_size (int): Text chunk size for processing (default: 2048 tokens).
            chunk_overlap (int): Overlap between consecutive chunks to preserve context (default: 256 tokens).
            max_workers (int): Maximum parallel workers for batch extraction (default: 10).
            verbose (bool): Whether to display detailed extraction logs (default: True).
        """
        # 1. Define Key Extractors
        node_key_fn = lambda x: x.name
        edge_key_fn = lambda x: md5(x.knowledge_segment.encode()).hexdigest()
        nodes_in_edge_fn = lambda x: [entity.name for entity in x.related_entities]

        # 4. Call parent class initialization
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Inject customized prompts for extraction
            prompt_for_edge_extraction=HyperGraph_RAG_EDGE_EXTRACTION_PROMPT,
            # Pass custom merger instances
            node_strategy_or_merger=MergeStrategy.LLM.BALANCED,
            edge_strategy_or_merger=MergeStrategy.LLM.BALANCED,
            # Optimize indexing
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["knowledge_segment"],
            # Display labels
            node_label_extractor=lambda x: x.name,
            edge_label_extractor=lambda x: f"{x.knowledge_segment[:5]}...",
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    def _extract_data(self, text: str) -> AutoHypergraphSchema[NodeSchema, EdgeSchema]:
        """Extract hypergraph knowledge from text via knowledge segment identification.

        Performs simultaneous extraction of knowledge segments (hyperedges) and associated entities
        from the input text. The extraction process:
        1. Segments the text into knowledge-bearing units (sentences/clauses)
        2. Identifies all entities referenced within each knowledge segment
        3. Merges and deduplicates extracted components across multiple chunks
        4. Prunes dangling edges (hyperedges without valid entity references)

        Args:
            text (str): Source text for hypergraph extraction.

        Returns:
            AutoHypergraphSchema[NodeSchema, EdgeSchema]: Extracted hypergraph containing
                deduplicated and merged entities (nodes) and knowledge segments (hyperedges).
        """
        # 1. Extract Hyperedges
        # Extract from single chunk or multiple chunks
        if len(text) <= self.chunk_size:
            raw_hyperedges = self.edge_extractor.invoke({"source_text": text})
            raw_hyperedges_list = [raw_hyperedges]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"source_text": chunk} for chunk in chunks]
            raw_hyperedges_list = self.edge_extractor.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        # Extract Nodes and Edges from raw_hyperedges_list
        all_nodes_list, all_edges_list = [], []

        for raw_hyperedges in raw_hyperedges_list:
            cur_nodes, cur_edges = [], []
            # batch()/invoke() can return None for a chunk when LLM extraction
            # fails; guard before accessing .items (matches Atom / iText2KG_Star).
            if raw_hyperedges and raw_hyperedges.items:
                for data in raw_hyperedges.items:
                    data: EdgeSchema
                    cur_nodes.extend(data.related_entities)
                    cur_edges.append(data)
            all_nodes_list.append(cur_nodes)
            all_edges_list.append(cur_edges)

        # Merge multiple hypergraphs
        partial_hypergraphs = (all_nodes_list, all_edges_list)
        raw_hypergraph = self.merge_batch_data(partial_hypergraphs)

        return self._prune_dangling_edges(raw_hypergraph)
