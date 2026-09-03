"""
AutoList Demo - Tesla Timeline

Extract a list of items from text using AutoList.
This demo shows how to extract and merge items from multiple chunks.

Usage:
    python examples/en/autotypes/list_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge import AutoList

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"


class TimelineEvent(BaseModel):
    """Timeline event"""
    year: str = Field(description="Year of the event")
    title: str = Field(description="Event title")
    description: str = Field(description="Event description")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  AutoList Demo - Tesla Timeline")
    print("=" * 60)
    print("Extracting timeline events...")

    timeline = AutoList[TimelineEvent](
        item_schema=TimelineEvent,
        llm_client=llm,
        embedder=embedder,
    )

    timeline.feed_text(text)

    sorted_events = sorted(timeline.items, key=lambda x: x.year)
    print(f"\nExtracted {len(sorted_events)} events")

    for event in sorted_events[:5]:
        print(f"  {event.year}: {event.title}")

    timeline.build_index()

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = timeline.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    timeline.show(item_label_extractor=lambda x: f"{x.year}: {x.title}")
