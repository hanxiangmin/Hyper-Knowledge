"""
Graph-RAG: Graph-based Retrieval-Augmented Generation
Extracts and manages entity-relationship knowledge graphs with standard binary edges.
"""

import json
from pathlib import Path
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from ontomem.merger import CustomRuleMerger
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoGraph

try:
    from graspologic.partition import hierarchical_leiden

    HAS_GRASPOLOGIC = True
except ImportError:
    HAS_GRASPOLOGIC = False


def _ensure_networkx():
    """Lazy import networkx, raise helpful error if not installed."""
    try:
        import networkx as nx

        return nx
    except ImportError:
        raise ImportError(
            "networkx is required for community detection. "
            "Install with: pip install networkx"
        )


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
    strength: int = Field(
        ge=1,
        le=10,
        description="Numerical score indicating relationship strength (1-10)",
    )


# ============================================================================
# Community Report Schema
# ============================================================================


class CommunityFinding(BaseModel):
    summary: str = Field(description="Summary of the insight")
    explanation: str = Field(description="Detailed explanation of the insight")


class CommunityReport(BaseModel):
    """Represents a summary of a graph community."""

    title: str = Field(description="Short title for the community")
    summary: str = Field(
        description="Detailed executive summary of the community's structure and key entities"
    )
    rating: float = Field(description="Impact severity rating (0-10)")
    findings: list[CommunityFinding] = Field(description="List of key findings")
    # Optional fields (filled programmatically)
    id: str | None = Field(default=None, description="Community ID")
    key_entities: list[str] | None = Field(
        default_factory=list, description="List of key entities in this community"
    )


# ============================================================================
# Extraction Prompts
# ============================================================================

Graph_RAG_NODE_EXTRACTION_PROMPT = """
-Goal-
Identify relevant entities from the text.
Entities will serve as nodes in the knowledge graph.

### Source Text:
{source_text}
"""

Graph_RAG_EDGE_EXTRACTION_PROMPT = """
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

COMMUNITY_REPORT_PROMPT = """
You are an expert analyst. 
Given the following list of entities and relationships within a specific community, generate a comprehensive report.

### Community Data:
Entities: {entities}
Relationships: {relationships}

### Output Requirements:
1. Title: A short name for the community.
2. Summary: An executive summary of the community's structure and dynamics.
3. Impact Rating: Score 0-10 based on importance/severity.
4. Key Findings: 3-5 main insights. Each finding must include a "summary" and an "explanation".

Output must strictly follow the JSON schema.
"""

GLOBAL_SEARCH_PROMPT = """
You are an intelligent assistant capable of answering questions based *solely* on the provided community summaries.

### Question: 
{query}

### Community Summaries:
{context}

### Instructions:
- Synthesize the information from the community summaries to answer the question.
- Do not use outside knowledge.
- If the answer includes multiple points, structure them clearly.
- If the context is insufficient, state that you cannot answer.

Answer:
"""

# ============================================================================
# Merge Templates for LLM.CUSTOM_RULE Strategy
# ============================================================================

Graph_RAG_NODE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Entity.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **name/type**: Keep the most frequent or precise value.
2. **description**: Synthesize a single, comprehensive description containing all unique details from the input descriptions. Write it in the third person. Resolve any contradictions coherently.
"""

Graph_RAG_EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Relationship (Edge).

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **source/target**: Store the two endpoints in lexicographic order. The fields do not encode direction.
2. **description**: Synthesize a single, comprehensive description covering the relationship dynamics from all inputs. Write it in the third person.
3. **strength**: Calculate the average of the input strengths (round to nearest integer).
"""

# ============================================================================
# Graph_RAG Class
# ============================================================================


class Graph_RAG(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Graph-RAG: Graph-based Retrieval-Augmented Generation

    Extracts entity-relationships (binary edges) and supports advanced GraphRAG features:
    - Community Detection (Leiden/Modularity)
    - Community Reports (Summarization)
    - Global Search (Map-Reduce over summaries)

    Implements the architecture of Microsoft GraphRAG / Nano-GraphRAG.
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
        Initialize Graph_RAG engine.

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

        # Edge key: canonical undirected endpoint pair
        edge_key_fn = lambda x: tuple(sorted((x.source, x.target)))

        # 2. Edge consistency check: tell AutoGraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: (x.source, x.target)

        # 3. Create custom Mergers with LLM.CUSTOM_RULE strategy
        # Node merger: merges entity descriptions using NODE_MERGE_RULE
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=Graph_RAG_NODE_MERGE_RULE,
        )

        # Edge merger: merges relationship descriptions using EDGE_MERGE_RULE
        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=Graph_RAG_EDGE_MERGE_RULE,
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
            prompt_for_node_extraction=Graph_RAG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=Graph_RAG_EDGE_EXTRACTION_PROMPT,
            # Pass custom merger instances
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            # Optimize indexing
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["description"],
            # Display labels
            node_label_extractor=lambda x: x.name,
            edge_label_extractor=lambda x: f"{x.description[:5]}...",
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

        # Community Management
        self.community_reports: dict[str, CommunityReport] = {}
        self._community_graph: Any | None = None
        self._community_hierarchy: dict[
            int, dict[str, list[str]]
        ] = {}  # level -> {community_id: [node_names]}
        self._node_to_community: dict[
            str, dict[str, Any]
        ] = {}  # node_name -> {level: community_id}

    def dump(self, folder_path: str | Path) -> None:
        """Saves graph state: internal data, community reports, and GraphML for visualization."""
        root = Path(folder_path)

        if self.verbose:
            print("Saving Results...")
            print("=" * 80)

        # 1. Save standard graph data (nodes, edges, index)
        super().dump(folder_path)

        # 2. Save Community Data (only if exists)
        if self.community_reports:
            community_data = {
                "reports": {
                    k: v.model_dump() for k, v in self.community_reports.items()
                },
                "hierarchy": {str(k): v for k, v in self._community_hierarchy.items()},
                "node_map": self._node_to_community,
            }

            comm_path = root / "community_data.json"
            with open(comm_path, "w", encoding="utf-8") as f:
                json.dump(community_data, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"✓ Results saved to {root}/")

    def load(self, folder_path: str | Path) -> None:
        """Loads graph state from directory."""
        root = Path(folder_path)

        # 1. Load standard graph data
        super().load(folder_path)

        # 2. Load Community Data (if exists)
        comm_path = root / "community_data.json"
        if comm_path.exists():
            with open(comm_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.community_reports = {
                k: CommunityReport.model_validate(v)
                for k, v in data.get("reports", {}).items()
            }
            self._community_hierarchy = {
                int(k) if k.isdigit() else k: v
                for k, v in data.get("hierarchy", {}).items()
            }
            self._node_to_community = data.get("node_map", {})

            if self.verbose:
                print(f"Loaded {len(self.community_reports)} community reports.")

    # ============================================================================
    # Community Detection & Summarization
    # ============================================================================

    def _ensure_community_graph(self):
        """Lazily build _community_graph from nodes and edges when needed."""
        if self._community_graph is None:
            nx = _ensure_networkx()
            self._community_graph = nx.Graph()
            for n in self.nodes:
                self._community_graph.add_node(n.name, **n.model_dump())
            for e in self.edges:
                self._community_graph.add_edge(
                    e.source, e.target, weight=float(e.strength), **e.model_dump()
                )
        return self._community_graph

    def build_communities(self, level: int = 0):
        """
        Detects communities in the graph and generates reports for them.
        Uses Leiden algorithm (via graspologic).

        Args:
            level: The hierarchical level for Leiden algorithm (default 0).
        """
        if self.empty():
            if self.verbose:
                print("Graph is empty, cannot build communities.")
            return

        nx = _ensure_networkx()

        if self.verbose:
            print("Building graph topology...")

        # Construct NetworkX graph
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.name, **node.model_dump())

        for edge in self.edges:
            # Use 'weight' if available, mapped from 'strength'
            G.add_edge(
                edge.source,
                edge.target,
                weight=float(edge.strength),
                **edge.model_dump(),
            )

        self._community_graph = G

        if not HAS_GRASPOLOGIC:
            if self.verbose:
                print(
                    "Error: `graspologic` is not installed. Please install it to use Leiden community detection."
                )
            return

        # Community Detection Strategy
        communities = []
        community_algo = "Leiden"

        if self.verbose:
            print("Using Hierarchical Leiden algorithm (graspologic)...")

        try:
            # Create a subgraph without isolated nodes for Leiden to avoid warnings
            G_leiden = G.copy()
            isolates = list(nx.isolates(G_leiden))
            G_leiden.remove_nodes_from(isolates)

            if G_leiden.number_of_nodes() == 0:
                if self.verbose:
                    print("No connected nodes found. Skipping community detection.")
                return

            # Hierarchical Leiden returns a list of CommunityAssignment objects
            # Each assignment has (node, cluster, level)
            hierarchical_clusters = hierarchical_leiden(G_leiden, max_cluster_size=100)

            # Transform to our internal structure: level -> community_id -> [nodes]
            self._community_hierarchy = {}
            self._node_to_community = {}

            # Group by level first
            clusters_by_level = {}
            for assignment in hierarchical_clusters:
                lvl = assignment.level
                cluster_id = f"LEVEL_{lvl}_CID_{assignment.cluster}"
                node = assignment.node

                if lvl not in clusters_by_level:
                    clusters_by_level[lvl] = {}
                if cluster_id not in clusters_by_level[lvl]:
                    clusters_by_level[lvl][cluster_id] = []

                clusters_by_level[lvl][cluster_id].append(node)

                # Track node mapping
                if node not in self._node_to_community:
                    self._node_to_community[node] = {}
                self._node_to_community[node][f"level_{lvl}"] = cluster_id

            self._community_hierarchy = clusters_by_level

            # Select the requested level for reports
            # In graspologic, level 0 is usually the top-most (coarsest)
            if level in self._community_hierarchy:
                communities = list(self._community_hierarchy[level].values())
                community_algo = f"Leiden (Level {level})"
            elif self._community_hierarchy:
                # Fallback to the first available level if requested level doesn't exist
                fallback_lvl = next(iter(self._community_hierarchy))
                communities = list(self._community_hierarchy[fallback_lvl].values())
                community_algo = f"Leiden (Fallback Level {fallback_lvl})"

        except Exception as e:
            if self.verbose:
                print(f"Leiden algorithm failed: {e}.")
            return

        if self.verbose:
            print(f"Detected {len(communities)} communities using {community_algo}.")

        # Generate Reports
        if self.verbose:
            print("Generating community reports...")
        self.community_reports = {}

        chain = ChatPromptTemplate.from_template(
            COMMUNITY_REPORT_PROMPT
        ) | self.llm_client.with_structured_output(
            CommunityReport, method="function_calling"
        )

        for i, community_nodes in enumerate(communities):
            cid = f"COMMUNITY_{i}"
            # Gather context
            subgraph_nodes = [n for n in self.nodes if n.name in community_nodes]
            # Edges where *both* source and target are in the community (strict)
            # Or edges where *at least one* is in the community (relaxed) -> tailored for coverage
            subgraph_edges = [
                e
                for e in self.edges
                if e.source in community_nodes and e.target in community_nodes
            ]

            if not subgraph_nodes:
                continue

            # Format minimal context for LLM to save tokens
            entities_txt = "\\n".join(
                [f"- {n.name} ({n.type}): {n.description}" for n in subgraph_nodes]
            )
            relationships_txt = "\\n".join(
                [f"- {e.source}—{e.target}: {e.description}" for e in subgraph_edges]
            )

            try:
                report = chain.invoke(
                    {"entities": entities_txt, "relationships": relationships_txt}
                )
                # Post-processing
                report.id = cid
                report.key_entities = list(community_nodes)[:10]  # Track top entities
                self.community_reports[cid] = report

                # Check mapping for manual fallback methods
                for node_name in community_nodes:
                    if node_name not in self._node_to_community:
                        self._node_to_community[node_name] = {}
                    self._node_to_community[node_name]["manual"] = cid

            except Exception as e:
                if self.verbose:
                    print(f"Failed to generate report for community {cid}: {e}")

        if self.verbose:
            print(
                f"Successfully generated {len(self.community_reports)} community reports."
            )

    # ============================================================================
    # Search Override with Community Support
    # ============================================================================

    def search(
        self,
        query: str,
        top_k_nodes: int = 3,
        top_k_edges: int = 3,
        top_k: int | None = None,
        use_community: bool = False,
    ) -> tuple[list, list, dict | None]:
        """Unified graph search interface with optional community enhancement.

        Args:
            query: Search query string.
            top_k_nodes: Number of node results to return (default: 3).
            top_k_edges: Number of edge results to return (default: 3).
            top_k: If provided, sets both top_k_nodes and top_k_edges to this value.
            use_community: If True, enables community-aware search.
                          Requires networkx and graspologic. Default: False.

        Returns:
            Tuple of (nodes, edges, community_context).
            community_context is None when use_community=False.
        """
        if use_community:
            return self._global_search_impl(query, top_k_nodes, top_k_edges)
        return super().search(query, top_k_nodes, top_k_edges, top_k)

    def _global_search_impl(
        self,
        query: str,
        top_k_nodes: int = 3,
        top_k_edges: int = 3,
    ) -> tuple[list, list, dict]:
        """Internal implementation for community-enhanced search."""
        if not self.community_reports:
            if self.verbose:
                print("No community reports found. Building communities first...")
            self.build_communities()

        community_context = self._get_community_context_for_query(query)
        nodes, edges = super().search(query, top_k_nodes, top_k_edges)

        return nodes, edges, community_context

    def _get_community_context_for_query(self, query: str) -> dict:
        """Get community context related to the query."""
        if not self.community_reports:
            return {}

        sorted_reports = sorted(
            self.community_reports.values(), key=lambda r: r.rating, reverse=True
        )[:3]

        return {
            "summaries": [
                {"title": r.title, "summary": r.summary, "rating": r.rating}
                for r in sorted_reports
            ]
        }
