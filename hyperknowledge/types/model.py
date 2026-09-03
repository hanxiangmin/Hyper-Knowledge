"""Unit Knowledge Pattern - extracts a single structured object from text."""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from .list import AutoList
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from ontomem.merger import BaseMerger, MergeStrategy, create_merger
from ontosight import view_nodes

from hyperknowledge.utils.logging import get_logger
from hyperknowledge.utils.index_security import (
    verify_index_manifest,
    write_index_manifest,
)

from .base import BaseAutoType, T

logger = get_logger(__name__)


DEFAULT_MODEL_PROMPT = (
    "You are an expert knowledge extraction assistant. "
    "Your task is to carefully analyze the following text and extract structured information "
    "according to the specified schema. Be precise, comprehensive, and faithful to the source text. "
    "Extract all relevant details without adding information not present in the text.\n\n"
    "### Source Text:\n"
    "{source_text}"
)


class AutoModel(BaseAutoType[T]):
    """AutoModel - extracts a single structured object from text.

    This pattern is designed for extracting exactly one structured object per document,
    regardless of document length. Suitable for document-level information like summaries,
    metadata, or aggregate statistics.

    Key characteristics:
        - Extraction target: One unique structured object per document
        - Merge strategy: Configurable via MergeStrategy enum (supports LLM-powered intelligent merging)
            * MERGE_FIELD: Non-null fields overwrite, lists append (simple field merge)
            * LLM.BALANCED: LLM intelligently synthesizes both versions (default)
            * LLM.PREFER_EXISTING: LLM synthesis but prioritizes original data
            * LLM.PREFER_INCOMING: LLM synthesis but prioritizes new data
        - Indexing strategy: Each non-null field of the object is indexed independently
        - Processing: Uses LangChain native batch processing for efficient multi-chunk handling
        - Advanced merging: All chunk extractions are treated as the same object, triggering merge logic
    """

    def __init__(
        self,
        data_schema: type[T],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        strategy_or_merger: MergeStrategy | BaseMerger = MergeStrategy.LLM.BALANCED,
        prompt: str = "",
        label_extractor: Callable[[T], str] | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs,
    ):
        """Initialize AutoModel with schema and configuration.

        Args:
            data_schema: Pydantic BaseModel subclass defining the object structure.
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            strategy_or_merger: Merge strategy for multi-chunk results. Can be:
                - MergeStrategy enum value (e.g., MergeStrategy.MERGE_FIELD, MergeStrategy.LLM.BALANCED)
                - Custom BaseMerger instance
                Default: MergeStrategy.LLM.BALANCED (LLM intelligently synthesizes both versions)
            prompt: Custom extraction prompt (defaults to generic prompt).
            label_extractor: Optional function to extract label from model instance for visualization.
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            verbose: Whether to log progress information.
        """
        # Store strategy before calling super().__init__
        self._strategy_or_merger = strategy_or_merger
        self._constructor_kwargs = kwargs

        # Store label extractor for visualization
        self._label_extractor = label_extractor

        super().__init__(
            data_schema,
            llm_client,
            embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

        # Initialize merger after super().__init__
        # Use a constant key extractor so all extractions are treated as the same object
        self._constant_key = "singleton"
        self._key_extractor = lambda x: self._constant_key

        if isinstance(strategy_or_merger, BaseMerger):
            self._merger = strategy_or_merger
        else:
            self._merger = create_merger(
                strategy=strategy_or_merger,
                key_extractor=self._key_extractor,
                llm_client=llm_client,
                item_schema=data_schema,
                **kwargs,
            )

    def _create_empty_instance(self) -> "AutoModel[T]":
        """Creates a new empty instance with the same configuration.

        Overrides parent method to include AutoModel-specific parameters.

        Returns:
            New AutoModel instance.
        """
        return self.__class__(
            data_schema=self._data_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            strategy_or_merger=self._strategy_or_merger,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            **self._constructor_kwargs,  # Propagate additional arguments
        )

    def _default_prompt(self) -> str:
        """Returns the default extraction prompt for single-object extraction."""
        return DEFAULT_MODEL_PROMPT

    @property
    def data(self) -> T:
        """Returns all stored knowledge (read-only access).

        Returns:
            The internal knowledge data as a Pydantic model instance.
        """
        return self._data

    def empty(self) -> bool:
        """Checks if the model is empty (no data stored).

        Returns:
            True if no data is stored, False otherwise.
        """
        if self._data is None:
            return True
        for field_name in self._data_schema.model_fields:
            value = getattr(self._data, field_name)
            # Check if the value is not considered empty
            if (
                value is not None
                and value != ""
                and value != []
                and value != {}
                and value != ()
            ):
                return False
        return True

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """
        INIT/RESET: Initialize or reset to empty state (None).
        Called during __init__ and when clear() is called.
        """
        self._data = None

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._index = None

    def _set_data_state(self, data: T) -> None:
        """
        SET: Full reset. Replace with new data (e.g., load from disk).
        Called by parse() or load() where data IS the new state.
        """
        self._data = data
        self.clear_index()

    def _update_data_state(self, incoming_data: T) -> None:
        """
        UPDATE: Incremental merge. Merge fields with field-level update strategy (called by feed()).

        For AutoModel, incremental update means filling missing fields, first extraction wins.
        """
        if self.empty():
            self._data = incoming_data
        else:
            merged_data = self.merge_batch_data([self._data, incoming_data])
            self._data = merged_data
        self.clear_index()

    # ==================== Core Methods ====================

    def merge_batch_data(self, data_list: list[T]) -> T:
        """Merge multiple extracted objects using configured strategy.

        Leverages ontomem's merge strategies to intelligently combine results from
        multiple chunks. All extractions are treated as the same object (singleton)
        to trigger the merge logic.

        Supported merge strategies:
        - MERGE_FIELD: Non-null fields overwrite, lists append (simple field merge)
        - LLM.BALANCED: LLM synthesizes both versions, balancing insights
        - LLM.PREFER_EXISTING: LLM synthesis prioritizing original data
        - LLM.PREFER_INCOMING: LLM synthesis prioritizing new data

        Args:
            data_list: List of extracted data objects from batch processing to merge.

        Returns:
            A new merged knowledge object with intelligently combined fields.
        """
        if not data_list:
            return None

        if len(data_list) == 1:
            return data_list[0]

        # Use merger to combine all items
        # Since all items have the same key ('singleton'), they will be grouped and merged
        merged_results = self._merger.merge(data_list)

        # Return the first (and should be only) merged result
        if merged_results:
            return merged_results[0]
        else:
            # Fallback to first item if merger returns empty
            return data_list[0]

    # ==================== Indexing & Query ====================

    def build_index(self):
        """Builds vector index from all non-null fields in the data object."""
        # Check if there's data to index
        if self.empty():
            return

        documents = []
        for field_name in self.data_schema.model_fields:
            field_value = getattr(self._data, field_name)
            if field_value is not None:
                documents.append(
                    Document(
                        page_content=field_name,
                        metadata={"raw": {field_name: field_value}},
                    )
                )

        self._index = FAISS.from_documents(documents, self.embedder)
        logger.info(f"Built FAISS index with {len(documents)} documents")

    def search(self, query: str, top_k: int = 3) -> list[Any]:
        """Searches all indexed fields using semantic similarity.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant knowledge items (field-value dictionaries).
        """
        # Check if there's data to search
        if not self.data.model_dump(exclude_none=True):
            logger.warning("No data to search")
            return []

        if self._index is None:
            raise Exception("Index is not built, please build the index first.")

        docs = self._index.similarity_search(query, k=top_k)

        # Restore original objects from metadata
        results = []
        for doc in docs:
            try:
                raw_data = doc.metadata["raw"]  # {field_name: field_value}
                results.append(raw_data)
            except Exception as e:
                logger.warning(f"Failed to restore item: {e}")

        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    # ==================== Index Storage ====================

    def dump_index(self, folder_path: str | Path) -> None:
        """Saves FAISS vector index to disk."""
        if self._index is None:
            return
        self._index.save_local(folder_path)
        write_index_manifest(folder_path)

    def load_index(self, folder_path: str | Path) -> None:
        """Loads FAISS vector index from disk."""
        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")
        verify_index_manifest(folder)
        self._index = FAISS.load_local(
            str(folder), self.embedder, allow_dangerous_deserialization=True
        )

    def show(
        self,
        label_extractor: Callable[[T], str] | None = None,
        *,
        top_k: int = 3,
    ) -> None:
        """Visualize the model using OntoSight.

        Args:
            label_extractor: Optional function to extract label from model instance for visualization.
                If not provided, uses the one from __init__.
            top_k: Number of items to retrieve for chat callback (default: 3).
        """
        if label_extractor is None:
            label_extractor = self._label_extractor

        if self._index is not None:
            logger.info(
                "Visualizing model with search and chat capabilities (indices detected)."
            )

            def chat_callback(question: str) -> None:
                response = self.chat(question, top_k=top_k)
                content = response.content
                retrieved_items = [self.data]
                return content, retrieved_items
        else:
            logger.info(
                "Visualizing list without search and chat capabilities (no indices detected)."
            )
            chat_callback = None

        from hashlib import md5

        def item_id_extractor(item: T) -> str:
            return md5(str(item.model_dump()).encode()).hexdigest()[:8]

        view_nodes(
            node_list=[self.data],
            node_schema=self._data_schema,
            node_id_extractor=item_id_extractor,
            node_label_extractor=label_extractor,
            on_chat=chat_callback,
            context={
                "title": f"{self._data_schema.__name__} Model",
                "description": f"Visualizing {len(self._data_schema.model_fields)} fields in AutoModel",
            },
        )

    # ==================== Operators ====================

    def __add__(self, other: Union["AutoModel", "AutoList"]) -> "AutoList":
        """Operator overload for '+' to combine AutoModel instances into AutoList.

        Supports multiple combination patterns:
        - AutoModel + AutoModel → AutoList (create list from both items)
        - AutoModel + AutoList → AutoList (prepend model to list)

        This enables intuitive chain operations like: unit1 + unit2 + unit3

        Usage:
            >>> unit1 = AutoModel(PersonSchema, ...)
            >>> unit2 = AutoModel(PersonSchema, ...)
            >>> person_list = unit1 + unit2  # → AutoList[PersonSchema]
            >>>
            >>> # Chain operations
            >>> unit3 = AutoModel(PersonSchema, ...)
            >>> person_list = unit1 + unit2 + unit3  # → AutoList with 3 items

        Args:
            other: Another AutoModel with the same data schema, or AutoList.

        Returns:
            AutoList containing both objects as items.

        Raises:
            TypeError: If schemas don't match or invalid operand type.
        """
        from .list import AutoList

        # Case 1: AutoModel + AutoModel → AutoList
        if isinstance(other, AutoModel):
            # Check schema compatibility
            if self._data_schema != other._data_schema:
                raise TypeError(
                    f"Cannot add AutoModel instances with different schemas. "
                    f"Left: {self._data_schema.__name__}, Right: {other._data_schema.__name__}"
                )

            # Create new AutoList
            list_ka = AutoList(
                item_schema=self._data_schema,
                llm_client=self.llm_client,
                embedder=self.embedder,
                prompt=self.prompt,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                max_workers=self.max_workers,
                verbose=self.verbose,
            )

            # Set items from both units
            list_ka._data.items = [self._data, other._data]

            # Merge metadata
            list_ka.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            list_ka.metadata["updated_at"] = datetime.now()

            return list_ka

        # Case 2: AutoModel + AutoList → AutoList (prepend model)
        elif isinstance(other, AutoList):
            # Check schema compatibility
            if self._data_schema != other.item_schema:
                raise TypeError(
                    f"Cannot add AutoModel to AutoList with different schemas. "
                    f"Unit: {self._data_schema.__name__}, List: {other.item_schema.__name__}"
                )

            # Create new AutoList with unit prepended
            new_list = AutoList(
                item_schema=self._data_schema,
                llm_client=self.llm_client,
                embedder=self.embedder,
                prompt=self.prompt,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                max_workers=self.max_workers,
                verbose=self.verbose,
            )

            # Prepend self to other's items
            new_list._data.items = [self._data] + other.items

            # Merge metadata
            new_list.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            new_list.metadata["updated_at"] = datetime.now()

            return new_list

        else:
            raise TypeError(
                f"Unsupported operand type for +: 'AutoModel' and '{type(other).__name__}'"
            )
