"""Unit tests for AutoSet key operations."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from hyperknowledge.types import AutoSet


class ProductItemSchema(BaseModel):
    """Schema for product items."""

    sku: str
    name: str
    price: Optional[float] = None


class TestAutoSetOperators:
    """Test cases for AutoSet operator overloads."""

    def test_len(self, llm_client, embedder):
        """Test len() function."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        assert len(auto_set) == 0

        auto_set.add(ProductItemSchema(sku="P001", name="Product 1"))
        auto_set.add(ProductItemSchema(sku="P002", name="Product 2"))

        assert len(auto_set) == 2

    def test_contains_with_key(self, llm_client, embedder):
        """Test __contains__ with key value."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        auto_set.add(ProductItemSchema(sku="P001", name="Product 1"))

        assert "P001" in auto_set
        assert "P002" not in auto_set

    def test_iter(self, llm_client, embedder):
        """Test __iter__."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        auto_set.add(ProductItemSchema(sku="P001", name="Product 1"))
        auto_set.add(ProductItemSchema(sku="P002", name="Product 2"))

        items = list(auto_set)

        assert len(items) == 2
        assert all(isinstance(item, ProductItemSchema) for item in items)

    def test_union_operator(self, llm_client, embedder):
        """Test that | (union) operator is supported for AutoSet."""
        auto_set1 = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )
        auto_set2 = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        auto_set1.add(ProductItemSchema(sku="P001", name="Product 1"))
        auto_set2.add(ProductItemSchema(sku="P002", name="Product 2"))

        result = auto_set1 | auto_set2

        assert len(result) == 2
        assert "P001" in result
        assert "P002" in result


class TestAutoSetKeyOperations:
    """Test cases for AutoSet key-based operations."""

    def test_key_extractor(self, llm_client, embedder):
        """Test that key extractor is used correctly."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        auto_set.add(ProductItemSchema(sku="ABC123", name="Test Product"))

        assert "ABC123" in auto_set
        assert auto_set.get("ABC123").name == "Test Product"

    def test_composite_key_extractor(self, llm_client, embedder):
        """Test composite key extractor."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: f"{x.sku}_{x.name}",
        )

        auto_set.add(ProductItemSchema(sku="P001", name="Product 1"))

        assert "P001_Product 1" in auto_set

    def test_batch_add_via_memory(self, llm_client, embedder):
        """Test batch adding via internal memory."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        items = [
            ProductItemSchema(sku="P001", name="Product 1"),
            ProductItemSchema(sku="P002", name="Product 2"),
        ]

        auto_set._data_memory.add(items)

        assert len(auto_set) == 2
        assert "P001" in auto_set
        assert "P002" in auto_set


class TestAutoSetStateManagement:
    """Test cases for AutoSet state management."""

    def test_clear(self, llm_client, embedder):
        """Test clearing the set."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        auto_set.add(ProductItemSchema(sku="P001", name="Product 1"))
        auto_set.add(ProductItemSchema(sku="P002", name="Product 2"))

        assert len(auto_set) == 2

        auto_set.clear()

        assert len(auto_set) == 0
        assert auto_set.empty() is True

    def test_empty_after_clear(self, llm_client, embedder):
        """Test empty() after clear()."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        auto_set.add(ProductItemSchema(sku="P001", name="Product 1"))
        auto_set.clear()

        assert auto_set.empty() is True

    def test_metadata_initialized(self, llm_client, embedder):
        """Test that metadata is initialized correctly."""
        auto_set = AutoSet(
            item_schema=ProductItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.sku,
        )

        assert "created_at" in auto_set.metadata
        assert "updated_at" in auto_set.metadata
