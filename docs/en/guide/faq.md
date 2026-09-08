# Questions and troubleshooting

## Do I need my own server?

The local runtime and exported workbench need no website server. The default Skill route uses the current agent's model service to understand the document. Independent Python/CLI extraction uses a separately configured model; structured import and rendering need none. [Choose a route](agents.md).

This GitHub Pages site documents and demonstrates the project. It does not offer document upload or hosted parsing.

## Do I need to parse again if I already have a bundle?

No. Validate it, then render it. Changing views, inspecting memberships, moving nodes, and reframing the graph do not require another extraction. [Bundle command recipes](commands.md)

## Why is hk unavailable after installing the Skill?

Copying Skill files alone does not install the Python runtime. Even an installed runtime may have no `hk` command in a terminal that is not using its environment. Check help through the explicit Python path instead of repeating a missing command.

**Conda users:** select the environment without guessing its Python path. Replace the environment name if different:

```bash
conda run -n hyper-knowledge python -m hyperknowledge --help
```

**venv users**, Windows PowerShell after following the tutorial:

```powershell
& "$env:USERPROFILE\.venvs\hyper-knowledge\Scripts\python.exe" -m hyperknowledge --help
```

macOS / Linux after following the venv tutorial:

```bash
"$HOME/.venvs/hyper-knowledge/bin/python" -m hyperknowledge --help
```

For other existing environments, activate as usual and run `python -m hyperknowledge --help`. If help appears, you do not need to reinstall; [prepare the shortcut in this terminal](commands.md#prepare-shell). If the module or path is missing, follow the [complete setup](install.md). Use [optional diagnostics](install.md#installation-check) for persistent failures; do not hide problems by disabling checks or editing paths arbitrarily.

## Can I pass a PDF or scan directly?

The current text entry point handles `.txt` and `.md`. Convert PDF, Word, and image inputs first, preserving paragraphs and source locations. Review OCR errors before extraction because they can affect both entities and relationships.

## Why review a relationship that already has evidence?

Source coverage means that a reference record exists. It does not establish that the passage supports the entire assertion, or that the input itself is reliable. Structural validity, traceability, and semantic correctness require different checks. [Read more](artifacts.md)

## What if dates and places are mixed together?

Revisit event scope. Represent separate episodes as separate hyperedges sharing a person node; distinguish start and end roles when multiple times really belong to one event. Moving circles cannot repair ambiguous modeling. [Modeling examples](modeling.md)

## Should I hide nodes when the graph becomes dense?

Use the matrix for membership lookup, then focus one node or hyperedge in incidence. Fading or temporarily hiding other elements does not remove data. Enclosure is useful for shared structure; it need not handle every item-by-item check.

## How should I report a problem?

Include the command, version, error receipt, and a minimal reproducible input. Use de-identified material for private documents. For layout issues, include the view, selected node or hyperedge, and window size. Remove credentials and unrelated personal information first.

[Open an issue](https://github.com/hanxiangmin/Hyper-Knowledge/issues)
