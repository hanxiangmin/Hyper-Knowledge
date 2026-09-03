# Template Library

Choose a template based on what you want to extract.

---

## I want to analyze...

<div class="grid cards" markdown>

-   :material-file-document:{ .lg .middle } **Research Papers**

    ---

    Extract concepts, methods, results, and relationships

    - [Concept Graph](examples/research-paper.md) — *Recommended*
    - [Knowledge Graph](examples/research-paper.md#knowledge-graph)
    - [Document Structure](examples/research-paper.md#document-structure)

-   :material-account:{ .lg .middle } **Biographies & Profiles**

    ---

    Extract life events, relationships, and timeline

    - [Biography Graph](reference/general.md) — *Recommended*
    - [Person Summary](reference/general.md)

-   :material-chart-line:{ .lg .middle } **Financial Reports**

    ---

    Extract earnings, risks, and ownership structures

    - [Earnings Summary](examples/financial-report.md) — *Recommended*
    - [Risk Factors](examples/financial-report.md#risk-factors)
    - [Ownership Graph](examples/financial-report.md#ownership-structure)

-   :material-scale-balance:{ .lg .middle } **Legal Documents**

    ---

    Extract obligations, cases, and compliance items

    - [Contract Obligations](examples/legal-contract.md) — *Recommended*
    - [Case Timeline](examples/legal-contract.md#case-timeline)
    - [Defined Terms](examples/legal-contract.md#defined-terms)

-   :material-hospital:{ .lg .middle } **Medical Records**

    ---

    Extract symptoms, treatments, and timelines

    - [Hospital Timeline](reference/medicine.md) — *Recommended*
    - [Drug Interactions](reference/medicine.md)
    - [Discharge Summary](reference/medicine.md)

-   :material-leaf:{ .lg .middle } **TCM Texts**

    ---

    Extract herb properties and formula compositions

    - [Herb Properties](reference/tcm.md) — *Recommended*
    - [Formula Composition](reference/tcm.md)
    - [Meridian Graph](reference/tcm.md)

-   :material-factory:{ .lg .middle } **Industrial Documents**

    ---

    Extract equipment, safety, and operation flows

    - [Equipment Topology](reference/industry.md) — *Recommended*
    - [Safety Controls](reference/industry.md)
    - [Operation Flow](reference/industry.md)

</div>

---

## Not sure what to choose?

**By task type:**

| Task | Recommended Template |
|------|---------------------|
| Summarize a document | `general/model` |
| Extract a list of items | `general/list` |
| Build a knowledge network | `general/graph` |
| Create a timeline | `general/base_temporal_graph` |

→ [More task-based guidance](choosing/by-task.md)

**By output type:**

| Output | Auto-Type | Use When... |
|--------|-----------|-------------|
| Structured summary | AutoModel | Need a report |
| Network/Graph | AutoGraph | Need relationships |
| Timeline | AutoTemporalGraph | Need time sequence |

→ [More output type guidance](choosing/by-output.md)

---

## Quick Start

```bash
# List all templates
hk list template

# Use a template
hk parse document.md -t general/biography_graph -l en -o ./output/
```

```python
from hyperknowledge import Template

# Create template
ka = Template.create("general/biography_graph", "en")

# Extract
result = ka.parse(text)
```

---

## Browse All Templates

→ [Complete Template Reference](reference/overview.md)

---

## Create Custom Templates

Need something specific? Learn to create your own:

→ [Custom Templates Guide](../python/guides/custom-templates.md)
