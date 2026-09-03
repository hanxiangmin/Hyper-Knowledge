# Step 1: Extract Knowledge

Parse a research paper and extract structured concepts.

---

## Goal

Extract entities, relationships, and concepts from a research paper into a structured knowledge graph.

---

## Preparation

### 1. Get a Research Paper

Download a paper or use your own. For this tutorial, we'll use a sample:

```bash
# Download a sample paper (or use your own)
curl -o paper.md https://arxiv.org/abs/1706.03762  # Attention Is All You Need
```

### 2. Convert to Text (if needed)

If you have a PDF:

```bash
pdftotext paper.pdf paper.md
```

---

## Extract Using CLI

### Basic Extraction

```bash
hk parse paper.md -t general/concept_graph -o ./paper_kb/ -l en
```

**What this does:**
- Reads the paper
- Extracts concepts and their relationships
- Saves to `./paper_kb/`

### Verify Extraction

```bash
hk info ./paper_kb/
```

Expected output:
```
Knowledge Abstract Info

Path          ./paper_kb/
Template      general/concept_graph
Language      en
Nodes         25
Edges         32
Index         Built
```

### Visualize

```bash
hk show ./paper_kb/
```

---

## Extract Using Python

### Script

```python
"""Step 1: Extract knowledge from research paper."""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template
from pathlib import Path

# Configuration
PAPER_FILE = "paper.md"
OUTPUT_DIR = "./paper_kb/"

def main():
    # Create template
    print("Creating concept extraction template...")
    ka = Template.create("general/concept_graph", language="en")
    
    # Read paper
    print(f"Reading: {PAPER_FILE}")
    text = Path(PAPER_FILE).read_text(encoding="utf-8")
    
    # Extract knowledge
    print("Extracting concepts and relationships...")
    result = ka.parse(text)
    
    # Display results
    print(f"\nExtraction Complete:")
    print(f"  Nodes: {len(result.nodes)}")
    print(f"  Edges: {len(result.edges)}")

    # Show sample nodes
    print("\nSample Concepts:")
    for node in result.nodes[:5]:
        print(f"  - {node.name} ({node.type})")
    
    # Save
    print(f"\nSaving to: {OUTPUT_DIR}")
    result.dump(OUTPUT_DIR)
    
    # Build index for next step
    print("Building search index...")
    result.build_index()
    result.dump(OUTPUT_DIR)
    
    print("\n✓ Step 1 complete!")
    print(f"  Knowledge base: {OUTPUT_DIR}")
    print(f"\nNext: Run 'python step2_search.py'")

if __name__ == "__main__":
    main()
```

### Run

```bash
python step1_extract.py
```

---

## Understanding the Output

### What Was Extracted?

The concept graph template extracts:

**Entities:**
- Concepts (models, algorithms, techniques)
- Authors
- Datasets
- Metrics

**Relations:**
- `uses` — Concept uses another
- `improves_upon` — Improvement relationships
- `evaluated_on` — Evaluation datasets
- `achieves` — Results/metrics

### Example Output

```python
# Entities
[
    {"name": "Transformer", "type": "model"},
    {"name": "Attention Mechanism", "type": "concept"},
    {"name": "BLEU Score", "type": "metric"}
]

# Relations
[
    {"source": "Transformer", "target": "Attention Mechanism", "type": "uses"},
    {"source": "Transformer", "target": "BLEU Score", "type": "achieves"}
]
```

---

## Troubleshooting

### "No entities extracted"

- Check paper is not empty: `wc -l paper.md`
- Try different template: `general/graph`
- Check language setting matches document

### "Extraction is slow"

- Long papers are chunked automatically
- Each chunk requires an LLM call
- Consider using `--no-index` and building later

---

## Next Step

→ [Step 2: Semantic Search](step2-search.md)
