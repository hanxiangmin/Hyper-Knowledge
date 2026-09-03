# MCP Server

Hyper-Knowledge ships an [MCP](https://modelcontextprotocol.io) server so MCP-capable assistants (Claude Desktop, IDE agents, etc.) can **query and export your Knowledge Abstracts** over the Model Context Protocol.

It is **read + export only** — it never creates, mutates, or deletes a KA.

---

## Install & Run

```bash
pip install 'hyperknowledge[mcp]'

# start the server (stdio transport)
hk-mcp
# equivalent:
python -m hyperknowledge.mcp_server
```

The server reads your LLM/embedder configuration from `~/.hk/config.toml` — the same config the CLI uses, so run `hk config init ...` first (see [Configuration](cli/configuration.md)).

---

## Connect it to an MCP client

Point your MCP client at the `hk-mcp` command. For a Claude Desktop–style config:

```json
{
  "mcpServers": {
    "hyper-knowledge": {
      "command": "hk-mcp"
    }
  }
}
```

---

## Tools

| Tool | Description | Needs index | Needs LLM |
|------|-------------|:-----------:|:---------:|
| `list_templates` | List available extraction templates | — | — |
| `info` | Stats for a KA (template, counts, index status) | — | — |
| `search` | Semantic retrieval over a KA | ✓ | embedder |
| `ask` | RAG question-answering over a KA | ✓ | ✓ |
| `export_obsidian` | Export a KA to an Obsidian vault | — | embedder |

All tools take a `ka_path` (a directory created by `hk parse`). `search`/`ask` require an index — build it with [`hk build-index`](cli/commands/build-index.md).

> `export_obsidian` requires the Obsidian export feature (see [`hk export obsidian`](cli/commands/export.md)). If it is unavailable, the tool returns an explanatory message instead of failing.

---

## Example session

```text
list_templates()                        → [{name: "general/biography_graph", ...}, ...]
info(ka_path="./tesla_kb")              → {nodes: 48, edges: 70, index_built: true, ...}
search(ka_path="./tesla_kb",
       query="War of Currents")          → {nodes: [...], edges: [...]}
ask(ka_path="./tesla_kb",
    question="Who were Tesla's rivals?")  → "Thomas Edison ..."
export_obsidian(ka_path="./tesla_kb",
                output="./vault")          → "Exported 49 notes to ./vault"
```
