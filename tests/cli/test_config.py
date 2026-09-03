"""Tests for ConfigManager persistence."""

from pathlib import Path

from hyperknowledge.cli.config import DEFAULT_CONFIG_DIR, ConfigManager
from hyperknowledge.utils.client import DEFAULT_CONFIG_DIR as CLIENT_CONFIG_DIR


def test_default_config_directory_uses_hyper_knowledge_identity():
    """CLI and Python clients share the canonical .hk location."""
    assert DEFAULT_CONFIG_DIR == Path.home() / ".hk"
    assert CLIENT_CONFIG_DIR == DEFAULT_CONFIG_DIR


def test_save_creates_custom_parent_dir(tmp_path):
    """_save() must create the parent of a custom config_path, not the default dir."""
    cfg_path = tmp_path / "nested" / "dir" / "config.toml"  # parent doesn't exist yet

    mgr = ConfigManager(cfg_path)
    mgr.set_llm(provider="openai", model="gpt-4o-mini", api_key="sk-x")

    assert cfg_path.exists()

    # Round-trips back through a fresh manager.
    reloaded = ConfigManager(cfg_path)
    assert reloaded.llm.model == "gpt-4o-mini"
