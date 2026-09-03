"""Integration tests using real OpenAI API.

These tests are marked with @pytest.mark.integration and require OPENAI_API_KEY.
Run with: pytest -m integration -v
"""

import pytest

# Skip all integration tests if no API key is available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not pytest.importorskip("os").environ.get("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    ),
]
