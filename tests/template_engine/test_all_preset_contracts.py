"""Every bundled preset must compile for every declared language."""

from pathlib import Path

import pytest

from hyperknowledge.utils.template_engine.parsers import (
    load_template,
    localize_template,
    parse_display,
    parse_guideline,
    parse_identifiers,
    parse_option,
    parse_output,
)


PRESETS = Path(__file__).parents[2] / "hyperknowledge" / "templates" / "presets"
TEMPLATES = sorted(PRESETS.rglob("*.yaml"))


@pytest.mark.parametrize(
    "template_path",
    TEMPLATES,
    ids=lambda path: path.relative_to(PRESETS).as_posix(),
)
def test_every_preset_compiles_its_runtime_contract(template_path):
    config = load_template(template_path)
    languages = (
        config.language if isinstance(config.language, list) else [config.language]
    )
    for language in languages:
        localized = localize_template(config, language)
        parse_output(localized.output, localized.type)
        parse_guideline(localized.guideline, localized.type, localized.language)
        parse_option(localized.options, localized.type)
        parse_display(localized.display, localized.type)
        if localized.identifiers is not None:
            parse_identifiers(localized.identifiers, localized.type)
