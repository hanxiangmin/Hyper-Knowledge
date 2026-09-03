# Hyper-Knowledge CLI

> **"Stop reading. Start understanding."**

A powerful command-line tool for extracting structured knowledge from unstructured text.

---

## ⚡ Quick Start

```bash
# Install
uv tool install git+https://github.com/hanxiangmin/Hyper-Knowledge.git

# First-time setup
hk config init

# Extract knowledge from a document
hk parse document.md -o my_ka -l zh

# Visualize the knowledge graph
hk show my_ka

# Search within your Knowledge Abstract
hk search my_ka "key insights"
```

---

## ⚙️ Configuration

### One-Command Setup (Simplest)

```bash
# Just provide your API key - defaults work for most users
hk config init --api-key YOUR_API_KEY

# With custom base URL
hk config init -k YOUR_KEY -u https://your-endpoint.com/v1
```

This automatically configures both LLM and Embedder with:
- LLM: gpt-4o-mini
- Embedder: text-embedding-3-small

### Interactive Setup

```bash
hk config init
```

### Manual Configuration

For advanced users who need separate configurations:

```bash
# Configure LLM
hk config llm --api-key YOUR_KEY --model gpt-4o

# Configure Embedder
hk config embedder --api-key YOUR_KEY --model text-embedding-3-small
```

### Environment Variables

You can also use environment variables as an alternative:

```bash
export OPENAI_API_KEY=your_api_key
export OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
```

Environment variables take precedence over config file settings.

### View Current Configuration

```bash
hk config show
```

---

## 📄 Parse Command

Extract knowledge from documents into structured Knowledge Abstracts.

### Basic Usage

```bash
# Parse with interactive template selection
hk parse document.md -o my_ka -l zh

# Parse with specific template
hk parse document.md -o my_ka -t general/knowledge_graph -l zh

# Parse with specific method
hk parse document.md -o my_ka -m light_rag
```

### Options

- `<input>` - Input file path, directory, or `-` for stdin
- `-o, --output` - Output Knowledge Abstract directory (required)
- `-t, --template` - Template ID (omit for interactive selection)
- `-m, --method` - Method template (e.g., `light_rag`, `hyper_rag`)
- `-l, --lang` - Language (`zh` or `en`, required for knowledge templates)
- `-f, --force` - Force overwrite existing output
- `--no-index` - Skip building search index

### List Available Templates

```bash
hk list template
hk list template -l zh  # Filter by language
hk list template -a graph  # Filter by type
hk list template -q finance  # Search by keyword
```

### List Available Methods

```bash
hk list method
hk list method -q rag  # Search by keyword
```

---

## 🔍 Other Commands

### Build Search Index

Required for semantic search and chat functionality.

```bash
hk build-index my_ka
hk build-index my_ka --force  # Rebuild existing index
```

### Search Knowledge Abstract

Perform semantic search within your Knowledge Abstract.

```bash
hk search my_ka "What are the key findings?"
hk search my_ka "key insights" -n 5  # Return top 5 results
```

### Chat with Knowledge Abstract

Ask questions about your Knowledge Abstract.

```bash
# Single query
hk talk my_ka -q "What was discussed in the meeting?"

# Interactive mode
hk talk my_ka -i
```

### Visualize Knowledge Graph

View your Knowledge Abstract as an interactive graph.

```bash
hk show my_ka
```

### View Knowledge Abstract Info

Display statistics and metadata about your Knowledge Abstract.

```bash
hk info my_ka
```

### Add Knowledge to Existing KA

Append new knowledge to an existing Knowledge Abstract.

```bash
hk feed my_ka new_document.md
```

---

## 📝 Examples

### Example 1: Extract Financial Data

```bash
# Configure API keys
hk config init

# List finance templates
hk list template -l zh | grep finance

# Extract earnings report
hk parse earnings_report.md -o finance_ka -t finance/earnings_summary -l zh

# Build index for search
hk build-index finance_ka

# Search for insights
hk search finance_ka "What was the revenue growth?"
```

### Example 2: Extract Legal Contracts

```bash
# List legal templates
hk list template -l zh | grep legal

# Extract contract information
hk parse contract.md -o legal_ka -t legal/contract_summary -l zh

# View as knowledge graph
hk show legal_ka
```

### Example 3: Use Method Templates

```bash
# Use Light RAG method
hk parse document.md -o ka -m light_rag

# Use Hyper RAG method
hk parse document.md -o ka -m hyper_rag
```

---

## ❓ FAQ

### Q: How do I choose between template and method?

**A:** Use **templates** when you need domain-specific extraction (finance, legal, medicine, etc.). Use **methods** when you want algorithm-driven extraction (RAG-based approaches).

### Q: Why do I need to build an index?

**A:** The index enables semantic search and chat functionality. Without it, you can still extract and visualize knowledge, but search and talk commands won't work.

### Q: How do I switch between languages?

**A:** Use the `-l` or `--lang` option:
- `-l zh` for Chinese
- `-l en` for English

### Q: Can I use custom API endpoints?

**A:** Yes! Configure with `--base-url` to use API-compatible endpoints:
```bash
hk config llm --api-key YOUR_KEY --base-url https://your-custom-api.com/v1
```

### Q: Where is the configuration stored?

**A:** Configuration is stored in `~/.hk/config.toml`

### Q: How do I update my API key?

**A:** Simply run the configuration command again:
```bash
hk config llm --api-key NEW_API_KEY
```

---

## 🆘 Need Help?

```bash
# View all available commands
hk --help

# View help for specific command
hk parse --help
hk config --help
hk search --help
```

---

## 📚 Learn More

- [Full Documentation](../README.md)
- [Template Gallery](../templates/)
- [Examples](../examples/)
