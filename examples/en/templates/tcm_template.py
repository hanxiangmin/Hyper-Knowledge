"""
Traditional Chinese Medicine Domain Template Demo

Usage:
    python examples/en/templates/tcm_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== Test Cases (uncomment to select test case) ====================

# // test for Formula Composition Graph
# test_data_file = "prescription_formulary_sample.md"
# template_name = "tcm/formula_composition"

# // test for Herb Properties
# test_data_file = "herb_property_single.md"
# template_name = "tcm/herb_property"

# // test for Herb Relationship Graph
# test_data_file = "herbal_compendium_sample.md"
# template_name = "tcm/herb_relation"

# // test for Meridian Graph
# test_data_file = "meridian_treatise_sample.md"
# template_name = "tcm/meridian_graph"

# // test for Syndrome Reasoning
test_data_file = "medical_case_record_sample.md"
template_name = "tcm/syndrome_reasoning"

# ==================== Main Function ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "en" / "tcm"
    input_file = test_data_dir / test_data_file

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("=" * 80)
    print(f"🧪 Testing template: {template_name}")
    print(f"📂 Test data: {input_file}")
    print("=" * 80)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    extractor = Template.create(
        template_name,
        language="en",
        llm_client=llm,
        embedder=embedder,
    )

    print("\n📥 Extracting knowledge summary...")
    extractor.feed_text(text)
    print("✅ Extraction complete!\n")

    extractor.show()


if __name__ == "__main__":
    main()
