"""
AutoModel 示例 - 苏轼传记摘要

使用 AutoModel 从文本中提取结构化摘要。

使用方法：
    python examples/zh/autotypes/model_demo.py
"""

from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperknowledge import AutoModel

project_root = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "examples" / "zh" / "sushi.md"
QUESTION_FILE = project_root / "examples" / "zh" / "sushi_question.md"


class BiographySummary(BaseModel):
    """传记摘要结构"""
    title: str = Field(description="作品标题")
    subject: str = Field(description="主人公姓名")
    birth_year: Optional[str] = Field(default="", description="出生年份")
    death_year: Optional[str] = Field(default="", description="逝世年份")
    style_name: str = Field(description="字/号", default="")
    era: str = Field(description="所属朝代", default="")
    identity: List[str] = Field(default_factory=list, description="主要身份")
    summary: str = Field(description="人物生平概述")
    major_works: List[str] = Field(default_factory=list, description="代表作品")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  AutoModel 示例 - 苏轼传记摘要")
    print("=" * 60)
    print("提取传记摘要...")

    model = AutoModel(
        data_schema=BiographySummary,
        llm_client=llm,
        embedder=embedder,
    )

    model.feed_text(text)

    data = model.data
    print(f"\n主人公：{data.subject}")
    print(f"生卒年份：{data.birth_year} - {data.death_year}")
    print(f"字号：{data.style_name}")
    print(f"\n摘要：{data.summary}")

    if data.major_works:
        print(f"\n代表作品：")
        for work in data.major_works[:3]:
            print(f"  - {work}")

    model.build_index()

    print("-" * 60)
    print("问答")
    print("-" * 60)
    for q in questions:
        print(f"\n问: {q}")
        try:
            result = model.chat(q)
            print(f"答: {result.content}")
        except Exception as e:
            print(f"错误: {e}")

    model.show(label_extractor=lambda x: x.title)
