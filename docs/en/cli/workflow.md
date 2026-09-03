# CLI Workflow Guide

This guide walks you through a complete knowledge extraction workflow using real-world examples.

---

## Scenario: Research Paper Analysis

Imagine you're a researcher who wants to extract and interact with knowledge from academic papers. Here's how to do it with Hyper-Knowledge.

---

## Step 1: Prepare Your Document

Hyper-Knowledge supports `.md` and `.txt` files. Download the sample research paper below to follow this guide:

<a href="../../assets/examples/en/transformer_paper.txt" download class="md-button">📥 Download Sample Document</a>

Save the file as `transformer_paper.md` in your working directory.

---

## Step 2: Extract Knowledge

Use the `parse` command to extract knowledge:

```bash
hk parse transformer_paper.md -t general/concept_graph -o ./transformer_kb/ -l en
```

**What happens:**
1. The document is read and chunked (if long)
2. LLM extracts entities and relationships
3. Results are saved to `./transformer_kb/`

**Output structure:**
```
./transformer_kb/
├── data.json       # Extracted knowledge
├── metadata.json   # Extraction metadata
└── index/          # Vector search index (if built)
```

---

## Step 3: Explore the Knowledge

### View Statistics

```bash
hk info ./transformer_kb/
```

**Output:**
```
Knowledge Abstract Info

Path          ./transformer_kb/
Template      general/concept_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:30:00
Nodes         12
Edges         15
Index         Built
```

### Visualize

```bash
hk show ./transformer_kb/
```

![Knowledge Graph Visualization](../../assets/en_show.jpg)

This opens an interactive graph in your browser showing:

- **Nodes**: Authors, concepts, models, metrics
- **Edges**: Relationships between them

---

## Step 4: Search for Information

### Semantic Search

Find information even if keywords don't match exactly:

```bash
hk search ./transformer_kb/ "neural network architecture"
```

**Results:**
```
Found 3 result(s):

Result 1:
{
  "name": "Transformer",
  "type": "model",
  "description": "A neural network architecture based solely on attention mechanisms"
}

Result 2:
{
  "name": "Attention Mechanism",
  "type": "concept",
  "description": "Mechanism to draw global dependencies between sequences"
}
...
```

### Specific Queries

```bash
hk search ./transformer_kb/ "performance metrics" -n 5
```

---

## Step 5: Chat with Your Knowledge

### Single Question

```bash
hk talk ./transformer_kb/ -q "What is the main contribution of this paper?"
```

**Response:**
```
The main contribution is the introduction of the Transformer architecture, 
which achieves state-of-the-art results on machine translation tasks while 
being more parallelizable and requiring significantly less training time than 
recurrent or convolutional architectures.
```

### Interactive Mode

```bash
hk talk ./transformer_kb/ -i
```

**Session:**
```
Entering interactive mode. Type 'exit' or 'quit' to stop.

> Who are the authors?
The paper was authored by Ashish Vaswani, Noam Shazeer, Niki Parmar, 
Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and 
Illia Polosukhin.

> What BLEU score did they achieve?
The model achieved a BLEU score of 28.4 on the WMT 2014 English-to-German 
translation task.

> exit
Goodbye!
```

---

## Step 6: Expand Your Knowledge Abstract

### Add Another Document

```bash
# Download another paper
curl -o bert_paper.md https://example.com/bert.md

# Add to existing knowledge abstract
hk feed ./transformer_kb/ bert_paper.md
```

### Verify the Update

```bash
hk info ./transformer_kb/
```

Notice the increased node/edge count and updated timestamp.

---

## Step 7: Rebuild Index (If Needed)

After adding documents, rebuild the search index:

```bash
hk build-index ./transformer_kb/
```

Or force a complete rebuild:

```bash
hk build-index ./transformer_kb/ -f
```

---

## Complete Script Example

Here's a bash script that automates the entire workflow:

```bash
#!/bin/bash

# Configuration
INPUT_FILE="paper.md"
OUTPUT_DIR="./paper_kb/"
TEMPLATE="general/concept_graph"
LANGUAGE="en"

echo "=== Hyper-Knowledge Workflow ==="
echo

# Step 1: Parse
echo "Step 1: Extracting knowledge..."
hk parse "$INPUT_FILE" -t "$TEMPLATE" -o "$OUTPUT_DIR" -l "$LANGUAGE"
echo

# Step 2: Info
echo "Step 2: Knowledge base info:"
hk info "$OUTPUT_DIR"
echo

# Step 3: Search example
echo "Step 3: Sample search:"
hk search "$OUTPUT_DIR" "main contributions" -n 2
echo

# Step 4: Open visualization
echo "Step 4: Opening visualization..."
hk show "$OUTPUT_DIR"

echo "=== Workflow Complete ==="
```

---

## Advanced: Batch Processing

Process multiple documents at once:

```bash
# Create output directories
mkdir -p ./ka/paper1 ./ka/paper2 ./ka/paper3

# Process each
hk parse papers/paper1.md -t general/concept_graph -o ./ka/paper1/ -l en
hk parse papers/paper2.md -t general/concept_graph -o ./ka/paper2/ -l en
hk parse papers/paper3.md -t general/concept_graph -o ./ka/paper3/ -l en

# Or use a loop
for file in papers/*.md; do
    name=$(basename "$file" .md)
    hk parse "$file" -t general/concept_graph -o "./ka/$name/" -l en
done
```

---

## Common Patterns

### Pattern 1: Continuous Knowledge Building

```bash
# Initial extraction
hk parse initial_doc.md -t general/biography_graph -o ./ka/ -l en

# Weekly updates
hk feed ./ka/ week1_update.md
hk feed ./ka/ week2_update.md
hk feed ./ka/ week3_update.md

# Monthly rebuild
hk build-index ./ka/ -f
```

### Pattern 2: Multi-Domain Project

```bash
# Technical documentation
hk parse api_docs.md -t general/concept_graph -o ./project_kb/tech/ -l en

# Legal contracts
hk parse contract.md -t legal/contract_obligation -o ./project_kb/legal/ -l en

# Financial reports
hk parse q4_report.md -t finance/earnings_summary -o ./project_kb/finance/ -l en
```

### Pattern 3: Compare Documents

```bash
# Extract two versions
hk parse draft_v1.md -t general/concept_graph -o ./ka/v1/ -l en
hk parse draft_v2.md -t general/concept_graph -o ./ka/v2/ -l en

# Compare via chat
hk talk ./ka/v1/ -q "What are the main topics?"
hk talk ./ka/v2/ -q "What are the main topics?"
```

---

## Troubleshooting Tips

| Issue | Solution |
|-------|----------|
| Extraction is slow | Long documents are chunked; use `--no-index` to skip indexing during parse |
| Search returns nothing | Ensure index is built: `hk build-index ./ka/` |
| Template not found | List available: `hk list template` |
| Out of memory | Reduce chunk size in config or process smaller documents |

---

## Next Steps

- Learn about [all CLI commands](commands/parse.md)
- Explore the [Template Library](../templates/index.md)
- Read about [choosing the right Auto-Type](../concepts/autotypes.md)
