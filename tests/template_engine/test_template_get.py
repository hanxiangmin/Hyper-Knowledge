"""Template lookup supports the same custom YAML paths as Template.create."""

from pathlib import Path

from hyperknowledge.utils.template_engine import Template


def test_get_loads_custom_yaml_path():
    root = Path(__file__).parents[2]
    template_path = (
        root / "hyperknowledge" / "templates" / "presets" / "general" / "base_graph.yaml"
    )

    config = Template.get(str(template_path))

    assert config is not None
    assert config.type == "graph"
    assert config.identifiers.relation_members == {
        "source": "source",
        "target": "target",
    }
