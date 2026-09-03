"""CLI entry point for Hyper-Knowledge."""

import hashlib
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from hyperknowledge.utils.logging import configure_logging, get_logger
from hyperknowledge.utils.template_engine import Gallery, Template

from .commands import (
    benchmark_app,
    bundle_app,
    config_app,
    list_app,
    skill_app,
)
from .config import (
    load_ka_metadata,
)
from .utils import (
    LOGO,
    get_template_from_ka,
    read_input,
    validate_config,
    validate_ka_path,
    validate_ka_with_data,
    validate_ka_with_index,
)

console = Console()
logger = get_logger("hk")


def _source_record(path: Path, *, relative_to: Path | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    display_path = path.relative_to(relative_to) if relative_to else path.name
    return {
        "path": display_path.as_posix(),
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


app = typer.Typer(
    name="hk",
    help="Hyper-Knowledge CLI - Higher-order knowledge graph extraction and visualization",
    add_completion=False,
    invoke_without_command=True,
)

app.add_typer(list_app, name="list")
app.add_typer(config_app, name="config")
app.add_typer(skill_app, name="skill")
app.add_typer(bundle_app, name="bundle")
app.add_typer(benchmark_app, name="benchmark")


@app.command(name="visualize")
def visualize(
    bundle_path: Path = typer.Argument(..., help="hk.bundle/v1 directory"),
    output: Path = typer.Option(
        Path("hyperknowledge-view.html"), "--output", "-o", help="HTML output path"
    ),
    view: str = typer.Option(
        "contour",
        help="Initial view: contour, incidence, graph, or hypergraph",
    ),
    quality: str = typer.Option(
        "standard", help="Bundle validation profile: standard or showcase"
    ),
    open_browser: bool = typer.Option(
        False, "--open/--no-open", help="Open the exported page in the browser"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
):
    """Create a fully offline higher-order knowledge graph page."""
    import json
    import webbrowser

    from hyperknowledge.visualization import render_bundle_html

    try:
        result = render_bundle_html(bundle_path, output, view=view, quality=quality)
    except (OSError, ValueError) as exc:
        if as_json:
            typer.echo(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)
    if open_browser:
        webbrowser.open(output.resolve().as_uri())
    payload = {"ok": True, **result}
    if as_json:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]Offline view exported:[/green] {output.resolve()}")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information",
        is_eager=True,
    ),
):
    # Configure logging after all imports complete so dependency loggers
    # (e.g. ontosight) don't override our level settings.
    # Log level is controlled solely by the HYPER_KNOWLEDGE_LOG_LEVEL env var.
    configure_logging()
    if version:
        from . import __version__

        console.print(f"[bold]Hyper-Knowledge CLI[/bold] version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        from . import __version__

        console.print()
        console.print(Text(LOGO, style="bold cyan"))

        title_text = Text("HYPER-KNOWLEDGE", style="bold cyan")
        version_text = Text(f"v{__version__}", style="dim white")
        desc_text = Text(
            "Transform document into knowledge-abstract", style="dim", no_wrap=True
        )

        header = Table(box=None, show_header=False, pad_edge=False)
        header.add_column(no_wrap=True)
        header.add_column(style="dim white", no_wrap=True)
        header.add_row(title_text, version_text)

        console.print(header)
        console.print(desc_text)
        console.print()

        from rich.rule import Rule

        console.print(Rule(style="cyan dim"))
        console.print()

        from rich.panel import Panel

        def make_section(title: str, commands: list[tuple[str, str]]) -> Panel:
            table = Table(box=None, show_header=False, pad_edge=False)
            table.add_column(style="green bold", no_wrap=True)
            table.add_column(style="white", no_wrap=True)
            for cmd, desc in commands:
                table.add_row(f"  {cmd}", desc)
            return Panel(
                table,
                title=f"[bold cyan]{title}[/]",
                border_style="cyan dim",
                padding=(0, 1),
                title_align="center",
                width=80,
            )

        sections = [
            make_section(
                "🚀 Getting Started",
                [
                    ("hk list template", "List available templates"),
                    ("hk list method", "List extraction methods"),
                    ("hk config --help", "Manage LLM/Embedder config"),
                ],
            ),
            make_section(
                "✨ Create Knowledge Abstract (KA)",
                [
                    (
                        "hk parse <input_document> -o <ka_path>",
                        "Extract KA from document",
                    ),
                    (
                        "hk feed <ka_path> <input_document>",
                        "Add document to existing KA",
                    ),
                    ("hk build-index <ka_path>", "Build semantic search index"),
                ],
            ),
            make_section(
                "🔍 Explore Knowledge Abstract (KA)",
                [
                    ("hk info <ka_path>", "View KA info & stats"),
                    ("hk talk <ka_path> [-i]", "Chat with KA"),
                    ("hk search <ka_path> <query>", "Semantic search"),
                    ("hk show <ka_path>", "Visualize KA"),
                    (
                        "hk export obsidian <ka_path> -o <vault>",
                        "Export to Obsidian vault",
                    ),
                ],
            ),
            make_section(
                "🤖 Codex Skill & Evidence Views",
                [
                    ("hk skill install", "Install the bundled Codex skill"),
                    ("hk bundle export <ka> -o <dir>", "Export a stable bundle"),
                    (
                        "hk visualize <bundle> -o <html>",
                        "Inspect higher-order knowledge graph views",
                    ),
                    (
                        "hk benchmark datasets <paths>",
                        "Preflight every bundled dataset",
                    ),
                ],
            ),
        ]

        for section in sections:
            console.print(section)
        console.print()
        console.print(Rule(style="cyan dim"))
        console.print()

        hint_text = Text("💡 Tip: Run ", style="dim")
        hint_text.append("hk --help", style="bold cyan")
        hint_text.append(" for detailed documentation", style="dim")
        console.print(hint_text)
        console.print()
        raise typer.Exit()


def select_template_interactive() -> str | None:
    """Interactive template selection when user doesn't specify one."""
    templates = Gallery.list()

    if not templates:
        console.print("[yellow]No templates available.[/yellow]")
        return None

    template_list = list(templates.items())

    console.print()
    console.print("[bold cyan]Select a template:[/bold cyan]")
    console.print()

    for i, (path, cfg) in enumerate(template_list, 1):
        desc = cfg.description if cfg.description else ""
        if isinstance(desc, dict):
            desc = desc.get("zh", desc.get("en", ""))
        console.print(f"  [{i}] {path}")
        if desc:
            console.print(f"      {desc}")

    console.print()

    while True:
        choice = Prompt.ask(
            "Enter number or search keyword",
            default="1",
            show_default=True,
        )

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(template_list):
                return template_list[idx][0]
            else:
                console.print(
                    f"[red]Invalid number. Please choose 1-{len(template_list)}[/red]"
                )
        else:
            query_lower = choice.lower()
            matches = [
                (i, p, c)
                for i, (p, c) in enumerate(template_list)
                if query_lower in p.lower()
                or (c.description and query_lower in str(c.description).lower())
            ]

            if len(matches) == 1:
                return matches[0][1]
            elif len(matches) > 1:
                console.print(f"[yellow]Found {len(matches)} matches:[/yellow]")
                for i, path, cfg in matches:
                    console.print(f"  [{i + 1}] {path}")
                continue
            else:
                console.print("[yellow]No matches found. Try another keyword.[/yellow]")


@app.command(name="parse")
def parse(
    input: str = typer.Argument(
        ..., help="Input file path, directory, or '-' for stdin"
    ),
    output: str = typer.Option(..., "--output", "-o", help="Output directory"),
    template: str | None = typer.Option(
        None, "--template", "-t", help="Template (omit for interactive selection)"
    ),
    method: str | None = typer.Option(
        None, "--method", "-m", help="Method template (e.g., light_rag, hyper_rag)"
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Language (zh/en). Required for knowledge templates, optional for methods (default: en)",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
    no_index: bool = typer.Option(
        False, "--no-index", help="Skip building search index"
    ),
):
    """Extract knowledge from text to a new directory."""
    logger.info(
        "command=parse input=%s output=%s template=%s lang=%s",
        input,
        output,
        template or "auto",
        lang or "auto",
    )
    validate_config()
    logger.info("stage=config_validated")

    if method:
        template = f"method/{method}"
    elif template is None:
        template = select_template_interactive()
        if template is None:
            console.print("[red]No template selected. Exiting.[/red]")
            raise typer.Exit(1)

    is_method_template = template.startswith("method/")

    if is_method_template:
        if lang is not None:
            console.print(
                "[dim]Note: Method templates use English prompts. --lang parameter is ignored.[/dim]"
            )
        lang = "en"
    elif lang is None:
        console.print(
            "[red]Error:[/red] --lang is required for knowledge templates. Use --lang en or --lang zh."
        )
        raise typer.Exit(1)

    output_path = Path(output)

    if output_path.exists() and not force:
        if any(output_path.iterdir()):
            console.print(
                "[red]Error:[/red] Output directory already exists and is not empty. Use --force to overwrite."
            )
            raise typer.Exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[blue]Input:[/blue] {input}")
    console.print(f"[blue]Output:[/blue] {output}")
    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print(f"[blue]Build Index:[/blue] {'No' if no_index else 'Yes'}")
    console.print()

    try:
        template_config = Template.get(template)
        if template_config is None:
            raise ValueError(f"Template '{template}' not found")
        console.print(f"[green]Template resolved:[/green] {template_config.name}")
        logger.info("stage=template_resolved template=%s", template_config.name)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    input_path = Path(input)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating template instance...", total=None)

        ka = Template.create(template, lang)
        logger.info("stage=template_created")

        if input_path.is_dir():
            progress.update(task, description="Processing directory...")
            text_files = sorted(
                [
                    path
                    for path in input_path.rglob("*")
                    if path.is_file() and path.suffix.lower() in {".txt", ".md"}
                ],
                key=lambda path: path.relative_to(input_path).as_posix(),
            )
            if not text_files:
                console.print(
                    f"[red]Error:[/red] No .txt or .md files found in {input}"
                )
                raise typer.Exit(1)

            all_text = []
            source_records = []
            for file_path in text_files:
                text = read_input(str(file_path))
                relative_path = file_path.relative_to(input_path).as_posix()
                all_text.append(f"[SOURCE: {relative_path}]\n{text}")
                source_records.append(_source_record(file_path, relative_to=input_path))
                console.print(f"[dim]Loaded {file_path.name}: {len(text)} chars[/dim]")

            combined_text = "\n\n".join(all_text)
            console.print(f"[dim]Total input: {len(combined_text)} characters[/dim]")

            progress.update(task, description="Extracting knowledge...")
            logger.debug("stage=feed_text_invoked")
            ka.feed_text(combined_text)
            ka.metadata["sources"] = source_records
            logger.info("stage=knowledge_extracted chars=%d", len(combined_text))
        else:
            progress.update(task, description="Reading input...")
            text = read_input(input)
            console.print(f"[dim]Input text: {len(text)} characters[/dim]")

            progress.update(task, description="Extracting knowledge...")
            logger.debug("stage=feed_text_invoked")
            ka.feed_text(text)
            if input == "-":
                ka.metadata["sources"] = [
                    {
                        "path": "stdin",
                        "size_bytes": len(text.encode("utf-8")),
                        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    }
                ]
            else:
                ka.metadata["sources"] = [_source_record(input_path)]
            logger.info("stage=knowledge_extracted chars=%d", len(text))

        progress.update(task, description="Saving data...")

        template_path = Path(template).expanduser()
        if template_path.is_file():
            import shutil

            filename = template_path.name
            shutil.copy2(template_path, output_path / filename)
            console.print(
                f"[dim]Custom template '{filename}' saved to KA directory[/dim]"
            )

        ka.dump(output_path)
        logger.info("stage=data_saved output=%s", output_path)

        if not no_index:
            progress.update(task, description="Building search index...")
            ka.build_index()
            console.print("[dim]Index built successfully[/dim]")
            logger.info("stage=index_built")
            progress.update(task, description="Saving index...")
            ka.dump(output_path)
            logger.info("stage=index_saved")

    console.print()
    console.print(
        f"[bold green]Success![/bold green] Knowledge extracted to {output_path}"
    )
    console.print()
    if no_index:
        console.print("[dim]Note: Index was not built.[/dim]")
        console.print(
            f"[dim]  hk build-index {output}       # Build index to enable search/talk[/dim]"
        )
        console.print(
            f"[dim]  hk feed {output} <new_document>  # Append more documents[/dim]"
        )
    else:
        console.print("[dim]What's next?[/dim]")
        console.print(
            f"[dim]  hk show {output}                    # Visualize knowledge graph[/dim]"
        )
        console.print(
            f"[dim]  hk feed {output} <new_document>     # Append more documents[/dim]"
        )
        console.print(
            f'[dim]  hk search {output} "keyword"        # Semantic search[/dim]'
        )
        console.print(
            f"[dim]  hk talk {output} -i                 # Interactive chat[/dim]"
        )
        console.print(
            f'[dim]  hk talk {output} -q "your question" # Single query[/dim]'
        )


@app.command(name="show")
def show(ka_path: str = typer.Argument(..., help="Knowledge Abstract directory")):
    """Visualize Knowledge Abstract using OntoSight."""
    logger.info("command=show ka_path=%s", ka_path)
    path = validate_ka_with_data(ka_path)

    template, lang = get_template_from_ka(path)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    validate_config()

    with console.status("[bold blue]Loading Knowledge Abstract..."):
        try:
            ka = Template.create(template, lang)
            ka.load(path)

        except Exception as e:
            console.print(f"[red]Error loading Knowledge Abstract:[/red] {e}")
            raise typer.Exit(1)

    console.print("[bold blue]Visualizing with OntoSight...[/bold blue]")
    logger.info("stage=visualizing")

    try:
        ka.show()
        logger.info("stage=visualization_complete")
    except Exception as e:
        console.print(f"[red]Error during visualization:[/red] {e}")
        raise typer.Exit(1)

    console.print()
    console.print("[dim]Continue exploring:[/dim]")
    console.print(
        f'[dim]  hk search {ka_path} "keyword"  # Search specific content[/dim]'
    )
    console.print(f"[dim]  hk talk {ka_path} -i           # Interactive chat[/dim]")


export_app = typer.Typer(
    name="export",
    help="Export a Knowledge Abstract to other formats",
    no_args_is_help=True,
)


@export_app.command(name="obsidian")
def export_obsidian_cmd(
    ka_path: str = typer.Argument(..., help="Knowledge Abstract directory"),
    output: str = typer.Option(..., "--output", "-o", help="Output vault directory"),
    name: str | None = typer.Option(
        None, "--name", help="Vault name used for the index note"
    ),
    no_index: bool = typer.Option(
        False, "--no-index", help="Skip writing the index/map-of-content note"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Write into an existing, non-empty directory"
    ),
):
    """Export a Knowledge Abstract to an Obsidian vault (Markdown + wikilinks)."""
    logger.info("command=export-obsidian ka_path=%s output=%s", ka_path, output)

    path = validate_ka_with_data(ka_path)
    template, lang = get_template_from_ka(path)

    output_path = Path(output)
    if output_path.exists() and any(output_path.iterdir()) and not force:
        console.print(
            "[red]Error:[/red] Output directory already exists and is not empty. "
            "Use --force to write into it."
        )
        raise typer.Exit(1)

    console.print(f"[blue]Knowledge Abstract:[/blue] {ka_path}")
    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Output vault:[/blue] {output}")
    console.print()

    validate_config()

    vault_name = name or output_path.name or "Knowledge Vault"

    with console.status("[bold blue]Loading Knowledge Abstract..."):
        try:
            ka = Template.create(template, lang)
            ka.load(path)
        except Exception as e:
            console.print(f"[red]Error loading Knowledge Abstract:[/red] {e}")
            raise typer.Exit(1)

    if not hasattr(ka, "export_obsidian"):
        console.print(
            "[red]Error:[/red] Obsidian export is only supported for graph-type "
            "Knowledge Abstracts (graph, hypergraph, temporal/spatial graphs)."
        )
        raise typer.Exit(1)

    with console.status("[bold blue]Exporting to Obsidian vault..."):
        try:
            ka.export_obsidian(
                output_path,
                vault_name=vault_name,
                include_index=not no_index,
                overwrite=force,
            )
        except Exception as e:
            console.print(f"[red]Error during export:[/red] {e}")
            raise typer.Exit(1)

    note_count = len(list(output_path.glob("*.md")))
    console.print()
    console.print(
        f"[bold green]Success![/bold green] Exported {note_count} notes to {output_path}"
    )
    console.print()
    console.print("[dim]Open the folder as a vault in Obsidian to explore it.[/dim]")


app.add_typer(export_app, name="export")


@app.command(name="info")
def info(ka_path: str = typer.Argument(..., help="Knowledge Abstract directory")):
    """View Knowledge Abstract information and statistics."""
    logger.info("command=info ka_path=%s", ka_path)
    import json

    path = validate_ka_with_data(ka_path)

    metadata = load_ka_metadata(path)

    data_file = path / "data.json"
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        node_count = len(data.get("nodes", data.get("entities", [])))
        edge_count = len(data.get("edges", data.get("relations", [])))
    elif isinstance(data, list):
        node_count = len(data)
        edge_count = 0
    else:
        node_count = 0
        edge_count = 0

    index_exists = (path / "index").exists() and any((path / "index").iterdir())

    table = Table(title="Knowledge Abstract Info", show_header=False, box=None)
    table.add_column("Key", style="cyan", width=15)
    table.add_column("Value", style="green")

    table.add_row("Path", str(path))

    if metadata:
        table.add_row("Template", metadata.get("template", "unknown"))
        table.add_row("Language", metadata.get("lang", "unknown"))
        table.add_row("Created", metadata.get("created_at", "unknown"))
        table.add_row("Updated", metadata.get("updated_at", "unknown"))
    else:
        table.add_row("Template", "[yellow]unknown[/yellow]")
        table.add_row("Language", "[yellow]unknown[/yellow]")

    table.add_row("Nodes", str(node_count))
    table.add_row("Edges", str(edge_count))
    table.add_row(
        "Index", "[green]Built[/green]" if index_exists else "[red]Not Built[/red]"
    )

    console.print(table)


@app.command(name="search")
def search(
    ka_path: str = typer.Argument(..., help="Knowledge Abstract directory"),
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(3, "--top-k", "-n", help="Number of results"),
):
    """Semantic search in Knowledge Abstract."""
    logger.info("command=search ka_path=%s query=%s top_k=%d", ka_path, query, top_k)
    import json

    validate_config()

    path = validate_ka_with_index(ka_path)
    template, lang = get_template_from_ka(path)

    console.print(f"[blue]Knowledge Abstract:[/blue] {ka_path}")
    console.print(f"[blue]Query:[/blue] {query}")
    console.print(f"[blue]Top K:[/blue] {top_k}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching...", total=None)

        try:
            ka = Template.create(template, lang)

            progress.update(task, description="Loading Knowledge Abstract...")
            ka.load(path)

            progress.update(task, description="Searching...")
            results = ka.search(query, top_k=top_k)
            logger.info("stage=search_complete results=%d", len(results))

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print()
    if not results:
        console.print("[yellow]No results found.[/yellow]")
    else:
        console.print(f"[bold green]Found {len(results)} result(s):[/bold green]")
        console.print()

        for i, result in enumerate(results, 1):
            console.print(f"[bold cyan]Result {i}:[/bold cyan]")
            if hasattr(result, "model_dump"):
                console.print_json(
                    json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
                )
            elif hasattr(result, "dict"):
                console.print_json(
                    json.dumps(result.dict(), indent=2, ensure_ascii=False)
                )
            else:
                console.print(str(result))
            console.print()

    console.print("[dim]Continue:[/dim]")
    console.print(
        f'[dim]  hk talk {ka_path} -q "question about results"  # Deep dive[/dim]'
    )
    console.print(
        f"[dim]  hk talk {ka_path} -i                           # Interactive mode[/dim]"
    )
    console.print(
        f"[dim]  hk show {ka_path}                              # Visualize[/dim]"
    )


def chat_loop(ka, ka_path: str):
    """Interactive chat loop."""
    console.print(
        "\n[bold green]Entering interactive mode. Type 'exit' or 'quit' to stop.[/bold green]\n"
    )
    while True:
        try:
            query = console.input("[bold cyan]>[/bold cyan] ")
            if query.lower() in ["exit", "quit", "q"]:
                console.print("\n[dim]Goodbye![/dim]")
                console.print()
                console.print("[dim]Other useful commands:[/dim]")
                console.print(
                    f"[dim]  hk show {ka_path}              # Visualize[/dim]"
                )
                console.print(f'[dim]  hk search {ka_path} "keyword"  # Search[/dim]')
                console.print(
                    f"[dim]  hk info {ka_path}              # View info[/dim]"
                )
                break
            if not query.strip():
                continue
            response = ka.chat(query)
            console.print()
            console.print(response.content)
            console.print()
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            console.print()
            console.print("[dim]Other useful commands:[/dim]")
            console.print(f"[dim]  hk show {ka_path}              # Visualize[/dim]")
            console.print(f'[dim]  hk search {ka_path} "keyword"  # Search[/dim]')
            console.print(f"[dim]  hk info {ka_path}              # View info[/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


@app.command(name="talk")
def talk(
    ka_path: str = typer.Argument(..., help="Knowledge Abstract directory"),
    query: str | None = typer.Option(None, "--query", "-q", help="Question to ask"),
    top_k: int = typer.Option(3, "--top-k", "-n", help="Number of context items"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode"
    ),
):
    """Chat with Knowledge Abstract."""
    logger.info(
        "command=talk ka_path=%s query=%s interactive=%s",
        ka_path,
        query or "loop",
        interactive,
    )
    validate_config()

    path = validate_ka_with_index(ka_path)
    template, lang = get_template_from_ka(path)

    if interactive:
        console.print(f"[blue]Knowledge Abstract:[/blue] {ka_path}")
        console.print(f"[blue]Template:[/blue] {template}")
        console.print(f"[blue]Top K:[/blue] {top_k}")
        console.print()
    elif query is None:
        console.print(
            "[red]Error:[/red] Please provide a query or use --interactive mode"
        )
        raise typer.Exit(1)
    else:
        console.print(f"[blue]Query:[/blue] {query}")
        console.print(f"[blue]Knowledge Abstract:[/blue] {ka_path}")
        console.print(f"[blue]Top K:[/blue] {top_k}")
        console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading...", total=None)

        try:
            ka = Template.create(template, lang)

            progress.update(task, description="Loading Knowledge Abstract...")
            ka.load(path)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if interactive:
        chat_loop(ka, ka_path)
    else:
        with console.status("[bold blue]Thinking..."):
            try:
                response = ka.chat(query, top_k=top_k)
                console.print(response.content)

                if response.additional_kwargs.get("retrieved_items"):
                    console.print()
                    console.print("[dim]Retrieved context:[/dim]")
                    items = response.additional_kwargs["retrieved_items"]
                    for i, item in enumerate(items, 1):
                        console.print(f"[dim]{i}. {str(item)[:100]}...[/dim]")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

        console.print()
        console.print("[dim]Continue:[/dim]")
        console.print(
            f"[dim]  hk talk {ka_path} -i           # Enter interactive mode[/dim]"
        )
        console.print(f'[dim]  hk search {ka_path} "keyword"  # Search more[/dim]')
        console.print(f"[dim]  hk show {ka_path}              # Visualize[/dim]")


@app.command(name="feed")
def feed(
    ka_path: str = typer.Argument(..., help="Knowledge Abstract directory"),
    input: str = typer.Argument(..., help="Input file path or '-' for stdin"),
    template: str | None = typer.Option(None, "--template", "-t", help="Template"),
    lang: str | None = typer.Option(None, "--lang", "-l", help="Language"),
):
    """Append knowledge to an existing Knowledge Abstract."""
    logger.info("command=feed ka_path=%s input=%s", ka_path, input)
    validate_config()

    output_path = validate_ka_path(ka_path)

    metadata = load_ka_metadata(output_path)
    if not metadata:
        console.print(
            f"[red]Error:[/red] Not a valid Knowledge Abstract directory: {ka_path}"
        )
        raise typer.Exit(1)

    if template is None:
        template = metadata.get("template", "general/graph")
    if lang is None:
        lang = metadata.get("lang", "zh")

    console.print(f"[blue]Knowledge Abstract:[/blue] {ka_path}")
    console.print(f"[blue]Input:[/blue] {input}")
    console.print(f"[blue]Template:[/blue] {template} (from metadata)")
    console.print(f"[blue]Language:[/blue] {lang} (from metadata)")
    console.print()

    try:
        ka = Template.create(template, lang)
        console.print(f"[green]Template loaded:[/green] {template}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading existing knowledge...", total=None)

        ka.load(output_path)

        progress.update(task, description="Reading input...")
        text = read_input(input)
        console.print(f"[dim]Input text: {len(text)} characters[/dim]")

        progress.update(task, description="Appending knowledge...")
        logger.debug("stage=feed_text_invoked")
        ka.feed_text(text)
        logger.info("stage=knowledge_appended chars=%d", len(text))

        progress.update(task, description="Saving data...")
        ka.dump(output_path)
        logger.info("stage=data_saved")

    console.print()
    console.print(
        f"[bold green]Success![/bold green] Knowledge appended to {output_path}"
    )
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print(f"[dim]  hk show {ka_path}              # Visualize[/dim]")
    console.print(
        f"[dim]  hk build-index {ka_path}       # Rebuild index (if needed)[/dim]"
    )


@app.command(name="build-index")
def build_index(
    ka_path: str = typer.Argument(..., help="Knowledge Abstract directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild"),
):
    """Build vector index for Knowledge Abstract."""
    logger.info("command=build-index ka_path=%s force=%s", ka_path, force)
    validate_config()

    path = validate_ka_with_data(ka_path)

    index_dir = path / "index"
    if index_dir.exists() and any(index_dir.iterdir()) and not force:
        console.print(
            "[yellow]Warning:[/yellow] Index already exists. Use --force to rebuild."
        )
        console.print(f"[dim]Index location: {index_dir}[/dim]")
        raise typer.Exit(0)

    template, lang = get_template_from_ka(path)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing...", total=None)

        try:
            ka = Template.create(template, lang)

            progress.update(task, description="Loading Knowledge Abstract...")
            ka.load(path)

            if force:
                console.print("[dim]Force rebuild: clearing existing index...[/dim]")
                ka.clear_index()

            progress.update(task, description="Building index...")
            ka.build_index()
            logger.info("stage=index_built")

            progress.update(task, description="Saving index...")
            ka.dump(path)
            logger.info("stage=index_saved")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print()
    console.print(f"[bold green]Success![/bold green] Index built for {ka_path}")
    console.print()
    console.print("[dim]Now you can:[/dim]")
    console.print(f'[dim]  hk search {ka_path} "keyword"  # Semantic search[/dim]')
    console.print(f"[dim]  hk talk {ka_path} -i           # Interactive chat[/dim]")


@app.command(name="clean")
def clean(
    ka_path: str = typer.Argument(..., help="Knowledge Abstract directory"),
    all_: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Remove the ENTIRE Knowledge Abstract (data, metadata, and index)",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt"),
):
    """Clean a Knowledge Abstract: remove its search index, or the whole KA with --all."""
    import shutil

    logger.info("command=clean ka_path=%s all=%s", ka_path, all_)

    # validate_ka_with_data ensures the target really is a KA (has data.json),
    # so --all never rmtree's an arbitrary mistyped directory.
    path = validate_ka_with_data(ka_path)

    if all_:
        target = path
        what = f"the ENTIRE Knowledge Abstract '{path}' (data, metadata, index)"
    else:
        target = path / "index"
        if not target.exists() or not any(target.iterdir()):
            console.print("[yellow]Nothing to clean:[/yellow] no index found.")
            console.print(
                f"[dim]Tip: use --all to remove the whole KA at {path}.[/dim]"
            )
            raise typer.Exit(0)
        what = f"the search index of '{path}'"

    console.print(f"[yellow]This will permanently delete[/yellow] {what}.")
    if not yes and not typer.confirm("Are you sure?"):
        console.print("[dim]Aborted. Nothing was deleted.[/dim]")
        raise typer.Exit(0)

    try:
        shutil.rmtree(target)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to delete {target}: {e}")
        raise typer.Exit(1)

    console.print(f"[bold green]Cleaned![/bold green] Removed {target}")
    if not all_:
        console.print(f"[dim]Rebuild it with: hk build-index {ka_path}[/dim]")
