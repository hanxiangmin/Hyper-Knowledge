# hk show

使用 OntoSight 交互式查看器可视化知识图谱。

---

## 概要

```bash
hk show KA_PATH
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 知识库目录的路径 |

---

## 描述

在默认 Web 浏览器中打开知识图谱的交互式可视化。可视化显示：

- **节点** — 实体、概念或项目（按类型着色）
- **边** — 节点之间的关系
- **标签** — 点击节点/边查看详情

---

## 示例

### 基本用法

```bash
hk show ./output/
```

### 提取后

```bash
# 先提取
hk parse sushi.md -t general/biography_graph -o ./sushi_kb/ -l zh

# 然后可视化
hk show ./sushi_kb/
```

### 增量更新后

```bash
# 添加更多内容
hk feed ./sushi_kb/ additional_info.md

# 可视化更新后的图谱
hk show ./sushi_kb/
```

---

## 可视化功能

OntoSight 查看器提供：

### 交互控制

- **缩放** — 鼠标滚轮或捏合手势
- **平移** — 点击并拖动背景
- **选择** — 点击节点/边查看详情
- **筛选** — 显示/隐藏节点类型

### 节点显示

- 大小表示重要性（可配置）
- 颜色表示实体类型
- 标签显示实体名称

### 边显示

- 粗细表示关系强度
- 标签显示关系类型
- 方向显示关系流向

---

## 支持的自动类型

可视化适用于所有基于图谱的自动类型：

| 自动类型 | 可视化 |
|-----------|--------------|
| `AutoGraph` | ✓ 完整图谱可视化 |
| `AutoHypergraph` | ✓ 带多节点边的超图 |
| `AutoTemporalGraph` | ✓ 带时间信息的图谱 |
| `AutoSpatialGraph` | ✓ 带空间信息的图谱 |
| `AutoSpatioTemporalGraph` | ✓ 完整上下文可视化 |
| `AutoList` | ✓ 列表视图 |
| `AutoSet` | ✓ 集合视图 |
| `AutoModel` | ✓ 结构化视图 |

---

## 故障排除

### "浏览器未打开"

会打印可视化 URL。手动打开：

```
http://localhost:xxxx
```

### "显示空图谱"

检查提取是否成功：

```bash
hk info ./ka/
# 应该显示 Nodes > 0 和 Edges > 0
```

### "加载可视化出错"

确保知识库有效：

```bash
# 检查数据文件存在
ls ./ka/data.json

# 尝试重新加载
hk show ./ka/
```

---

## 另请参见

- [`hk parse`](parse.md) — 提取知识
- [`hk feed`](feed.md) — 增量添加文档
- [`hk info`](info.md) — 查看知识库统计信息
