# Python Quickstart

Get started with the Hyper-Knowledge Python SDK in 5 minutes.

---

## Prerequisites

- Python 3.11+
- OpenAI API key

## Installation

```bash
pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

## Basic Usage

### 1. Configure API Key

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

Or use a `.env` file:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Extract Knowledge

```python
from hyperknowledge import Template

# Create a template
ka = Template.create("general/biography_graph", language="en")

# Your text
text = """
Marie Curie was a Polish-French physicist and chemist who conducted 
pioneering research on radioactivity. She was the first woman to win 
a Nobel Prize and the only person to win Nobel Prizes in two different 
scientific fields.
"""

# Extract
result = ka.parse(text)

# Access results
print(f"Nodes: {len(result.nodes)}")
print(f"Edges: {len(result.edges)}")

# Print first node
if result.nodes:
    node = result.nodes[0]
    print(f"\nFirst: {node.name} ({node.type})")
    print(f"Description: {node.description}")
```

**Output:**
```
Entities: 5
Relations: 4

First: Marie Curie (person)
Description: Polish-French physicist and chemist
```

### 3. Visualize

```python
# Build index for search/chat capabilities
result.build_index()

# Open interactive visualization
result.show()
```

![Interactive Visualization](../../assets/en_show.jpg)

### 4. Search

```python
# Build search index
result.build_index()

# Search
results = result.search("Nobel Prize", top_k=3)
for item in results:
    print(item)
```

### 5. Chat

```python
# Ask questions
response = result.chat("What did Marie Curie discover?")
print(response.content)
```

### 6. Save and Load

```python
# Save to disk
result.dump("./curie_kb/")

# Load later
new_ka = Template.create("general/biography_graph", language="en")
new_ka.load("./curie_kb/")
```

---

## Complete Example

```python
"""Complete example: Extract, explore, and save knowledge."""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template

def main():
    # Create template
    print("Creating template...")
    ka = Template.create("general/biography_graph", language="en")
    
    # Sample text
    text = """
    Ada Lovelace was an English mathematician and writer, chiefly known 
    for her work on Charles Babbage's early mechanical general-purpose 
    computer, the Analytical Engine. She is often regarded as the first 
    computer programmer.
    """
    
    # Extract knowledge
    print("Extracting knowledge...")
    result = ka.parse(text)
    
    # Display results
    print(f"\nExtraction Results:")
    print(f"  Nodes: {len(result.nodes)}")
    print(f"  Edges: {len(result.edges)}")

    # List nodes
    print("\nNodes found:")
    for node in result.nodes:
        print(f"  - {node.name} ({node.type})")
    
    # Build index and search
    print("\nBuilding search index...")
    result.build_index()
    
    search_nodes, search_edges = result.search("computer programming", top_k=2)
    print(f"\nSearch results: {len(search_nodes)} nodes, {len(search_edges)} edges")
    
    # Save
    print("\nSaving knowledge abstract...")
    result.dump("./ada_kb/")
    
    print("\nDone! Try: hk show ./ada_kb/")

if __name__ == "__main__":
    main()
```

---

## Next Steps

- Learn about [Core Concepts](core-concepts.md)
- Read [Using Templates Guide](guides/using-templates.md)
- Explore [API Reference](api-reference/template.md)
