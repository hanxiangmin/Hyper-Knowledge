# Creating Custom Templates

!!! tip "Level 2+ - Intermediate Extension"
    This guide shows how to create reusable templates. Before reading, complete [Level 1: Using Templates](using-templates.md) or [Level 2: Working with Auto-Types](working-with-autotypes.md).

Learn how to create your own templates for specialized extraction tasks.

---

## Overview

Custom templates allow you to define:

- **Output schema** — What entities and relationships to extract
- **Extraction rules** — Guidelines for the LLM
- **Display configuration** — How to visualize results

---

## Quick Start

### 1. Create Template File

Create a YAML file in `~/.hyperknowledge/templates/`:

```bash
mkdir -p ~/.hyperknowledge/templates/my_domain
```

### 2. Define Template Structure

```yaml
language: [zh, en]

name: my_template
type: graph
tags: [custom, domain]

description:
  zh: "自定义模板描述"
  en: "Custom template description"

output:
  description:
    zh: "输出描述"
    en: "Output description"
  entities:
    description:
      zh: "实体描述"
      en: "Entity description"
    fields:
      - name: name
        type: str
        description:
          zh: "名称"
          en: "Name"
        required: true
      - name: category
        type: str
        description:
          zh: "类别"
          en: "Category"
        required: true

  relations:
    description:
      zh: "关系描述"
      en: "Relation description"
    fields:
      - name: type
        type: str
        description:
          zh: "关系类型"
          en: "Relation type"
        required: true

guideline:
  target:
    zh: "提取目标描述"
    en: "Extraction target description"
  rules_for_entities:
    zh:
      - "规则1"
      - "规则2"
    en:
      - "Rule 1"
      - "Rule 2"
  rules_for_relations:
    zh:
      - "关系规则1"
    en:
      - "Relation rule 1"

identifiers:
  entity_id: name
  relation_id: "{source}|{type}|{target}"
  relation_members:
    source: source
    target: target

display:
  entity_label: "{name} ({category})"
  relation_label: "{type}"
```

### 3. Validate and Use

```python
from hyperknowledge import Template

# Load your custom template
ka = Template.create("my_domain/my_template", "en")

# Use it
result = ka.parse("Your document text here")
```

---

## Field Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | String value | `"Hello"` |
| `int` | Integer | `42` |
| `float` | Floating point | `3.14` |
| `bool` | Boolean | `true` |
| `list[str]` | List of strings | `["a", "b"]` |
| `datetime` | Date/time | `"2024-01-01"` |
| `enum` | Enumerated values | See below |

### Enum Type

For fields with predefined values:

```yaml
- name: priority
  type: str
  description:
    zh: "优先级: high/medium/low"
    en: "Priority: high/medium/low"
  required: true
```

---

## Auto-Types

Choose the appropriate Auto-Type for your data:

| Type | Use Case | Features |
|------|----------|----------|
| `graph` | General knowledge graphs | Entities + Relations |
| `temporal_graph` | Time-series data | + Temporal events |
| `spatial_graph` | Geospatial data | + Location coordinates |
| `hypergraph` | Complex relationships | + Hyperedges |
| `tree` | Hierarchical data | Parent-child structure |
| `table` | Structured records | Row-based data |

---

## Best Practices

### 1. Clear Descriptions

Write detailed descriptions to guide the LLM:

```yaml
# Good
description:
  en: "Extract product information including name, price, and category"

# Bad
description:
  en: "Product info"
```

### 2. Specific Rules

Provide concrete extraction rules:

```yaml
guideline:
  rules_for_entities:
    en:
      - "Only extract products mentioned in the pricing section"
      - "Category must be one of: electronics, clothing, food, other"
      - "Round prices to 2 decimal places"
```

### 3. Required Fields

Mark critical fields as required:

```yaml
fields:
  - name: id
    type: str
    required: true  # Extraction will fail if missing
  - name: notes
    type: str
    required: false  # Optional field
```

### 4. Validation

Test your template with sample documents:

```python
# Test extraction
test_doc = """
Sample document text for testing...
"""

result = ka.parse(test_doc)
print(result.data.entities)
print(result.data.relations)
```

---

## Example: Product Catalog Template

```yaml
language: [zh, en]

name: product_catalog
type: table
tags: [ecommerce, products]

description:
  zh: "从商品目录中提取产品信息"
  en: "Extract product information from catalogs"

output:
  description:
    zh: "产品信息表"
    en: "Product information table"
  entities:
    description:
      zh: "产品实体"
      en: "Product entities"
    fields:
      - name: sku
        type: str
        description:
          zh: "产品SKU（唯一标识）"
          en: "Product SKU (unique identifier)"
        required: true
      - name: name
        type: str
        description:
          zh: "产品名称"
          en: "Product name"
        required: true
      - name: price
        type: float
        description:
          zh: "价格（数字）"
          en: "Price (numeric value)"
        required: true
      - name: category
        type: str
        description:
          zh: "类别：electronics/clothing/food/home/other"
          en: "Category: electronics/clothing/food/home/other"
        required: true
      - name: in_stock
        type: bool
        description:
          zh: "是否有库存"
          en: "Whether in stock"
        required: false

guideline:
  target:
    zh: "提取所有产品信息，忽略缺货商品"
    en: "Extract all product info, skip out-of-stock items"
  rules_for_entities:
    en:
      - "Extract products from tables and bullet lists"
      - "Convert price strings to numeric values"
      - "Map category names to standard values"
      - "Set in_stock=false if explicitly mentioned as out of stock"

identifiers:
  entity_id: sku

display:
  entity_label: "{name} (${price})"
```

---

## Using Method Classes Directly

If you need full control over the extraction process, you can instantiate method classes directly instead of going through `Template.create`:

```python
from hyperknowledge.methods import Light_RAG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Create method instance directly
llm = ChatOpenAI()
emb = OpenAIEmbeddings()

method = Light_RAG(
    llm_client=llm,
    embedder=emb,
    # Method-specific parameters
    chunk_size=1024,
    max_workers=5
)

# Extract knowledge
result = method.parse(text)
```

This approach is useful for advanced scenarios where you want to bypass the Template layer and tune algorithm parameters directly.

---

## Registering Custom Methods

You can also register custom extraction methods and use them through the Template API:

```python
from hyperknowledge.methods import register_method

class MyCustomMethod:
    def __init__(self, llm_client, embedder, **kwargs):
        self.llm_client = llm_client
        self.embedder = embedder
    
    def parse(self, text):
        # Your extraction logic
        pass

# Register the method
register_method(
    name="my_method",
    method_class=MyCustomMethod,
    autotype="graph",
    description="My custom extraction method"
)

# Use via Template API
from hyperknowledge import Template
ka = Template.create("method/my_method")
```

---

## Sharing Templates

### Register Globally

Place templates in the system directory:

```bash
# System-wide (all users)
/usr/share/hyperknowledge/templates/

# User-specific
~/.hyperknowledge/templates/
```

### Template Registry

To share with the community:

1. Fork the [Hyper-Knowledge repository](https://github.com/hanxiangmin/Hyper-Knowledge)
2. Add your template to `hyperknowledge/templates/`
3. Submit a pull request

---

## Troubleshooting

### Template Not Found

```python
# Check template path
Template.list_available()  # List all templates

# Verify directory
import os
print(os.listdir("~/.hyperknowledge/templates/"))
```

### Poor Extraction Quality

1. **Add more examples** in guidelines
2. **Refine field descriptions** with specific constraints
3. **Split complex templates** into smaller ones
4. **Use stricter rules** to constrain output

### Validation Errors

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('template.yaml'))"
```

---

## See Also

**Prerequisites:**
- [Template Format Reference](../../concepts/templates-format.md) — Complete YAML specification
- [Using Templates](using-templates.md) — Level 1: Basic template usage

**Advanced Usage:**
- [Incremental Updates](incremental-updates.md) — Add more documents
- [Search and Chat](search-and-chat.md) — Use extracted knowledge
- [Template Library](../../templates/index.md) — Browse existing templates
