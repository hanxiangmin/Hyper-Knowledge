# hk export obsidian

Export a knowledge abstract to an [Obsidian](https://obsidian.md) vault — a folder of Markdown notes linked by `[[wikilinks]]`.

`export` is a command group; `obsidian` is the format. (More formats may be added later.)

---

## Synopsis

```bash
hk export obsidian KA_PATH -o VAULT_PATH [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to the knowledge abstract directory (created by `hk parse`) |

## Options

| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | *(required)* | Output vault directory |
| `--name` | | output dir name | Vault name used for the index note |
| `--no-index` | | off | Skip writing the index / map-of-content note |
| `--force` | `-f` | off | Write into an existing, non-empty directory |

---

## Description

`hk export obsidian` turns an extracted knowledge graph into an Obsidian vault you can open and browse in Obsidian's interactive graph view:

- **Each node → a Markdown note.** The node's fields are stored as YAML front-matter, followed by a `# Title` heading and (when present) a description.
- **Each edge → a `[[wikilink]]`.** Relationships are rendered under the source note's `## Relationships` section, with the relationship label and description.
- **An index note** (named after `--name`) lists every note grouped by type — a map-of-content for the vault.

The exporter is dependency-free and writes plain Markdown, so the result is a normal Obsidian vault: open the folder via **"Open folder as vault"** in Obsidian, or re-ingest it later with [`hk parse`](parse.md).

---

## Examples

### Basic Usage

```bash
# Extract, then export
hk parse tesla.md -t general/biography_graph -o ./tesla_kb/ -l en
hk export obsidian ./tesla_kb/ -o ./tesla_vault/
```

### Custom Vault Name

```bash
hk export obsidian ./tesla_kb/ -o ./tesla_vault/ --name "Tesla Knowledge Base"
```

### Overwrite an Existing Directory

```bash
hk export obsidian ./tesla_kb/ -o ./tesla_vault/ --force
```

### Without the Index Note

```bash
hk export obsidian ./tesla_kb/ -o ./tesla_vault/ --no-index
```

---

## Output Structure

```
tesla_vault/
├── Tesla Knowledge Base.md   # index (grouped by type)
├── Nikola Tesla.md
├── Alternating Current.md
└── ...
```

A note looks like:

```markdown
---
name: Nikola Tesla
type: Person
description: "Serbian-American inventor and electrical engineer"
---

# Nikola Tesla

Serbian-American inventor and electrical engineer

## Relationships

- **developed** → [[Alternating Current]] — Pioneered the AC system.
- **rivaled** → [[Thomas Edison]] — The War of the Currents.
```

Notes:

- Filenames are sanitized for Obsidian/the filesystem; the original id/title is preserved as a front-matter `alias`, and wikilinks use a `[[stem|display]]` form so links always resolve.
- Name collisions are de-duplicated (e.g. `Tesla coil (2)`).

---

## Supported Auto-Types

Export works with the graph family:

| Auto-Type | Export |
|-----------|--------|
| `AutoGraph` | ✓ one note per node, edges as wikilinks |
| `AutoHypergraph` | ✓ N-ary edges link all members |
| `AutoTemporalGraph` | ✓ (inherits `AutoGraph`) |
| `AutoSpatialGraph` | ✓ (inherits `AutoGraph`) |
| `AutoSpatioTemporalGraph` | ✓ (inherits `AutoGraph`) |

Non-graph types (`AutoList`, `AutoSet`, `AutoModel`) are not supported; the command reports a clear error.

---

## Python API

The same capability is available on graph Auto-Types:

```python
ka.export_obsidian("./tesla_vault/", vault_name="Tesla KB", overwrite=True)
```

---

## See Also

- [`hk parse`](parse.md) — Extract knowledge (and ingest an existing vault folder)
- [`hk show`](show.md) — Visualize the graph with OntoSight
- [`hk info`](info.md) — View knowledge abstract statistics
