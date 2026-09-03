# Research Assistant Tutorial

Build an interactive research assistant from academic papers.

---

## What You'll Build

By the end of this tutorial, you'll have a research assistant that can:
- Extract structured knowledge from research papers
- Answer questions about the paper's content
- Find relevant sections based on semantic search
- Visualize concept relationships

---

## Tutorial Overview

| Step | Topic | What You'll Learn |
|------|-------|-------------------|
| 1 | [Extract Knowledge](step1-extract.md) | Parse a research paper and extract concepts |
| 2 | [Semantic Search](step2-search.md) | Build a searchable knowledge abstract |
| 3 | [Q&A System](step3-chat.md) | Create an interactive Q&A interface |

---

## Prerequisites

- Hyper-Knowledge installed: `pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"`
- OpenAI API key configured
- A research paper (PDF or text format)

---

## Example Use Cases

### Use Case 1: Paper Review

Quickly understand a new paper by asking questions:
- "What are the main contributions?"
- "How does this compare to prior work?"
- "What are the limitations?"

### Use Case 2: Literature Review

Build a knowledge abstract from multiple papers:
- Extract concepts from 10+ papers
- Search across all papers
- Find connections between works

### Use Case 3: Teaching Assistant

Help students understand complex papers:
- Visualize concept maps
- Answer student questions
- Generate summaries

---

## Project Structure

```
research-assistant/
├── paper.md              # Your research paper
├── knowledge_base/       # Extracted knowledge
├── research_assistant.py # Main application
└── requirements.txt      # Dependencies
```

---

## Next Steps

Ready to start? Begin with [Step 1: Extract Knowledge](step1-extract.md).
