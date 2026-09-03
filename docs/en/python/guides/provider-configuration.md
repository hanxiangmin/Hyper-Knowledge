# Provider Configuration Guide

Configure Hyper-Knowledge to work with OpenAI, Bailian (Alibaba Cloud), or local vLLM deployments.

---

## Unified Example

All three platforms run the **same extraction task** below. Only the client setup (first 3 lines) changes.

### OpenAI

```python
from hyperknowledge import create_client, AutoGraph

llm, emb = create_client("openai", api_key="sk-xxx")
```

### Alibaba Bailian

```python
from hyperknowledge import create_client, AutoGraph

llm, emb = create_client("bailian", api_key="sk-xxx")
# Or override model: create_client("bailian:qwen3.6-plus", api_key="sk-xxx")
```

### Anthropic (Claude)

```python
from hyperknowledge import create_client, AutoGraph

# Anthropic is LLM only — pair it with an OpenAI-compatible embedder.
# Keys: ANTHROPIC_API_KEY (or CLAUDE_API_KEY) for the LLM, OPENAI_API_KEY for embeddings.
llm, emb = create_client(
    llm="anthropic",  # default model: claude-opus-4-8 (override with "anthropic:<model>")
    embedder="openai:text-embedding-3-small",
)
```

### DeepSeek

```python
from hyperknowledge import create_client, AutoGraph

# DeepSeek is OpenAI-compatible but has no embeddings API — pair it with an
# OpenAI-compatible embedder. The V4 models default to "thinking" mode, which
# Hyper-Knowledge auto-disables so structured extraction works out of the box.
llm, emb = create_client(
    llm="deepseek",  # default: deepseek-v4-flash; override with "deepseek:deepseek-v4-pro"
    embedder="openai:text-embedding-3-small",
)
```

### Local vLLM

```python
from hyperknowledge import create_client, AutoGraph

llm, emb = create_client(
    llm="vllm:Qwen3.5-9B@http://localhost:8000/v1",
    embedder="vllm:bge-m3@http://localhost:8001/v1",
    api_key="dummy",
)
```

### Extraction Task (same for all)

```python
graph = AutoGraph(
    instruction="Extract people and their relationships",
    llm_client=llm,
    embedder=emb,
    node_key_extractor=lambda n: n.name,
    edge_key_extractor=lambda e: (e.source, e.target, e.type),
    nodes_in_edge_extractor=lambda e: (e.source, e.target),
)

text = "Zhang San founded ByteDance. Li Si serves as CEO."
graph.parse(text)
print(f"Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
```

---

## CLI Equivalents

| Platform | Command |
|----------|---------|
| **OpenAI** | `hk config init -p openai -k sk-xxx` |
| **Bailian** | `hk config init -p bailian -k sk-xxx` |
| **Anthropic** | `hk config llm -p anthropic -k sk-ant-xxx` + `hk config embedder -p openai -k sk-xxx` |
| **DeepSeek** | `hk config llm -p deepseek -k sk-xxx` + `hk config embedder -p openai -k sk-xxx` |
| **vLLM** | `hk config init` → select "local vLLM" |
| **Mixed** (LLM=Bailian, Embedder=vLLM) | `hk config llm -p bailian -k sk-xxx` + `hk config embedder -p vllm -u http://localhost:8001/v1 -k dummy` |

---

## String Shorthand Format

`create_client()` supports a compact string syntax for quick configuration:

| Format | Example | Result |
|--------|---------|--------|
| `provider` | `"bailian"` | Uses preset defaults for LLM + embedder |
| `provider:model` | `"bailian:qwen3.6-plus"` | Overrides LLM model, keeps preset embedder |
| `provider:model@url` | `"vllm:Qwen3.5-9B@localhost:8000/v1"` | Full manual specification |

---

## Using Config File Instead

If you prefer file-based configuration, run `hk config init` once and then use `Template.create()` or `get_client()`:

```python
from hyperknowledge import get_client, AutoGraph

llm, emb = get_client()  # Reads ~/.hk/config.toml
graph = AutoGraph(..., llm_client=llm, embedder=emb)
```

---

## See Also

- [Provider System & Model Compatibility](../../concepts/provider-system.md) — Full compatibility table and vLLM deployment guide
- [CLI Configuration Reference](../../cli/configuration.md) — Complete `hk config` command reference
