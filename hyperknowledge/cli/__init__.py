"""Hyper-Knowledge command-line interface."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hyper-knowledge")
except PackageNotFoundError:
    __version__ = "source"
__author__ = "hanxiangmin"

from .cli import app

__all__ = ["app"]
