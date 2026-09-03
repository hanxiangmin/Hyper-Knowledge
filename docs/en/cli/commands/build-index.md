# hk build-index

Build or rebuild the vector search index for a knowledge abstract.

---

## Synopsis

```bash
hk build-index KA_PATH [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge abstract directory |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Force rebuild even if index exists |

---

## Description

Builds a vector search index for semantic search and chat functionality:

1. **Reads all entities/relations** — From the knowledge abstract data
2. **Generates embeddings** — Using the configured embedding model
3. **Builds FAISS index** — For fast similarity search
4. **Saves to disk** — In the `index/` subdirectory

**Required for**: `hk search` and `hk talk` commands.

---

## Examples

### Build Index

```bash
hk build-index ./output/
```

**Output:**
```
Template: general/biography_graph
Language: en

Success! Index built for ./output/

Now you can:
  hk search ./output/ "keyword"  # Semantic search
  hk talk ./output/ -i           # Interactive chat
```

### Force Rebuild

If the index is corrupted or you want to rebuild:

```bash
hk build-index ./output/ -f
```

---

## When to Build Index

### After Parse (Default)

By default, `hk parse` builds the index automatically:

```bash
hk parse doc.md -t general/biography_graph -o ./ka/ -l en
# Index is built automatically
```

Skip with `--no-index` if you don't need search/chat:

```bash
hk parse doc.md -t general/biography_graph -o ./ka/ -l en --no-index
```

### After Feed

Always rebuild after feeding new documents:

```bash
hk feed ./ka/ new_doc.md
hk build-index ./ka/
```

### After Manual Changes

If you modify `data.json` manually:

```bash
hk build-index ./ka/ -f
```

---

## Index Storage

The index is stored in the knowledge abstract directory:

```
./ka/
├── data.json
├── metadata.json
└── index/              # Index directory
    ├── index.faiss     # FAISS vector index
    └── docstore.json   # Document store mapping
```

---

## Performance

### Build Time

| Knowledge Abstract Size | Approximate Build Time |
|---------------------|----------------------|
| Small (< 100 items) | < 5 seconds |
| Medium (100-1000) | 5-30 seconds |
| Large (1000+) | 30+ seconds |

### Search Speed

Once built, searches are fast:

```bash
hk search ./ka/ "query"  # Typically < 1 second
```

---

## Best Practices

1. **Build after feeding** — Index becomes stale after `hk feed`
2. **Use `--no-index` for batch** — Build once after all parsing
3. **Force rebuild if issues** — Use `-f` if search returns unexpected results
4. **Backup large indices** — The `index/` directory can be large

---

## Batch Workflow

For processing multiple documents efficiently:

```bash
# Parse all without building index
hk parse doc1.md -t general/biography_graph -o ./ka/ -l en --no-index
hk feed ./ka/ doc2.md
hk feed ./ka/ doc3.md

# Build index once at the end
hk build-index ./ka/

# Now ready for search/chat
hk search ./ka/ "query"
hk talk ./ka/ -q "question"
```

---

## Troubleshooting

### "Index already exists"

Use `-f` to force rebuild:

```bash
hk build-index ./ka/ -f
```

### "Failed to build index"

Check:
1. Knowledge base has data: `hk info ./ka/`
2. API key is configured: `hk config show`
3. Sufficient disk space for index

### Search still doesn't work

Try force rebuild:

```bash
hk build-index ./ka/ -f
```

---

## See Also

- [`hk parse`](parse.md) — Parse with optional index building
- [`hk feed`](feed.md) — Add documents (requires rebuild)
- [`hk search`](search.md) — Search the index
- [`hk talk`](talk.md) — Chat using the index
