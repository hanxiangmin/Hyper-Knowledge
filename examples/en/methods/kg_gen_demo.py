"""
KG Gen Demo: Tesla Biography Graph Generation

Generate simple knowledge graph from Tesla's biography.

Usage:
    python examples/en/methods/kg_gen_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge.methods.typical import KG_Gen

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
    print("KG Gen Demo")
    print("=" * 60)

    ka = KG_Gen(llm_client=llm, embedder=embedder)
    ka.feed_text(text)

    print("Extracting entities and relations from Tesla's biography...")
    print(f"\n✓ Extracted {len(ka.nodes)} entities, {len(ka.edges)} relations\n")

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = ka.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    ka.show()
