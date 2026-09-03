"""Config loader and template configuration models."""

from pathlib import Path

import yaml
from pydantic import BaseModel

from .schemas.base import VALID_AUTOTYPES, FieldSchema
from .schemas.graph import (
    GraphDisplaySchema,
    GraphGuidelineSchema,
    GraphIdentifiersSchema,
    GraphOptionsSchema,
    GraphOutputSchema,
)
from .schemas.naive import (
    NaiveDisplaySchema,
    NaiveGuidelineSchema,
    NaiveIdentifierSchema,
    NaiveOptionsSchema,
    NaiveOutputSchema,
)


class TemplateCfg(BaseModel):
    """Template configuration loaded from YAML."""

    language: str | list[str] = "en"
    name: str
    type: VALID_AUTOTYPES
    tags: list[str]
    description: str | dict[str, str]
    output: NaiveOutputSchema | GraphOutputSchema
    guideline: NaiveGuidelineSchema | GraphGuidelineSchema
    identifiers: NaiveIdentifierSchema | GraphIdentifiersSchema | None = None
    options: NaiveOptionsSchema | GraphOptionsSchema | None = None
    display: NaiveDisplaySchema | GraphDisplaySchema


def _localize_data(
    value: str | list[str] | dict[str, str | list[str]],
    language: str,
) -> str:
    """Get multilingual text value, supports list format

    Args:
        value: Multilingual value, supports str, list or dict format
        language: Target language code

    Returns:
        str: Converted str
    """
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(value))
    # Fall back to English (then empty) when the requested language is absent,
    # so the return is always a str — a missing key otherwise returns None.
    dict_value = value.get(language, value.get("en"))
    if isinstance(dict_value, str):
        return dict_value
    if isinstance(dict_value, list):
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(dict_value))
    return ""


def _localize_field(field: FieldSchema, language: str) -> FieldSchema:
    """Localize a single field."""
    return FieldSchema(
        name=field.name,
        type=field.type,
        description=_localize_data(field.description, language),
        required=field.required,
        default=field.default,
    )


def _localize_naive_output(
    output: NaiveOutputSchema, language: str
) -> NaiveOutputSchema:
    """Localize NaiveOutputSchema."""
    fields = [_localize_field(f, language) for f in output.fields]
    return NaiveOutputSchema(
        description=_localize_data(output.description, language),
        fields=fields,
    )


def _localize_output(
    output: NaiveOutputSchema | GraphOutputSchema,
    language: str,
    autotype: VALID_AUTOTYPES,
) -> NaiveOutputSchema | GraphOutputSchema:
    """Localize output configuration."""
    if autotype in ("model", "list", "set"):
        return _localize_naive_output(output, language)
    return GraphOutputSchema(
        description=_localize_data(output.description, language),
        entities=_localize_naive_output(output.entities, language),
        relations=_localize_naive_output(output.relations, language),
    )


def _localize_guideline(
    guideline: NaiveGuidelineSchema | GraphGuidelineSchema,
    language: str,
    autotype: VALID_AUTOTYPES,
) -> NaiveGuidelineSchema | GraphGuidelineSchema:
    """Localize guideline configuration."""
    if autotype in ("model", "list", "set"):
        return NaiveGuidelineSchema(
            target=_localize_data(guideline.target, language),
            rules=_localize_data(guideline.rules, language),
        )
    return GraphGuidelineSchema(
        target=_localize_data(guideline.target, language),
        rules_for_entities=_localize_data(guideline.rules_for_entities, language),
        rules_for_relations=_localize_data(guideline.rules_for_relations, language),
        rules_for_time=_localize_data(guideline.rules_for_time, language)
        if guideline.rules_for_time
        else None,
        rules_for_location=_localize_data(guideline.rules_for_location, language)
        if guideline.rules_for_location
        else None,
    )


def localize_template(config: TemplateCfg, language: str) -> TemplateCfg:
    """Convert multilingual template config to single-language config.

    Args:
        config: Original multilingual config
        language: Target language code (e.g., 'zh', 'en')

    Returns:
        TemplateCfg: Single-language config with all multilingual fields converted to strings

    Examples:
        >>> config = ConfigLoader.load_config("template.yaml")
        >>> config_zh = localize_template(config, "zh")
        >>> print(config_zh.description)  # str
    """

    return TemplateCfg(
        language=language,
        name=config.name,
        type=config.type,
        tags=config.tags,
        description=_localize_data(config.description, language),
        output=_localize_output(config.output, language, config.type),
        guideline=_localize_guideline(config.guideline, language, config.type),
        identifiers=config.identifiers,
        options=config.options,
        display=config.display,
    )


def load_template(file_path: str | Path) -> TemplateCfg:
    """Load and validate template configuration."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        template = TemplateCfg(**yaml.safe_load(f))

    # Validate and localize the template for each language
    existing_languages = (
        template.language
        if isinstance(template.language, list)
        else [template.language]
    )
    for lang in existing_languages:
        try:
            localize_template(template, lang)
        except Exception as e:
            raise ValueError(
                f"The template configuration is not valid for language {lang}: {e}"
            )

    return template


__all__ = [
    "TemplateCfg",
    "load_template",
    "localize_template",
]
