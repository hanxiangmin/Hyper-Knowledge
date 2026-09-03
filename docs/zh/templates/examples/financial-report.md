# 财务报告分析

从收益报告和 SEC 文件中提取财务信息的完整指南。

---

## 场景

您有一份财务文档，想要：
- 提取收益指标（收入、EPS、增长）
- 识别风险因素
- 映射股权结构
- 创建事件时间线

---

## 按任务推荐模板

### 收益摘要

**模板：** `finance/earnings_summary`

最适合季度/年度收益报告、10-Q、10-K 文件。

**提取内容：**
- 收入和净利润
- EPS（基本和稀释）
- 同比和环比增长
- 分部业绩
- 前瞻指引

---

### 风险因素 {#risk-factors}

**模板：** `finance/risk_factor_set`

最适合 SEC 文件的风险评估部分。

**提取内容：**
- 风险类别
- 风险描述
- 影响评估

---

### 股权结构 {#ownership-structure}

**模板：** `finance/ownership_graph`

最适合映射子公司、投资和企业结构。

**提取内容：**
- 子公司关系
- 股权百分比
- 投资实体

---

## 完整工作流：收益分析

### 第 1 步：提取收益数据

=== "CLI"

    ```bash
    hk parse earnings_10k.md -t finance/earnings_summary -l zh -o ./earnings/
    ```

=== "Python"

    ```python
    from hyperknowledge import Template

    # 加载报告
    with open("earnings_report.md", "r") as f:
        report = f.read()

    # 创建模板
    ka = Template.create("finance/earnings_summary", "zh")

    # 提取
    result = ka.parse(report)

    # 访问数据
    print(f"收入：${result.data.revenue:,.0f}")
    print(f"EPS：${result.data.eps:.2f}")
    print(f"同比增长：{result.data.yoy_growth}%")
    ```

**示例输出：**
```python
{
    "revenue": 1234567890,
    "net_income": 98765432,
    "eps": 2.45,
    "eps_diluted": 2.40,
    "yoy_growth": 15.3,
    "qoq_growth": 3.2,
    "segments": [
        {"name": "云服务", "revenue": 500000000},
        {"name": "硬件", "revenue": 734567890}
    ],
    "guidance": {
        "next_quarter_revenue": "¥8.5B - ¥9.5B",
        "full_year_eps": "¥70.00 - ¥77.00"
    }
}
```

---

### 第 2 步：提取风险因素

> **注意：** 以下步骤假设您在第 1 步使用了 Python 方式。如果使用了 CLI，请使用 `ka.load("./earnings/")` 加载结果。

```python
# 提取风险
risk_ka = Template.create("finance/risk_factor_set", "zh")
risk_result = risk_ka.parse(report)

print(f"\n识别了 {len(risk_result.data.items)} 个风险因素：")
for risk in risk_result.data.items:
    print(f"\n[{risk.category}] {risk.description[:100]}...")
```

---

### 第 3 步：保存和比较

```python
# 保存收益数据
result.dump("./earnings_q3_2024/")

# 稍后比较季度
from pathlib import Path
import json

def compare_quarters(q1_path, q2_path):
    """比较两个季度的收益。"""
    q1_data = json.load(open(Path(q1_path) / "data.json"))
    q2_data = json.load(open(Path(q2_path) / "data.json"))
    
    revenue_change = ((q2_data["revenue"] - q1_data["revenue"]) 
                      / q1_data["revenue"] * 100)
    
    print(f"收入变化：{revenue_change:+.1f}%")
    print(f"Q1：${q1_data['revenue']:,.0f}")
    print(f"Q2：${q2_data['revenue']:,.0f}")

compare_quarters("./earnings_q2_2024/", "./earnings_q3_2024/")
```

---

## 股权结构分析

### 提取企业结构

```python
from hyperknowledge import Template

# 分析股权
ka = Template.create("finance/ownership_graph", "zh")
result = ka.parse(ownership_report)

# 可视化结构
result.build_index()
result.show()

# 查询股权
response = result.chat("公司拥有哪些 100% 控股的子公司？")
print(response.content)
```

**示例输出：**
```python
# 实体
[
    {"name": "母公司", "type": "控股公司"},
    {"name": "子公司 A", "type": "子公司"},
    {"name": "合资企业 B", "type": "合资企业"}
]

# 关系
[
    {"source": "母公司", "target": "子公司 A", 
     "type": "控股", "percentage": 100},
    {"source": "母公司", "target": "合资企业 B", 
     "type": "控股", "percentage": 51}
]
```

---

## 财务事件时间线

### 追踪财务事件

```python
# 提取事件时间线
ka = Template.create("finance/event_timeline", "zh")
result = ka.parse(report)

# 显示时间线
for edge in result.edges:
    if hasattr(edge, 'time'):
        print(f"{edge.time}：{edge.source} - {edge.type} - {edge.target}")
```

**示例事件：**
- 产品发布
- 收购公告
- 股息声明
- 管理层变动

---

## 对比表

| 模板 | 最佳场景 | 输出 |
|------|---------|------|
| `earnings_summary` | 财务指标 | 结构化模型 |
| `risk_factor_set` | 风险评估 | 唯一风险项目 |
| `ownership_graph` | 企业结构 | 实体网络 |
| `event_timeline` | 财务事件 | 时间线图谱 |
| `sentiment_model` | 市场情绪 | 情感分析 |

---

## 批量处理多份报告

```python
"""批量处理财务报告。"""

from hyperknowledge import Template
from pathlib import Path
import pandas as pd

def batch_extract_reports(report_dir, output_dir):
    """从多份财务报告中提取数据。"""
    
    ka = Template.create("finance/earnings_summary", "zh")
    results = []
    
    for report_file in Path(report_dir).glob("*.md"):
        print(f"处理 {report_file.name}...")
        
        text = report_file.read_text()
        result = ka.parse(text)
        
        # 保存单个
        output_path = Path(output_dir) / report_file.stem
        result.dump(output_path)
        
        # 收集聚合
        results.append({
            "file": report_file.name,
            "revenue": result.data.revenue,
            "eps": result.data.eps,
            "yoy_growth": result.data.yoy_growth
        })
    
    # 创建汇总表
    df = pd.DataFrame(results)
    df.to_csv(Path(output_dir) / "summary.csv", index=False)
    
    print(f"\n处理了 {len(results)} 份报告")
    print(f"汇总保存到：{output_dir}/summary.csv")
    
    return df

# 用法
df = batch_extract_reports("./reports/", "./extracted/")
```

---

## 最佳实践技巧

### 1. 文档类型

| 文档 | 推荐模板 |
|------|---------|
| 10-K 年报 | `earnings_summary` + `risk_factor_set` |
| 10-Q 季报 | `earnings_summary` |
| 代理声明 | `ownership_graph` |
| 财报电话会议记录 | `sentiment_model` + `event_timeline` |
| 投资者演示 | `earnings_summary` |

### 2. 语言支持

=== "CLI"

    ```bash
    # 中国公司（中文财报）
    hk parse report.md -t finance/earnings_summary -l zh

    # 美国公司（英文）
    hk parse report.md -t finance/earnings_summary -l en
    ```

### 3. 组合模板

```python
from hyperknowledge import Template

# 用多个模板解析报告
text = open("10k_report.md").read()

# 提取收益
earnings = Template.create("finance/earnings_summary", "zh").parse(text)

# 提取风险
risks = Template.create("finance/risk_factor_set", "zh").parse(text)

# 保存组合
earnings.dump("./10k_earnings/")
risks.dump("./10k_risks/")
```

### 4. 数据验证

```python
# 检查提取的数据
result = ka.parse(report)

def validate_earnings(data):
    """验证收益数据。"""
    assert data.revenue > 0, "收入必须为正数"
    assert data.eps is not None, "EPS 是必需的"
    assert -100 < data.yoy_growth < 1000, "增长率似乎不合理"
    print("✓ 数据验证通过")

validate_earnings(result.data)
```

---

## 另请参见

- [按任务选择](../choosing/by-task.md) — 其他财务分析模板
- [金融模板](../reference/finance.md) — 所有金融模板
- [自定义模板指南](../../python/guides/custom-templates.md) — 创建自定义财务模板
