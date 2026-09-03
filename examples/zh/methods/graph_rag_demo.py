"""
Graph RAG 示例：苏轼传记知识图谱

使用 Graph RAG 从苏轼传记中提取和查询知识。

Usage:
    python examples/zh/methods/graph_rag_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge.methods.rag import Graph_RAG

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
    print("Graph RAG 示例")
    print("=" * 60)

    rag = Graph_RAG(llm_client=llm, embedder=embedder)
    rag.feed_text(text)

    print("从苏轼传记中提取实体和关系...")
    print(f"\n✓ 提取了 {len(rag.nodes)} 个实体，{len(rag.edges)} 条关系\n")

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
