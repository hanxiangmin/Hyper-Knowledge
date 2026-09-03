# Working with Auto-Types

!!! tip "Level 2 - Intermediate"
    This guide covers configured Auto-Type usage. Before reading, please complete [Level 1: Using Templates](using-templates.md) and [Level 1: Using Methods](using-methods.md).

Learn how to configure Auto-Types directly to customize schemas, deduplication logic, and extraction behavior.

---

## What Are Auto-Types?

Auto-Types are the core data structures in Hyper-Knowledge that extract, organize, and store structured knowledge from text. They provide:

- **Type-safe schemas** — Pydantic-based validation
- **LLM-powered extraction** — Automatic content processing
- **Built-in operations** — Search, merge, visualize
- **Serialization** — Save/load to disk

All Auto-Types inherit from `BaseAutoType`, so they share a common set of capabilities (e.g., `parse`, `feed_text`, `build_index`, `search`, `chat`, `dump`, `load`).

---

## Three-Level Usage Architecture

Hyper-Knowledge provides three levels of control. This guide focuses on **Level 2**.

| Level | Approach | When to Use | Reference |
|-------|----------|-------------|-----------|
| **Level 1** | Templates / Methods | Quick start, standard use cases | [Using Templates](using-templates.md), [Using Methods](using-methods.md) |
| **Level 2** | Configured Auto-Type | Custom schemas, same extraction logic | **This guide** |
| **Level 3** | Fully custom methods | Complete control over extraction | [Methods Concepts](../../concepts/methods.md) |

---

## Level 2: Configured Auto-Type Usage

When you need custom schemas but don't want to implement full extraction logic from scratch, instantiate an Auto-Type directly and pass configuration parameters.

### When to Use Level 2

- You need custom node/edge schemas
- You want to control deduplication logic
- Template output doesn't match your exact needs
- You're building reusable Python components

### Complete Example: Custom Graph

```python
from hyperknowledge import AutoGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

# Step 1: Define custom schemas
class Person(BaseModel):
    """Custom node schema"""
    name: str = Field(description="Person's full name")
    role: str = Field(description="Job title or role")
    expertise: list[str] = Field(default=[], description="Areas of expertise")

class Collaboration(BaseModel):
    """Custom edge schema"""
    source: str = Field(description="First person's name")
    target: str = Field(description="Second person's name")
    project: str = Field(description="Project they worked on together")
    year: int = Field(description="Year of collaboration")

# Step 2: Configure LLM clients
# You can use any OpenAI-compatible endpoint by setting base_url
# Or use create_client() for simplified configuration
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# Step 3: Create configured AutoGraph
graph = AutoGraph[Person, Collaboration](
    node_schema=Person,
    edge_schema=Collaboration,
    # Define how to extract unique keys for deduplication
    node_key_extractor=lambda p: p.name,
    edge_key_extractor=lambda c: f"{c.source}-{c.target}-{c.project}",
    # Define how to extract node references from edges
    nodes_in_edge_extractor=lambda c: (c.source, c.target),
    # LLM clients
    llm_client=llm,
    embedder=embedder,
)

# Step 4: Extract
text = """
Dr. Sarah Chen and Dr. Michael Wang collaborated on the Climate AI project in 2023.
Sarah is a machine learning researcher with expertise in neural networks and climate modeling.
Michael specializes in data engineering and distributed systems.
"""

graph.feed_text(text)

# Step 5: Access results
print(f"Extracted {len(graph.nodes)} people")
for person in graph.nodes:
    print(f"- {person.name}: {person.role}")
    print(f"  Expertise: {', '.join(person.expertise)}")

print(f"\nExtracted {len(graph.edges)} collaborations")
for collab in graph.edges:
    print(f"- {collab.source} & {collab.target}: {collab.project} ({collab.year})")

# Step 6: Use built-in features
graph.build_index()

# Search
nodes, edges = graph.search("machine learning", top_k=2)
print(f"\nSearch found: {len(nodes)} people")

# Visualize
graph.show()
```

### Key Configuration Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `node_schema` / `edge_schema` | Yes | Pydantic model defining the structure |
| `node_key_extractor` | Yes | Function to extract unique key from node |
| `edge_key_extractor` | Yes | Function to extract unique key from edge |
| `nodes_in_edge_extractor` | Yes | Function to get (source, target) from edge |
| `llm_client` | Yes | LangChain-compatible LLM client |
| `embedder` | Yes | LangChain-compatible embeddings client |

### Comparison: Template vs Configured Auto-Type

| Aspect | Template | Configured Auto-Type |
|--------|----------|---------------------|
| Schema definition | YAML file | Python Pydantic classes |
| Extraction logic | Pre-built | Same pre-built logic |
| Deduplication | Pre-configured | You define key extractors |
| Language support | Built-in | You provide prompts |
| Reusability | Share YAML files | Package as Python module |

### More Configuration Examples

#### Temporal Graph

```python
from hyperknowledge import AutoTemporalGraph
from pydantic import BaseModel, Field

class Event(BaseModel):
    """Node: A historical event"""
    name: str = Field(description="Event name")
    category: str = Field(description="Type of event")

class CausalLink(BaseModel):
    """Edge: Time-aware causal relationship"""
    source: str = Field(description="Earlier event")
    target: str = Field(description="Later event")
    relationship: str = Field(description="How they connect")
    time: str = Field(description="When the link occurred")

timeline = AutoTemporalGraph[Event, CausalLink](
    node_schema=Event,
    edge_schema=CausalLink,
    node_key_extractor=lambda e: e.name,
    edge_key_extractor=lambda l: f"{l.source}-{l.target}-{l.time}",
    nodes_in_edge_extractor=lambda l: (l.source, l.target),
    llm_client=llm,
    embedder=embedder,
    # Temporal-specific: extract time from edge
    time_extractor=lambda l: l.time,
)

timeline.feed_text(historical_text)
```

---

## Common Operations

### Checking if Empty

```python
if result.empty():
    print("No data extracted")
else:
    print(f"Extracted {len(result.nodes)} nodes")
```

### Clearing Data

```python
# Clear all data
result.clear()

# Clear only index
result.clear_index()
```

### Merging Instances

```python
# Two separate extractions
result1 = ka.parse(text1)
result2 = ka.parse(text2)

# Merge into new instance
combined = result1 + result2
```

---

## Accessing Data

### Property Access

```python
result = ka.parse(text)

# Direct property access (Pydantic model)
nodes = result.nodes
edges = result.edges

# Dictionary conversion
data_dict = result.data.model_dump()
```

### JSON Export

```python
import json

# Export to JSON
json_data = result.data.model_dump_json(indent=2)

# Save to file
with open("output.json", "w") as f:
    f.write(json_data)
```

---

## Working with Results

### Iteration Patterns

```python
# Iterate nodes
for node in result.nodes:
    print(f"Name: {node.name}")
    print(f"Type: {node.type}")
    if hasattr(node, 'description'):
        print(f"Description: {node.description}")

# Iterate edges with filtering
for edge in result.edges:
    if edge.type == "worked_with":
        print(f"{edge.source} worked with {edge.target}")
```

### Filtering

```python
# Filter nodes by type
people = [n for n in result.nodes if n.type == "person"]
organizations = [n for n in result.nodes if n.type == "organization"]

# Filter edges
inventions = [e for e in result.edges if "invent" in e.type.lower()]
```

### Statistics

```python
# Basic counts
node_count = len(result.nodes)
edge_count = len(result.edges)

# Type distribution
from collections import Counter
node_types = Counter(n.type for n in result.nodes)
edge_types = Counter(e.type for e in result.edges)

print(f"Nodes: {node_types}")
print(f"Edges: {edge_types}")
```

---

## Advanced Usage

### Accessing the Schema

```python
# Access the schema
schema = result.data_schema

print(schema.model_fields)  # Available fields
```

### Raw Data Access

```python
# Access internal data if needed
internal_data = result._data
```

### Type Checking

```python
from hyperknowledge import AutoGraph, AutoList

# Check instance type
if isinstance(result, AutoGraph):
    print("Graph extraction")
elif isinstance(result, AutoList):
    print("List extraction")
```

---

## Best Practices

### Level 2 (Configured Auto-Types)

1. **Design schemas carefully** — Fields become LLM extraction targets
2. **Use clear Field descriptions** — Help LLM understand expectations
3. **Choose good key extractors** — Critical for deduplication
4. **Test with small samples** — Iterate on schema design

### General

1. **Check `hasattr` before optional fields** — Schema fields may vary
2. **Handle empty results** — Always check `empty()`
3. **Use `model_dump` for serialization** — Proper JSON conversion
4. **Leverage type hints** — IDE support for autocomplete

---

## See Also

**Prerequisites:**
- [Using Templates](using-templates.md) — Level 1 basics
- [Using Methods](using-methods.md) — Level 1 basics
- [Auto-Types Concepts](../../concepts/autotypes.md) — What each type does

**Next Steps:**
- [Creating Custom Templates](custom-templates.md) — Package your configurations
- [Incremental Updates](incremental-updates.md) — Add more documents
- [Search and Chat](search-and-chat.md) — Use extracted knowledge
- [Saving and Loading](saving-loading.md) — Persist your results
