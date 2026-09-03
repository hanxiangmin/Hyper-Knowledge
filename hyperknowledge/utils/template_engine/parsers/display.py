"""Display parser - generates label extraction functions from YAML config."""

from collections.abc import Callable
from typing import Any

from .identifiers import _extractor
from .schemas import (
    VALID_AUTOTYPES,
    GraphDisplaySchema,
    NaiveDisplaySchema,
)


def parse_display(
    display: NaiveDisplaySchema | GraphDisplaySchema,
    autotype: VALID_AUTOTYPES,
) -> Callable[[Any], str] | tuple[Callable[[Any], str], Callable[[Any], str]]:
    """Parse display config and return label extractors.

    Args:
        display: display config from YAML
        autotype: auto type

    Returns:
        - For model/list/set: label_extractor
        - For graph types: (entity_label_extractor, relation_label_extractor)
    """
    if autotype in ("model", "list", "set"):
        return _extractor(display.label)

    entity_extractor = _extractor(display.entity_label)
    relation_extractor = _extractor(display.relation_label)
    return (entity_extractor, relation_extractor)


__all__ = [
    "parse_display",
]
