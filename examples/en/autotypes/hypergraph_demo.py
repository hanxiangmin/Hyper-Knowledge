"""
Hypergraph Demo - Tesla Biography

Extract hyper-relationships from text using AutoHypergraph.
This demo shows how to capture multi-entity relationships.

Usage:
    python examples/en/autotypes/hypergraph_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoHypergraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"


class Entity(BaseModel):
    """Entity node"""
    name: str = Field(description="Entity name")
    type: str = Field(description="Type: person/location/invention", default="person")
    description: str = Field(description="Entity description") 


class Relation(BaseModel):
    """Hyperedge (multi-entity relationship)"""
    description: str = Field(description="Relationship description")
    members: list[str] = Field(description="Entities involved")
    type: str = Field(description="Relationship type")
    description: str = Field(description="Relationship description") 


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  Hypergraph Demo")
    print("=" * 60)
    print("Extracting multi-entity relationships...")

    graph = AutoHypergraph[Entity, Relation](
        node_schema=Entity,
        edge_schema=Relation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.type}_{'_'.join(sorted(x.members))}",
        nodes_in_edge_extractor=lambda x: tuple(x.members),
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} hyper-edges")

    for edge in graph.edges[:5]:
        print(f"\n{edge.type}: {edge.description}")
        print(f"  Members: {', '.join(edge.members)}")

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

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: x.type)
