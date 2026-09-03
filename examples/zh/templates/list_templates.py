"""列出已校验模板及它们的中文示例数据映射。"""

from pathlib import Path

import yaml

from hyperknowledge import Template


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MATRIX = PROJECT_ROOT / "examples" / "template_dataset_matrix.yaml"


def list_templates() -> None:
    mappings = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))["cases"]
    templates = Template.list(include_methods=False)
    print("\n" + "=" * 80)
    print("Hyper-Knowledge 预设模板与中文示例数据")
    print("=" * 80)
    for case in mappings:
        template = case["template"]
        config = templates.get(template)
        state = "可用" if config else "缺失"
        kind = config.type if config else "unknown"
        print(f"[{state}] {template:<36} {kind:<24} {case['dataset']}")
    print("\n运行单项抽取：")
    print("  hk parse tests/test_data/zh/<dataset> -t <template> -l zh -o <ka>")


if __name__ == "__main__":
    list_templates()
