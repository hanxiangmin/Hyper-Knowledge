# 工业模板

工业文档和操作分析。

---

## 概述

工业模板专为从工业文档中提取信息而设计，包括设备规格、安全程序和操作流程。

---

## 模板

### equipment_topology

**类型**：graph

**用途**：提取设备连接和拓扑

**最适合**：
- 系统图
- P&ID（管道和仪表图）
- 设备手册
- 网络布局

**实体**：
- 设备（泵、阀门、储罐等）
- 传感器
- 控制系统

**关系**：
- `connected_to` — 物理连接
- `controlled_by` — 控制关系
- `monitors` — 监控关系

=== "CLI"

    ```bash
    hk parse system_diagram.md -t industry/equipment_topology -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("industry/equipment_topology", "zh")
    result = ka.parse(pandid_description)

    # 构建索引以支持可视化中的交互式搜索/对话
    result.build_index()

    result.show()  # 显示带有交互功能的设备网络
    ```

---

### safety_control

**类型**：graph

**用途**：提取安全控制系统

**最适合**：
- 安全手册
- HAZOP 研究
- 安全系统设计
- 应急程序

**实体**：
- 安全功能
- 危险
- 保护措施
- 传感器
- 执行器

**关系**：
- `protects_against` — 保护措施与危险的关系
- `triggers` — 传感器与动作的关系
- `implements` — 系统与功能的关系

=== "CLI"

    ```bash
    hk parse safety_manual.md -t industry/safety_control -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("industry/safety_control", "zh")
    result = ka.parse(safety_text)

    print(f"安全功能数: {len(result.nodes)}")
    print(f"保护措施数: {len(result.edges)}")

    # 可视化安全系统
    result.build_index()
    result.show()
    ```

---

### operation_flow

**类型**：graph

**用途**：提取操作程序

**最适合**：
- 操作程序（SOP）
- 批记录
- 流程描述
- 工作指导

**特性**：
- 步骤序列
- 决策点
- 并行操作
- 依赖关系

=== "CLI"

    ```bash
    hk parse sop.md -t industry/operation_flow -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("industry/operation_flow", "zh")
    result = ka.parse(sop_text)

    print(f"步骤数: {len(result.nodes)}")
    print(f"流程连接数: {len(result.edges)}")

    # 可视化操作流程
    result.build_index()
    result.show()
    ```

---

### emergency_response

**类型**：graph

**用途**：提取应急响应程序

**最适合**：
- 应急响应计划
- 事件响应指南
- 危机管理协议

**实体**：
- 紧急情况类型
- 响应动作
- 责任方
- 资源

**关系**：
- `responds_to` — 动作与紧急情况的关系
- `requires` — 资源需求
- `notifies` — 通知链

=== "CLI"

    ```bash
    hk parse emergency_plan.md -t industry/emergency_response -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("industry/emergency_response", "zh")
    result = ka.parse(emergency_text)

    print(f"紧急情况类型数: {len(result.nodes)}")
    print(f"响应动作数: {len(result.edges)}")

    # 可视化应急响应计划
    result.build_index()
    result.show()
    ```

---

### failure_case

**类型**：temporal_graph

**用途**：提取故障分析案例

**最适合**：
- 根本原因分析报告
- 事件调查
- 故障模式文档

**特性**：
- 事件时间线
- 促成因素
- 根本原因
- 纠正措施

=== "CLI"

    ```bash
    hk parse incident_report.md -t industry/failure_case -l zh
    ```

=== "Python"

    ```python
    ka = Template.create("industry/failure_case", "zh")
    result = ka.parse(incident_text)

    print(f"事件数: {len(result.nodes)}")
    for edge in result.edges:
        if hasattr(edge, 'time'):
            print(f"  {edge.time}: {edge.source} -> {edge.target}")

    # 可视化故障时间线
    result.build_index()
    result.show()
    ```

---

## 用例

### 系统文档

```python
from hyperknowledge import Template

ka = Template.create("industry/equipment_topology", "zh")
system = ka.parse(pandid_description)

# 查找所有泵
pumps = [e for e in system.data.entities if "pump" in e.type.lower()]

for pump in pumps:
    # 查找连接
    connections = [
        r for r in system.data.relations
        if r.source == pump.name or r.target == pump.name
    ]
    print(f"{pump.name}: {len(connections)} 个连接")
```

### 安全分析

```python
ka = Template.create("industry/safety_control", "zh")
safety = ka.parse(hazop_report)

# 将危险映射到保护措施
hazards = [e for e in safety.data.entities if e.type == "hazard"]

for hazard in hazards:
    safeguards = [
        r.source for r in safety.data.relations
        if r.target == hazard.name and r.type == "protects_against"
    ]
    print(f"{hazard.name}:")
    for sg in safeguards:
        print(f"  受保护: {sg}")
```

### 程序文档

```python
ka = Template.create("industry/operation_flow", "zh")
procedure = ka.parse(sop_document)

# 构建索引以支持交互式可视化
procedure.build_index()

# 可视化工作流（支持搜索/对话功能）
procedure.show()

# 搜索特定步骤
results = procedure.search("启动序列")
```

---

## 提示

1. **equipment_topology 用于系统设计** — 记录设备网络
2. **safety_control 用于 HAZOP** — 提取安全系统
3. **operation_flow 用于 SOP** — 记录程序
4. **failure_case 用于 RCA** — 分析事件

---

## 参见

- [模板概览](overview.md)
- [通用模板](general.md)
