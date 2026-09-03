"""
Medicine Domain Template Demo

Usage:
    python examples/en/templates/medicine_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== Test Cases (uncomment to select test case) ====================

# // test for Anatomy Structure Graph
# test_data_file = "textbook_sample.md"
# template_name = "medicine/anatomy_graph"

# // test for Discharge Instruction
test_data_file = "discharge_summary_sample.md"
template_name = "medicine/discharge_instruction"

# // test for Drug Interaction Graph
# test_data_file = "package_insert_sample.md"
# template_name = "medicine/drug_interaction"

# // test for Hospital Event Timeline
# test_data_file = "pathology_report_sample.md"
# template_name = "medicine/hospital_timeline"

# // test for Treatment Plan Graph
# test_data_file = "clinical_guideline_sample.md"
# template_name = "medicine/treatment_map"

# ==================== Main Function ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "en" / "medicine"
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
