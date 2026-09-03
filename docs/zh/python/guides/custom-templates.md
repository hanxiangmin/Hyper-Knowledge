# 创建自定义模板

!!! tip "Level 2+ - 进阶拓展"
    本指南介绍如何创建可复用模板。在阅读前，请先完成 [Level 1: 使用模板](using-templates.md) 或 [Level 2: 使用自动类型](working-with-autotypes.md)。

学习如何为专业提取任务创建自己的模板。

---

## 概述

自定义模板允许您定义：

- **输出 schema** — 要提取的实体和关系
- **提取规则** — LLM 的指南
- **显示配置** — 如何可视化结果

---

## 快速开始

### 1. 创建模板文件

在 `~/.hyperknowledge/templates/` 中创建 YAML 文件：

```bash
mkdir -p ~/.hyperknowledge/templates/my_domain
```

### 2. 定义模板结构

```yaml
language: [zh, en]

name: my_template
type: graph
tags: [custom, domain]

description:
  zh: "自定义模板描述"
  en: "Custom template description"

output:
  description:
    zh: "输出描述"
    en: "Output description"
  entities:
    description:
      zh: "实体描述"
      en: "Entity description"
    fields:
      - name: name
        type: str
        description:
          zh: "名称"
          en: "Name"
        required: true
      - name: category
        type: str
        description:
          zh: "类别"
          en: "Category"
        required: true

  relations:
    description:
      zh: "关系描述"
      en: "Relation description"
    fields:
      - name: type
        type: str
        description:
          zh: "关系类型"
          en: "Relation type"
        required: true

guideline:
  target:
    zh: "提取目标描述"
    en: "Extraction target description"
  rules_for_entities:
    zh:
      - "规则1"
      - "规则2"
    en:
      - "Rule 1"
      - "Rule 2"
  rules_for_relations:
    zh:
      - "关系规则1"
    en:
      - "Relation rule 1"

identifiers:
  entity_id: name
  relation_id: "{source}|{type}|{target}"
  relation_members:
    source: source
    target: target

display:
  entity_label: "{name} ({category})"
  relation_label: "{type}"
```

### 3. 验证并使用

```python
from hyperknowledge import Template

# 加载自定义模板
ka = Template.create("my_domain/my_template", "zh")

# 使用
result = ka.parse("您的文档文本")
```

---

## 字段类型

| 类型 | 描述 | 示例 |
|------|-------------|---------|
| `str` | 字符串值 | `"Hello"` |
| `int` | 整数 | `42` |
| `float` | 浮点数 | `3.14` |
| `bool` | 布尔值 | `true` |
| `list[str]` | 字符串列表 | `["a", "b"]` |
| `datetime` | 日期/时间 | `"2024-01-01"` |
| `enum` | 枚举值 | 见下文 |

### 枚举类型

用于预定义值的字段：

```yaml
- name: priority
  type: str
  description:
    zh: "优先级: high/medium/low"
    en: "Priority: high/medium/low"
  required: true
```

---

## 自动类型

为您的数据选择合适的自动类型：

| 类型 | 用例 | 特性 |
|------|----------|----------|
| `graph` | 通用知识图谱 | 实体 + 关系 |
| `temporal_graph` | 时序数据 | + 时间事件 |
| `spatial_graph` | 地理空间数据 | + 位置坐标 |
| `hypergraph` | 复杂关系 | + 超边 |
| `tree` | 层次数据 | 父子结构 |
| `table` | 结构化记录 | 基于行的数据 |

---

## 最佳实践

### 1. 清晰的描述

编写详细描述以指导 LLM：

```yaml
# 好
description:
  zh: "提取产品信息，包括名称、价格和类别"

# 不好
description:
  zh: "产品信息"
```

### 2. 具体的规则

提供具体的提取规则：

```yaml
guideline:
  rules_for_entities:
    zh:
      - "仅提取定价部分中提到的产品"
      - "类别必须是以下之一：电子产品、服装、食品、其他"
      - "价格四舍五入到 2 位小数"
```

### 3. 必填字段

将关键字段标记为必填：

```yaml
fields:
  - name: id
    type: str
    required: true  # 如果缺失，提取将失败
  - name: notes
    type: str
    required: false  # 可选字段
```

### 4. 验证

使用样本文档测试模板：

```python
# 测试提取
test_doc = """
样本文档文本用于测试...
"""

result = ka.parse(test_doc)
print(result.data.entities)
print(result.data.relations)
```

---

## 示例：产品目录模板

```yaml
language: [zh, en]

name: product_catalog
type: table
tags: [ecommerce, products]

description:
  zh: "从商品目录中提取产品信息"
  en: "Extract product information from catalogs"

output:
  description:
    zh: "产品信息表"
    en: "Product information table"
  entities:
    description:
      zh: "产品实体"
      en: "Product entities"
    fields:
      - name: sku
        type: str
        description:
          zh: "产品SKU（唯一标识）"
          en: "Product SKU (unique identifier)"
        required: true
      - name: name
        type: str
        description:
          zh: "产品名称"
          en: "Product name"
        required: true
      - name: price
        type: float
        description:
          zh: "价格（数字）"
          en: "Price (numeric value)"
        required: true
      - name: category
        type: str
        description:
          zh: "类别：electronics/clothing/food/home/other"
          en: "Category: electronics/clothing/food/home/other"
        required: true
      - name: in_stock
        type: bool
        description:
          zh: "是否有库存"
          en: "Whether in stock"
        required: false

guideline:
  target:
    zh: "提取所有产品信息，忽略缺货商品"
    en: "Extract all product info, skip out-of-stock items"
  rules_for_entities:
    zh:
      - "从表格和项目列表中提取产品"
      - "将价格字符串转换为数值"
      - "将类别名称映射到标准值"
      - "如果明确提到缺货，则设置 in_stock=false"

identifiers:
  entity_id: sku

display:
  entity_label: "{name} (¥{price})"
```

---

## 直接使用方法类

如果你需要完全控制提取过程，可以直接使用方法类，而不通过 `Template.create`：

```python
from hyperknowledge.methods import Light_RAG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 直接创建方法实例
llm = ChatOpenAI()
emb = OpenAIEmbeddings()

method = Light_RAG(
    llm_client=llm,
    embedder=emb,
    # 方法特定参数
    chunk_size=1024,
    max_workers=5
)

# 提取知识
result = method.parse(text)
```

这种方式适合需要绕过模板层、直接调优算法参数的进阶场景。

---

## 注册自定义方法

您还可以注册自定义提取方法，并通过 Template API 使用它们：

```python
from hyperknowledge.methods import register_method

class MyCustomMethod:
    def __init__(self, llm_client, embedder, **kwargs):
        self.llm_client = llm_client
        self.embedder = embedder
    
    def parse(self, text):
        # 您的提取逻辑
        pass

# 注册方法
register_method(
    name="my_method",
    method_class=MyCustomMethod,
    autotype="graph",
    description="我的自定义提取方法"
)

# 通过 Template API 使用
from hyperknowledge import Template
ka = Template.create("method/my_method")
```

---

## 分享模板

### 全局注册

将模板放在系统目录中：

```bash
# 系统范围（所有用户）
/usr/share/hyperknowledge/templates/

# 用户特定
~/.hyperknowledge/templates/
```

### 模板仓库

与社区分享：

1. Fork [Hyper-Knowledge 仓库](https://github.com/hanxiangmin/Hyper-Knowledge)
2. 添加模板到 `hyperknowledge/templates/`
3. 提交 pull request

---

## 故障排除

### 模板未找到

```python
# 检查模板路径
Template.list()  # 列出所有模板

# 验证目录
import os
print(os.listdir("~/.hyperknowledge/templates/"))
```

### 提取质量不佳

1. **添加更多示例** 在指南中
2. **优化字段描述** 使用具体约束
3. **拆分复杂模板** 为更小的模板
4. **使用更严格的规则** 约束输出

### 验证错误

```bash
# 验证 YAML 语法
python -c "import yaml; yaml.safe_load(open('template.yaml'))"
```

---

## 另请参见

**前置知识：**
- [模板格式参考](../../concepts/templates-format.md) — 完整 YAML 规范
- [使用模板](using-templates.md) — Level 1: 模板基础用法

**进阶使用：**
- [增量更新](incremental-updates.md) — 添加更多文档
- [搜索和聊天](search-and-chat.md) — 使用提取的知识
- [模板库](../../templates/index.md) — 浏览现有模板
