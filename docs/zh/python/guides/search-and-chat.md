# 搜索和聊天

!!! tip "进阶 - 提取后操作"
    本指南涵盖使用提取后的知识。您应该先熟悉 [Level 1: 使用模板](using-templates.md)。

使用语义搜索和对话 AI 查询您的知识库。

---

## 概述

提取知识后，您可以通过两种方式与其交互：

- **搜索** — 查找特定的实体和关系
- **聊天** — 进行自然语言对话

两者都需要首先构建**搜索索引**。

---

## 构建索引

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "zh")
result = ka.parse(text)

# 构建搜索索引
result.build_index()
```

**注意：** 搜索/聊天操作之前需要构建索引。

---

## 语义搜索

### 基本搜索

```python
# 搜索相关项目（返回节点和边的元组）
nodes, edges = result.search("代表作", top_k=5)

for node in nodes:
    print(f"节点: {node.name}")
for edge in edges:
    print(f"边: {edge.source} -> {edge.target}")
```

### 搜索参数

```python
nodes, edges = result.search(
    query="苏轼文学成就",
    top_k=10  # 节点和边的结果数量
)
```

### 处理结果

```python
nodes, edges = result.search("代表作")

# 处理节点
for node in nodes:
    print(f"节点: {node.name} ({node.type})")

# 处理边
for edge in edges:
    print(f"边: {edge.source} -> {edge.target}")
```

### 搜索用例

```python
# 查找特定人物
people_nodes, people_edges = result.search("与苏轼相关的人物", top_k=10)

# 查找概念
concept_nodes, concept_edges = result.search("豪放词", top_k=5)

# 查找事件
event_nodes, event_edges = result.search("苏轼生平重要年份", top_k=10)
```

---

## 聊天接口

### 单个问题

```python
# 提问
response = result.chat("苏轼的主要成就是什么？")

print(response.content)
```

### 访问检索到的上下文

```python
response = result.chat("苏轼创作了哪些作品？")

print(response.content)

# 访问用于生成响应的节点和边
retrieved_nodes = response.additional_kwargs.get("retrieved_nodes", [])
retrieved_edges = response.additional_kwargs.get("retrieved_edges", [])
print(f"基于 {len(retrieved_nodes)} 个节点和 {len(retrieved_edges)} 条边")
```

### 聊天参数

```python
response = result.chat(
    query="解释乌台诗案",
    top_k=10  # 复杂问题需要更多上下文
)
```

### 聊天用例

```python
# 摘要
summary = result.chat("用三句话总结苏轼的生平")

# 解释
explanation = result.chat("《赤壁赋》的意义是什么？")

# 比较
comparison = result.chat("苏轼与王安石的政见有何不同？")

# 时间线
timeline = result.chat("苏轼在 1080-1090 年间发生了什么？")
```

---

## 搜索 vs 聊天

| 功能 | 搜索 | 聊天 |
|---------|--------|------|
| **返回** | 原始实体/关系 | 自然语言答案 |
| **速度** | 快 | 较慢（LLM 调用） |
| **用于** | 查找特定数据 | 理解/解释 |
| **精度** | 精确匹配 | 解释性 |
| **输出** | 结构化 | 自由文本 |

### 何时使用

**使用搜索当：**
- 您需要特定实体
- 构建报告或摘要
- 导出数据
- 需要快速查找

**使用聊天当：**
- 解释概念
- 回答复杂问题
- 摘要内容
- 交互式探索

---

## 高级模式

### 先搜索后聊天

```python
# 首先，搜索特定节点
nodes, edges = result.search("东坡赤壁", top_k=5)

# 然后，询问它们
if nodes:
    context = ", ".join([node.name for node in nodes])
    response = result.chat(f"解释 {context} 的意义")
    print(response.content)
```

### 迭代探索

```python
# 从广泛开始
response = result.chat("本文档中的主要主题是什么？")
print(response.content)

# 深入了解
response = result.chat("更多关于赤壁赋的信息")
print(response.content)

# 特定问题
response = result.chat("赤壁赋的创作背景是什么？")
print(response.content)
```

### 构建研究助手

```python
class ResearchAssistant:
    def __init__(self, ka_path):
        self.ka = Template.create("general/concept_graph", "zh")
        self.ka.load(ka_path)
        self.ka.build_index()
    
    def ask(self, question):
        response = self.ka.chat(question)
        return response.content
    
    def find(self, query, n=5):
        return self.ka.search(query, top_k=n)
    
    def summarize(self):
        return self.ask("总结本文的主要观点")

# 用法
assistant = ResearchAssistant("./paper_kb/")
print(assistant.summarize())
print(assistant.ask("有哪些局限性？"))
```

---

## 最佳实践

### 搜索技巧

1. **使用自然语言** — "文学成就"而非"文学"
2. **要具体** — "苏轼的作品"而非"苏轼"
3. **广泛查询时增加 top_k** — `top_k=10` 或更多
4. **按类型筛选结果** — 检查 `hasattr(item, 'name')`

### 聊天技巧

1. **提出清晰的问题** — 具体问题得到更好的答案
2. **使用上下文** — 逐步构建理解
3. **调整 top_k** — 复杂问题需要更多上下文
4. **检查来源** — 审查 `retrieved_nodes` 和 `retrieved_edges` 以确保准确性

---

## 故障排除

### "索引未构建"

```python
# 错误：需要先构建索引
result.build_index()
```

### "未找到结果"

```python
# 尝试不同的措辞
results = result.search("发明")  # 尝试同义词
results = result.search("发现")
results = result.search("贡献")

# 增加 top_k
results = result.search("苏轼", top_k=20)
```

### "无关的聊天响应"

```python
# 增加上下文
response = result.chat(question, top_k=10)

# 或重新表述问题
response = result.chat("请更具体地说明：...")
```

---

## 另请参见

**相关工作流：**
- [增量更新](incremental-updates.md) — 添加更多内容
- [保存和加载](saving-loading.md) — 持久化以供后续使用

**基础知识：**
- [使用模板](using-templates.md) — Level 1 基础
- [使用自动类型](working-with-autotypes.md) — Level 2 自定义
