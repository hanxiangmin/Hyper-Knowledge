# Using Templates

!!! tip "Level 1 - Beginner"
    This guide is for beginners. Before reading, please complete the [Quickstart](../quickstart.md).

Learn how to use and customize templates for knowledge extraction.

---

## What Are Templates?

Templates are pre-configured extraction setups that combine:

- **Auto-Type** — Output data structure
- **Prompts** — Instructions for the LLM
- **Schema** — Field definitions and types
- **Guidelines** — Extraction rules and constraints

---

## Built-in Templates

Hyper-Knowledge includes 80+ templates across 6 domains:

| Domain | Templates | Use Cases |
|--------|-----------|-----------|
| `general` | Base types, biography, concept graph | Common extraction tasks |
| `finance` | Earnings, risk, ownership, timeline | Financial analysis |
| `legal` | Contracts, cases, compliance | Legal document processing |
| `medicine` | Anatomy, drugs, treatments | Medical text analysis |
| `tcm` | Herbs, formulas, syndromes | Traditional Chinese Medicine |
| `industry` | Equipment, safety, operations | Industrial documentation |

---

## Creating Templates

### From Preset

```python
from hyperknowledge import Template

# Basic usage
ka = Template.create("general/biography_graph", language="en")

# With custom clients
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o")
emb = OpenAIEmbeddings()

ka = Template.create(
    "general/biography_graph",
    language="en",
    llm_client=llm,
    embedder=emb
)
```

### From File

```python
# Load custom YAML template
ka = Template.create(
    "/path/to/my_template.yaml",
    language="en"
)
```

### From Method

```python
# Use extraction method instead of template
ka = Template.create("method/light_rag")
```

---

## Listing Templates

### All Templates

```python
from hyperknowledge import Template

templates = Template.list()

for path, cfg in templates.items():
    print(f"{path}: {cfg.description}")
```

### Filtered Listing

```python
# By type
graphs = Template.list(filter_by_type="graph")

# By tag
biography = Template.list(filter_by_tag="biography")

# By language
zh_templates = Template.list(filter_by_language="zh")

# Combined
results = Template.list(
    filter_by_type="graph",
    filter_by_language="en"
)
```

### Search Templates

```python
# Search in name and description
results = Template.list(filter_by_query="financial")
```

---

## Template Configuration

### Getting Template Info

```python
from hyperknowledge import Template

# Get template configuration
cfg = Template.get("general/biography_graph")

print(cfg.name)        # biography_graph
print(cfg.type)        # temporal_graph
print(cfg.description) # Template description
```

### Template Properties

```python
cfg = Template.get("general/biography_graph")

# Properties
print(cfg.name)           # Template name
print(cfg.type)           # Auto-Type (graph, list, etc.)
print(cfg.description)    # Human-readable description
print(cfg.tags)           # Associated tags
print(cfg.language)       # Supported languages
```

---

## Understanding Template Outputs

`Template.create` returns an **AutoType** object. Different templates use different AutoTypes, so the way you access extracted results varies:

| Type | AutoType | Typical Access | Use Case |
|------|----------|----------------|----------|
| **Model** | `AutoModel` | `result.data.field_name` | Reports, profiles, structured objects |
| **List** | `AutoList` | `result.data.items` | Ordered collections, steps |
| **Set** | `AutoSet` | `result.data.items` | Deduplicated tags, keywords |
| **Graph** | `AutoGraph` | `result.nodes` / `result.edges` | Binary entity relationships |
| **Hypergraph** | `AutoHypergraph` | `result.nodes` / `result.edges` | Multi-entity relationships |
| **Temporal Graph** | `AutoTemporalGraph` | `result.nodes` / `result.edges` (with `time`) | Timelines, biographies |
| **Spatial Graph** | `AutoSpatialGraph` | `result.nodes` / `result.edges` (with `location`) | Geographic networks |
| **Spatio-Temporal Graph** | `AutoSpatioTemporalGraph` | `result.nodes` / `result.edges` (with `time` + `location`) | Historical events |

!!! info "Related Docs"
    - Learn more about the design and use cases of each AutoType in [Auto-Types Concepts](../../concepts/autotypes.md).
    - Learn how to customize schemas and configs in [Working with Auto-Types](working-with-autotypes.md).

### Quick Examples

#### Model (AutoModel)

```python
ka = Template.create("finance/earnings_summary", "en")
result = ka.parse(report_text)

print(result.data.company_name)
print(result.data.revenue)
```

#### List (AutoList)

```python
ka = Template.create("general/list", "en")
result = ka.parse(text)

for item in result.data.items:
    print(item)
```

#### Set (AutoSet)

```python
ka = Template.create("general/set", "en")
result = ka.parse(text)

for item in result.data.items:
    print(item)  # deduplicated
```

#### Graph (AutoGraph)

```python
ka = Template.create("general/graph", "en")
result = ka.parse(text)

for node in result.nodes:
    print(f"{node.name} ({node.type})")

for edge in result.edges:
    print(f"{edge.source} --{edge.type}--> {edge.target}")
```

---

## Common Template Patterns

### Pattern 1: Biography Analysis

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "en")

with open("biography.md") as f:
    result = ka.parse(f.read())

# Access timeline data
for edge in result.edges:
    if hasattr(edge, 'time'):
        print(f"{edge.time}: {edge.source} -> {edge.target}")

# Build index for interactive visualization
result.build_index()

result.show()  # Visualize life timeline with search/chat
```

![Interactive Visualization](../../../assets/en_show.jpg)

### Pattern 2: Financial Report

```python
from hyperknowledge import Template

ka = Template.create("finance/earnings_summary", "en")

report = ka.parse(earnings_text)

# Access financial data
print(f"Revenue: {report.data.revenue}")
print(f"EPS: {report.data.eps}")
print(f"Growth: {report.data.yoy_growth}%")
```

### Pattern 3: Legal Contract

```python
from hyperknowledge import Template

ka = Template.create("legal/contract_obligation", "en")

contract = ka.parse(contract_text)

# List obligations
for obligation in contract.data.obligations:
    print(f"Party: {obligation.party}")
    print(f"Obligation: {obligation.description}")
    print(f"Deadline: {obligation.deadline}")
```

### Pattern 4: Research Paper

```python
from hyperknowledge import Template

ka = Template.create("general/concept_graph", "en")

paper = ka.parse(paper_text)

# Build searchable knowledge abstract
paper.build_index()

# Query findings
response = paper.chat("What are the main contributions?")
print(response.content)
```

---

## Multi-Language Support

Templates support both English and Chinese:

```python
# English document
ka_en = Template.create("general/biography_graph", "en")
result_en = ka_en.parse(english_text)

# Chinese document
ka_zh = Template.create("general/biography_graph", "zh")
result_zh = ka_zh.parse(chinese_text)
```

**Note:** Use the language that matches your document for best results.

---

## Template Caching

Templates are loaded and cached for efficiency:

```python
# First call loads template
ka1 = Template.create("general/biography_graph", "en")

# Second call uses cached version
ka2 = Template.create("general/biography_graph", "en")

# Both are independent instances with same configuration
```

---

## Error Handling

### Template Not Found

```python
from hyperknowledge import Template

try:
    ka = Template.create("nonexistent/template")
except ValueError as e:
    print(f"Template not found: {e}")
    
    # List available
    available = Template.list()
    print("Available templates:", list(available.keys()))
```

### Language Not Supported

```python
cfg = Template.get("general/biography_graph")
print(cfg.language)  # Check supported languages

# Will raise error if language not supported
ka = Template.create("general/biography_graph", "fr")  # May fail
```

---

## Best Practices

1. **Choose domain-specific templates** — Better results than generic ones
2. **Match language to document** — Improves extraction quality
3. **Cache template instances** — Reuse for multiple documents
4. **Check template output schema** — Know what fields to expect

---

## See Also

**Next Steps:**
- [Working with Auto-Types](working-with-autotypes.md) — Level 2: Custom schemas
- [Creating Custom Templates](custom-templates.md) — Level 2+: Write your own templates

**Reference:**
- [Template Library](../../templates/index.md) — Browse all templates
- [Using Methods](using-methods.md) — When to use methods instead
