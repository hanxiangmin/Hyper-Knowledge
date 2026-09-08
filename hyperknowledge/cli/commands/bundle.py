"""Export normalized Knowledge Bundles."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from hyperknowledge.bundle import BundleExportError, export_bundle, validate_bundle

console = Console()
app = typer.Typer(
    name="bundle", help="Import, export and validate versioned knowledge bundles"
)


@app.command(name="import")
def import_command(
    graph: Path = typer.Argument(..., help="JSON containing Bundle-v1 tables"),
    output: Path = typer.Option(..., "--output", "-o", help="Bundle output directory"),
    source: list[str] = typer.Option(
        [], "--source", help="Allowed source NAME=PATH; repeat for multiple files"
    ),
    language: str = typer.Option("zh", "--lang", "-l"),
    quality: str = typer.Option("standard", help="standard or showcase"),
    force: bool = typer.Option(
        False, help="Retain old output as a backup and replace it"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Import structured hypergraph data locally, without a model or vector index."""
    from hyperknowledge.api import import_graph

    try:
        sources = {}
        for item in source:
            name, separator, path = item.partition("=")
            if not separator or not name or not path or name in sources:
                raise ValueError("Use one unique --source NAME=PATH per source file")
            sources[name] = path
        result = import_graph(
            graph,
            output_dir=output,
            sources=sources,
            language=language,
            quality=quality,
            force=force,
        )
        payload = {"ok": True, **result.to_dict()}
    except (ValueError, OSError, TypeError) as exc:
        if as_json:
            typer.echo(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
        else:
            console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)
    if as_json:
        typer.echo(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        console.print(f"[green]Bundle imported:[/green] {result.bundle_path}")


@app.command(name="export")
def export(
    ka_path: Path = typer.Argument(..., help="Knowledge Abstract directory"),
    output: Path = typer.Option(..., "--output", "-o", help="Bundle output directory"),
    force: bool = typer.Option(False, help="Replace existing bundle files"),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Export a KA to hk.bundle/v1 without loading its vector index."""
    try:
        manifest = export_bundle(ka_path, output, force=force)
    except (BundleExportError, OSError, json.JSONDecodeError) as exc:
        if as_json:
            typer.echo(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)
    payload = {"ok": True, "bundle_path": str(output.resolve()), "manifest": manifest}
    if as_json:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]Bundle exported:[/green] {output.resolve()}")


@app.command(name="validate")
def validate(
    bundle_path: Path = typer.Argument(..., help="hk.bundle/v1 directory"),
    quality: str = typer.Option(
        "standard", help="Validation profile: standard or showcase"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Validate bundle topology, references, counts, and file identity."""
    try:
        receipt = validate_bundle(bundle_path, quality=quality)
    except (BundleExportError, OSError, json.JSONDecodeError) as exc:
        receipt = {"status": "error", "error": str(exc)}
    if as_json:
        typer.echo(json.dumps(receipt, ensure_ascii=True, indent=2))
    else:
        summary = receipt.get("summary", {})
        console.print(
            f"[{'green' if receipt.get('status') == 'passed' else 'red'}]"
            f"{receipt.get('status')}[/]: {summary.get('checks', 0)} checks, "
            f"{summary.get('errors', 0)} errors, {summary.get('warnings', 0)} warnings"
        )
    if receipt.get("status") != "passed":
        raise typer.Exit(1)
