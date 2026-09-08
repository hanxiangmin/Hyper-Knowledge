# Python and Notebook

Use the same runtime as the CLI and Skill. [Install once](install.md#python) in a retained Python 3.11+ environment.

## Parse a document

Configure a model service first; this sends document text to that service.

```python
from hyperknowledge import extract_file, render_bundle_html

result = extract_file("notes.md", output_dir="output", language="zh")
render_bundle_html(result.bundle_path, "output/workbench.html")
print(result.to_dict())
```

`extract_text("text...", output_dir="output/text")` accepts a string. Both functions use the existing template engine, default to `general/hypergraph`, and save a Knowledge Abstract plus Bundle v1. They **do not build an index by default**.

## Configure only the services you use

`hk config llm` configures the independent Python/CLI model; it does not reuse a Codex or Kimi login. Configuration lives in `~/.hk/config.toml`.

```bash
hk config llm --provider openai --model YOUR_AVAILABLE_MODEL
```

Provide the key through your environment (`OPENAI_API_KEY` for OpenAI-compatible services, `ANTHROPIC_API_KEY` for Anthropic) or the existing configuration. Use `--base-url` for a compatible endpoint. Do not commit credentials. A copied `.env` is not automatically the CLI configuration.

Or supply a client directly:

```python
import os
from langchain_openai import ChatOpenAI
from hyperknowledge import extract_text

client = ChatOpenAI(model=os.environ["HK_CHAT_MODEL"])
result = extract_text(
    "A researcher presented a report at a meeting.",
    output_dir="output/text",
    language="en",
    llm_client=client,
)
```

The explicit client must support the template engine's LangChain chat/structured-output calls. Other supported providers can use their corresponding client packages. Authentication and model availability belong to the selected service.

An embedder is resolved only on use. Requesting `build_index=True`, semantic search or similar operations requires an embedding service; extraction without indexing does not. Missing configuration raises a useful error, never fabricated vectors.

## Import without a model

Use the checked-in [four-node fixture](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/python):

```python
from hyperknowledge import import_graph, read_bundle, validate_bundle, render_bundle_html

result = import_graph(
    "examples/python/graph.json",
    sources={"notes.md": "examples/python/notes.md"},
    output_dir="output/tutorial/bundle",
    quality="showcase",
)
tables = read_bundle(result.bundle_path)
print([(node["label"], node["type"]) for node in tables["nodes"]])
assert validate_bundle(result.bundle_path)["status"] == "passed"
render_bundle_html(result.bundle_path, "output/tutorial/workbench.html")
```

Import accepts a Python dictionary or a JSON path. It preserves two-member hyperedges and multiple roles, computes hashes/counts, and checks references. It does not infer missing facts or evidence. Source files are read only from the explicit `sources=` mapping, not paths requested inside JSON.

[Input contract and API reference](api.md#import-graph) · [Equivalent CLI workflow](commands.md)

## Notebook

The executable [quickstart.ipynb](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/python/quickstart.ipynb) constructs the input, imports, inspects nodes and member roles, validates, then embeds the interactive HTML.

Anaconda / Miniconda users should [register/select the matching kernel](install.md#conda-notebook), **Python (Hyper-Knowledge)**. If the runtime is already installed there, do not reinstall; check `import sys; print(sys.executable)` in the Notebook first.

Only if this kernel still lacks the project, use `%pip` to install into its environment:

```python
%pip install "hyper-knowledge[notebook] @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

Check `sys.executable` and restart the kernel after an upgrade. For an unpublished local revision use its built wheel. Generate the HTML below the notebook directory so Jupyter can serve it:

```python
from IPython.display import IFrame
IFrame("output/tutorial/workbench.html", width="100%", height=720)
```

Notebook execution and browser interaction are separate tests; [compatibility records](compatibility.md) distinguish them.

## Outputs and safe reruns

`GraphResult` exposes `ka_path` (None for imports), `bundle_path`, `node_count`, `hyperedge_count`, `pairwise_count`, and `warnings`. Use `.to_dict()` for JSON.

Choose a new output directory for another run. Import/extraction refuse nonempty output by default; explicit `force=True` keeps the previous directory in a sibling `.backup-...` folder. Validation happens before replacement. HTML rendering has the existing overwrite behavior: use a new filename if you need to preserve it.
