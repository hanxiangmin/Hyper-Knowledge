"""Identifier parser - generates extraction functions from YAML config."""

import re
from collections.abc import Callable
from typing import Any

from .schemas import (
    VALID_AUTOTYPES,
    GraphIdentifiersSchema,
    NaiveIdentifierSchema,
)


def _extractor(field_or_template: str) -> Callable[[Any], str]:
    """Field or template extractor.

    - Simple field: 'name' -> lambda x: x.name
    - Bracket template: '{source}|{type}' -> lambda x: f"{x.source}|{x.type}"

    Raises:
        AttributeError: if field does not exist on item
    """
    if "{" in field_or_template:
        fields = re.findall(r"\{(\w+)\}", field_or_template)

        def extractor(item: Any) -> str:
            missing = [f for f in fields if not hasattr(item, f)]
            if missing:
                raise AttributeError(f"Missing fields: {missing}")
            values = {}
            for field in fields:
                value = getattr(item, field, None)
                if isinstance(value, (list, tuple, set)):
                    value = sorted(
                        str(member) for member in value if member is not None
                    )
                values[field] = "" if value is None else value
            return field_or_template.format(**values)

        return extractor

    def extractor(item: Any) -> str:
        if not hasattr(item, field_or_template):
            raise AttributeError(f"Missing field: {field_or_template}")
        value = getattr(item, field_or_template)
        return str(value)

    return extractor


def _members_extractor(
    members: dict[str, str] | str | list[str],
) -> Callable[[Any], tuple[str, ...]]:
    """Relation members extractor:
    Graph:    {source: 's', target: 't'} -> lambda x: (x.s, x.t)
    Hypergraph: 'members' -> lambda x: tuple(sorted(x.members)) or
                'members' -> lambda x: tuple(sorted(x.m) for m in x.members)
    """

    def values(item: Any, field: str) -> list[str]:
        value = getattr(item, field, None)
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if not isinstance(value, (list, tuple, set)):
            raise ValueError(
                "Member fields must contain a node id or a list of node ids"
            )
        return [str(node) for node in value if node is not None and str(node).strip()]

    # A source/target-only map remains the undirected pairwise convention.
    # Other maps are role-aware hyperedges; do not drop their additional roles.
    if isinstance(members, dict):
        if set(members) == {"source", "target"}:

            def extractor(item: Any) -> tuple[str, str]:
                return tuple(
                    sorted(
                        (
                            str(getattr(item, members["source"])),
                            str(getattr(item, members["target"])),
                        )
                    )
                )

            return extractor

        def extractor(item: Any) -> tuple[str, ...]:
            return tuple(
                sorted(
                    [node for field in members.values() for node in values(item, field)]
                )
            )

        return extractor

    # Handle Hypergraph
    if isinstance(members, str):

        def extractor(item: Any) -> tuple[str, ...]:
            return tuple(sorted(values(item, members)))

        return extractor

    def extractor(item: Any) -> tuple[str, ...]:
        result: list[str] = []
        for field_name in members:
            result.extend(values(item, field_name))
        return tuple(sorted(result))

    return extractor


def parse_identifiers(
    identifiers: NaiveIdentifierSchema | GraphIdentifiersSchema,
    autotype: VALID_AUTOTYPES,
) -> (
    Callable[[Any], str]
    | tuple[
        Callable[[Any], str], Callable[[Any], str], Callable[[Any], tuple[str, ...]]
    ]
):
    """Parse identifiers config and return extractors based on autotype.

    Args:
        identifiers: identifiers config from YAML
        autotype: auto type (model, list, set, graph, hypergraph, ...)

    Returns:
        - For set: item_id_extractor
        - For graph types: (entity_key_extractor, relation_key_extractor, entities_in_relation_extractor)
    """

    if autotype == "set":
        return _extractor(identifiers.item_id)

    if autotype in (
        "graph",
        "hypergraph",
        "temporal_graph",
        "spatial_graph",
        "spatio_temporal_graph",
    ):
        entity_extractor = _extractor(identifiers.entity_id)
        relation_extractor = _extractor(identifiers.relation_id)
        members_extractor = _members_extractor(identifiers.relation_members)
        rets = [entity_extractor, relation_extractor, members_extractor]

        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            time_extractor = _extractor(identifiers.time_field)
            rets.append(time_extractor)

        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            location_extractor = _extractor(identifiers.location_field)
            rets.append(location_extractor)

        return tuple(rets)

    return None


__all__ = [
    "parse_identifiers",
]
