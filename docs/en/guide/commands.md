# Command recipes

Use the command that fits your task; you do not need to learn an entire SDK first. Complete [installation](install.md) and activate the environment. Relative paths start at your current working directory.

## Check the Skill's runtime connection

```bash
hk --version
hk skill doctor --scope user --deep --json
```

For a project-scoped installation:

```bash
hk skill doctor --scope project --project-root . --deep --json
```

The doctor checks installation and runtime health, not a model's understanding of your document.

## Try a synthetic demo without a model

```bash
hk skill demo -o output/local-demo --json
```

The receipt identifies the bundle, validation, and workbench outputs. Preserve previous results and use a new directory for another run.

## Start from a document

```bash
hk config init
hk list template
hk parse notes.md -t general/hypergraph -l en --no-index -o output/notes-ka
hk bundle export output/notes-ka -o output/notes-bundle --json
```

Extraction requires a working model configuration. A template constrains the output structure but does not guarantee correct entities, roles, or event boundaries. Keep credentials out of commits and public command screenshots.

## Start from an existing bundle

```bash
hk bundle validate output/notes-bundle --quality showcase --json
hk visualize output/notes-bundle -o output/notes-workbench.html --view contour --no-open --json
```

Use `--view incidence` instead of `--view contour` to open the incidence view initially. Access the matrix through its separate button in the workbench.

## Check options instead of guessing

```bash
hk parse --help
hk bundle export --help
hk bundle validate --help
hk visualize --help
hk skill --help
```

`--json` returns a machine-readable receipt for commands that support it; it is not a universal option. UI actions, command options, and raw data fields are not interchangeable names.
