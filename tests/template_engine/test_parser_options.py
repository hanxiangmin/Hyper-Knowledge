"""Unit tests for template parsers - options (merge strategy resolution)."""

from typing import get_args

import pytest

from hyperknowledge.utils.template_engine.parsers.options import resolve_merge_strategy
from hyperknowledge.utils.template_engine.parsers.schemas.base import (
    VALID_MERGE_STRATEGIES,
)


class TestResolveMergeStrategy:
    """``resolve_merge_strategy`` must resolve every documented strategy."""

    @pytest.mark.parametrize("strategy", get_args(VALID_MERGE_STRATEGIES))
    def test_every_valid_strategy_resolves(self, strategy):
        """No value declared in ``VALID_MERGE_STRATEGIES`` may resolve to None.

        Regression test: multi-word ``llm_*`` strategies such as
        ``llm_prefer_incoming`` / ``llm_prefer_existing`` used to fall through the
        resolver and silently return ``None`` (their name splits into 3 parts,
        which failed the ``len(parts) == 2`` guard).
        """
        assert resolve_merge_strategy(strategy) is not None

    @pytest.mark.parametrize("strategy", ["llm_prefer_incoming", "llm_prefer_existing"])
    def test_multiword_llm_strategies_map_to_llm_member(self, strategy):
        """Multi-word ``llm_*`` strategies map onto the nested ``MergeStrategy.LLM``."""
        from ontomem.merger import MergeStrategy

        expected = getattr(MergeStrategy.LLM, strategy[len("llm_") :].upper())
        assert resolve_merge_strategy(strategy) == expected
