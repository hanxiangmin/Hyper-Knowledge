"""
时序图示例 - 苏轼传记

使用 AutoTemporalGraph 从文本中提取时序关系。
展示如何理解实体之间的时间顺序关系。

使用方法：
    python examples/zh/autotypes/temporal_demo.py
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoTemporalGraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    category: str = Field(description="类别，例如：人物/地点/发明等")
    description: str = Field(description="实体描述")


class TemporalRelation(BaseModel):
    """时序关系"""
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relation_type: str = Field(description="关系类型，例如：父亲/兄弟/发明/参与等")
    event_date: Optional[str] = Field(description="关系发生的时间（年份或日期）", default=None)
    description: str = Field(description="关系描述")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  时序图示例")
    print("=" * 60)
    print("提取时序关系...")

    graph = AutoTemporalGraph[Entity, TemporalRelation](
        node_schema=Entity,
        edge_schema=TemporalRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        time_in_edge_extractor=lambda x: x.event_date or "",
        llm_client=llm,
        embedder=embedder,
        observation_time="2024-01-01",
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个关系")

    sorted_edges = sorted(graph.edges, key=lambda x: x.event_date or "")
    for edge in sorted_edges[:5]:
        time_info = f"（{edge.event_date}）" if edge.event_date else ""
        print(f"  {edge.source} --[{edge.relation_type}]--> {edge.target}{time_info}")

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

    graph.show(
        node_label_extractor=lambda x: x.name,
        edge_label_extractor=lambda x: f"{x.relation_type}@{x.event_date}" if x.event_date else x.relation_type,
    )
