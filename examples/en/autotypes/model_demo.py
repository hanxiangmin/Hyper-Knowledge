"""
AutoModel Demo - Tesla Biography Summary

Extract a structured summary from text using AutoModel.
This demo shows how to merge multiple chunks into one consistent object.

Usage:
    python examples/en/autotypes/model_demo.py
"""

from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge import AutoModel

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"


class BiographySummary(BaseModel):
    """Biography summary schema"""
    title: str = Field(description="Title of the biography")
    subject: str = Field(description="Main subject name")
    birth_year: Optional[str] = Field(default="", description="Year of birth")
    death_year: Optional[str] = Field(default="", description="Year of death")
    nationality: str = Field(description="Nationality", default="")
    occupation: List[str] = Field(default_factory=list, description="Main occupations")
    summary: str = Field(description="Brief summary")
    major_inventions: List[str] = Field(default_factory=list, description="Major inventions")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  AutoModel Demo - Tesla Summary")
    print("=" * 60)
    print("Extracting biography summary...")

    model = AutoModel(
        data_schema=BiographySummary,
        llm_client=llm,
        embedder=embedder,
    )

    model.feed_text(text)

    data = model.data
    print(f"\nSubject: {data.subject}")
    print(f"Lifespan: {data.birth_year} - {data.death_year}")
    print(f"Nationality: {data.nationality}")
    print(f"\nSummary: {data.summary}")

    if data.major_inventions:
        print(f"\nMajor Inventions:")
        for inv in data.major_inventions[:3]:
            print(f"  - {inv}")

    model.build_index()

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = model.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    model.show(label_extractor=lambda x: x.title)
