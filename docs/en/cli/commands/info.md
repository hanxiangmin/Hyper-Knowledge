# hk info

Display information and statistics about a knowledge abstract.

---

## Synopsis

```bash
hk info KA_PATH
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge abstract directory |

---

## Description

Shows metadata and statistics for a knowledge abstract:

- **Path** — Location of the knowledge abstract
- **Template** — Template used for extraction
- **Language** — Language code (en/zh)
- **Timestamps** — Creation and last update times
- **Statistics** — Node count, edge count
- **Index status** — Whether search index is built

---

## Examples

### Basic Usage

```bash
hk info ./output/
```

**Output:**
```
Knowledge Abstract Info

Path          ./output/
Template      general/biography_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:35:22
Nodes         25
Edges         32
Index         Built
```

### After Extraction

```bash
hk parse tesla.md -t general/biography_graph -o ./ka/ -l en
hk info ./ka/
```

### After Feed

```bash
hk feed ./ka/ more_content.md
hk info ./ka/
# Note the updated node/edge counts and timestamp
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `Path` | Absolute path to knowledge abstract |
| `Template` | Template identifier (e.g., `general/biography_graph`) |
| `Language` | Processing language (`en` or `zh`) |
| `Created` | Initial extraction timestamp |
| `Updated` | Last modification timestamp |
| `Nodes` | Number of entities/items |
| `Edges` | Number of relationships |
| `Index` | Search index status (`Built` or `Not Built`) |

---

## Use Cases

### Verify Extraction

Check that extraction worked:

```bash
hk info ./ka/
# Should show Nodes > 0, Edges > 0
```

### Check Index Status

Before using search or chat:

```bash
hk info ./ka/
# If Index shows "Not Built", run:
hk build-index ./ka/
```

### Monitor Growth

Track knowledge abstract growth over time:

```bash
hk info ./ka/
# Feed more documents
hk feed ./ka/ update.md
hk info ./ka/
# Compare node/edge counts
```

### Scripting

Use in automation scripts:

```bash
#!/bin/bash

if hk info ./ka/ 2>/dev/null; then
    echo "Knowledge base exists"
    hk feed ./ka/ new_doc.md
else
    echo "Creating new knowledge abstract"
    hk parse new_doc.md -t general/biography_graph -o ./ka/ -l en
fi
```

---

## Troubleshooting

### "Knowledge base directory not found"

The directory doesn't exist or doesn't contain a knowledge abstract:

```bash
# Check directory exists
ls ./ka/

# Should contain:
# - data.json
# - metadata.json
```

### Missing metadata

If metadata is corrupted, template/language show as "unknown":

```bash
hk info ./ka/
# Template: [yellow]unknown[/yellow]
# Language: [yellow]unknown[/yellow]
```

The knowledge abstract is still usable but some features may be limited.

---

## See Also

- [`hk parse`](parse.md) — Create knowledge abstract
- [`hk feed`](feed.md) — Add to knowledge abstract
- [`hk build-index`](build-index.md) — Build search index
