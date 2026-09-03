# hk info

显示知识库的信息和统计信息。

---

## 概要

```bash
hk info KA_PATH
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 知识库目录的路径 |

---

## 描述

显示知识库的元数据和统计信息：

- **路径** — 知识库的位置
- **模板** — 用于提取的模板
- **语言** — 语言代码（en/zh）
- **时间戳** — 创建和最后更新时间
- **统计信息** — 节点数、边数
- **索引状态** — 搜索索引是否已构建

---

## 示例

### 基本用法

```bash
hk info ./output/
```

**输出：**
```
Knowledge Abstract Info

Path          ./output/
Template      general/biography_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:35:22
Nodes         25
Edges         32
Index         Built
```

### 提取后

```bash
hk parse sushi.md -t general/biography_graph -o ./ka/ -l zh
hk info ./ka/
```

### Feed 后

```bash
hk feed ./ka/ more_content.md
hk info ./ka/
# 注意更新的节点/边数和时间戳
```

---

## 输出字段

| 字段 | 描述 |
|-------|-------------|
| `Path` | 知识库的绝对路径 |
| `Template` | 模板标识符（例如 `general/biography_graph`） |
| `Language` | 处理语言（`en` 或 `zh`） |
| `Created` | 初始提取时间戳 |
| `Updated` | 最后修改时间戳 |
| `Nodes` | 实体/项目数量 |
| `Edges` | 关系数量 |
| `Index` | 搜索索引状态（`Built` 或 `Not Built`） |

---

## 用例

### 验证提取

检查提取是否成功：

```bash
hk info ./ka/
# 应该显示 Nodes > 0, Edges > 0
```

### 检查索引状态

在使用搜索或聊天之前：

```bash
hk info ./ka/
# 如果索引显示 "Not Built"，运行：
hk build-index ./ka/
```

### 监控增长

跟踪知识库随时间的增长：

```bash
hk info ./ka/
# 喂养更多文档
hk feed ./ka/ update.md
hk info ./ka/
# 比较节点/边数
```

### 脚本

在自动化脚本中使用：

```bash
#!/bin/bash

if hk info ./ka/ 2>/dev/null; then
    echo "Knowledge base exists"
    hk feed ./ka/ new_doc.md
else
    echo "Creating new knowledge abstract"
    hk parse new_doc.md -t general/biography_graph -o ./ka/ -l zh
fi
```

---

## 故障排除

### "未找到知识库目录"

目录不存在或不包含知识库：

```bash
# 检查目录存在
ls ./ka/

# 应该包含：
# - data.json
# - metadata.json
```

### 元数据缺失

如果元数据损坏，模板/语言显示为 "unknown"：

```bash
hk info ./ka/
# Template: [yellow]unknown[/yellow]
# Language: [yellow]unknown[/yellow]
```

知识库仍然可用，但某些功能可能受限。

---

## 另请参见

- [`hk parse`](parse.md) — 创建知识库
- [`hk feed`](feed.md) — 添加到知识库
- [`hk build-index`](build-index.md) — 构建搜索索引
