# Using Methods

!!! tip "Level 1 - Beginner"
    This guide is for beginners. Before reading, please complete the [Quickstart](../quickstart.md) and [Using Templates](using-templates.md).

Learn about Hyper-Knowledge extraction methods and how to quickly switch between algorithms in `Template.create`.

---

## What Are Methods?

A **Method** is the underlying algorithm that drives knowledge extraction. In Hyper-Knowledge, both methods and templates can be called directly through `Template.create`:

```python
# Using a template
ka = Template.create("general/biography_graph", language="en")

# Using a method
ka = Template.create("method/light_rag")
```

The difference:
- **Template** = Pre-configured domain solution (structure + prompts + language)
- **Method** = Pure extraction algorithm, lighter weight, ideal when you need to switch algorithms

---

## Method Categories

### Typical Methods

**Direct extraction** methods that process text without retrieval.

| Method | Best For | Key Feature |
|--------|----------|-------------|
| `itext2kg` | Quality-focused | High-quality triples |
| `itext2kg_star` | Enhanced quality | Improved iText2KG |
| `kg_gen` | Flexibility | Configurable generation |
| `atom` | Temporal data | Evidence attribution |

### RAG-Based Methods

**Retrieval-Augmented Generation** methods excel at processing large documents by combining retrieval with generation.

| Method | Best For | Key Feature |
|--------|----------|-------------|
| `light_rag` | General use | Fast, lightweight |
| `graph_rag` | Large documents | Community detection |
| `hyper_rag` | Complex relationships | N-ary hyperedges |
| `hypergraph_rag` | Advanced scenarios | Enhanced hypergraph |
| `cog_rag` | Reasoning tasks | Cognitive retrieval |

---

## Basic Usage

### Default Configuration

```python
from hyperknowledge import Template

# Create and extract
ka = Template.create("method/light_rag")
result = ka.parse(text)
```

### With Custom Clients

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperknowledge import Template

llm = ChatOpenAI(model="gpt-4o")
emb = OpenAIEmbeddings(model="text-embedding-3-large")

ka = Template.create(
    "method/graph_rag",
    llm_client=llm,
    embedder=emb
)
```

---

## Method Selection Guide

### Decision Tree

```mermaid
graph TD
    A[Select Method] --> B{Document size?}
    B -->|Large| C[RAG-Based]
    B -->|Small/Medium| D{Need evidence?}
    D -->|Yes| E[atom]
    D -->|No| F{Prioritize quality?}
    F -->|Yes| G[iText2KG]
    F -->|No| H[kg_gen]

    C --> I{Relationship complexity?}
    I -->|Simple| J[light_rag]
    I -->|Standard| K[graph_rag]
    I -->|Complex| L[hyper_rag]
```

### By Use Case

#### Quick Extraction (Small Documents)

```python
# Fast and simple
ka = Template.create("method/kg_gen")
```

#### High-Quality Results

```python
# Best extraction quality
ka = Template.create("method/itext2kg_star")
```

#### Large Documents

```python
# Efficient processing
ka = Template.create("method/light_rag")
```

#### Complex Relationships

```python
# Multi-entity relationships
ka = Template.create("method/hyper_rag")
```

#### Temporal Analysis

```python
# Time-based with evidence
ka = Template.create("method/atom")
```

---

## RAG vs Typical Comparison

| Feature | RAG-Based | Typical |
|---------|-----------|---------|
| **Document size** | Large (10k+ words) | Small-Medium |
| **Speed** | Slower (retrieval step) | Faster |
| **Memory** | Higher | Lower |
| **Quality** | Good for large docs | Better for small docs |
| **Context handling** | Excellent | Good |
| **Use case** | Books, papers, reports | Articles, summaries |

---

## Method Quick Reference

### itext2kg

Best for: High-quality triple extraction

```python
ka = Template.create("method/itext2kg")

# Characteristics:
# - Optimized for triple quality
# - Iterative refinement
# - Good for knowledge base construction
```

### itext2kg_star

Best for: Enhanced quality extraction

```python
ka = Template.create("method/itext2kg_star")

# Characteristics:
# - Improved extraction quality
# - Better handling of complex cases
# - Enhanced entity linking
```

### kg_gen

Best for: Flexible, configurable extraction

```python
ka = Template.create("method/kg_gen")

# Characteristics:
# - Configurable generation
# - Flexible schema
# - Fast processing
```

### atom

Best for: Temporal analysis with evidence

```python
ka = Template.create("method/atom")

# Characteristics:
# - Temporal fact extraction
# - Evidence attribution
# - Confidence scoring
```

### light_rag

Best for: General-purpose, fast extraction

```python
ka = Template.create("method/light_rag")

# Characteristics:
# - Fastest RAG method
# - Binary edges (source-target)
# - Good balance of speed/quality
```

### graph_rag

Best for: Large documents with community structure

```python
ka = Template.create("method/graph_rag")

# Characteristics:
# - Community detection
# - Hierarchical summaries
# - Best for very large documents
```

### hyper_rag

Best for: Complex multi-entity relationships

```python
ka = Template.create("method/hyper_rag")

# Characteristics:
# - Hyperedges (connect 2+ entities)
# - Captures complex relationships
# - Richer graph structure
```

---

## Listing Available Methods

```python
from hyperknowledge import Template
from hyperknowledge.methods import list_methods

# List all methods
methods = list_methods()
for name, info in methods.items():
    print(f"{name}: {info['description']}")
    print(f"  Type: {info['type']}")
```

---

## Best Practices

1. **Start with light_rag** — Good default for most cases
2. **Use itext2kg for quality** — When extraction quality is critical
3. **Try hyper_rag for complex data** — When relationships are multi-faceted
4. **Consider atom for temporal data** — When time is important
5. **Benchmark on your data** — Methods perform differently on different content

---

## See Also

**Prerequisites:**
- [Using Templates](using-templates.md) — Level 1: Ready-to-use domain solutions

**Next Steps:**
- [Working with Auto-Types](working-with-autotypes.md) — Level 2: Custom schemas and extraction configs
- [Creating Custom Templates](custom-templates.md) — Package your custom configs into reusable templates

**Reference:**
- [Methods Concept Doc](../../concepts/methods.md) — Detailed algorithm explanations
- [Template Library](../../templates/index.md) — Browse existing templates
