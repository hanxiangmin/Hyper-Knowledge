"""
金融领域模板示例

Usage:
    python examples/templates/finance_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== 测试用例（取消注释选择要测试的用例） ====================

# // test for 重大事件时间线
test_data_file = "annual_report_sample.md"
template_name = "finance/event_timeline"

# // test for 股权结构图
# test_data_file = "ipo_prospectus_sample.md"
# template_name = "finance/ownership_graph"

# // test for 风险因子集合
# test_data_file = "annual_report_sample.md"
# template_name = "finance/risk_factor_set"

# // test for 市场情绪模型
# test_data_file = "financial_news_sample.md"
# template_name = "finance/sentiment_model"

# // test for 财报电话会议摘要
# test_data_file = "earnings_call_transcript_sample.md"
# template_name = "finance/earnings_summary"

# ==================== 主函数 ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "zh" / "finance"
    input_file = test_data_dir / test_data_file
    
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    print("=" * 80)
    print(f"🧪 测试模板: {template_name}")
    print(f"📂 测试数据: {input_file}")
    print("=" * 80)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    extractor = Template.create(
        template_name,
        language="zh",
        llm_client=llm,
        embedder=embedder,
    )

    print("\n📥 正在提取知识摘要...")
    extractor.feed_text(text)
    print("✅ 提取完成！\n")

    extractor.show()


if __name__ == "__main__":
    main()
