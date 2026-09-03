from typing import Any, Literal

from pydantic import BaseModel

VALID_MERGE_STRATEGIES = Literal[
    "merge_field",
    "keep_incoming",
    "keep_existing",
    "llm_balanced",
    "llm_prefer_incoming",
    "llm_prefer_existing",
]
VALID_AUTOTYPES = Literal[
    "model",
    "list",
    "set",
    "graph",
    "hypergraph",
    "temporal_graph",
    "spatial_graph",
    "spatio_temporal_graph",
]

VALID_FIELD_TYPES = Literal["str", "int", "float", "bool", "list"]


class FieldSchema(BaseModel):
    name: str
    type: VALID_FIELD_TYPES
    description: str | dict[str, str]
    required: bool | None = None
    default: Any | None = None
