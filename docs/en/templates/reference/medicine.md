# Medical Templates

Medical text analysis and extraction.

---

## Overview

Medical templates are designed for extracting clinical information from medical texts.

**Disclaimer**: These templates are for research and analysis purposes only. Not for clinical decision-making without professional review.

---

## Templates

### anatomy_graph

**Type**: graph

**Purpose**: Extract anatomical structures and relationships

**Best for**:
- Anatomy textbooks
- Surgical reports
- Medical education materials

**Entities**:

- Body parts
- Organs
- Systems
- Structures

**Relations**:

- `part_of` — Anatomical hierarchy
- `connected_to` — Structural connections
- `supplies` — Blood/nerve supply

=== "CLI"

    ```bash
    hk parse anatomy.md -t medicine/anatomy_graph -l en
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/anatomy_graph", "en")
    result = ka.parse(anatomy_text)

    print(f"Structures: {len(result.nodes)}")
    print(f"Relationships: {len(result.edges)}")

    # Build index for interactive exploration
    result.build_index()
    result.show()
    ```

---

### discharge_instruction

**Type**: model

**Purpose**: Extract discharge summary information

**Best for**:
- Discharge summaries
- Transfer notes
- After-visit summaries

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `diagnosis` | str | Primary diagnosis |
| `procedures` | list[str] | Procedures performed |
| `medications` | list[str] | Prescribed medications |
| `follow_up` | str | Follow-up instructions |
| `warnings` | list[str] | Warning signs |

=== "CLI"

    ```bash
    hk parse discharge.md -t medicine/discharge_instruction -l en
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/discharge_instruction", "en")
    summary = ka.parse(discharge_text)

    print(f"Diagnosis: {summary.data.diagnosis}")
    print(f"Follow-up: {summary.data.follow_up}")
    ```

---

### drug_interaction

**Type**: graph

**Purpose**: Extract drug interactions and relationships

**Best for**:
- Drug databases
- Pharmacy references
- Medication reconciliation

**Entities**:

- Drugs
- Drug classes
- Effects

**Relations**:

- `interacts_with` — Drug interactions
- `contraindicated_with` — Contraindications
- `synergizes_with` — Synergistic effects

=== "CLI"

    ```bash
    hk parse drug_ref.md -t medicine/drug_interaction -l en
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/drug_interaction", "en")
    result = ka.parse(drug_text)

    print(f"Drugs: {len(result.nodes)}")
    for relation in result.edges:
        print(f"{relation.source} {relation.type} {relation.target}")
    ```

---

### hospital_timeline

**Type**: temporal_graph

**Purpose**: Extract hospital stay timeline

**Best for**:
- Hospital course notes
- Progress notes
- Transfer summaries

**Features**:

- Admission/discharge dates
- Procedures and events
- Timeline visualization

=== "CLI"

    ```bash
    hk parse hospital_notes.md -t medicine/hospital_timeline -l en
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/hospital_timeline", "en")
    result = ka.parse(notes_text)

    print(f"Events: {len(result.nodes)}")
    for edge in result.edges:
        if hasattr(edge, 'time'):
            print(f"  {edge.time}: {edge.source} -> {edge.target}")

    # Visualize timeline
    result.build_index()
    result.show()
    ```

---

### treatment_map

**Type**: graph

**Purpose**: Extract treatment protocols and pathways

**Best for**:
- Treatment guidelines
- Care pathways
- Protocol documents

=== "CLI"

    ```bash
    hk parse protocol.md -t medicine/treatment_map -l en
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/treatment_map", "en")
    result = ka.parse(protocol_text)

    print(f"Steps: {len(result.nodes)}")
    print(f"Flow relationships: {len(result.edges)}")

    # Visualize treatment pathway
    result.build_index()
    result.show()
    ```

---

## Use Cases

### Discharge Summary Analysis

```python
from hyperknowledge import Template

ka = Template.create("medicine/discharge_instruction", "en")
discharges = []

for file in discharge_files:
    summary = ka.parse(file.read_text())
    discharges.append(summary.data)

# Analyze common diagnoses
from collections import Counter
diagnoses = Counter(d.diagnosis for d in discharges)
print(diagnoses.most_common(10))
```

### Drug Interaction Network

```python
ka = Template.create("medicine/drug_interaction", "en")
network = ka.parse(drug_database)

# Find interactions for specific drug
drug = "Warfarin"
interactions = [
    r for r in network.data.relations
    if r.source == drug or r.target == drug
]

for i in interactions:
    print(f"{i.source} {i.type} {i.target}")
```

### Anatomy Education

```python
ka = Template.create("medicine/anatomy_graph", "en")
anatomy = ka.parse(textbook_chapter)

# Build index for interactive visualization
anatomy.build_index()

# Visualize with search/chat capabilities
anatomy.show()

# Search
results = anatomy.search("nerves in hand")
```

---

## Tips

1. **discharge_instruction for summaries** — Quick extraction of key discharge info
2. **drug_interaction for safety** — Build interaction checking tools
3. **anatomy_graph for education** — Create interactive anatomy maps
4. **hospital_timeline for courses** — Track patient journeys

---

## Data Privacy

When working with medical data:
- Ensure HIPAA compliance
- De-identify data before processing
- Use secure environments
- Follow institutional policies

---

## See Also

- [Template Overview](overview.md)
- [TCM Templates](tcm.md)
