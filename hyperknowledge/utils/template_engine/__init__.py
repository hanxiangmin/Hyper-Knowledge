"""Template Engine - Dynamically creates knowledge extraction templates from YAML configuration.

Main Components:
- Template: Unified API for template operations
- Gallery: Template library management
- TemplateFactory: Creates template instances from configuration
- TemplateCfg: Template config (supports multilingual)
- ConfigLoader: Loads YAML configuration
- localize_template: Converts multilingual config to single-language config
- SchemaParser: Parses output schemas based on template type
- GuidelineParser: Parses prompts based on template type
- parse_identifiers: Parses identifier extractors from config
"""

from .factory import TemplateFactory
from .gallery import Gallery
from .parsers import (
    TemplateCfg,
    load_template,
    localize_template,
)
from .template import Template

__all__ = [
    "Gallery",
    "Template",
    "TemplateCfg",
    "TemplateFactory",
    "load_template",
    "localize_template",
]
