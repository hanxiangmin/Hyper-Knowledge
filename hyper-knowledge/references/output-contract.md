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

The receipt checks required files, schema version, nonempty unique identifiers, member and evidence references, distinct-node topology arity, declared counts, and SHA-256 for every table. Member roles must be nonempty strings, and ordinals must be nonnegative integers unique within a relation. Duplicate entity-role memberships fail; one entity may legitimately hold several different roles. `standard` preserves unresolved members as warnings; `showcase` treats them as blocking errors.

Enriched Knowledge Abstract evidence records and explicit epistemic status survive export. For registered UTF-8 source files within the bundle's local project, validation also checks source hashes, one-based inclusive line spans, and literal quotes. A paraphrase belongs in `summary`, not `quote`. Quote mismatches are warnings in `standard` and errors in `showcase`. Unavailable or external sources produce availability warnings and are not read or downloaded. Source coverage means references exist, not that the underlying claim is independently true.
