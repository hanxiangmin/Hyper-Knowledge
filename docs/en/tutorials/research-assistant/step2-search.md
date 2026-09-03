# Step 2: Semantic Search

Build a searchable knowledge abstract.

---

## Goal

Enable semantic search over the extracted knowledge to find relevant concepts and sections.

---

## Why Semantic Search?

Unlike keyword search, semantic search:
- Understands context and meaning
- Finds relevant content even with different words
- Handles synonyms and related concepts

---

## Using CLI

### Basic Search

```bash
hk search ./paper_kb/ "attention mechanism"
```

### Natural Language Queries

```bash
hk search ./paper_kb/ "What are the main contributions?"
```

### Get More Results

```bash
hk search ./paper_kb/ "transformer architecture" -n 10
```

---

## Using Python

### Script

```python
"""Step 2: Semantic search over knowledge abstract."""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template

KB_DIR = "./paper_kb/"

def main():
    # Load knowledge abstract
    print("Loading knowledge abstract...")
    ka = Template.create("general/concept_graph", language="en")
    ka.load(KB_DIR)
    
    # Ensure index is built
    print("Building search index...")
    ka.build_index()
    
    # Interactive search loop
    print("\n" + "="*50)
    print("Semantic Search Interface")
    print("="*50)
    print("Type your query (or 'quit' to exit)\n")
    
    while True:
        query = input("Search: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        # Search
        results = ka.search(query, top_k=5)
        
        # Display results
        print(f"\nFound {len(results)} results:\n")
        
        for i, item in enumerate(results, 1):
            if hasattr(item, 'name'):  # Entity
                print(f"{i}. [{item.type}] {item.name}")
                if hasattr(item, 'description'):
                    print(f"   {item.description[:100]}...")
            elif hasattr(item, 'source'):  # Relation
                print(f"{i}. {item.source} --{item.type}--> {item.target}")
            print()
        
        print("-" * 50)
    
    print("\n✓ Step 2 complete!")
    print("Next: Run 'python step3_chat.py'")

if __name__ == "__main__":
    main()
```

### Run

```bash
python step2_search.py
```

**Example Session:**
```
Search: transformer architecture

Found 3 results:

1. [model] Transformer
   A neural network architecture based on attention...

2. [concept] Self-Attention
   Mechanism allowing the model to weigh input tokens...

3. [concept] Multi-Head Attention
   Multiple attention heads operating in parallel...

--------------------------------------------------
Search: quit
```

---

## Search Tips

### Effective Queries

| Query Type | Example | Use When |
|------------|---------|----------|
| Concept | "attention mechanism" | Finding specific concepts |
| Question | "What are the main contributions?" | Broad exploration |
| Comparison | "transformer vs rnn" | Finding comparisons |
| Results | "bleu score results" | Finding specific data |

### Improving Results

1. **Be specific**: "transformer encoder" vs "transformer"
2. **Use natural language**: "How does attention work?"
3. **Try synonyms**: "attention" → "self-attention" → "query-key-value"
4. **Increase top_k**: `top_k=10` for broader results

---

## Building Search into Your App

```python
class ResearchSearch:
    def __init__(self, ka_path):
        self.ka = Template.create("general/concept_graph", "en")
        self.ka.load(ka_path)
        self.ka.build_index()
    
    def find_concepts(self, query, n=5):
        """Find concepts related to query."""
        results = self.ka.search(query, top_k=n)
        return [r for r in results if hasattr(r, 'name')]
    
    def find_relationships(self, concept):
        """Find relationships for a concept."""
        return [
            r for r in self.ka.data.relations
            if r.source == concept or r.target == concept
        ]

# Usage
search = ResearchSearch("./paper_kb/")
concepts = search.find_concepts("attention", n=10)
```

---

## Next Step

→ [Step 3: Q&A System](step3-chat.md)
