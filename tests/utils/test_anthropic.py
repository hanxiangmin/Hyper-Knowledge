"""Tests for the Anthropic (Claude) provider integration."""

from unittest.mock import patch

import pytest

from hyperknowledge.utils.client import (
    ANTHROPIC_PROVIDERS,
    PROVIDER_PRESETS,
    _env_api_key,
    _parse_client_spec,
    create_embedder,
    create_llm,
)


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------


class TestAnthropicPresets:
    def test_anthropic_preset(self):
        preset = PROVIDER_PRESETS["anthropic"]
        assert preset["base_url"] == ""  # native client, no base_url needed
        assert preset["default_llm"]
        assert preset["default_embedder"] is None  # no embeddings API

    def test_claude_alias_matches_anthropic(self):
        assert PROVIDER_PRESETS["claude"] == PROVIDER_PRESETS["anthropic"]

    def test_providers_constant(self):
        assert "anthropic" in ANTHROPIC_PROVIDERS
        assert "claude" in ANTHROPIC_PROVIDERS


# ---------------------------------------------------------------------------
# Spec parsing
# ---------------------------------------------------------------------------


class TestParseAnthropicSpec:
    def test_default_model(self):
        result = _parse_client_spec("anthropic", default_kind="llm")
        assert result["provider"] == "anthropic"
        assert result["model"] == PROVIDER_PRESETS["anthropic"]["default_llm"]

    def test_explicit_model(self):
        result = _parse_client_spec("anthropic:claude-opus-4-1", default_kind="llm")
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-opus-4-1"


# ---------------------------------------------------------------------------
# API key env resolution
# ---------------------------------------------------------------------------


class TestEnvApiKey:
    def test_anthropic_uses_anthropic_key(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-xyz")
        assert _env_api_key("anthropic") == "sk-ant-xyz"

    def test_anthropic_falls_back_to_claude_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("CLAUDE_API_KEY", "sk-claude")
        assert _env_api_key("claude") == "sk-claude"

    def test_openai_default(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-oai")
        assert _env_api_key("openai") == "sk-oai"


# ---------------------------------------------------------------------------
# create_llm — Anthropic branch
# ---------------------------------------------------------------------------


class TestCreateLLMAnthropic:
    def test_builds_chatanthropic(self):
        with patch("langchain_anthropic.ChatAnthropic") as MockChat:
            create_llm("anthropic:claude-sonnet-4-6", api_key="sk-ant-1")
            MockChat.assert_called_once()
            kwargs = MockChat.call_args.kwargs
            assert kwargs["model"] == "claude-sonnet-4-6"
            assert kwargs["api_key"] == "sk-ant-1"
            assert kwargs["temperature"] == 0
            assert kwargs["max_tokens"] == 4096

    def test_env_key_fallback(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-env")
        with patch("langchain_anthropic.ChatAnthropic") as MockChat:
            create_llm("anthropic")
            assert MockChat.call_args.kwargs["api_key"] == "sk-env"

    def test_missing_key_raises(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        with patch("langchain_anthropic.ChatAnthropic"):
            with pytest.raises(ValueError, match="Anthropic API key"):
                create_llm("anthropic")

    def test_temperature_and_max_tokens_forwarded(self):
        with patch("langchain_anthropic.ChatAnthropic") as MockChat:
            create_llm("anthropic", api_key="k", temperature=0.7, max_tokens=8192)
            kwargs = MockChat.call_args.kwargs
            assert kwargs["temperature"] == 0.7
            assert kwargs["max_tokens"] == 8192


# ---------------------------------------------------------------------------
# create_embedder — Anthropic guard
# ---------------------------------------------------------------------------


class TestCreateEmbedderAnthropicGuard:
    def test_anthropic_embedder_raises(self):
        with pytest.raises(ValueError, match="embeddings"):
            create_embedder("anthropic", api_key="sk-ant")

    def test_claude_embedder_raises(self):
        with pytest.raises(ValueError, match="embeddings"):
            create_embedder("claude", api_key="sk-ant")


# ---------------------------------------------------------------------------
# ConfigManager integration
# ---------------------------------------------------------------------------


class TestConfigManagerAnthropic:
    def test_resolves_without_base_url_error(self, tmp_path, monkeypatch):
        from hyperknowledge.cli.config import ConfigManager

        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-cfg")

        cm = ConfigManager(tmp_path / "config.toml")
        cm.set_llm(provider="anthropic", model="claude-sonnet-4-6", api_key="")
        cfg = cm.get_llm_config()

        assert cfg.provider == "anthropic"
        assert cfg.base_url == ""  # must not raise (unlike vllm)
        assert cfg.api_key == "sk-ant-cfg"
