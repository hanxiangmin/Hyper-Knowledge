# Step 2: Ingest

Add documents to your knowledge abstract.

---

## Goal

Ingest documents into the knowledge abstract with proper version control.

---

## Document Preparation

### Supported Formats

- Markdown (.md)
- Text (.txt)
- Convert PDFs: `pdftotext document.pdf document.txt`

### Organize Documents

```
documents/
├── raw/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── doc1.md
│   │   │   └── doc2.md
│   │   └── 02/
│   │       └── doc3.md
│   └── archive/
└── processed/  # Processing log
```

---

## Ingestion Methods

### Method 1: Initial Ingestion

First batch of documents:

```python
def initial_ingest(self, documents_dir: str):
    """Initial ingestion of documents."""
    print("Starting initial ingestion...")
    
    # Get all documents
    docs = list(Path(documents_dir).glob("**/*.md"))
    docs.extend(Path(documents_dir).glob("**/*.txt"))
    
    print(f"Found {len(docs)} documents")
    
    # Parse first document
    print(f"Processing: {docs[0].name}")
    text = docs[0].read_text(encoding="utf-8")
    ka = self.ka.parse(text)
    
    # Feed remaining documents
    for doc in docs[1:]:
        print(f"Adding: {doc.name}")
        text = doc.read_text(encoding="utf-8")
        ka.feed_text(text)
    
    # Build index
    print("Building search index...")
    ka.build_index()
    
    # Save version
    version_path = self.save_version(ka, "v1.0")
    
    # Log processing
    self._log_processing(docs, version_path)
    
    print(f"✓ Ingested {len(docs)} documents")
    print(f"✓ Knowledge base: {version_path}")
    
    return ka
```

### Method 2: Incremental Updates

Add new documents to existing KA:

```python
def add_documents(self, document_paths: list[str]):
    """Add new documents to existing knowledge abstract."""
    print("Loading current knowledge abstract...")
    
    # Load current version
    current_path = Path(self.config.kb_dir) / "current"
    ka = Template.create(self.config.template, self.config.language)
    ka.load(current_path)
    
    # Add new documents
    for path in document_paths:
        doc_path = Path(path)
        print(f"Adding: {doc_path.name}")
        
        text = doc_path.read_text(encoding="utf-8")
        ka.feed_text(text)
    
    # Rebuild index
    print("Rebuilding search index...")
    ka.build_index()
    
    # Save new version
    version = self._get_next_version()
    version_path = self.save_version(ka, version)
    
    print(f"✓ Added {len(document_paths)} documents")
    print(f"✓ New version: {version}")
    
    return ka

def _get_next_version(self) -> str:
    """Generate next version number."""
    current = Path(self.config.kb_dir) / "current"
    if not current.exists():
        return "v1.0"
    
    # Parse current version
    current_target = current.readlink().name
    if current_target.startswith("v"):
        try:
            parts = current_target[1:].split(".")
            major = int(parts[0])
            minor = int(parts[1])
            return f"v{major}.{minor + 1}"
        except:
            pass
    
    return datetime.now().strftime("v%Y%m%d_%H%M%S")
```

---

## Complete Ingestion Script

```python
"""Step 2: Document Ingestion."""

import argparse
from pathlib import Path
from kb_manager import KnowledgeBaseManager

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into KA")
    parser.add_argument("--initial", action="store_true", help="Initial ingestion")
    parser.add_argument("--add", nargs="+", help="Add specific documents")
    parser.add_argument("--dir", default="./documents/raw", help="Documents directory")
    args = parser.parse_args()
    
    # Initialize manager
    manager = KnowledgeBaseManager()
    manager.initialize()
    
    if args.initial:
        # Initial ingestion
        ka = manager.initial_ingest(args.dir)
        
        # Print stats
        print("\nKnowledge Abstract Stats:")
        print(f"  Nodes: {len(ka.nodes)}")
        print(f"  Edges: {len(ka.edges)}")
        
    elif args.add:
        # Add specific documents
        ka = manager.add_documents(args.add)
        
        print("\nKnowledge Abstract Stats:")
        print(f"  Nodes: {len(ka.nodes)}")
        print(f"  Edges: {len(ka.edges)}")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# Initial ingestion
python step2_ingest.py --initial

# Add specific documents
python step2_ingest.py --add documents/raw/2024/02/new_doc.md

# Add multiple documents
python step2_ingest.py --add doc1.md doc2.md doc3.md
```

---

## Processing Log

Track what was ingested:

```python
def _log_processing(self, documents: list[Path], version_path: Path):
    """Log processing details."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "version": version_path.name,
        "documents": [str(d) for d in documents],
        "document_count": len(documents)
    }
    
    log_file = Path("logs") / "ingestions.jsonl"
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## Best Practices

### 1. Batch Size

Process documents in batches:

```python
BATCH_SIZE = 10

for i in range(0, len(docs), BATCH_SIZE):
    batch = docs[i:i + BATCH_SIZE]
    for doc in batch:
        ka.feed_text(doc.read_text())
    
    # Save checkpoint
    if i % (BATCH_SIZE * 5) == 0:
        ka.dump(f"./ka/checkpoint_{i}/")
```

### 2. Error Handling

```python
try:
    text = doc.read_text(encoding="utf-8")
    ka.feed_text(text)
except Exception as e:
    print(f"Error processing {doc}: {e}")
    # Log error, continue with next
    continue
```

### 3. Validation

```python
def validate_ingestion(self, ka):
    """Validate knowledge abstract after ingestion."""
    assert not ka.empty(), "Knowledge base is empty"
    assert len(ka.data.entities) > 0, "No entities extracted"
    
    # Try to build index
    try:
        ka.build_index()
    except Exception as e:
        raise ValueError(f"Failed to build index: {e}")
```

---

## Next Step

→ [Step 3: Query and Maintain](step3-query.md)
