# hk feed

Add documents to an existing knowledge abstract incrementally.

---

## Synopsis

```bash
hk feed KA_PATH INPUT [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to existing knowledge abstract directory |
| `INPUT` | Input file path or `-` for stdin |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--template` | `-t` | Override template (uses metadata if omitted) |
| `--lang` | `-l` | Override language (uses metadata if omitted) |

---

## Description

The `feed` command adds new documents to an existing knowledge abstract without losing existing data:

1. **Loads existing knowledge** — Reads current knowledge abstract state
2. **Extracts from new document** — Processes the new content
3. **Merges intelligently** — Combines new and existing data, handling duplicates
4. **Updates metadata** — Records the update timestamp

This is ideal for:
- Building knowledge abstracts over time
- Adding updates to existing documents
- Combining information from multiple sources

---

## Examples

### Basic Usage

```bash
# Initial extraction
hk parse tesla_bio.md -t general/biography_graph -o ./tesla_kb/ -l en

# Add more content
hk feed ./tesla_kb/ tesla_inventions.md
```

### Feed Multiple Documents

```bash
hk feed ./ka/ doc1.md
hk feed ./ka/ doc2.md
hk feed ./ka/ doc3.md
```

Or use a loop:

```bash
for file in updates/*.md; do
    hk feed ./ka/ "$file"
done
```

### From Stdin

```bash
cat new_content.md | hk feed ./ka/ -
```

---

## Merge Behavior

The merge process handles:

| Scenario | Behavior |
|----------|----------|
| Same entity | Merged, descriptions combined |
| Same relation | Updated with latest information |
| New entities | Added to knowledge abstract |
| New relations | Added connecting existing/new entities |

---

## Workflow Example

### Building a Research Knowledge Abstract

```bash
# Day 1: Initial paper
hk parse paper_v1.md -t general/concept_graph -o ./research_kb/ -l en
hk show ./research_kb/

# Day 7: Updated version
hk feed ./research_kb/ paper_v2.md
hk show ./research_kb/

# Day 14: Related work
hk feed ./research_kb/ related_work.md
hk build-index ./research_kb/
hk talk ./research_kb/ -q "What are the key concepts across all papers?"
```

### Incremental Biography

```bash
# Start with early life
hk parse early_life.md -t general/biography_graph -o ./bio_kb/ -l en

# Add career period
hk feed ./bio_kb/ career.md

# Add later years
hk feed ./bio_kb/ later_years.md

# Final visualization
hk show ./bio_kb/
```

---

## Verification

Check that the feed worked:

```bash
hk info ./ka/
```

Look for:
- Increased node count
- Increased edge count  
- Updated timestamp

---

## Best Practices

1. **Use same template** — Feeding should use compatible templates
2. **Match language** — Use consistent language for best results
3. **Rebuild index after** — `hk build-index ./ka/` for search/chat
4. **Visualize changes** — `hk show ./ka/` to see updates

---

## Error Handling

### "Not a valid Knowledge Abstract directory"

The directory doesn't contain a valid knowledge abstract. Check:

```bash
ls ./ka/
# Should contain: data.json, metadata.json
```

### "Template mismatch"

Feeding works best with the same template type. Override if needed:

```bash
hk feed ./ka/ doc.md -t general/biography_graph
```

---

## See Also

- [`hk parse`](parse.md) — Create new knowledge abstract
- [`hk info`](info.md) — View knowledge abstract statistics
- [`hk build-index`](build-index.md) — Rebuild search index after feeding
