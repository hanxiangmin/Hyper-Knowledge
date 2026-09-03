"""Common utilities for Hyper-Knowledge CLI."""

import sys
from pathlib import Path

import typer
from rich.console import Console

from .config import ConfigManager

console = Console()

LOGO = r"""
                                                                                     
▄▄▄   ▄▄▄                                ▄▄▄▄▄▄▄                                     
███   ███                               ███▀▀▀▀▀        ██                      ██   
█████████ ██ ██ ████▄ ▄█▀█▄ ████▄       ███▄▄    ██ ██ ▀██▀▀ ████▄  ▀▀█▄ ▄████ ▀██▀▀ 
███▀▀▀███ ██▄██ ██ ██ ██▄█▀ ██ ▀▀ ▀▀▀▀▀ ███       ███   ██   ██ ▀▀ ▄█▀██ ██     ██   
███   ███  ▀██▀ ████▀ ▀█▄▄▄ ██          ▀███████ ██ ██  ██   ██    ▀█▄██ ▀████  ██   
            ██  ██                                                                   
          ▀▀▀   ▀▀                                                                   
"""


def read_input(input_path: str) -> str:
    """Read input from file or stdin."""
    if input_path == "-":
        return sys.stdin.read()
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def validate_ka_path(ka_path: str) -> Path:
    """Validate Knowledge Abstract path.

    Args:
        ka_path: Knowledge Abstract directory path

    Returns:
        Path object

    Raises:
        typer.Exit: If path is invalid
    """
    path = Path(ka_path)

    if not path.exists():
        console.print(f"[red]Error:[/red] Knowledge Abstract not found: {ka_path}")
        raise typer.Exit(1)

    if not path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {ka_path}")
        raise typer.Exit(1)

    return path


def validate_ka_with_data(ka_path: str) -> Path:
    """Validate Knowledge Abstract path with data.json.

    Args:
        ka_path: Knowledge Abstract directory path

    Returns:
        Path object

    Raises:
        typer.Exit: If path is invalid or missing data.json
    """
    path = validate_ka_path(ka_path)

    data_file = path / "data.json"
    if not data_file.exists():
        console.print(
            f"[red]Error:[/red] Not a valid Knowledge Abstract: {ka_path} (no data.json)"
        )
        raise typer.Exit(1)

    return path


def validate_ka_with_index(ka_path: str) -> Path:
    """Validate Knowledge Abstract path with index.

    Args:
        ka_path: Knowledge Abstract directory path

    Returns:
        Path object

    Raises:
        typer.Exit: If path is invalid or missing index
    """
    path = validate_ka_path(ka_path)

    index_dir = path / "index"
    if not index_dir.exists() or not any(index_dir.iterdir()):
        console.print(
            f"[red]Error:[/red] Index not found. Please run 'hk build-index {ka_path}' first."
        )
        raise typer.Exit(1)

    return path


def get_template_from_ka(ka_path: Path) -> tuple[str, str]:
    """Get template path for Knowledge Abstract.

    Load priority:
    1. If template is in presets (e.g., "general/graph") -> use preset name
    2. If template not in presets -> try to find {template}.yaml in KA directory

    Raises:
        ValueError: If template not found and no local yaml file exists
    """
    from hyperknowledge.utils.template_engine import Gallery

    from .config import load_ka_metadata

    metadata = load_ka_metadata(ka_path)
    if metadata is None:
        raise ValueError(f"No metadata.json found in Knowledge Abstract: {ka_path}")

    template = metadata.get("template")
    lang = metadata.get("lang")

    if template:
        if Gallery.get(template) is not None:
            return template, lang
        else:
            local_yaml = ka_path / f"{template}.yaml"
            if local_yaml.exists():
                return str(local_yaml), lang
            raise ValueError(
                f"Template '{template}' not found in presets and local file "
                f"'{local_yaml}' does not exist."
            )

    raise ValueError("No template specified in metadata.json")


def validate_config() -> "ConfigManager":
    """Validate configuration.

    Returns:
        ConfigManager instance

    Raises:
        typer.Exit: If configuration is invalid
    """

    config = ConfigManager()
    valid, msg = config.validate()

    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    return config
