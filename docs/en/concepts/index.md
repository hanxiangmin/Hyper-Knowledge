# Concepts

Understand the fundamental concepts behind Hyper-Knowledge.

---

## Three-Layer Architecture

Hyper-Knowledge is built on a three-layer architecture:

```mermaid
graph TD
    subgraph "Layer 3: Interface"
    A[CLI] --> B[Python SDK]
    B --> C[Template API]
    end
    
    subgraph "Layer 2: Methods"
    C --> D[RAG-Based]
    C --> E[Typical]
    end
    
    subgraph "Layer 1: Data"
    D --> F[Auto-Types]
    E --> F
    end
    
    F --> G[Structured Knowledge]
```

| Layer | Purpose | Components |
|-------|---------|------------|
| **Auto-Types** | Define data structures | 8 type classes |
| **Methods** | Extraction algorithms | RAG + Typical methods |
| **Templates** | Domain-specific configs | 80+ preset templates |

---

## Core Concepts

### [Auto-Types](autotypes.md)

The 8 data structure types that define extraction output:

- **Record Types**: AutoModel, AutoList, AutoSet (store data, no entity relations)
- **Graph Types**: AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph (represent entity relationships)

→ [Learn about Auto-Types](autotypes.md)

### [Methods](methods.md)

The extraction algorithms:

- **RAG-Based**: GraphRAG, LightRAG, Hyper-RAG
- **Typical**: iText2KG, KG-Gen, Atom

→ [Learn about Methods](methods.md)

### [Template Format](templates-format.md)

The YAML format for defining extraction templates:

- Schema definition
- Prompt engineering
- Guidelines and rules

→ [Learn about Template Format](templates-format.md)

### [Architecture](architecture.md)

Deep dive into the system design:

- Data flow
- Processing pipeline
- Extension points

→ [Learn about Architecture](architecture.md)

---

## Quick Links

- [CLI Documentation](../cli/index.md) — Terminal usage
- [Python SDK](../python/index.md) — Programmatic usage
- [Template Library](../templates/index.md) — Available templates
