"""
DeepSeek Provider Demo

Extract entities and relationships using the DeepSeek API.
DeepSeek is OpenAI-compatible but has no embeddings API, so pair it
with an OpenAI-compatible embedder.

Usage:
    DEEPSEEK_API_KEY=sk-xxx OPENAI_API_KEY=sk-xxx python examples/providers/deepseek_demo.py
"""

from hyperknowledge import create_client, AutoGraph

# DeepSeek for LLM, OpenAI for embeddings (DeepSeek has no embeddings API)
llm, emb = create_client(
    llm="deepseek",  # default: deepseek-v4-flash
    embedder="openai:text-embedding-3-small",
)

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
for n in graph.nodes:
    print(f"  - {n.name} ({n.type})")
