from pydantic import BaseModel

from .base import VALID_MERGE_STRATEGIES, FieldSchema


class NaiveGuidelineSchema(BaseModel):
    target: str | list[str] | dict[str, str]
    rules: str | list[str] | dict[str, str | list[str]]


class NaiveOutputSchema(BaseModel):
    description: str | dict[str, str]
    fields: list[FieldSchema]


class NaiveOptionsSchema(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    max_workers: int | None = None
    verbose: bool | None = None
    merge_strategy: VALID_MERGE_STRATEGIES | None = None
    fields_for_search: list[str] | None = None


class NaiveDisplaySchema(BaseModel):
    label: str


class NaiveIdentifierSchema(BaseModel):
    item_id: str
