# Hyper-Knowledge Design Guide

A comprehensive guide for designing YAML extraction templates in Hyper-Knowledge.

> 本指南中文版请查看 [DESIGN_GUIDE_zh.md](./DESIGN_GUIDE_zh.md)

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [Part 1: Design Workflow](#part-1-design-workflow)
- [Part 2: Type-Specific Design](#part-2-type-specific-design)
- [Part 3: Field Reference](#part-3-field-reference)
- [Part 4: Quality Assurance](#part-4-quality-assurance)
- [Part 5: Validation](#part-5-validation)

---

## Quick Reference

### Type Selection Decision Tree

```
Need relationships?
├─ No → Record types
│   ├─ Single object → model
│   ├─ Ordered list → list
│   └─ Deduplicated set → set
└─ Yes → Graph types
    ├─ Binary (A→B) → graph
    └─ Multi-entity (A+B+C→D)
        ├─ Flat list → hypergraph (simple)
        └─ Role groups → hypergraph (nested)

After graph:
├─ + time dimension → temporal_graph
├─ + space dimension → spatial_graph
└─ + both → spatio_temporal_graph
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Template name | CamelCase | `EarningsSummary` |
| Field names | snake_case | `company_name` |
| Relation type | `type` | (not `relation_type`) |
| Time field | `time` | (not `event_date`) |
| Tags | lowercase | `finance, investor` |

### Field Count Guidelines

| Component | Max Fields | Priority |
|-----------|------------|----------|
| Entity fields | 5 | Essential → Important → Optional |
| Relation fields | 5 | Essential → Important → Optional |
| List fields | 3 | Essential → Important → Optional |

---

## Part 1: Design Workflow

### Workflow Overview

```
User Input → brainstorm → designer → optimizer → validator
                  ↓            ↓          ↓          ↓
              Type Selection  YAML Gen  Auto-fix   Check
```

### Step 1: Brainstorm

Clarify requirements and determine the extraction type.

**Discussion Questions:**
- What is the input source?
- What to extract?
- Key fields needed?
- Entity types and granularity?
- Relation types (predefined or custom)?

**Output:** Design draft with type, fields, and notes.

### Step 2: Designer

Generate YAML based on the design draft.

**Output Template:**

```yaml
language: [zh, en]

name: TemplateName
type: [type]
tags: [domain]

description:
  zh: '...'
  en: '...'

output:
  description: '...'
  entities:        # For graph types
    description: '...'
    fields: [...]
  fields:         # For record types
    - name: field_name
      type: str
      description: '...'

guideline:
  target: '...'
  rules: [...]          # For record types
  rules_for_entities: [...]   # For graph types
  rules_for_relations: [...] # For graph types

identifiers: {}

display:
  label: '...'
```

### Step 3: Optimizer (Optional)

Auto-fix common issues and apply best practices.

**Auto-fix rules:**
- `relation_type` → `type`
- `event_date` → `time`
- Mixed language → separated zh/en

### Step 4: Validator

Verify YAML correctness.

**Validation checklist:**
- [ ] language: zh/en
- [ ] name: CamelCase
- [ ] type: valid AutoType
- [ ] tags: lowercase array
- [ ] description: non-empty
- [ ] output: exists
- [ ] guideline: exists

---

## Part 2: Type-Specific Design

### Critical: Schema vs Guideline Separation

**Schema defines WHAT, Guideline defines HOW TO DO WELL.**

| Schema Defines | Guideline Defines |
|---------------|-----------------|
| Field names | Extraction strategy |
| Field types | Quality requirements |
| Field descriptions | Creation conditions |
| Required/optional | Common mistakes |

**❌ Wrong:** Guideline repeats field definitions
**✅ Correct:** Guideline explains how to extract well

---

### 1. model - Single Structured Object

**Use when:** Extracting a single record with multiple fields.

**Template:**

```yaml
name: EarningsSummary
type: model
tags: [finance]

output:
  description: '...'
  fields:
    - name: company_name
      type: str
      description: 'Company name'
      required: true
    - name: revenue
      type: str
      description: 'Revenue amount'
      required: false

guideline:
  target: 'You are a financial analyst...'
  rules:
    - 'Extract precise figures consistent with the source'
    - 'Follow the format in the original text'

identifiers: {}

display:
  label: '{company_name}'
```

**Design Checklist:**
- [ ] All fields have clear semantic meaning?
- [ ] Field types are appropriate (str/int/float/list)?
- [ ] Required vs optional is reasonable?
- [ ] Default values are safe/meaningful?
- [ ] Display label references correct fields?
- [ ] Guideline does NOT repeat field definitions?

---

### 2. list - Ordered Array

**Use when:** Extracting ordered items (rankings, sequences, bullet points).

**Template:**

```yaml
name: KeywordList
type: list
tags: [general]

output:
  description: '...'
  fields:
    - name: term
      type: str
      description: 'Keyword or term'
    - name: rank
      type: int
      description: 'Order position'
      required: false

guideline:
  target: 'You are a keyword extraction expert...'
  rules:
    - 'Extract terms in the order they appear'
    - 'Maintain ranking order if explicitly stated'

identifiers: {}

display:
  label: '{term}'
```

**Design Checklist:**
- [ ] Items have consistent structure?
- [ ] Order is meaningful and preserved?
- [ ] No redundant fields?

---

### 3. set - Deduplicated Collection

**Use when:** Extracting unique entities (entity registry, keyword list).

**Template:**

```yaml
name: EntityRegistry
type: set
tags: [general]

output:
  description: '...'
  fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: category
      type: str
      description: 'Entity type'
      required: false

guideline:
  target: 'You are an entity recognition expert...'
  rules:
    - 'Extract all unique entities'
    - 'Maintain consistent naming across the text'

identifiers:
  item_id: name

display:
  label: '{name}'
```

**Design Checklist:**
- [ ] item_id can uniquely identify records?
- [ ] Deduplication rules are clear?
- [ ] Similar entities are handled consistently?

---

### 4. graph - Binary Relations

**Use when:** Modeling relationships between two entities (A→B).

**Template:**

```yaml
name: OwnershipGraph
type: graph
tags: [finance]

output:
  description: '...'
  entities:
    description: 'Organization entities'
    fields:
      - name: name
        type: str
        description: 'Entity name'
      - name: type
        type: str
        description: 'Entity type'
  relations:
    description: 'Ownership relationships'
    fields:
      - name: source
        type: str
        description: 'Owner entity'
      - name: target
        type: str
        description: 'Owned entity'
      - name: type
        type: str
        description: 'Relation type'

guideline:
  target: 'You are a knowledge graph expert...'
  rules_for_entities:
    - 'Extract entities valuable for understanding the text'
    - 'Maintain consistent naming throughout'
  rules_for_relations:
    - 'Create relations only when explicitly stated'
    - 'Prefer relation words that appear in the text'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

**Design Checklist:**
- [ ] Entity types cover key concepts?
- [ ] Entity granularity appropriate?
- [ ] Relation types semantically clear?
- [ ] source/target reference valid entities?
- [ ] No ambiguous relations?
- [ ] relation_label doesn't repeat source/target?

---

### 5. hypergraph - Multi-Entity Relations

**Use when:** Modeling complex relationships with multiple participants.

#### 5a. Simple Hypergraph (Flat List)

**Use when:** All participants have equal roles.

```yaml
relations:
  fields:
    - name: event_name
      type: str
      description: 'Event or mechanism name'
    - name: participants
      type: list
      description: 'List of participating entities'
    - name: type
      type: str
      description: 'Relation type'
    - name: outcome
      type: str
      description: 'Result or conclusion'
      required: false

identifiers:
  entity_id: name
  relation_id: '{event_name}|{type}'
  relation_members: participants  # STRING
```

#### 5b. Nested Hypergraph (Semantic Grouping)

**Use when:** Participants have distinct semantic roles.

```yaml
relations:
  fields:
    - name: event_name
      type: str
      description: 'Event name'
    - name: group_a
      type: list
      description: 'Group A participants (e.g., attackers)'
    - name: group_b
      type: list
      description: 'Group B participants (e.g., defenders)'
    - name: outcome
      type: str
      description: 'Result'
    - name: reasoning
      type: str
      description: 'Explanation'
      required: false

identifiers:
  entity_id: name
  relation_id: '{event_name}'
  relation_members: [group_a, group_b]  # LIST
```

**Common Grouping Patterns:**

| Scenario | Groups | Use Case |
|----------|--------|----------|
| Formula | sovereigns, ministers, assistants, envoys | TCM formulas |
| Battle | attackers, defenders | Military conflicts |
| Transaction | buyers, sellers, intermediaries | Commercial deals |
| Contract | parties, witnesses | Legal documents |

**Design Checklist:**
- [ ] How many semantic groups?
- [ ] What are the group names?
- [ ] Should use nested grouping instead of role field?
- [ ] Participant count reasonable?
- [ ] Outcome defined?

---

### 6. temporal_graph - Relations with Time

**Use when:** Relationships have temporal aspects.

**Add to graph:**

```yaml
relations:
  fields:
    - name: source
      type: str
    - name: target
      type: str
    - name: type
      type: str
    - name: time
      type: str
      description: 'When the relation occurred'
      required: false

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time

guideline:
  rules_for_time:
    - 'Observation time: {observation_time}'
    - 'Absolute dates: Keep as-is (e.g., 2024-01-01)'
    - 'Relative time: Convert to absolute'
    - 'Fuzzy time: Leave empty, do not guess'
```

**Design Checklist:**
- [ ] Time is edge property, not node property?
- [ ] Format handling rules clear?
- [ ] Relative time conversion specified?

---

### 7. spatial_graph - Relations with Location

**Add to graph:**

```yaml
relations:
  fields:
    - name: source
      type: str
    - name: target
      type: str
    - name: type
      type: str
    - name: location
      type: str
      description: 'Where the relation occurred'
      required: false

identifiers:
  location_field: location

guideline:
  rules_for_location:
    - 'Observation location: {observation_location}'
    - 'Structured: Keep as-is'
    - 'Fuzzy: Use observation_location'
```

---

### 8. spatio_temporal_graph - Relations with Time + Location

**Combines temporal_graph and spatial_graph.**

```yaml
identifiers:
  time_field: time
  location_field: location
```

---

## Part 3: Field Reference

### Common Entity Fields

```yaml
entities:
  description: 'Entity definitions'
  fields:
    - name: name
      type: str
      description: 'Entity name (unique identifier)'
    - name: type
      type: str
      description: 'Entity type/category'
    - name: description
      type: str
      description: 'Brief description'
      required: false
```

### Common Relation Fields

```yaml
relations:
  description: 'Relation definitions'
  fields:
    - name: source
      type: str
      description: 'Source entity'
    - name: target
      type: str
      description: 'Target entity'
    - name: type
      type: str
      description: 'Relation type'
```

### Identifiers Configuration

#### For graph (binary)

```yaml
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target
```

#### For hypergraph (simple)

```yaml
identifiers:
  relation_members: participants  # STRING
```

#### For hypergraph (nested)

```yaml
identifiers:
  relation_members: [group_a, group_b]  # LIST
```

### Display Configuration

| Type | entity_label | relation_label |
|------|--------------|----------------|
| graph | `{name} ({type})` | `{type}` |
| hypergraph | `{name}` | `{event_name}` or `{outcome}` |
| temporal | `{name} ({type})` | `{type}@{time}` |
| spatio_temporal | `{name} ({type})` | `{type}@{location}({time})` |

**Length guidelines:**
- entity_label: 5-20 characters
- relation_label: 10-30 characters

---

## Part 4: Quality Assurance

### Multi-language Rules

**Core Principle:** Each language field should use that language's own terminology.

| Field | Rule | Example |
|-------|------|---------|
| `zh` | Pure Chinese | `类型：实体` |
| `en` | Pure English | `Type: entity` |

**Forbidden patterns:**
- ❌ `zh` with English terms: `entity(实体)`
- ❌ `en` with Chinese characters: `类型`

**Translation patterns:**

| Chinese | English |
|---------|---------|
| 实体 | entity |
| 抽象概念 | abstract |
| 过程 | process |
| 关系 | relation |
| 高/中/低 | high/medium/low |

---

### Field Count Optimization

**Max fields per component:** 5

| Priority | Description |
|----------|-------------|
| Essential | source, target, participants |
| Important | type, time, location |
| Optional | description, metadata |

**Simplification strategy:** If >5 fields, consider:
- Splitting into multiple templates
- Moving optional fields to description
- Removing redundant fields

---

### Auto-fix Patterns

| Issue | Fix |
|-------|-----|
| `relation_type` | → `type` |
| `event_date` | → `time` |
| `entity_type` | → `type` |
| Mixed language in `zh` | Extract `entity(...)` → `实体` |
| Chinese chars in `en` | Translate to English |

---

## Part 5: Validation

### Validation Checklist

#### All Types
- [ ] language: zh/en
- [ ] name: CamelCase
- [ ] type: valid AutoType
- [ ] tags: lowercase array
- [ ] description: non-empty
- [ ] output: exists
- [ ] guideline: exists

#### Graph Types
- [ ] output.entities: exists
- [ ] output.relations: exists
- [ ] identifiers.entity_id: exists
- [ ] identifiers.relation_id: exists
- [ ] identifiers.relation_members: configured

#### Hypergraph
- [ ] relation_members is string OR list
- [ ] If list: all fields are type: list

#### Temporal/Spatial
- [ ] identifiers.time_field: configured (temporal)
- [ ] identifiers.location_field: configured (spatial)

### Common Errors

| Error | Fix |
|-------|-----|
| Missing required field | Add the field |
| Invalid type value | Use valid AutoType |
| Mixed language | Separate zh/en content |
| Field count >5 | Simplify or split |

---

## Appendix

### AutoType Quick Reference

```
Need single object → model
Need list → list
Need deduplication → set
Need binary relations → graph
Need multi-party relations → hypergraph
Need time → temporal_graph
Need location → spatial_graph
Need both → spatio_temporal_graph
```

### Template Directory Structure

```
templates/
├── presets/
│   ├── general/        # 13 templates (8 base + 5 domain-specific)
│   ├── finance/        # 5 templates
│   ├── medicine/       # 5 templates
│   ├── tcm/           # 5 templates
│   ├── industry/      # 5 templates
│   └── legal/         # 5 templates
├── DESIGN_GUIDE.md        # This guide
├── DESIGN_GUIDE_zh.md     # Chinese version
├── README.md              # Template catalog
└── README_ZH.md          # 中文目录
```

---

## License

Part of the Hyper-Knowledge project. See [root LICENSE](../../LICENSE).
