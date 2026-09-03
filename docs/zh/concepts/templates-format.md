# 模板格式

YAML 模板结构的完整参考。

---

## 概述

模板是定义以下内容的 YAML 文件：
- **输出 schema** — 要提取什么
- **提示** — 如何指导 LLM
- **指南** — 提取规则
- **配置** — 显示和标识符

---

## 模板结构

```yaml
language: [zh, en]           # 支持的语言

name: template_name          # 模板标识符
type: graph                  # Auto-Type
tags: [domain, category]     # 分类标签

description:                 # 人类可读的描述
  zh: "中文描述"
  en: "English description"

output:                      # 输出 schema 定义
  description:
    zh: "输出描述"
    en: "Output description"
  entities:                  # 实体 schema
    description:
      zh: "实体描述"
      en: "Entity description"
    fields:
      - name: field_name
        type: str
        description:
          zh: "字段描述"
          en: "Field description"
        required: true
  relations:                 # 关系 schema（用于图谱）
    # 与实体相同的结构

guideline:                   # LLM 指令
  target:
    zh: "提取目标"
    en: "Extraction target"
  rules_for_entities:
    zh: ["规则1", "规则2"]
    en: ["Rule 1", "Rule 2"]
  rules_for_relations:
    zh: ["规则1"]
    en: ["Rule 1"]

identifiers:                 # ID 生成规则
  entity_id: name            # 用作实体 ID 的字段
  relation_id: "{source}|{type}|{target}"  # 关系 ID 格式
  relation_members:
    source: source
    target: target

display:                     # 可视化设置
  entity_label: "{name} ({type})"
  relation_label: "{type}"
```

---

## 字段类型

| 类型 | 描述 | 示例 |
|------|-------------|---------|
| `str` | 字符串 | `"Hello"` |
| `int` | 整数 | `42` |
| `float` | 浮点数 | `3.14` |
| `bool` | 布尔值 | `true` |
| `list[str]` | 字符串列表 | `["a", "b"]` |
| `datetime` | 日期/时间 | `"2024-01-01"` |

---

## 完整示例

```yaml
language: [zh, en]

name: biography_graph
type: temporal_graph
tags: [general, biography, life, events, timeline]

description:
  zh: '传记图模板 - 从人物传记、回忆录、年谱中提取实体和关系'
  en: 'Biography Graph Template - Extract entities and relationships from biographies'

output:
  description:
    zh: '人物传记中的实体和关系网络'
    en: "Entity and relationship network from biographies"
  
  entities:
    description:
      zh: '传记中的实体'
      en: 'Entities in the biography'
    fields:
      - name: name
        type: str
        description:
          zh: '实体名称'
          en: 'Entity name'
        required: true
      
      - name: type
        type: str
        description:
          zh: '实体类型：人物、地点、组织、作品、事件、成就等'
          en: 'Entity type: person, location, organization, work, event, achievement'
        required: true
      
      - name: description
        type: str
        description:
          zh: '实体描述'
          en: 'Entity description'
        required: false
  
  relations:
    description:
      zh: '实体之间的关系'
      en: 'Relationships between entities'
    fields:
      - name: source
        type: str
        description:
          zh: '关系起点实体'
          en: 'Source entity'
        required: true
      
      - name: target
        type: str
        description:
          zh: '关系终点实体'
          en: 'Target entity'
        required: true
      
      - name: type
        type: str
        description:
          zh: '关系类型'
          en: 'Relation type'
        required: true
      
      - name: time
        type: str
        description:
          zh: '关系对应的时间'
          en: 'Time associated with the relation'
        required: false

guideline:
  target:
    zh: '你是一位专业的传记分析师...'
    en: 'You are a professional biography analyst...'
  
  rules_for_entities:
    zh:
      - '提取传记主人公作为核心实体'
      - '同一实体在全文中保持命名一致'
    en:
      - 'Extract the biographical subject as the core entity'
      - 'Maintain consistent naming for the same entity'
  
  rules_for_relations:
    zh:
      - '仅在文本明确表达两个实体之间存在关系时创建关系'
    en:
      - 'Create relationships only when explicitly expressed'
  
  rules_for_time:
    zh:
      - '绝对日期：保持原文格式'
      - '相对时间：转换为绝对时间'
    en:
      - 'Absolute dates: Keep as-is'
      - 'Relative time: Convert to absolute'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target
  time_field: time

display:
  entity_label: '{name}'
  relation_label: '{type}'
```

---

## Auto-Type 特定部分

### 列表/集合

```yaml
output:
  items:                       # 而不是 entities/relations
    description:
      zh: "列表项"
      en: "List items"
    fields:
      - name: value
        type: str
```

### 模型

```yaml
output:
  fields:                      # 直接字段（不是 entities）
    - name: company_name
      type: str
    - name: revenue
      type: float
```

### 时序图谱

```yaml
guideline:
  rules_for_time:              # 时间提取规则
    zh: ["规则1", "规则2"]
    en: ["Rule 1", "Rule 2"]

identifiers:
  time_field: time             # 包含时间的字段
```

### 空间图谱

```yaml
output:
  entities:
    fields:
      - name: location         # 位置字段
        type: str
      - name: coordinates      # 可选坐标
        type: str

guideline:
  rules_for_location:          # 位置提取规则
    zh: ["规则1"]
    en: ["Rule 1"]
```

---

## 模板变量

在指南中使用占位符：

```yaml
guideline:
  target:
    zh: '观察时间基准：{observation_time}'
    en: 'Observation time baseline: {observation_time}'
```

在运行时传递：

```python
ka = Template.create(
    "template_name",
    "en",
    observation_time="2024-01-01"
)
```

---

## 验证

模板验证以下内容：
- 必填字段存在
- 类型定义有效
- 语言代码支持
- Schema 一致性

---

## 最佳实践

1. **清晰的描述** — 帮助用户选择正确的模板
2. **具体的规则** — 指导 LLM 更好地提取
3. **一致的命名** — 使用清晰、一致的字段名
4. **双语支持** — 尽可能提供中英文
5. **必填与可选** — 适当标记字段

---

## 另请参见

- [模板库](../templates/index.md)
- [创建自定义模板](../python/guides/custom-templates.md)
- [自动类型](autotypes.md)
