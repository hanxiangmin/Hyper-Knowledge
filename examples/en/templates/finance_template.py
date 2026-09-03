"""
Finance Domain Template Demo

Usage:
    python examples/en/templates/finance_template.py
"""

from pathlib import Path

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperknowledge import Template

project_root = Path(__file__).resolve().parent.parent.parent.parent

dotenv.load_dotenv()

# ==================== Test Cases (uncomment to select test case) ====================

# // test for Event Timeline
test_data_file = "annual_report_sample.md"
template_name = "finance/event_timeline"

# // test for Ownership Graph
# test_data_file = "ipo_prospectus_sample.md"
# template_name = "finance/ownership_graph"

# // test for Risk Factor Set
# test_data_file = "annual_report_sample.md"
# template_name = "finance/risk_factor_set"

# // test for Sentiment Model
# test_data_file = "financial_news_sample.md"
# template_name = "finance/sentiment_model"

# // test for Earnings Call Summary
# test_data_file = "earnings_call_transcript_sample.md"
# template_name = "finance/earnings_summary"

# ==================== Main Function ====================

def main():
    test_data_dir = project_root / "tests" / "test_data" / "en" / "finance"
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
