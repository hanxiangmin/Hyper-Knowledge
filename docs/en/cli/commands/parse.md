# hk parse

Extract knowledge from documents and save to a knowledge abstract.

---

## Synopsis

```bash
hk parse INPUT [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `INPUT` | Input file path, directory, or `-` for stdin |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output directory (required) |
| `--template` | `-t` | Template to use (omit for interactive selection) |
| `--method` | `-m` | Method template (e.g., `light_rag`, `graph_rag`) |
| `--lang` | `-l` | Language: `zh` or `en` (required for knowledge templates) |
| `--force` | `-f` | Force overwrite existing output |
| `--no-index` | — | Skip building search index |

---

## Examples

### Basic Usage

Extract from a single file:

```bash
hk parse document.md -t general/biography_graph -o ./output/ -l en
```

### Interactive Template Selection

Omit `-t` to select from available templates:

```bash
hk parse document.md -o ./output/ -l en

# You'll see:
# Select a template:
#   [1] general/biography_graph
#   [2] general/graph
#   [3] finance/earnings_summary
#   ...
# Enter number or search keyword: 
```

### Process a Directory

Extract from all `.md` and `.txt` files in a directory:

```bash
hk parse ./documents/ -t general/concept_graph -o ./output/ -l en
```

Files are combined in alphabetical order before extraction.

### Using Methods Instead of Templates

Use underlying extraction methods:

```bash
hk parse document.md -m light_rag -o ./output/
```

Methods always use English prompts.

### Force Overwrite

Overwrite existing output directory:

```bash
hk parse document.md -t general/biography_graph -o ./output/ -l en -f
```

### Skip Index Building

Speed up extraction if you don't need search/chat:

```bash
hk parse document.md -t general/biography_graph -o ./output/ -l en --no-index
```

Build index later with `hk build-index`.

### Read from Stdin

```bash
cat document.md | hk parse - -t general/biography_graph -o ./output/ -l en
```

---

## Output Structure

```
./output/
├── data.json           # Extracted knowledge (entities, relations, etc.)
├── metadata.json       # Extraction metadata
│   ├── template        # Template used
│   ├── lang           # Language
│   ├── created_at     # Creation timestamp
│   └── updated_at     # Last update timestamp
└── index/             # Vector search index (if built)
    ├── index.faiss
    └── docstore.json
```

---

## Language Support

Templates support multiple languages:

```bash
# English
hk parse doc.md -t general/biography_graph -l en -o ./output/

# Chinese
hk parse doc.md -t general/biography_graph -l zh -o ./output/
```

Choose the language that matches your document for best results.

---

## Common Use Cases

### Research Paper

```bash
hk parse paper.md -t general/concept_graph -o ./paper_kb/ -l en
```

### Biography

```bash
hk parse biography.md -t general/biography_graph -o ./bio_kb/ -l en
```

### Legal Contract

```bash
hk parse contract.md -t legal/contract_obligation -o ./contract_kb/ -l en
```

### Financial Report

```bash
hk parse earnings.md -t finance/earnings_summary -o ./finance_kb/ -l en
```

---

## Error Handling

### "Output directory already exists"

The output directory exists and is not empty. Solutions:

1. Use `-f` to force overwrite
2. Choose a different output path
3. Remove the existing directory first

### "Template not found"

The specified template doesn't exist. Solutions:

1. List available templates: `hk list template`
2. Use interactive selection (omit `-t`)
3. Check template path spelling

### "Language is required"

Knowledge templates require a language flag. Methods don't:

```bash
# Template - requires -l
hk parse doc.md -t general/biography_graph -o ./out/ -l en

# Method - no -l needed
hk parse doc.md -m light_rag -o ./out/
```

---

## Best Practices

1. **Choose the right template** — Match your document type
2. **Use correct language** — Improves extraction quality
3. **Organize outputs** — Use descriptive directory names
4. **Skip index during batch** — Use `--no-index`, build once at the end

---

## See Also

- [`hk feed`](feed.md) — Add documents incrementally
- [`hk build-index`](build-index.md) — Build search index
- [`hk list`](list.md) — List available templates
- [Template Library](../../templates/index.md)
