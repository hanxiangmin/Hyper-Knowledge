# 模板库

根据您的任务选择合适的模板。

---

## 我要分析...

<div class="grid cards" markdown>

-   :material-file-document:{ .lg .middle } **研究论文**

    ---

    提取概念、方法、结论及关系

    - [概念图谱](examples/research-paper.md) — *推荐*
    - [知识图谱](examples/research-paper.md#knowledge-graph)
    - [文档结构](examples/research-paper.md#document-structure)

-   :material-account:{ .lg .middle } **人物传记**

    ---

    提取生平事件、关系和时间线

    - [传记图谱](reference/general.md) — *推荐*
    - [人物摘要](reference/general.md)

-   :material-chart-line:{ .lg .middle } **财务报告**

    ---

    提取财务指标、风险因素、股权结构

    - [财报摘要](examples/financial-report.md) — *推荐*
    - [风险因素](examples/financial-report.md#risk-factors)
    - [股权图谱](examples/financial-report.md#ownership-structure)

-   :material-scale-balance:{ .lg .middle } **法律文档**

    ---

    提取义务条款、案例、合规项

    - [合同义务](examples/legal-contract.md) — *推荐*
    - [案例时间线](examples/legal-contract.md#case-timeline)
    - [定义术语](examples/legal-contract.md#defined-terms)

-   :material-hospital:{ .lg .middle } **医疗记录**

    ---

    提取症状、治疗方案和时间线

    - [住院时间线](reference/medicine.md) — *推荐*
    - [药物相互作用](reference/medicine.md)
    - [出院摘要](reference/medicine.md)

-   :material-leaf:{ .lg .middle } **中医文献**

    ---

    提取草药属性和方剂组成

    - [草药属性](reference/tcm.md) — *推荐*
    - [方剂组成](reference/tcm.md)
    - [经络图谱](reference/tcm.md)

-   :material-factory:{ .lg .middle } **工业文档**

    ---

    提取设备、安全和操作流程

    - [设备拓扑](reference/industry.md) — *推荐*
    - [安全控制](reference/industry.md)
    - [操作流程](reference/industry.md)

</div>

---

## 不确定用什么？

**按任务类型：**

| 任务 | 推荐模板 |
|------|---------|
| 文档摘要 | `general/model` |
| 提取列表 | `general/list` |
| 构建知识网络 | `general/graph` |
| 创建时间线 | `general/base_temporal_graph` |

→ [更多任务指南](choosing/by-task.md)

**按输出类型：**

| 输出 | 自动类型 | 适用场景 |
|------|---------|---------|
| 结构化摘要 | AutoModel | 需要报告 |
| 网络/图谱 | AutoGraph | 需要关系 |
| 时间线 | AutoTemporalGraph | 需要时序 |

→ [更多输出类型指南](choosing/by-output.md)

---

## 快速开始

```bash
# 列出所有模板
hk list template

# 使用模板
hk parse document.md -t general/biography_graph -l zh -o ./output/
```

```python
from hyperknowledge import Template

# 创建模板
ka = Template.create("general/biography_graph", "zh")

# 提取
result = ka.parse(text)
```

---

## 浏览所有模板

→ [完整模板参考](reference/overview.md)

---

## 创建自定义模板

需要特定功能？学习创建自己的模板：

→ [自定义模板指南](../../python/guides/custom-templates.md)
