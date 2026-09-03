"""
Graph Extraction Demo - Tesla Biography

Extract entities and relationships from text using AutoGraph.
This demo shows how to build a knowledge graph from unstructured text.

Usage:
    python examples/en/autotypes/graph_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoGraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"


class Entity(BaseModel):
    """Entity in the knowledge graph"""

    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type: person/location/invention/etc")
    description: str = Field(description="Entity description")


class Relation(BaseModel):
    """Relation between entities"""

    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    type: str = Field(description="Relation type: employer/partner/rival/invented/etc")
    description: str = Field(description="Relation description")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  Graph Extraction Demo")
    print("=" * 60)
    print("Extracting entities and relationships from Tesla's biography...")

    graph = AutoGraph[Entity, Relation](
        node_schema=Entity,
        edge_schema=Relation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.type}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} relations")

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
        edge_label_extractor=lambda x: f"{x.type}",
    )
