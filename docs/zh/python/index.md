# Python SDK

使用 Hyper-Knowledge Python API 构建知识提取管道。

---

## 安装

```bash
pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

开发安装：

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd Hyper-Knowledge
uv sync --group dev
```

---

## 快速示例

```python
from hyperknowledge import Template

# 创建模板
ka = Template.create("general/biography_graph", language="zh")

# 提取知识
with open("document.md") as f:
    result = ka.parse(f.read())

# 访问数据
print(f"节点数: {len(result.nodes)}")
print(f"边数: {len(result.edges)}")

# 构建索引以支持搜索/对话功能
result.build_index()

# 可视化
result.show()
```

![交互式可视化](../../assets/zh_show.jpg)

---

## 核心类

### Template

模板化提取的主要入口点。

```python
from hyperknowledge import Template

# 从预设创建
ka = Template.create("general/biography_graph", language="zh")

# 从自定义 YAML 创建
ka = Template.create("/path/to/custom_template.yaml", language="zh")

# 从方法创建
ka = Template.create("method/light_rag")
```

### 自动类型

8 种用于不同提取需求的数据结构类型：

| 类 | 用例 |
|-------|----------|
| `AutoModel` | 结构化数据模型 |
| `AutoList` | 有序集合 |
| `AutoSet` | 去重集合 |
| `AutoGraph` | 实体关系图谱 |
| `AutoHypergraph` | 多实体关系 |
| `AutoTemporalGraph` | 基于时间的关系 |
| `AutoSpatialGraph` | 基于位置的关系 |
| `AutoSpatioTemporalGraph` | 时间 + 空间组合 |

---

## API 概览

### Template API

```python
# 创建
ka = Template.create(template_path, language="zh")

# 提取
result = ka.parse(text)           # 新提取
result.feed_text(text)            # 添加到现有

# 查询
result.build_index()              # 构建搜索索引
results = result.search(query)    # 语义搜索
response = result.chat(query)     # 与知识聊天

# 持久化
result.dump("./output/")          # 保存到磁盘
result.load("./output/")          # 从磁盘加载

# 可视化
result.show()                     # 交互式可视化
```

![交互式可视化](../../assets/zh_show.jpg)

---

## 文档结构

- **[快速入门](quickstart.md)** — 您的首次 Python 提取
- **[核心概念](core-concepts.md)** — 模板、自动类型、方法详解
- **指南：**
  - [使用模板](guides/using-templates.md)
  - [使用方法](guides/using-methods.md)
  - [使用自动类型](guides/working-with-autotypes.md)
  - [搜索和聊天](guides/search-and-chat.md)
  - [增量更新](guides/incremental-updates.md)
  - [保存和加载](guides/saving-loading.md)
- **API 参考：**
  - [模板](api-reference/template.md)
  - [自动类型](api-reference/autotypes/base.md)
  - [方法](api-reference/methods/registry.md)

---

## 用例示例

### 研究论文分析

```python
from hyperknowledge import Template

ka = Template.create("general/concept_graph", language="zh")

with open("paper.md") as f:
    paper = ka.parse(f.read())

# 构建可搜索知识库
paper.build_index()

# 提问
response = paper.chat("主要贡献是什么？")
print(response.content)
```

### 财务报告提取

```python
from hyperknowledge import Template

ka = Template.create("finance/earnings_summary", language="zh")

report = ka.parse(earnings_text)
print(report.data.revenue)
print(report.data.eps)
```

### 构建知识库

```python
from hyperknowledge import Template

ka = Template.create("general/graph", language="zh")

# 初始提取
ka = ka.parse(doc1_text)

# 添加更多文档
ka.feed_text(doc2_text)
ka.feed_text(doc3_text)

# 保存供以后使用
ka.dump("./my_ka/")
```

---

## 配置

### 环境变量

```python
import os

os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
```

### 使用 .env 文件

```python
from dotenv import load_dotenv
load_dotenv()  # 从 .env 文件加载
```

### 自定义客户端

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperknowledge import Template

llm = ChatOpenAI(model="gpt-4o")
embedder = OpenAIEmbeddings(model="text-embedding-3-large")

ka = Template.create(
    "general/biography_graph",
    language="zh",
    llm_client=llm,
    embedder=embedder
)
```

---

## 类型提示

Hyper-Knowledge 完全类型化，支持 IDE 自动完成：

```python
from hyperknowledge import Template, AutoGraph

ka: AutoGraph = Template.create("general/graph", "zh")
result = ka.parse(text)

# IDE 自动完成有效
nodes = result.nodes
edges = result.edges
```

---

## 下一步

- 遵循[快速入门](quickstart.md)
- 学习[核心概念](core-concepts.md)
- 浏览[指南](guides/using-templates.md)
- 阅读 [API 参考](api-reference/template.md)
