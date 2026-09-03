"""
Spatial Graph Demo - Tesla Biography

Extract spatial relationships from text using AutoSpatialGraph.
This demo shows how to understand location-based relationships between entities.

Usage:
    python examples/en/autotypes/spatial_graph_demo.py
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoSpatialGraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"


class Entity(BaseModel):
    """Entity node"""
    name: str = Field(description="Entity name")
    category: str = Field(description="Category, e.g., person, location, invention, etc.")
    description: str = Field(description="Entity description")


class SpatialRelation(BaseModel):
    """Spatial relation"""
    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    relation_type: str = Field(description="Relation type, e.g., father, brother, invention, etc.")
    location: Optional[str] = Field(description="Location, e.g., New York", default=None)
    description: str = Field(description="Relation description")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  Spatial Graph Demo")
    print("=" * 60)
    print("Extracting spatial relationships...")

    graph = AutoSpatialGraph[Entity, SpatialRelation](
        node_schema=Entity,
        edge_schema=SpatialRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        location_in_edge_extractor=lambda x: x.location or "",
        llm_client=llm,
        embedder=embedder,
        observation_location="United States",
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} relations")

    for node in graph.nodes[:5]:
        print(f"  {node.name}")

    graph.build_index()

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = graph.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    graph.show(
        node_label_extractor=lambda x: x.name,
        edge_label_extractor=lambda x: f"{x.relation_type}@{x.location}" if x.location else x.relation_type,
    )
