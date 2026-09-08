# Python API reference

Public imports come from `hyperknowledge`. This is a local Python API, not an HTTP service. It uses existing KA, Bundle v1 and renderer implementations.

## Extraction

```python
extract_text(
    text, *, output_dir, template="general/hypergraph", language="zh",
    source_name="input.txt", llm_client=None, embedder=None,
    build_index=False, force=False,
) -> GraphResult

extract_file(
    path, *, output_dir, template="general/hypergraph", language="zh",
    llm_client=None, embedder=None, build_index=False, force=False,
) -> GraphResult
```

| Parameter | Contract |
| --- | --- |
| text / path | Nonempty string / local UTF-8 (BOM allowed) .txt or .md file |
| output_dir | Required dedicated output directory; not the source directory |
| template | Existing graph/hypergraph template ID or local template YAML |
| language | Template and workbench language, usually zh or en |
| source_name | Relative logical source filename for a string |
| llm_client | Explicit LangChain-compatible chat client; None uses hk model configuration |
| embedder | Optional LangChain embeddings client; None resolves configuration only when used |
| build_index | False; True explicitly builds the KA vector index |
| force | False; True replaces validated output while retaining a sibling backup |

Result saves `output_dir/ka` and `output_dir/bundle`. Text extraction is model-dependent and may fail or produce incomplete evidence; review warnings.

Errors: `ValueError` for empty/unsupported input, invalid configuration or graph; `FileNotFoundError`/`OSError` for file access; `UnicodeDecodeError` for non-UTF-8 input; `FileExistsError` for protected output. Provider exceptions propagate. Failed extraction does not publish a partial result directory. [Runnable usage and configuration](python.md)

## import_graph { #import-graph }

```python
import_graph(
    data, *, output_dir, sources=None, language="zh",
    quality="standard", force=False,
) -> GraphResult
```

`data` is a Python mapping or UTF-8 JSON path; `sources` maps logical names to explicitly approved local files. No model/index is initialized.

Top-level fields: optional `schema_version="hk.bundle/v1"`, required `nodes`, `assertions`, `members`, optional `evidence=[]`. Unknown top-level fields are rejected.

| Table | Required fields | Defaults / notes |
| --- | --- | --- |
| nodes | id, label, type | Nonempty strings; properties={} |
| assertions | id, predicate | topology=hyperedge; semantics=structured_import; epistemic_status=unreviewed_import; evidence_refs=[]; properties={} |
| members | assertion_id, node_id, role | ordinal assigned in per-assertion input order; resolved computed from IDs |
| evidence | id, type plus type-specific fields | source_text_span uses source, line_start, line_end, quote; source_text_summary uses source and summary |

IDs must resolve; duplicate node/assertion IDs and duplicate member-role pairs fail validation. Multiple roles for the same node are valid. An explicit `ordinal` is a nonnegative integer; it is not causal order. Arity counts distinct nodes. Two-member hyperedges remain hyperedges.

An agent should set `epistemic_status="model_extracted"`; import never implies human approval. Quote and line number must come from the actual file. Python copies declared sources and computes source/table hashes, counts and missing-evidence warnings. `quality="showcase"` requires exact available literal spans; `standard` retains some evidence-quality issues as warnings. Neither checks historical truth.

```python
from hyperknowledge import import_graph

graph = {
    "nodes": [
        {"id": "a", "label": "Alice", "type": "person"},
        {"id": "b", "label": "Bob", "type": "person"},
    ],
    "assertions": [{"id": "e", "predicate": "collaboration"}],
    "members": [
        {"assertion_id": "e", "node_id": "a", "role": "researcher"},
        {"assertion_id": "e", "node_id": "b", "role": "researcher"},
    ],
}
result = import_graph(graph, output_dir="output/minimal")
assert result.node_count == 2 and result.hyperedge_count == 1
# Missing source evidence is reported; this example makes no evidence claim.
```

Validation failure raises `ValueError` (including `BundleExportError`); malformed JSON raises `JSONDecodeError`; file errors and overwrite protection use the same exceptions as extraction. Nothing is written outside the dedicated output and its sibling backup/staging paths.

## GraphResult

Frozen result object; no hidden network operations.

| Field | Type | Meaning |
| --- | --- | --- |
| ka_path | Path or None | KA for extraction; None for structured import |
| bundle_path | Path | Validated Bundle directory |
| node_count | int | Number of normalized nodes |
| hyperedge_count | int | Number of assertions explicitly represented as hyperedges |
| pairwise_count | int | Number of explicitly pairwise assertions |
| warnings | tuple[str, ...] | Limitations and validation warning codes |

`.to_dict()` converts Paths to strings and warnings to a list. Counts describe structure, not importance or confidence.

## Existing Bundle and rendering APIs

```python
read_bundle(bundle_path) -> dict
validate_bundle(bundle_path, *, quality="standard") -> dict
export_bundle(ka_path, output_path, *, force=False) -> dict
render_bundle_html(bundle_path, output_path, *, view="contour", quality="standard") -> dict
```

- `read_bundle`: returns manifest and nodes/assertions/members/evidence lists. It reads; call validate for validation.
- `validate_bundle`: returns status, counts, diagnostics and file hashes. Ordinary validation errors return `status="failed"`; callers must check it. File/format errors can raise exceptions.
- `export_bundle`: normalizes an existing KA; returns the computed manifest. Existing overwrite rules remain; prefer a new output directory.
- `render_bundle_html`: validates then writes one self-contained HTML; returns a render receipt. Invalid Bundle/view raises ValueError; output errors raise OSError. The existing file may be overwritten.
- Views: `contour` (default), `incidence`, `hypergraph` (matrix), `graph`, `compare`. Canonical topology is unchanged by a view choice.

[Complete workflow](python.md) · [Agent input contract](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyper-knowledge/references/structured-input.md)
