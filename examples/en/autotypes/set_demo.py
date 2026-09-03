"""
AutoSet Demo - Tesla Related Entities

Extract a deduplicated set of entities from text using AutoSet.
This demo shows how to extract and deduplicate entities based on unique keys.

Usage:
    python examples/en/autotypes/set_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge import AutoSet

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"


class Entity(BaseModel):
    """Entity with unique key"""
    name: str = Field(description="Entity name")
    category: str = Field(description="Category: person/location/invention", default="person")
    description: str = Field(description="Brief description", default="")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  AutoSet Demo - Tesla Entities")
    print("=" * 60)
    print("Extracting and deduplicating entities...")

    entities = AutoSet[Entity](
        item_schema=Entity,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,
    )

    entities.feed_text(text)

    print(f"\nExtracted {len(entities.items)} unique entities")

    categories = {}
    for e in entities.items:
        categories.setdefault(e.category, []).append(e)

    for cat, items in sorted(categories.items()):
        print(f"\n{cat.upper()}:")
        for item in items[:5]:
            print(f"  - {item.name}")

    entities.build_index()

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = entities.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    entities.show(item_label_extractor=lambda x: x.name)
