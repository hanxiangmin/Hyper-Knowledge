"""Tests for parse_guideline label localization."""

from types import SimpleNamespace

from hyperknowledge.utils.template_engine.parsers.guideline import parse_guideline


def _guideline():
    return SimpleNamespace(target="Extract people", rules="Be precise")


def test_labels_follow_language():
    """Section labels use the given language, not a hardcoded one."""
    en = parse_guideline(_guideline(), "model", "en")
    assert "Role and Task" in en
    assert "角色与任务" not in en

    zh = parse_guideline(_guideline(), "model", "zh")
    assert "角色与任务" in zh
    assert "Role and Task" not in zh


def test_unknown_language_falls_back_to_en():
    out = parse_guideline(_guideline(), "model", "fr")
    assert "Role and Task" in out
