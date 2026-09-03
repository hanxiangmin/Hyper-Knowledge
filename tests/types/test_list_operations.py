"""Unit tests for AutoList operations."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoList
from tests.fixtures import PersonSchema


class PersonItemSchema(BaseModel):
    """Schema for person list items."""

    name: str
    age: Optional[int] = None


class TestAutoListOperations:
    """Test cases for AutoList basic operations."""

    def test_init_and_empty_state(self, llm_client, embedder):
        """Test that AutoList initializes correctly."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert auto_list.empty() is True
        assert len(auto_list) == 0
        assert len(auto_list.items) == 0

    def test_item_schema_property(self, llm_client, embedder):
        """Test that item_schema property returns correct schema."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        assert auto_list.item_schema == PersonItemSchema

    def test_append_single_item(self, llm_client, embedder):
        """Test appending a single item."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        item = PersonItemSchema(name="John", age=30)
        auto_list.append(item)

        assert len(auto_list) == 1
        assert auto_list.items[0].name == "John"

    def test_append_multiple_items(self, llm_client, embedder):
        """Test appending multiple items one by one."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        assert len(auto_list) == 2

    def test_extend_with_list(self, llm_client, embedder):
        """Test extending with a Python list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        items = [
            PersonItemSchema(name="John", age=30),
            PersonItemSchema(name="Jane", age=25),
        ]
        auto_list.extend(items)

        assert len(auto_list) == 2

    def test_extend_with_autolist(self, llm_client, embedder):
        """Test extending with another AutoList."""
        list1 = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )
        list2 = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        list1.append(PersonItemSchema(name="John"))
        list2.append(PersonItemSchema(name="Jane"))

        list1.extend(list2)

        assert len(list1) == 2

    def test_insert_at_beginning(self, llm_client, embedder):
        """Test inserting at the beginning of the list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.insert(0, PersonItemSchema(name="Jane"))

        assert auto_list.items[0].name == "Jane"
        assert auto_list.items[1].name == "John"

    def test_insert_at_end(self, llm_client, embedder):
        """Test inserting at the end of the list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.insert(1, PersonItemSchema(name="Jane"))

        assert auto_list.items[1].name == "Jane"

    def test_remove_item(self, llm_client, embedder):
        """Test removing an item."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        item = PersonItemSchema(name="John", age=30)
        auto_list.append(item)
        auto_list.append(PersonItemSchema(name="Jane"))

        auto_list.remove(item)

        assert len(auto_list) == 1
        assert auto_list.items[0].name == "Jane"

    def test_remove_raises_when_not_found(self, llm_client, embedder):
        """Test that remove raises ValueError when item not found."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))

        with pytest.raises(ValueError):
            auto_list.remove(PersonItemSchema(name="NotFound"))

    def test_pop_default(self, llm_client, embedder):
        """Test popping from end by default."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.append(PersonItemSchema(name="Jane"))

        popped = auto_list.pop()

        assert popped.name == "Jane"
        assert len(auto_list) == 1

    def test_pop_first(self, llm_client, embedder):
        """Test popping from beginning."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.append(PersonItemSchema(name="Jane"))

        popped = auto_list.pop(0)

        assert popped.name == "John"
        assert len(auto_list) == 1

    def test_pop_from_empty_raises(self, llm_client, embedder):
        """Test that popping from empty list raises IndexError."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        with pytest.raises(IndexError):
            auto_list.pop()

    def test_clear(self, llm_client, embedder):
        """Test clearing the list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.append(PersonItemSchema(name="Jane"))

        assert len(auto_list) == 2

        auto_list.clear()

        assert len(auto_list) == 0
        assert auto_list.empty() is True

    def test_index_method(self, llm_client, embedder):
        """Test finding index of an item."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.append(PersonItemSchema(name="Jane"))

        idx = auto_list.index(PersonItemSchema(name="Jane"))

        assert idx == 1

    def test_index_raises_when_not_found(self, llm_client, embedder):
        """Test that index raises ValueError when item not found."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))

        with pytest.raises(ValueError):
            auto_list.index(PersonItemSchema(name="NotFound"))

    def test_count_method(self, llm_client, embedder):
        """Test counting occurrences of an item."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.append(PersonItemSchema(name="Jane"))
        auto_list.append(PersonItemSchema(name="John"))

        count = auto_list.count(PersonItemSchema(name="John"))

        assert count == 2

    def test_copy(self, llm_client, embedder):
        """Test copying the list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))

        copied = auto_list.copy()

        assert len(copied) == 1
        assert copied.items[0].name == "John"
        assert copied.items[0] is not auto_list.items[0]

    def test_reverse(self, llm_client, embedder):
        """Test reversing the list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))
        auto_list.append(PersonItemSchema(name="Jane"))
        auto_list.append(PersonItemSchema(name="Bob"))

        auto_list.reverse()

        assert auto_list.items[0].name == "Bob"
        assert auto_list.items[2].name == "John"
