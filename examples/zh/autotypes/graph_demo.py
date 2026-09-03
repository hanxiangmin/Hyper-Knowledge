"""
图谱提取示例 - 苏轼传记

使用 AutoGraph 从文本中提取实体和关系，构建知识图谱。

使用方法：
    python examples/zh/autotypes/graph_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoGraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class Entity(BaseModel):
    """知识图谱中的实体"""
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型，例如：人物/地名/事件/物品/作品等")
    description: str = Field(description="实体的详细描述") 


class Relation(BaseModel):
    """实体之间的关系"""
    source: str = Field(description="关系起点实体")
    target: str = Field(description="关系终点实体")
    type: str = Field(description="关系类型，例如：父亲/兄弟/发明/参与等")
    description: str = Field(description="关系的详细描述") 


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  图谱提取示例")
    print("=" * 60)
    print("从苏轼传记中提取实体和关系...")

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

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个关系")

    graph.build_index()

    print("-" * 60)
    print("问答")
    print("-" * 60)
    for q in questions:
        print(f"\n问: {q}")
        try:
            result = graph.chat(q)
            print(f"答: {result.content}")
        except Exception as e:
            print(f"错误: {e}")

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: x.type)
