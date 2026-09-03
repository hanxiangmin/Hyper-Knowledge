# 中医模板

中医药文本分析。

---

## 概述

中医模板专为从中医文本中提取知识而设计，包括草药、方剂和辨证。

---

## 模板

### herb_property

**类型**：model

**用途**：提取草药属性和特征

**最适合**：
- 本草文献
- 草药数据库
- 处方参考

**字段**：

| 字段 | 类型 | 描述 |
|------|------|------|
| `name` | str | 草药名称（中文/拼音） |
| `properties` | list[str] | 性质（寒、热、温、凉、平） |
| `flavors` | list[str] | 五味（酸、苦、甘、辛、咸） |
| `meridians` | list[str] | 归经 |
| `functions` | list[str] | 主要功效 |
| `indications` | list[str] | 临床应用 |

=== "CLI"

    ```bash
    hk parse herb_text.md -t tcm/herb_property -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/herb_property", "zh")
    herb = ka.parse(huang_qi_text)

    print(f"名称: {herb.data.name}")
    print(f"性质: {', '.join(herb.data.properties)}")
    print(f"功效: {', '.join(herb.data.functions)}")
    ```

---

### formula_composition

**类型**：graph

**用途**：提取草药方剂组成

**最适合**：
- 方剂学
- 处方文本
- 经典文献（伤寒论、金匮要略）

**实体**：
- 草药（药物）
- 方剂
- 病症

**关系**：
- `contains` — 方剂包含草药
- `treats` — 方剂治疗病症
- `modifies` — 加减方关系

=== "CLI"

    ```bash
    hk parse formula_book.md -t tcm/formula_composition -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/formula_composition", "zh")
    result = ka.parse(formula_text)

    print(f"实体数: {len(result.nodes)}")
    print(f"关系数: {len(result.edges)}")

    # 列方剂中的草药
    for edge in result.edges:
        if edge.type == "contains":
            print(f"  - {edge.target}")
    ```

---

### herb_relation

**类型**：graph

**用途**：提取草药间关系

**最适合**：
- 药对参考
- 配伍禁忌文本（十八反、十九畏）
- 组合指南

**关系**：
- `pairs_with` — 常见配对
- `synergizes_with` — 协同作用
- `incompatible_with` — 配伍禁忌

=== "CLI"

    ```bash
    hk parse herb_pairs.md -t tcm/herb_relation -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/herb_relation", "zh")
    result = ka.parse(herb_text)

    print(f"草药数: {len(result.nodes)}")
    for edge in result.edges:
        print(f"{edge.source} {edge.type} {edge.target}")
    ```

---

### meridian_graph

**类型**：graph

**用途**：提取经络路径信息

**最适合**：
- 针灸文本
- 经络学
- 穴位定位参考

**实体**：
- 经脉
- 穴位
- 脏腑

**关系**：
- `connects_to` — 经络连接
- `belongs_to` — 穴位所属经络
- `influences` — 经络与脏腑关系

=== "CLI"

    ```bash
    hk parse acupuncture.md -t tcm/meridian_graph -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/meridian_graph", "zh")
    result = ka.parse(acupuncture_text)

    print(f"经络数: {len(result.nodes)}")
    print(f"连接数: {len(result.edges)}")

    # 可视化经络路径
    result.build_index()
    result.show()
    ```

---

### syndrome_reasoning

**类型**：graph

**用途**：提取辨证逻辑

**最适合**：
- 诊断学文本
- 案例分析
- 辨证指南

**实体**：
- 症状
- 证型
- 病机

**关系**：
- `indicates` — 症状指示证型
- `differentiates_from` — 鉴别诊断
- `leads_to` — 病机演变

=== "CLI"

    ```bash
    hk parse diagnostics.md -t tcm/syndrome_reasoning -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("tcm/syndrome_reasoning", "zh")
    result = ka.parse(diagnostics_text)

    print(f"症状数: {len(result.nodes)}")
    print(f"证型关联: {len(result.edges)}")

    # 探索证型关系
    result.build_index()
    result.show()
    ```

---

## 用例

### 草药数据库构建

```python
from hyperknowledge import Template

ka = Template.create("tcm/herb_property", "zh")
herb_db = {}

for herb_file in herb_files:
    herb = ka.parse(herb_file.read_text())
    herb_db[herb.data.name] = herb.data

# 按功效查询
for name, data in herb_db.items():
    if "补气" in data.functions:
        print(f"{name}: 补气草药")
```

### 方剂分析

```python
ka = Template.create("tcm/formula_composition", "zh")
formula = ka.parse(si_jun_zi_tang_text)

# 列出草药
print("方剂组成:")
for relation in formula.data.relations:
    if relation.type == "contains":
        print(f"  - {relation.target}")
```

### 证型研究

```python
ka = Template.create("tcm/syndrome_reasoning", "zh")
syndromes = ka.parse(diagnostics_text)

# 查找症状指示的证型
symptom = "舌淡苔白"
related = [
    r for r in syndromes.data.relations
    if r.source == symptom and r.type == "indicates"
]

for r in related:
    print(f"{symptom} 指示 {r.target}")
```

---

## 提示

1. **使用中文语言（`-l zh`）** — 更好地从中医文本中提取
2. **herb_property 用于本草** — 构建草药数据库
3. **formula_composition 用于方剂学** — 研究经典方剂
4. **meridian_graph 用于针灸** — 映射经络路径

---

## 参见

- [模板概览](overview.md)
- [医疗模板](medicine.md)
