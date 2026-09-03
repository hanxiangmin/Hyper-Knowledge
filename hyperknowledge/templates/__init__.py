"""Hyper-Knowledge templates module.

此模块提供知识模板的 YAML 配置文件。

目录结构:
    templates/
    └── presets/          # 预设模板（系统预置）

使用方式:
    >>> from hyperknowledge.utils.template_engine import Template

    # 使用preset模板
    >>> template = Template.create("general/graph", "zh", llm, embedder)

    # 使用自定义模板（文件路径）
    >>> template = Template.create("/path/to/my_template.yaml", "zh", llm, embedder)
"""

__all__ = []
