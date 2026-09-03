"""
法律领域模板示例

Usage:
    python examples/templates/legal_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== 测试用例（取消注释选择要测试的用例） ====================

# // test for 案例引用图
# test_data_file = "legal_treatise_sample.md"
# template_name = "legal/case_citation"

# // test for 案件事实时间线
# test_data_file = "court_judgment_sample.md"
# template_name = "legal/case_fact_timeline"

# // test for 合规清单
# test_data_file = "compliance_filing_sample.md"
# template_name = "legal/compliance_list"

# // test for 合同义务
test_data_file = "msa_contract_sample.md"
template_name = "legal/contract_obligation"

# // test for 术语定义
# test_data_file = "msa_contract_sample.md"
# template_name = "legal/defined_term_set"

# ==================== 主函数 ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "zh" / "legal"
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
