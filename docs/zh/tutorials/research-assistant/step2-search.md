# 步骤 2：语义搜索

构建可搜索的知识库。

---

## 目标

在提取的知识上启用语义搜索，以找到相关概念和章节。

---

## 为什么使用语义搜索？

与关键词搜索不同，语义搜索：
- 理解上下文和含义
- 即使使用不同词汇也能找到相关内容
- 处理同义词和相关概念

---

## 使用 CLI

### 基本搜索

```bash
hk search ./paper_kb/ "注意力机制"
```

### 自然语言查询

```bash
hk search ./paper_kb/ "主要贡献是什么？"
```

### 获取更多结果

```bash
hk search ./paper_kb/ "Transformer 架构" -n 10
```

---

## 使用 Python

### 脚本

```python
"""步骤 2：知识库语义搜索。"""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template

KB_DIR = "./paper_kb/"

def main():
    # 加载知识库
    print("加载知识库...")
    ka = Template.create("general/concept_graph", language="zh")
    ka.load(KB_DIR)
    
    # 确保索引已构建
    print("构建搜索索引...")
    ka.build_index()
    
    # 交互式搜索循环
    print("\n" + "="*50)
    print("语义搜索界面")
    print("="*50)
    print("输入查询（或 'quit' 退出）\n")
    
    while True:
        query = input("搜索: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        # 搜索
        results = ka.search(query, top_k=5)
        
        # 显示结果
        print(f"\n找到 {len(results)} 个结果:\n")
        
        for i, item in enumerate(results, 1):
            if hasattr(item, 'name'):  # 实体
                print(f"{i}. [{item.type}] {item.name}")
                if hasattr(item, 'description'):
                    print(f"   {item.description[:100]}...")
            elif hasattr(item, 'source'):  # 关系
                print(f"{i}. {item.source} --{item.type}--> {item.target}")
            print()
        
        print("-" * 50)
    
    print("\n✓ 步骤 2 完成!")
    print("下一步: 运行 'python step3_chat.py'")

if __name__ == "__main__":
    main()
```

### 运行

```bash
python step2_search.py
```

**示例会话：**
```
搜索: transformer architecture

找到 3 个结果:

1. [model] Transformer
   基于注意力机制的神经网络架构...

2. [concept] Self-Attention
   允许模型权衡输入 token 的机制...

3. [concept] Multi-Head Attention
   并行运行的多个注意力头...

--------------------------------------------------
搜索: quit
```

---

## 搜索技巧

### 有效查询

| 查询类型 | 示例 | 使用时机 |
|----------|------|---------|
| 概念 | "注意力机制" | 查找特定概念 |
| 问题 | "主要贡献是什么？" | 广泛探索 |
| 比较 | "Transformer 与 RNN 的比较" | 查找比较 |
| 结果 | "BLEU 分数结果" | 查找特定数据 |

### 改进结果

1. **具体化**: "Transformer 编码器" vs "Transformer"
2. **使用自然语言**: "注意力机制如何工作？"
3. **尝试同义词**: "注意力" → "自注意力" → "查询-键-值"
4. **增加 top_k**: `top_k=10` 以获得更广泛的结果

---

## 将搜索集成到您的应用

```python
class ResearchSearch:
    def __init__(self, ka_path):
        self.ka = Template.create("general/concept_graph", "zh")
        self.ka.load(ka_path)
        self.ka.build_index()
    
    def find_concepts(self, query, n=5):
        """查找与查询相关的概念。"""
        results = self.ka.search(query, top_k=n)
        return [r for r in results if hasattr(r, 'name')]
    
    def find_relationships(self, concept):
        """查找概念的关系。"""
        return [
            r for r in self.ka.data.relations
            if r.source == concept or r.target == concept
        ]

# 使用
search = ResearchSearch("./paper_kb/")
concepts = search.find_concepts("注意力", n=10)
```

---

## 下一步

→ [步骤 3：问答系统](step3-chat.md)
