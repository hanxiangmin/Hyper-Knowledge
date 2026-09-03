"""
医学领域模板示例

Usage:
    python examples/templates/medicine_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== 测试用例（取消注释选择要测试的用例） ====================

# // test for 解剖结构图
# test_data_file = "textbook_sample.md"
# template_name = "medicine/anatomy_graph"

# // test for 出院指导
test_data_file = "discharge_summary_sample.md"
template_name = "medicine/discharge_instruction"

# // test for 药物相互作用图
# test_data_file = "package_insert_sample.md"
# template_name = "medicine/drug_interaction"

# // test for 医院事件时间线
# test_data_file = "pathology_report_sample.md"
# template_name = "medicine/hospital_timeline"

# // test for 治疗方案图
# test_data_file = "clinical_guideline_sample.md"
# template_name = "medicine/treatment_map"

# ==================== 主函数 ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "zh" / "medicine"
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
