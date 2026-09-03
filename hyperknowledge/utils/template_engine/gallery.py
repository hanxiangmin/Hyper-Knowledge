"""Template Gallery - Manages discovery and loading of knowledge extraction templates.

Auto-loads templates from presets directory.
"""

from pathlib import Path
from typing import Optional

from .parsers import TemplateCfg, load_template


class Gallery:
    """Template Gallery.

    Usage Examples:
        from hyperknowledge.utils.template_engine import Gallery

        # Get template by path
        config = Gallery.get("general/graph")

        # List all templates (returns Dict[str, TemplateCfg])
        all_templates = Gallery.list()

        # List templates with filters
        graph_templates = Gallery.list(filter_by_type="graph")
        zh_templates = Gallery.list(filter_by_language="zh")
    """

    _instance: Optional["Gallery"] = None

    def __init__(self):
        self._configs: dict[str, TemplateCfg] = {}

    @classmethod
    def get(cls, path: str) -> TemplateCfg | None:
        """Get template configuration by path.

        Args:
            path: Template path
                If no domain is specified, "general/" is assumed.
                Only templates in the "general/" domain are supported.
                Other domains are not supported.
                (e.g., "general/graph" or "graph")

        Returns:
            TemplateCfg or None if not found
        """
        if "/" in path:
            return cls._instance._configs.get(path)

        return cls._instance._configs.get(f"general/{path}")

    @classmethod
    def list(
        cls,
        filter_by_query: str | None = None,
        filter_by_type: str | None = None,
        filter_by_tag: str | None = None,
        filter_by_language: str | None = None,
    ) -> dict[str, "TemplateCfg"]:
        """List templates with optional filters.

        Args:
            filter_by_query: Search in template name/description
            filter_by_type: Filter by autotype (e.g., "graph", "list", "model")
            filter_by_tag: Filter by tag
            filter_by_language: Filter by language (e.g., "zh", "en")

        Returns:
            Dict mapping template name to TemplateCfg
        """
        if not cls._instance:
            return {}

        results = {}
        for key, config in cls._instance._configs.items():
            q = filter_by_query.lower() if filter_by_query else None

            if q and q not in config.name.lower():
                desc = config.description
                if isinstance(desc, str) and q not in desc.lower():
                    continue
                if isinstance(desc, dict) and not any(
                    q in v.lower() for v in desc.values()
                ):
                    continue

            if filter_by_type and config.type != filter_by_type:
                continue
            if filter_by_tag and (not config.tags or filter_by_tag not in config.tags):
                continue
            if filter_by_language:
                config_lang = config.language
                if isinstance(config_lang, list):
                    if filter_by_language not in config_lang:
                        continue
                elif config_lang != filter_by_language:
                    continue
            results[key] = config

        return results

    def _load_config(self, file_path: Path, presets_dir: Path) -> None:
        try:
            config = load_template(file_path)
            domain = file_path.parent.relative_to(presets_dir).parts[0]
            key = f"{domain}/{config.name}"
            self._configs[key] = config
        except Exception as e:
            print(f"Failed to load config {file_path}: {e}")


def _init_gallery() -> Gallery:
    gallery = Gallery()
    Gallery._instance = gallery

    presets_dir = Path(__file__).parent.parent.parent / "templates" / "presets"

    if presets_dir.exists():
        for file_path in presets_dir.rglob("*.yaml"):
            gallery._load_config(file_path, presets_dir)

    return gallery


Gallery._instance = _init_gallery()
