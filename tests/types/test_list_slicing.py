"""Unit tests for AutoList slicing and indexing."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoList


class PersonItemSchema(BaseModel):
    """Schema for person list items."""

    name: str
    age: Optional[int] = None


class TestAutoListIndexing:
    """Test cases for AutoList indexing."""

    def test_getitem_positive_index(self, llm_client, embedder):
        """Test getting item by positive index."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))
        auto_list.append(PersonItemSchema(name="Bob", age=35))

        item = auto_list[0]

        assert item.name == "John"

    def test_getitem_negative_index(self, llm_client, embedder):
        """Test getting item by negative index."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))
        auto_list.append(PersonItemSchema(name="Bob", age=35))

        item = auto_list[-1]

        assert item.name == "Bob"

    def test_getitem_out_of_range_raises(self, llm_client, embedder):
        """Test that getting item out of range raises IndexError."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John"))

        with pytest.raises(IndexError):
            _ = auto_list[10]

    def test_getitem_empty_list_raises(self, llm_client, embedder):
        """Test that getting item from empty list raises IndexError."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        with pytest.raises(IndexError):
            _ = auto_list[0]


class TestAutoListSlicing:
    """Test cases for AutoList slicing."""

    def test_slice_basic(self, llm_client, embedder):
        """Test basic slicing."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))
        auto_list.append(PersonItemSchema(name="Bob", age=35))

        sliced = auto_list[0:2]

        assert isinstance(sliced, AutoList)
        assert len(sliced) == 2
        assert sliced.items[0].name == "John"
        assert sliced.items[1].name == "Jane"

    def test_slice_returns_new_instance(self, llm_client, embedder):
        """Test that slicing returns a new instance."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        sliced = auto_list[0:1]

        assert sliced is not auto_list

    def test_slice_does_not_modify_original(self, llm_client, embedder):
        """Test that slicing does not modify the original list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        sliced = auto_list[0:1]

        assert len(auto_list) == 2

    def test_slice_first_n(self, llm_client, embedder):
        """Test slicing first n items."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        for i in range(5):
            auto_list.append(PersonItemSchema(name=f"Person{i}", age=20 + i))

        sliced = auto_list[:3]

        assert len(sliced) == 3
        assert sliced.items[0].name == "Person0"
        assert sliced.items[2].name == "Person2"

    def test_slice_last_n(self, llm_client, embedder):
        """Test slicing last n items."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        for i in range(5):
            auto_list.append(PersonItemSchema(name=f"Person{i}", age=20 + i))

        sliced = auto_list[-2:]

        assert len(sliced) == 2
        assert sliced.items[0].name == "Person3"
        assert sliced.items[1].name == "Person4"

    def test_slice_with_step(self, llm_client, embedder):
        """Test slicing with step."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        for i in range(6):
            auto_list.append(PersonItemSchema(name=f"Person{i}", age=20 + i))

        sliced = auto_list[::2]

        assert len(sliced) == 3
        assert sliced.items[0].name == "Person0"
        assert sliced.items[1].name == "Person2"
        assert sliced.items[2].name == "Person4"

    def test_slice_with_negative_step(self, llm_client, embedder):
        """Test slicing with negative step (reverses list)."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))
        auto_list.append(PersonItemSchema(name="Bob", age=35))

        sliced = auto_list[::-1]

        assert sliced.items[0].name == "Bob"
        assert sliced.items[2].name == "John"

    def test_slice_empty_result(self, llm_client, embedder):
        """Test slicing that results in empty list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))

        sliced = auto_list[5:10]

        assert isinstance(sliced, AutoList)
        assert len(sliced) == 0

    def test_slice_preserves_schema(self, llm_client, embedder):
        """Test that sliced list preserves item schema."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))

        sliced = auto_list[:]

        assert sliced.item_schema == auto_list.item_schema

    def test_sliced_list_is_independent(self, llm_client, embedder):
        """Test that sliced list is independent of original."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))

        sliced = auto_list[:]

        sliced.append(PersonItemSchema(name="Jane", age=25))

        assert len(auto_list) == 1
        assert len(sliced) == 2


class TestAutoListRepr:
    """Test cases for AutoList string representation."""

    def test_repr(self, llm_client, embedder):
        """Test __repr__ method."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        repr_str = repr(auto_list)

        assert "AutoList" in repr_str
        assert "PersonItemSchema" in repr_str
        assert "2" in repr_str

    def test_str(self, llm_client, embedder):
        """Test __str__ method."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))

        str_repr = str(auto_list)

        assert "AutoList" in str_repr
        assert "1" in str_repr
