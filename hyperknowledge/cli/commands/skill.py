"""Manage the bundled Codex skill."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from hyperknowledge.skill_manager import (
    SkillInstallError,
    doctor_skill,
    install_skill,
    uninstall_skill,
)


console = Console()
app = typer.Typer(name="skill", help="Install and verify the Codex skill")


def _require_codex(platform: str) -> None:
    if platform.lower() != "codex":
        raise typer.BadParameter("Only the 'codex' platform is supported in v0.5")


def _emit(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    status = payload.get("status", "unknown")
    path = payload.get("path", "")
    color = "green" if payload.get("ok") else "yellow"
    console.print(f"[{color}]{status}[/{color}]: {path}")
    for issue in payload.get("issues", []):
        console.print(f"[yellow]- {issue}[/yellow]")
    if payload.get("backup_path"):
        console.print(
            f"[dim]Previous installation backed up to {payload['backup_path']}[/dim]"
        )


def _run(operation, *, as_json: bool, **kwargs) -> None:
    try:
        payload = operation(**kwargs)
    except SkillInstallError as exc:
        payload = {"ok": False, "status": "error", "error": str(exc)}
        _emit(payload, as_json)
        raise typer.Exit(1)
    _emit(payload, as_json)
    if not payload.get("ok", False):
        raise typer.Exit(1)


@app.command(name="install")
def install(
    platform: str = typer.Option(
        "codex", help="Target agent platform (currently: codex)"
    ),
    scope: str = typer.Option("user", help="Installation scope: user or project"),
    project_root: Path | None = typer.Option(
        None, help="Project root for project-scoped installation"
    ),
    force: bool = typer.Option(False, help="Replace an unmanaged or modified skill"),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Install the bundled skill into an official Codex discovery directory."""
    _require_codex(platform)
    _run(
        install_skill,
        as_json=as_json,
        scope=scope,
        project_root=project_root,
        force=force,
    )


@app.command(name="doctor")
def doctor(
    platform: str = typer.Option(
        "codex", help="Target agent platform (currently: codex)"
    ),
    scope: str = typer.Option("user", help="Installation scope: user or project"),
    project_root: Path | None = typer.Option(
        None, help="Project root for project-scoped installation"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
    deep: bool = typer.Option(
        False, help="Probe the pinned runtime and render a synthetic comparison demo"
    ),
):
    """Check bundled files, installation ownership, version, and drift."""
    _require_codex(platform)
    _run(
        doctor_skill,
        as_json=as_json,
        scope=scope,
        project_root=project_root,
        deep=deep,
    )


@app.command(name="demo")
def demo(
    output: Path = typer.Option(
        Path("hyperknowledge-skill-demo"),
        "--output",
        "-o",
        help="Synthetic demo output directory",
    ),
    force: bool = typer.Option(False, help="Replace known demo files"),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Generate a synthetic graph/hypergraph comparison without an LLM."""
    from hyperknowledge.demo import create_skill_demo

    try:
        receipt = create_skill_demo(output, force=force)
    except (OSError, ValueError) as exc:
        payload = {"ok": False, "status": "error", "error": str(exc)}
        _emit(payload, as_json)
        raise typer.Exit(1)
    payload = {"ok": True, **receipt}
    if as_json:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]Synthetic demo created:[/green] {receipt['html']}")


@app.command(name="uninstall")
def uninstall(
    platform: str = typer.Option(
        "codex", help="Target agent platform (currently: codex)"
    ),
    scope: str = typer.Option("user", help="Installation scope: user or project"),
    project_root: Path | None = typer.Option(
        None, help="Project root for project-scoped installation"
    ),
    force: bool = typer.Option(False, help="Remove an unmanaged or modified skill"),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Remove only the managed Hyper-Knowledge skill directory."""
    _require_codex(platform)
    _run(
        uninstall_skill,
        as_json=as_json,
        scope=scope,
        project_root=project_root,
        force=force,
    )
