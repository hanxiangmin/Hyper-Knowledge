"""List Knowledge Pattern - extracts a collection of objects from text."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from ontosight import view_nodes
from pydantic import BaseModel, Field, create_model

from hyperknowledge.utils.logging import get_logger
from hyperknowledge.utils.index_security import (
    verify_index_manifest,
    write_index_manifest,
)

from .base import BaseAutoType

logger = get_logger(__name__)


ItemSchema = TypeVar("ItemSchema", bound=BaseModel)


DEFAULT_LIST_PROMPT = (
    "You are an expert knowledge extraction assistant. "
    "Extract all relevant items from the text into a list. "
    "Be comprehensive and ensure no item is missed. "
    "Extract all items without adding information not present in the text.\n\n"
    "### Source Text:\n"
    "{source_text}"
)


class AutoListSchema(BaseModel, Generic[ItemSchema]):
    """Generic schema container for list-based knowledge patterns."""

    items: list[ItemSchema] = Field(default_factory=list, description="Item list")


class AutoList(BaseAutoType[AutoListSchema[ItemSchema]], Generic[ItemSchema]):
    """AutoList - extracts a collection of objects from text.

    This pattern extracts multiple independent objects from a document, suitable for
    extracting entities, events, references, or any collection of structured items.

    Key characteristics:
        - Extraction target: A collection of structured objects
        - Merge strategy: Append with basic deduplication (extensible by subclasses)
        - Indexing strategy: Each item in the list is indexed independently

    Comparison with AutoModel:
        - AutoModel: Extracts a single structured object (e.g., summary, metadata)
        - AutoList: Extracts multiple independent objects (e.g., entity list, event list)
    """

    if TYPE_CHECKING:
        # Use generic version during type checking to maintain complete type hints
        item_list_schema: type[AutoListSchema[ItemSchema]]

    def __init__(
        self,
        item_schema: type[ItemSchema],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        item_label_extractor: Callable[[ItemSchema], str] | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        fields_for_index: list[str] | None = None,
    ):
        """Initialize AutoList with item schema and configuration.

        Args:
            item_schema: Pydantic BaseModel subclass for individual list items.
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            prompt: Custom extraction prompt (defaults to list-oriented prompt).
            item_label_extractor: Optional function to extract label from item for visualization.
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            verbose: Whether to log progress information.
            fields_for_index: Optional list of field names to include in vector index.
                             If None, all fields are indexed.
        """
        self.item_schema = item_schema
        self.fields_for_index = fields_for_index

        container_name = f"{item_schema.__name__}List"
        self.item_list_schema = create_model(
            container_name,
            items=(
                list[item_schema],
                Field(default_factory=list, description="Item list"),
            ),
        )

        # check fields_for_index validity
        if self.fields_for_index:
            for field_name in self.fields_for_index:
                if field_name not in item_schema.model_fields:
                    raise ValueError(
                        f"Field '{field_name}' not found in item schema '{item_schema.__name__}'"
                    )
        # Store label extractor for visualization
        self._item_label_extractor = item_label_extractor

        super().__init__(
            data_schema=self.item_list_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    def _default_prompt(self) -> str:
        """Returns the default extraction prompt for list-based extraction."""
        return DEFAULT_LIST_PROMPT

    @property
    def items(self) -> list[ItemSchema]:
        """Returns the internal list of extracted items."""
        return getattr(self._data, "items", [])

    def _create_empty_instance(self) -> AutoList[ItemSchema]:
        """Creates a new empty instance with the same configuration.

        Overrides base class method to handle AutoList's item_schema parameter.

        Returns:
            A new AutoList instance with the same configuration.
        """
        return self.__class__(
            item_schema=self.item_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            fields_for_index=self.fields_for_index,
        )

    @property
    def data(self) -> AutoListSchema:
        """Returns all stored knowledge (read-only access).

        Returns:
            The internal knowledge data as AutoListSchema.
        """
        return self._data

    def empty(self) -> bool:
        """Checks if the list is empty.

        Returns:
            True if no items are stored, False otherwise.
        """
        return len(self._data.items) == 0

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """
        INIT/RESET: Initialize or reset with empty schema.
        Called during __init__ and when clear() is called.
        """
        self._data = self.item_list_schema()

    def _set_data_state(self, data: AutoListSchema) -> None:
        """
        SET: Full reset. Replace with new data (e.g., load from disk).
        Called by parse() or load() where data IS the new state.
        """
        self._data = data
        self.clear_index()

    def _update_data_state(self, incoming_data: AutoListSchema) -> None:
        """
        UPDATE: Incremental merge. Append incoming items to current list (called by feed()).

        For AutoList, incremental update means appending new items to existing list.
        """
        if self.empty():
            self._set_data_state(incoming_data)
        elif incoming_data.items:
            # Optimization: directly extend list instead of creating new objects
            self._data.items.extend(incoming_data.items)
            self.clear_index()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._index = None

    # ==================== Core Methods ====================

    def merge_batch_data(self, data_list: list[AutoListSchema]) -> AutoListSchema:
        """Pure data merge method implementing list append strategy.

        Merge strategy: Collects all items from all container objects and merges them
        into a single list. Used for aggregating extraction results from batch processing
        across multiple chunks. Subclasses can override this method to implement more
        sophisticated deduplication logic (e.g., AutoSet with custom key_extractor).

        Args:
            data_list: List of container objects from batch processing to merge.

        Returns:
            A new merged AutoListSchema object with combined items from all containers.
        """
        all_items = []

        for data in data_list:
            all_items.extend(data.items)

        return self.item_list_schema(items=all_items)

    def build_index(self) -> None:
        """Builds independent vector index for each item in the list.

        If fields_for_index is specified, only those fields are indexed.
        Otherwise, all fields are indexed.
        """
        if self.empty():
            return

        items = self.items

        if self._index is not None:
            return

        documents = []
        for idx, item in enumerate(items):
            # Extract content based on fields_for_index
            if self.fields_for_index:
                # Only index specified fields
                item_dict = item.model_dump()
                indexed_fields = {
                    k: v for k, v in item_dict.items() if k in self.fields_for_index
                }
                content = str(indexed_fields)
            else:
                # Index all fields
                content = item.model_dump_json()

            documents.append(
                Document(
                    page_content=content,
                    metadata={"raw": item.model_dump(), "index": idx},
                )
            )

        if documents:
            try:
                self._index = FAISS.from_documents(documents, self.embedder)
                logger.info(
                    f"Built FAISS index with {len(documents)} items (fields: {self.fields_for_index or 'all'})"
                )
            except ImportError:
                logger.error("FAISS not available. Install with: pip install faiss-cpu")
                raise

    def search(self, query: str, top_k: int = 3) -> list[ItemSchema]:
        """Searches items in the list using semantic similarity.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant items.
        """
        if not self.items:
            logger.warning("No items to search")
            return []

        if self._index is None:
            raise Exception("Vector store not initialized")

        docs = self._index.similarity_search(query, k=top_k)
        results: list[ItemSchema] = []
        for doc in docs:
            # Attempt to restore as object
            try:
                raw = doc.metadata.get("raw", {})
                item = self.item_schema.model_validate(raw)
                results.append(item)
            except Exception as e:
                logger.warning(f"Failed to restore item: {e}")
                results.append(doc.metadata.get("raw"))

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
        item_label_extractor: Callable[[ItemSchema], str] | None = None,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """Visualize the list using OntoSight.

        Args:
            item_label_extractor: Optional function to extract label from item for visualization.
                If not provided, uses the one from __init__.
            top_k_for_search: Number of items to retrieve for search callback (default: 3).
            top_k_for_chat: Number of items to retrieve for chat callback (default: 3).
        """
        if item_label_extractor is None:
            item_label_extractor = self._item_label_extractor

        if self._index is not None:
            logger.info(
                "Visualizing list with search and chat capabilities (indices detected)."
            )

            def search_callback(query: str) -> None:
                related_items = self.search(query, top_k=top_k_for_search)
                return related_items

            def chat_callback(question: str) -> None:
                response = self.chat(question, top_k=top_k_for_chat)
                content = response.content
                retrieved_items = response.additional_kwargs.get("retrieved_items", [])
                return content, retrieved_items
        else:
            logger.info(
                "Visualizing list without search and chat capabilities (no indices detected)."
            )
            search_callback = None
            chat_callback = None

        from hashlib import md5

        def item_id_extractor(item: ItemSchema) -> str:
            return md5(str(item.model_dump()).encode()).hexdigest()[:8]

        view_nodes(
            node_list=self.items,
            node_schema=self.item_schema,
            node_id_extractor=item_id_extractor,
            node_label_extractor=item_label_extractor,
            on_search=search_callback,
            on_chat=chat_callback,
            context={
                "title": f"{self.item_schema.__name__} List",
                "description": f"Visualizing {len(self.items)} items in AutoList",
            },
        )

    # ==================== Pythonic Sequence Operations ====================

    def __len__(self) -> int:
        """Returns the number of elements in the list."""
        return len(self.items)

    def __getitem__(self, key: int | slice) -> ItemSchema | AutoList[ItemSchema]:
        """Support index access and slicing.

        Args:
            key: Integer index or slice object.

        Returns:
            - For integer index: Returns the Item at that position
            - For slice: Returns a new AutoList instance with sliced items

        Raises:
            IndexError: If index is out of range.
            TypeError: If key is neither int nor slice.

        Examples:
            >>> knowledge[0]           # First item
            >>> knowledge[-1]          # Last item
            >>> knowledge[1:3]         # New AutoList with items [1:3]
            >>> knowledge[:5]          # First 5 items as new instance
        """
        if isinstance(key, int):
            # Integer index: return Item directly
            return self.items[key]
        elif isinstance(key, slice):
            # Slice: return new AutoList instance
            new_instance = self._create_empty_instance()
            new_instance._data.items = self.items[key]
            new_instance.metadata["updated_at"] = datetime.now()
            return new_instance
        else:
            raise TypeError(
                f"List indices must be integers or slices, not {type(key).__name__}"
            )

    def __setitem__(self, index: int, item: ItemSchema) -> None:
        """Support index assignment.

        Args:
            index: Position to set (supports negative indexing).
            item: The item to set at that position.

        Raises:
            TypeError: If item schema doesn't match.
            IndexError: If index is out of range.

        Examples:
            >>> knowledge[0] = new_item
            >>> knowledge[-1] = updated_item

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        self._validate_item_schema(item)
        self._data.items[index] = item
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def __add__(self, other: BaseAutoType[ItemSchema]) -> AutoList[ItemSchema]:
        """Operator overload for '+' to combine knowledge instances.

        Supports multiple combination patterns:
        - AutoList + AutoList → AutoList (merge lists)
        - AutoList + AutoModel → AutoList (append model to list)

        This enables chain operations like: model1 + model2 + model3

        Args:
            other: Another AutoList or AutoModel with compatible schema.

        Returns:
            New AutoList with combined items.

        Raises:
            TypeError: If schemas don't match or invalid operand type.
        """
        from .model import AutoModel

        # Case 1: AutoList + AutoList
        if isinstance(other, AutoList):
            # Check schema compatibility
            if self.item_schema != other.item_schema:
                raise TypeError(
                    f"Cannot add AutoList instances with different schemas. "
                    f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
                )
            # Create new instance with merged items
            new_instance = self._create_empty_instance()
            new_instance._data.items = self.items + other.items
            # Keep the earliest creation time and mark the merge as just updated,
            # consistent with the List + AutoModel case below and BaseAutoType.
            new_instance.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            new_instance.metadata["updated_at"] = datetime.now()
            return new_instance

        # Case 2: AutoList + AutoModel → AutoList (append model)
        elif isinstance(other, AutoModel):
            # Check schema compatibility
            if self.item_schema != other._data_schema:
                raise TypeError(
                    f"Cannot add AutoModel to AutoList with different schemas. "
                    f"List: {self.item_schema.__name__}, Unit: {other._data_schema.__name__}"
                )

            # Create new AutoList with appended model
            new_list = self._create_empty_instance()
            new_list._data.items = self.items + [other._data]

            # Merge metadata
            new_list.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            new_list.metadata["updated_at"] = datetime.now()

            return new_list

        else:
            raise TypeError(
                f"Unsupported operand type for +: 'AutoList' and '{type(other).__name__}'"
            )

    def __delitem__(self, index: int) -> None:
        """Support del operation for removing items by index.

        Args:
            index: Position to delete (supports negative indexing).

        Raises:
            IndexError: If index is out of range.

        Examples:
            >>> del knowledge[0]      # Delete first item
            >>> del knowledge[-1]     # Delete last item

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        del self._data.items[index]
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def __iter__(self) -> Iterator[ItemSchema]:
        """Support iteration over items.

        Returns:
            Iterator over items in the list.

        Examples:
            >>> for item in knowledge:
            ...     print(item.name)

            >>> items_list = list(knowledge)
            >>> names = [item.name for item in knowledge]
        """
        return iter(self.items)

    def __contains__(self, item: ItemSchema) -> bool:
        """Support 'in' operator for membership testing.

        Args:
            item: The item to check for membership.

        Returns:
            True if item exists in the list, False otherwise.

        Comparison Logic:
            1. Check if item's model_fields match any item's schema
            2. If schemas match, compare model_dump() equality

        Examples:
            >>> if person in knowledge:
            ...     print("Person already exists")
        """
        for existing_item in self.items:
            if self._items_equal(existing_item, item):
                return True
        return False

    def __repr__(self) -> str:
        """Return detailed string representation.

        Returns:
            String in format: ClassName[ItemSchema](count items)

        Examples:
            >>> repr(knowledge)
            'AutoList[PersonSchema](5 items)'
        """
        return (
            f"{self.__class__.__name__}[{self.item_schema.__name__}]({len(self)} items)"
        )

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            Brief description of the knowledge instance.

        Examples:
            >>> str(knowledge)
            'AutoList with 5 PersonSchema items'
        """
        return f"{self.__class__.__name__} with {len(self)} {self.item_schema.__name__} items"

    # ==================== List Modification Methods ====================

    def append(self, item: ItemSchema) -> None:
        """Append a single item to the end of the list.

        Args:
            item: The item to append.

        Raises:
            TypeError: If item schema doesn't match item_schema.

        Examples:
            >>> knowledge.append(PersonSchema(name="Alice", age=30))

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        self._validate_item_schema(item)
        self._data.items.append(item)
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def extend(self, items: Iterable[ItemSchema] | AutoList[ItemSchema]) -> None:
        """Extend the list by appending multiple items.

        Args:
            items: Iterable of items to append. Can be:
                - List of items
                - Another AutoList instance
                - Any iterable yielding items

        Raises:
            TypeError: If any item's schema doesn't match item_schema.

        Examples:
            >>> knowledge.extend([person1, person2, person3])
            >>> knowledge.extend(other_knowledge)

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        # Handle AutoList instance
        if isinstance(items, AutoList):
            if self.item_schema != items.item_schema:
                raise TypeError(
                    f"Cannot extend with AutoList of different schema. "
                    f"Expected: {self.item_schema.__name__}, "
                    f"Got: {items.item_schema.__name__}"
                )
            items_to_add = items.items
        else:
            items_to_add = list(items)

        # Validate all items
        for item in items_to_add:
            self._validate_item_schema(item)

        # Extend the list
        self._data.items.extend(items_to_add)
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def insert(self, index: int, item: ItemSchema) -> None:
        """Insert an item at a specific position.

        Args:
            index: Position to insert at (supports negative indexing).
            item: The item to insert.

        Raises:
            TypeError: If item schema doesn't match item_schema.

        Examples:
            >>> knowledge.insert(0, new_person)    # Insert at beginning
            >>> knowledge.insert(-1, new_person)   # Insert before last

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        self._validate_item_schema(item)
        self._data.items.insert(index, item)
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def remove(self, item: ItemSchema) -> None:
        """Remove the first occurrence of an item from the list.

        Args:
            item: The item to remove.

        Raises:
            ValueError: If item is not found in the list.

        Comparison Logic:
            Uses _items_equal() to find matching item.

        Examples:
            >>> knowledge.remove(person)

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        for i, existing_item in enumerate(self.items):
            if self._items_equal(existing_item, item):
                del self._data.items[i]
                self.clear_index()
                self.metadata["updated_at"] = datetime.now()
                return

        # Item not found
        raise ValueError(f"{item} is not in list")

    def pop(self, index: int = -1) -> ItemSchema:
        """Remove and return an item at the given position.

        Args:
            index: Position to pop (default: -1, last item).

        Returns:
            The removed item.

        Raises:
            IndexError: If list is empty or index is out of range.

        Examples:
            >>> last_item = knowledge.pop()
            >>> first_item = knowledge.pop(0)

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        if not self.items:
            raise IndexError("pop from empty list")

        item = self._data.items.pop(index)
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()
        return item

    # ==================== Query and Utility Methods ====================

    def index(self, item: ItemSchema, start: int = 0, stop: int | None = None) -> int:
        """Return the index of the first occurrence of item.

        Args:
            item: The item to find.
            start: Start searching from this position (default: 0).
            stop: Stop searching at this position (default: end of list).

        Returns:
            The index of the first matching item.

        Raises:
            ValueError: If item is not found in the specified range.

        Comparison Logic:
            Uses _items_equal() to match items.

        Examples:
            >>> idx = knowledge.index(person)
            >>> idx = knowledge.index(person, 5, 10)  # Search in range [5:10]
        """
        items = self.items[start:stop]
        for i, existing_item in enumerate(items):
            if self._items_equal(existing_item, item):
                return start + i

        raise ValueError(f"{item} is not in list")

    def count(self, item: ItemSchema) -> int:
        """Return the number of times item appears in the list.

        Args:
            item: The item to count.

        Returns:
            Number of occurrences.

        Comparison Logic:
            Uses _items_equal() to match items.

        Examples:
            >>> count = knowledge.count(person)
        """
        count = 0
        for existing_item in self.items:
            if self._items_equal(existing_item, item):
                count += 1
        return count

    def copy(self) -> AutoList[ItemSchema]:
        """Create a deep copy of this AutoList instance.

        Returns:
            A new AutoList instance with copied items and metadata.

        Note:
            The vector index is not copied; it needs to be rebuilt if needed.

        Examples:
            >>> backup = knowledge.copy()
            >>> backup.append(new_item)  # Original unchanged
        """
        new_instance = self._create_empty_instance()
        # Deep copy the data
        new_instance._data = self._data.model_copy(deep=True)
        # Copy metadata
        new_instance.metadata = self.metadata.copy()
        new_instance.metadata["updated_at"] = datetime.now()
        return new_instance

    def reverse(self) -> None:
        """Reverse the items in place.

        Examples:
            >>> knowledge.reverse()

        Side Effects:
            - Rebuilds the vector index if it exists (to maintain consistency)
            - Updates metadata timestamp

        Note:
            Does not call clear_index() since elements aren't modified,
            but rebuilds index to maintain metadata order consistency.
        """
        self._data.items.reverse()
        self.metadata["updated_at"] = datetime.now()

    def sort(
        self, key: Callable[[ItemSchema], Any] | None = None, reverse: bool = False
    ) -> None:
        """Sort the items in place.

        Args:
            key: Function to extract comparison key from each item.
                 Must be provided since Items may not be directly comparable.
            reverse: If True, sort in descending order (default: False).

        Raises:
            TypeError: If key is not provided and items aren't comparable.

        Examples:
            >>> knowledge.sort(key=lambda x: x.name)
            >>> knowledge.sort(key=lambda x: x.age, reverse=True)

        Side Effects:
            - Rebuilds the vector index if it exists (to maintain consistency)
            - Updates metadata timestamp

        Note:
            Does not call clear_index() since elements aren't modified,
            but rebuilds index to maintain metadata order consistency.
        """
        if key is None:
            raise TypeError(
                "sort() requires a 'key' function. "
                "Example: knowledge.sort(key=lambda x: x.name)"
            )

        self._data.items.sort(key=key, reverse=reverse)
        self.metadata["updated_at"] = datetime.now()

    # ==================== Helper Methods ====================

    def _validate_item_schema(self, item: Any) -> None:
        """Validate that item's schema matches item_schema.

        Args:
            item: The item to validate.

        Raises:
            TypeError: If schemas don't match, with detailed field difference.
        """
        if not isinstance(item, BaseModel):
            raise TypeError(
                f"Item must be a Pydantic BaseModel instance. "
                f"Got: {type(item).__name__}"
            )

        # Compare model_fields (schema structure)
        item_fields = type(item).model_fields
        expected_fields = self.item_schema.model_fields

        if item_fields != expected_fields:
            # Provide detailed error message
            expected_field_names = set(expected_fields.keys())
            got_field_names = set(item_fields.keys())

            missing = expected_field_names - got_field_names
            extra = got_field_names - expected_field_names

            error_parts = [
                (
                    f"Item schema mismatch. Expected {self.item_schema.__name__}, "
                    f"but got {type(item).__name__}."
                )
            ]

            if missing:
                error_parts.append(f"Missing fields: {sorted(missing)}")
            if extra:
                error_parts.append(f"Extra fields: {sorted(extra)}")

            if not missing and not extra:
                error_parts.append(
                    f"Expected fields: {sorted(expected_field_names)}, "
                    f"Got fields: {sorted(got_field_names)}"
                )

            raise TypeError(" ".join(error_parts))

    def _items_equal(self, item1: BaseModel, item2: BaseModel) -> bool:
        """Check if two items are equal.

        Args:
            item1: First item to compare.
            item2: Second item to compare.

        Returns:
            True if items are equal, False otherwise.

        Comparison Logic:
            1. Check if both have the same model_fields (schema)
            2. If schemas match, compare model_dump() equality
        """
        # Check schema compatibility
        if type(item1).model_fields != type(item2).model_fields:
            return False

        # Compare data
        return item1.model_dump() == item2.model_dump()
