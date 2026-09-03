# 金融模板

金融文档分析和提取。

---

## 概述

金融模板针对从金融文档中提取结构化信息进行了优化。

---

## 模板

### earnings_summary

**类型**：model

**用途**：从财报中提取关键指标

**最适合**：
- 季度财报（10-Q）
- 年度报告（10-K）
- 财报电话会议记录

**字段**：

| 字段 | 类型 | 描述 |
|------|------|------|
| `company_name` | str | 公司名称 |
| `quarter` | str | 财政季度 |
| `revenue` | float | 总收入 |
| `net_income` | float | 净收入 |
| `eps` | float | 每股收益 |
| `yoy_growth` | float | 同比增长率 |

=== "CLI"

    ```bash
    hk parse 10q.md -t finance/earnings_summary -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("finance/earnings_summary", "zh")
    result = ka.parse(earnings_text)

    print(f"收入: ${result.data.revenue}B")
    print(f"EPS: ${result.data.eps}")
    ```

---

### ownership_graph

**类型**：graph

**用途**：提取公司股权结构

**最适合**：
- 股东报告
- 代理声明
- 公司结构

**实体**：
- 公司
- 股东
- 子公司

**关系**：
- `owns` — 所有权关系
- `controls` — 控制关系
- `subsidiary_of` — 子公司关系

=== "CLI"

    ```bash
    hk parse proxy.md -t finance/ownership_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("finance/ownership_graph", "zh")
    result = ka.parse(proxy_statement)

    # 构建索引以支持可视化中的交互式搜索/对话
    result.build_index()

    result.show()  # 显示带有交互功能的所有权网络
    ```

---

### event_timeline

**类型**：temporal_graph

**用途**：提取带日期的金融事件

**最适合**：
- 公司事件历史
- 并购时间线
- 市场事件

**特性**：
- 事件日期
- 事件类型（合并、收购、IPO 等）
- 相关实体

=== "CLI"

    ```bash
    hk parse history.md -t finance/event_timeline -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("finance/event_timeline", "zh")
    result = ka.parse(history_text)

    print(f"事件数: {len(result.nodes)}")
    for node in result.nodes:
        print(f"  - {node.name}")
    ```

---

### risk_factor_set

**类型**：set

**用途**：提取唯一风险因素

**最适合**：
- 风险因素章节
- 尽职调查报告
- 风险评估

=== "CLI"

    ```bash
    hk parse 10k.md -t finance/risk_factor_set -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("finance/risk_factor_set", "zh")
    result = ka.parse(risk_section)

    print(f"发现 {len(result.data.items)} 个风险因素")
    for risk in result.data.items:
        print(f"  - {risk}")
    ```

---

### sentiment_model

**类型**：model

**用途**：提取情感指标

**最适合**：
- 新闻文章
- 分析师报告
- 社交媒体情感

**字段**：

| 字段 | 类型 | 描述 |
|------|------|------|
| `sentiment` | str | 整体情感（正面/负面/中性） |
| `confidence` | float | 置信度分数 |
| `key_points` | list[str] | 关键情感指标 |

=== "CLI"

    ```bash
    hk parse article.md -t finance/sentiment_model -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("finance/sentiment_model", "zh")
    result = ka.parse(article_text)

    print(f"情感: {result.data.sentiment}")
    print(f"置信度: {result.data.confidence}")
    for point in result.data.key_points:
        print(f"  - {point}")
    ```

---

## 用例

### 用例 1：季度报告分析

```python
from hyperknowledge import Template

# 提取财报
ka = Template.create("finance/earnings_summary", "zh")
q1 = ka.parse(q1_report)
q2 = ka.parse(q2_report)

# 对比
print(f"Q1 收入: ${q1.data.revenue}B")
print(f"Q2 收入: ${q2.data.revenue}B")
print(f"增长: {(q2.data.revenue - q1.data.revenue) / q1.data.revenue * 100:.1f}%")
```

### 用例 2：股权结构

```python
ka = Template.create("finance/ownership_graph", "zh")
ownership = ka.parse(proxy_statement)

# 查找主要股东
shareholders = [
    e for e in ownership.data.entities 
    if e.type == "shareholder"
]

for sh in sorted(shareholders, key=lambda x: x.stake, reverse=True)[:5]:
    print(f"{sh.name}: {sh.stake}%")
```

### 用例 3：风险评估

```python
ka = Template.create("finance/risk_factor_set", "zh")
risk_factors = ka.parse(risk_section)

# 分类风险
for risk in risk_factors.data.items:
    if "监管" in risk:
        print(f"监管风险: {risk}")
    elif "市场" in risk:
        print(f"市场风险: {risk}")
```

---

## 数据源

这些模板适用于：
- SEC 文件（10-K、10-Q、8-K）
- 财报电话会议记录
- 投资者演示文稿
- 分析师报告
- 财经新闻

---

## 提示

1. **earnings_summary 用于快速指标** — 快速提取关键数字
2. **ownership_graph 用于结构** — 可视化公司层次结构
3. **event_timeline 用于历史** — 跟踪公司事件
4. **组合模板** — 使用多个模板进行综合分析

---

## 参见

- [模板概览](overview.md)
- [如何选择](../how-to-choose.md)
- [通用模板](general.md)
