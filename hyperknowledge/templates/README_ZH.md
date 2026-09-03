# Hyper-Knowledge 知识模板库

面向垂直行业的 YAML 模板库，用于从领域文档中提取结构化知识。

> 英文版 [English](./README.md)

---

## 目录

- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [AutoType 参考](#autotype-参考)
- [如何选择类型](#如何选择类型)
- [文档-模板对照表](#文档-模板对照表)
- [模板目录](#模板目录)
  - [通用领域](#通用领域)
  - [金融领域](#金融领域)
  - [医疗领域](#医疗领域)
  - [中医领域](#中医领域)
  - [工业领域](#工业领域)
  - [法律领域](#法律领域)
- [基础模板参考](#基础模板参考)
- [自定义模板](#自定义模板)

---

## 快速开始

### 安装与配置

```python
from hyperknowledge.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()
```

### 加载并使用模板

```python
config = Gallery.get("general/workflow_graph")

template = TemplateFactory.create(config, llm, embedder)

result = template.parse("您的文档文本...")
```

### 浏览可用模板

```python
all_templates = Gallery.list()
print(f"模板总数: {len(all_templates)}")

graph_templates = Gallery.list(filter_by_type="graph")
print(f"图类型模板: {list(graph_templates.keys())}")

finance_templates = Gallery.list(filter_by_tag="finance")
print(f"金融模板: {list(finance_templates.keys())}")
```

---

## 核心概念

### 什么是知识模板？

知识模板是一个 YAML 配置文件，定义：
- **抽取内容**：从文档中提取什么（实体、关系、字段）
- **输出结构**：如何组织输出（schema 定义）
- **抽取规则**：给 LLM 的指令（指南和规则）

### 模板结构

```yaml
language: [zh, en]

name: template_name
type: graph | hypergraph | model | list | set | temporal_graph | spatial_graph | spatio_temporal_graph
tags: [domain, category]

description:
  zh: '中文描述'
  en: 'English description'

output:
  description:
    zh: '输出描述'
    en: 'Output description'
  entities:          # 图类型
    fields: [...]
  fields:           # 模型类型
    - name: field_name
      type: str | int | float | list
      description: {...}
  relations:
    fields: [...]

guideline:
  target: {...}
  rules_for_entities: [...]
  rules_for_relations: [...]

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
```

---

## AutoType 参考

Hyper-Knowledge 提供 8 种抽取类型，分为两大类：

### 记录类型（提取数据）

| 类型 | 描述 | 输出结构 |
|------|------|----------|
| **model** | 单个结构化对象 | 扁平字段与值 |
| **list** | 有序数组 | 排序后的项目列表 |
| **set** | 去重集合 | 唯一项目 |

### 图类型（提取关系）

| 类型 | 描述 | 输出结构 |
|------|------|----------|
| **graph** | 二元关系 | 节点 + 边 (source→target) |
| **hypergraph** | 多元关系 | 节点 + 超边 (多参与者) |
| **temporal_graph** | 带时间的关系 | 节点 + 边 + 时间戳 |
| **spatial_graph** | 带位置的关系 | 节点 + 边 + 坐标 |
| **spatio_temporal_graph** | 带时间和位置的关系 | 节点 + 边 + 两者 |

```
                    ┌─────────────┐
                    │   记录      │
                    │   类型      │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐     ┌───────────┐     ┌─────────┐
    │  model  │     │   list    │     │   set   │
    └─────────┘     └───────────┘     └─────────┘

                    ┌─────────────┐
                    │    图       │
                    │   类型      │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐     ┌───────────┐     ┌─────────────┐
    │  graph  │     │ hypergraph│     │ temporal_*  │
    └─────────┘     └───────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ spatial_*   │
                    └─────────────┘
```

---

## 如何选择类型

### 决策树

```
文档中是否包含实体之间的关系？
│
├─ 否
│   └─ 数据是单个结构化对象吗？
│       ├─ 是 → model
│       └─ 否
│           └─ 顺序重要吗？
│               ├─ 是 → list
│               └─ 否 → set
│
└─ 是
    └─ 关系是二元的 (A→B)？
        ├─ 是
        │   └─ 需要时间或位置？
        │       ├─ 只需时间 → temporal_graph
        │       ├─ 只需位置 → spatial_graph
        │       ├─ 两者都需要 → spatio_temporal_graph
        │       └─ 都不需要 → graph
        └─ 否（多方）
            └─ 需要时间或位置？
                ├─ 只需时间 → temporal_graph
                ├─ 只需位置 → spatial_graph
                ├─ 两者都需要 → spatio_temporal_graph
                └─ 都不需要 → hypergraph
```

### 快速参考

| 场景 | 推荐类型 |
|------|----------|
| 提取人物档案 | model |
| 列出所有参会者 | set |
| 按营收排名公司 | list |
| 提取谁在哪工作 | graph |
| 分析多方合同义务 | hypergraph |
| 构建公司历史时间线 | temporal_graph |
| 绘制门店位置和区域 | spatial_graph |
| 追踪带时间戳的配送路线 | spatio_temporal_graph |

---

## 文档-模板对照表

根据文档类型匹配合适的模板：

| 文档类型 | 推荐模板 | 类型 |
|----------|----------|------|
| **财报电话会议记录** | earnings_summary | model |
| **财经新闻** | sentiment_model, event_timeline | model, temporal_graph |
| **招股说明书** | ownership_graph, event_timeline | graph, temporal_graph |
| **临床实践指南** | treatment_map | hypergraph |
| **药物相互作用参考** | drug_interaction | graph |
| **出院小结** | hospital_timeline, discharge_instruction | temporal_graph, model |
| **医学教科书** | anatomy_graph | graph |
| **服务合同 (MSA)** | contract_obligation | hypergraph |
| **法院判决书** | case_fact_timeline, case_citation | temporal_graph, graph |
| **合规申报文档** | compliance_list, defined_term_set | list, set |
| **SOP / 操作手册** | workflow_graph, operation_flow | graph |
| **设备手册** | equipment_topology | graph |
| **安全管理手册** | safety_control, emergency_response | graph, graph |
| **故障分析报告** | failure_case | graph |
| **中医医案** | syndrome_reasoning | hypergraph |
| **经典方剂文本** | formula_composition | hypergraph |
| **针灸学文本** | meridian_graph | graph |
| **本草典籍** | herb_property | model |
| **人物传记 / 回忆录** | biography_graph | temporal_graph |
| **技术文档** | doc_structure | graph |
| **Skill 定义 (Agent)** | workflow_graph | graph |
| **概念性文本** | concept_graph | graph |

---

## 模板目录

### 通用领域

通用模板，适用于任何类型的文档。

**基础模板 (8)**

| 模板 | 类型 | 描述 |
|------|------|------|
| [base_model](./presets/general/base_model.yaml) | model | 通用结构化数据抽取 |
| [base_list](./presets/general/base_list.yaml) | list | 通用有序列表抽取 |
| [base_set](./presets/general/base_set.yaml) | set | 通用去重集合抽取 |
| [base_graph](./presets/general/base_graph.yaml) | graph | 通用知识图谱（实体 + 二元关系）|
| [base_hypergraph](./presets/general/base_hypergraph.yaml) | hypergraph | 通用超图（多元关系）|
| [base_temporal_graph](./presets/general/base_temporal_graph.yaml) | temporal_graph | 通用时序图（关系 + 时间）|
| [base_spatial_graph](./presets/general/base_spatial_graph.yaml) | spatial_graph | 通用空间图（关系 + 位置）|
| [base_spatio_temporal_graph](./presets/general/base_spatio_temporal_graph.yaml) | spatio_temporal_graph | 通用时空图（关系 + 时间 + 位置）|

**领域专用模板 (5)**

| 模板 | 类型 | 用途 | 适用文档 |
|------|------|------|----------|
| [workflow_graph](./presets/general/workflow_graph.yaml) | graph | 提取工作流步骤和执行顺序 | Skill 定义、Agent 工作流、SOP |
| [doc_structure](./presets/general/doc_structure.yaml) | graph | 提取文档层级和交叉引用 | 技术文档、论文、报告 |
| [biography_graph](./presets/general/biography_graph.yaml) | temporal_graph | 提取带时间戳的人生事件 | 传记、回忆录、年表 |
| [concept_graph](./presets/general/concept_graph.yaml) | graph | 提取概念层级和关系 | 教科书、百科全书、学术论文 |

---

### 金融领域

面向金融文档和投资者关系的模板。

| 模板 | 类型 | 用途 | 适用文档 |
|------|------|------|----------|
| [earnings_summary](./presets/finance/earnings_summary.yaml) | model | 提取财报会议关键指标 | 财报电话会议记录 |
| [sentiment_model](./presets/finance/sentiment_model.yaml) | model | 量化市场情绪和主题 | 财经新闻、研究报告 |
| [event_timeline](./presets/finance/event_timeline.yaml) | temporal_graph | 构建公司事件时间线 | 8-K 文件、新闻稿 |
| [ownership_graph](./presets/finance/ownership_graph.yaml) | graph | 提取股权结构 | 招股说明书、年报 |
| [risk_factor_set](./presets/finance/risk_factor_set.yaml) | set | 按类别编目风险因子 | 年报风险章节 |

---

### 医疗领域

面向临床和医学文档的模板。

| 模板 | 类型 | 用途 | 适用文档 |
|------|------|------|----------|
| [treatment_map](./presets/medicine/treatment_map.yaml) | hypergraph | 提取诊断-治疗-结果映射 | 临床指南 |
| [drug_interaction](./presets/medicine/drug_interaction.yaml) | graph | 绘制药物相互作用网络 | 药品参考、相互作用数据库 |
| [anatomy_graph](./presets/medicine/anatomy_graph.yaml) | graph | 提取解剖层级 | 解剖学教科书、手术记录 |
| [hospital_timeline](./presets/medicine/hospital_timeline.yaml) | temporal_graph | 构建患者入院时间线 | 出院小结、病程记录 |
| [discharge_instruction](./presets/medicine/discharge_instruction.yaml) | model | 结构化出院信息 | 出院小结、患者教育 |

---

### 中医领域

面向中医药文献的模板。

| 模板 | 类型 | 用途 | 适用文档 |
|------|------|------|----------|
| [formula_composition](./presets/tcm/formula_composition.yaml) | hypergraph | 提取方剂组成（君臣佐使）| 经典方剂著作 |
| [syndrome_reasoning](./presets/tcm/syndrome_reasoning.yaml) | hypergraph | 提取证候推理链条 | 医案、临床经验集 |
| [meridian_graph](./presets/tcm/meridian_graph.yaml) | graph | 绘制穴位-经脉关系 | 针灸学教材 |
| [herb_property](./presets/tcm/herb_property.yaml) | model | 提取药材属性（四气五味）| 本草典籍 |
| [herb_relation](./presets/tcm/herb_relation.yaml) | graph | 绘制药材配伍关系（七情）| 方剂学文献 |

---

### 工业领域

面向工业运维和安全的模板。

| 模板 | 类型 | 用途 | 适用文档 |
|------|------|------|----------|
| [operation_flow](./presets/industry/operation_flow.yaml) | graph | 提取操作步骤和结果 | SOP 操作手册、设备规程 |
| [safety_control](./presets/industry/safety_control.yaml) | graph | 绘制危险源-风险-控制关系 | 安全管理手册 |
| [failure_case](./presets/industry/failure_case.yaml) | graph | 提取故障现象-原因-措施 | 故障分析报告 |
| [equipment_topology](./presets/industry/equipment_topology.yaml) | graph | 绘制设备层级和连接 | 设备手册 |
| [emergency_response](./presets/industry/emergency_response.yaml) | graph | 绘制应急场景和响应 | 应急预案 |

---

### 法律领域

面向法律文档和合规的模板。

| 模板 | 类型 | 用途 | 适用文档 |
|------|------|------|----------|
| [contract_obligation](./presets/legal/contract_obligation.yaml) | hypergraph | 提取当事人-义务关系 | 服务合同、采购合同 |
| [case_fact_timeline](./presets/legal/case_fact_timeline.yaml) | temporal_graph | 构建案件事实时间线 | 判决书 |
| [case_citation](./presets/legal/case_citation.yaml) | graph | 提取判例引用关系 | 法律意见书、判例汇编 |
| [compliance_list](./presets/legal/compliance_list.yaml) | list | 结构化合规要求清单 | 合规手册、审计报告 |
| [defined_term_set](./presets/legal/defined_term_set.yaml) | set | 编目定义术语 | 合同、法律意见书 |

---

## 基础模板参考

基础模板提供抽取的Foundation模式。可直接使用或扩展以满足自定义需求。

### 记录类型模式

| 模式 | Schema | 适用场景 |
|------|--------|----------|
| 键值对 | model | 信息卡、档案 |
| 序列项 | list | 排名、序列 |
| 唯一项 | set | 实体注册表 |

### 图类型模式

| 模式 | Schema | 适用场景 |
|------|--------|----------|
| 二元关系 | graph | 简单实体关系 |
| 多元关系 | hypergraph | 复杂事件、群体关系 |
| 时间锚定关系 | temporal_graph | 历史、时间线 |
| 位置锚定关系 | spatial_graph | 地图、区域 |
| 时间+位置关系 | spatio_temporal_graph | 路线、事件 |

---

## 自定义模板

### 创建自定义模板

自定义模板是一个独立的 YAML 文件，可以放在任意位置。

### YAML模板结构

```yaml
language: [zh, en]

name: my_custom_template
type: graph
tags: [custom]

description:
  zh: '我的自定义模板'
  en: 'My custom template'

output:
  description:
    zh: '输出描述'
    en: 'Output description'
  entities:
    fields:
      - name: name
        type: str
        description:
          zh: '实体名称'
          en: 'Entity name'
  relations:
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str

guideline:
  target:
    zh: '你是一位...'
    en: 'You are an...'
  rules_for_entities:
    - '...'
  rules_for_relations:
    - '...'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
```

### 使用自定义模板

```python
from hyperknowledge.utils.template_engine import Template
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

# 使用文件路径加载自定义模板
template = Template.create(
    "/path/to/my_template.yaml",  # 模板文件路径
    "zh",  # 语言
    llm,
    embedder,
)

result = template.parse("您的文档文本...")
```

---

## 统计信息

| 领域 | 模板数 | 基础 | 领域专用 |
|------|--------|------|----------|
| general | 13 | 8 | 5 |
| finance | 5 | 0 | 5 |
| medicine | 5 | 0 | 5 |
| tcm | 5 | 0 | 5 |
| industry | 5 | 0 | 5 |
| legal | 5 | 0 | 5 |
| **总计** | **38** | **8** | **30** |

---

## 贡献指南

添加新模板的步骤：
1. 在相应的领域目录下创建 YAML 文件
2. 遵循模板结构规范
3. 包含中英文描述
4. 使用示例文档进行测试

---

## 许可证

作为 Hyper-Knowledge 项目的一部分。参见 [根目录许可证](../../LICENSE)。
