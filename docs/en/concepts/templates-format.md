# Template Format

Complete reference for YAML template structure.

---

## Overview

Templates are YAML files that define:
- **Output schema** — What to extract
- **Prompts** — How to instruct the LLM
- **Guidelines** — Extraction rules
- **Configuration** — Display and identifiers

---

## Template Structure

```yaml
language: [zh, en]           # Supported languages

name: template_name          # Template identifier
type: graph                  # Auto-Type
tags: [domain, category]     # Classification tags

description:                 # Human-readable description
  zh: "中文描述"
  en: "English description"

output:                      # Output schema definition
  description:
    zh: "输出描述"
    en: "Output description"
  entities:                  # Entity schema
    description:
      zh: "实体描述"
      en: "Entity description"
    fields:
      - name: field_name
        type: str
        description:
          zh: "字段描述"
          en: "Field description"
        required: true
  relations:                 # Relation schema (for graphs)
    # Same structure as entities

guideline:                   # LLM instructions
  target:
    zh: "提取目标"
    en: "Extraction target"
  rules_for_entities:
    zh: ["规则1", "规则2"]
    en: ["Rule 1", "Rule 2"]
  rules_for_relations:
    zh: ["规则1"]
    en: ["Rule 1"]

identifiers:                 # ID generation rules
  entity_id: name            # Field used as entity ID
  relation_id: "{source}|{type}|{target}"  # Relation ID format
  relation_members:
    source: source
    target: target

display:                     # Visualization settings
  entity_label: "{name} ({type})"
  relation_label: "{type}"
```

---

## Field Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | String | `"Hello"` |
| `int` | Integer | `42` |
| `float` | Float | `3.14` |
| `bool` | Boolean | `true` |
| `list[str]` | List of strings | `["a", "b"]` |
| `datetime` | Date/time | `"2024-01-01"` |

---

## Complete Example

```yaml
language: [zh, en]

name: biography_graph
type: temporal_graph
tags: [general, biography, life, events, timeline]

description:
  zh: '传记图模板 - 从人物传记、回忆录、年谱中提取实体和关系'
  en: 'Biography Graph Template - Extract entities and relationships from biographies'

output:
  description:
    zh: '人物传记中的实体和关系网络'
    en: "Entity and relationship network from biographies"
  
  entities:
    description:
      zh: '传记中的实体'
      en: 'Entities in the biography'
    fields:
      - name: name
        type: str
        description:
          zh: '实体名称'
          en: 'Entity name'
        required: true
      
      - name: type
        type: str
        description:
          zh: '实体类型：人物、地点、组织、作品、事件、成就等'
          en: 'Entity type: person, location, organization, work, event, achievement'
        required: true
      
      - name: description
        type: str
        description:
          zh: '实体描述'
          en: 'Entity description'
        required: false
  
  relations:
    description:
      zh: '实体之间的关系'
      en: 'Relationships between entities'
    fields:
      - name: source
        type: str
        description:
          zh: '关系起点实体'
          en: 'Source entity'
        required: true
      
      - name: target
        type: str
        description:
          zh: '关系终点实体'
          en: 'Target entity'
        required: true
      
      - name: type
        type: str
        description:
          zh: '关系类型'
          en: 'Relation type'
        required: true
      
      - name: time
        type: str
        description:
          zh: '关系对应的时间'
          en: 'Time associated with the relation'
        required: false

guideline:
  target:
    zh: '你是一位专业的传记分析师...'
    en: 'You are a professional biography analyst...'
  
  rules_for_entities:
    zh:
      - '提取传记主人公作为核心实体'
      - '同一实体在全文中保持命名一致'
    en:
      - 'Extract the biographical subject as the core entity'
      - 'Maintain consistent naming for the same entity'
  
  rules_for_relations:
    zh:
      - '仅在文本明确表达两个实体之间存在关系时创建关系'
    en:
      - 'Create relationships only when explicitly expressed'
  
  rules_for_time:
    zh:
      - '绝对日期：保持原文格式'
      - '相对时间：转换为绝对时间'
    en:
      - 'Absolute dates: Keep as-is'
      - 'Relative time: Convert to absolute'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target
  time_field: time

display:
  entity_label: '{name}'
  relation_label: '{type}'
```

---

## Auto-Type Specific Sections

### For Lists/Sets

```yaml
output:
  items:                       # Instead of entities/relations
    description:
      zh: "列表项"
      en: "List items"
    fields:
      - name: value
        type: str
```

### For Models

```yaml
output:
  fields:                      # Direct fields (no entities)
    - name: company_name
      type: str
    - name: revenue
      type: float
```

### For Temporal Graphs

```yaml
guideline:
  rules_for_time:              # Time extraction rules
    zh: ["规则1", "规则2"]
    en: ["Rule 1", "Rule 2"]

identifiers:
  time_field: time             # Which field contains time
```

### For Spatial Graphs

```yaml
output:
  entities:
    fields:
      - name: location         # Location field
        type: str
      - name: coordinates      # Optional coordinates
        type: str

guideline:
  rules_for_location:          # Location extraction rules
    zh: ["规则1"]
    en: ["Rule 1"]
```

---

## Template Variables

Use placeholders in guidelines:

```yaml
guideline:
  target:
    zh: '观察时间基准：{observation_time}'
    en: 'Observation time baseline: {observation_time}'
```

Passed at runtime:

```python
ka = Template.create(
    "template_name",
    "en",
    observation_time="2024-01-01"
)
```

---

## Validation

Templates are validated for:
- Required fields present
- Type definitions valid
- Language codes supported
- Schema consistency

---

## Best Practices

1. **Clear descriptions** — Help users choose the right template
2. **Specific rules** — Guide LLM to better extraction
3. **Consistent naming** — Use clear, consistent field names
4. **Bilingual support** — Provide both languages when possible
5. **Required vs optional** — Mark fields appropriately

---

## See Also

- [Template Library](../templates/index.md)
- [Creating Custom Templates](../python/guides/custom-templates.md)
- [Auto-Types](autotypes.md)
