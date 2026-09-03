"""Methods Layer - Algorithms and strategies for knowledge extraction.

This module organizes concrete algorithms and strategies that operate on
the AutoTypes primitives. It's divided into:
- rag: Retrieval-augmented generation strategies
- typical: Typical/canonical graph construction pipelines
"""

from . import rag, typical
from .registry import (
    MethodCfg,
    get_method,
    get_method_cfg,
    list_method_cfgs,
    list_methods,
    register_method,
)

__all__ = [
    "MethodCfg",
    "get_method",
    "get_method_cfg",
    "list_method_cfgs",
    "list_methods",
    "rag",
    "register_method",
    "typical",
]
