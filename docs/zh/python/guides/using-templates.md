# 使用模板

!!! tip "Level 1 入门"
    本指南适合初学者。阅读本指南前，请先完成 [快速入门](../quickstart.md)。

学习如何使用和自定义模板进行知识提取。

---

## 什么是模板？

模板是预配置的提取设置，组合了：

- **自动类型** — 输出数据结构
- **提示** — LLM 指令
- **Schema** — 字段定义和类型
- **指南** — 提取规则和约束

---

## 内置模板

Hyper-Knowledge 包含 80+ 个跨 6 个领域的模板：

| 领域 | 模板 | 用例 |
|--------|-----------|-----------|
| `general` | 基础类型、传记、概念图谱 | 常见提取任务 |
| `finance` | 财报、风险、所有权、时间线 | 财务分析 |
| `legal` | 合同、案件、合规 | 法律文档处理 |
| `medicine` | 解剖、药物、治疗 | 医学文本分析 |
| `tcm` | 草药、方剂、证候 | 中医 |
| `industry` | 设备、安全、操作 | 工业文档 |

---

## 创建模板

### 从预设创建

```python
from hyperknowledge import Template

# 基本用法
ka = Template.create("general/biography_graph", language="zh")

# 使用自定义客户端
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o")
emb = OpenAIEmbeddings()

ka = Template.create(
    "general/biography_graph",
    language="zh",
    llm_client=llm,
    embedder=emb
)
```

### 从文件创建

```python
# 加载自定义 YAML 模板
ka = Template.create(
    "/path/to/my_template.yaml",
    language="zh"
)
```

### 从方法创建

```python
# 使用提取方法而非模板
ka = Template.create("method/light_rag")
```

---

## 列出模板

### 所有模板

```python
from hyperknowledge import Template

templates = Template.list()

for path, cfg in templates.items():
    print(f"{path}: {cfg.description}")
```

### 筛选列表

```python
# 按类型
graphs = Template.list(filter_by_type="graph")

# 按标签
biography = Template.list(filter_by_tag="biography")

# 按语言
zh_templates = Template.list(filter_by_language="zh")

# 组合
results = Template.list(
    filter_by_type="graph",
    filter_by_language="zh"
)
```

### 搜索模板

```python
# 在名称和描述中搜索
results = Template.list(filter_by_query="financial")
```

---

## 模板配置

### 获取模板信息

```python
from hyperknowledge import Template

# 获取模板配置
cfg = Template.get("general/biography_graph")

print(cfg.name)        # biography_graph
print(cfg.type)        # temporal_graph
print(cfg.description) # 模板描述
```

### 模板属性

```python
cfg = Template.get("general/biography_graph")

# 属性
print(cfg.name)           # 模板名称
print(cfg.type)           # 自动类型（graph、list 等）
print(cfg.description)    # 人类可读描述
print(cfg.tags)           # 关联标签
print(cfg.language)       # 支持的语言
```

---

## 理解模板返回值

`Template.create` 返回的是**自动类型（AutoType）**对象。不同模板对应的 AutoType 不同，访问提取结果的方式也不同：

| 类型 | AutoType | 典型访问方式 | 适用场景 |
|------|----------|--------------|----------|
| **模型** | `AutoModel` | `result.data.field_name` | 财报、档案等结构化对象 |
| **列表** | `AutoList` | `result.data.items` | 有序集合、流程步骤 |
| **集合** | `AutoSet` | `result.data.items` | 去重标签、关键词 |
| **图谱** | `AutoGraph` | `result.nodes` / `result.edges` | 二元实体关系 |
| **超图** | `AutoHypergraph` | `result.nodes` / `result.edges` | 多实体关系 |
| **时序图** | `AutoTemporalGraph` | `result.nodes` / `result.edges`（边含 `time`） | 时间线、传记 |
| **空间图** | `AutoSpatialGraph` | `result.nodes` / `result.edges`（含 `location`） | 地理网络 |
| **时空图** | `AutoSpatioTemporalGraph` | `result.nodes` / `result.edges`（含 `time` + `location`） | 历史事件 |

!!! info "相关文档"
    - 想了解更多每种 AutoType 的设计理念和适用场景？参见 [自动类型概念](../../concepts/autotypes.md)。
    - 想学习如何自定义 schema 和配置参数？参见 [使用自动类型](working-with-autotypes.md)。

### 快速示例

#### 模型（AutoModel）

```python
ka = Template.create("finance/earnings_summary", "zh")
result = ka.parse(report_text)

print(result.data.company_name)
print(result.data.revenue)
```

#### 列表（AutoList）

```python
ka = Template.create("general/list", "zh")
result = ka.parse(text)

for item in result.data.items:
    print(item)
```

#### 集合（AutoSet）

```python
ka = Template.create("general/set", "zh")
result = ka.parse(text)

for item in result.data.items:
    print(item)  # 自动去重
```

#### 图谱（AutoGraph）

```python
ka = Template.create("general/graph", "zh")
result = ka.parse(text)

for node in result.nodes:
    print(f"{node.name} ({node.type})")

for edge in result.edges:
    print(f"{edge.source} --{edge.type}--> {edge.target}")
```

---

## 常见模板模式

### 模式 1：传记分析

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "zh")

with open("biography.md") as f:
    result = ka.parse(f.read())

# 访问时间线数据
for edge in result.edges:
    if hasattr(edge, 'time'):
        print(f"{edge.time}: {edge.source} -> {edge.target}")

# 构建索引以支持交互式可视化
result.build_index()

result.show()  # 可视化生平时间线（支持搜索/对话功能）
```

![交互式可视化](../../../assets/zh_show.jpg)

### 模式 2：财务报告

```python
from hyperknowledge import Template

ka = Template.create("finance/earnings_summary", "zh")

report = ka.parse(earnings_text)

# 访问财务数据
print(f"收入: {report.data.revenue}")
print(f"每股收益: {report.data.eps}")
print(f"同比增长: {report.data.yoy_growth}%")
```

### 模式 3：法律合同

```python
from hyperknowledge import Template

ka = Template.create("legal/contract_obligation", "zh")

contract = ka.parse(contract_text)

# 列出义务
for obligation in contract.data.obligations:
    print(f"当事人: {obligation.party}")
    print(f"义务: {obligation.description}")
    print(f"截止日期: {obligation.deadline}")
```

### 模式 4：研究论文

```python
from hyperknowledge import Template

ka = Template.create("general/concept_graph", "zh")

paper = ka.parse(paper_text)

# 构建可搜索知识库
paper.build_index()

# 查询发现
response = paper.chat("主要贡献是什么？")
print(response.content)
```

---

## 多语言支持

模板支持英文和中文：

```python
# 英文文档
ka_en = Template.create("general/biography_graph", "en")
result_en = ka_en.parse(english_text)

# 中文文档
ka_zh = Template.create("general/biography_graph", "zh")
result_zh = ka_zh.parse(chinese_text)
```

**注意：** 使用与文档匹配的语言以获得最佳结果。

---

## 模板缓存

模板被加载和缓存以提高效率：

```python
# 首次调用加载模板
ka1 = Template.create("general/biography_graph", "zh")

# 第二次调用使用缓存版本
ka2 = Template.create("general/biography_graph", "zh")

# 两者是具有相同配置但独立的实例
```

---

## 错误处理

### 模板未找到

```python
from hyperknowledge import Template

try:
    ka = Template.create("nonexistent/template")
except ValueError as e:
    print(f"模板未找到: {e}")
    
    # 列出可用的
    available = Template.list()
    print("可用模板:", list(available.keys()))
```

### 不支持的语言

```python
cfg = Template.get("general/biography_graph")
print(cfg.language)  # 检查支持的语言

# 如果语言不支持将抛出错误
ka = Template.create("general/biography_graph", "fr")  # 可能失败
```

---

## 最佳实践

1. **选择特定领域的模板** — 比通用模板效果更好
2. **语言匹配文档** — 提高提取质量
3. **缓存模板实例** — 为多个文档重用
4. **检查模板输出 schema** — 了解期望的字段

---

## 另请参见

**下一步：**
- [使用自动类型](working-with-autotypes.md) — Level 2: 自定义 schema
- [创建自定义模板](custom-templates.md) — Level 2+: 编写自己的模板

**参考：**
- [模板库](../../templates/index.md) — 浏览所有模板
- [使用方法](using-methods.md) — 何时使用方法