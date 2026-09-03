# Hyper-Knowledge Knowledge Templates

A curated library of YAML-based templates for structured knowledge extraction from domain-specific documents.

> Read this in [中文](./README_ZH.md)

---

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [AutoType Reference](#autotype-reference)
- [When to Use Which Type](#when-to-use-which-type)
- [Document-to-Template Guide](#document-to-template-guide)
- [Template Catalog](#template-catalog)
  - [General Domain](#general-domain)
  - [Finance Domain](#finance-domain)
  - [Medicine Domain](#medicine-domain)
  - [TCM Domain](#tcm-domain)
  - [Industry Domain](#industry-domain)
  - [Legal Domain](#legal-domain)
- [Base Templates Reference](#base-templates-reference)
- [Custom Templates](#custom-templates)

---

## Quick Start

### Installation & Setup

```python
from hyperknowledge.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()
```

### Load & Use a Template

```python
config = Gallery.get("general/workflow_graph")

template = TemplateFactory.create(config, llm, embedder)

result = template.parse("Your document text here...")
```

### Browse Available Templates

```python
all_templates = Gallery.list()
print(f"Total templates: {len(all_templates)}")

graph_templates = Gallery.list(filter_by_type="graph")
print(f"Graph templates: {list(graph_templates.keys())}")

finance_templates = Gallery.list(filter_by_tag="finance")
print(f"Finance templates: {list(finance_templates.keys())}")
```

---

## Core Concepts

### What is a Knowledge Template?

A knowledge template is a YAML configuration that defines:
- **What to extract** from your documents (entities, relations, fields)
- **How to structure** the output (schema definition)
- **Extraction guidelines** for the LLM (instructions and rules)

### Template Structure

```yaml
language: [zh, en]

name: template_name
type: graph | hypergraph | model | list | set | temporal_graph | spatial_graph | spatio_temporal_graph
tags: [domain, category]

description:
  zh: '中文描述'
  en: 'English description'

output:
  description:
    zh: '输出描述'
    en: 'Output description'
  entities:          # For graph types
    fields: [...]
  fields:           # For model types
    - name: field_name
      type: str | int | float | list
      description: {...}
  relations:
    fields: [...]

guideline:
  target: {...}
  rules_for_entities: [...]
  rules_for_relations: [...]

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
```

---

## AutoType Reference

Hyper-Knowledge provides 8 extraction types, forming two families:

### Record Types (Extracting Data)

| Type | Description | Output Structure |
|------|-------------|-----------------|
| **model** | Single structured object | Flat fields with values |
| **list** | Ordered array | Array of items |
| **set** | Deduplicated collection | Unique items only |

### Graph Types (Extracting Relationships)

| Type | Description | Output Structure |
|------|-------------|-----------------|
| **graph** | Binary relations | Nodes + Edges (source→target) |
| **hypergraph** | Multi-entity relations | Nodes + Hyperedges (multiple participants) |
| **temporal_graph** | Relations + time | Nodes + Edges with timestamps |
| **spatial_graph** | Relations + location | Nodes + Edges with coordinates |
| **spatio_temporal_graph** | Relations + time + location | Nodes + Edges with both |

```
                    ┌─────────────┐
                    │   Record    │
                    │   Types     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐     ┌───────────┐     ┌─────────┐
    │  model  │     │   list    │     │   set   │
    └─────────┘     └───────────┘     └─────────┘

                    ┌─────────────┐
                    │    Graph    │
                    │    Types    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐     ┌───────────┐     ┌─────────────┐
    │  graph  │     │ hypergraph│     │ temporal_*  │
    └─────────┘     └───────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ spatial_*   │
                    └─────────────┘
```

---

## When to Use Which Type

### Decision Tree

```
Does your document contain relationships between entities?
│
├─ No
│   └─ Is the data a single structured object?
│       ├─ Yes → model
│       └─ No
│           └─ Is order important?
│               ├─ Yes → list
│               └─ No → set
│
└─ Yes
    └─ Are relations binary (A→B)?
        ├─ Yes
        │   └─ Need time or location?
        │       ├─ Time only → temporal_graph
        │       ├─ Location only → spatial_graph
        │       ├─ Both → spatio_temporal_graph
        │       └─ Neither → graph
        └─ No (multi-party)
            └─ Need time or location?
                ├─ Time only → temporal_graph
                ├─ Location only → spatial_graph
                ├─ Both → spatio_temporal_graph
                └─ Neither → hypergraph
```

### Quick Reference

| Scenario | Recommended Type |
|----------|-----------------|
| Extract a person profile | model |
| List all meeting attendees | set |
| Rank companies by revenue | list |
| Extract who works at where | graph |
| Analyze multi-party contract obligations | hypergraph |
| Build a company history timeline | temporal_graph |
| Map store locations and territories | spatial_graph |
| Track delivery routes with timestamps | spatio_temporal_graph |

---

## Document-to-Template Guide

Match your document type to the right template:

| Document Type | Recommended Templates | Type |
|---------------|---------------------|------|
| **Earnings Call Transcript** | earnings_summary | model |
| **Financial News Article** | sentiment_model, event_timeline | model, temporal_graph |
| **IPO Prospectus** | ownership_graph, event_timeline | graph, temporal_graph |
| **Clinical Practice Guideline** | treatment_map | hypergraph |
| **Drug Interaction Reference** | drug_interaction | graph |
| **Patient Discharge Summary** | hospital_timeline, discharge_instruction | temporal_graph, model |
| **Medical Textbook** | anatomy_graph | graph |
| **Service Contract (MSA)** | contract_obligation | hypergraph |
| **Court Judgment** | case_fact_timeline, case_citation | temporal_graph, graph |
| **Legal Compliance Document** | compliance_list, defined_term_set | list, set |
| **SOP / Operation Manual** | workflow_graph, operation_flow | graph |
| **Equipment Manual** | equipment_topology | graph |
| **Safety Handbook** | safety_control, emergency_response | graph, graph |
| **Failure Analysis Report** | failure_case | graph |
| **TCM Medical Record** | syndrome_reasoning | hypergraph |
| **Classical Formula Text** | formula_composition | hypergraph |
| **Acupuncture Text** | meridian_graph | graph |
| **Herbal Compendium** | herb_property | model |
| **Biography / Memoir** | biography_graph | temporal_graph |
| **Technical Documentation** | doc_structure | graph |
| **Skill Definition (Agent)** | workflow_graph | graph |
| **Conceptual Text** | concept_graph | graph |

---

## Template Catalog

### General Domain

General-purpose templates applicable to any document type.

**Base Templates (8)**

| Template | Type | Description |
|----------|------|-------------|
| [base_model](./presets/general/base_model.yaml) | model | General structured data extraction |
| [base_list](./presets/general/base_list.yaml) | list | General ordered list extraction |
| [base_set](./presets/general/base_set.yaml) | set | General deduplicated set extraction |
| [base_graph](./presets/general/base_graph.yaml) | graph | General knowledge graph (entities + binary relations) |
| [base_hypergraph](./presets/general/base_hypergraph.yaml) | hypergraph | General hypergraph (multi-entity relations) |
| [base_temporal_graph](./presets/general/base_temporal_graph.yaml) | temporal_graph | General temporal graph (relations + time) |
| [base_spatial_graph](./presets/general/base_spatial_graph.yaml) | spatial_graph | General spatial graph (relations + location) |
| [base_spatio_temporal_graph](./presets/general/base_spatio_temporal_graph.yaml) | spatio_temporal_graph | General spatio-temporal graph (relations + time + location) |

**Domain-Specific Templates (5)**

| Template | Type | Purpose | Documents |
|---------|------|---------|-----------|
| [workflow_graph](./presets/general/workflow_graph.yaml) | graph | Extract workflow steps and execution order | Skill definitions, Agent workflows, SOPs |
| [doc_structure](./presets/general/doc_structure.yaml) | graph | Extract document hierarchy and cross-references | Technical docs, papers, reports |
| [biography_graph](./presets/general/biography_graph.yaml) | temporal_graph | Extract life events with timestamps | Biographies, memoirs, year timelines |
| [concept_graph](./presets/general/concept_graph.yaml) | graph | Extract conceptual hierarchies and relations | Textbooks, encyclopedias, academic papers |

---

### Finance Domain

Templates optimized for financial documents and investor relations.

| Template | Type | Purpose | Documents |
|---------|------|---------|-----------|
| [earnings_summary](./presets/finance/earnings_summary.yaml) | model | Extract earnings call key metrics | Earnings call transcripts |
| [sentiment_model](./presets/finance/sentiment_model.yaml) | model | Quantify market sentiment and themes | Financial news, research reports |
| [event_timeline](./presets/finance/event_timeline.yaml) | temporal_graph | Build company event timelines | 8-K filings, news releases |
| [ownership_graph](./presets/finance/ownership_graph.yaml) | graph | Extract shareholder structures | IPO prospectuses, annual reports |
| [risk_factor_set](./presets/finance/risk_factor_set.yaml) | set | Catalog risk factors by category | 10-K risk sections |

---

### Medicine Domain

Templates for clinical and medical documentation.

| Template | Type | Purpose | Documents |
|---------|------|---------|-----------|
| [treatment_map](./presets/medicine/treatment_map.yaml) | hypergraph | Extract diagnosis-treatment-outcome mappings | Clinical guidelines |
| [drug_interaction](./presets/medicine/drug_interaction.yaml) | graph | Map drug interaction networks | Drug references, interaction databases |
| [anatomy_graph](./presets/medicine/anatomy_graph.yaml) | graph | Extract anatomical hierarchies | Anatomy textbooks, surgical records |
| [hospital_timeline](./presets/medicine/hospital_timeline.yaml) | temporal_graph | Build patient admission timelines | Discharge summaries, progress notes |
| [discharge_instruction](./presets/medicine/discharge_instruction.yaml) | model | Structured patient discharge information | Discharge summaries, patient education |

---

### TCM Domain

Templates for Traditional Chinese Medicine literature.

| Template | Type | Purpose | Documents |
|---------|------|---------|-----------|
| [formula_composition](./presets/tcm/formula_composition.yaml) | hypergraph | Extract formula composition (君臣佐使) | Classical formula texts |
| [syndrome_reasoning](./presets/tcm/syndrome_reasoning.yaml) | hypergraph | Extract syndrome-treatment reasoning | Medical case records |
| [meridian_graph](./presets/tcm/meridian_graph.yaml) | graph | Map acupoint-meridian relationships | Acupuncture texts |
| [herb_property](./presets/tcm/herb_property.yaml) | model | Extract herb properties (四气五味) | Herbal compendiums |
| [herb_relation](./presets/tcm/herb_relation.yaml) | graph | Map herb compatibility (七情) | Formula texts, compatibility guides |

---

### Industry Domain

Templates for industrial operations and maintenance.

| Template | Type | Purpose | Documents |
|---------|------|---------|-----------|
| [operation_flow](./presets/industry/operation_flow.yaml) | graph | Extract operation steps and outcomes | SOPs, operation manuals |
| [safety_control](./presets/industry/safety_control.yaml) | graph | Map hazard-risk-control relationships | Safety handbooks |
| [failure_case](./presets/industry/failure_case.yaml) | graph | Extract failure phenomenon-causes-solutions | Failure analysis reports |
| [equipment_topology](./presets/industry/equipment_topology.yaml) | graph | Map equipment hierarchies and connections | Equipment manuals |
| [emergency_response](./presets/industry/emergency_response.yaml) | graph | Map emergency scenarios and responses | Emergency plans |

---

### Legal Domain

Templates for legal documents and compliance.

| Template | Type | Purpose | Documents |
|---------|------|---------|-----------|
| [contract_obligation](./presets/legal/contract_obligation.yaml) | hypergraph | Extract party-obligation relationships | Service contracts, procurement contracts |
| [case_fact_timeline](./presets/legal/case_fact_timeline.yaml) | temporal_graph | Build case fact timelines | Court judgments |
| [case_citation](./presets/legal/case_citation.yaml) | graph | Extract case citation relationships | Legal opinions, case law |
| [compliance_list](./presets/legal/compliance_list.yaml) | list | Structured compliance requirements | Compliance manuals, audit reports |
| [defined_term_set](./presets/legal/defined_term_set.yaml) | set | Catalog defined terms | Contracts, legal opinions |

---

## Base Templates Reference

Base templates provide foundation patterns for extraction. Use them directly or extend them for custom needs.

### Record Type Patterns

| Pattern | Schema | Use Case |
|---------|--------|----------|
| Key-Value Pairs | model | Information cards, profiles |
| Sequential Items | list | Rankings, sequences |
| Unique Items | set | Entity registries |

### Graph Type Patterns

| Pattern | Schema | Use Case |
|---------|--------|----------|
| Binary Relations | graph | Simple entity relationships |
| Multi-Entity Relations | hypergraph | Complex events, group relations |
| Time-Anchored Relations | temporal_graph | Histories, timelines |
| Location-Anchored Relations | spatial_graph | Maps, territories |
| Time + Location Relations | spatio_temporal_graph | Routes, events |

---

## Custom Templates

### Create Your Own Template

A custom template is a standalone YAML file that can be placed anywhere.

### YAML Template Structure

```yaml
language: [zh, en]

name: my_custom_template
type: graph
tags: [custom]

description:
  zh: '我的自定义模板'
  en: 'My custom template'

output:
  description:
    zh: '输出描述'
    en: 'Output description'
  entities:
    fields:
      - name: name
        type: str
        description:
          zh: '实体名称'
          en: 'Entity name'
  relations:
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str

guideline:
  target:
    zh: '你是一位...'
    en: 'You are an...'
  rules_for_entities:
    - '...'
  rules_for_relations:
    - '...'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
```

### Use Custom Template

```python
from hyperknowledge.utils.template_engine import Template
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

# Load custom template by file path
template = Template.create(
    "/path/to/my_template.yaml",  # Template file path
    "zh",  # Language
    llm,
    embedder,
)

result = template.parse("Your document text here...")
```

---

## Statistics

| Domain | Templates | Base | Domain-Specific |
|--------|-----------|------|-----------------|
| general | 13 | 8 | 5 |
| finance | 5 | 0 | 5 |
| medicine | 5 | 0 | 5 |
| tcm | 5 | 0 | 5 |
| industry | 5 | 0 | 5 |
| legal | 5 | 0 | 5 |
| **Total** | **38** | **8** | **30** |

---

## Contributing

To add a new template:
1. Create a YAML file in the appropriate domain directory
2. Follow the template structure conventions
3. Include both Chinese and English descriptions
4. Test with sample documents

---

## License

Part of the Hyper-Knowledge project. See [root LICENSE](../../LICENSE).
