# Legal Document Analysis

Complete guide for extracting information from legal contracts and case documents.

---

## Scenario

You have a legal document and want to:
- Extract contract obligations and deadlines
- Identify defined terms
- Create case chronologies
- Map precedent relationships

---

## Recommended Templates by Task

### Contract Obligations

**Template:** `legal/contract_obligation`

Best for service agreements, NDAs, employment contracts, vendor agreements.

**Extracts:**
- Party obligations
- Deadlines and milestones
- Deliverables
- Conditions precedent
- Breach consequences

---

### Defined Terms

**Template:** `legal/defined_term_set`

Best for extracting all capitalized defined terms from contracts.

**Extracts:**
- Term definitions
- Cross-references
- Definition locations

---

### Case Timeline

**Template:** `legal/case_fact_timeline`

Best for litigation chronologies, case summaries.

**Extracts:**
- Chronological events
- Party actions
- Court decisions

---

## Complete Workflow: Contract Analysis

### Step 1: Extract Obligations

=== "CLI"

    ```bash
    hk parse contract.md -t legal/contract_obligation -l en -o ./contract/
    ```

=== "Python"

    ```python
    from hyperknowledge import Template

    # Load contract
    with open("service_agreement.md", "r") as f:
        contract = f.read()

    # Create template
    ka = Template.create("legal/contract_obligation", "en")

    # Extract
    result = ka.parse(contract)

    print(f"Found {len(result.data.items)} obligations")
    ```

**Example Output:**
```python
{
    "items": [
        {
            "party": "Service Provider",
            "obligation": "Deliver software module within 30 days",
            "deadline": "2024-03-15",
            "deliverable": "Source code and documentation",
            "conditions": "Upon receipt of payment"
        },
        {
            "party": "Client",
            "obligation": "Pay milestone payment",
            "deadline": "2024-03-01",
            "amount": "$50,000",
            "conditions": "Upon acceptance of deliverables"
        }
    ]
}
```

---

### Step 2: Extract Defined Terms

> **Note:** The following steps assume you used the Python approach in Step 1. If you used CLI, load the result with `ka.load("./contract/")`.

```python
# Extract defined terms
terms_ka = Template.create("legal/defined_term_set", "en")
terms_result = terms_ka.parse(contract)

print(f"\nFound {len(terms_result.data.items)} defined terms:")
for term in terms_result.data.items:
    print(f"\n{term.term}: {term.definition}")
```

**Example:**
```
"Confidential Information": Any and all non-public, proprietary, or confidential information...

"Deliverables": The software, documentation, and materials to be delivered...

"Effective Date": The date first written above...
```

---

### Step 3: Build Contract Knowledge Base

```python
# Build index for querying
result.build_index()

# Save for future reference
result.dump("./contract_analysis/")

# Query obligations
response = result.chat("What are Service Provider's obligations related to data security?")
print(response.content)

response = result.chat("List all payment milestones and their due dates")
print(response.content)
```

---

## Case Analysis Workflow

### Extract Case Timeline

```python
from hyperknowledge import Template

# Load case document
with open("case_summary.md", "r") as f:
    case = f.read()

# Extract timeline
ka = Template.create("legal/case_fact_timeline", "en")
result = ka.parse(case)

# Display chronology
print("Case Timeline:")
for edge in sorted(result.edges, key=lambda e: e.time if hasattr(e, 'time') else ''):
    if hasattr(edge, 'time'):
        print(f"\n{edge.time}:")
        print(f"  Event: {edge.source}")
        print(f"  Action: {edge.type}")
        print(f"  Party: {edge.target}")

# Visualize
result.build_index()
result.show()
```

**Example Output:**
```
2023-01-15:
  Event: Complaint filed
  Action: initiated
  Party: Plaintiff

2023-02-01:
  Event: Motion to dismiss
  Action: filed
  Party: Defendant

2023-03-15:
  Event: Discovery phase
  Action: began
  Party: Both parties
```

---

## Case Precedent Analysis

### Map Precedent Relationships

```python
# Extract case citations
ka = Template.create("legal/case_citation", "en")
result = ka.parse(legal_opinion)

# Analyze citation network
print("Cases cited:")
for node in result.nodes:
    if node.type == "case":
        print(f"  - {node.name} ({node.citation})")
        print(f"    Principle: {node.principle[:100]}...")

# Visualize precedent network
result.build_index()
result.show()
```

---

## Comparison Table

| Template | Best For | Output |
|----------|----------|--------|
| `contract_obligation` | Service agreements, NDAs | List of obligations |
| `defined_term_set` | Defined terms extraction | Set of term definitions |
| `case_fact_timeline` | Litigation chronologies | Temporal graph |
| `case_citation` | Precedent analysis | Citation network |
| `compliance_list` | Regulatory requirements | Compliance checklist |

---

## Batch Contract Processing

```python
"""Batch analyze multiple contracts."""

from hyperknowledge import Template
from pathlib import Path
import pandas as pd

def analyze_contract_folder(folder_path, output_dir):
    """Extract obligations from all contracts in folder."""
    
    ka = Template.create("legal/contract_obligation", "en")
    all_obligations = []
    
    for contract_file in Path(folder_path).glob("*.md"):
        print(f"Processing {contract_file.name}...")
        
        text = contract_file.read_text()
        result = ka.parse(text)
        
        # Save individual
        output_path = Path(output_dir) / contract_file.stem
        result.dump(output_path)
        
        # Collect obligations
        for obl in result.data.items:
            all_obligations.append({
                "contract": contract_file.name,
                "party": obl.party,
                "obligation": obl.obligation,
                "deadline": getattr(obl, 'deadline', 'N/A'),
                "deliverable": getattr(obl, 'deliverable', 'N/A')
            })
    
    # Create summary
    df = pd.DataFrame(all_obligations)
    df.to_csv(Path(output_dir) / "all_obligations.csv", index=False)
    
    print(f"\nProcessed {len(list(Path(folder_path).glob('*.md')))} contracts")
    print(f"Found {len(all_obligations)} total obligations")
    
    return df

# Usage
df = analyze_contract_folder("./contracts/", "./contract_analysis/")

# Find upcoming deadlines
from datetime import datetime
df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
upcoming = df[df['deadline'] > datetime.now()].sort_values('deadline')
print("\nUpcoming deadlines:")
print(upcoming[['contract', 'party', 'deadline', 'obligation']].head(10))
```

---

## Tips for Best Results

### 1. Document Preparation

- Convert PDFs to clean Markdown
- Remove headers/footers/page numbers
- Preserve paragraph structure
- Keep section headings

### 2. Contract Types

| Contract Type | Primary Template | Secondary Template |
|--------------|------------------|-------------------|
| Service Agreement | `contract_obligation` | `defined_term_set` |
| NDA | `contract_obligation` | `defined_term_set` |
| Employment Contract | `contract_obligation` | `defined_term_set` |
| License Agreement | `contract_obligation` | `defined_term_set` |
| Litigation Summary | `case_fact_timeline` | `case_citation` |
| Regulatory Document | `compliance_list` | - |

### 3. Multi-Language Support

=== "CLI"

    ```bash
    # English contracts
    hk parse contract.md -t legal/contract_obligation -l en

    # Chinese contracts (中文合同)
    hk parse contract.md -t legal/contract_obligation -l zh
    ```

### 4. Combining Templates

```python
# Comprehensive contract analysis
text = open("contract.md").read()

# Extract obligations
obligations = Template.create("legal/contract_obligation", "en").parse(text)

# Extract defined terms
terms = Template.create("legal/defined_term_set", "en").parse(text)

# Save both
obligations.dump("./contract_obligations/")
terms.dump("./contract_terms/")

# Cross-reference
print("\nObligations referencing defined terms:")
for obl in obligations.data.items:
    for term in terms.data.items:
        if term.term.lower() in obl.obligation.lower():
            print(f"  '{term.term}' in: {obl.obligation[:60]}...")
```

---

## Example: Contract Review Checklist

```python
"""Automated contract review checklist."""

from hyperknowledge import Template
from datetime import datetime

def contract_review_checklist(contract_path):
    """Generate review checklist from contract."""
    
    text = open(contract_path).read()
    
    # Extract obligations
    obl_ka = Template.create("legal/contract_obligation", "en")
    obl_result = obl_ka.parse(text)
    
    # Extract terms
    terms_ka = Template.create("legal/defined_term_set", "en")
    terms_result = terms_ka.parse(text)
    
    print("=" * 60)
    print("CONTRACT REVIEW CHECKLIST")
    print("=" * 60)
    
    # Obligations summary
    print("\n## OBLIGATIONS SUMMARY")
    print(f"Total obligations: {len(obl_result.data.items)}")
    
    party_obligations = {}
    for obl in obl_result.data.items:
        party = obl.party
        if party not in party_obligations:
            party_obligations[party] = []
        party_obligations[party].append(obl)
    
    for party, obligations in party_obligations.items():
        print(f"\n{party}: {len(obligations)} obligations")
        for obl in obligations[:3]:  # Show first 3
            deadline = getattr(obl, 'deadline', 'No deadline')
            print(f"  - {obl.obligation[:50]}... (Due: {deadline})")
    
    # Critical dates
    print("\n## CRITICAL DATES")
    deadlines = [obl.deadline for obl in obl_result.data.items 
                 if hasattr(obl, 'deadline') and obl.deadline]
    for deadline in sorted(deadlines)[:5]:
        print(f"  - {deadline}")
    
    # Key terms
    print("\n## KEY DEFINED TERMS")
    for term in terms_result.data.items[:10]:
        print(f"  - {term.term}")
    
    # Risk flags
    print("\n## RISK FLAGS TO REVIEW")
    risk_keywords = ['unlimited', 'perpetual', 'sole discretion', 'waiver', 'indemnify']
    for obl in obl_result.data.items:
        for keyword in risk_keywords:
            if keyword.lower() in obl.obligation.lower():
                print(f"  ⚠ Contains '{keyword}': {obl.obligation[:60]}...")
    
    print("\n" + "=" * 60)

# Usage
contract_review_checklist("service_agreement.md")
```

---

## See Also

- [Choose by Task](../choosing/by-task.md) — Other legal analysis templates
- [Legal Templates](../reference/legal.md) — All legal templates
- [Custom Templates Guide](../../python/guides/custom-templates.md) — Create custom legal templates
