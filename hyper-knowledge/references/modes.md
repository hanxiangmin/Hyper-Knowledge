# Execution modes

## Plan and template

Use `hk list template` and `hk list method` before inventing a new schema. Recommend a pairwise graph when every relation has exactly two ordered or unordered endpoints. Recommend a hypergraph when an event, group, episode, experiment, transaction, or other relation has three or more members or member roles that must remain together.

For a custom YAML template, preserve the source file and call it directly:

```text
hk parse INPUT --template TEMPLATE.yaml --lang en --output KA
```

Do not place extraction strategy inside field descriptions. The schema defines what is returned; the guideline defines when and how to extract it.

## Extract

Use `hk parse` for a new KA. Prefer `--no-index` when the user only needs structured extraction or visualization. Index building is optional and can be performed later.

For a directory, Hyper-Knowledge processes `.txt` and `.md` files recursively in stable path order and records source hashes. Report unsupported input formats rather than pretending they were parsed.

## Extend

Use `hk feed` only when the existing KA template and the new source semantics are compatible. Updating a source or template creates a new output when reproducibility matters; do not overwrite a released result.

## Query

Use `hk info KA` first. Use `hk search` only when a verified index is available, and `hk talk` only when the configured provider and data-sharing boundary are acceptable.

## Bundle and audit

Create a normalized artifact before visualization or publication:

```text
hk bundle export KA -o hyperknowledge-out/RUN --json
```

Inspect `manifest.json`, unresolved-member counts, `REPORT.md`, and assertion-level evidence coverage before making claims.

## Visualize

```text
hk visualize hyperknowledge-out/RUN -o hyperknowledge-out/RUN/views/workbench.html --view contour --no-open --json
```

The workbench always offers the lossless enclosure and incidence views for hypergraphs. It adds the pairwise view only when the source bundle contains native two-node relations. Hyperedges are never expanded into clique edges, star hubs, or inferred pairwise facts.
