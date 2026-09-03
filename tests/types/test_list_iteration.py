"""Unit tests for AutoList iteration and membership."""

from datetime import datetime, timedelta

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoList
from tests.fixtures import PersonSchema


class PersonItemSchema(BaseModel):
    """Schema for person list items."""

    name: str
    age: Optional[int] = None


class TestAutoListIteration:
    """Test cases for AutoList iteration and membership."""

    def test_iteration(self, llm_client, embedder):
        """Test that AutoList is iterable."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        names = []
        for item in auto_list:
            names.append(item.name)

        assert names == ["John", "Jane"]

    def test_iteration_with_list_comprehension(self, llm_client, embedder):
        """Test iteration with list comprehension."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        names = [item.name for item in auto_list]

        assert names == ["John", "Jane"]

    def test_list_function(self, llm_client, embedder):
        """Test converting to Python list."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        items_list = list(auto_list)

        assert len(items_list) == 2
        assert isinstance(items_list, list)

    def test_contains_true(self, llm_client, embedder):
        """Test that contains returns True for existing item."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        item = PersonItemSchema(name="John", age=30)
        auto_list.append(item)

        assert item in auto_list

    def test_contains_false(self, llm_client, embedder):
        """Test that contains returns False for non-existing item."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))

        assert PersonItemSchema(name="NotFound") not in auto_list

    def test_contains_with_same_values(self, llm_client, embedder):
        """Test contains with items that have same values."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        item1 = PersonItemSchema(name="John", age=30)
        auto_list.append(item1)

        item2 = PersonItemSchema(name="John", age=30)
        assert item2 in auto_list

    def test_not_in_operator(self, llm_client, embedder):
        """Test not in operator."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))

        assert PersonItemSchema(name="NotFound") not in auto_list


class TestAutoListOperators:
    """Test cases for AutoList operators."""

    def test_add_two_lists(self, llm_client, embedder):
        """Test adding two AutoList instances."""
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

        result = list1 + list2

        assert len(result) == 2
        assert result.items[0].name == "John"
        assert result.items[1].name == "Jane"

    def test_add_preserves_original(self, llm_client, embedder):
        """Test that add preserves original lists."""
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

        result = list1 + list2

        assert len(list1) == 1
        assert len(list2) == 1
        assert len(result) == 2

    def test_add_chaining(self, llm_client, embedder):
        """Test chaining multiple add operations."""
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
        list3 = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        list1.append(PersonItemSchema(name="John"))
        list2.append(PersonItemSchema(name="Jane"))
        list3.append(PersonItemSchema(name="Bob"))

        result = list1 + list2 + list3

        assert len(result) == 3

    def test_add_merges_metadata(self, llm_client, embedder):
        """List + List keeps the earliest created_at and a fresh updated_at."""
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

        # list2 is the older list; both carry a stale updated_at. The left
        # operand (list1) is the newer one, so a fix that merely copies self's
        # timestamps would pick the wrong created_at and a stale updated_at.
        older = datetime.now() - timedelta(days=2)
        newer = datetime.now() - timedelta(days=1)
        list1.metadata["created_at"] = newer
        list2.metadata["created_at"] = older
        list1.metadata["updated_at"] = older
        list2.metadata["updated_at"] = older

        before = datetime.now()
        result = list1 + list2

        assert result.metadata["created_at"] == older
        assert result.metadata["updated_at"] >= before

    def test_add_with_different_schema_raises(self, llm_client, embedder):
        """Test that adding lists with different schemas raises TypeError."""
        from hyperknowledge.types import AutoModel

        list1 = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        list2 = AutoList(
            item_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        list1.append(PersonItemSchema(name="John"))
        list2.append(PersonSchema(name="Jane", age=30))

        with pytest.raises(TypeError):
            list1 + list2

    def test_add_with_automodel(self, llm_client, embedder):
        """Test adding AutoList with AutoModel."""
        from hyperknowledge.types import AutoModel

        list1 = AutoList(
            item_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        list1.append(PersonSchema(name="John", age=30))

        model = AutoModel(
            data_schema=PersonSchema,
            llm_client=llm_client,
            embedder=embedder,
        )
        model.feed_text("Jane is 25 years old.")

        result = list1 + model

        assert len(result) == 2

    def test_setitem(self, llm_client, embedder):
        """Test setting item by index."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        auto_list[0] = PersonItemSchema(name="Bob", age=35)

        assert auto_list.items[0].name == "Bob"

    def test_delitem(self, llm_client, embedder):
        """Test deleting item by index."""
        auto_list = AutoList(
            item_schema=PersonItemSchema,
            llm_client=llm_client,
            embedder=embedder,
        )

        auto_list.append(PersonItemSchema(name="John", age=30))
        auto_list.append(PersonItemSchema(name="Jane", age=25))

        del auto_list[0]

        assert len(auto_list) == 1
        assert auto_list.items[0].name == "Jane"
