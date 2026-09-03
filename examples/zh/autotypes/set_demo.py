"""
AutoSet 示例 - 苏轼相关人物

使用 AutoSet 从文本中提取去重的人物集合。

使用方法：
    python examples/zh/autotypes/set_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge import AutoSet

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class Person(BaseModel):
    """人物实体"""
    name: str = Field(description="人物姓名")
    category: str = Field(description="类别：家人/师友/政敌", default="人物")
    description: str = Field(description="简要描述", default="")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  AutoSet 示例 - 苏轼相关人物")
    print("=" * 60)
    print("提取并去重人物...")

    entities = AutoSet[Person](
        item_schema=Person,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,
    )

    entities.feed_text(text)

    print(f"\n提取了 {len(entities.items)} 个不同人物")

    categories = {}
    for p in entities.items:
        categories.setdefault(p.category, []).append(p)

    for cat, persons in sorted(categories.items()):
        print(f"\n{cat}：")
        for p in persons[:5]:
            print(f"  - {p.name}")

    entities.build_index()

    print("-" * 60)
    print("问答")
    print("-" * 60)
    for q in questions:
        print(f"\n问: {q}")
        try:
            result = entities.chat(q)
            print(f"答: {result.content}")
        except Exception as e:
            print(f"错误: {e}")

    entities.show(item_label_extractor=lambda x: x.name)
