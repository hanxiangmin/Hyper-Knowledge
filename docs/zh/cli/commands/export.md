# hk export obsidian

将知识摘要导出为 [Obsidian](https://obsidian.md) 知识库——一个由 `[[双向链接]]` 关联的 Markdown 笔记文件夹。

`export` 是一个命令组，`obsidian` 是格式（后续可能会增加更多格式）。

---

## 用法

```bash
hk export obsidian KA_PATH -o VAULT_PATH [选项]
```

## 参数

| 参数 | 说明 |
|----------|-------------|
| `KA_PATH` | 知识摘要目录路径（由 `hk parse` 生成） |

## 选项

| 选项 | 别名 | 默认值 | 说明 |
|--------|-------|---------|-------------|
| `--output` | `-o` | *(必填)* | 输出知识库目录 |
| `--name` | | 输出目录名 | 索引笔记使用的知识库名称 |
| `--no-index` | | 关闭 | 跳过生成索引 / 目录笔记 |
| `--force` | `-f` | 关闭 | 写入已存在且非空的目录 |

---

## 说明

`hk export obsidian` 将提取出的知识图谱转换为一个可在 Obsidian 图谱视图中浏览的知识库：

- **每个节点 → 一篇 Markdown 笔记。** 节点字段写入 YAML front-matter，随后是 `# 标题` 以及（如有）描述。
- **每条边 → 一个 `[[双向链接]]`。** 关系渲染在源笔记的 `## Relationships` 区块中，包含关系标签与描述。
- **索引笔记**（以 `--name` 命名）按类型分组列出所有笔记，作为知识库目录。

导出器无额外依赖，生成的是纯 Markdown，因此结果是一个标准 Obsidian 知识库：在 Obsidian 中用 **"Open folder as vault"** 打开该文件夹，或之后用 [`hk parse`](parse.md) 重新导入。

---

## 示例

### 基本用法

```bash
# 先提取，再导出
hk parse tesla.md -t general/biography_graph -o ./tesla_kb/ -l zh
hk export obsidian ./tesla_kb/ -o ./tesla_vault/
```

### 自定义知识库名称

```bash
hk export obsidian ./tesla_kb/ -o ./tesla_vault/ --name "Tesla 知识库"
```

### 覆盖已存在目录

```bash
hk export obsidian ./tesla_kb/ -o ./tesla_vault/ --force
```

### 不生成索引笔记

```bash
hk export obsidian ./tesla_kb/ -o ./tesla_vault/ --no-index
```

---

## 输出结构

```
tesla_vault/
├── Tesla 知识库.md          # 索引（按类型分组）
├── Nikola Tesla.md
├── Alternating Current.md
└── ...
```

一篇笔记的样子：

```markdown
---
name: Nikola Tesla
type: Person
description: "Serbian-American inventor and electrical engineer"
---

# Nikola Tesla

Serbian-American inventor and electrical engineer

## Relationships

- **developed** → [[Alternating Current]] — Pioneered the AC system.
- **rivaled** → [[Thomas Edison]] — The War of the Currents.
```

说明：

- 文件名会针对 Obsidian / 文件系统做净化；原始 id/标题保留为 front-matter 的 `alias`，双向链接使用 `[[stem|display]]` 形式以确保始终可解析。
- 同名冲突会自动去重（例如 `Tesla coil (2)`）。

---

## 支持的 Auto-Type

导出支持图谱家族：

| Auto-Type | 导出 |
|-----------|--------|
| `AutoGraph` | ✓ 每个节点一篇笔记，边为双向链接 |
| `AutoHypergraph` | ✓ N 元边链接所有成员 |
| `AutoTemporalGraph` | ✓（继承自 `AutoGraph`） |
| `AutoSpatialGraph` | ✓（继承自 `AutoGraph`） |
| `AutoSpatioTemporalGraph` | ✓（继承自 `AutoGraph`） |

非图谱类型（`AutoList`、`AutoSet`、`AutoModel`）不支持；命令会给出明确的错误提示。

---

## Python API

图谱类 Auto-Type 也提供同样的能力：

```python
ka.export_obsidian("./tesla_vault/", vault_name="Tesla KB", overwrite=True)
```

---

## 另请参阅

- [`hk parse`](parse.md) — 提取知识（也可导入已有的知识库文件夹）
- [`hk show`](show.md) — 使用 OntoSight 可视化图谱
- [`hk info`](info.md) — 查看知识摘要统计
