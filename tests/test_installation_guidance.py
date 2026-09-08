"""Keep environment-specific setup complete and user chat requests short."""

import re

import pytest

from tools.check_install_docs import PAGES, recipe


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_conda_and_runtime_recipes_agree(page):
    text = page.read_text(encoding="utf-8")
    reference = PAGES[4].read_text(encoding="utf-8")
    assert recipe(text, "conda") == recipe(reference, "conda")
    assert recipe(text, "runtime") == recipe(reference, "runtime")
    assert "python=3.12 pip git" in recipe(text, "conda")
    assert "conda activate research" in text
    assert "base" in text
    assert (
        "python -m hyperknowledge skill install --platform codex --scope user" in text
    )
    assert "python -m hyperknowledge skill install --platform kimi --scope user" in text


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_install_chat_is_short_and_preserves_local_edits(page):
    text = page.read_text(encoding="utf-8")
    prompts = [
        block.strip()
        for block in re.findall(r"```text\n(.*?)```", text, re.S)
        if "github.com/hanxiangmin/Hyper-Knowledge" in block
    ]
    assert len(prompts) == 2
    for client, prompt in zip(("Codex", "Kimi Code"), prompts, strict=True):
        assert client in prompt
        other = "Kimi Code" if client == "Codex" else "Codex"
        assert other not in prompt
        assert len(prompt.splitlines()) == 1
        assert len(prompt) < 260
        assert "Conda" in prompt
        assert "修改" in prompt or "local edits" in prompt
        assert "python -m" not in prompt
        assert "research" not in prompt
    assert "replace `Codex`" not in text
    assert "只把句子中的" not in text
