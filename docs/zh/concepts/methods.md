# 方法

提取算法指南以及何时使用每种方法。

---

## 概述

方法是底层算法，从文本中提取知识。它们决定：
- 如何处理文本
- 如何识别实体和关系
- 提取的质量和风格

---

## 方法类别

### 典型方法

**直接提取**，无需检索。

**最适合**：较小的文档、直接提取

```mermaid
graph LR
    A[Document] --> B[LLM Processing]
    B --> C[Extract Structure]
```

### 基于 RAG 的方法

**检索增强生成** 将信息检索与文本生成相结合。

**最适合**：大型文档、复杂查询

```mermaid
graph LR
    A[Document] --> B[Chunk & Index]
    B --> C[Retrieve Relevant]
    C --> D[Generate Answer]
    D --> E[Extract Structure]
```

---

## 典型方法

### itext2kg

**描述**：高质量基于三元组的提取

**特点**：
- 针对三元组质量优化
- 迭代精炼
- 适合知识库构建

**最适合**：
- 知识图谱构建
- 高质量要求
- 三元组提取

**用法**：
```python
ka = Template.create("method/itext2kg")
```

---

### itext2kg_star

**描述**：增强版 iText2KG

**特点**：
- 提高提取质量
- 更好地处理复杂情况
- 增强的实体链接

**最适合**：
- 质量至关重要时
- 复杂提取场景
- 生产系统

**用法**：
```python
ka = Template.create("method/itext2kg_star")
```

---

### kg_gen

**描述**：知识图谱生成器

**特点**：
- 可配置的生成
- 灵活的 schema
- 快速处理

**最适合**：
- 自定义 schema
- 快速原型
- 灵活需求

**用法**：
```python
ka = Template.create("method/kg_gen")
```

---

### atom

**描述**：带证据的时序知识图谱

**特点**：
- 时序事实提取
- 证据归属
- 置信度评分

**最适合**：
- 时序分析
- 事实验证
- 时间线提取

**用法**：
```python
ka = Template.create("method/atom")
```

---

## 基于 RAG 的方法

### light_rag

**描述**：轻量级基于图谱的 RAG

**特点**：
- 最快的 RAG 方法
- 二元边（source → target）
- 速度/质量的良好平衡
- 适合大多数用例

**最适合**：
- 通用提取
- 中大型文档
- 快速结果

**用法**：
```python
ka = Template.create("method/light_rag")
```

---

### graph_rag

**描述**：带社区检测的 Graph-RAG

**特点**：
- 社区检测用于组织
- 层次化摘要
- 最适合非常大的文档
- 较慢但彻底

**最适合**：
- 非常大的文档（书籍、长论文）
- 复杂主题结构
- 研究论文

**用法**：
```python
ka = Template.create("method/graph_rag")
```

---

### hyper_rag

**描述**：基于超图谱的 RAG

**特点**：
- N 元超边（2+ 个实体）
- 捕获复杂关系
- 更丰富的图谱结构

**最适合**：
- 多方关系
- 项目协作
- 复杂组织结构

**用法**：
```python
ka = Template.create("method/hyper_rag")
```

---

### hypergraph_rag

**描述**：高级超图谱 RAG

**特点**：
- 增强的超图谱能力
- 高级关系建模

**最适合**：
- 复杂超图谱场景
- 高级关系分析

**用法**：
```python
ka = Template.create("method/hypergraph_rag")
```

---

### cog_rag

**描述**：认知 RAG

**特点**：
- 认知检索机制
- 以推理为中心

**最适合**：
- 推理任务
- 问答系统

**用法**：
```python
ka = Template.create("method/cog_rag")
```

---

## 选择指南

### 按文档大小

| 大小 | 推荐 |
|------|-------------|
| 小型（< 1K 词） | itext2kg, kg_gen |
| 中型（1-10K） | light_rag, itext2kg_star |
| 大型（10-50K） | light_rag, graph_rag |
| 非常大（> 50K） | graph_rag |

### 按用例

| 用例 | 推荐 |
|----------|-------------|
| 快速提取 | light_rag |
| 最佳质量 | itext2kg_star |
| 大型文档 | graph_rag |
| 复杂关系 | hyper_rag |
| 时序事实 | atom |
| 知识库 | itext2kg |

### 按优先级

| 优先级 | 推荐 |
|----------|-------------|
| 速度 | light_rag |
| 质量 | itext2kg_star |
| 成本 | light_rag |
| 完整性 | graph_rag |

---

## 比较表

| 方法 | 速度 | 质量 | 内存 | 最佳用途 |
|--------|-------|---------|--------|----------|
| itext2kg | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | 质量优先 |
| itext2kg_star | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | 生产质量 |
| kg_gen | ⭐⭐⭐ | ⭐⭐ | ⭐ | 灵活性 |
| atom | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 时序数据 |
| light_rag | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 通用 |
| graph_rag | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 大型文档 |
| hyper_rag | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 复杂关系 |

---

## 列出可用方法

```python
from hyperknowledge.methods import list_methods

methods = list_methods()
for name, info in methods.items():
    print(f"{name}: {info['description']}")
    print(f"  Type: {info['type']}")
```

---

## 另请参见

- [使用方法指南](../python/guides/using-methods.md)
- [模板](../templates/index.md)
- [自动类型](autotypes.md)
