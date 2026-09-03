"""
AutoList 示例 - 苏轼人生事件

使用 AutoList 从文本中提取列表项，合并多个文本块。

使用方法：
    python examples/zh/autotypes/list_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge import AutoList

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class TimelineEvent(BaseModel):
    """人生事件"""
    year: str = Field(description="事件发生年份")
    title: str = Field(description="事件标题")
    description: str = Field(description="事件描述")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  AutoList 示例 - 苏轼人生事件")
    print("=" * 60)
    print("提取人生事件时间线...")

    timeline = AutoList[TimelineEvent](
        item_schema=TimelineEvent,
        llm_client=llm,
        embedder=embedder,
    )

    timeline.feed_text(text)

    sorted_events = sorted(timeline.items, key=lambda x: x.year)
    print(f"\n提取了 {len(sorted_events)} 个事件")

    for event in sorted_events[:5]:
        print(f"  {event.year}：{event.title}")

    timeline.build_index()

    print("-" * 60)
    print("问答")
    print("-" * 60)
    for q in questions:
        print(f"\n问: {q}")
        try:
            result = timeline.chat(q)
            print(f"答: {result.content}")
        except Exception as e:
            print(f"错误: {e}")

    timeline.show(item_label_extractor=lambda x: f"{x.year}：{x.title}")
