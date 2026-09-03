# Hyper-Knowledge Bundle v1

`hk bundle export` creates a stable, machine-readable directory:

```text
manifest.json
nodes.jsonl
assertions.jsonl
members.jsonl
evidence.jsonl
REPORT.md
```

`manifest.json` records the bundle ID, source KA, data hash, template, language, source inventory, topology type, counts, and known limitations.

`nodes.jsonl` contains canonical node IDs, display labels, types, and original properties.

`assertions.jsonl` contains pairwise and hyperedge assertions without converting hyperedges into pairwise facts.

`members.jsonl` stores node membership, semantic role, order, and whether the member resolves to a known node.

`evidence.jsonl` is reserved for assertion-level evidence. When a Knowledge Abstract lacks exact source spans, exporters must leave `evidence_refs` empty and state the limitation rather than inventing provenance.

Use the bundle as the fact source for downstream views. Vector indexes and visualization projections are rebuildable caches or derived artifacts.

Before delivery, run:

```text
hk bundle validate BUNDLE --quality standard|showcase --json
```

The receipt checks required files, schema version, unique identifiers, member and evidence references, topology arity, declared counts, and SHA-256 for every table. `standard` preserves unresolved members as warnings for audit workflows; `showcase` treats them as blocking errors.
