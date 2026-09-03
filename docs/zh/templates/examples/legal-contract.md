# 法律文档分析

从法律合同和案例文档中提取信息的完整指南。

---

## 场景

您有一份法律文档，想要：
- 提取合同义务和截止日期
- 识别定义术语
- 创建案例年表
- 映射先例关系

---

## 按任务推荐模板

### 合同义务

**模板：** `legal/contract_obligation`

最适合服务协议、保密协议、雇佣合同、供应商协议。

**提取内容：**
- 当事人义务
- 截止日期和里程碑
- 交付物
- 先决条件
- 违约后果

---

### 定义术语 {#defined-terms}

**模板：** `legal/defined_term_set`

最适合从合同中提取所有大写的定义术语。

**提取内容：**
- 术语定义
- 交叉引用
- 定义位置

---

### 案例时间线 {#case-timeline}

**模板：** `legal/case_fact_timeline`

最适合诉讼年表、案例摘要。

**提取内容：**
- 时序事件
- 当事人行为
- 法院判决

---

## 完整工作流：合同分析

### 第 1 步：提取义务

=== "CLI"

    ```bash
    hk parse contract.md -t legal/contract_obligation -l zh -o ./contract/
    ```

=== "Python"

    ```python
    from hyperknowledge import Template

    # 加载合同
    with open("service_agreement.md", "r") as f:
        contract = f.read()

    # 创建模板
    ka = Template.create("legal/contract_obligation", "zh")

    # 提取
    result = ka.parse(contract)

    print(f"找到 {len(result.data.items)} 个义务")
    ```

**示例输出：**
```python
{
    "items": [
        {
            "party": "服务提供商",
            "obligation": "30 天内交付软件模块",
            "deadline": "2024-03-15",
            "deliverable": "源代码和文档",
            "conditions": "收到付款后"
        },
        {
            "party": "客户",
            "obligation": "支付里程碑款项",
            "deadline": "2024-03-01",
            "amount": "¥350,000",
            "conditions": "交付物验收后"
        }
    ]
}
```

---

### 第 2 步：提取定义术语

> **注意：** 以下步骤假设您在第 1 步使用了 Python 方式。如果使用了 CLI，请使用 `ka.load("./contract/")` 加载结果。

```python
# 提取定义术语
terms_ka = Template.create("legal/defined_term_set", "zh")
terms_result = terms_ka.parse(contract)

print(f"\n找到 {len(terms_result.data.items)} 个定义术语：")
for term in terms_result.data.items:
    print(f"\n{term.term}：{term.definition}")
```

**示例：**
```
"保密信息"：所有非公开、专有或机密信息...

"交付物"：要交付的软件、文档和材料...

"生效日期"：上方首次书写的日期...
```

---

### 第 3 步：构建合同知识库

```python
# 构建查询索引
result.build_index()

# 保存供将来参考
result.dump("./contract_analysis/")

# 查询义务
response = result.chat("服务提供商在数据安全方面有哪些义务？")
print(response.content)

response = result.chat("列出所有付款里程碑及其到期日")
print(response.content)
```

---

## 案例分析工作流

### 提取案例时间线

```python
from hyperknowledge import Template

# 加载案例文档
with open("case_summary.md", "r") as f:
    case = f.read()

# 提取时间线
ka = Template.create("legal/case_fact_timeline", "zh")
result = ka.parse(case)

# 显示年表
print("案例时间线：")
for edge in sorted(result.edges, key=lambda e: e.time if hasattr(e, 'time') else ''):
    if hasattr(edge, 'time'):
        print(f"\n{edge.time}：")
        print(f"  事件：{edge.source}")
        print(f"  行为：{edge.type}")
        print(f"  当事人：{edge.target}")

# 可视化
result.build_index()
result.show()
```

**示例输出：**
```
2023-01-15：
  事件：提起诉讼
  行为：发起
  当事人：原告

2023-02-01：
  事件：驳回动议
  行为：提交
  当事人：被告

2023-03-15：
  事件：证据开示阶段
  行为：开始
  当事人：双方
```

---

## 案例先例分析

### 映射先例关系

```python
# 提取案例引用
ka = Template.create("legal/case_citation", "zh")
result = ka.parse(legal_opinion)

# 分析引用网络
print("引用的案例：")
for node in result.nodes:
    if node.type == "案例":
        print(f"  - {node.name} ({node.citation})")
        print(f"    原则：{node.principle[:100]}...")

# 可视化先例网络
result.build_index()
result.show()
```

---

## 对比表

| 模板 | 最佳场景 | 输出 |
|------|---------|------|
| `contract_obligation` | 服务协议、保密协议 | 义务列表 |
| `defined_term_set` | 定义术语提取 | 术语定义集合 |
| `case_fact_timeline` | 诉讼年表 | 时间线图谱 |
| `case_citation` | 先例分析 | 引用网络 |
| `compliance_list` | 监管要求 | 合规清单 |

---

## 批量合同处理

```python
"""批量分析多个合同。"""

from hyperknowledge import Template
from pathlib import Path
import pandas as pd

def analyze_contract_folder(folder_path, output_dir):
    """从文件夹中所有合同提取义务。"""
    
    ka = Template.create("legal/contract_obligation", "zh")
    all_obligations = []
    
    for contract_file in Path(folder_path).glob("*.md"):
        print(f"处理 {contract_file.name}...")
        
        text = contract_file.read_text()
        result = ka.parse(text)
        
        # 保存单个
        output_path = Path(output_dir) / contract_file.stem
        result.dump(output_path)
        
        # 收集义务
        for obl in result.data.items:
            all_obligations.append({
                "contract": contract_file.name,
                "party": obl.party,
                "obligation": obl.obligation,
                "deadline": getattr(obl, 'deadline', 'N/A'),
                "deliverable": getattr(obl, 'deliverable', 'N/A')
            })
    
    # 创建汇总
    df = pd.DataFrame(all_obligations)
    df.to_csv(Path(output_dir) / "all_obligations.csv", index=False)
    
    print(f"\n处理了 {len(list(Path(folder_path).glob('*.md')))} 个合同")
    print(f"找到 {len(all_obligations)} 个总义务")
    
    return df

# 用法
df = analyze_contract_folder("./contracts/", "./contract_analysis/")

# 查找即将到期的截止日期
from datetime import datetime
df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
upcoming = df[df['deadline'] > datetime.now()].sort_values('deadline')
print("\n即将到期的截止日期：")
print(upcoming[['contract', 'party', 'deadline', 'obligation']].head(10))
```

---

## 最佳实践技巧

### 1. 文档准备

- 将 PDF 转换为干净的 Markdown
- 移除页眉/页脚/页码
- 保留段落结构
- 保留章节标题

### 2. 合同类型

| 合同类型 | 主要模板 | 次要模板 |
|---------|---------|---------|
| 服务协议 | `contract_obligation` | `defined_term_set` |
| 保密协议 | `contract_obligation` | `defined_term_set` |
| 雇佣合同 | `contract_obligation` | `defined_term_set` |
| 许可协议 | `contract_obligation` | `defined_term_set` |
| 诉讼摘要 | `case_fact_timeline` | `case_citation` |
| 监管文档 | `compliance_list` | - |

### 3. 多语言支持

=== "CLI"

    ```bash
    # 中文合同
    hk parse contract.md -t legal/contract_obligation -l zh

    # 英文合同
    hk parse contract.md -t legal/contract_obligation -l en
    ```

### 4. 组合模板

```python
# 全面合同分析
text = open("contract.md").read()

# 提取义务
obligations = Template.create("legal/contract_obligation", "zh").parse(text)

# 提取定义术语
terms = Template.create("legal/defined_term_set", "zh").parse(text)

# 保存两者
obligations.dump("./contract_obligations/")
terms.dump("./contract_terms/")

# 交叉引用
print("\n引用定义术语的义务：")
for obl in obligations.data.items:
    for term in terms.data.items:
        if term.term.lower() in obl.obligation.lower():
            print(f"  '{term.term}' 在：{obl.obligation[:60]}...")
```

---

## 示例：合同审查清单

```python
"""自动化合同审查清单。"""

from hyperknowledge import Template
from datetime import datetime

def contract_review_checklist(contract_path):
    """从合同生成审查清单。"""
    
    text = open(contract_path).read()
    
    # 提取义务
    obl_ka = Template.create("legal/contract_obligation", "zh")
    obl_result = obl_ka.parse(text)
    
    # 提取术语
    terms_ka = Template.create("legal/defined_term_set", "zh")
    terms_result = terms_ka.parse(text)
    
    print("=" * 60)
    print("合同审查清单")
    print("=" * 60)
    
    # 义务摘要
    print("\n## 义务摘要")
    print(f"总义务数：{len(obl_result.data.items)}")
    
    party_obligations = {}
    for obl in obl_result.data.items:
        party = obl.party
        if party not in party_obligations:
            party_obligations[party] = []
        party_obligations[party].append(obl)
    
    for party, obligations in party_obligations.items():
        print(f"\n{party}：{len(obligations)} 个义务")
        for obl in obligations[:3]:  # 显示前 3 个
            deadline = getattr(obl, 'deadline', '无截止日期')
            print(f"  - {obl.obligation[:50]}... (到期：{deadline})")
    
    # 关键日期
    print("\n## 关键日期")
    deadlines = [obl.deadline for obl in obl_result.data.items 
                 if hasattr(obl, 'deadline') and obl.deadline]
    for deadline in sorted(deadlines)[:5]:
        print(f"  - {deadline}")
    
    # 关键术语
    print("\n## 关键定义术语")
    for term in terms_result.data.items[:10]:
        print(f"  - {term.term}")
    
    # 风险标记
    print("\n## 需审查的风险标记")
    risk_keywords = ['无限', '永久', '唯一酌情权', '放弃', '赔偿']
    for obl in obl_result.data.items:
        for keyword in risk_keywords:
            if keyword in obl.obligation:
                print(f"  ⚠ 包含'{keyword}'：{obl.obligation[:60]}...")
    
    print("\n" + "=" * 60)

# 用法
contract_review_checklist("service_agreement.md")
```

---

## 另请参见

- [按任务选择](../choosing/by-task.md) — 其他法律分析模板
- [法律模板](../reference/legal.md) — 所有法律模板
- [自定义模板指南](../../python/guides/custom-templates.md) — 创建自定义法律模板
