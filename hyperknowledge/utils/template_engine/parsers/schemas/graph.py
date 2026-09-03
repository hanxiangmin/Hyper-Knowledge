from pydantic import BaseModel

from .base import VALID_MERGE_STRATEGIES
from .naive import NaiveOutputSchema


class GraphGuidelineSchema(BaseModel):
    target: str | list[str] | dict[str, str]
    rules_for_entities: str | list[str] | dict[str, str | list[str]]
    rules_for_relations: str | list[str] | dict[str, str | list[str]]
    # Only for AutoTemporalGraph, AutoSpatioTemporalGraph
    rules_for_time: str | list[str] | dict[str, str | list[str]] | None = None
    # Only for AutoSpatialGraph, AutoSpatioTemporalGraph
    rules_for_location: str | list[str] | dict[str, str | list[str]] | None = None


class GraphOutputSchema(BaseModel):
    description: str | dict[str, str]
    entities: NaiveOutputSchema
    relations: NaiveOutputSchema


class GraphOptionsSchema(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    max_workers: int | None = None
    verbose: bool | None = None
    entity_merge_strategy: VALID_MERGE_STRATEGIES | None = None
    relation_merge_strategy: VALID_MERGE_STRATEGIES | None = None
    extraction_mode: str | None = None
    entity_fields_for_search: list[str] | None = None
    relation_fields_for_search: list[str] | None = None
    # Only for AutoTemporalGraph, AutoSpatioTemporalGraph
    observation_time: str | None = None
    # Only for AutoSpatialGraph, AutoSpatioTemporalGraph
    observation_location: str | None = None


class GraphDisplaySchema(BaseModel):
    entity_label: str
    relation_label: str


class GraphIdentifiersSchema(BaseModel):
    entity_id: str = None
    relation_id: str = None
    relation_members: str | dict[str, str] | list[str] = None
    # Only for AutoTemporalGraph, AutoSpatioTemporalGraph
    time_field: str | None = None
    # Only for AutoSpatialGraph, AutoSpatioTemporalGraph
    location_field: str | None = None
