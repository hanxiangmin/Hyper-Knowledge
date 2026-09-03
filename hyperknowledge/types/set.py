"""Set Knowledge Pattern - extracts a unique collection of objects from text.

Provides automatic deduplication based on a user-specified unique key field.
Supports multiple merge strategies including LLM-powered intelligent merging.
"""

from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from ontomem import OMem
from ontomem.merger import BaseMerger, MergeStrategy, create_merger
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


DEFAULT_SET_PROMPT = (
    "You are an expert knowledge extraction assistant. "
    "Extract all unique items from the text into a set. "
    "Be comprehensive and ensure no item is missed. "
    "Extract all items without adding information not present in the text.\n\n"
    "### Source Text:\n"
    "{source_text}"
)


class AutoSetSchema(BaseModel, Generic[ItemSchema]):
    """Generic schema container for set-based knowledge patterns."""

    items: list[ItemSchema] = Field(
        default_factory=list, description="Set of unique items"
    )


class AutoSet(BaseAutoType[AutoSetSchema[ItemSchema]], Generic[ItemSchema]):
    """AutoSet - extracts a unique collection of objects.

    This pattern automatically deduplicates items based on a user-specified
    key extractor function. Provides flexible merge strategies including LLM-powered
    intelligent merging for handling duplicates.

    Key characteristics:
        - Extraction target: A unique collection of structured objects
        - Deduplication: Based on key_extractor function (user-specified)
        - Merge strategy: Configurable via MergeStrategy enum:
            * KEEP_EXISTING: Preserve first (original) data, ignore updates
            * KEEP_INCOMING: Always use latest data, overwrite existing
            * MERGE_FIELD: Non-null fields overwrite, lists append (default)
            * LLM.BALANCED: LLM intelligently synthesizes both versions
            * LLM.PREFER_EXISTING: LLM synthesis but prioritizes original data
            * LLM.PREFER_INCOMING: LLM synthesis but prioritizes new data
            * LLM.CUSTOM_RULE: User-defined rules with dynamic context
        - Internal storage: Dict for O(1) lookup and deduplication
        - External interface: List (via items property)
        - Set operations: union (|), intersection (&), difference (-)

    Comparison with AutoList:
        - AutoList: Allows duplicates, simple append merge
        - AutoSet: Automatic deduplication, intelligent merge strategies

    Example:
        >>> class KeywordSchema(BaseModel):
        ...     term: str
        ...     category: str | None = None
        ...     frequency: int | None = None
        >>>
        >>> keywords = AutoSet(
        ...     item_schema=KeywordSchema,
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     key_extractor=lambda x: x.term,
        ...     merge_item_strategy="field_merge"
        ... )
        >>> keywords.parse("Python is great. Python is powerful.")
        >>> len(keywords)  # Only 1 item (deduplicated)
        1
    """

    if TYPE_CHECKING:
        # Use generic version during type checking to maintain complete type hints
        item_set_schema: type[AutoSetSchema[ItemSchema]]

    def __init__(
        self,
        item_schema: type[ItemSchema],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        key_extractor: Callable[[ItemSchema], Any],
        *,
        strategy_or_merger: MergeStrategy | BaseMerger = MergeStrategy.LLM.BALANCED,
        prompt: str = "",
        item_label_extractor: Callable[[ItemSchema], str] | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        fields_for_index: list[str] | None = None,
        **kwargs: Any,
    ):
        """Initialize AutoSet with key extractor and merge strategy.

        Args:
            item_schema: Pydantic BaseModel subclass for individual items.
            llm_client: Language model client for extraction and merging.
            embedder: Embedding model for vector indexing.
            key_extractor: Function to extract unique key from an item (required).
            strategy_or_merger: Merge strategy or pre-configured merger instance. Can be:
                                1. A MergeStrategy enum value (e.g., MergeStrategy.LLM.BALANCED)
                                2. A pre-configured BaseMerger instance (for full control)
            prompt: Custom extraction prompt.
            item_label_extractor: Optional function to extract label from item for visualization.
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            verbose: Whether to display detailed execution logs and progress information.
            fields_for_index: Optional list of field names in item_schema to include in vector index.
                             If None, all text fields are indexed by default.
                             Useful for optimizing search on complex schemas.
                             Example: ['name', 'summary'] (only index these fields)
            **kwargs: Additional arguments passed to create_merger() when strategy_or_merger is
                      a MergeStrategy enum. Ignored if strategy_or_merger is a BaseMerger instance.
        """

        # Store item_schema and index config
        self.item_schema = item_schema
        self.fields_for_index = fields_for_index
        self._constructor_kwargs = kwargs

        # Create AutoSetSchema container dynamically (similar to AutoList's AutoListSchema)
        container_name = f"{item_schema.__name__}Set"
        self.item_set_schema = create_model(
            container_name,
            items=(
                list[item_schema],
                Field(default_factory=list, description="Set of unique items"),
            ),
        )

        # AutoSet-specific attributes (MUST be initialized BEFORE super().__init__ calls _init_internal_state)
        self.key_extractor = key_extractor
        self.strategy_or_merger = strategy_or_merger

        # Setup Merge Strategy
        if isinstance(strategy_or_merger, BaseMerger):
            # Pre-configured merger instance: use directly
            if kwargs:
                logger.warning(
                    "Initialized with a Merger instance. Additional kwargs are ignored: %s",
                    list(kwargs.keys()),
                )
            self._merger = strategy_or_merger
        else:
            # MergeStrategy enum: create merger with strategy and pass kwargs
            self._merger = create_merger(
                strategy=strategy_or_merger,
                key_extractor=key_extractor,
                llm_client=llm_client,
                item_schema=item_schema,
                **kwargs,  # Pass additional arguments to create_merger
            )

        # Initialize OMem instance BEFORE calling super().__init__ so _init_internal_state can use it
        self._data_memory: OMem[ItemSchema] = OMem(
            memory_schema=item_schema,
            key_extractor=key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self._merger,
            verbose=verbose,
            fields_for_index=fields_for_index,  # Pass field selection to OMem
        )
        # Store label extractor for visualization
        self._item_label_extractor = item_label_extractor

        super().__init__(
            data_schema=self.item_set_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    # ==================== Override Instance Creation ====================

    def _create_empty_instance(self) -> "AutoSet[ItemSchema]":
        """Creates a new empty instance with the same configuration.

        Overrides parent method to include AutoSet-specific parameters.

        Returns:
            New AutoSet instance with identical configuration.
        """
        return self.__class__(
            item_schema=self.item_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            key_extractor=self.key_extractor,
            strategy_or_merger=self.strategy_or_merger,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            fields_for_index=self.fields_for_index,  # Persist index field configuration
            **self._constructor_kwargs,  # Propagate additional arguments
        )

    def _default_prompt(self) -> str:
        """Returns the default extraction prompt for set-based extraction."""
        return DEFAULT_SET_PROMPT

    @property
    def data(self) -> AutoSetSchema[ItemSchema]:
        """Returns all stored knowledge (read-only access).

        Returns:
            The internal knowledge data as a Pydantic model instance.
        """
        return self.data_schema(items=self.items)

    def empty(self) -> bool:
        """Checks if the set is empty.

        Returns:
            True if no items are stored, False otherwise.
        """
        return self._data_memory.empty()

    @property
    def items(self) -> list[ItemSchema]:
        """Returns the internal items as a list (for external interface compatibility).

        Returns:
            List of unique items.
        """
        return self._data_memory.items

    @property
    def keys(self) -> list[Any]:
        """Returns all unique key values.

        Returns:
            List of unique key values.
        """
        return self._data_memory.keys

    # ==================== State Management Lifecycle Overrides ====================

    def _init_data_state(self) -> None:
        """
        INIT/RESET: Initialize or reset OMem as empty.
        Called during __init__ and when clear() is called.
        """
        self._data_memory.clear()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._data_memory.clear_index()

    def _set_data_state(self, data: AutoSetSchema[ItemSchema]) -> None:
        """
        SET: Full Reset. Wipe OMem and refill from data (e.g., load from disk).
        Called by parse() or load() where data IS the new state.
        """
        self._data_memory.clear()
        if data.items:
            self._data_memory.add(data.items)
        self.clear_index()

    def _update_data_state(self, incoming_data: AutoSetSchema[ItemSchema]) -> None:
        """
        UPDATE: Incremental merge. Add to OMem efficiently (called by feed()).

        Unlike the default behavior which uses merge_batch for full re-merge,
        AutoSet optimizes this by directly adding items to OMem, which
        handles deduplication and merging internally.
        """
        if self.empty():
            self._set_data_state(incoming_data)
        elif incoming_data.items:
            self._data_memory.add(incoming_data.items)
            self.clear_index()

    # ==================== Core Override Methods ====================

    def merge_batch_data(
        self, data_list: list[AutoSetSchema[ItemSchema]]
    ) -> AutoSetSchema[ItemSchema]:
        """Merges multiple data containers with automatic deduplication.

        Pure function: Does not modify internal state.
        Delegates to OMem's merge strategy for efficient deduplication and merging.
        All merge strategies are handled by the Merger implementation in OMem.

        Args:
            data_list: List of container objects from batch processing to merge.

        Returns:
            New merged AutoSetSchema with deduplicated items and resolved conflicts.
        """
        all_items = []
        for data in data_list:
            all_items.extend(data.items)

        if not all_items:
            return self.item_set_schema()

        logger.info(
            f"Merging {len(all_items)} items from {len(data_list)} containers..."
        )

        merged_items = self._merger.merge(all_items)
        logger.info(f"Merged into {len(merged_items)} unique items.")

        return self.item_set_schema(items=merged_items)

    # ==================== Indexing & Query ====================

    def build_index(self, force: bool = False) -> None:
        """Build/rebuild independent vector index for each item in the set.

        Args:
            force: If True, forces rebuilding the index even if it already exists.
        """
        self._data_memory.build_index(force=force)

    def search(self, query: str, top_k: int = 3) -> list[ItemSchema]:
        """Searches items in the set using semantic similarity.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant items.
        """
        if not self.items:
            logger.warning("No items to search")
            return []
        if not self._data_memory.has_index():
            raise ValueError("Index not built. Call build_index() first.")
        return self._data_memory.search(query, top_k=top_k)

    # ==================== Index Storage ====================

    def dump_index(self, folder_path: str | Path) -> None:
        """Saves FAISS vector index to disk."""
        self._data_memory.dump_index(Path(folder_path))
        write_index_manifest(folder_path)

    def load_index(self, folder_path: str | Path) -> None:
        """Loads FAISS vector index from disk."""
        verify_index_manifest(folder_path)
        self._data_memory.load_index(Path(folder_path))

    def show(
        self,
        item_label_extractor: Callable[[ItemSchema], str] | None = None,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """Visualize the set using OntoSight.

        Args:
            item_label_extractor: Optional function to extract label from item for visualization.
                If not provided, uses the one from __init__.
            top_k_for_search: Number of items to retrieve for search callback (default: 3).
            top_k_for_chat: Number of items to retrieve for chat callback (default: 3).
        """
        if item_label_extractor is None:
            item_label_extractor = self._item_label_extractor

        if self._data_memory.has_index():
            logger.info(
                "Visualizing set with search and chat capabilities (indices detected)."
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
                "Visualizing set without search and chat capabilities (no indices detected)."
            )
            search_callback = None
            chat_callback = None

        view_nodes(
            node_list=self.items,
            node_schema=self.item_schema,
            node_id_extractor=self.key_extractor,
            node_label_extractor=item_label_extractor,
            on_search=search_callback,
            on_chat=chat_callback,
            context={
                "title": f"{self.item_schema.__name__} Set",
                "description": f"Visualizing {len(self.items)} unique items in AutoSet",
            },
        )

    # ==================== Set Interface Methods ====================

    def __len__(self) -> int:
        """Returns the number of unique items in the set."""
        return len(self._data_memory.items)

    def __contains__(self, key: Any) -> bool:
        """Checks if a unique key exists in the set.

        Args:
            key: The unique key value to check.

        Returns:
            True if key exists, False otherwise.
        """
        return self._data_memory.get(key) is not None

    def __repr__(self) -> str:
        """Returns a developer-friendly representation."""
        return f"AutoSet[{self.item_schema.__name__}]({len(self)} unique items)"

    def __str__(self) -> str:
        """Returns a user-friendly string representation."""
        return f"AutoSet with {len(self)} unique {self.item_schema.__name__} items"

    def __iter__(self) -> Iterator[ItemSchema]:
        """Enables iteration over all items in the set.

        Yields:
            Iterator over all unique items.

        Examples:
            >>> for skill in skills:
            ...     print(skill.name)
            >>> names = [s.name for s in skills]
        """
        return iter(self.items)

    # ==================== Set-Specific Methods ====================

    def add(self, item: ItemSchema) -> None:
        """Adds a single item to the set with automatic deduplication.

        Args:
            item: The item to add.
        """
        # OMem handles deduplication and merging automatically
        self._data_memory.add([item])
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def remove(self, key: Any) -> ItemSchema | None:
        """Removes an item by its unique key value.

        Args:
            key: The unique key value to remove.

        Returns:
            The removed item, or None if not found.
        """
        # Get item before removing
        item = self._data_memory.get(key)
        if item is None:
            return None

        # Remove from OMem
        removed = self._data_memory.remove(key)
        if removed:
            self.clear_index()
            self.metadata["updated_at"] = datetime.now()
            logger.debug(f"Removed item with key '{key}'")
        return item

    def contains(self, key: Any) -> bool:
        """Checks if an item with the given key exists in the set.

        Args:
            key: The unique key value to check.

        Returns:
            True if key exists, False otherwise.
        """
        return self._data_memory.get(key) is not None

    def get(self, key: Any, default: ItemSchema | None = None) -> ItemSchema | None:
        """Gets an item by its unique key value.

        Args:
            key: The unique key value to retrieve.
            default: Default value if key not found.

        Returns:
            The item if found, otherwise default.
        """
        result = self._data_memory.get(key)
        return result if result is not None else default

    def update(self, items: list[ItemSchema]) -> None:
        """Batch adds multiple items.

        Args:
            items: List of items to add.
        """
        # add() takes a single item and would wrap the whole list as one entry;
        # pass the list straight to the backing store so each item is added.
        self._data_memory.add(items)
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def discard(self, key: Any) -> None:
        """Removes an item by its unique key value, silently ignoring if not found.

        Unlike remove(), this method does not raise an error if the key does not exist.

        Args:
            key: The unique key value to remove.

        Examples:
            >>> skills.discard("Python")  # No error if not found

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        try:
            if self._data_memory.get(key) is not None:
                self._data_memory.remove(key)
                self.clear_index()
                self.metadata["updated_at"] = datetime.now()
        except (KeyError, Exception):
            pass

    def pop(self) -> ItemSchema:
        """Removes and returns an arbitrary item from the set.

        Returns:
            The removed item.

        Raises:
            KeyError: If the set is empty.

        Examples:
            >>> skill = skills.pop()
            >>> print(f"Removed: {skill.name}")

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        if not self._data_memory.items:
            raise KeyError("pop from an empty AutoSet")

        item = self._data_memory.items[0]
        key = self.key_extractor(item)
        self._data_memory.remove(key)

        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

        return item

    def copy(self) -> "AutoSet[ItemSchema]":
        """Creates a deep copy of the set.

        Returns:
            A new AutoSet instance with copies of all items.

        Examples:
            >>> backup = skills.copy()
            >>> backup.add(new_skill)
            >>> # Original skills unchanged
        """
        new_set = self._create_empty_instance()

        # Add copies of all items
        items_copy = [item.model_copy(deep=True) for item in self._data_memory.items]
        new_set._data_memory.add(items_copy)
        new_set.metadata = self.metadata.copy()
        # A copy preserves the original creation time and refreshes the
        # modification time (matching AutoList.copy()).
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    # ==================== Set Operations ====================

    def __or__(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Union operation: set1 | set2.

        Returns a new set containing all items from both sets.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with union of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for |: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot union AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_empty_instance()

        # Add all items from both sets (OMem handles merge automatically)
        all_items = self._data_memory.items + other._data_memory.items
        new_set._data_memory.add(all_items)
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __and__(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Intersection operation: set1 & set2.

        Returns a new set containing only items present in both sets.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with intersection of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for &: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot intersect AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_empty_instance()

        # Only keep items present in both sets (by key)
        intersection_items = [
            item
            for item in self._data_memory.items
            if self.key_extractor(item) in other.keys
        ]

        if intersection_items:
            new_set._data_memory.add(intersection_items)

        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __sub__(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Difference operation: set1 - set2.

        Returns a new set containing items in self but not in other.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with difference of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for -: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot subtract AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_empty_instance()

        # Only keep items not in other (by key)
        difference_items = [
            item
            for item in self._data_memory.items
            if self.key_extractor(item) not in other.keys
        ]

        if difference_items:
            new_set._data_memory.add(difference_items)

        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __xor__(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Symmetric difference operation: set1 ^ set2.

        Returns a new set containing items in either set but not in both.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with symmetric difference of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for ^: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compute symmetric difference of AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_empty_instance()

        # Items only in self
        symmetric_items = [
            item
            for item in self._data_memory.items
            if self.key_extractor(item) not in other.keys
        ]

        # Add items only in other
        symmetric_items.extend(
            [
                item
                for item in other._data_memory.items
                if self.key_extractor(item) not in self.keys
            ]
        )

        if symmetric_items:
            new_set._data_memory.add(symmetric_items)

        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    # ==================== Named Set Operations ====================

    def union(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Union operation (named method)."""
        return self | other

    def intersection(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Intersection operation (named method)."""
        return self & other

    def difference(self, other: "AutoSet[ItemSchema]") -> "AutoSet[ItemSchema]":
        """Difference operation (named method)."""
        return self - other

    def symmetric_difference(
        self, other: "AutoSet[ItemSchema]"
    ) -> "AutoSet[ItemSchema]":
        """Symmetric difference operation (named method)."""
        return self ^ other

    # ==================== Set Comparison Operations ====================

    def __eq__(self, other: object) -> bool:
        """Equality comparison: set1 == set2.

        Two sets are equal if they have the same schema and key set.
        Note: Does not compare item contents, only keys.

        Args:
            other: Another object to compare with.

        Returns:
            True if both sets have the same keys, False otherwise.

        Examples:
            >>> skills1 == skills2  # True if same keys
        """
        if not isinstance(other, AutoSet):
            return False

        if self.item_schema != other.item_schema:
            return False

        return self.keys == other.keys

    def __ne__(self, other: object) -> bool:
        """Inequality comparison: set1 != set2.

        Returns:
            True if sets are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __le__(self, other: "AutoSet[ItemSchema]") -> bool:
        """Subset comparison: set1 <= set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a subset of other (all keys in self are in other).

        Raises:
            TypeError: If other is not a AutoSet or has different schema.

        Examples:
            >>> skills1 <= skills2  # True if skills1 is subset of skills2
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self.keys).issubset(set(other.keys))

    def __lt__(self, other: "AutoSet[ItemSchema]") -> bool:
        """Proper subset comparison: set1 < set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a proper subset of other (subset and not equal).

        Examples:
            >>> skills1 < skills2  # True if skills1 is proper subset
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        return self <= other and self != other

    def __ge__(self, other: "AutoSet[ItemSchema]") -> bool:
        """Superset comparison: set1 >= set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a superset of other (all keys in other are in self).

        Examples:
            >>> skills1 >= skills2  # True if skills1 is superset of skills2
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self.keys).issuperset(set(other.keys))

    def __gt__(self, other: "AutoSet[ItemSchema]") -> bool:
        """Proper superset comparison: set1 > set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a proper superset of other (superset and not equal).

        Examples:
            >>> skills1 > skills2  # True if skills1 is proper superset
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        return self >= other and self != other

    def issubset(self, other: "AutoSet[ItemSchema]") -> bool:
        """Test whether every key in the set is in other.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a subset of other.

        Examples:
            >>> skills1.issubset(skills2)
        """
        return self <= other

    def issuperset(self, other: "AutoSet[ItemSchema]") -> bool:
        """Test whether every key in other is in the set.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a superset of other.

        Examples:
            >>> skills1.issuperset(skills2)
        """
        return self >= other

    def isdisjoint(self, other: "AutoSet[ItemSchema]") -> bool:
        """Test whether the set has no keys in common with other.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if the two sets have no keys in common.

        Raises:
            TypeError: If other is not a AutoSet or has different schema.

        Examples:
            >>> skills1.isdisjoint(skills2)  # True if no common skills
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"isdisjoint() argument must be AutoSet, not {type(other).__name__}"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self.keys).isdisjoint(set(other.keys))
