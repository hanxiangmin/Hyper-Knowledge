"""MkDocs hooks for documentation build adjustments."""

import logging


class SuppressDuplicatePrimaryURLFilter(logging.Filter):
    """Silences mkdocstrings-autorefs "Multiple primary URLs found" warnings.

    These warnings are expected in bilingual (i18n) builds because the same
    Python identifier is documented in both the default and translated API
    reference pages. The duplicate-primary-URL warning is noise in this
    context and does not indicate a real cross-reference error.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return "Multiple primary URLs found" not in record.getMessage()


def _suppress_autorefs_duplicates():
    """Apply logging filter to all mkdocs_autorefs loggers.

    mkdocs_autorefs uses child loggers such as
    ``mkdocs.plugins.mkdocs_autorefs._internal.references``.  We must attach
    the filter to every concrete logger that emits the warning.
    """
    target_prefix = "mkdocs.plugins.mkdocs_autorefs"
    filter_obj = SuppressDuplicatePrimaryURLFilter()

    for name, logger in logging.Logger.manager.loggerDict.items():
        if name.startswith(target_prefix) and isinstance(logger, logging.Logger):
            if not any(isinstance(f, SuppressDuplicatePrimaryURLFilter) for f in logger.filters):
                logger.addFilter(filter_obj)

    # Also cover the parent logger itself
    parent = logging.getLogger(target_prefix)
    if not any(isinstance(f, SuppressDuplicatePrimaryURLFilter) for f in parent.filters):
        parent.addFilter(filter_obj)


def on_config(config, **kwargs):
    """Apply logging filters after configuration is loaded."""
    _suppress_autorefs_duplicates()
    return config


def on_pre_build(config, **kwargs):
    """Re-apply filter right before build starts (plugins may recreate loggers)."""
    _suppress_autorefs_duplicates()
