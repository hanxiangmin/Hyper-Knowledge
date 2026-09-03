"""Options models and parser."""

from ontomem.merger import MergeStrategy
from pydantic import BaseModel

from .schemas import (
    VALID_AUTOTYPES,
    VALID_MERGE_STRATEGIES,
    GraphOptionsSchema,
    NaiveOptionsSchema,
)


def resolve_merge_strategy(strategy_name: VALID_MERGE_STRATEGIES) -> MergeStrategy:
    """Resolve merge strategy from string to MergeStrategy enum."""
    if strategy_name.startswith("llm_"):
        # Map every "llm_*" variant onto the nested MergeStrategy.LLM member,
        # e.g. "llm_balanced" -> MergeStrategy.LLM.BALANCED,
        #      "llm_prefer_incoming" -> MergeStrategy.LLM.PREFER_INCOMING.
        return getattr(MergeStrategy.LLM, strategy_name[len("llm_") :].upper())
    return MergeStrategy[strategy_name.upper()]


class Options(BaseModel):
    """Unified Options - covers all possible configuration for all autotypes."""

    chunk_size: int | None = None
    chunk_overlap: int | None = None
    max_workers: int | None = None
    verbose: bool | None = None

    strategy_or_merger: str | None = None
    fields_for_index: list[str] | None = None

    extraction_mode: str | None = None
    node_strategy_or_merger: str | None = None
    edge_strategy_or_merger: str | None = None
    node_fields_for_index: list[str] | None = None
    edge_fields_for_index: list[str] | None = None

    observation_time: str | None = None
    observation_location: str | None = None


COMMON_PARAMS = ("chunk_size", "chunk_overlap", "max_workers", "verbose")

MODEL_PARAMS = ("strategy_or_merger",)
LIST_PARAMS = ("fields_for_index",)
SET_PARAMS = ("strategy_or_merger", "fields_for_index")

GRAPH_PARAMS = (
    "extraction_mode",
    "node_strategy_or_merger",
    "edge_strategy_or_merger",
    "node_fields_for_index",
    "edge_fields_for_index",
)

YAML_TO_AUTOTYPE_MAPPING = {
    "merge_strategy": "strategy_or_merger",
    "entity_merge_strategy": "node_strategy_or_merger",
    "relation_merge_strategy": "edge_strategy_or_merger",
    "entity_fields_for_search": "node_fields_for_index",
    "relation_fields_for_search": "edge_fields_for_index",
}


def parse_option(
    options: NaiveOptionsSchema | GraphOptionsSchema | None,
    autotype: VALID_AUTOTYPES,
    override: dict | None = None,
) -> dict:
    """Parse options and return kwargs for specific autotype.

    Args:
        options: Unified Options configuration (can be None if not defined in template)
        autotype: auto type (model, list, set, graph, hypergraph, temporal_graph, spatial_graph, spatio_temporal_graph)
        override: Optional override for specific parameters

    Returns:
        dict: Only contains parameters needed for the corresponding autotype
    """
    if options is None:
        return {}

    options_dict = options.model_dump()
    options_dict = {
        YAML_TO_AUTOTYPE_MAPPING.get(k, k): v for k, v in options_dict.items()
    }
    if override:
        options_dict.update(override)
    options = Options(**options_dict)

    if autotype in ("model",):
        return _build_kwargs(options, MODEL_PARAMS, COMMON_PARAMS)

    if autotype in ("list",):
        return _build_kwargs(options, LIST_PARAMS, COMMON_PARAMS)

    if autotype in ("set",):
        return _build_kwargs(options, SET_PARAMS, COMMON_PARAMS)

    if autotype in ("graph", "hypergraph"):
        return _build_kwargs(options, GRAPH_PARAMS, COMMON_PARAMS)

    if autotype in ("temporal_graph",):
        return _build_kwargs(
            options, ("observation_time",) + GRAPH_PARAMS, COMMON_PARAMS
        )

    if autotype in ("spatial_graph",):
        return _build_kwargs(
            options, ("observation_location",) + GRAPH_PARAMS, COMMON_PARAMS
        )

    if autotype in ("spatio_temporal_graph",):
        return _build_kwargs(
            options,
            ("observation_time", "observation_location") + GRAPH_PARAMS,
            COMMON_PARAMS,
        )


def _build_kwargs(
    options: Options, specific_params: tuple, common_params: tuple
) -> dict:
    """Build kwargs, only returning non-None parameters."""
    kwargs = {}
    all_params = specific_params + common_params

    for param in all_params:
        value = getattr(options, param, None)
        if value is not None:
            if "strategy_or_merger" in param:
                value = resolve_merge_strategy(value)
            kwargs[param] = value

    return kwargs


__all__ = [
    "parse_option",
]
