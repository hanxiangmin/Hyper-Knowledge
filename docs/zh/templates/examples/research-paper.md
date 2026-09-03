# 研究论文分析

从研究论文中提取知识的完整指南。

---

## 场景

您有一篇研究论文，想要：
- 提取关键概念及其定义
- 映射概念之间的关系
- 构建可查询的知识库
- 可视化概念网络

---

## 推荐模板

### `general/concept_graph`

最适合从学术论文中提取概念、方法及其关系。

**为什么选这个模板？**
- 自动识别关键概念
- 映射 "is-a"、"uses"、"relates-to" 关系
- 支持层次结构
- 针对学术语言优化

---

## 完整工作流

### 第 1 步：提取知识

=== "CLI"

    ```bash
    hk parse paper.md -t general/concept_graph -l zh -o ./paper_kb/
    ```

=== "Python"

    ```python
    from hyperknowledge import Template

    # 加载论文
    with open("paper.md", "r") as f:
        paper_text = f.read()

    # 创建模板
    ka = Template.create("general/concept_graph", "zh")

    # 提取
    result = ka.parse(paper_text)

    print(f"提取了 {len(result.nodes)} 个概念")
    print(f"提取了 {len(result.edges)} 个关系")
    ```

**示例输出：**
```python
{
    "entities": [
        {"name": "Transformer", "type": "模型"},
        {"name": "注意力机制", "type": "概念"},
        {"name": "BLEU 分数", "type": "指标"}
    ],
    "relations": [
        {"source": "Transformer", "target": "注意力机制", "type": "使用"},
        {"source": "Transformer", "target": "BLEU 分数", "type": "达成"}
    ]
}
```

---

### 第 2 步：探索结果

> **注意：** 以下步骤假设您在第 1 步使用了 Python 方式。如果使用了 CLI，请使用 `ka.load("./paper_kb/")` 加载结果。

```python
# 列出所有概念
print("\n发现的概念：")
for node in result.nodes:
    print(f"  - {node.name} ({node.type})")
    if hasattr(node, 'description'):
        print(f"    {node.description[:100]}...")

# 列出关系
print("\n关系：")
for edge in result.edges:
    print(f"  - {edge.source} → {edge.target}: {edge.type}")
```

**示例输出：**
```
发现的概念：
  - Transformer (架构)
    基于自注意力机制的神经网络架构...
  - 注意力机制 (方法)
    允许模型关注输入相关部分的技术...
  - BERT (模型)
    双向编码器表示...

关系：
  - BERT → Transformer: 实现
  - Transformer → 注意力机制: 使用
  - BERT → NLP: 应用于
```

---

### 第 3 步：构建可搜索索引

```python
# 为搜索和对话构建索引
result.build_index()

# 保存供以后使用
result.dump("./paper_kb/")
```

---

### 第 4 步：可视化

```python
# 打开交互式可视化
result.show()
```

这将打开交互式浏览器视图，您可以在其中：
- 可视化探索概念图
- 搜索特定概念
- 询问论文相关问题

---

### 第 5 步：查询

```python
# 语义搜索
nodes, edges = result.search("注意力机制", top_k=5)

print("相关概念：")
for node in nodes:
    print(f"  - {node.name}")

# 对话界面
response = result.chat("这篇论文的主要贡献是什么？")
print(response.content)

response = result.chat("提出的方法与之前的方法相比如何？")
print(response.content)
```

---

## 替代模板

### 文档结构 {#document-structure}

如果您需要论文的大纲和结构：

=== "CLI"

    ```bash
    hk parse paper.md -t general/doc_structure -l zh -o ./structure/
    ```

**提取内容：**
- 章节标题
- 每节要点
- 论文组织

### 知识图谱 {#knowledge-graph}

用于超越单纯概念的更广泛领域知识：

=== "CLI"

    ```bash
    hk parse paper.md -t general/graph -l zh -o ./knowledge/
    ```

**与 concept_graph 的区别：**
- 更广泛的实体类型（人物、组织、方法）
- 一般关系
- 较少关注概念定义

### 工作流图谱

如果论文描述了一个过程或算法：

=== "CLI"

    ```bash
    hk parse paper.md -t general/workflow_graph -l zh -o ./workflow/
    ```

**提取内容：**
- 过程步骤
- 决策点
- 流程关系

---

## 对比表

| 模板 | 最佳场景 | 输出 |
|------|---------|------|
| `concept_graph` | 有概念/定义的研究论文 | 概念网络 |
| `graph` | 更广泛的领域知识 | 通用实体网络 |
| `doc_structure` | 文档大纲 | 层次结构 |
| `workflow_graph` | 过程/方法描述 | 流程图 |

---

## 最佳实践技巧

### 1. 文档准备

- 移除页眉/页脚
- 确保干净的 Markdown 或纯文本
- 保持方程式为 LaTeX 或纯文本

### 2. 语言选择

=== "CLI"

    ```bash
    # 中文论文
    hk parse paper.md -t general/concept_graph -l zh

    # 英文论文
    hk parse paper.md -t general/concept_graph -l en
    ```

### 3. 处理长论文

对于超过 5000 词的论文：

```python
# 选项 1：使用 RAG 方法
ka = Template.create("method/graph_rag")
result = ka.parse(paper_text)

# 选项 2：按章节处理
sections = split_paper_into_sections(paper_text)
ka = Template.create("general/concept_graph", "zh")
result = ka.parse(sections[0])

for section in sections[1:]:
    result.feed_text(section)
```

### 4. 后处理

```python
# 按概念类型筛选
concepts = [n for n in result.nodes if n.type == "概念"]
methods = [n for n in result.nodes if n.type == "方法"]

# 查找中心概念（连接最多的）
from collections import Counter
edge_counts = Counter([e.source for e in result.edges] + 
                      [e.target for e in result.edges])
top_concepts = edge_counts.most_common(5)
```

---

## 示例：完整分析脚本

```python
"""完整的研究论文分析工作流。"""

from hyperknowledge import Template
from pathlib import Path

def analyze_paper(paper_path, output_dir="./paper_analysis/"):
    """分析研究论文并创建知识库。"""
    
    # 加载论文
    text = Path(paper_path).read_text()
    
    # 提取概念
    print("提取概念中...")
    ka = Template.create("general/concept_graph", "zh")
    result = ka.parse(text)
    
    print(f"找到 {len(result.nodes)} 个概念")
    print(f"找到 {len(result.edges)} 个关系")
    
    # 构建索引
    print("构建搜索索引...")
    result.build_index()
    
    # 保存
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    result.dump(output_path)
    
    # 生成摘要
    print("\n=== 论文摘要 ===")
    response = result.chat("用三句话总结主要贡献")
    print(response.content)
    
    print("\n=== 关键概念 ===")
    for node in result.nodes[:5]:
        print(f"- {node.name}")
    
    print(f"\n保存到：{output_path}")
    print(f"\n要探索：result.show()")
    
    return result

# 用法
if __name__ == "__main__":
    result = analyze_paper("paper.md")
    
    # 交互式探索
    result.show()
```

---

## 另请参见

- [按任务选择](../choosing/by-task.md) — 其他任务模板
- [概念图谱模板](../reference/general.md) — 模板详情
- [Python 快速入门](../../python/quickstart.md) — Python SDK 入门
