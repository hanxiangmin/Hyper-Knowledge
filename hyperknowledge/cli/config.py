"""Configuration management for Hyper-Knowledge CLI."""

import json
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli_w

DEFAULT_CONFIG_DIR = Path.home() / ".hk"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"

# Provider presets: base_url and default models for each provider
PROVIDER_PRESETS: dict[str, dict[str, str | None]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_llm": "gpt-4o-mini",
        "default_embedder": "text-embedding-3-small",
    },
    "bailian": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_llm": "qwen3.6-plus",
        "default_embedder": "text-embedding-v4",
    },
    "vllm": {
        "base_url": None,
        "default_llm": None,
        "default_embedder": None,
    },
    # DeepSeek: OpenAI-compatible, no embeddings API.
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_llm": "deepseek-v4-flash",
        "default_embedder": None,
    },
    # Anthropic (Claude): native client, no base_url, no embeddings API.
    "anthropic": {
        "base_url": "",
        "default_llm": "claude-opus-4-8",
        "default_embedder": None,
    },
    "claude": {
        "base_url": "",
        "default_llm": "claude-opus-4-8",
        "default_embedder": None,
    },
}

# Environment variables checked (in order) for each provider's API key.
PROVIDER_API_KEY_ENV: dict[str, tuple] = {
    "anthropic": ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"),
    "claude": ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"),
    "deepseek": ("DEEPSEEK_API_KEY",),
}


def _env_api_key(provider: str) -> str:
    """Return the first non-empty API key from the provider's env vars.

    Falls back to OPENAI_API_KEY for OpenAI-compatible providers.
    """
    for var in PROVIDER_API_KEY_ENV.get(provider, ("OPENAI_API_KEY",)):
        value = os.environ.get(var, "")
        if value:
            return value
    return ""


@dataclass
class LLMConfig:
    provider: str = ""
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMConfig":
        return cls(
            provider=data.get("provider", ""),
            model=data.get("model", "gpt-4o-mini"),
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", ""),
        )


@dataclass
class EmbedderConfig:
    provider: str = ""
    model: str = "text-embedding-3-small"
    api_key: str = ""
    base_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmbedderConfig":
        return cls(
            provider=data.get("provider", ""),
            model=data.get("model", "text-embedding-3-small"),
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", ""),
        )


class ConfigManager:
    """Manages Hyper-Knowledge CLI configuration."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or DEFAULT_CONFIG_FILE
        self.llm = LLMConfig()
        self.embedder = EmbedderConfig()
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            return

        with open(self.config_path, "rb") as f:
            data = tomllib.load(f)

        if "llm" in data:
            self.llm = LLMConfig.from_dict(data["llm"])
        if "embedder" in data:
            self.embedder = EmbedderConfig.from_dict(data["embedder"])

    def _save(self) -> None:
        """Save configuration to file."""
        # Create the parent of the actual target path, not the default dir —
        # a custom config_path may live elsewhere and would otherwise 404.
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "llm": self.llm.to_dict(),
            "embedder": self.embedder.to_dict(),
        }

        with open(self.config_path, "wb") as f:
            tomli_w.dump(data, f)

    def _resolve_base_url(self, provider: str, explicit_base_url: str) -> str:
        """Resolve base_url from provider preset. Explicit value takes precedence."""
        if explicit_base_url:
            return explicit_base_url
        if provider in PROVIDER_PRESETS:
            preset_url = PROVIDER_PRESETS[provider].get("base_url")
            if preset_url is None:
                raise ValueError(
                    f"Provider '{provider}' requires explicit base_url. "
                    f"Please set it via config or environment variable."
                )
            return preset_url
        return ""

    def get_llm_config(self) -> LLMConfig:
        """Get LLM config with environment variable fallback."""
        config = LLMConfig(
            provider=self.llm.provider,
            model=self.llm.model,
            api_key=self.llm.api_key or _env_api_key(self.llm.provider),
            base_url=self._resolve_base_url(
                self.llm.provider,
                self.llm.base_url or os.environ.get("OPENAI_BASE_URL", ""),
            ),
        )
        return config

    def get_embedder_config(self) -> EmbedderConfig:
        """Get Embedder config with environment variable fallback."""
        config = EmbedderConfig(
            provider=self.embedder.provider,
            model=self.embedder.model,
            api_key=self.embedder.api_key or _env_api_key(self.embedder.provider),
            base_url=self._resolve_base_url(
                self.embedder.provider,
                self.embedder.base_url or os.environ.get("OPENAI_BASE_URL", ""),
            ),
        )
        return config

    def set_llm(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Set LLM configuration."""
        if provider is not None:
            self.llm.provider = provider
        if model:
            self.llm.model = model
        if api_key is not None:
            self.llm.api_key = api_key
        if base_url is not None:
            self.llm.base_url = base_url
        self._save()

    def set_embedder(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Set Embedder configuration."""
        if provider is not None:
            self.embedder.provider = provider
        if model:
            self.embedder.model = model
        if api_key is not None:
            self.embedder.api_key = api_key
        if base_url is not None:
            self.embedder.base_url = base_url
        self._save()

    def unset_llm(self) -> None:
        """Unset LLM configuration."""
        self.llm = LLMConfig()
        self._save()

    def unset_embedder(self) -> None:
        """Unset Embedder configuration."""
        self.embedder = EmbedderConfig()
        self._save()

    def show(self) -> dict[str, Any]:
        """Show current configuration."""
        return {
            "llm": self.get_llm_config().to_dict(),
            "embedder": self.get_embedder_config().to_dict(),
        }

    def validate(self) -> tuple[bool, str]:
        """Validate configuration."""
        llm_config = self.get_llm_config()
        embedder_config = self.get_embedder_config()

        # vLLM mode: api_key can be empty or dummy, but base_url is required
        if llm_config.provider == "vllm":
            if not llm_config.base_url:
                return False, "vLLM provider requires base_url."
        elif not llm_config.api_key:
            return (
                False,
                "LLM API key is not configured. Run 'hk config llm --api-key YOUR_KEY'",
            )

        if embedder_config.provider == "vllm":
            if not embedder_config.base_url:
                return False, "vLLM embedder requires base_url."
        elif not embedder_config.api_key:
            return (
                False,
                "Embedder API key is not configured. Run 'hk config embedder --api-key YOUR_KEY'",
            )

        return True, "Configuration is valid"


def load_ka_metadata(ka_path: Path) -> dict[str, Any] | None:
    """Load knowledge abstract metadata from directory."""
    metadata_path = ka_path / "metadata.json"
    if not metadata_path.exists():
        return None

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)
