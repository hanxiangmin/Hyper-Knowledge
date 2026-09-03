# Finance Templates

Financial document analysis and extraction.

---

## Overview

Finance templates are optimized for extracting structured information from financial documents.

---

## Templates

### earnings_summary

**Type**: model

**Purpose**: Extract key metrics from earnings reports

**Best for**: 
- Quarterly earnings (10-Q)
- Annual reports (10-K)
- Earnings call transcripts

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `company_name` | str | Company name |
| `quarter` | str | Fiscal quarter |
| `revenue` | float | Total revenue |
| `net_income` | float | Net income |
| `eps` | float | Earnings per share |
| `yoy_growth` | float | Year-over-year growth |

=== "CLI"

    ```bash
    hk parse 10q.md -t finance/earnings_summary -l en
    ```

=== "Python"

    ```python
    ka = Template.create("finance/earnings_summary", "en")
    result = ka.parse(earnings_text)

    print(f"Revenue: ${result.data.revenue}B")
    print(f"EPS: ${result.data.eps}")
    ```

---

### ownership_graph

**Type**: graph

**Purpose**: Extract company ownership structures

**Best for**:
- Shareholder reports
- Proxy statements
- Corporate structures

**Entities**:
- Companies
- Shareholders
- Subsidiaries

**Relations**:
- `owns` — Ownership relationships
- `controls` — Control relationships
- `subsidiary_of` — Subsidiary relationships

=== "CLI"

    ```bash
    hk parse proxy.md -t finance/ownership_graph -l en
    ```

=== "Python"

    ```python
    ka = Template.create("finance/ownership_graph", "en")
    result = ka.parse(proxy_statement)

    # Build index for interactive search/chat in visualization
    result.build_index()

    result.show()  # Shows ownership network with interactive features
    ```

---

### event_timeline

**Type**: temporal_graph

**Purpose**: Extract financial events with dates

**Best for**:
- Corporate event histories
- M&A timelines
- Market events

**Features**:

- Event dates
- Event types (merger, acquisition, IPO, etc.)
- Related entities

=== "CLI"

    ```bash
    hk parse history.md -t finance/event_timeline -l en
    ```

=== "Python"

    ```python
    ka = Template.create("finance/event_timeline", "en")
    result = ka.parse(history_text)

    print(f"Events: {len(result.nodes)}")
    for node in result.nodes:
        print(f"  - {node.name}")
    ```

---

### risk_factor_set

**Type**: set

**Purpose**: Extract unique risk factors

**Best for**:
- Risk factor sections
- Due diligence reports
- Risk assessments

=== "CLI"

    ```bash
    hk parse 10k.md -t finance/risk_factor_set -l en
    ```

=== "Python"

    ```python
    ka = Template.create("finance/risk_factor_set", "en")
    result = ka.parse(risk_section)

    print(f"Found {len(result.data.items)} risk factors")
    for risk in result.data.items:
        print(f"  - {risk}")
    ```

---

### sentiment_model

**Type**: model

**Purpose**: Extract sentiment indicators

**Best for**:
- News articles
- Analyst reports
- Social media sentiment

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `sentiment` | str | Overall sentiment (positive/negative/neutral) |
| `confidence` | float | Confidence score |
| `key_points` | list[str] | Key sentiment indicators |

=== "CLI"

    ```bash
    hk parse article.md -t finance/sentiment_model -l en
    ```

=== "Python"

    ```python
    ka = Template.create("finance/sentiment_model", "en")
    result = ka.parse(article_text)

    print(f"Sentiment: {result.data.sentiment}")
    print(f"Confidence: {result.data.confidence}")
    for point in result.data.key_points:
        print(f"  - {point}")
    ```

---

## Use Cases

### Use Case 1: Quarterly Report Analysis

```python
from hyperknowledge import Template

# Extract earnings
ka = Template.create("finance/earnings_summary", "en")
q1 = ka.parse(q1_report)
q2 = ka.parse(q2_report)

# Compare
print(f"Q1 Revenue: ${q1.data.revenue}B")
print(f"Q2 Revenue: ${q2.data.revenue}B")
print(f"Growth: {(q2.data.revenue - q1.data.revenue) / q1.data.revenue * 100:.1f}%")
```

### Use Case 2: Ownership Structure

```python
ka = Template.create("finance/ownership_graph", "en")
ownership = ka.parse(proxy_statement)

# Find major shareholders
shareholders = [
    e for e in ownership.data.entities 
    if e.type == "shareholder"
]

for sh in sorted(shareholders, key=lambda x: x.stake, reverse=True)[:5]:
    print(f"{sh.name}: {sh.stake}%")
```

### Use Case 3: Risk Assessment

```python
ka = Template.create("finance/risk_factor_set", "en")
risk_factors = ka.parse(risk_section)

# Categorize risks
for risk in risk_factors.data.items:
    if "regulatory" in risk.lower():
        print(f"Regulatory Risk: {risk}")
    elif "market" in risk.lower():
        print(f"Market Risk: {risk}")
```

---

## Data Sources

These templates work well with:
- SEC filings (10-K, 10-Q, 8-K)
- Earnings call transcripts
- Investor presentations
- Analyst reports
- Financial news

---

## Tips

1. **Use earnings_summary for quick metrics** — Fast extraction of key numbers
2. **Use ownership_graph for structure** — Visualize corporate hierarchies
3. **Use event_timeline for history** — Track corporate events
4. **Combine templates** — Use multiple templates for comprehensive analysis

---

## See Also

- [Template Overview](overview.md)
- [How to Choose](../how-to-choose.md)
- [General Templates](general.md)
