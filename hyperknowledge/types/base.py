import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, TypeVar

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from hyperknowledge.utils.logging import get_logger

logger = get_logger(__name__)


T = TypeVar("T", bound=BaseModel)


# ===================== Knowledge Abstract Class =====================


class BaseAutoType(ABC, Generic[T]):
    """Unified knowledge abstract class integrating extraction, storage, and aggregation.

    This abstract base class provides a complete framework for managing structured knowledge
    extracted from text. It handles the full lifecycle from extraction to serialization.

    Responsibilities:
        - Extract structured knowledge from text using LLM
        - Automatically handle long text chunking and parallel processing
        - Store and aggregate extracted knowledge with configurable merge strategies
        - Build and maintain vector indices for semantic search
        - Provide semantic search and retrieval capabilities
        - Support chat/QA interactions by retrieving relevant context and feeding it to LLM
        - Provide serialization and deserialization capabilities
    """

    # ==================== Initialization & Configuration ====================

    def __init__(
        self,
        data_schema: type[T],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        """Initialize the knowledge object with schema and processing configuration.

        Args:
            data_schema: Pydantic BaseModel subclass defining the knowledge structure.
            llm_client: Language model client for extraction.
            embedder: Embedding model for semantic search and similarity computation.
            prompt: Custom prompt template for extraction (defaults to generic prompt).
            chunk_size: Maximum chunk size for splitting long texts.
            chunk_overlap: Number of overlapping characters between chunks.
            max_workers: Maximum number of concurrent extraction tasks.
            verbose: Whether to display detailed execution logs and progress information.
        """
        self._data_schema = data_schema
        self.llm_client = llm_client
        self.embedder = embedder
        self.prompt = prompt or self._default_prompt()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose

        # Initialize template
        self.prompt_template = ChatPromptTemplate.from_template(self.prompt)
        self.data_extractor = (
            self.prompt_template
            | self.llm_client.with_structured_output(
                self._data_schema, method="function_calling"
            )
        )

        # Initialize text splitter for chunking long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "! ", "? ", " ", ""],
        )

        # Initialize internal state (calls hook for subclass setup)
        self._init_internal_state()

        # Internal state storing the extracted knowledge
        self.metadata: dict[str, Any] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def _create_empty_instance(self) -> "BaseAutoType[T]":
        """Creates a new empty instance with the same configuration as this one.

        Subclasses can override this method if they have special initialization requirements.

        Returns:
            A new empty knowledge instance with the same configuration.
        """
        return self.__class__(
            data_schema=self._data_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
        )

    @abstractmethod
    def _default_prompt(self) -> str:
        """Returns the default extraction prompt template.

        Subclasses must implement this to provide a prompt tailored to their extraction pattern.
        """

    # ==================== Data Access Interface ====================

    @property
    def data_schema(self) -> type[T]:
        """Returns the Pydantic schema class used by this knowledge instance.

        Returns:
            The Pydantic BaseModel subclass defining the knowledge structure.
        """
        return self._data_schema

    @property
    @abstractmethod
    def data(self) -> T:
        """Returns all stored knowledge (read-only access).

        This is an abstract property that subclasses must implement.
        Subclasses may apply transformations to convert internal _data structure
        to the external Schema T if they differ (e.g., AutoSet converts OMem → List).

        Returns:
            The internal knowledge data as a Pydantic model instance (or converted form).
        """

    @abstractmethod
    def empty(self) -> bool:
        """Checks if the knowledge abstract is currently empty.

        Returns:
            True if no data is stored, False otherwise.
        """

    # ==================== Data Management Operations ====================

    def clear(self):
        """Clears all knowledge including data and vector index."""
        self._init_internal_state()
        self.metadata["updated_at"] = datetime.now()

    def clear_index(self):
        """Clears the vector index without affecting the stored data."""
        self._init_index_state()

    # ==================== Lifecycle Hooks: State Management ====================

    def _init_internal_state(self) -> None:
        """Master control: Initialize or reset all internal state (INIT/RESET).

        This concrete method orchestrates the reset process by calling two hooks:
        1. _init_data_state() - Subclass responsibility: reset data structures
        2. _init_index_state() - Default: reset index, can be overridden by subclass

        Called in two scenarios:
        - During __init__ to set up the initial state
        - When clear() is called to reset to empty state
        """
        self._init_data_state()
        self._init_index_state()

    @abstractmethod
    def _init_data_state(self) -> None:
        """HOOK: Initialize or reset data structures to empty state.

        Subclass Responsibility:
        - Initialize self._data with appropriate structure (may differ from Schema T)
        - Reset any auxiliary data structures (e.g., lookup dicts, caches)

        Subclasses must implement this to set up internal structures that may be optimized
        beyond the standard Pydantic schema (e.g., OMem for AutoSet, dict-based for others).
        """

    @abstractmethod
    def _set_data_state(self, data: T) -> None:
        """HOOK: Overwrite data state with new data (SET).

        Called by parse() or load() where the data provided IS the new state.

        Subclass Responsibilities:
        1. Replace self._data with new data (full reset)
        2. Convert standard Schema T to optimized internal structure if needed
        3. Invalidate vector index (self.clear_index())

        Args:
            data: The new data object to set.
        """

    @abstractmethod
    def _update_data_state(self, incoming_data: T) -> None:
        """HOOK: Merge new data into state (UPDATE).

        Called by feed() where the data provided is INCREMENTAL.

        Subclass Responsibilities:
        1. Merge incoming_data into current data state (optimized for incremental updates)
        2. Invalidate vector index (self.clear_index())

        Subclasses should implement optimized incremental updates (e.g., set.add instead of
        full merge_batch, graph.add_edge instead of graph rebuild).

        Args:
            incoming_data: The incremental data to merge into the current state.
        """

    @abstractmethod
    def _init_index_state(self) -> None:
        """HOOK: Initialize or reset vector index to empty state.

        Subclass Responsibility:
        - Initialize or reset vector index structures
        - Can be FAISS, Chroma, Pinecone, or custom implementation
        - Typically sets self._index = None or initializes specific index instance

        This separation allows index implementation to be decoupled from base class.
        """

    # ==================== Extraction & Merge ====================

    def _extract_data(self, text: str) -> T:
        """Internal: Unified extraction logic (Chunking -> LLM -> Merge)."""
        logger.debug(
            "stage=extract_start input_chars=%d chunk_size=%d",
            len(text),
            self.chunk_size,
        )

        if len(text) <= self.chunk_size:
            logger.debug("stage=extract_single_chunk chunk_text_preview=%s", text[:200])
            try:
                extracted_data = self.data_extractor.invoke({"source_text": text})
            except Exception as e:
                # LLM returned unparseable output (e.g. prose instead of JSON).
                # Log and treat as an empty result instead of crashing the run.
                logger.warning("stage=extract_single_chunk_failed error=%s", e)
                extracted_data = None
            logger.debug(
                "stage=extract_single_chunk_result chunk=0 result_summary=%s",
                self._summarize_extracted(extracted_data),
            )
            extracted_data_list = [extracted_data]
        else:
            chunks = self.text_splitter.split_text(text)
            logger.debug("stage=text_split num_chunks=%d", len(chunks))
            for i, chunk in enumerate(chunks):
                logger.debug(
                    "stage=chunk_before_llm chunk_index=%d chunk_chars=%d chunk_text_preview=%s",
                    i,
                    len(chunk),
                    chunk[:200],
                )
            inputs = [{"source_text": chunk} for chunk in chunks]
            logger.debug(
                "stage=llm_batch_start max_concurrency=%d num_inputs=%d",
                self.max_workers,
                len(inputs),
            )
            # return_exceptions keeps one bad chunk from aborting the whole batch;
            # failures are logged and nulled (then filtered) below.
            extracted_data_list = self.data_extractor.batch(
                inputs,
                config={"max_concurrency": self.max_workers},
                return_exceptions=True,
            )
            cleaned = []
            for i, r in enumerate(extracted_data_list):
                if isinstance(r, Exception):
                    logger.warning(
                        "stage=chunk_extract_failed chunk_index=%d error=%s", i, r
                    )
                    r = None
                cleaned.append(r)
            extracted_data_list = cleaned
            logger.debug(
                "stage=llm_batch_complete results=%d", len(extracted_data_list)
            )
            for i, result in enumerate(extracted_data_list):
                logger.debug(
                    "stage=chunk_llm_result chunk_index=%d result_summary=%s",
                    i,
                    self._summarize_extracted(result),
                )

        # Filter out None results from failed LLM extractions
        extracted_data_list = self._filter_none_results(extracted_data_list)

        logger.debug("stage=merge_start num_items=%d", len(extracted_data_list))
        merged_data = self.merge_batch_data(extracted_data_list)
        logger.debug(
            "stage=extract_complete merged_summary=%s",
            self._summarize_extracted(merged_data),
        )
        return merged_data

    def _filter_none_results(self, results: list, default_factory=None) -> list:
        """Replace None results from batch LLM extractions with empty defaults.

        When the LLM fails to parse output (e.g., context length exceeded,
        json_schema validation failure), batch() returns None for that item.
        This method replaces None with empty objects to maintain index alignment
        with the original chunks list.

        Args:
            results: List of extraction results, may contain None values.
            default_factory: Callable that creates a default empty object.
                If None, None values are simply removed (legacy behavior).

        Returns:
            List with None values replaced or removed.
        """
        if not results:
            return results
        none_count = sum(1 for r in results if r is None)
        if none_count > 0:
            logger.warning(
                "stage=batch_filter none_results_detected none_count=%d total=%d",
                none_count,
                len(results),
            )
            if default_factory is not None:
                return [r if r is not None else default_factory() for r in results]
            return [r for r in results if r is not None]
        return results

    def _summarize_extracted(self, data: T) -> str:
        """Return a concise summary of extracted data for debug logging."""
        try:
            dump = data.model_dump()
            # Count entities and relations for graph-type schemas
            entities = len(dump.get("entities", []))
            relations = len(dump.get("relations", []))
            if entities or relations:
                return f"entities={entities} relations={relations}"
            # Generic fallback: list top-level keys with their lengths
            parts = []
            for key, val in dump.items():
                if isinstance(val, (list, tuple)):
                    parts.append(f"{key}={len(val)}")
                elif isinstance(val, str):
                    parts.append(f"{key}={val[:50]!r}")
            return ", ".join(parts) if parts else str(dump)[:100]
        except Exception:
            return repr(data)[:100]

    def parse(self, text: str) -> "BaseAutoType[T]":
        """
        Parses knowledge into a NEW instance without modifying the current one.

        Use this for previewing data or branching knowledge abstracts.

        Args:
            text: Input text.

        Returns:
            A new knowledge instance containing only the parsed data.
        """
        parsed_data = self._extract_data(text)

        new_instance = self._create_empty_instance()
        new_instance._set_data_state(parsed_data)

        new_instance.metadata["created_at"] = datetime.now()
        new_instance.metadata["updated_at"] = datetime.now()

        return new_instance

    def feed_text(self, text: str) -> "BaseAutoType[T]":
        """
        Ingests text into the CURRENT knowledge abstract instance.

        This modifies the internal state by merging new data with existing data.
        Supports method chaining (e.g., ka.feed_text(text1).feed_text(text2)).

        Args:
            text: Input text.

        Returns:
            Self (the current instance).
        """
        logger.debug("stage=feed_text_start input_chars=%d", len(text))
        extracted_data = self._extract_data(text)
        logger.debug("stage=extract_done")

        # Use UPDATE hook instead of manual merge+set
        self._update_data_state(extracted_data)
        logger.debug("stage=data_merged")

        self.metadata["updated_at"] = datetime.now()

        return self

    @abstractmethod
    def merge_batch_data(self, data_list: list[T]) -> T:
        """Merges multiple knowledge data objects into a single unified object.

        This is a pure data transformation method that does not modify internal state.
        Subclasses implement specific merge strategies (deduplication, conflict resolution, etc.).
        The batch merge is typically used during multi-chunk extraction where results from
        different chunks need to be aggregated into a single knowledge object.

        Responsibilities:
            - Implement concrete merge algorithms (deduplication, conflict resolution, etc.)
            - Return a new merged data object
            - Never modify instance attributes

        Args:
            data_list: List of knowledge data objects to merge from batch processing.

        Returns:
            A new merged knowledge object.
        """

    # ==================== Indexing & Search & Chat ====================

    @abstractmethod
    def build_index(self):
        """Builds or rebuilds the vector index for semantic search.

        Subclasses must implement this method to define how the vector index is constructed
        from the knowledge data. Uses FAISS as the vector store backend.
        """

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> list[Any]:
        """Performs semantic search over the knowledge abstract.

        Standard search workflow:
            1. Ensure index is built (call build_index if needed)
            2. Use vector_store.similarity_search for retrieval
            3. Restore original data structures from Document.metadata

        Subclasses can override this method to implement custom search logic.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant knowledge items.
        """

    def chat(self, query: str, top_k: int = 3) -> AIMessage:
        """Performs a chat-like interaction with the knowledge abstract.

        This generic method retrieves relevant items and generates a response.
        Subclasses with complex data structures (like graphs) should override this
        to provide better context formatting.

        Args:
            query: User query string.
            top_k: Number of relevant items to retrieve (default: 3).

        Returns:
            An AIMessage object containing the LLM-generated response.
        """
        # Step 1: Retrieve relevant items from knowledge abstract
        search_results = self.search(query, top_k)

        # Step 2: Format context from retrieved items
        formatted_context = []

        if not search_results:
            context = "No relevant information found in the knowledge abstract."
        else:
            for item in search_results:
                if isinstance(item, BaseModel):
                    formatted_context.append(item.model_dump_json(indent=2))
                elif isinstance(item, dict):
                    formatted_context.append(
                        json.dumps(item, indent=2, ensure_ascii=False)
                    )
                elif isinstance(item, str):
                    formatted_context.append(item)
                else:
                    raise ValueError(
                        "Search results must be Pydantic models, strings, or dicts for formatting."
                    )
            context = "\n---\n".join(formatted_context)

        # Step 3: Create QA prompt template and invoke LLM
        qa_prompt = ChatPromptTemplate.from_template(
            "Based on the following context from the knowledge abstract, answer the user's question.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

        qa_chain = qa_prompt | self.llm_client

        response = qa_chain.invoke({"context": context, "question": query})

        # Step 4: Inject retrieved items into response metadata
        if not response.additional_kwargs:
            response.additional_kwargs = {}
        response.additional_kwargs["retrieved_items"] = search_results

        # Step 5: Return the AIMessage response
        return response

    # ==================== Serialization: Orchestrator ====================

    def dump(self, folder_path: str | Path) -> None:
        """Saves the entire knowledge abstract (data, metadata, index) to a directory.

        This is the main entry point for serialization. It creates a directory structure:
            /folder_path
              |-- data.json       (The structured knowledge data)
              |-- metadata.json   (Metadata, localized config, timestamps)
              |-- /index          (Vector store files, e.g., FAISS)

        Args:
            folder_path: Target directory path.
        """
        root = Path(folder_path)
        root.mkdir(parents=True, exist_ok=True)

        # 1. Save Core Data
        self.dump_data(root / "data.json")

        # 2. Save Metadata
        self.dump_metadata(root / "metadata.json")

        # 3. Save Index (Sub-folder)
        # We perform a try-catch or check here because building an index is optional
        index_path = root / "index"
        if not index_path.exists():
            index_path.mkdir()
        try:
            self.dump_index(index_path)
            from hyperknowledge.utils.index_security import write_index_manifest

            write_index_manifest(index_path)
        except Exception as e:
            # If saving index fails (or isn't implemented/initialized), we treat it as non-fatal
            # user can always rebuild_index()
            print(f"Warning: Failed to save vector index: {e}")

    def load(self, folder_path: str | Path) -> None:
        """Loads the entire knowledge abstract from a directory.

        Args:
            folder_path: Source directory path.
        """
        root = Path(folder_path)
        if not root.exists():
            raise FileNotFoundError(f"Knowledge abstract directory not found: {root}")

        # 1. Load Core Data (Critical)
        self.load_data(root / "data.json")

        # 2. Load Metadata (Optional but recommended)
        meta_path = root / "metadata.json"
        if meta_path.exists():
            self.load_metadata(meta_path)

        # 3. Load Index (Optional)
        index_path = root / "index"
        if index_path.exists() and any(index_path.iterdir()):
            try:
                from hyperknowledge.utils.index_security import verify_index_manifest

                verify_index_manifest(index_path)
                self.load_index(index_path)
            except Exception as e:
                print(
                    f"Warning: Failed to load vector index: {e}. You may need to rebuild_index()."
                )

    # ==================== Serialization: Components ====================

    def dump_data(self, file_path: str | Path) -> None:
        """Saves the pure knowledge data to disk as JSON.

        Args:
            file_path: Target file path for saving data (e.g., "data.json").
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Use Pydantic's model_dump to serialize the schema
        export_data = self.data.model_dump()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    def load_data(self, file_path: str | Path) -> None:
        """Loads data from disk and restores internal state.

        Args:
            file_path: Source file path containing data (e.g., "data.json").
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Validate and Set State
        validated_data = self._data_schema.model_validate(raw_data)
        self._set_data_state(validated_data)

    def dump_metadata(self, file_path: str | Path) -> None:
        """Saves metadata (timestamps, configs) to disk.

        Args:
            file_path: Target file path.
        """
        path = Path(file_path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False, default=str)

    def load_metadata(self, file_path: str | Path) -> None:
        """Loads metadata from disk.

        Args:
            file_path: Source file path.
        """
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            params = json.load(f)

        # Timestamps are serialized as ISO strings (dump_metadata uses
        # default=str). Restore them to datetime so a loaded instance behaves
        # like a freshly created one; otherwise comparisons such as the
        # min(created_at, ...) merge in __add__ raise TypeError when a loaded
        # instance (str) is combined with a fresh one (datetime).
        for key in ("created_at", "updated_at"):
            value = params.get(key)
            if isinstance(value, str):
                try:
                    params[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass

        self.metadata.update(params)

    @abstractmethod
    def dump_index(self, folder_path: str | Path) -> None:
        """Save vector index to disk.

        Subclasses must implement to support their specific vector store
        (FAISS, Chroma, Pinecone, etc.).

        Args:
            folder_path: Target folder path for saving index files.
        """

    @abstractmethod
    def load_index(self, folder_path: str | Path) -> None:
        """Load vector index from disk.

        Subclasses must implement to support their specific vector store
        (FAISS, Chroma, Pinecone, etc.).

        Args:
            folder_path: Source folder path containing index files.
        """

    # ==================== Operator Overloads ====================

    def __add__(self, other: "BaseAutoType[T]") -> "BaseAutoType[T]":
        """Operator overload for '+' to merge two knowledge instances.

        Creates a new knowledge instance by merging the data from both instances.
        The new instance inherits configuration from the left operand (self).

        Usage:
            >>> kb1 = AutoList(PersonSchema, ...)
            >>> kb2 = AutoList(PersonSchema, ...)
            >>> kb3 = kb1 + kb2  # ✅ Same schema, creates merged instance
            >>>
            >>> kb4 = AutoList(CompanySchema, ...)
            >>> kb5 = kb1 + kb4  # ❌ TypeError: Different schemas

        Args:
            other: Another knowledge instance of the same type to merge with.

        Returns:
            A new knowledge instance containing merged data.

        Raises:
            TypeError: If other is not an instance of the same knowledge class or has different data schema.
        """
        # Check 1: Both must be instances of the same knowledge class
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot add {type(other).__name__} to {type(self).__name__}. "
                f"Both operands must be instances of the same knowledge class."
            )

        # Check 2: Both must have the same data schema
        if self._data_schema != other._data_schema:
            raise TypeError(
                f"Cannot add knowledge instances with different data schemas. "
                f"Left schema: {self._data_schema.__name__}, "
                f"Right schema: {other._data_schema.__name__}. "
                f"Both operands must have the same data schema to be merged."
            )

        # Merge the data from both instances
        merged_data = self.merge_batch_data([self._data, other._data])

        # Create a new instance with the same configuration
        new_instance = self._create_empty_instance()

        # Set the merged data using hook and update metadata
        new_instance._set_data_state(merged_data)
        new_instance.metadata["created_at"] = min(
            self.metadata["created_at"], other.metadata["created_at"]
        )
        new_instance.metadata["updated_at"] = datetime.now()

        return new_instance
