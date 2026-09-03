# Python Quickstart

Get your first knowledge extraction running in 5 minutes using Python.

---

## Prerequisites

- [Hyper-Knowledge installed](installation.md)

---

## Step 1: Set Up Your Project

Create a new directory and set up your environment:

```bash
mkdir my_extraction_project
cd my_extraction_project

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install hyperknowledge
pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

---

## Step 2: Configure Your Model

**Option A — OpenAI (default)**

Create a `.env` file:

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

**Option B — Other providers (Anthropic, DeepSeek, Bailian, vLLM)**

Set the appropriate environment variables in `.env`:

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx          # for embeddings

# DeepSeek
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx          # for embeddings

# Bailian (Alibaba Cloud)
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

Then configure the client in your script:

```python
from hyperknowledge import create_client, Template

# Example: DeepSeek LLM + OpenAI embedder
llm, emb = create_client(llm="deepseek", embedder="openai:text-embedding-3-small")
ka = Template.create("general/biography_graph", language="en", llm_client=llm, embedder=emb)
```

See the [Provider Configuration Guide](../python/guides/provider-configuration.md) for full details.

---

## Step 3: Create Your First Extraction Script

Create a file `extract.py`:

```python
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

from hyperknowledge import Template

# Create a template instance
ka = Template.create("general/biography_graph", language="en")

# Sample text
text = """
Nikola Tesla was a Serbian-American inventor, electrical engineer, 
mechanical engineer, and futurist. He is best known for his 
contributions to the design of the modern alternating current 
(AC) electricity supply system.

Born: July 10, 1856, Smiljan, Croatia
Died: January 7, 1943, New York City, NY

Tesla immigrated to the United States in 1884 and briefly worked 
with Thomas Edison before the two parted ways due to conflicting 
business and scientific interests. He later established his own 
laboratory and developed numerous revolutionary inventions, 
including the Tesla coil, induction motor, and wireless transmission 
technologies.

Despite his brilliance, Tesla struggled financially in his later years
and died impoverished in a New York hotel room. His legacy was 
largely overlooked during his lifetime but has since been recognized 
worldwide, with the Tesla unit of magnetic flux density named in his honor.
"""

# Extract knowledge
result = ka.parse(text)

# Access the extracted data
print(f"Nodes: {len(result.nodes)}")
print(f"Edges: {len(result.edges)}")

# Print first node
if result.nodes:
    node = result.nodes[0]
    print(f"\nFirst node: {node.name} ({node.type})")

# Build index for search/chat capabilities
result.build_index()

# Visualize
result.show()
```

![Knowledge Graph Visualization](../../assets/en_show.jpg)

---

## Step 4: Run the Script

```bash
python extract.py
```

You should see:

```
Entities: 5
Relations: 4

First entity: Nikola Tesla (person)
```

And a browser window will open showing the interactive knowledge graph.

![Knowledge Graph Visualization](../../assets/en_show.jpg)

---

## Step 5: Working with Results

Access different parts of the extraction:

```python
# Iterate over all nodes
for node in result.nodes:
    print(f"- {node.name}: {node.description}")

# Iterate over all edges
for edge in result.edges:
    print(f"- {edge.source} --{edge.type}--> {edge.target}")

# Search within the knowledge abstract
result.build_index()
nodes, edges = result.search("inventions", top_k=3)
for node in nodes:
    print(f"Node: {node.name}")
for edge in edges:
    print(f"Edge: {edge.source} -> {edge.target}")
```

---

## Step 6: Save and Load

Save your knowledge abstract for later use:

```python
# Save to disk
result.dump("./my_ka/")

# Load it back later
new_ka = Template.create("general/biography_graph", language="en")
new_ka.load("./my_ka/")
```

---

## Step 7: Incremental Updates

Add more text without losing existing knowledge:

```python
additional_text = """
Tesla worked for Thomas Edison in New York City in 1884. 
They had a contentious relationship due to differing views on DC vs AC power.
"""

# Feed adds to existing knowledge
result.feed_text(additional_text)

# Rebuild index after feeding new data
result.build_index()

# Visualize the updated graph
result.show()
```

![Updated Knowledge Graph Visualization](../../assets/en_show.jpg)

---

## Complete Example

Here's a complete, production-ready script:

```python
"""Extract knowledge from a document and interact with it."""

import os
from pathlib import Path
from dotenv import load_dotenv
from hyperknowledge import Template

# Configuration
load_dotenv()

INPUT_FILE = "document.txt"
OUTPUT_DIR = "./output/"
TEMPLATE = "general/biography_graph"
LANGUAGE = "en"


def main():
    # Create template
    print(f"Creating template: {TEMPLATE}")
    ka = Template.create(TEMPLATE, language=LANGUAGE)
    
    # Read document
    print(f"Reading: {INPUT_FILE}")
    text = Path(INPUT_FILE).read_text(encoding="utf-8")
    
    # Extract knowledge
    print("Extracting knowledge...")
    result = ka.parse(text)
    
    # Print summary
    print(f"\nExtraction complete:")
    print(f"  - Nodes: {len(result.nodes)}")
    print(f"  - Edges: {len(result.edges)}")
    
    # Build search index
    print("Building search index...")
    result.build_index()
    
    # Save to disk
    print(f"Saving to: {OUTPUT_DIR}")
    result.dump(OUTPUT_DIR)
    
    # Interactive visualization
    print("Opening visualization...")
    result.show()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
```

![Interactive Knowledge Graph Visualization](../../assets/en_show.jpg)

---

## What's Next?

- [Python SDK Overview](../python/index.md) — Complete API reference
- [Working with Templates](../python/guides/using-templates.md) — Template usage guide
- [Auto-Types Guide](../concepts/autotypes.md) — Choose the right data structure

---

## Troubleshooting

**"No module named 'hyperknowledge'"**
→ Run `pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"`

**"API key not found"**
→ Check your `.env` file or set `OPENAI_API_KEY` environment variable

**"Template not found"**
→ Use `Template.list()` to see available templates
