"""
Legal Domain Template Demo

Usage:
    python examples/en/templates/legal_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== Test Cases (uncomment to select test case) ====================

# // test for Case Citation Graph
# test_data_file = "legal_treatise_sample.md"
# template_name = "legal/case_citation"

# // test for Case Fact Timeline
# test_data_file = "court_judgment_sample.md"
# template_name = "legal/case_fact_timeline"

# // test for Compliance Checklist
# test_data_file = "compliance_filing_sample.md"
# template_name = "legal/compliance_list"

# // test for Contract Obligation
test_data_file = "msa_contract_sample.md"
template_name = "legal/contract_obligation"

# // test for Defined Terms
# test_data_file = "msa_contract_sample.md"
# template_name = "legal/defined_term_set"

# ==================== Main Function ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "en" / "legal"
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
