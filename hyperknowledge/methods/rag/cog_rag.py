"""
COG_RAG: Cognitive-Inspired Dual-Hypergraph RAG System Pattern
Extracts and manages Theme-Entity relationships where Themes act as Hyperedges connecting multiple Entities.
"""

import json
import os
from datetime import datetime
from hashlib import md5

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from ontomem.merger import CustomRuleMerger
from pydantic import BaseModel, Field

from hyperknowledge.types.hypergraph import AutoHypergraph, AutoHypergraphSchema

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
# Theme Schemas (Layer 1: Macro Narrative)
# ============================================================================


class ThemeSchema(BaseModel):
    """Represents a Theme or Narrative Arc connecting multiple entities (Hyperedge)."""

    # participants: List[str] = Field(
    #     description="Names of key entities involved in this theme"
    # )
    participants: list[NodeSchema] = Field(
        description="List of key entities involved in this theme, with their details."
    )
    description: str = Field(
        description="A sentence that describes the primary theme, reflecting the main conflict, resolution, or key message"
    )


# ============================================================================
# Edge Schema (Layer 2: Micro Entity Relation)
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

COG_RAG_THEME_PROMPT = """
You are an expert narrative analyst.
Your goal is to extract "Themes" (Narrative Arcs) from the text.

A **Theme** is a high-level concept, conflict, or main idea that connects multiple entities.
For each Theme, you must also identify the key **Participants** (Entities) involved.

# Instructions
1. Analyze the text to identify primary themes/events.
2. For each theme, identify the entities involved.
3. Output the Theme description and the list of Participant Entities.

### Source Text:
{source_text}
"""

COG_RAG_NODE_EXTRACTION_PROMPT = """
-Goal-
Identify relevant entities from the text.
Entities will serve as participants in complex events later.

### Source Text:
{source_text}
"""

COG_RAG_EDGE_EXTRACTION_PROMPT = """
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

COG_RAG_NODE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Entity.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **name/type**: Keep the most frequent or precise value.
2. **description**: Synthesize a single, comprehensive description containing all unique details from the input descriptions. Write it in the third person. Resolve any contradictions coherently.
"""

COG_RAG_THEME_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Theme.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **participants**: Keep the list (they should be identical for the same theme key).
2. **description**: Synthesize a global theme description that encompasses the narrative details from all input themes. Write it in the third person.
"""

COG_RAG_EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Relationship.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **participants**: Keep the list (they should be identical for the same relationship key).
2. **description**: Synthesize a single, comprehensive description covering the relationship dynamics from all inputs. Write it in the third person.
3. **keywords**: Combine keyword lists from all inputs, removing duplicates.
4. **strength**: Calculate the average of the input strengths (round to nearest integer).
"""

# ============================================================================
# Theme Hypergraph (Layer 1: Macro Narrative)
# ============================================================================


class Cog_RAG_ThemeLayer(AutoHypergraph[NodeSchema, ThemeSchema]):
    """
    Layer 1 of Cog_RAG: Theme-First Extraction.
    Extracts Themes (Hyperedges) and Key Entities (Nodes) simultaneously.
    Follows the HyperGraph_RAG pattern (Edge-First).
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
        # 1. Define Key Extractors
        # Node key: exact match by name
        node_key_fn = lambda x: x.name

        # Theme key: md5 hash of description (Semantic uniqueness)
        edge_key_fn = lambda x: md5(x.description.encode()).hexdigest()

        # Nodes in theme
        nodes_in_edge_fn = lambda x: [n.name for n in x.participants]

        # 2. Create custom Mergers
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=COG_RAG_NODE_MERGE_RULE,
        )

        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=ThemeSchema,
            rule=COG_RAG_THEME_MERGE_RULE,
        )

        super().__init__(
            node_schema=NodeSchema,
            edge_schema=ThemeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Prompt is utilized in _extract_data override
            prompt_for_edge_extraction=COG_RAG_THEME_PROMPT,
            # Pass custom merger instances
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            # Optimize indexing
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["description"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    def _extract_data(self, text: str) -> AutoHypergraphSchema:
        """
        Extract Themes and nested Participants (One-Stage).
        Implements the HyperGraph_RAG extraction pattern.
        """
        # Batch Processing
        if len(text) <= self.chunk_size:
            raw_results_list = [self.edge_extractor.invoke({"source_text": text})]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"source_text": chunk} for chunk in chunks]
            raw_results_list = self.edge_extractor.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        # Transform to Flat Schema
        all_nodes_list = []
        all_edges_list = []

        for result in raw_results_list:
            if not result or not result.items:
                continue

            cur_nodes = []
            cur_edges = []

            for item in result.items:
                item: ThemeSchema
                extracted_nodes = item.participants
                cur_nodes.extend(extracted_nodes)

                cur_edges.append(item)

            all_nodes_list.append(cur_nodes)
            all_edges_list.append(cur_edges)

        # Merge
        raw_graph = self.merge_batch_data((all_nodes_list, all_edges_list))
        return self._prune_dangling_edges(raw_graph)


# ============================================================================
# Detail Hypergraph (Layer 2: Micro Relations)
# ============================================================================


class Cog_RAG_DetailLayer(AutoHypergraph[NodeSchema, EdgeSchema]):
    """
    Layer 2 of Cog_RAG: Entity-First Extraction.
    Extracts Entities (Nodes) and Semantic Relationships (Hyperedges).
    Follows the Hyper_RAG pattern (Two-Stage).
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
        node_key_fn = lambda x: x.name
        # Relations: Unique by Sorted Participants
        edge_key_fn = lambda x: tuple(sorted(x.participants))
        nodes_in_edge_fn = lambda x: x.participants

        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=COG_RAG_NODE_MERGE_RULE,
        )

        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=COG_RAG_EDGE_MERGE_RULE,
        )

        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
            prompt_for_node_extraction=COG_RAG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=COG_RAG_EDGE_EXTRACTION_PROMPT,
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["description", "keywords"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )


# ============================================================================
# Main System Class (Wrapper)
# ============================================================================


class Cog_RAG:
    """
    Cognitive-Inspired Dual-Hypergraph RAG System.

    Combines two Hypergraph Layers:
    1. Theme Layer (Cog_RAG_ThemeLayer): Captures macro narratives and themes.
    2. Detail Layer (Cog_RAG_DetailLayer): Captures micro entity relationships.
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
        self.metadata = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        self.theme_layer = Cog_RAG_ThemeLayer(
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )
        self.detail_layer = Cog_RAG_DetailLayer(
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )
        self.llm = llm_client
        self.verbose = verbose

    def feed_text(self, text: str):
        """Feed text to both hypergraph layers."""
        if self.verbose:
            print("Cog_RAG: Feeding text to Theme Layer...")
        self.theme_layer.feed_text(text)

        if self.verbose:
            print("Cog_RAG: Feeding text to Detail Layer...")
        self.detail_layer.feed_text(text)

    def build_index(self):
        """Build indices for both layers."""
        if self.verbose:
            print("Cog_RAG: Building indices...")
        self.theme_layer.build_index()
        self.detail_layer.build_index()

    def search(self, query: str, top_k_themes: int = 3, top_k_entities: int = 3):
        """
        Dual-Layer Search.
        Strategy:
        1. Macro: Search for Themes in ThemeLayer (Edge-First).
        2. Micro: Search for Entities in DetailLayer (Node-First).
        """
        # 1. Macro Context: Themes
        themes = self.theme_layer.search_edges(query, top_k=top_k_themes)

        # 2. Micro Context: Entities (Nodes)
        # Note: The user requested searching for "Specific Entities" in the second step.
        entities = self.detail_layer.search_nodes(query, top_k=top_k_entities)

        return {"themes": themes, "entities": entities}

    def chat(self, query: str, top_k_themes: int = 3, top_k_entities: int = 3):
        """Generate an answer using context from both layers."""
        results = self.search(query, top_k_themes, top_k_entities)

        context_parts = []
        if results["themes"]:
            context_parts.append("=== MACRO THEMES (Narrative Context) ===")
            for t in results["themes"]:
                context_parts.append(
                    f"- {t.description} (Involved: {', '.join([n.name for n in t.participants])})"
                )

        if results["entities"]:
            context_parts.append("\n=== MICRO ENTITIES (Specific Details) ===")
            for e in results["entities"]:
                context_parts.append(f"- [{e.type}] {e.name}: {e.description}")

        if not context_parts:
            context = "No relevant information found."
        else:
            context = "\n".join(context_parts)

        prompt = ChatPromptTemplate.from_template(
            "You are an intelligent assistant using a Dual-Layer Hypergraph Knowledge Abstract.\n"
            "Use the provided Themes (Macro) and Key Entities (Micro) to answer the user's question comprehensively.\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

        chain = prompt | self.llm
        return chain.invoke({"context": context, "question": query})

    def dump(self, folder_path: str):
        """Save both extracted graphs and metadata."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        metadata_path = os.path.join(folder_path, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False, default=str)

        # 导出根目录 data.json 以供 CLI 合法性校验和 info 命令统计
        root_data = {
            "nodes": [n.model_dump() for n in self.nodes],
            "edges": [e.model_dump() for e in self.edges],
        }
        with open(os.path.join(folder_path, "data.json"), "w", encoding="utf-8") as f:
            json.dump(root_data, f, ensure_ascii=False, indent=2)

        self.theme_layer.dump(os.path.join(folder_path, "theme_layer"))
        self.detail_layer.dump(os.path.join(folder_path, "detail_layer"))

    def load(self, folder_path: str):
        """Load extracted graphs and metadata."""
        metadata_path = os.path.join(folder_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                params = json.load(f)
                if isinstance(self.metadata, dict):
                    self.metadata.update(params)
                else:
                    self.metadata = params

        theme_path = os.path.join(folder_path, "theme_layer")
        if os.path.exists(theme_path) and os.path.exists(
            os.path.join(theme_path, "data.json")
        ):
            self.theme_layer.load(theme_path)

        detail_path = os.path.join(folder_path, "detail_layer")
        if os.path.exists(detail_path) and os.path.exists(
            os.path.join(detail_path, "data.json")
        ):
            self.detail_layer.load(detail_path)

    def show(
        self,
        node_label_extractor=None,
        edge_label_extractor=None,
    ):
        """Visualize the specified layer interactively."""
        print("\n[Cog_RAG] 这是一个双层图谱系统。请选择你想可视化的层级：")
        print("1. Detail Layer (细节层：具体实体及其关系) - [默认]")
        print("2. Theme Layer (主题层：宏观主题及其参与者)")

        try:
            choice = input("请输入选项 [1/2]: ").strip()
        except EOFError:
            choice = "1"

        layer_map = {
            "2": ("Theme Layer", self.theme_layer),
            "1": ("Detail Layer", self.detail_layer),
        }

        layer_name, layer_obj = layer_map.get(choice, layer_map["1"])

        print(f"Visualizing Cog_RAG ({layer_name})...")
        try:
            layer_obj.show(
                node_label_extractor=node_label_extractor,
                edge_label_extractor=edge_label_extractor,
            )
        except Exception as e:
            print(f"Error visualizing {layer_name}: {e}")

    @property
    def nodes(self):
        """Return combined unique nodes from both layers (simple aggregation)."""
        seen = set()
        unique = []
        for n in self.theme_layer.nodes + self.detail_layer.nodes:
            if n.name not in seen:
                seen.add(n.name)
                unique.append(n)
        return unique

    @property
    def edges(self):
        """Return all edges (Themes + Relations)."""
        return self.theme_layer.edges + self.detail_layer.edges
