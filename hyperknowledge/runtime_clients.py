"""Resolve only the model capabilities a workflow actually uses."""

from pathlib import Path

from langchain_core.embeddings import Embeddings


def configured_llm():
    from hyperknowledge.cli.config import ConfigManager
    from hyperknowledge.utils.client import DEFAULT_CONFIG_FILE, create_llm

    manager = ConfigManager(DEFAULT_CONFIG_FILE)
    valid, message = manager.validate(require_embeddings=False)
    if not valid:
        raise ValueError(message)
    return create_llm(manager.get_llm_config().to_dict())


class DeferredEmbeddings(Embeddings):
    """Construct a real embedder on first use; never fabricate vectors."""

    def __init__(self, config_path: str | Path | None = None):
        self.config_path = config_path
        self._client = None

    def _resolve(self):
        if self._client is None:
            from hyperknowledge.cli.config import ConfigManager
            from hyperknowledge.utils.client import DEFAULT_CONFIG_FILE, create_embedder

            manager = ConfigManager(self.config_path or DEFAULT_CONFIG_FILE)
            config = manager.get_embedder_config()
            if config.provider != "vllm" and not config.api_key:
                raise ValueError(
                    "This operation needs embeddings. Configure 'hk config embedder' "
                    "or pass embedder= explicitly. Extraction without an index and "
                    "bundle import/visualization do not need embeddings."
                )
            if config.provider == "vllm" and not config.base_url:
                raise ValueError("The embedding service requires a base_url.")
            self._client = create_embedder(config.to_dict())
        return self._client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._resolve().embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._resolve().embed_query(text)
