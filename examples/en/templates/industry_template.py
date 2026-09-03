"""
Industry Domain Template Demo

Usage:
    python examples/en/templates/industry_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== Test Cases (uncomment to select test case) ====================

# // test for Equipment Topology
test_data_file = "equipment_technical_manual.md"
template_name = "industry/equipment_topology"

# // test for Operation Flow
# test_data_file = "operation_maintenance_manual.md"
# template_name = "industry/operation_flow"

# // test for Safety Control
# test_data_file = "safety_management_handbook.md"
# template_name = "industry/safety_control"

# // test for Emergency Response Timeline
# test_data_file = "safety_management_handbook.md"
# template_name = "industry/emergency_response"

# // test for Failure Case
# test_data_file = "failure_analysis_report.md"
# template_name = "industry/failure_case"

# ==================== Main Function ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "en" / "industry"
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
