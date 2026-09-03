# 使用自动类型

!!! tip "Level 2 - 进阶"
    本指南涵盖配置化 Auto-Type 用法。在阅读前，请先完成 [Level 1: 使用模板](using-templates.md) 和 [Level 1: 使用方法](using-methods.md)。

学习如何直接配置自动类型，以自定义 schema、去重逻辑和提取行为。

---

## 什么是自动类型？

自动类型是 Hyper-Knowledge 的核心数据结构，负责从文本中提取、组织和存储结构化知识。它们提供：

- **类型安全的 schema** — 基于 Pydantic 的验证
- **LLM 驱动的提取** — 自动内容处理
- **内置操作** — 搜索、合并、可视化
- **序列化** — 保存/加载到磁盘

所有自动类型都继承自 `BaseAutoType`，因此共享一组通用能力（如 `parse`、`feed_text`、`build_index`、`search`、`chat`、`dump`、`load` 等）。

---

## 三层使用架构

Hyper-Knowledge 提供三个控制层级。本文档聚焦 **层级 2**。

| 层级 | 方式 | 何时使用 | 参考文档 |
|-------|----------|-------------|----------|
| **层级 1** | 模板 / 方法 | 快速开始、标准用例 | [使用模板](using-templates.md)、[使用方法](using-methods.md) |
| **层级 2** | 配置化自动类型 | 自定义 schema、保留预置提取逻辑 | **本文档** |
| **层级 3** | 完全自定义方法 | 完全控制提取过程 | [方法概念](../../concepts/methods.md) |

---

## 层级 2：配置化自动类型用法

当你需要自定义 schema，但不想从零实现提取逻辑时，可以直接实例化自动类型并传入配置参数。

### 何时使用层级 2

- 你需要自定义节点/边 schema
- 你想控制去重逻辑
- 模板输出不完全匹配你的需求
- 你在构建可复用的 Python 组件

### 完整示例：自定义图谱

```python
from hyperknowledge import AutoGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

# 步骤 1：定义自定义 schema
class Person(BaseModel):
    """自定义节点 schema"""
    name: str = Field(description="人员全名")
    role: str = Field(description="职位或角色")
    expertise: list[str] = Field(default=[], description="专业领域")

class Collaboration(BaseModel):
    """自定义边 schema"""
    source: str = Field(description="第一人姓名")
    target: str = Field(description="第二人姓名")
    project: str = Field(description="共同项目")
    year: int = Field(description="协作年份")

# 步骤 2：配置 LLM 客户端
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# 步骤 3：创建配置化的 AutoGraph
graph = AutoGraph[Person, Collaboration](
    node_schema=Person,
    edge_schema=Collaboration,
    # 定义如何提取唯一键用于去重
    node_key_extractor=lambda p: p.name,
    edge_key_extractor=lambda c: f"{c.source}-{c.target}-{c.project}",
    # 定义如何从边提取节点引用
    nodes_in_edge_extractor=lambda c: (c.source, c.target),
    # LLM 客户端
    llm_client=llm,
    embedder=embedder,
)

# 步骤 4：提取
text = """
陈博士和王博士在2023年合作了气候 AI 项目。
陈博士是机器学习研究员，专长于神经网络和气候建模。
王博士专攻数据工程和分布式系统。
"""

graph.feed_text(text)

# 步骤 5：访问结果
print(f"提取了 {len(graph.nodes)} 个人员")
for person in graph.nodes:
    print(f"- {person.name}: {person.role}")
    print(f"  专业: {', '.join(person.expertise)}")

print(f"\n提取了 {len(graph.edges)} 个协作关系")
for collab in graph.edges:
    print(f"- {collab.source} 和 {collab.target}: {collab.project} ({collab.year})")

# 步骤 6：使用内置功能
graph.build_index()

# 搜索
nodes, edges = graph.search("机器学习", top_k=2)
print(f"\n搜索找到: {len(nodes)} 个人员")

# 可视化
graph.show()
```

### 关键配置参数

| 参数 | 必需 | 描述 |
|-----------|----------|-------------|
| `node_schema` / `edge_schema` | 是 | 定义结构的 Pydantic 模型 |
| `node_key_extractor` | 是 | 从节点提取唯一键的函数 |
| `edge_key_extractor` | 是 | 从边提取唯一键的函数 |
| `nodes_in_edge_extractor` | 是 | 从边获取 (source, target) 的函数 |
| `llm_client` | 是 | LangChain 兼容的 LLM 客户端 |
| `embedder` | 是 | LangChain 兼容的嵌入客户端 |

### 对比：模板 vs 配置化自动类型

| 方面 | 模板 | 配置化自动类型 |
|--------|----------|---------------------|
| Schema 定义 | YAML 文件 | Python Pydantic 类 |
| 提取逻辑 | 预构建 | 相同预构建逻辑 |
| 去重 | 预配置 | 你定义键提取器 |
| 语言支持 | 内置 | 你提供提示 |
| 可复用性 | 分享 YAML 文件 | 打包为 Python 模块 |

### 更多配置示例

#### 时序图谱

```python
from hyperknowledge import AutoTemporalGraph
from pydantic import BaseModel, Field

class Event(BaseModel):
    """节点：历史事件"""
    name: str = Field(description="事件名称")
    category: str = Field(description="事件类型")

class CausalLink(BaseModel):
    """边：带时间的因果关系"""
    source: str = Field(description="早期事件")
    target: str = Field(description="后期事件")
    relationship: str = Field(description="连接方式")
    time: str = Field(description="连接发生时间")

timeline = AutoTemporalGraph[Event, CausalLink](
    node_schema=Event,
    edge_schema=CausalLink,
    node_key_extractor=lambda e: e.name,
    edge_key_extractor=lambda l: f"{l.source}-{l.target}-{l.time}",
    nodes_in_edge_extractor=lambda l: (l.source, l.target),
    llm_client=llm,
    embedder=embedder,
    # 时序特有：从边提取时间
    time_extractor=lambda l: l.time,
)

timeline.feed_text(historical_text)
```

---

## 常见操作

### 检查是否为空

```python
if result.empty():
    print("未提取到数据")
else:
    print(f"提取了 {len(result.nodes)} 个节点")
```

### 清除数据

```python
# 清除所有数据
result.clear()

# 仅清除索引
result.clear_index()
```

### 合并实例

```python
# 两次独立提取
result1 = ka.parse(text1)
result2 = ka.parse(text2)

# 合并到新实例
combined = result1 + result2
```

---

## 访问数据

### 属性访问

```python
result = ka.parse(text)

# 直接属性访问（Pydantic 模型）
nodes = result.nodes
edges = result.edges

# 字典转换
data_dict = result.data.model_dump()
```

### JSON 导出

```python
import json

# 导出为 JSON
json_data = result.data.model_dump_json(indent=2)

# 保存到文件
with open("output.json", "w") as f:
    f.write(json_data)
```

---

## 处理结果

### 迭代模式

```python
# 遍历节点
for node in result.nodes:
    print(f"名称: {node.name}")
    print(f"类型: {node.type}")
    if hasattr(node, 'description'):
        print(f"描述: {node.description}")

# 带筛选的边迭代
for edge in result.edges:
    if edge.type == "worked_with":
        print(f"{edge.source} 与 {edge.target} 合作")
```

### 筛选

```python
# 按类型筛选节点
people = [n for n in result.nodes if n.type == "person"]
organizations = [n for n in result.nodes if n.type == "organization"]

# 筛选边
inventions = [e for e in result.edges if "invent" in e.type.lower()]
```

### 统计

```python
# 基本计数
node_count = len(result.nodes)
edge_count = len(result.edges)

# 类型分布
from collections import Counter
node_types = Counter(n.type for n in result.nodes)
edge_types = Counter(e.type for e in result.edges)

print(f"节点: {node_types}")
print(f"边: {edge_types}")
```

---

## 高级用法 {#advanced-usage}

### 访问 Schema

```python
# 访问 schema
schema = result.data_schema

print(schema.model_fields)  # 可用字段
```

### 原始数据访问

```python
# 如需要访问内部数据
internal_data = result._data
```

### 类型检查

```python
from hyperknowledge import AutoGraph, AutoList

# 检查实例类型
if isinstance(result, AutoGraph):
    print("图谱提取")
elif isinstance(result, AutoList):
    print("列表提取")
```

---

## 最佳实践

### 层级 2（配置化自动类型）

1. **仔细设计 schema** — 字段成为 LLM 提取目标
2. **使用清晰的 Field 描述** — 帮助 LLM 理解期望
3. **选择好的键提取器** — 对去重至关重要
4. **用小样本测试** — 迭代 schema 设计

### 通用

1. **访问可选字段前检查 `hasattr`** — Schema 字段可能不同
2. **处理空结果** — 始终检查 `empty()`
3. **使用 `model_dump` 进行序列化** — 正确的 JSON 转换
4. **利用类型提示** — IDE 自动完成支持

---

## 另请参见

**前置知识：**
- [使用模板](using-templates.md) — Level 1 基础
- [使用方法](using-methods.md) — Level 1 基础
- [自动类型概念](../../concepts/autotypes.md) — 每种类型的作用

**下一步：**
- [创建自定义模板](custom-templates.md) — 打包你的配置
- [增量更新](incremental-updates.md) — 添加更多文档
- [搜索和聊天](search-and-chat.md) — 使用提取的知识
- [保存和加载](saving-loading.md) — 持久化结果
