# Research Paper Analysis

Complete guide for extracting knowledge from research papers.

---

## Scenario

You have a research paper and want to:
- Extract key concepts and their definitions
- Map relationships between concepts
- Build a queryable knowledge base
- Visualize the concept network

---

## Recommended Template

### `general/concept_graph`

Best for extracting concepts, methods, and their relationships from academic papers.

**Why this template?**
- Automatically identifies key concepts
- Maps "is-a", "uses", "relates-to" relationships
- Supports hierarchical structures
- Optimized for academic language

---

## Complete Workflow

### Step 1: Extract Knowledge

=== "CLI"

    ```bash
    hk parse paper.md -t general/concept_graph -l en -o ./paper_kb/
    ```

=== "Python"

    ```python
    from hyperknowledge import Template

    # Load paper
    with open("paper.md", "r") as f:
        paper_text = f.read()

    # Create template
    ka = Template.create("general/concept_graph", "en")

    # Extract
    result = ka.parse(paper_text)

    print(f"Extracted {len(result.nodes)} concepts")
    print(f"Extracted {len(result.edges)} relationships")
    ```

**Example Output:**
```python
{
    "entities": [
        {"name": "Transformer", "type": "model"},
        {"name": "Attention Mechanism", "type": "concept"},
        {"name": "BLEU Score", "type": "metric"}
    ],
    "relations": [
        {"source": "Transformer", "target": "Attention Mechanism", "type": "uses"},
        {"source": "Transformer", "target": "BLEU Score", "type": "achieves"}
    ]
}
```

---

### Step 2: Explore Results

> **Note:** The following steps assume you used the Python approach in Step 1. If you used CLI, load the result with `ka.load("./paper_kb/")`.

```python
# List all concepts
print("\nConcepts found:")
for node in result.nodes:
    print(f"  - {node.name} ({node.type})")
    if hasattr(node, 'description'):
        print(f"    {node.description[:100]}...")

# List relationships
print("\nRelationships:")
for edge in result.edges:
    print(f"  - {edge.source} → {edge.target}: {edge.type}")
```

**Example Output:**
```
Concepts found:
  - Transformer (architecture)
    A neural network architecture based on self-attention mechanisms...
  - Attention Mechanism (method)
    A technique allowing models to focus on relevant parts of input...
  - BERT (model)
    Bidirectional Encoder Representations from Transformers...

Relationships:
  - BERT → Transformer: implements
  - Transformer → Attention Mechanism: uses
  - BERT → NLP: applied_in
```

---

### Step 3: Build Searchable Index

```python
# Build index for search and chat
result.build_index()

# Save for later use
result.dump("./paper_kb/")
```

---

### Step 4: Visualize

```python
# Open interactive visualization
result.show()
```

This opens an interactive browser view where you can:
- Explore the concept graph visually
- Search for specific concepts
- Ask questions about the paper

---

### Step 5: Query

```python
# Semantic search
nodes, edges = result.search("attention mechanisms", top_k=5)

print("Related concepts:")
for node in nodes:
    print(f"  - {node.name}")

# Chat interface
response = result.chat("What is the main contribution of this paper?")
print(response.content)

response = result.chat("How does the proposed method compare to previous approaches?")
print(response.content)
```

---

## Alternative Templates

### Document Structure

If you need the paper's outline and structure:

=== "CLI"

    ```bash
    hk parse paper.md -t general/doc_structure -l en -o ./structure/
    ```

**Extracts:**
- Section headings
- Key points per section
- Paper organization

### Knowledge Graph

For broader domain knowledge beyond just concepts:

=== "CLI"

    ```bash
    hk parse paper.md -t general/graph -l en -o ./knowledge/
    ```

**Difference from concept_graph:**
- Broader entity types (people, organizations, methods)
- General relationships
- Less focused on conceptual definitions

### Workflow Graph

If the paper describes a process or algorithm:

=== "CLI"

    ```bash
    hk parse paper.md -t general/workflow_graph -l en -o ./workflow/
    ```

**Extracts:**
- Process steps
- Decision points
- Flow relationships

---

## Comparison Table

| Template | Best For | Output |
|----------|----------|--------|
| `concept_graph` | Research papers with concepts/definitions | Concept network |
| `graph` | Broader domain knowledge | General entity network |
| `doc_structure` | Document outline | Hierarchical structure |
| `workflow_graph` | Process/method descriptions | Process flow |

---

## Tips for Best Results

### 1. Document Preparation

- Remove headers/footers
- Ensure clean Markdown or plain text
- Keep equations as LaTeX or plain text

### 2. Language Selection

=== "CLI"

    ```bash
    # English paper
    hk parse paper.md -t general/concept_graph -l en

    # Chinese paper
    hk parse paper.md -t general/concept_graph -l zh
    ```

### 3. Processing Long Papers

For papers over 5000 words:

```python
# Option 1: Use RAG method
ka = Template.create("method/graph_rag")
result = ka.parse(paper_text)

# Option 2: Process by sections
sections = split_paper_into_sections(paper_text)
ka = Template.create("general/concept_graph", "en")
result = ka.parse(sections[0])

for section in sections[1:]:
    result.feed_text(section)
```

### 4. Post-Processing

```python
# Filter by concept type
concepts = [n for n in result.nodes if n.type == "concept"]
methods = [n for n in result.nodes if n.type == "method"]

# Find central concepts (most connected)
from collections import Counter
edge_counts = Counter([e.source for e in result.edges] + 
                      [e.target for e in result.edges])
top_concepts = edge_counts.most_common(5)
```

---

## Example: Complete Analysis Script

```python
"""Complete research paper analysis workflow."""

from hyperknowledge import Template
from pathlib import Path

def analyze_paper(paper_path, output_dir="./paper_analysis/"):
    """Analyze a research paper and create a knowledge base."""
    
    # Load paper
    text = Path(paper_path).read_text()
    
    # Extract concepts
    print("Extracting concepts...")
    ka = Template.create("general/concept_graph", "en")
    result = ka.parse(text)
    
    print(f"Found {len(result.nodes)} concepts")
    print(f"Found {len(result.edges)} relationships")
    
    # Build index
    print("Building search index...")
    result.build_index()
    
    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    result.dump(output_path)
    
    # Generate summary
    print("\n=== Paper Summary ===")
    response = result.chat("Summarize the main contributions in 3 sentences")
    print(response.content)
    
    print("\n=== Key Concepts ===")
    for node in result.nodes[:5]:
        print(f"- {node.name}")
    
    print(f"\nSaved to: {output_path}")
    print(f"\nTo explore: result.show()")
    
    return result

# Usage
if __name__ == "__main__":
    result = analyze_paper("paper.md")
    
    # Interactive exploration
    result.show()
```

---

## See Also

- [Choose by Task](../choosing/by-task.md) — Other task templates
- [Concept Graph Template](../reference/general.md) — Template details
- [Python Quickstart](../../python/quickstart.md) — Getting started with Python SDK
