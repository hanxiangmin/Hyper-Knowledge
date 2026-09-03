"""
超图示例 - 苏轼传记

使用 AutoHypergraph 从文本中提取超关系。

使用方法：
    python examples/zh/autotypes/hypergraph_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoHypergraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    type: str = Field(description="类型：人物/地名/事件/物品/作品等")
    description: str = Field(description="实体描述") 


class Relation(BaseModel):
    """超边（多实体关系）"""
    members: list[str] = Field(description="参与的实体")
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
    print("  超图示例")
    print("=" * 60)
    print("提取多实体关系...")

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

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个超边")

    for edge in graph.edges[:5]:
        print(f"\n{edge.type}：{edge.description}")
        print(f"  成员：{', '.join(edge.members)}")

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
