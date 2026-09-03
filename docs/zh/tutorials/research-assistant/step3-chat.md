# 步骤 3：问答系统

创建交互式问答界面。

---

## 目标

构建一个对话界面，使用自然语言回答关于研究论文的问题。

---

## 工作原理

1. 用户提问
2. 系统从知识库检索相关上下文
3. 大语言模型基于检索到的上下文生成答案
4. 响应包含来自论文的引用

---

## 使用 CLI

### 单问题

```bash
hk talk ./paper_kb/ -q "这篇论文的主要贡献是什么？"
```

### 交互模式

```bash
hk talk ./paper_kb/ -i
```

**示例会话：**
```
进入交互模式。输入 'exit' 或 'quit' 停止。

> Transformer 架构是什么？

Transformer 是这篇论文提出的一种全新的神经网络架构，
完全依赖注意力机制，彻底摒弃了循环和卷积结构...

> 它与 RNN 相比有何优势？

与按顺序处理序列的 RNN 不同，Transformer 可以并行处理所有位置，
这使得它在大型数据集上的训练更加高效...

> exit
```

---

## 使用 Python

### 脚本

```python
"""步骤 3：交互式问答系统。"""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template

KB_DIR = "./paper_kb/"

class ResearchAssistant:
    def __init__(self, ka_path):
        print("加载研究助手...")
        self.ka = Template.create("general/concept_graph", "zh")
        self.ka.load(ka_path)
        self.ka.build_index()
        print("✓ 准备就绪!\n")
    
    def ask(self, question, top_k=5):
        """询问关于论文的问题。"""
        response = self.ka.chat(question, top_k=top_k)
        return response.content
    
    def interactive(self):
        """运行交互式问答会话。"""
        print("="*60)
        print("研究助手 - 向我询问关于论文的问题!")
        print("="*60)
        print("输入 'quit' 退出\n")
        
        while True:
            question = input("\nQ: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            print("\n思考中...")
            answer = self.ask(question)
            print(f"\nA: {answer}\n")
            print("-"*60)
        
        print("\n再见!")

def main():
    assistant = ResearchAssistant(KB_DIR)
    assistant.interactive()

if __name__ == "__main__":
    main()
```

### 运行

```bash
python step3_chat.py
```

---

## 示例问题

### 理解论文

- "这篇论文解决什么问题？"
- "主要贡献是什么？"
- "关键创新是什么？"

### 技术细节

- "解释注意力机制"
- "什么是多头注意力？"
- "位置编码如何处理？"

### 结果和评估

- "使用了哪些数据集？"
- "主要结果是什么？"
- "与基线方法相比如何？"

### 局限性和未来工作

- "局限性是什么？"
- "建议了哪些未来工作？"

---

## 高级功能

### 引用跟踪

```python
def ask_with_citations(assistant, question):
    """获取带来源引用的答案。"""
    response = assistant.ka.chat(question, top_k=5)
    
    print(f"答案: {response.content}\n")
    
    # 显示检索到的来源
    retrieved_nodes = response.additional_kwargs.get("retrieved_nodes", [])
    retrieved_edges = response.additional_kwargs.get("retrieved_edges", [])
    if retrieved_nodes or retrieved_edges:
        print("来源:")
        for node in retrieved_nodes:
            print(f"  - {node.name}")
        for edge in retrieved_edges:
            print(f"  - {edge.source} -> {edge.target}")
```

### 问题建议

```python
def suggest_questions(assistant):
    """基于论文内容建议问题。"""
    suggestions = [
        "这篇论文的主要贡献是什么？",
        "它解决了什么问题？",
        "关键结果有哪些？",
        "与之前的工作相比有何不同？",
    ]
    return suggestions
```

### 导出问答历史

```python
def export_history(questions_answers, filename="qa_history.json"):
    """导出问答会话到文件。"""
    import json
    with open(filename, 'w') as f:
        json.dump(questions_answers, f, indent=2)
```

---

## 完整应用

整合所有内容：

```python
"""完整研究助手应用。"""

from hyperknowledge import Template
from pathlib import Path

class ResearchAssistantApp:
    def __init__(self, paper_path, kb_dir="./paper_kb/"):
        self.paper_path = paper_path
        self.ka_dir = kb_dir
        self.ka = None
        
        # 加载或创建知识库
        if Path(kb_dir).exists():
            self._load_kb()
        else:
            self._create_kb()
    
    def _create_kb(self):
        """从论文创建知识库。"""
        print("创建知识库...")
        ka = Template.create("general/concept_graph", "zh")
        text = Path(self.paper_path).read_text()
        self.ka = ka.parse(text)
        self.ka.build_index()
        self.ka.dump(self.ka_dir)
        print("✓ 知识库已创建\n")
    
    def _load_kb(self):
        """加载现有知识库。"""
        print("加载知识库...")
        self.ka = Template.create("general/concept_graph", "zh")
        self.ka.load(self.ka_dir)
        print("✓ 知识库已加载\n")
    
    def search(self, query):
        """搜索论文。"""
        return self.ka.search(query)
    
    def ask(self, question):
        """提问。"""
        return self.ka.chat(question).content
    
    def visualize(self):
        """打开可视化。"""
        self.ka.show()

![交互式可视化](../../../../assets/zh_show.jpg)

    def run(self):
        """运行交互式会话。"""
        print("="*60)
        print("研究助手")
        print("命令: search, ask, visualize, quit")
        print("="*60)
        
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "search":
                query = input("搜索查询: ")
                nodes, edges = self.search(query)
                for node in nodes[:5]:
                    print(f"  - {node.name}")
                for edge in edges[:5]:
                    print(f"  - {edge.source} -> {edge.target}")
            elif cmd == "ask":
                question = input("问题: ")
                answer = self.ask(question)
                print(f"\n{answer}")
            elif cmd == "visualize":
                self.visualize()

if __name__ == "__main__":
    app = ResearchAssistantApp("paper.md")
    app.run()
```

---

## 总结

恭喜！您已构建了一个完整的研究助手，能够：

✓ 从研究论文中提取知识  
✓ 使用语义查询搜索  
✓ 用自然语言回答问题  
✓ 可视化概念关系  

### 下一步

- 尝试不同的论文
- 尝试不同的模板
- 使用 Streamlit 或 Flask 构建 Web 界面
- 处理多篇论文并进行比较

---

## 参见

- [知识库教程](../knowledge-base/index.md)
- [文档分析教程](../document-analysis/index.md)
