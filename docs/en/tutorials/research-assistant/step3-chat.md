# Step 3: Q&A System

Create an interactive Q&A interface.

---

## Goal

Build a conversational interface that answers questions about the research paper using natural language.

---

## How It Works

1. User asks a question
2. System retrieves relevant context from knowledge abstract
3. LLM generates answer based on retrieved context
4. Response includes citations from the paper

---

## Using CLI

### Single Question

```bash
hk talk ./paper_kb/ -q "What are the main contributions of this paper?"
```

### Interactive Mode

```bash
hk talk ./paper_kb/ -i
```

**Example Session:**
```
Entering interactive mode. Type 'exit' or 'quit' to stop.

> What is the Transformer architecture?

The Transformer is a novel neural network architecture introduced in 
this paper that relies entirely on attention mechanisms, dispensing 
with recurrence and convolutions entirely...

> How does it compare to RNNs?

Unlike RNNs, which process sequences sequentially, the Transformer 
processes all positions in parallel, making it more efficient for 
training on large datasets...

> exit
```

---

## Using Python

### Script

```python
"""Step 3: Interactive Q&A system."""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template

KB_DIR = "./paper_kb/"

class ResearchAssistant:
    def __init__(self, ka_path):
        print("Loading research assistant...")
        self.ka = Template.create("general/concept_graph", "en")
        self.ka.load(ka_path)
        self.ka.build_index()
        print("✓ Ready!\n")
    
    def ask(self, question, top_k=5):
        """Ask a question about the paper."""
        response = self.ka.chat(question, top_k=top_k)
        return response.content
    
    def interactive(self):
        """Run interactive Q&A session."""
        print("="*60)
        print("Research Assistant - Ask me about the paper!")
        print("="*60)
        print("Type 'quit' to exit\n")
        
        while True:
            question = input("\nQ: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            print("\nThinking...")
            answer = self.ask(question)
            print(f"\nA: {answer}\n")
            print("-"*60)
        
        print("\nGoodbye!")

def main():
    assistant = ResearchAssistant(KB_DIR)
    assistant.interactive()

if __name__ == "__main__":
    main()
```

### Run

```bash
python step3_chat.py
```

---

## Example Questions

### Understanding the Paper

- "What problem does this paper solve?"
- "What are the main contributions?"
- "What is the key innovation?"

### Technical Details

- "Explain the attention mechanism"
- "What is multi-head attention?"
- "How is positional encoding handled?"

### Results and Evaluation

- "What datasets were used?"
- "What were the main results?"
- "How does it compare to baseline methods?"

### Limitations and Future Work

- "What are the limitations?"
- "What future work is suggested?"

---

## Advanced Features

### Citation Tracking

```python
def ask_with_citations(assistant, question):
    """Get answer with source citations."""
    response = assistant.ka.chat(question, top_k=5)
    
    print(f"Answer: {response.content}\n")
    
    # Show retrieved sources
    retrieved_nodes = response.additional_kwargs.get("retrieved_nodes", [])
    retrieved_edges = response.additional_kwargs.get("retrieved_edges", [])
    if retrieved_nodes or retrieved_edges:
        print("Sources:")
        for node in retrieved_nodes:
            print(f"  - {node.name}")
        for edge in retrieved_edges:
            print(f"  - {edge.source} -> {edge.target}")
```

### Question Suggestions

```python
def suggest_questions(assistant):
    """Suggest questions based on paper content."""
    suggestions = [
        "What are the main contributions?",
        "What problem does this solve?",
        "What are the key results?",
        "How does this compare to prior work?",
    ]
    return suggestions
```

### Exporting Q&A History

```python
def export_history(questions_answers, filename="qa_history.json"):
    """Export Q&A session to file."""
    import json
    with open(filename, 'w') as f:
        json.dump(questions_answers, f, indent=2)
```

---

## Complete Application

Putting it all together:

```python
"""Complete Research Assistant Application."""

from hyperknowledge import Template
from pathlib import Path

class ResearchAssistantApp:
    def __init__(self, paper_path, kb_dir="./paper_kb/"):
        self.paper_path = paper_path
        self.ka_dir = kb_dir
        self.ka = None
        
        # Load or create knowledge abstract
        if Path(kb_dir).exists():
            self._load_kb()
        else:
            self._create_kb()
    
    def _create_kb(self):
        """Create knowledge abstract from paper."""
        print("Creating knowledge abstract...")
        ka = Template.create("general/concept_graph", "en")
        text = Path(self.paper_path).read_text()
        self.ka = ka.parse(text)
        self.ka.build_index()
        self.ka.dump(self.ka_dir)
        print("✓ Knowledge base created\n")
    
    def _load_kb(self):
        """Load existing knowledge abstract."""
        print("Loading knowledge abstract...")
        self.ka = Template.create("general/concept_graph", "en")
        self.ka.load(self.ka_dir)
        print("✓ Knowledge base loaded\n")
    
    def search(self, query):
        """Search the paper."""
        return self.ka.search(query)
    
    def ask(self, question):
        """Ask a question."""
        return self.ka.chat(question).content
    
    def visualize(self):
        """Open visualization."""
        self.ka.show()

![Interactive Visualization](../../../../assets/en_show.jpg)

    def run(self):
        """Run interactive session."""
        print("="*60)
        print("Research Assistant")
        print("Commands: search, ask, visualize, quit")
        print("="*60)
        
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "search":
                query = input("Search query: ")
                nodes, edges = self.search(query)
                for node in nodes[:5]:
                    print(f"  - {node.name}")
                for edge in edges[:5]:
                    print(f"  - {edge.source} -> {edge.target}")
            elif cmd == "ask":
                question = input("Question: ")
                answer = self.ask(question)
                print(f"\n{answer}")
            elif cmd == "visualize":
                self.visualize()

if __name__ == "__main__":
    app = ResearchAssistantApp("paper.md")
    app.run()
```

---

## Summary

Congratulations! You've built a complete research assistant that can:

✓ Extract knowledge from research papers  
✓ Search using semantic queries  
✓ Answer questions in natural language  
✓ Visualize concept relationships  

### Next Steps

- Try with different papers
- Experiment with different templates
- Build a web interface using Streamlit or Flask
- Process multiple papers and compare them

---

## See Also

- [Knowledge Abstract Tutorial](../knowledge-base/index.md)
- [Document Analysis Tutorial](../document-analysis/index.md)
