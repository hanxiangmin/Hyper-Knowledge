# Financial Report Analysis

Complete guide for extracting financial information from earnings reports and SEC filings.

---

## Scenario

You have a financial document and want to:
- Extract earnings metrics (revenue, EPS, growth)
- Identify risk factors
- Map ownership structures
- Create event timelines

---

## Recommended Templates by Task

### Earnings Summary

**Template:** `finance/earnings_summary`

Best for quarterly/annual earnings reports, 10-Q, 10-K filings.

**Extracts:**
- Revenue and net income
- EPS (basic and diluted)
- YoY and QoQ growth rates
- Segment performance
- Forward guidance

---

### Risk Factors

**Template:** `finance/risk_factor_set`

Best for risk assessment sections of SEC filings.

**Extracts:**
- Risk categories
- Risk descriptions
- Impact assessments

---

### Ownership Structure

**Template:** `finance/ownership_graph`

Best for mapping subsidiaries, investments, and corporate structures.

**Extracts:**
- Subsidiary relationships
- Ownership percentages
- Investment entities

---

## Complete Workflow: Earnings Analysis

### Step 1: Extract Earnings Data

=== "CLI"

    ```bash
    hk parse earnings_10k.md -t finance/earnings_summary -l en -o ./earnings/
    ```

=== "Python"

    ```python
    from hyperknowledge import Template

    # Load report
    with open("earnings_report.md", "r") as f:
        report = f.read()

    # Create template
    ka = Template.create("finance/earnings_summary", "en")

    # Extract
    result = ka.parse(report)

    # Access data
    print(f"Revenue: ${result.data.revenue:,.0f}")
    print(f"EPS: ${result.data.eps:.2f}")
    print(f"YoY Growth: {result.data.yoy_growth}%")
    ```

**Example Output:**
```python
{
    "revenue": 1234567890,
    "net_income": 98765432,
    "eps": 2.45,
    "eps_diluted": 2.40,
    "yoy_growth": 15.3,
    "qoq_growth": 3.2,
    "segments": [
        {"name": "Cloud Services", "revenue": 500000000},
        {"name": "Hardware", "revenue": 734567890}
    ],
    "guidance": {
        "next_quarter_revenue": "$1.3B - $1.4B",
        "full_year_eps": "$10.00 - $11.00"
    }
}
```

---

### Step 2: Extract Risk Factors

> **Note:** The following steps assume you used the Python approach in Step 1. If you used CLI, load the result with `ka.load("./earnings/")`.

```python
# Extract risks
risk_ka = Template.create("finance/risk_factor_set", "en")
risk_result = risk_ka.parse(report)

print(f"\nIdentified {len(risk_result.data.items)} risk factors:")
for risk in risk_result.data.items:
    print(f"\n[{risk.category}] {risk.description[:100]}...")
```

---

### Step 3: Save and Compare

```python
# Save earnings data
result.dump("./earnings_q3_2024/")

# Later, compare quarters
from pathlib import Path
import json

def compare_quarters(q1_path, q2_path):
    """Compare earnings between two quarters."""
    q1_data = json.load(open(Path(q1_path) / "data.json"))
    q2_data = json.load(open(Path(q2_path) / "data.json"))
    
    revenue_change = ((q2_data["revenue"] - q1_data["revenue"]) 
                      / q1_data["revenue"] * 100)
    
    print(f"Revenue Change: {revenue_change:+.1f}%")
    print(f"Q1: ${q1_data['revenue']:,.0f}")
    print(f"Q2: ${q2_data['revenue']:,.0f}")

compare_quarters("./earnings_q2_2024/", "./earnings_q3_2024/")
```

---

## Ownership Structure Analysis

### Extract Corporate Structure

```python
from hyperknowledge import Template

# Analyze ownership
ka = Template.create("finance/ownership_graph", "en")
result = ka.parse(ownership_report)

# Visualize structure
result.build_index()
result.show()

# Query ownership
response = result.chat("What subsidiaries does the company own 100%?")
print(response.content)
```

**Example Output:**
```python
# Entities
[
    {"name": "Parent Corp", "type": "holding_company"},
    {"name": "Subsidiary A", "type": "subsidiary"},
    {"name": "Joint Venture B", "type": "joint_venture"}
]

# Relations
[
    {"source": "Parent Corp", "target": "Subsidiary A", 
     "type": "owns", "percentage": 100},
    {"source": "Parent Corp", "target": "Joint Venture B", 
     "type": "owns", "percentage": 51}
]
```

---

## Financial Event Timeline

### Track Financial Events

```python
# Extract event timeline
ka = Template.create("finance/event_timeline", "en")
result = ka.parse(report)

# Show timeline
for edge in result.edges:
    if hasattr(edge, 'time'):
        print(f"{edge.time}: {edge.source} - {edge.type} - {edge.target}")
```

**Example Events:**
- Product launches
- Acquisition announcements
- Dividend declarations
- Management changes

---

## Comparison Table

| Template | Best For | Output |
|----------|----------|--------|
| `earnings_summary` | Financial metrics | Structured model |
| `risk_factor_set` | Risk assessment | Unique risk items |
| `ownership_graph` | Corporate structure | Entity network |
| `event_timeline` | Financial events | Temporal graph |
| `sentiment_model` | Market sentiment | Sentiment analysis |

---

## Batch Processing Multiple Reports

```python
"""Batch process financial reports."""

from hyperknowledge import Template
from pathlib import Path
import pandas as pd

def batch_extract_reports(report_dir, output_dir):
    """Extract data from multiple financial reports."""
    
    ka = Template.create("finance/earnings_summary", "en")
    results = []
    
    for report_file in Path(report_dir).glob("*.md"):
        print(f"Processing {report_file.name}...")
        
        text = report_file.read_text()
        result = ka.parse(text)
        
        # Save individual
        output_path = Path(output_dir) / report_file.stem
        result.dump(output_path)
        
        # Collect for aggregation
        results.append({
            "file": report_file.name,
            "revenue": result.data.revenue,
            "eps": result.data.eps,
            "yoy_growth": result.data.yoy_growth
        })
    
    # Create summary table
    df = pd.DataFrame(results)
    df.to_csv(Path(output_dir) / "summary.csv", index=False)
    
    print(f"\nProcessed {len(results)} reports")
    print(f"Summary saved to: {output_dir}/summary.csv")
    
    return df

# Usage
df = batch_extract_reports("./reports/", "./extracted/")
```

---

## Tips for Best Results

### 1. Document Types

| Document | Recommended Template |
|----------|---------------------|
| 10-K Annual Report | `earnings_summary` + `risk_factor_set` |
| 10-Q Quarterly | `earnings_summary` |
| Proxy Statement | `ownership_graph` |
| Earnings Call Transcript | `sentiment_model` + `event_timeline` |
| Investor Presentation | `earnings_summary` |

### 2. Language Support

=== "CLI"

    ```bash
    # US companies (English)
    hk parse report.md -t finance/earnings_summary -l en

    # Chinese companies (中文财报)
    hk parse report.md -t finance/earnings_summary -l zh
    ```

### 3. Combining Templates

```python
from hyperknowledge import Template

# Parse report with multiple templates
text = open("10k_report.md").read()

# Extract earnings
earnings = Template.create("finance/earnings_summary", "en").parse(text)

# Extract risks
risks = Template.create("finance/risk_factor_set", "en").parse(text)

# Save combined
earnings.dump("./10k_earnings/")
risks.dump("./10k_risks/")
```

### 4. Data Validation

```python
# Check extracted data
result = ka.parse(report)

def validate_earnings(data):
    """Validate earnings data."""
    assert data.revenue > 0, "Revenue must be positive"
    assert data.eps is not None, "EPS is required"
    assert -100 < data.yoy_growth < 1000, "Growth seems unreasonable"
    print("✓ Data validation passed")

validate_earnings(result.data)
```

---

## See Also

- [Choose by Task](../choosing/by-task.md) — Other financial analysis templates
- [Finance Templates](../reference/finance.md) — All finance templates
- [Custom Templates Guide](../../python/guides/custom-templates.md) — Create custom financial templates
