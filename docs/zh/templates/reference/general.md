# 通用模板

基础类型和常见提取任务。

---

## 概述

通用模板为各种文档提供基本的提取功能。

---

## 基础类型

### base_model

**用途**：基础结构化数据提取

**输出**：单个结构化对象

**用于**：简单摘要、表单类数据

=== "CLI"

    ```bash
    hk parse doc.md -t general/model -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/model", "zh")
    result = ka.parse(doc_text)
    
    print(result.data)
    ```

**输出模式**：
```python
{
    "field1": "value1",
    "field2": "value2"
}
```

---

### base_list

**用途**：有序集合提取

**输出**：项目列表

**用于**：序列、排名

=== "CLI"

    ```bash
    hk parse doc.md -t general/list -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/list", "zh")
    result = ka.parse(doc_text)
    
    for item in result.data.items:
        print(f"- {item}")
    ```

**输出模式**：
```python
{
    "items": ["item1", "item2", "item3"]
}
```

---

### base_set

**用途**：唯一集合提取

**输出**：唯一项目集合

**用于**：标签、类别、关键词

=== "CLI"

    ```bash
    hk parse doc.md -t general/set -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/set", "zh")
    result = ka.parse(doc_text)
    
    for item in result.data.items:
        print(f"- {item}")
    ```

**输出模式**：
```python
{
    "items": {"unique1", "unique2", "unique3"}
}
```

---

### base_graph

**用途**：基础实体关系提取

**输出**：包含实体和关系的图谱

**用于**：知识图谱、网络

=== "CLI"

    ```bash
    hk parse doc.md -t general/graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/graph", "zh")
    result = ka.parse(doc_text)
    
    print(f"实体: {len(result.nodes)}")
    print(f"关系: {len(result.edges)}")
    ```

**输出模式**：
```python
{
    "entities": [
        {"name": "Entity1", "type": "type1"},
        {"name": "Entity2", "type": "type2"}
    ],
    "relations": [
        {"source": "Entity1", "target": "Entity2", "type": "relates_to"}
    ]
}
```

---

## 专业模板

### biography_graph

**类型**：temporal_graph

**用途**：提取人物生平事件和时间线

**最适合**：传记、简介、回忆录

=== "CLI"

    ```bash
    hk parse sushi.md -t general/biography_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/biography_graph", "zh")
    result = ka.parse(biography_text)
    
    # 构建索引以支持交互功能
    result.build_index()
    
    # 可视化生平事件（支持搜索/对话功能）
    result.show()
    
    # 提问
    response = result.chat("主要成就是什么？")
    print(response.content)
    ```

**特性**：
- 提取人物、地点、事件
- 捕获时间关系
- 时间线可视化

**示例输出**：
```python
{
    "entities": [
        {"name": "苏轼", "type": "人物"},
        {"name": "《念奴娇·赤壁怀古》", "type": "作品"}
    ],
    "relations": [
        {
            "source": "苏轼",
            "target": "《念奴娇·赤壁怀古》",
            "type": "创作",
            "time": "1082"
        }
    ]
}
```

---

### concept_graph

**类型**：graph

**用途**：提取概念及其关系

**最适合**：研究论文、技术文档、文章

=== "CLI"

    ```bash
    hk parse paper.md -t general/concept_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/concept_graph", "zh")
    result = ka.parse(paper_text)
    
    # 获取概念图
    for node in result.nodes:
        print(f"概念: {node.name}")
    
    for edge in result.edges:
        print(f"{edge.source} → {edge.target}")
    ```

**特性**：
- 概念识别
- 关系映射
- 层次结构

---

### doc_structure

**类型**：model

**用途**：提取文档结构和大纲

**最适合**：长文档、报告、书籍

=== "CLI"

    ```bash
    hk parse report.md -t general/doc_structure -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/doc_structure", "zh")
    result = ka.parse(report_text)
    
    print(f"标题: {result.data.title}")
    print(f"章节: {len(result.data.sections)}")
    
    for section in result.data.sections:
        print(f"- {section.heading}")
    ```

**特性**：
- 章节识别
- 标题层次
- 每节要点

---

### workflow_graph

**类型**：graph

**用途**：提取流程工作流

**最适合**：程序、流程、工作流

=== "CLI"

    ```bash
    hk parse procedure.md -t general/workflow_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("general/workflow_graph", "zh")
    result = ka.parse(procedure_text)
    
    # 构建索引用于可视化
    result.build_index()
    
    # 可视化工作流
    result.show()
    
    # 查询工作流
    response = result.chat("第一步是什么？")
    print(response.content)
    ```

**特性**：
- 步骤识别
- 流程关系
- 决策点

---

## 何时使用通用模板

### 何时使用：
- 文档不属于特定领域
- 需要基础提取
- 探索/文档类型未知
- 构建自定义工作流

### 何时不使用：
- 有领域特定模板可用（改用那个）
- 需要专业字段（创建自定义模板）

---

## 示例

### 示例 1：简单摘要

```python
from hyperknowledge import Template

ka = Template.create("general/model", "zh")
result = ka.parse("""
会议记录：
日期：2024年1月15日
参会：Alice, Bob, Carol
主题：Q1 规划
决定：3月发布产品
""")

print(result.data)
```

### 示例 2：传记分析

```python
ka = Template.create("general/biography_graph", "zh")
result = ka.parse(biography_text)

# 构建索引以支持交互功能
result.build_index()

# 可视化生平事件（支持搜索/对话功能）
result.show()

# 提问
response = result.chat("主要成就是什么？")
print(response.content)
```

### 示例 3：研究论文

```python
ka = Template.create("general/concept_graph", "zh")
result = ka.parse(paper_text)

# 获取概念图
for node in result.nodes:
    print(f"概念: {node.name}")

for edge in result.edges:
    print(f"{edge.source} → {edge.target}")
```

---

## 参见

- [模板概览](overview.md)
- [如何选择](../how-to-choose.md)
- [自动类型](../../concepts/autotypes.md)
