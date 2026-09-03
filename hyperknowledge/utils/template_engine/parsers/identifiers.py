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
            values = [getattr(item, f, None) for f in fields]
            return field_or_template.format(**dict(zip(fields, values)))

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
    # Handle Graph
    if isinstance(members, dict):
        source_field = members.get("source")
        target_field = members.get("target")
        if not source_field or not target_field:
            raise ValueError("relation_members must map source/target for a graph")

        def extractor(item: Any) -> tuple[str, str]:
            return tuple(
                sorted(
                    (
                        str(getattr(item, source_field)),
                        str(getattr(item, target_field)),
                    )
                )
            )

        return extractor

    # Handle Hypergraph
    if isinstance(members, str):

        def extractor(item: Any) -> tuple[str, ...]:
            value = getattr(item, members)
            if value is None:
                return ()
            if isinstance(value, str):
                return (value,)
            return tuple(sorted(str(member) for member in value if member is not None))

        return extractor

    def extractor(item: Any) -> tuple[str, ...]:
        result: list[str] = []
        for field_name in members:
            value = getattr(item, field_name)
            if value is None:
                continue
            if isinstance(value, str):
                result.append(value)
            else:
                result.extend(str(member) for member in value if member is not None)
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
