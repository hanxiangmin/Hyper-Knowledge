"""
中医领域模板示例

Usage:
    python examples/templates/tcm_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== 测试用例（取消注释选择要测试的用例） ====================

# // test for 方剂组成图
# test_data_file = "prescription_formulary_sample.md"
# template_name = "tcm/formula_composition"

# // test for 药材属性
# test_data_file = "herb_property_single.md"
# template_name = "tcm/herb_property"

# // test for 药材关系图
# test_data_file = "herbal_compendium_sample.md"
# template_name = "tcm/herb_relation"

# // test for 经络图
# test_data_file = "meridian_treatise_sample.md"
# template_name = "tcm/meridian_graph"

# // test for 证候推理
test_data_file = "medical_case_record_sample.md"
template_name = "tcm/syndrome_reasoning"

# ==================== 主函数 ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "zh" / "tcm"
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
