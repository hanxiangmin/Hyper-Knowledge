# hk search

Perform semantic search over a knowledge abstract.

---

## Synopsis

```bash
hk search KA_PATH QUERY [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge abstract directory |
| `QUERY` | Search query string |

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--top-k` | `-n` | Number of results to return | 3 |

---

## Description

Semantic search finds relevant information even when keywords don't match exactly. It uses:

1. **Vector embeddings** — Converts query and content to vectors
2. **Similarity matching** — Finds semantically similar content
3. **Ranking** — Returns most relevant results

**Requires**: Search index must be built. Run `hk build-index` if needed.

---

## Examples

### Basic Search

```bash
hk search ./output/ "Tesla's inventions"
```

### Get More Results

```bash
hk search ./output/ "electrical engineering" -n 10
```

### Natural Language Queries

```bash
hk search ./ka/ "What were the major achievements?"
hk search ./ka/ "People who worked with Edison"
hk search ./ka/ "Important dates in the timeline"
```

### After Building Index

```bash
# First, ensure index exists
hk build-index ./output/

# Then search
hk search ./output/ "innovation"
```

---

## Output Format

```
Found 3 result(s):

Result 1:
{
  "name": "Nikola Tesla",
  "type": "person",
  "description": "Serbian-American inventor, electrical engineer..."
}

Result 2:
{
  "source": "Nikola Tesla",
  "target": "Thomas Edison",
  "type": "worked_with",
  "description": "Tesla worked for Edison in 1884"
}

Result 3:
...
```

---

## How It Works

1. **Query Embedding** — Converts your query to a vector
2. **Index Search** — Finds nearest vectors in the knowledge abstract
3. **Result Ranking** — Returns top-k most similar items

---

## Tips for Better Search

1. **Use natural language** — "inventions in electrical engineering" vs "invention electrical"
2. **Be specific** — "Tesla's work on AC power" vs "Tesla work"
3. **Try synonyms** — If "inventions" doesn't work, try "discoveries"
4. **Increase top-k** — Use `-n 10` for broader results

---

## Comparison with `hk talk`

| Feature | `hk search` | `hk talk` |
|---------|-------------|-----------|
| Returns | Raw entities/relations | Natural language answer |
| Use case | Find specific data | Get explanations |
| Speed | Faster | Slower (LLM generation) |
| Precision | Exact matches | Interpretive |

---

## Troubleshooting

### "Index not found"

Build the search index:

```bash
hk build-index ./output/
```

### "No results found"

Try:
1. Broader query terms
2. Increase `-n` for more results
3. Different phrasing
4. Check `hk info ./output/` to verify data exists

---

## See Also

- [`hk talk`](talk.md) — Chat with knowledge abstract
- [`hk build-index`](build-index.md) — Build search index
- [`hk parse`](parse.md) — Extract with index building
