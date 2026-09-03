"""
General Domain Template Demo

Usage:
    python examples/en/templates/general_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== Test Cases (uncomment to select test case) ====================

# // test for Base Knowledge Graph
test_data_file = "arbitrary_tech_news.md"
template_name = "general/graph"

# // test for Base Hypergraph
# test_data_file = "encyclopedia_machine_learning.md"
# template_name = "general/hypergraph"

# // test for Base List
# test_data_file = "regulation_company_policy.md"
# template_name = "general/list"

# // test for Biography Graph
# test_data_file = "biography_scientist.md"
# template_name = "general/biography_graph"

# // test for Concept Graph
# test_data_file = "encyclopedia_machine_learning.md"
# template_name = "general/concept_graph"

# ==================== Main Function ====================


def main():
    test_data_dir = project_root / "tests" / "test_data" / "en" / "general"
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
