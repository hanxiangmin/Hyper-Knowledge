"""
Cog RAG 示例：苏轼传记认知知识图谱

使用 Cog RAG 从苏轼传记中提取主题和实体的认知知识。

Usage:
    python examples/zh/methods/cog_rag_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge.methods.rag import Cog_RAG

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"

if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini")
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("=" * 60)
    print("Cog RAG 示例")
    print("=" * 60)

    rag = Cog_RAG(llm_client=llm, embedder=embedder)
    rag.feed_text(text)

    print("从苏轼传记中提取认知知识...")
    print(f"\n✓ 提取了 {len(rag.themes)} 个主题，{len(rag.nodes)} 个实体\n")

    print("-" * 60)
    print("问答")
    print("-" * 60)
    for q in questions:
        print(f"\n问: {q}")
        try:
            result = rag.chat(q)
            print(f"答: {result.content}")
        except Exception as e:
            print(f"错误: {e}")

    rag.show()
