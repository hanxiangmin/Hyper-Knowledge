# 模板概览

所有可用模板的完整概览。

---

## 统计

- **模板总数**：80+
- **类别**：6 个领域
- **自动类型**：8 种类型
- **语言**：中文、英文

---

## 按领域

### 通用模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `general/model` | model | 基础结构化模型 |
| `general/list` | list | 基础有序列表 |
| `general/set` | set | 基础唯一集合 |
| `general/graph` | graph | 基础知识图谱 |
| `general/base_hypergraph` | hypergraph | 基础超图 |
| `general/base_temporal_graph` | temporal_graph | 基础时间线图谱 |
| `general/base_spatial_graph` | spatial_graph | 基础空间图谱 |
| `general/base_spatio_temporal_graph` | spatio_temporal_graph | 基础时空图谱 |
| `general/biography_graph` | temporal_graph | 人物生平时间线 |
| `general/concept_graph` | graph | 研究概念提取 |
| `general/graph` | graph | 通用知识提取 |
| `general/doc_structure` | model | 文档大纲结构 |
| `general/workflow_graph` | graph | 流程工作流 |

### 金融模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `finance/earnings_summary` | model | 季度/年度财报 |
| `finance/event_timeline` | temporal_graph | 财务事件 |
| `finance/ownership_graph` | graph | 公司股权结构 |
| `finance/risk_factor_set` | set | 风险因素 |
| `finance/sentiment_model` | model | 情感分析 |

### 法律模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `legal/case_citation` | graph | 法律案例引用 |
| `legal/case_fact_timeline` | temporal_graph | 案例年表 |
| `legal/compliance_list` | list | 合规要求 |
| `legal/contract_obligation` | list | 合同义务 |
| `legal/defined_term_set` | set | 定义术语 |

### 医疗模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `medicine/anatomy_graph` | graph | 解剖结构 |
| `medicine/discharge_instruction` | model | 患者出院摘要 |
| `medicine/drug_interaction` | graph | 药物相互作用 |
| `medicine/hospital_timeline` | temporal_graph | 住院时间线 |
| `medicine/symptom_list` | list | 症状 |
| `medicine/treatment_map` | graph | 治疗方案 |

### 中医模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `tcm/formula_composition` | graph | 中药方剂组成 |
| `tcm/herb_property` | model | 草药属性 |
| `tcm/herb_relation` | graph | 草药关系 |
| `tcm/meridian_graph` | graph | 经络路径 |
| `tcm/syndrome_reasoning` | graph | 证候推理 |

### 工业模板

| 模板 | 类型 | 描述 |
|------|------|------|
| `industry/emergency_response` | graph | 应急程序 |
| `industry/equipment_topology` | graph | 设备连接 |
| `industry/failure_case` | temporal_graph | 故障分析 |
| `industry/operation_flow` | graph | 操作工作流 |
| `industry/safety_control` | graph | 安全控制系统 |

---

## 按自动类型

### Model 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/model` | general | 基础结构化模型 |
| `finance/earnings_summary` | finance | 财务摘要 |
| `finance/sentiment_model` | finance | 情感分析 |
| `medicine/discharge_instruction` | medical | 出院摘要 |
| `tcm/herb_property` | tcm | 草药属性 |

### List 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/list` | general | 基础列表 |
| `legal/compliance_list` | legal | 合规要求 |
| `legal/contract_obligation` | legal | 合同义务 |
| `medicine/symptom_list` | medical | 症状 |

### Set 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/set` | general | 基础集合 |
| `finance/risk_factor_set` | finance | 风险因素 |
| `legal/defined_term_set` | legal | 定义术语 |

### Graph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/graph` | general | 基础图谱 |
| `general/graph` | general | 知识图谱 |
| `general/concept_graph` | general | 概念图谱 |
| `general/workflow_graph` | general | 流程工作流 |
| `finance/ownership_graph` | finance | 股权结构 |
| `legal/case_citation` | legal | 案例引用 |
| `medicine/anatomy_graph` | medical | 解剖学 |
| `medicine/drug_interaction` | medical | 药物相互作用 |
| `medicine/treatment_map` | medical | 治疗方案 |
| `tcm/herb_relation` | tcm | 草药关系 |
| `tcm/meridian_graph` | tcm | 经络路径 |
| `tcm/syndrome_reasoning` | tcm | 证候推理 |
| `industry/equipment_topology` | industry | 设备连接 |
| `industry/operation_flow` | industry | 操作工作流 |
| `industry/safety_control` | industry | 安全控制系统 |

### Temporal Graph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_temporal_graph` | general | 基础时间线图谱 |
| `general/biography_graph` | general | 传记时间线 |
| `finance/event_timeline` | finance | 财务事件 |
| `legal/case_fact_timeline` | legal | 案例时间线 |
| `medicine/hospital_timeline` | medical | 住院时间线 |
| `industry/failure_case` | industry | 故障分析 |

### Spatial Graph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_spatial_graph` | general | 基础空间图谱 |

### Spatio-Temporal Graph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_spatio_temporal_graph` | general | 基础时空图谱 |

### Hypergraph 模板

| 模板 | 领域 | 描述 |
|------|------|------|
| `general/base_hypergraph` | general | 基础超图 |

---

## 方法（算法级访问）

方法提供对提取算法的直接访问：

| 方法 | 类型 | 最佳场景 |
|------|------|---------|
| `method/light_rag` | RAG | 通用，快速 |
| `method/graph_rag` | RAG | 大型文档 |
| `method/hyper_rag` | RAG | 复杂关系 |
| `method/itext2kg` | 标准 | 高质量三元组 |
| `method/itext2kg_star` | 标准 | 增强质量 |
| `method/kg_gen` | 标准 | 灵活生成 |
| `method/atom` | 标准 | 带证据的时间提取 |

→ [何时使用方法](../../python/guides/using-methods.md)

---

## 使用本参考

### CLI

```bash
# 列出所有模板
hk list template

# 按领域筛选
hk list template | grep finance

# 获取模板信息
hk info template general/biography_graph
```

### Python

```python
from hyperknowledge import Template

# 获取所有模板
templates = Template.list()

# 按类型筛选
graphs = Template.list(filter_by_type="graph")
temporal = Template.list(filter_by_type="temporal_graph")

# 按领域/标签筛选
finance = Template.list(filter_by_tag="finance")
medical = Template.list(filter_by_tag="medicine")

# 获取模板详情
cfg = Template.get("general/biography_graph")
print(cfg.name)        # biography_graph
print(cfg.type)        # temporal_graph
print(cfg.description) # 描述文本
print(cfg.tags)        # ['general', 'biography']
print(cfg.language)    # ['zh', 'en']
```

---

## 另请参见

- [按任务选择](../choosing/by-task.md) — 基于任务的选择
- [按输出类型选择](../choosing/by-output.md) — 基于输出的选择
- [模板库首页](../index.md) — 返回主模板页面
- [自定义模板指南](../../python/guides/custom-templates.md) — 创建您自己的模板
