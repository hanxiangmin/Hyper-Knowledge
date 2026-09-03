"""Dataset benchmark commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from hyperknowledge.dataset_benchmark import benchmark_datasets, write_dataset_benchmark


console = Console()
app = typer.Typer(name="benchmark", help="Run deterministic Hyper-Knowledge benchmarks")


@app.command(name="datasets")
def datasets(
    inputs: list[Path] = typer.Argument(
        ...,
        help="Dataset files or directories; every .md and .txt file is checked",
    ),
    output: Path = typer.Option(
        Path("hyperknowledge-dataset-benchmark"),
        "--output",
        "-o",
        help="Receipt directory",
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit one JSON receipt"),
):
    """Preflight every dataset without making LLM or network calls."""
    try:
        report = benchmark_datasets(inputs)
        receipt = write_dataset_benchmark(report, output)
    except (OSError, ValueError) as exc:
        payload = {
            "schema_version": "hk.dataset-benchmark/v1",
            "status": "error",
            "error": str(exc),
        }
        if as_json:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            console.print(f"[red]Dataset benchmark failed:[/red] {exc}")
        raise typer.Exit(1)

    if as_json:
        typer.echo(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        summary = receipt["summary"]
        color = "green" if receipt["status"] == "passed" else "red"
        console.print(
            f"[{color}]{receipt['status']}[/{color}]: "
            f"{summary['passed']}/{summary['total']} datasets passed"
        )
        console.print(f"[dim]{receipt['report_markdown']}[/dim]")
    if receipt["status"] != "passed":
        raise typer.Exit(1)
