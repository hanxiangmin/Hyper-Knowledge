# Command recipes

Complete [command-line or chat installation](install.md) first. Paths below are relative to the terminal's current directory; supply or download the example inputs before using them.

## Make `hk` available in this terminal { #prepare-shell }

`hk` is an installed shortcut, not a built-in command. Choose the case matching your installation environment.

**Anaconda / Miniconda users:** open a Conda terminal and activate the installation environment, substituting its name if different:

```bash
conda activate hyper-knowledge
python -c "import sys; print(sys.executable)"
hk --help
```

Without manual activation, replace each leading `hk` with `conda run -n hyper-knowledge python -m hyperknowledge`.

**Windows users who created the tutorial's venv:** add its command directory to **this PowerShell window's** PATH without changing execution policy. This is not a Conda directory:

```powershell
$hkScripts = Join-Path $env:USERPROFILE ".venvs\hyper-knowledge\Scripts"
if (-not (Test-Path -LiteralPath (Join-Path $hkScripts "hk.exe"))) {
    throw "Hyper-Knowledge is not installed at this path. Follow the installation guide first."
}
$env:PATH = "$hkScripts;$env:PATH"
hk --help
```

**macOS / Linux users who created the tutorial's venv:**

```bash
source "$HOME/.venvs/hyper-knowledge/bin/activate"
hk --help
```

**Other existing environments:** activate as usual and run `python -m hyperknowledge --help`. Continue after help appears, and select the environment again in a new terminal. If `hk` is missing, substitute `python -m hyperknowledge` in the selected environment. [Environment and full-path instructions](install.md#reopen-shell)

## Document → KA → Bundle → workbench

After [configuring a chat model](python.md):

```bash
hk parse notes.md -t general/hypergraph -l en --no-index -o output/ka
hk bundle export output/ka -o output/bundle
hk visualize output/bundle -o output/workbench.html --no-open
```

`--no-index` skips indexing and does not require an embedder. Parsing still uses your model service.

## Structured input, no model key

The same [fixture](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/python) is used by the Python and Notebook examples:

```bash
hk bundle import examples/python/graph.json --source notes.md=examples/python/notes.md -o output/cli-bundle --json
hk bundle validate output/cli-bundle --quality showcase --json
hk visualize output/cli-bundle -o output/cli-workbench.html --no-open --json
```

`bundle import` shares implementation with `import_graph()`. Repeat `--source NAME=PATH` for multiple explicitly allowed source files; quote arguments containing spaces.
`--quality` is standard by default; showcase applies stricter evidence checks.
`--force` is opt-in and preserves a sibling backup; use a new output directory normally.

## Batch document processing

Bash:

```bash
for file in notes/*.md; do
  name="$(basename "$file" .md)"
  hk parse "$file" -t general/hypergraph -l en --no-index -o "output/$name/ka" &&
  hk bundle export "output/$name/ka" -o "output/$name/bundle" &&
  hk visualize "output/$name/bundle" -o "output/$name/workbench.html" --no-open || exit 1
done
```

PowerShell:

```powershell
Get-ChildItem notes -Filter *.md | ForEach-Object {
  $target = Join-Path output $_.BaseName
  hk parse $_.FullName -t general/hypergraph -l en --no-index -o "$target/ka"
  if ($LASTEXITCODE) { throw "Parse failed" }
  hk bundle export "$target/ka" -o "$target/bundle"
  if ($LASTEXITCODE) { throw "Export failed" }
  hk visualize "$target/bundle" -o "$target/workbench.html" --no-open
  if ($LASTEXITCODE) { throw "Render failed" }
}
```

Each document keeps its own output and provenance. These loops stop on failure; they are not an implicit graph merge.

## Machine calls and error handling

Import/export/validate/visualize support `--json`; it is not a universal CLI flag.
Import success returns `ok=true`, paths, counts and warnings with exit code 0.
Import failures return `ok=false`, error text and exit code 1; argument parsing errors use the CLI's nonzero usage code.
Validation callers must check the process exit code and receipt status.
Dependency logs can appear on stderr; parse JSON from stdout, not the combined stream.

## Optional checks and help

```bash
hk skill doctor --platform codex --scope user --deep --json
hk bundle import --help
hk parse --help
hk visualize --help
```

Doctor is optional installation diagnosis. Match its platform/scope to your installation.
