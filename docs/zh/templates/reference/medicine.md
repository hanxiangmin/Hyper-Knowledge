# 医疗模板

医疗文本分析和提取。

---

## 概述

医疗模板专为从医疗文本中提取临床信息而设计。

**免责声明**：这些模板仅用于研究和分析目的。未经专业审查不得用于临床决策。

---

## 模板

### anatomy_graph

**类型**：graph

**用途**：提取解剖结构和关系

**最适合**：
- 解剖学教科书
- 手术报告
- 医学教育材料

**实体**：
- 身体部位
- 器官
- 系统
- 结构

**关系**：
- `part_of` — 解剖层次
- `connected_to` — 结构连接
- `supplies` — 血液/神经供应

=== "CLI"

    ```bash
    hk parse anatomy.md -t medicine/anatomy_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/anatomy_graph", "zh")
    result = ka.parse(anatomy_text)

    print(f"结构数: {len(result.nodes)}")
    print(f"关系数: {len(result.edges)}")

    # 构建索引用于交互式探索
    result.build_index()
    result.show()
    ```

---

### discharge_instruction

**类型**：model

**用途**：提取出院摘要信息

**最适合**：
- 出院摘要
- 转院记录
- 就诊后总结

**字段**：

| 字段 | 类型 | 描述 |
|------|------|------|
| `diagnosis` | str | 主要诊断 |
| `procedures` | list[str] | 执行的程序 |
| `medications` | list[str] | 处方药物 |
| `follow_up` | str | 随访指导 |
| `warnings` | list[str] | 警告信号 |

=== "CLI"

    ```bash
    hk parse discharge.md -t medicine/discharge_instruction -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/discharge_instruction", "zh")
    summary = ka.parse(discharge_text)

    print(f"诊断: {summary.data.diagnosis}")
    print(f"随访: {summary.data.follow_up}")
    ```

---

### drug_interaction

**类型**：graph

**用途**：提取药物相互作用和关系

**最适合**：
- 药物数据库
- 药房参考
- 药物重整

**实体**：
- 药物
- 药物类别
- 作用

**关系**：
- `interacts_with` — 药物相互作用
- `contraindicated_with` — 禁忌
- `synergizes_with` — 协同作用

=== "CLI"

    ```bash
    hk parse drug_ref.md -t medicine/drug_interaction -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/drug_interaction", "zh")
    result = ka.parse(drug_text)

    print(f"药物数: {len(result.nodes)}")
    for relation in result.edges:
        print(f"{relation.source} {relation.type} {relation.target}")
    ```

---

### hospital_timeline

**类型**：temporal_graph

**用途**：提取住院时间线

**最适合**：
- 住院病程记录
- 病程记录
- 转院摘要

**特性**：
- 入院/出院日期
- 程序和事件
- 时间线可视化

=== "CLI"

    ```bash
    hk parse hospital_notes.md -t medicine/hospital_timeline -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/hospital_timeline", "zh")
    result = ka.parse(notes_text)

    print(f"事件数: {len(result.nodes)}")
    for edge in result.edges:
        if hasattr(edge, 'time'):
            print(f"  {edge.time}: {edge.source} -> {edge.target}")

    # 可视化时间线
    result.build_index()
    result.show()
    ```

---

### treatment_map

**类型**：graph

**用途**：提取治疗方案和路径

**最适合**：
- 治疗指南
- 护理路径
- 方案文档

=== "CLI"

    ```bash
    hk parse protocol.md -t medicine/treatment_map -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("medicine/treatment_map", "zh")
    result = ka.parse(protocol_text)

    print(f"步骤数: {len(result.nodes)}")
    print(f"流程关系: {len(result.edges)}")

    # 可视化治疗路径
    result.build_index()
    result.show()
    ```

---

## 用例

### 出院摘要分析

```python
from hyperknowledge import Template

ka = Template.create("medicine/discharge_instruction", "zh")
discharges = []

for file in discharge_files:
    summary = ka.parse(file.read_text())
    discharges.append(summary.data)

# 分析常见诊断
from collections import Counter
diagnoses = Counter(d.diagnosis for d in discharges)
print(diagnoses.most_common(10))
```

### 药物相互作用网络

```python
ka = Template.create("medicine/drug_interaction", "zh")
network = ka.parse(drug_database)

# 查找特定药物的相互作用
drug = "华法林"
interactions = [
    r for r in network.data.relations
    if r.source == drug or r.target == drug
]

for i in interactions:
    print(f"{i.source} {i.type} {i.target}")
```

### 解剖学教育

```python
ka = Template.create("medicine/anatomy_graph", "zh")
anatomy = ka.parse(textbook_chapter)

# 构建索引以支持交互式可视化
anatomy.build_index()

# 可视化（支持搜索/对话功能）
anatomy.show()

# 搜索
results = anatomy.search("手部神经")
```

---

## 提示

1. **discharge_instruction 用于摘要** — 快速提取关键出院信息
2. **drug_interaction 用于安全** — 构建相互作用检查工具
3. **anatomy_graph 用于教育** — 创建交互式解剖图
4. **hospital_timeline 用于病程** — 跟踪患者就诊过程

---

## 数据隐私

处理医疗数据时：
- 确保符合 HIPAA 要求
- 处理前对数据进行去标识化
- 使用安全环境
- 遵守机构政策

---

## 参见

- [模板概览](overview.md)
- [中医模板](tcm.md)
