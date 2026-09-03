"""Atom implementation using AutoGraph as the core engine.

This module provides a specialized implementation of the Atom algorithm
using the AutoGraph framework, designed for extracting high-quality,
standardized triple-based knowledge graphs.

Prompts and schemas are adapted from the original Atom implementation.
"""

from datetime import datetime

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from ontomem.merger import CustomRuleMerger, MergeStrategy
from pydantic import BaseModel, Field
from semhash import SemHash

from hyperknowledge.types.graph import AutoGraph, AutoGraphSchema
from hyperknowledge.utils.logging import get_logger

logger = get_logger(__name__)

# ==============================================================================
# 1. Schema Definition - Consistent with original Atom implementation
# ==============================================================================


class AtomicFactSchema(BaseModel):
    """Schema for extracting atomic facts from text."""

    atomic_fact: list[str] = Field(
        description=(
            "A comprehensive list of atomic, self-contained, and temporally-grounded facts extracted from the text."
        )
    )


class NodeSchema(BaseModel):
    """Schema for representing an entity."""

    label: str = Field(
        description=(
            "The semantic category of the entity (e.g., 'Person', 'Event', 'Location', 'Methodology', 'Position') as you understand it from the text. "
            "Use 'Relationship' objects if the concept is inherently relational or verbal (e.g., 'plans'). "
            "Prefer consistent, single-word categories where possible (e.g., 'Person', not 'Person_Entity'). "
            "Do not extract Date entities as they will be integrated in the relation."
        )
    )
    name: str = Field(
        description=(
            "The unique name or title identifying this entity, representing exactly one concept. "
            "For example, 'Yassir', 'CEO', or 'X'. Avoid combining multiple concepts (e.g., 'CEO of X'), "
            "since linking them should be done via Relationship objects. "
            "Verbs or multi-concept phrases (e.g., 'plans an escape') typically belong in Relationship objects. "
            "Do not extract Date entities as they will be integrated in the relation."
        )
    )


class EdgeSchema(BaseModel):
    """Schema for representing a relationship between two entities."""

    startNode: NodeSchema = Field(
        description=(
            "The 'subject' or source entity of this relationship, which must appear in the EntitiesExtractor."
        )
    )
    endNode: NodeSchema = Field(
        description=(
            "The 'object' or target entity of this relationship, which must also appear in the EntitiesExtractor."
        )
    )
    name: str = Field(
        description=(
            "A single, canonical predicate in PRESENT TENSE capturing how the startNode and endNode relate "
            "(e.g., 'is_CEO', 'holds_position', 'is_located_in', 'works_at'). "
            "ALWAYS use present tense verbs regardless of the temporal context in the text. "
            "Avoid compound verbs (e.g., 'plans_and_executes'). "
            "If the text implies negation (e.g., 'no longer CEO'), still use the affirmative present form (e.g., 'is_CEO') "
            "and rely on 't_end' for the end date. "
            "AVOID preposition-only relation names like 'of', 'in', 'at' - use descriptive present-tense verbs instead."
        )
    )
    t_start: list[str] | None = Field(
        default_factory=list,
        description=(
            "A time or interval indicating when this relationship begins or is active. "
            "Resolve relative temporal expressions based on the observation_time:\n"
            "  - 'today' → exact observation_time\n"
            "  - 'yesterday' → observation_time minus 1 day\n"
            "  - 'this week' → Monday of observation_time's week\n"
            "  - 'last week' → Monday of the week before observation_time\n"
            "  - 'this month' → first day of observation_time's month\n"
            "  - 'last month' → first day of the month before observation_time\n"
            "  - 'this year' → January 1st of observation_time's year\n"
            "  - 'last year' → January 1st of the year before observation_time\n"
            "Keep explicit dates as-is (e.g., '18-06-2024'). "
            "For example, if 'Yassir became CEO from 2023', then t_start=['01-01-2023']. "
            "This can be a single year, a date, or a resolved relative reference. "
            "Leave it [] if not specified."
        ),
    )
    t_end: list[str] | None = Field(
        default_factory=list,
        description=(
            "A time or interval indicating when this relationship ceases to hold. "
            "Resolve relative temporal expressions based on the observation_time using the same rules as t_start:\n"
            "  - 'today' → exact observation_time\n"
            "  - 'yesterday' → observation_time minus 1 day\n"
            "  - 'this week' → Monday of observation_time's week\n"
            "  - etc. (same resolution rules as t_start)\n"
            "Keep explicit dates as-is. "
            "For example, if 'Yassir left his position in 2025', then t_end=['01-01-2025']. "
            "Use this field to capture any 'end action' (e.g., leaving a job, ending a marriage), "
            "while keeping the relationship name in a canonical present tense form (e.g., 'is_CEO' not 'was_CEO'). "
            "Leave it [] if no end date/time is given."
        ),
    )
    t_obs: list[str] | None = Field(
        default=None,
        description=(
            "DO NOT EXTRACT OR INFER THIS FIELD. Leave it null/None. "
            "This field represents the extraction timestamp and will be populated manually by the user post-processing."
        ),
    )
    atomic_facts: list[str] | None = Field(
        default_factory=list,
        description=(
            "A list of exact string copies of the atomic facts or sentences from the source text that provide evidence for this relationship. "
            "Select the specific facts from the input context that justify this edge. "
            "Do NOT paraphrase or modify the text. Copy it exactly as it appears in the source."
        ),
    )


# ==============================================================================
# 2. Prompt Definition - Adapted from original Atom implementation
# ==============================================================================


Atom_FACTOID_EXTRACTION_PROMPT = """
Observation Date: {observation_time}

You are an expert factoid extraction engine. Your primary function is to read a news paragraph and its associated observation date, and then decompose the text into a comprehensive list of atomic, self-contained, and temporally-grounded facts.

## Task
Given an input paragraph and an `observation_time`, generate a list of all distinct factoids present in the text.

## Guidelines for Generating Temporal Factoids

### 1. Atomic Factoids
- Convert compound or complex sentences into short, single-fact statements
- Each factoid must contain exactly one piece of information or relationship
- Ensure that each factoid is expressed directly and concisely, without redundancies or duplicating the same information across multiple statements
- **Example:** "Unsupervised learning is dedicated to discovering intrinsic patterns in unlabeled datasets" becomes "Unsupervised learning discovers patterns in unlabeled data"

### 2. Decontextualization
- Replace pronouns (e.g., "it," "he," "they") with the full entity name or a clarifying noun phrase
- Include any necessary modifiers so that each factoid is understandable in isolation

### 3. Temporal Context
- Convert ALL time references to absolute dates/times using the observation_time

#### Conversion Rules:
- "today" → exact observation_time
- "yesterday" → observation_time minus 1 day
- "this week" → Monday of observation_time's week
- "last week" → Monday of the week before observation_time
- "this month" → first day of observation_time's month
- "last month" → first day of the month before observation_time
- "this year" → January 1st of observation_time's year
- "last year" → January 1st of the year before observation_time
- Keep explicit dates as-is (e.g., "June 18, 2024")

#### Additional Temporal Guidelines:
- Position time references naturally within factoids
- Split sentences with multiple time references into separate factoids
- **NEVER include relative terms like "today," "yesterday," "last week" in the final factoids**

### 4. Accuracy & Completeness
- Preserve the original meaning without combining multiple facts into a single statement
- Avoid adding details not present in the source text

### 5. End Actions
- If the text indicates the end of a role or an action (for example, someone leaving a position), be explicit about the role/action and the time it ended

### 6. Redundancies
- Eliminate redundancies by simplifying phrases
- **Example:** Convert "the method is crucial for maintaining X" into "the method maintains X"

## Example

**Input:** "On June 18, 2024, Real Madrid won the Champions League final with a 2-1 victory. Following the triumph, fans of Real Madrid celebrated the Champions League victory across the city."

**Output:**
- Real Madrid won the Champions League final on June 18, 2024
- The Champions League final ended with a 2-1 victory for Real Madrid on June 18, 2024
- Fans of Real Madrid celebrated the Champions League victory across the city on June 18, 2024

## Source Text:
{source_text}
"""

# Atom FACToid prompt ends, edge prompt begins
Atom_EDGE_EXTRACTION_PROMPT = """
Observation Date: {observation_time}

You are a precise knowledge extraction engine designed to distill unstructured text into a structured Knowledge Graph.
Your goal is to extract all meaningful relationships (edges) between entities, while rigorously capturing their temporal bounds and grounding evidence.

### Objective
Extract a list of relationships where each relationship consists of:
1. **Start Node**: The subject entity (Name + Label).
2. **End Node**: The object entity (Name + Label).
3. **Relation Name**: A canonical, present-tense predicate (e.g., 'works_at', 'is_CEO_of').
4. **Time Start (`t_start`)**: Strategies for when the relation began.
5. **Time End (`t_end`)**: Strategies for when the relation ended.
6. **Evidence (`atomic_facts`)**: The exact source sentences/facts supporting this edge.

### 🎯 Guidelines

#### 1. Entity & Relation Standards
- **Entities**: Extract precise names (e.g., "Apple Inc.", "Steve Jobs"). Assign accurate semantic labels (e.g., "Organization", "Person").
- **Relations**: use **SIMPLE PRESENT TENSE** verbs only (e.g., use 'manages', NOT 'managed', 'was_managing', or 'will_manage').
- **Forbidden**: Do NOT use vague prepositions like "in", "of", "at" as relation names. Use descriptive verbs instead (e.g., "located_in", "part_of").

#### 2. Temporal Extraction (Critical)
- **Format**: All dates must be in `YYYY-MM-DD` or `YYYY` format.
- **Lists**: `t_start` and `t_end` must always be lists of strings. If no date is found, use an empty list `[]`.
- **Relative Time Resolution**: Calculate absolute dates based on the **Observation Date** ({observation_time}).
    - "last year" -> {observation_time} year - 1 (Jan 1st)
    - "a few months ago" -> Estimate conservatively based on context.
    - "currently" -> implies the relationship is active (no `t_end`).
- **End Actions**: If the text says someone "left" or "stopped", capture this in `t_end` while keeping the relation positive (e.g., Relation: "works_at", t_end: ["2023-01-01"]).
- **t_obs**: Always set `t_obs` to null (or empty). Do not try to guess it.

#### 3. Evidence Attribution (atomic_facts)
- For every relationship extracted, identify the specific sentence(s) or atomic fact(s) in the source text that provide the evidence.
- **COPY EXACTLY**: Populate the `atomic_facts` list with the exact strings from the input text.
- **NO Paraphrasing**: Do not summarize or rewrite the source text in this field.
- If a relationship is derived from multiple facts, include all distinct facts in the list.

### 📝 Few-Shot Examples

**Input**: "Michel served as CFO at Acme Corp from 2019 to 2021. He was hired by Beta Inc in 2021, but left that role in 2023."
**Output**:
- (Michel, is_CFO_of, Acme Corp, t_start=["2019-01-01"], t_end=["2021-01-01"], atomic_facts=["Michel served as CFO at Acme Corp from 2019 to 2021."])
- (Michel, works_at, Beta Inc, t_start=["2021-01-01"], t_end=["2023-01-01"], atomic_facts=["He was hired by Beta Inc in 2021, but left that role in 2023."])

**Input**: "Sarah was a board member of GreenFuture until 2019."
**Output**:
- (Sarah, is_board_member_of, GreenFuture, t_start=[], t_end=["2019-01-01"], atomic_facts=["Sarah was a board member of GreenFuture until 2019."])

**Input**: "(Observation Date: 2024-06-15) John Doe is no longer the CEO of GreenIT since a few months ago."
**Output**:
- (John Doe, is_CEO_of, GreenIT, t_start=[], t_end=["2024-03-15"], atomic_facts=["John Doe is no longer the CEO of GreenIT since a few months ago."])
  *(Reasoning: "a few months ago" from June is approx. March)*

**Input**: "John Doe's marriage is happening on 26-02-2026."
**Output**:
- (John Doe, has_status, Married, t_start=["2026-02-26"], t_end=[], atomic_facts=["John Doe's marriage is happening on 26-02-2026."])

### ⚡ Directives
- Extract strictly what is in the text. Do not hallucinate external facts.
- Use the **Observation Date** as the anchor for all relative temporal expressions.
- Maintain consistency: The same entity name should be used across multiple relations.
- Ensure `atomic_facts` contains exact copies of the source text strings.

### Source Text:
{source_text}
"""


# ============================================================================
# Merge Templates for LLM.CUSTOM_RULE Strategy
# ============================================================================


EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of edges representing the exact same relationship (Same Subject -> Same Predicate -> Same Object).

Your task is to merge them into a SINGLE edge object exactly matching the schema.

Merge strategy:
1. **startNode/endNode**: Keep the node definitions consistent.
2. **name**: Keep the canonical predicate name (since they are already grouped by this key).
3. **t_start**: Collect ALL distinct start dates/times from all inputs into a single list. Remove exact duplicates.
4. **t_end**: Collect ALL distinct end dates/times from all inputs into a single list. Remove exact duplicates. 
5. **t_obs**: Collect ALL distinct observation dates from all inputs into a single list.
6. **atomic_facts**: Merge all evidence strings into a single list. Remove exact duplicate strings.
"""

# ==============================================================================
# 3. Atom Implementation - Inherits from AutoGraph
# ==============================================================================


class Atom(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Atom: A specialized AutoGraph for extracting high-quality triple-based KGs.

    Features:
    - Two-stage extraction: Extracts atomic facts first, then derives edges and nodes from facts
    - Customized prompts from original Atom implementation
    - Semantic Deduplication: Includes `match_nodes_and_update_edges` using SemHash with embeddings
    - Temporal tracking: t_start, t_end, and t_obs fields capture relationship timing and extraction metadata
    - Evidence attribution: atomic_facts field traces each extracted edge to source facts
    - Nested node schema: Maintains rich semantic information (name + label)

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>> kg = Atom(llm_client=llm, embedder=embedder)

        >>> # 1. Extract: Facts -> Edges -> Nodes
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
        observation_time: str | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        facts_per_chunk: int = 10,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        """Initialize Atom.

        Args:
            llm_client: Language model for extraction
            embedder: Embedding model for vector indexing
            observation_time: Date when the extraction was performed, like '1997-10-10' or '1997-10-10 23:59:59'.
                If None, uses current date and time.
            chunk_size: Characters per chunk
            chunk_overlap: Overlapping characters between chunks
            facts_per_chunk: Max number of atomic facts to group into a single extraction batch (default: 10)
            max_workers: Max concurrent extraction workers
            verbose: Display detailed execution logs and progress information
        """

        self.facts_per_chunk = facts_per_chunk
        self.observation_time = observation_time

        # 1. Define Key Extractors (critical for deduplication)
        # Node deduplication: exact match by name
        node_key_fn = lambda x: x.name

        # Edge deduplication: combination of subject-predicate-object triple
        edge_key_fn = lambda x: f"{x.startNode.name}|{x.name}|{x.endNode.name}"

        # 2. Edge consistency check: tell AutoGraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: (x.startNode.name, x.endNode.name)

        # Edge merger: merges relationship descriptions using EDGE_MERGE_RULE
        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=EDGE_MERGE_RULE,
        )

        # 3. Call parent class initialization
        logger.info("Initializing Atom")
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Inject customized prompts
            prompt_for_edge_extraction=Atom_EDGE_EXTRACTION_PROMPT,
            # Configure deduplication strategy
            node_strategy_or_merger=MergeStrategy.LLM.BALANCED,
            edge_strategy_or_merger=edge_merger,
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
        """Extract atomic facts first, then extract edges (Two-stage extraction).

        Process:
        1. Split text into chunks.
        2. Batch extract atomic facts from chunks.
        3. Consolidate facts into a unified context.
        4. Split consolidated facts into chunks.
        5. Batch extract edges from fact chunks.
        6. Post-process: Set t_obs timestamp & Derive nodes.
        7. Merge all partial graphs into one global graph.

        Args:
            text: Input text.

        Returns:
            Extracted and validated graph.
        """
        obs_date_str = self.observation_time or datetime.now().strftime("%Y-%m-%d")

        # ==================== Step 1: Extract Atomic Facts ====================
        logger.info("💡 [Phase 1] Extracting Atomic Facts...")

        # 1. Prepare raw chunks
        if len(text) <= self.chunk_size:
            raw_chunks = [text]
        else:
            raw_chunks = self.text_splitter.split_text(text)

        # 2. Define Fact Extraction Chain
        fact_prompt_template = ChatPromptTemplate.from_template(
            Atom_FACTOID_EXTRACTION_PROMPT
        )
        fact_chain = fact_prompt_template | self.llm_client.with_structured_output(
            AtomicFactSchema, method="function_calling"
        )

        # 3. Batch Extract Facts
        fact_inputs = [
            {"source_text": chunk, "observation_time": obs_date_str}
            for chunk in raw_chunks
        ]
        chunk_fact_lists: list[AtomicFactSchema] = fact_chain.batch(
            fact_inputs, config={"max_concurrency": self.max_workers}
        )

        # 4. Consolidate Facts
        all_facts = []
        for fact_list in chunk_fact_lists:
            if fact_list and fact_list.atomic_fact:
                all_facts.extend(fact_list.atomic_fact)

        logger.info(f"✅ Extracted {len(all_facts)} atomic facts.")

        if not all_facts:
            logger.warning("⚠️ No facts extracted. Returning empty graph.")
            return AutoGraphSchema()

        # ==================== Step 2: Extract Edges from Facts ====================
        logger.info("💡 [Phase 2] Extracting Edges from Atomic Facts...")

        # 5. Group Facts into Chunks (Controlled by count AND size)
        # This ensures each fact remains intact and fact IDs reset per chunk
        fact_chunks = []
        current_batch = []
        current_char_count = 0

        # Estimate overhead: "[Fact 99]: " + newline is approx 12 chars
        PREFIX_OVERHEAD = 12

        for fact in all_facts:
            fact_len = len(fact) + PREFIX_OVERHEAD

            # Check constraints:
            # 1. Size limit (fuzzy check to keep under chunk_size)
            # 2. Count limit (facts_per_chunk)
            size_limit_reached = (current_char_count + fact_len) > self.chunk_size
            count_limit_reached = len(current_batch) >= self.facts_per_chunk

            if (size_limit_reached or count_limit_reached) and current_batch:
                # Flush current batch
                formatted_chunk = "\n".join(
                    [f"[Fact {i + 1}]: {f}" for i, f in enumerate(current_batch)]
                )
                fact_chunks.append(formatted_chunk)

                # Reset
                current_batch = []
                current_char_count = 0

            current_batch.append(fact)
            current_char_count += fact_len

        # Flush remaining items
        if current_batch:
            formatted_chunk = "\n".join(
                [f"[Fact {i + 1}]: {f}" for i, f in enumerate(current_batch)]
            )
            fact_chunks.append(formatted_chunk)

        # 6. Batch Extract Edges directly from Fact Chunks
        edge_inputs = [
            {"source_text": chunk, "observation_time": obs_date_str}
            for chunk in fact_chunks
        ]
        chunk_edge_lists = self.edge_extractor.batch(
            edge_inputs, config={"max_concurrency": self.max_workers}
        )

        # ==================== Step 3: Post-process & Merge ====================

        # 7. Post-process: Derive Nodes & Set t_obs
        all_nodes_lists, all_edges_lists = [], []

        for edge_list in chunk_edge_lists:
            derived_nodes, processed_edges = [], []

            if edge_list and edge_list.items:
                for edge in edge_list.items:
                    edge: EdgeSchema
                    # Set t_obs to extraction timestamp
                    edge.t_obs = [obs_date_str]

                    # Derive nodes from edges
                    derived_nodes.append(edge.startNode)
                    derived_nodes.append(edge.endNode)
                    processed_edges.append(edge)

            all_nodes_lists.append(derived_nodes)
            all_edges_lists.append(processed_edges)

        # 8. Construct Partial Graphs
        partial_graphs = (all_nodes_lists, all_edges_lists)

        # 9. Global Merge
        raw_graph = self.merge_batch_data(partial_graphs)

        return self._prune_dangling_edges(raw_graph)

    # ==================== Node Deduplication ====================

    def match_nodes_and_update_edges(self, threshold: float = 0.8) -> "Atom":
        """Match nodes in the graph and update edges accordingly using SemHash with embeddings.

        This method identifies and merges similar nodes based on semantic similarity
        using embeddings from the instance's embedder. It updates edges to reflect
        any changes in node identities.

        Args:
            threshold: Similarity threshold for matching nodes (0.0 to 1.0). Defaults to 0.8.

        Returns:
            The updated Atom instance with matched nodes and updated edges.
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
