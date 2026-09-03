"""
时空图示例 - 苏轼传记

使用 AutoSpatioTemporalGraph 从文本中提取时空关系。
展示如何同时理解时间和空间维度的实体关系。

使用方法：
    python examples/zh/autotypes/spatio_temporal_demo.py
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge.types import AutoSpatioTemporalGraph

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class Entity(BaseModel):
    """实体节点"""
    name: str = Field(description="实体名称")
    category: str = Field(description="类别，例如：人物/地点/发明等")
    description: str = Field(description="实体描述")


class SpatioTemporalRelation(BaseModel):
    """时空关系"""
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relation_type: str = Field(description="关系类型，例如：父亲/兄弟/发明/参与等")
    event_date: Optional[str] = Field(description="关系发生的时间", default=None)
    location: Optional[str] = Field(description="关系发生地点，例如：北京等", default=None)


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  时空图示例")
    print("=" * 60)
    print("提取时空关系...")

    graph = AutoSpatioTemporalGraph[Entity, SpatioTemporalRelation](
        node_schema=Entity,
        edge_schema=SpatioTemporalRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        time_in_edge_extractor=lambda x: x.event_date or "",
        location_in_edge_extractor=lambda x: x.location or "",
        llm_client=llm,
        embedder=embedder,
        observation_time="2024-01-01",
        observation_location="北宋",
    )

    graph.feed_text(text)

    print(f"\n提取了 {len(graph.nodes)} 个实体和 {len(graph.edges)} 个关系")

    sorted_edges = sorted(graph.edges, key=lambda x: x.event_date or "")
    for edge in sorted_edges[:5]:
        time_info = f"（{edge.event_date}）" if edge.event_date else ""
        loc_info = f" 在 {edge.location}" if edge.location else ""
        print(f"  {edge.source} --[{edge.relation_type}]--> {edge.target}{time_info}{loc_info}")

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
