# Hyper-Knowledge 设计指南

Hyper-Knowledge YAML 抽取模板的完整设计指南。

> English version: [DESIGN_GUIDE.md](./DESIGN_GUIDE.md)

---

## 目录

- [快速参考](#快速参考)
- [第一部分：设计工作流](#第一部分设计工作流)
- [第二部分：类型设计指南](#第二部分类型设计指南)
- [第三部分：字段参考](#第三部分字段参考)
- [第四部分：质量保证](#第四部分质量保证)
- [第五部分：验证指南](#第五部分验证指南)

---

## 快速参考

### 类型选择决策树

```
需要建模关系吗？
├─ 否 → 记录类型
│   ├─ 单个对象 → model
│   ├─ 有序列表 → list
│   └─ 去重集合 → set
└─ 是 → 图类型
    ├─ 二元关系 (A→B) → graph
    └─ 多元关系 (A+B+C→D)
        ├─ 扁平列表 → hypergraph (简单)
        └─ 角色分组 → hypergraph (嵌套)

图类型扩展：
├─ + 时间维度 → temporal_graph
├─ + 空间维度 → spatial_graph
└─ + 两者 → spatio_temporal_graph
```

### 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 模板名称 | CamelCase | `EarningsSummary` |
| 字段名称 | snake_case | `company_name` |
| 关系类型字段 | `type` | (不是 `relation_type`) |
| 时间字段 | `time` | (不是 `event_date`) |
| 标签 | 小写 | `finance, investor` |

### 字段数量指南

| 组件 | 最大字段数 | 优先级 |
|------|-----------|--------|
| 实体字段 | 5 | 必要 → 重要 → 可选 |
| 关系字段 | 5 | 必要 → 重要 → 可选 |
| 列表字段 | 3 | 必要 → 重要 → 可选 |

---

## 第一部分：设计工作流

### 工作流概览

```
用户输入 → brainstorm → designer → optimizer → validator
               ↓            ↓          ↓          ↓
           类型选择      YAML生成    自动修复     检查
```

### 步骤 1: Brainstorm

明确需求，确定抽取类型。

**讨论问题：**
- 输入来源是什么？
- 需要抽取什么？
- 需要哪些关键字段？
- 实体类型和粒度？
- 关系类型（预定义还是自定义）？

**输出：** 包含类型、字段和备注的设计草稿。

### 步骤 2: Designer

根据设计草稿生成 YAML。

**输出模板：**

```yaml
language: [zh, en]

name: TemplateName
type: [type]
tags: [domain]

description:
  zh: '...'
  en: '...'

output:
  description: '...'
  entities:        # 图类型
    description: '...'
    fields: [...]
  fields:         # 记录类型
    - name: field_name
      type: str
      description: '...'

guideline:
  target: '...'
  rules: [...]              # 记录类型
  rules_for_entities: [...] # 图类型
  rules_for_relations: [...] # 图类型

identifiers: {}

display:
  label: '...'
```

### 步骤 3: Optimizer（可选）

自动修复常见问题，应用最佳实践。

**自动修复规则：**
- `relation_type` → `type`
- `event_date` → `time`
- 混合语言 → 分离 zh/en

### 步骤 4: Validator

验证 YAML 正确性。

**验证清单：**
- [ ] language: zh/en
- [ ] name: CamelCase
- [ ] type: 有效的 AutoType
- [ ] tags: 小写数组
- [ ] description: 非空
- [ ] output: 存在
- [ ] guideline: 存在

---

## 第二部分：类型设计指南

### 核心原则：Schema 与 Guideline 分离

**Schema 定义"是什么"，Guideline 定义"如何做好"。**

| Schema 定义 | Guideline 定义 |
|-------------|----------------|
| 字段名称 | 抽取策略 |
| 字段类型 | 质量要求 |
| 字段描述 | 创建条件 |
| 必填/可选 | 常见错误 |

**❌ 错误：** Guideline 重复字段定义
**✅ 正确：** Guideline 解释如何做好抽取

---

### 1. model - 单个结构化对象

**适用场景：** 抽取包含多个字段的单个记录。

**模板：**

```yaml
name: EarningsSummary
type: model
tags: [finance]

output:
  description: '...'
  fields:
    - name: company_name
      type: str
      description: '公司名称'
      required: true
    - name: revenue
      type: str
      description: '营收金额'
      required: false

guideline:
  target: '你是一位财务分析师...'
  rules:
    - '提取与原文一致的精确数字'
    - '遵循原文中的格式'

identifiers: {}

display:
  label: '{company_name}'
```

**设计清单：**
- [ ] 所有字段有明确的语义？
- [ ] 字段类型适当 (str/int/float/list)？
- [ ] 必填/可选设置合理？
- [ ] 默认值安全且有意义？
- [ ] display.label 引用正确字段？
- [ ] Guideline 没有重复字段定义？

---

### 2. list - 有序数组

**适用场景：** 抽取有序项目（排名、序列、项目列表）。

**模板：**

```yaml
name: KeywordList
type: list
tags: [general]

output:
  description: '...'
  fields:
    - name: term
      type: str
      description: '关键词或术语'
    - name: rank
      type: int
      description: '顺序位置'
      required: false

guideline:
  target: '你是一位关键词提取专家...'
  rules:
    - '按出现顺序提取术语'
    - '如有明确排名则保持顺序'

identifiers: {}

display:
  label: '{term}'
```

**设计清单：**
- [ ] 项目结构一致？
- [ ] 顺序有意义且被保留？
- [ ] 没有冗余字段？

---

### 3. set - 去重集合

**适用场景：** 抽取唯一实体（实体注册表、关键词列表）。

**模板：**

```yaml
name: EntityRegistry
type: set
tags: [general]

output:
  description: '...'
  fields:
    - name: name
      type: str
      description: '实体名称'
    - name: category
      type: str
      description: '实体类型'
      required: false

guideline:
  target: '你是一位实体识别专家...'
  rules:
    - '提取所有唯一实体'
    - '全文保持命名一致'

identifiers:
  item_id: name

display:
  label: '{name}'
```

**设计清单：**
- [ ] item_id 能唯一标识记录？
- [ ] 去重规则清晰？
- [ ] 相似的实体被一致处理？

---

### 4. graph - 二元关系

**适用场景：** 建模两个实体之间的关系（A→B）。

**模板：**

```yaml
name: OwnershipGraph
type: graph
tags: [finance]

output:
  description: '...'
  entities:
    description: '组织实体'
    fields:
      - name: name
        type: str
        description: '实体名称'
      - name: type
        type: str
        description: '实体类型'
  relations:
    description: '所有权关系'
    fields:
      - name: source
        type: str
        description: '所有者实体'
      - name: target
        type: str
        description: '被拥有实体'
      - name: type
        type: str
        description: '关系类型'

guideline:
  target: '你是一位知识图谱专家...'
  rules_for_entities:
    - '提取对理解文本有价值的实体'
    - '全文保持命名一致'
  rules_for_relations:
    - '仅在文本明确表达时创建关系'
    - '优先使用文本中出现的关系词'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

**设计清单：**
- [ ] 实体类型覆盖关键概念？
- [ ] 实体粒度适当？
- [ ] 关系类型语义清晰？
- [ ] source/target 引用有效实体？
- [ ] 没有歧义关系？
- [ ] relation_label 不重复 source/target？

---

### 5. hypergraph - 多元关系

**适用场景：** 建模多方参与的复杂关系。

#### 5a. 简单超图（扁平列表）

**适用场景：** 所有参与者角色相同。

```yaml
relations:
  fields:
    - name: event_name
      type: str
      description: '事件或机制名称'
    - name: participants
      type: list
      description: '参与实体列表'
    - name: type
      type: str
      description: '关系类型'
    - name: outcome
      type: str
      description: '结果或结论'
      required: false

identifiers:
  entity_id: name
  relation_id: '{event_name}|{type}'
  relation_members: participants  # 字符串
```

#### 5b. 嵌套超图（语义分组）

**适用场景：** 参与者有明确的语义角色。

```yaml
relations:
  fields:
    - name: event_name
      type: str
      description: '事件名称'
    - name: group_a
      type: list
      description: 'A组参与者（如：攻方）'
    - name: group_b
      type: list
      description: 'B组参与者（如：守方）'
    - name: outcome
      type: str
      description: '结果'
    - name: reasoning
      type: str
      description: '解释说明'
      required: false

identifiers:
  entity_id: name
  relation_id: '{event_name}'
  relation_members: [group_a, group_b]  # 列表
```

**常见分组模式：**

| 场景 | 分组 | 适用场景 |
|------|------|----------|
| 方剂 | sovereigns, ministers, assistants, envoys | 中医方剂 |
| 战役 | attackers, defenders | 军事冲突 |
| 交易 | buyers, sellers, intermediaries | 商业交易 |
| 合同 | parties, witnesses | 法律文档 |

**设计清单：**
- [ ] 有多少语义分组？
- [ ] 分组名称是什么？
- [ ] 是否应该使用嵌套分组而非角色字段？
- [ ] 参与者数量合理？
- [ ] 结果定义清晰？

---

### 6. temporal_graph - 带时间的关系

**适用场景：** 关系具有时间属性。

**添加到 graph：**

```yaml
relations:
  fields:
    - name: source
      type: str
    - name: target
      type: str
    - name: type
      type: str
    - name: time
      type: str
      description: '关系发生时间'
      required: false

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time

guideline:
  rules_for_time:
    - '观察时间点：{observation_time}'
    - '绝对时间：保持原样（如 2024-01-01）'
    - '相对时间：转换为绝对时间'
    - '模糊时间：留空，不猜测'
```

**设计清单：**
- [ ] 时间是边的属性，不是节点属性？
- [ ] 格式处理规则清晰？
- [ ] 相对时间转换规则已指定？

---

### 7. spatial_graph - 带位置的关系

**添加到 graph：**

```yaml
relations:
  fields:
    - name: source
      type: str
    - name: target
      type: str
    - name: type
      type: str
    - name: location
      type: str
      description: '关系发生地点'
      required: false

identifiers:
  location_field: location

guideline:
  rules_for_location:
    - '观察位置：{observation_location}'
    - '结构化地点：保持原样'
    - '模糊地点：使用观察位置'
```

---

### 8. spatio_temporal_graph - 带时间和位置的关系

**综合 temporal_graph 和 spatial_graph。**

```yaml
identifiers:
  time_field: time
  location_field: location
```

---

## 第三部分：字段参考

### 常用实体字段

```yaml
entities:
  description: '实体定义'
  fields:
    - name: name
      type: str
      description: '实体名称（唯一标识）'
    - name: type
      type: str
      description: '实体类型/类别'
    - name: description
      type: str
      description: '简要描述'
      required: false
```

### 常用关系字段

```yaml
relations:
  description: '关系定义'
  fields:
    - name: source
      type: str
      description: '源实体'
    - name: target
      type: str
      description: '目标实体'
    - name: type
      type: str
      description: '关系类型'
```

### Identifiers 配置

#### graph（二元关系）

```yaml
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target
```

#### hypergraph（简单）

```yaml
identifiers:
  relation_members: participants  # 字符串
```

#### hypergraph（嵌套）

```yaml
identifiers:
  relation_members: [group_a, group_b]  # 列表
```

### Display 配置

| 类型 | entity_label | relation_label |
|------|--------------|----------------|
| graph | `{name} ({type})` | `{type}` |
| hypergraph | `{name}` | `{event_name}` 或 `{outcome}` |
| temporal | `{name} ({type})` | `{type}@{time}` |
| spatio_temporal | `{name} ({type})` | `{type}@{location}({time})` |

**长度指南：**
- entity_label：5-20 个字符
- relation_label：10-30 个字符

---

## 第四部分：质量保证

### 多语言规则

**核心原则：** 每个语言字段应使用该语言的术语。

| 字段 | 规则 | 示例 |
|------|------|------|
| `zh` | 纯中文 | `类型：实体` |
| `en` | 纯英文 | `Type: entity` |

**禁止的模式：**
- ❌ `zh` 包含英文术语：`entity(实体)`
- ❌ `en` 包含中文字符：`类型`

**翻译对照：**

| 中文 | 英文 |
|------|------|
| 实体 | entity |
| 抽象概念 | abstract |
| 过程 | process |
| 关系 | relation |
| 高/中/低 | high/medium/low |

---

### 字段数量优化

**每个组件最大字段数：** 5

| 优先级 | 说明 |
|--------|------|
| 必要 | source, target, participants |
| 重要 | type, time, location |
| 可选 | description, metadata |

**简化策略：** 如果字段 > 5，考虑：
- 拆分为多个模板
- 将可选字段移到 description
- 删除冗余字段

---

### 自动修复模式

| 问题 | 修复 |
|------|------|
| `relation_type` | → `type` |
| `event_date` | → `time` |
| `entity_type` | → `type` |
| `zh` 中混合语言 | 提取 `entity(...)` → `实体` |
| `en` 中有中文字符 | 翻译为英文 |

---

## 第五部分：验证指南

### 验证清单

#### 所有类型
- [ ] language: zh/en
- [ ] name: CamelCase
- [ ] type: 有效的 AutoType
- [ ] tags: 小写数组
- [ ] description: 非空
- [ ] output: 存在
- [ ] guideline: 存在

#### 图类型
- [ ] output.entities: 存在
- [ ] output.relations: 存在
- [ ] identifiers.entity_id: 存在
- [ ] identifiers.relation_id: 存在
- [ ] identifiers.relation_members: 已配置

#### 超图
- [ ] relation_members 是字符串或列表
- [ ] 如果是列表：所有字段类型为 list

#### 时空类型
- [ ] identifiers.time_field: 已配置（temporal）
- [ ] identifiers.location_field: 已配置（spatial）

### 常见错误

| 错误 | 修复 |
|------|------|
| 缺少必填字段 | 添加字段 |
| 类型值无效 | 使用有效的 AutoType |
| 混合语言 | 分离 zh/en 内容 |
| 字段数量 >5 | 简化或拆分 |

---

## 附录

### AutoType 快速参考

```
需要单个对象 → model
需要列表 → list
需要去重 → set
需要二元关系 → graph
需要多方关系 → hypergraph
需要时间 → temporal_graph
需要位置 → spatial_graph
需要两者 → spatio_temporal_graph
```

### 模板目录结构

```
templates/
├── presets/
│   ├── general/        # 13 个模板（8 个基础 + 5 个领域专用）
│   ├── finance/        # 5 个模板
│   ├── medicine/       # 5 个模板
│   ├── tcm/            # 5 个模板
│   ├── industry/       # 5 个模板
│   └── legal/          # 5 个模板
├── DESIGN_GUIDE.md        # 本指南（英文）
├── DESIGN_GUIDE_zh.md    # 本指南（中文）
├── README.md              # 模板目录
└── README_ZH.md          # 中文目录
```

---

## 许可证

作为 Hyper-Knowledge 项目的一部分。参见[根目录许可证](../../LICENSE)。
