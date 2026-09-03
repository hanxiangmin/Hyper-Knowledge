# 按任务选择

为您的具体任务找到合适的模板。

---

## 研究与学术

### 分析研究论文

**目标：** 提取概念、方法、结果及其关系

**推荐：** `general/concept_graph`

```bash
hk parse paper.md -t general/concept_graph -l zh -o ./paper_kb/
```

**为什么选这个模板？**
- 自动识别关键概念及其定义
- 映射概念之间的关系
- 支持层次结构（如"神经网络" → "CNNs"）

**替代选项：**

| 模板 | 适用场景 |
|------|---------|
| `general/graph` | 更广泛的领域知识 |
| `general/doc_structure` | 文档大纲提取 |
| `general/workflow_graph` | 方法/流程工作流 |

---

### 提取技术文档

**目标：** 从手册、规格说明或文档中获取结构化信息

**推荐：** `general/model`

```python
from hyperknowledge import Template

ka = Template.create("general/model", "zh")
result = ka.parse(spec_text)

print(result.data)
```

---

## 人物与传记

### 分析传记

**目标：** 提取生平事件、关系和时间线

**推荐：** `general/biography_graph`

```bash
hk parse biography.md -t general/biography_graph -l zh -o ./bio_kb/
```

**功能：**
- 提取人物、地点、事件
- 捕获时间关系
- 创建时间线可视化

**示例输出：**
```python
{
    "entities": [
        {"name": "苏轼", "type": "人物"},
        {"name": "赤壁赋", "type": "作品"}
    ],
    "relations": [
        {"source": "苏轼", "target": "赤壁赋", "type": "创作", "time": "1082"}
    ]
}
```

**替代选项：**

| 模板 | 适用场景 |
|------|---------|
| `general/model` | 简单的人物摘要 |
| `general/graph` | 时间线之外的复杂关系 |

---

### 创建人物摘要

**目标：** 人物的结构化摘要

**推荐：** `general/model`

---

## 金融与商业

### 分析财报

**目标：** 提取财务指标和摘要

**推荐：** `finance/earnings_summary`

```bash
hk parse earnings.md -t finance/earnings_summary -l zh -o ./earnings/
```

**提取内容：**
- 收入、净利润、每股收益
- 同比增长、环比增长
n- 分部业绩
- 业绩指引

---

### 识别风险因素

**目标：** 从 SEC 文件或报告中提取风险因素

**推荐：** `finance/risk_factor_set`

```bash
hk parse 10k.md -t finance/risk_factor_set -l zh -o ./risks/
```

**输出：** 带分类的唯一风险因素集合

---

### 映射公司股权

**目标：** 提取股权结构和子公司

**推荐：** `finance/ownership_graph`

```bash
hk parse report.md -t finance/ownership_graph -l zh -o ./ownership/
```

---

## 法律文档

### 分析合同

**目标：** 提取义务、当事人和截止日期

**推荐：** `legal/contract_obligation`

```bash
hk parse contract.md -t legal/contract_obligation -l zh -o ./contract/
```

**提取内容：**
- 当事人义务
- 截止日期和里程碑
- 条件和条款

---

### 追踪案例时序

**目标：** 创建法律案例事件时间线

**推荐：** `legal/case_fact_timeline`

```bash
hk parse case.md -t legal/case_fact_timeline -l zh -o ./case/
```

---

### 提取定义术语

**目标：** 获取合同中所有定义的术语

**推荐：** `legal/defined_term_set`

```bash
hk parse contract.md -t legal/defined_term_set -l zh -o ./terms/
```

---

## 医疗与健康

### 患者时间线

**目标：** 追踪住院或治疗时间线

**推荐：** `medicine/hospital_timeline`

```bash
hk parse record.md -t medicine/hospital_timeline -l zh -o ./patient/
```

---

### 药物信息

**目标：** 提取药物相互作用和属性

**推荐：** `medicine/drug_interaction`

```bash
hk parse drug_info.md -t medicine/drug_interaction -l zh -o ./drugs/
```

---

### 出院摘要

**目标：** 生成患者出院摘要

**推荐：** `medicine/discharge_instruction`

---

## 中医药

### 草药属性

**目标：** 提取草药特性和用途

**推荐：** `tcm/herb_property`

---

### 方剂分析

**目标：** 分析中药方剂组成

**推荐：** `tcm/formula_composition`

---

## 工业与制造

### 设备文档

**目标：** 映射设备拓扑和连接

**推荐：** `industry/equipment_topology`

---

### 安全程序

**目标：** 提取安全控制系统

**推荐：** `industry/safety_control`

---

## 快速参考

| 任务 | 模板 | 类型 |
|------|------|------|
| 研究论文概念 | `general/concept_graph` | graph |
| 人物传记 | `general/biography_graph` | temporal_graph |
| 财务摘要 | `finance/earnings_summary` | model |
| 风险因素 | `finance/risk_factor_set` | set |
| 合同义务 | `legal/contract_obligation` | list |
| 案例时间线 | `legal/case_fact_timeline` | temporal_graph |
| 住院时间线 | `medicine/hospital_timeline` | temporal_graph |
| 药物相互作用 | `medicine/drug_interaction` | graph |

---

## 还不确定？

→ [按输出类型选择](by-output.md)  
→ [如何选择](../how-to-choose.md)  
→ [模板概览](../reference/overview.md)
