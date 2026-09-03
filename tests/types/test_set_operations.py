"""Unit tests for AutoSet set operations."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional
from ontomem.merger import MergeStrategy

from hyperknowledge.types import AutoSet


class KeywordItemSchema(BaseModel):
    """Schema for keyword items."""

    term: str
    category: Optional[str] = None


class TestAutoSetOperations:
    """Test cases for AutoSet set operations (union, intersection, difference)."""

    def _create_set_with_terms(self, llm_client, embedder, terms):
        """Helper to create a set with given terms."""
        auto_set = AutoSet(
            item_schema=KeywordItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.term,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )
        for term in terms:
            auto_set.add(KeywordItemSchema(term=term))
        return auto_set

    def test_union_operator(self, llm_client, embedder):
        """Test union operator |."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        result = set1 | set2

        assert len(result) == 3
        assert "Python" in result
        assert "Java" in result
        assert "React" in result

    def test_union_named_method(self, llm_client, embedder):
        """Test union named method."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        result = set1.union(set2)

        assert len(result) == 3

    def test_union_preserves_original(self, llm_client, embedder):
        """Test that union preserves original sets."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java"])

        _ = set1 | set2

        assert len(set1) == 1
        assert len(set2) == 1

    def test_intersection_operator(self, llm_client, embedder):
        """Test intersection operator &."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java", "React"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React", "Vue"])

        result = set1 & set2

        assert len(result) == 2
        assert "Java" in result
        assert "React" in result

    def test_intersection_named_method(self, llm_client, embedder):
        """Test intersection named method."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        result = set1.intersection(set2)

        assert len(result) == 1
        assert "Java" in result

    def test_intersection_no_common(self, llm_client, embedder):
        """Test intersection with no common elements."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java"])

        result = set1 & set2

        assert len(result) == 0

    def test_difference_operator(self, llm_client, embedder):
        """Test difference operator -."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java", "React"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        result = set1 - set2

        assert len(result) == 1
        assert "Python" in result
        assert "Java" not in result

    def test_difference_named_method(self, llm_client, embedder):
        """Test difference named method."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java"])

        result = set1.difference(set2)

        assert len(result) == 1
        assert "Python" in result

    def test_symmetric_difference_operator(self, llm_client, embedder):
        """Test symmetric difference operator ^."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        result = set1 ^ set2

        assert len(result) == 2
        assert "Python" in result
        assert "React" in result
        assert "Java" not in result

    def test_symmetric_difference_named_method(self, llm_client, embedder):
        """Test symmetric difference named method."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        result = set1.symmetric_difference(set2)

        assert len(result) == 2

    def test_symmetric_difference_with_no_overlap(self, llm_client, embedder):
        """Test symmetric difference with no overlapping elements."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java"])

        result = set1 ^ set2

        assert len(result) == 2
        assert "Python" in result
        assert "Java" in result


class TestAutoSetComparison:
    """Test cases for AutoSet comparison operators."""

    def _create_set_with_terms(self, llm_client, embedder, terms):
        """Helper to create a set with given terms."""
        auto_set = AutoSet(
            item_schema=KeywordItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.term,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )
        for term in terms:
            auto_set.add(KeywordItemSchema(term=term))
        return auto_set

    def test_equality_same_keys(self, llm_client, embedder):
        """Test equality with same keys."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1 == set2

    def test_equality_different_keys(self, llm_client, embedder):
        """Test equality with different keys."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java"])

        assert set1 != set2

    def test_equality_different_lengths(self, llm_client, embedder):
        """Test equality with different lengths."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python"])

        assert set1 != set2

    def test_subset_operator(self, llm_client, embedder):
        """Test subset operator <=."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1 <= set2

    def test_subset_not_equal(self, llm_client, embedder):
        """Test subset with equal sets."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1 <= set2

    def test_subset_not_reflexive_superset(self, llm_client, embedder):
        """Test that subset is not true when superset is smaller."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java", "React"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert not (set1 <= set2)

    def test_proper_subset_operator(self, llm_client, embedder):
        """Test proper subset operator <."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1 < set2

    def test_proper_subset_equal_sets(self, llm_client, embedder):
        """Test that proper subset is false for equal sets."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert not (set1 < set2)

    def test_superset_operator(self, llm_client, embedder):
        """Test superset operator >=."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java", "React"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1 >= set2

    def test_proper_superset_operator(self, llm_client, embedder):
        """Test proper superset operator >."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java", "React"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1 > set2

    def test_proper_superset_equal_sets(self, llm_client, embedder):
        """Test that proper superset is false for equal sets."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert not (set1 > set2)

    def test_issubset_method(self, llm_client, embedder):
        """Test issubset method."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1.issubset(set2)

    def test_issuperset_method(self, llm_client, embedder):
        """Test issuperset method."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java", "React"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])

        assert set1.issuperset(set2)

    def test_isdisjoint_true(self, llm_client, embedder):
        """Test isdisjoint when sets have no common elements."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java"])

        assert set1.isdisjoint(set2)

    def test_isdisjoint_false(self, llm_client, embedder):
        """Test isdisjoint when sets have common elements."""
        set1 = self._create_set_with_terms(llm_client, embedder, ["Python", "Java"])
        set2 = self._create_set_with_terms(llm_client, embedder, ["Java", "React"])

        assert not set1.isdisjoint(set2)


class TestAutoSetRepr:
    """Test cases for AutoSet string representation."""

    def test_repr(self, llm_client, embedder):
        """Test __repr__ method."""
        auto_set = AutoSet(
            item_schema=KeywordItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.term,
        )

        auto_set.add(KeywordItemSchema(term="Python"))
        auto_set.add(KeywordItemSchema(term="Java"))

        repr_str = repr(auto_set)

        assert "AutoSet" in repr_str
        assert "KeywordItemSchema" in repr_str
        assert "2" in repr_str

    def test_str(self, llm_client, embedder):
        """Test __str__ method."""
        auto_set = AutoSet(
            item_schema=KeywordItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.term,
        )

        auto_set.add(KeywordItemSchema(term="Python"))

        str_repr = str(auto_set)

        assert "AutoSet" in str_repr
        assert "1" in str_repr
