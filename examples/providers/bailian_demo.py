"""
Bailian (Alibaba Cloud) Provider Demo

Extract entities and relationships using Alibaba Cloud Bailian API.

Usage:
    python examples/providers/bailian_demo.py
"""

from hyperknowledge import create_client, AutoGraph

llm, emb = create_client("bailian", api_key="sk-xxx")

graph = AutoGraph(
    instruction="Extract people and their relationships",
    llm_client=llm,
    embedder=emb,
    node_key_extractor=lambda n: n.name,
    edge_key_extractor=lambda e: (e.source, e.target, e.type),
    nodes_in_edge_extractor=lambda e: (e.source, e.target),
)

text = "张三创立了字节跳动，李四担任 CEO。"
graph.parse(text)

print(f"节点: {len(graph.nodes)}, 关系: {len(graph.edges)}")
for n in graph.nodes:
    print(f"  - {n.name} ({n.type})")
