"""
Atom Demo: Tesla Biography Temporal Extraction

Extract temporal facts from Tesla's biography using Atom.

Usage:
    python examples/en/methods/atom_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge.methods.typical import Atom

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        text = f.read()
    with open(QUESTION_FILE) as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini")
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("=" * 60)
    print("Atom Demo")
    print("=" * 60)

    atom = Atom(llm_client=llm, embedder=embedder)
    atom.feed_text(text)

    print("Extracting temporal facts from Tesla's biography...")
    print(f"\n✓ Extracted {len(atom.facts)} temporal facts\n")

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = atom.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    atom.show()
