"""Pytest configuration: Auto-detect environment (Real API vs Mock) and inject fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (requires OPENAI_API_KEY env var)",
    )


# Load .env file if it exists
def _load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    # Also check for .env in current working directory
    load_dotenv()


_load_env()


def _has_openai_key() -> bool:
    """Check if OpenAI API key is available in environment."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(api_key and api_key != "sk-")


@pytest.fixture(scope="session")
def is_real_env() -> bool:
    """Fixture indicating whether tests should use real API or mock."""
    has_key = _has_openai_key()
    if has_key:
        print("\n\n[PYTEST CONFIG] 🔌 Real OpenAI API detected - Using REAL LLM & Embeddings")
    else:
        print("\n\n[PYTEST CONFIG] 🎭 No API key found - Using MOCK LLM & Embeddings")
    return has_key


@pytest.fixture(scope="session")
def llm_client(is_real_env):
    """
    Fixture that provides LLM client (Real or Mock).

    Auto-switches based on whether OPENAI_API_KEY is set.
    """
    if is_real_env:
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model="gpt-4o-mini", temperature=0)
        except ImportError:
            pytest.fail(
                "OPENAI_API_KEY detected but 'langchain-openai' package not installed. "
                "Install with: pip install langchain-openai"
            )
    else:
        from tests.mocks import MockChatModel

        return MockChatModel()


@pytest.fixture(scope="session")
def embedder(is_real_env):
    """
    Fixture that provides Embeddings client (Real or Mock).

    Auto-switches based on whether OPENAI_API_KEY is set.
    """
    if is_real_env:
        try:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(model="text-embedding-3-small")
        except ImportError:
            pytest.fail(
                "OPENAI_API_KEY detected but 'langchain-openai' package not installed. "
                "Install with: pip install langchain-openai"
            )
    else:
        from tests.mocks import MockEmbeddings

        return MockEmbeddings()
