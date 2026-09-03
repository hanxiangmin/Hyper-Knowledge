"""
OpenAI Provider Demo

Extract entities and relationships using OpenAI API.

Usage:
    export OPENAI_API_KEY=sk-xxx
    python examples/providers/openai_demo.py
"""

from hyperknowledge import create_client, AutoGraph

llm, emb = create_client("openai", api_key="sk-xxx")

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
