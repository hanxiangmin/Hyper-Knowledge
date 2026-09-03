# Template Overview

Complete overview of all available templates.

---

## Statistics

- **Total Templates**: 80+
- **Categories**: 6 domains
- **Auto-Types**: 8 types
- **Languages**: Chinese, English

---

## By Domain

### General Templates

| Template | Type | Description |
|----------|------|-------------|
| `general/model` | model | Basic structured model |
| `general/list` | list | Basic ordered list |
| `general/set` | set | Basic unique set |
| `general/graph` | graph | Basic knowledge graph |
| `general/base_hypergraph` | hypergraph | Basic hypergraph |
| `general/base_temporal_graph` | temporal_graph | Basic temporal graph |
| `general/base_spatial_graph` | spatial_graph | Basic spatial graph |
| `general/base_spatio_temporal_graph` | spatio_temporal_graph | Basic spatio-temporal graph |
| `general/biography_graph` | temporal_graph | Person's life timeline |
| `general/concept_graph` | graph | Research concept extraction |
| `general/graph` | graph | General knowledge extraction |
| `general/doc_structure` | model | Document outline structure |
| `general/workflow_graph` | graph | Process workflows |

### Finance Templates

| Template | Type | Description |
|----------|------|-------------|
| `finance/earnings_summary` | model | Quarterly/annual earnings |
| `finance/event_timeline` | temporal_graph | Financial events |
| `finance/ownership_graph` | graph | Company ownership structure |
| `finance/risk_factor_set` | set | Risk factors |
| `finance/sentiment_model` | model | Sentiment analysis |

### Legal Templates

| Template | Type | Description |
|----------|------|-------------|
| `legal/case_citation` | graph | Legal case precedents |
| `legal/case_fact_timeline` | temporal_graph | Case chronology |
| `legal/compliance_list` | list | Compliance requirements |
| `legal/contract_obligation` | list | Contract obligations |
| `legal/defined_term_set` | set | Defined terms |

### Medical Templates

| Template | Type | Description |
|----------|------|-------------|
| `medicine/anatomy_graph` | graph | Anatomical structures |
| `medicine/discharge_instruction` | model | Patient discharge summary |
| `medicine/drug_interaction` | graph | Drug interactions |
| `medicine/hospital_timeline` | temporal_graph | Hospital stay timeline |
| `medicine/symptom_list` | list | Symptoms |
| `medicine/treatment_map` | graph | Treatment protocols |

### TCM Templates

| Template | Type | Description |
|----------|------|-------------|
| `tcm/formula_composition` | graph | Herbal formula composition |
| `tcm/herb_property` | model | Herb properties |
| `tcm/herb_relation` | graph | Herb relationships |
| `tcm/meridian_graph` | graph | Meridian pathways |
| `tcm/syndrome_reasoning` | graph | Syndrome differentiation |

### Industry Templates

| Template | Type | Description |
|----------|------|-------------|
| `industry/emergency_response` | graph | Emergency procedures |
| `industry/equipment_topology` | graph | Equipment connections |
| `industry/failure_case` | temporal_graph | Failure analysis |
| `industry/operation_flow` | graph | Operational workflows |
| `industry/safety_control` | graph | Safety control systems |

---

## By Auto-Type

### Model Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/model` | general | Basic structured model |
| `finance/earnings_summary` | finance | Financial summary |
| `finance/sentiment_model` | finance | Sentiment analysis |
| `medicine/discharge_instruction` | medical | Discharge summary |
| `tcm/herb_property` | tcm | Herb properties |

### List Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/list` | general | Basic list |
| `legal/compliance_list` | legal | Compliance requirements |
| `legal/contract_obligation` | legal | Contract obligations |
| `medicine/symptom_list` | medical | Symptoms |

### Set Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/set` | general | Basic set |
| `finance/risk_factor_set` | finance | Risk factors |
| `legal/defined_term_set` | legal | Defined terms |

### Graph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/graph` | general | Basic graph |
| `general/graph` | general | Knowledge graph |
| `general/concept_graph` | general | Concept graph |
| `general/workflow_graph` | general | Process workflows |
| `finance/ownership_graph` | finance | Ownership structure |
| `legal/case_citation` | legal | Case precedents |
| `medicine/anatomy_graph` | medical | Anatomy |
| `medicine/drug_interaction` | medical | Drug interactions |
| `medicine/treatment_map` | medical | Treatment protocols |
| `tcm/herb_relation` | tcm | Herb relationships |
| `tcm/meridian_graph` | tcm | Meridian pathways |
| `tcm/syndrome_reasoning` | tcm | Syndrome differentiation |
| `industry/equipment_topology` | industry | Equipment connections |
| `industry/operation_flow` | industry | Operational workflows |
| `industry/safety_control` | industry | Safety control systems |

### Temporal Graph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_temporal_graph` | general | Basic temporal graph |
| `general/biography_graph` | general | Biography timeline |
| `finance/event_timeline` | finance | Financial events |
| `legal/case_fact_timeline` | legal | Case timeline |
| `medicine/hospital_timeline` | medical | Hospital timeline |
| `industry/failure_case` | industry | Failure analysis |

### Spatial Graph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_spatial_graph` | general | Basic spatial graph |

### Spatio-Temporal Graph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_spatio_temporal_graph` | general | Basic spatio-temporal graph |

### Hypergraph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_hypergraph` | general | Basic hypergraph |

---

## Methods (Algorithm-level Access)

Methods provide direct access to extraction algorithms:

| Method | Type | Best For |
|--------|------|----------|
| `method/light_rag` | RAG | General purpose, fast |
| `method/graph_rag` | RAG | Large documents |
| `method/hyper_rag` | RAG | Complex relationships |
| `method/itext2kg` | Standard | High-quality triples |
| `method/itext2kg_star` | Standard | Enhanced quality |
| `method/kg_gen` | Standard | Flexible generation |
| `method/atom` | Standard | Temporal with evidence |

→ [When to use methods](../../python/guides/using-methods.md)

---

## Using This Reference

### CLI

```bash
# List all templates
hk list template

# Filter by domain
hk list template | grep finance

# Get template info
hk info template general/biography_graph
```

### Python

```python
from hyperknowledge import Template

# Get all templates
templates = Template.list()

# Filter by type
graphs = Template.list(filter_by_type="graph")
temporal = Template.list(filter_by_type="temporal_graph")

# Filter by domain/tag
finance = Template.list(filter_by_tag="finance")
medical = Template.list(filter_by_tag="medicine")

# Get template details
cfg = Template.get("general/biography_graph")
print(cfg.name)        # biography_graph
print(cfg.type)        # temporal_graph
print(cfg.description) # Description text
print(cfg.tags)        # ['general', 'biography']
print(cfg.language)    # ['zh', 'en']
```

---

## See Also

- [Choose by Task](../choosing/by-task.md) — Task-based selection
- [Choose by Output Type](../choosing/by-output.md) — Output-based selection
- [Template Library Home](../index.md) — Back to main template page
- [Custom Templates Guide](../../python/guides/custom-templates.md) — Create your own
