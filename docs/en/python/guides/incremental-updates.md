# Incremental Updates

!!! tip "Advanced - Post-Extraction"
    This guide covers adding more documents after initial extraction. You should be comfortable with [Level 1: Using Templates](using-templates.md) first.

Add new information to existing knowledge abstracts without reprocessing.

---

## Overview

The `feed_text()` method allows you to incrementally add documents to an existing knowledge abstract:

1. **Preserves existing data** — Won't overwrite what's already there
2. **Intelligent merging** — Handles duplicates and conflicts
3. **Updates metadata** — Tracks when updates occurred

---

## Basic Usage

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "en")

# Initial extraction
result = ka.parse(initial_text)
print(f"Initial: {len(result.nodes)} nodes")

# Add more content
result.feed_text(additional_text)
print(f"After feed: {len(result.nodes)} nodes")
```

---

## Use Cases

### Building Knowledge Over Time

```python
ka = Template.create("general/biography_graph", "en")
ka = ka.parse(early_life_text)

# Add career information
ka.feed_text(career_text)

# Add later years
ka.feed_text(later_years_text)

# Rebuild index after feeding new data
ka.build_index()

# Final result combines all periods (with interactive search/chat)
ka.show()
```

![Interactive Visualization](../../../assets/en_show.jpg)

### Processing Multiple Documents

```python
ka = Template.create("general/concept_graph", "en")
ka = ka.parse(documents[0])

for doc in documents[1:]:
    ka.feed_text(doc)
    print(f"Added document, now {len(ka.nodes)} nodes")
```

### Updating with New Information

```python
# Original extraction
ka = ka.parse(original_paper)

# Add corrections/updates
ka.feed_text(corrections)

# Save updated version
ka.dump("./updated_ka/")
```

---

## How Merging Works

### Entity Merging

```python
# If same entity appears in both texts
# Result: Merged descriptions, fields combined
```

### Relation Merging

```python
# If same relation appears
# Result: Updated with latest information
```

### Duplicate Handling

```python
# Exact duplicates are detected and merged
# Near-duplicates (similar names) may create separate entries
```

---

## Best Practices

### 1. Same Template Type

Ensure you're using compatible Auto-Types:

```python
# Good: Same template type
ka = ka.parse(text1)  # biography_graph
ka.feed_text(text2)   # same type

# Be careful: Mixing types may cause issues
```

### 2. Rebuild Index After Feeding

```python
ka.feed_text(new_text)
ka.build_index()  # Required for search/chat
```

### 3. Save Intermediate States

```python
# Save after major updates
ka.feed_text(chapter1)
ka.dump("./kb_v1/")

ka.feed_text(chapter2)
ka.dump("./kb_v2/")
```

### 4. Monitor Growth

```python
initial_count = len(ka.nodes)
ka.feed_text(new_text)
new_count = len(ka.nodes)

print(f"Added {new_count - initial_count} new nodes")
```

---

## Complete Example

```python
"""Build a knowledge abstract incrementally from multiple sources."""

from hyperknowledge import Template
from pathlib import Path

def build_knowledge_base(source_dir, output_dir):
    ka = Template.create("general/biography_graph", "en")
    
    # Get all text files
    files = sorted(Path(source_dir).glob("*.md"))
    
    if not files:
        print("No files found")
        return
    
    # Initial extraction from first file
    print(f"Processing {files[0].name}...")
    ka = ka.parse(files[0].read_text())
    
    # Feed remaining files
    for file in files[1:]:
        print(f"Adding {file.name}...")
        ka.feed_text(file.read_text())
        print(f"  Now {len(ka.nodes)} nodes")
    
    # Build index for search/chat
    print("Building search index...")
    ka.build_index()
    
    # Save
    print(f"Saving to {output_dir}...")
    ka.dump(output_dir)
    
    print("Done!")
    return ka

# Usage
ka = build_knowledge_base("./sources/", "./combined_ka/")
```

---

## Comparison: Parse vs Feed

| Operation | Use When | Result |
|-----------|----------|--------|
| `parse()` | Starting fresh | New knowledge abstract |
| `feed_text()` | Adding to existing | Updated knowledge abstract |

### Chaining Operations

```python
# Parse returns new instance
result1 = ka.parse(text1)
result2 = ka.parse(text2)  # Independent of result1

# Feed modifies existing
result1.feed_text(text2)   # result1 is updated
```

---

## Limitations

### 1. Memory Usage

Large knowledge abstracts consume memory:

```python
# Monitor size
import sys
size = sys.getsizeof(ka.data)
print(f"Knowledge base size: {size} bytes")
```

### 2. Merge Quality

Merging isn't perfect:
- Similar but not identical entities may not merge
- Very large knowledge abstracts may slow down

### 3. Index Staleness

Always rebuild after feeding:

```python
ka.feed_text(text)
ka.build_index()  # Don't forget!
```

---

## Troubleshooting

### "Memory error"

Process in smaller batches:

```python
for batch in chunks(documents, batch_size=5):
    for doc in batch:
        ka.feed_text(doc)
    ka.dump(f"./kb_checkpoint/")  # Save periodically
```

### "Duplicate entities"

Normalize entity names in your text:

```python
# Instead of "Nikola Tesla" and "Tesla"
# Use consistent naming
```

### "Index out of date"

```python
# Forgot to rebuild?
ka.build_index()
```

---

## See Also

**Related Workflows:**
- [Search and Chat](search-and-chat.md) — Query your updated knowledge
- [Saving and Loading](saving-loading.md) — Persist merged results

**Basics:**
- [Using Templates](using-templates.md) — Level 1 fundamentals
- [Working with Auto-Types](working-with-autotypes.md) — Level 2 customization
