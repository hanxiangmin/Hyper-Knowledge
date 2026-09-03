# Saving and Loading

!!! tip "Advanced - Post-Extraction"
    This guide covers persisting extracted knowledge. You should be comfortable with [Level 1: Using Templates](using-templates.md) first.

---

## Overview

Hyper-Knowledge provides serialization for:
- **Data** — Extracted entities and relations
- **Metadata** — Extraction settings and timestamps
- **Index** — Vector search index (optional)

---

## Saving Knowledge Abstracts

### Basic Save

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "en")
result = ka.parse(text)

# Save to directory
result.dump("./my_ka/")
```

### Save Structure

```
./my_ka/
├── data.json          # Extracted knowledge
├── metadata.json      # Extraction info
└── index/             # Search index (if built)
    ├── index.faiss
    └── docstore.json
```

### Before Saving

```python
# Build index first (if needed)
result.build_index()

# Then save
result.dump("./my_ka/")
```

---

## Loading Knowledge Abstracts

### Basic Load

```python
from hyperknowledge import Template

# Create template (must match original)
ka = Template.create("general/biography_graph", "en")

# Load saved data
ka.load("./my_ka/")

# Use
print(f"Loaded {len(ka.nodes)} nodes")
```

### Verify Loaded Data

```python
ka.load("./my_ka/")

# Check it's not empty
if ka.empty():
    print("Warning: No data loaded")
else:
    print(f"Nodes: {len(ka.nodes)}")
    print(f"Edges: {len(ka.edges)}")
```

---

## Use Cases

### Long-term Storage

```python
# Extract and save
ka = Template.create("general/concept_graph", "en")
result = ka.parse(research_paper)
result.build_index()
result.dump("./research_paper_kb/")

# Use weeks later
ka2 = Template.create("general/concept_graph", "en")
ka2.load("./research_paper_kb/")
response = ka2.chat("What are the main findings?")
```

### Sharing Knowledge Abstracts

```python
# Save to shared location
result.dump("/shared/ka/project_x/")

# Others can load
ka.load("/shared/ka/project_x/")
```

### Backup and Versioning

```python
from datetime import datetime

# Save with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result.dump(f"./backups/kb_{timestamp}/")

# Or versioned
result.dump("./kb_v1/")
# ... later updates ...
result.dump("./kb_v2/")
```

---

## Working with the Filesystem

### Checking for Existing KA

```python
from pathlib import Path

ka_path = Path("./my_ka/")

if ka_path.exists() and (ka_path / "data.json").exists():
    print("Knowledge base exists, loading...")
    ka.load(ka_path)
else:
    print("Creating new knowledge abstract...")
    result = ka.parse(text)
    result.dump(ka_path)
```

### Listing Saved KBs

```python
import os

kb_dirs = [d for d in os.listdir("./") if os.path.isdir(d) and "_kb" in d]
print("Available knowledge abstracts:", kb_dirs)
```

### Moving/Copying

```python
import shutil

# Copy knowledge abstract
shutil.copytree("./kb_v1/", "./kb_backup/")

# Move knowledge abstract
shutil.move("./old_location/", "./new_location/")
```

---

## Metadata

### Accessing Metadata

```python
result.dump("./my_ka/")

# Metadata is saved automatically
# Contents:
# - template: Template used
# - lang: Language
# - created_at: Creation timestamp
# - updated_at: Last update timestamp
```

### Custom Metadata

```python
# Add custom metadata
result.metadata["project"] = "Research Project X"
result.metadata["version"] = "1.0"

result.dump("./my_ka/")
```

---

## Complete Example

```python
"""Manage knowledge abstracts with save/load."""

from hyperknowledge import Template
from pathlib import Path
import json

class KnowledgeBaseManager:
    def __init__(self, storage_dir="./knowledge_bases/"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save(self, ka, name):
        """Save knowledge abstract."""
        ka_path = self.storage_dir / name
        ka.dump(ka_path)
        print(f"Saved to {ka_path}")
        return ka_path
    
    def load(self, name, template="general/biography_graph", lang="en"):
        """Load knowledge abstract."""
        ka_path = self.storage_dir / name
        
        if not ka_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {name}")
        
        ka = Template.create(template, lang)
        ka.load(ka_path)
        return ka
    
    def list(self):
        """List available knowledge abstracts."""
        return [d.name for d in self.storage_dir.iterdir() if d.is_dir()]
    
    def info(self, name):
        """Get knowledge abstract info."""
        ka_path = self.storage_dir / name
        meta_path = ka_path / "metadata.json"
        
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return None

# Usage
manager = KnowledgeBaseManager()

# Save
ka = Template.create("general/biography_graph", "en")
result = ka.parse(text)
manager.save(result, "tesla_biography")

# List
print(manager.list())  # ['tesla_biography']

# Load
ka = manager.load("tesla_biography")
print(ka.chat("What did Tesla invent?"))
```

---

## Best Practices

### 1. Match Template on Load

```python
# Save with template X
ka = Template.create("general/biography_graph", "en")

# Load with same template
ka2 = Template.create("general/biography_graph", "en")
ka2.load("./ka/")
```

### 2. Build Index After Loading

```python
ka.load("./ka/")

# Check if index exists, otherwise rebuild
index_path = Path("./ka/") / "index"
if not index_path.exists():
    ka.build_index()
```

### 3. Validate Before Use

```python
try:
    ka.load("./ka/")
    if ka.empty():
        print("Warning: Empty knowledge abstract")
except FileNotFoundError:
    print("Knowledge base not found")
```

### 4. Use Descriptive Names

```python
# Good
result.dump("./ka/tesla_2024_01_15/")

# Avoid
result.dump("./ka/temp/")
```

---

## Troubleshooting

### "File not found"

```python
from pathlib import Path

ka_path = Path("./my_ka/")
if not ka_path.exists():
    print(f"Directory not found: {ka_path}")
    print(f"Available: {list(Path('.').glob('*/'))}")
```

### "Corrupted data"

```python
# Check data file
import json
data = json.load(open("./my_ka/data.json"))
print(f"Keys: {data.keys()}")
```

### "Index not loaded"

```python
ka.load("./ka/")

# Check if index exists
if (Path("./ka/") / "index").exists():
    print("Index directory exists")
else:
    print("No index, building...")
    ka.build_index()
```

---

## See Also

**Related Workflows:**
- [Incremental Updates](incremental-updates.md) — Add more content
- [Search and Chat](search-and-chat.md) — Use loaded knowledge

**Basics:**
- [Using Templates](using-templates.md) — Level 1 fundamentals
- [CLI `hk parse` command](../../cli/commands/parse.md) — Command-line extraction
