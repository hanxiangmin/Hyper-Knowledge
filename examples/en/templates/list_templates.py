"""List validated templates and their documented English dataset mappings."""

from pathlib import Path

import yaml

from hyperknowledge import Template


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MATRIX = PROJECT_ROOT / "examples" / "template_dataset_matrix.yaml"


def list_templates() -> None:
    mappings = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))["cases"]
    templates = Template.list(include_methods=False)
    print("\n" + "=" * 80)
    print("Hyper-Knowledge preset templates and documented English fixtures")
    print("=" * 80)
    for case in mappings:
        template = case["template"]
        config = templates.get(template)
        state = "READY" if config else "MISSING"
        kind = config.type if config else "unknown"
        print(f"[{state}] {template:<36} {kind:<24} {case['dataset']}")
    print("\nRun one extraction with:")
    print("  hk parse tests/test_data/en/<dataset> -t <template> -l en -o <ka>")


if __name__ == "__main__":
    list_templates()
