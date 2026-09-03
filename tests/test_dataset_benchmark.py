"""Dataset-by-dataset benchmark coverage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hyperknowledge.dataset_benchmark import (
    benchmark_datasets,
    inspect_dataset,
    write_dataset_benchmark,
)


ROOT = Path(__file__).parent / "test_data"
DATASETS = sorted(
    path
    for path in ROOT.rglob("*")
    if path.is_file() and path.suffix.lower() in {".md", ".txt"}
)
EXAMPLE_DATASETS = [
    Path(__file__).parents[1] / "examples" / "en" / "tesla.md",
    Path(__file__).parents[1] / "examples" / "zh" / "sushi.md",
    Path(__file__).parents[1]
    / "docs"
    / "assets"
    / "examples"
    / "en"
    / "transformer_paper.txt",
    Path(__file__).parents[1]
    / "docs"
    / "assets"
    / "examples"
    / "zh"
    / "transformer_paper.txt",
    Path(__file__).parent / "kg.md",
]
QUERY_FIXTURES = [
    Path(__file__).parents[1] / "examples" / "en" / "tesla_question.md",
    Path(__file__).parents[1] / "examples" / "zh" / "sushi_question.md",
]


@pytest.mark.parametrize(
    "dataset",
    DATASETS,
    ids=lambda path: path.relative_to(ROOT).as_posix(),
)
def test_each_bundled_dataset_passes_offline_preflight(dataset):
    record = inspect_dataset(dataset, root=ROOT)
    assert record["status"] == "passed", record["diagnostics"]


@pytest.mark.parametrize("dataset", EXAMPLE_DATASETS, ids=lambda path: path.name)
def test_each_documented_demo_corpus_passes_offline_preflight(dataset):
    record = inspect_dataset(dataset)
    assert record["status"] == "passed", record["diagnostics"]


@pytest.mark.parametrize("query_fixture", QUERY_FIXTURES, ids=lambda path: path.name)
def test_each_query_fixture_passes_text_preflight(query_fixture):
    record = inspect_dataset(query_fixture)
    assert record["status"] == "passed", record["diagnostics"]


def test_benchmark_writes_stable_receipts(tmp_path):
    report = benchmark_datasets([ROOT, *EXAMPLE_DATASETS])
    assert report["status"] == "passed"
    assert report["summary"]["total"] == len(DATASETS) + len(EXAMPLE_DATASETS)
    assert report["summary"]["live_semantic_extraction"] == "not_run"

    receipt = write_dataset_benchmark(report, tmp_path)
    parsed = json.loads(Path(receipt["report_json"]).read_text(encoding="utf-8"))
    assert parsed["dataset_manifest_sha256"] == report["dataset_manifest_sha256"]
    markdown = Path(receipt["report_markdown"]).read_text(encoding="utf-8")
    assert "## Diagnostics" in markdown
    assert "dataset.markdown_heading" in markdown


def test_invalid_dataset_produces_actionable_diagnostic(tmp_path):
    broken = tmp_path / "broken.md"
    broken.write_bytes(b"\xff\x00")
    record = inspect_dataset(broken)
    assert record["status"] == "failed"
    assert any(item["code"] == "dataset.utf8" for item in record["diagnostics"])
