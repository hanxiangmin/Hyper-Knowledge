# Search and Chat

!!! tip "Advanced - Post-Extraction"
    This guide covers using extracted knowledge. You should be comfortable with [Level 1: Using Templates](using-templates.md) first.

Query your knowledge abstract using semantic search and conversational AI.

---

## Overview

After extracting knowledge, you can interact with it in two ways:

- **Search** — Find specific entities and relations
- **Chat** — Have natural language conversations

Both require a **search index** to be built first.

---

## Building the Index

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "en")
result = ka.parse(text)

# Build search index
result.build_index()
```

**Note:** Index building is required before search/chat operations.

---

## Semantic Search

### Basic Search

```python
# Search for relevant items (returns tuple of nodes, edges)
nodes, edges = result.search("inventions", top_k=5)

for node in nodes:
    print(f"Node: {node.name}")
for edge in edges:
    print(f"Edge: {edge.source} -> {edge.target}")
```

### Search Parameters

```python
nodes, edges = result.search(
    query="electrical engineering achievements",
    top_k=10  # Number of results for both nodes and edges
)
```

### Working with Results

```python
nodes, edges = result.search("Nobel Prize")

# Process nodes
for node in nodes:
    print(f"Node: {node.name} ({node.type})")

# Process edges
for edge in edges:
    print(f"Edge: {edge.source} -> {edge.target}")
```

### Search Use Cases

```python
# Find specific people
people_nodes, people_edges = result.search("scientists who worked with Tesla", top_k=10)

# Find concepts
concept_nodes, concept_edges = result.search("alternating current system", top_k=5)

# Find events
event_nodes, event_edges = result.search("important dates in Tesla's life", top_k=10)
```

---

## Chat Interface

### Single Question

```python
# Ask a question
response = result.chat("What were Tesla's major achievements?")

print(response.content)
```

### Accessing Retrieved Context

```python
response = result.chat("What did Tesla invent?")

print(response.content)

# Access nodes and edges used to generate response
retrieved_nodes = response.additional_kwargs.get("retrieved_nodes", [])
retrieved_edges = response.additional_kwargs.get("retrieved_edges", [])
print(f"Based on {len(retrieved_nodes)} nodes and {len(retrieved_edges)} edges")
```

### Chat Parameters

```python
response = result.chat(
    query="Explain the War of Currents",
    top_k=10  # More context for complex questions
)
```

### Chat Use Cases

```python
# Summarization
summary = result.chat("Summarize Tesla's career in 3 sentences")

# Explanation
explanation = result.chat("What is the significance of the Tesla coil?")

# Comparison
comparison = result.chat("How did Tesla's approach differ from Edison's?")

# Timeline
timeline = result.chat("What happened in Tesla's life between 1880-1890?")
```

---

## Search vs Chat

| Feature | Search | Chat |
|---------|--------|------|
| **Returns** | Raw entities/relations | Natural language answer |
| **Speed** | Fast | Slower (LLM call) |
| **Use for** | Finding specific data | Understanding/explaining |
| **Precision** | Exact matches | Interpretive |
| **Output** | Structured | Free text |

### When to Use Each

**Use Search when:**
- You need specific entities
- Building reports or summaries
- Exporting data
- Fast lookup needed

**Use Chat when:**
- Explaining concepts
- Answering complex questions
- Summarizing content
- Interactive exploration

---

## Advanced Patterns

### Search then Chat

```python
# First, search for specific nodes
nodes, edges = result.search("wireless technology", top_k=5)

# Then, ask about them
if nodes:
    context = ", ".join([node.name for node in nodes])
    response = result.chat(f"Explain the significance of {context}")
    print(response.content)
```

### Iterative Exploration

```python
# Start broad
response = result.chat("What are the main topics in this document?")
print(response.content)

# Drill down
response = result.chat("Tell me more about the Tesla coil")
print(response.content)

# Specific question
response = result.chat("How does the Tesla coil work?")
print(response.content)
```

### Building a Research Assistant

```python
class ResearchAssistant:
    def __init__(self, ka_path):
        self.ka = Template.create("general/concept_graph", "en")
        self.ka.load(ka_path)
        self.ka.build_index()
    
    def ask(self, question):
        response = self.ka.chat(question)
        return response.content
    
    def find(self, query, n=5):
        return self.ka.search(query, top_k=n)
    
    def summarize(self):
        return self.ask("Summarize the main points of this paper")

# Usage
assistant = ResearchAssistant("./paper_kb/")
print(assistant.summarize())
print(assistant.ask("What are the limitations?"))
```

---

## Best Practices

### Search Tips

1. **Use natural language** — "wireless transmission" not "wireless"
2. **Be specific** — "Tesla's patents" not "Tesla"
3. **Increase top_k for broad queries** — `top_k=10` or more
4. **Filter results by type** — Check `hasattr(item, 'name')`

### Chat Tips

1. **Ask clear questions** — Specific questions get better answers
2. **Use context** — Build understanding progressively
3. **Adjust top_k** — Complex questions need more context
4. **Check sources** — Review `retrieved_nodes` and `retrieved_edges` for accuracy

---

## Troubleshooting

### "Index not built"

```python
# Error: Need to build index first
result.build_index()
```

### "No results found"

```python
# Try different phrasing
results = result.search("inventions")  # Try synonyms
results = result.search("discoveries")
results = result.search("contributions")

# Increase top_k
results = result.search("Tesla", top_k=20)
```

### "Irrelevant chat responses"

```python
# Increase context
response = result.chat(question, top_k=10)

# Or rephrase question
response = result.chat("Be more specific: ...")
```

---

## See Also

**Related Workflows:**
- [Incremental Updates](incremental-updates.md) — Add more content
- [Saving and Loading](saving-loading.md) — Persist for later use

**Basics:**
- [Using Templates](using-templates.md) — Level 1 fundamentals
- [Working with Auto-Types](working-with-autotypes.md) — Level 2 customization
