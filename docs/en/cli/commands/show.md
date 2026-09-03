# hk show

Visualize knowledge graph using OntoSight interactive viewer.

---

## Synopsis

```bash
hk show KA_PATH
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge abstract directory |

---

## Description

Opens an interactive visualization of your knowledge graph in the default web browser. The visualization displays:

- **Nodes** — Entities, concepts, or items (colored by type)
- **Edges** — Relationships between nodes
- **Labels** — Click on nodes/edges to see details

---

## Examples

### Basic Usage

```bash
hk show ./output/
```

### After Extraction

```bash
# Extract first
hk parse tesla.md -t general/biography_graph -o ./tesla_kb/ -l en

# Then visualize
hk show ./tesla_kb/
```

### After Incremental Update

```bash
# Add more content
hk feed ./tesla_kb/ additional_info.md

# Visualize updated graph
hk show ./tesla_kb/
```

---

## Visualization Features

The OntoSight viewer provides:

### Interactive Controls

- **Zoom** — Mouse wheel or pinch gesture
- **Pan** — Click and drag background
- **Select** — Click on nodes/edges to see details
- **Filter** — Show/hide node types

### Node Display

- Size indicates importance (configurable)
- Color indicates entity type
- Label shows entity name

### Edge Display

- Thickness indicates relationship strength
- Label shows relationship type
- Direction shows relationship flow

---

## Supported Auto-Types

Visualization works with all graph-based Auto-Types:

| Auto-Type | Visualization |
|-----------|--------------|
| `AutoGraph` | ✓ Full graph visualization |
| `AutoHypergraph` | ✓ Hypergraph with multi-node edges |
| `AutoTemporalGraph` | ✓ Graph with temporal info |
| `AutoSpatialGraph` | ✓ Graph with spatial info |
| `AutoSpatioTemporalGraph` | ✓ Full context visualization |
| `AutoList` | ✓ List view |
| `AutoSet` | ✓ Set view |
| `AutoModel` | ✓ Structured view |

---

## Troubleshooting

### "Browser doesn't open"

The visualization URL is printed. Open it manually:

```
http://localhost:xxxx
```

### "Empty graph displayed"

Check that extraction worked:

```bash
hk info ./ka/
# Should show Nodes > 0 and Edges > 0
```

### "Error loading visualization"

Ensure the knowledge abstract is valid:

```bash
# Check data file exists
ls ./ka/data.json

# Try reloading
hk show ./ka/
```

---

## See Also

- [`hk parse`](parse.md) — Extract knowledge
- [`hk feed`](feed.md) — Add documents incrementally
- [`hk info`](info.md) — View knowledge abstract statistics
