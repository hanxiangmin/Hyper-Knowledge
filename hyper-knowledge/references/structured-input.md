# Structured input for agents and Python

Use this route when the current agent reads and interprets a document. Write one
UTF-8 JSON file with the existing Bundle-v1 tables. Do not hand-write a manifest,
file hashes, counts, or a new visualization. Keep canonical IDs stable.

```json
{
  "nodes": [
    {"id": "su", "label": "苏轼", "type": "person"},
    {"id": "year", "label": "1101年", "type": "time"},
    {"id": "place", "label": "常州", "type": "place"}
  ],
  "assertions": [
    {"id": "return", "predicate": "北归", "topology": "hyperedge",
     "epistemic_status": "model_extracted", "evidence_refs": ["ev-return"]}
  ],
  "members": [
    {"assertion_id": "return", "node_id": "su", "role": "北归者"},
    {"assertion_id": "return", "node_id": "year", "role": "年份"},
    {"assertion_id": "return", "node_id": "place", "role": "到达地点"}
  ],
  "evidence": [
    {"id": "ev-return", "type": "source_text_span", "source": "notes.md",
     "line_start": 1, "line_end": 1, "quote": "1101年，苏轼北归抵达常州。"}
  ]
}
```

The example quote assumes exactly that sentence is on line 1 of the source;
replace it with evidence actually found in the user's document. Line numbers are
one-based and inclusive. A paraphrase belongs in `summary`, never `quote`.

- Required tables: `nodes`, `assertions`, `members`; `evidence` may be omitted.
- Nodes need `id`, `label`, `type`. Assertions need `id`, `predicate`.
- Assertions default to `topology: hyperedge`, `semantics: structured_import`,
  `epistemic_status: unreviewed_import`. Agents must set `model_extracted`.
- Members need `assertion_id`, `node_id`, `role`. Ordinals and resolved flags are
  computed if not supplied; do not repeat the same node/role in one assertion.
- Two distinct members are valid. One node may have multiple different roles,
  but that does not increase distinct-member count. Different events may share
  a title; their IDs must still differ.
- Optional `properties` on nodes and assertions is an object. Put a short
  relation display title in `properties.name` if different from `predicate`.
- Missing evidence stays absent and generates a warning. Do not invent it to
  obtain a better validation result.

```text
<launcher> bundle import graph.json --source notes.md=path/to/notes.md -o output/bundle --quality showcase --json
<launcher> visualize output/bundle -o output/workbench.html --no-open --json
```

Repeat `--source NAME=PATH` for multiple explicitly provided local source files.
Use relative POSIX logical names, not absolute paths or `..`. Only these supplied
files are read and copied into `bundle/sources/`; paths embedded in JSON are not
permission to read files. Hashes and references are computed locally. There is
no upload, model call, or vector index in either command above.

Python calls the same importer:

```python
from hyperknowledge import import_graph, render_bundle_html

result = import_graph("graph.json", output_dir="output/bundle",
                      sources={"notes.md": "path/to/notes.md"}, quality="showcase")
render_bundle_html(result.bundle_path, "output/workbench.html")
```

Import failures are actionable: correct the specific ID, role, or evidence
diagnostic and retry. Do not suppress a failed check or switch to a weaker
profile solely to claim success. Existing outputs are not overwritten by
default. Choose a new run directory unless replacement is explicitly requested.
