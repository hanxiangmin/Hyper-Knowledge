# TCM Templates

Traditional Chinese Medicine text analysis.

---

## Overview

TCM (Traditional Chinese Medicine) templates are designed for extracting knowledge from TCM texts, including herbal medicine, formulas, and syndrome differentiation.

---

## Templates

### herb_property

**Type**: model

**Purpose**: Extract herb properties and characteristics

**Best for**:
- Materia medica texts
- Herb databases
- Prescription references

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Herb name (Chinese/pinyin) |
| `properties` | list[str] | Nature (hot, warm, cool, cold, neutral) |
| `flavors` | list[str] | Five flavors (sour, bitter, sweet, pungent, salty) |
| `meridians` | list[str] | Entered meridians |
| `functions` | list[str] | Main functions |
| `indications` | list[str] | Clinical indications |

=== "CLI"

    ```bash
    hk parse herb_text.md -t tcm/herb_property -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/herb_property", "zh")
    herb = ka.parse(huang_qi_text)

    print(f"Name: {herb.data.name}")
    print(f"Nature: {', '.join(herb.data.properties)}")
    print(f"Functions: {', '.join(herb.data.functions)}")
    ```

---

### formula_composition

**Type**: graph

**Purpose**: Extract herbal formula compositions

**Best for**:
- Formula collections (方剂学)
- Prescription texts
- Classic texts (伤寒论, 金匮要略)

**Entities**:

- Herbs (药物)
- Formulas (方剂)
- Conditions (病症)

**Relations**:

- `contains` — Formula contains herb
- `treats` — Formula treats condition
- `modifies` — Modified formula relationship

=== "CLI"

    ```bash
    hk parse formula_book.md -t tcm/formula_composition -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/formula_composition", "zh")
    result = ka.parse(formula_text)

    print(f"Entities: {len(result.nodes)}")
    print(f"Relations: {len(result.edges)}")

    # List herbs in formula
    for edge in result.edges:
        if edge.type == "contains":
            print(f"  - {edge.target}")
    ```

---

### herb_relation

**Type**: graph

**Purpose**: Extract herb-to-herb relationships

**Best for**:
- Herb pairing references (药对)
- Compatibility texts (十八反, 十九畏)
- Combination guides

**Relations**:

- `pairs_with` — Common pairing
- `synergizes_with` — Synergistic effect
- `incompatible_with` — Contraindicated combination

=== "CLI"

    ```bash
    hk parse herb_pairs.md -t tcm/herb_relation -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/herb_relation", "zh")
    result = ka.parse(herb_text)

    print(f"Herbs: {len(result.nodes)}")
    for edge in result.edges:
        print(f"{edge.source} {edge.type} {edge.target}")
    ```

---

### meridian_graph

**Type**: graph

**Purpose**: Extract meridian pathway information

**Best for**:
- Acupuncture texts
- Meridian studies
- Point location references

**Entities**:

- Meridians (经脉)
- Acupoints (穴位)
- Organs (脏腑)

**Relations**:

- `connects_to` — Meridian connections
- `belongs_to` — Point to meridian
- `influences` — Meridian-organ relationship

=== "CLI"

    ```bash
    hk parse acupuncture.md -t tcm/meridian_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/meridian_graph", "zh")
    result = ka.parse(acupuncture_text)

    print(f"Meridians: {len(result.nodes)}")
    print(f"Connections: {len(result.edges)}")

    # Visualize meridian pathways
    result.build_index()
    result.show()
    ```

---

### syndrome_reasoning

**Type**: graph

**Purpose**: Extract syndrome differentiation logic

**Best for**:
- Diagnostics texts (中医诊断学)
- Case studies
- Syndrome differentiation guides

**Entities**:

- Symptoms (症状)
- Syndromes (证型)
- Patterns (病机)

**Relations**:

- `indicates` — Symptom indicates syndrome
- `differentiates_from` — Differential diagnosis
- `leads_to` — Pattern progression

=== "CLI"

    ```bash
    hk parse diagnostics.md -t tcm/syndrome_reasoning -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/syndrome_reasoning", "zh")
    result = ka.parse(diagnostics_text)

    print(f"Symptoms: {len(result.nodes)}")
    print(f"Indications: {len(result.edges)}")

    # Explore syndrome relationships
    result.build_index()
    result.show()
    ```

---

## Use Cases

### Herb Database Building

```python
from hyperknowledge import Template

ka = Template.create("tcm/herb_property", "zh")
herb_db = {}

for herb_file in herb_files:
    herb = ka.parse(herb_file.read_text())
    herb_db[herb.data.name] = herb.data

# Query by function
for name, data in herb_db.items():
    if "补气" in data.functions:
        print(f"{name}: Qi tonic herb")
```

### Formula Analysis

```python
ka = Template.create("tcm/formula_composition", "zh")
formula = ka.parse(si_jun_zi_tang_text)

# List herbs
print("Formula composition:")
for relation in formula.data.relations:
    if relation.type == "contains":
        print(f"  - {relation.target}")
```

### Syndrome Study

```python
ka = Template.create("tcm/syndrome_reasoning", "zh")
syndromes = ka.parse(diagnostics_text)

# Find what symptom indicates what syndrome
symptom = "舌淡苔白"
related = [
    r for r in syndromes.data.relations
    if r.source == symptom and r.type == "indicates"
]

for r in related:
    print(f"{symptom} indicates {r.target}")
```

---

## Tips

1. **Use Chinese language (`-l zh`)** — Better extraction from TCM texts
2. **herb_property for materia medica** — Build herb databases
3. **formula_composition for方剂学** — Study classic formulas
4. **meridian_graph for acupuncture** — Map meridian pathways

---

## See Also

- [Template Overview](overview.md)
- [Medical Templates](medicine.md)
