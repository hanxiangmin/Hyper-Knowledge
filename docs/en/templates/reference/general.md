# General Templates

Base types and common extraction tasks.

---

## Overview

General templates provide fundamental extraction capabilities suitable for a wide range of documents.

---

## Base Types

### base_model

**Purpose**: Basic structured data extraction

**Output**: Single structured object

**Use for**: Simple summaries, form-like data

=== "CLI"

    ```bash
    hk parse doc.md -t general/model -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/model", "en")
    result = ka.parse(doc_text)
    
    print(result.data)
    ```

**Output Schema**:
```python
{
    "field1": "value1",
    "field2": "value2"
}
```

---

### base_list

**Purpose**: Ordered collection extraction

**Output**: List of items

**Use for**: Sequences, rankings

=== "CLI"

    ```bash
    hk parse doc.md -t general/list -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/list", "en")
    result = ka.parse(doc_text)
    
    for item in result.data.items:
        print(f"- {item}")
    ```

**Output Schema**:
```python
{
    "items": ["item1", "item2", "item3"]
}
```

---

### base_set

**Purpose**: Unique collection extraction

**Output**: Set of unique items

**Use for**: Tags, categories, keywords

=== "CLI"

    ```bash
    hk parse doc.md -t general/set -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/set", "en")
    result = ka.parse(doc_text)
    
    for item in result.data.items:
        print(f"- {item}")
    ```

**Output Schema**:
```python
{
    "items": {"unique1", "unique2", "unique3"}
}
```

---

### base_graph

**Purpose**: Basic entity-relationship extraction

**Output**: Graph with entities and relations

**Use for**: Knowledge graphs, networks

=== "CLI"

    ```bash
    hk parse doc.md -t general/graph -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/graph", "en")
    result = ka.parse(doc_text)
    
    print(f"Entities: {len(result.nodes)}")
    print(f"Relations: {len(result.edges)}")
    ```

**Output Schema**:
```python
{
    "entities": [
        {"name": "Entity1", "type": "type1"},
        {"name": "Entity2", "type": "type2"}
    ],
    "relations": [
        {"source": "Entity1", "target": "Entity2", "type": "relates_to"}
    ]
}
```

---

## Specialized Templates

### biography_graph

**Type**: temporal_graph

**Purpose**: Extract person's life events and timeline

**Best for**: Biographies, profiles, memoirs

=== "CLI"

    ```bash
    hk parse tesla_bio.md -t general/biography_graph -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/biography_graph", "en")
    result = ka.parse(biography_text)
    
    # Build index for interactive features
    result.build_index()
    
    # Visualize life events (with search/chat capabilities)
    result.show()
    
    # Ask questions
    response = result.chat("What were the major achievements?")
    print(response.content)
    ```

**Features**:
- Extracts people, places, events
- Captures temporal relationships
- Timeline visualization

**Example Output**:
```python
{
    "entities": [
        {"name": "Nikola Tesla", "type": "person"},
        {"name": "AC Motor", "type": "invention"}
    ],
    "relations": [
        {
            "source": "Nikola Tesla",
            "target": "AC Motor",
            "type": "invented",
            "time": "1888"
        }
    ]
}
```

---

### concept_graph

**Type**: graph

**Purpose**: Extract concepts and their relationships

**Best for**: Research papers, technical documents, articles

=== "CLI"

    ```bash
    hk parse paper.md -t general/concept_graph -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/concept_graph", "en")
    result = ka.parse(paper_text)
    
    # Get concept map
    for node in result.nodes:
        print(f"Concept: {node.name}")
    
    for edge in result.edges:
        print(f"{edge.source} → {edge.target}")
    ```

**Features**:
- Concept identification
- Relationship mapping
- Hierarchical structures

---

### doc_structure

**Type**: model

**Purpose**: Extract document structure and outline

**Best for**: Long documents, reports, books

=== "CLI"

    ```bash
    hk parse report.md -t general/doc_structure -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/doc_structure", "en")
    result = ka.parse(report_text)
    
    print(f"Title: {result.data.title}")
    print(f"Sections: {len(result.data.sections)}")
    
    for section in result.data.sections:
        print(f"- {section.heading}")
    ```

**Features**:
- Section identification
- Heading hierarchy
- Key points per section

---

### workflow_graph

**Type**: graph

**Purpose**: Extract process workflows

**Best for**: Procedures, processes, workflows

=== "CLI"

    ```bash
    hk parse procedure.md -t general/workflow_graph -l en
    ```

=== "Python"

    ```python
    ka = Template.create("general/workflow_graph", "en")
    result = ka.parse(procedure_text)
    
    # Build index for visualization
    result.build_index()
    
    # Visualize workflow
    result.show()
    
    # Query workflow
    response = result.chat("What is the first step?")
    print(response.content)
    ```

**Features**:
- Step identification
- Flow relationships
- Decision points

---

## When to Use General Templates

### Use When:
- Document doesn't fit specific domain
- Need basic extraction
- Exploring/document type unknown
- Building custom workflows

### Don't Use When:
- Domain-specific template available (use that instead)
- Need specialized fields (create custom template)

---

## Examples

### Example 1: Simple Summary

```python
from hyperknowledge import Template

ka = Template.create("general/model", "en")
result = ka.parse("""
Meeting Notes:
Date: January 15, 2024
Attendees: Alice, Bob, Carol
Topic: Q1 Planning
Decision: Launch product in March
""")

print(result.data)
```

### Example 2: Biography Analysis

```python
ka = Template.create("general/biography_graph", "en")
result = ka.parse(biography_text)

# Build index for interactive features
result.build_index()

# Visualize life events (with search/chat capabilities)
result.show()

# Ask questions
response = result.chat("What were the major achievements?")
print(response.content)
```

### Example 3: Research Paper

```python
ka = Template.create("general/concept_graph", "en")
result = ka.parse(paper_text)

# Get concept map
for node in result.nodes:
    print(f"Concept: {node.name}")

for edge in result.edges:
    print(f"{edge.source} → {edge.target}")
```

---

## See Also

- [Template Overview](overview.md)
- [How to Choose](../how-to-choose.md)
- [Auto-Types](../../concepts/autotypes.md)
