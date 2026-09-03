# Choose by Task

Find the right template for your specific task.

---

## Research & Academic

### Analyzing a Research Paper

**Goal:** Extract concepts, methods, results, and their relationships

**Recommended:** `general/concept_graph`

```bash
hk parse paper.md -t general/concept_graph -l en -o ./paper_kb/
```

**Why this template?**
- Identifies key concepts and their definitions
- Maps relationships between concepts
- Supports hierarchical structures (e.g., "Neural Networks" → "CNNs")

**Alternatives:**

| Template | When to Use |
|----------|-------------|
| `general/graph` | Broader domain knowledge |
| `general/doc_structure` | Document outline extraction |
| `general/workflow_graph` | Method/process workflows |

---

### Extracting from a Technical Document

**Goal:** Get structured information from manuals, specs, or documentation

**Recommended:** `general/model`

```python
from hyperknowledge import Template

ka = Template.create("general/model", "en")
result = ka.parse(spec_text)

print(result.data)
```

---

## People & Biographies

### Analyzing a Biography

**Goal:** Extract life events, relationships, and timeline

**Recommended:** `general/biography_graph`

```bash
hk parse biography.md -t general/biography_graph -l en -o ./bio_kb/
```

**Features:**
- Extracts people, places, events
- Captures temporal relationships
- Creates timeline visualization

**Example Output:**
```python
{
    "entities": [
        {"name": "Nikola Tesla", "type": "person"},
        {"name": "AC Motor", "type": "invention"}
    ],
    "relations": [
        {"source": "Nikola Tesla", "target": "AC Motor", "type": "invented", "time": "1888"}
    ]
}
```

**Alternatives:**

| Template | When to Use |
|----------|-------------|
| `general/model` | Simple person summary |
| `general/graph` | Complex relationships beyond timeline |

---

### Creating a Profile Summary

**Goal:** Structured summary of a person

**Recommended:** `general/model`

---

## Finance & Business

### Analyzing Earnings Reports

**Goal:** Extract financial metrics and summaries

**Recommended:** `finance/earnings_summary`

```bash
hk parse earnings.md -t finance/earnings_summary -l en -o ./earnings/
```

**Extracts:**
- Revenue, EPS, YoY growth
- Segment performance
- Guidance information

---

### Identifying Risk Factors

**Goal:** Extract risk factors from SEC filings or reports

**Recommended:** `finance/risk_factor_set`

```bash
hk parse 10k.md -t finance/risk_factor_set -l en -o ./risks/
```

**Output:** Unique set of risk factors with categories

---

### Mapping Company Ownership

**Goal:** Extract ownership structure and subsidiaries

**Recommended:** `finance/ownership_graph`

```bash
hk parse report.md -t finance/ownership_graph -l en -o ./ownership/
```

---

## Legal Documents

### Analyzing Contracts

**Goal:** Extract obligations, parties, and deadlines

**Recommended:** `legal/contract_obligation`

```bash
hk parse contract.md -t legal/contract_obligation -l en -o ./contract/
```

**Extracts:**
- Party obligations
- Deadlines and milestones
- Conditions and terms

---

### Tracking Case Chronologies

**Goal:** Create timeline of legal case events

**Recommended:** `legal/case_fact_timeline`

```bash
hk parse case.md -t legal/case_fact_timeline -l en -o ./case/
```

---

### Extracting Defined Terms

**Goal:** Get all defined terms from a contract

**Recommended:** `legal/defined_term_set`

```bash
hk parse contract.md -t legal/defined_term_set -l en -o ./terms/
```

---

## Medical & Healthcare

### Patient Timeline

**Goal:** Track hospital stay or treatment timeline

**Recommended:** `medicine/hospital_timeline`

```bash
hk parse record.md -t medicine/hospital_timeline -l en -o ./patient/
```

---

### Drug Information

**Goal:** Extract drug interactions and properties

**Recommended:** `medicine/drug_interaction`

```bash
hk parse drug_info.md -t medicine/drug_interaction -l en -o ./drugs/
```

---

### Discharge Summary

**Goal:** Generate patient discharge summary

**Recommended:** `medicine/discharge_instruction`

---

## Traditional Chinese Medicine

### Herb Properties

**Goal:** Extract herb characteristics and uses

**Recommended:** `tcm/herb_property`

---

### Formula Analysis

**Goal:** Analyze herbal formula composition

**Recommended:** `tcm/formula_composition`

---

## Industrial & Manufacturing

### Equipment Documentation

**Goal:** Map equipment topology and connections

**Recommended:** `industry/equipment_topology`

---

### Safety Procedures

**Goal:** Extract safety control systems

**Recommended:** `industry/safety_control`

---

## Quick Reference

| Task | Template | Type |
|------|----------|------|
| Research paper concepts | `general/concept_graph` | graph |
| Person biography | `general/biography_graph` | temporal_graph |
| Financial summary | `finance/earnings_summary` | model |
| Risk factors | `finance/risk_factor_set` | set |
| Contract obligations | `legal/contract_obligation` | list |
| Case timeline | `legal/case_fact_timeline` | temporal_graph |
| Hospital timeline | `medicine/hospital_timeline` | temporal_graph |
| Drug interactions | `medicine/drug_interaction` | graph |

---

## Still Not Sure?

→ [Choose by Output Type](by-output.md)  
→ [How to Choose](../how-to-choose.md)  
→ [Template Overview](../reference/overview.md)
