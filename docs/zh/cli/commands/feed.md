# hk feed

增量地向现有知识库添加文档。

---

## 概要

```bash
hk feed KA_PATH INPUT [OPTIONS]
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 现有知识库目录的路径 |
| `INPUT` | 输入文件路径或 `-` 表示标准输入 |

## 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--template` | `-t` | 覆盖模板（如果省略则使用元数据） |
| `--lang` | `-l` | 覆盖语言（如果省略则使用元数据） |

---

## 描述

`feed` 命令向现有知识库添加新文档，不会丢失现有数据：

1. **加载现有知识** — 读取当前知识库状态
2. **从新文档提取** — 处理新内容
3. **智能合并** — 合并新旧数据，处理重复
4. **更新元数据** — 记录更新时间戳

这非常适合：
- 随着时间构建知识库
- 向现有文档添加更新
- 组合多个来源的信息

---

## 示例

### 基本用法

```bash
# 初始提取
hk parse sushi.md -t general/biography_graph -o ./sushi_kb/ -l zh

# 添加更多内容
hk feed ./sushi_kb/ more_sushi.md
```

### 喂养多个文档

```bash
hk feed ./ka/ doc1.md
hk feed ./ka/ doc2.md
hk feed ./ka/ doc3.md
```

或使用循环：

```bash
for file in updates/*.md; do
    hk feed ./ka/ "$file"
done
```

### 从标准输入

```bash
cat new_content.md | hk feed ./ka/ -
```

---

## 合并行为

合并过程处理：

| 场景 | 行为 |
|----------|----------|
| 相同实体 | 合并，描述组合 |
| 相同关系 | 使用最新信息更新 |
| 新实体 | 添加到知识库 |
| 新关系 | 添加连接现有/新实体 |

---

## 工作流程示例

### 构建研究知识库

```bash
# 第 1 天：初始论文
hk parse paper_v1.md -t general/concept_graph -o ./research_kb/ -l zh
hk show ./research_kb/

# 第 7 天：更新版本
hk feed ./research_kb/ paper_v2.md
hk show ./research_kb/

# 第 14 天：相关工作
hk feed ./research_kb/ related_work.md
hk build-index ./research_kb/
hk talk ./research_kb/ -q "所有论文中的关键概念是什么？"
```

### 增量传记

```bash
# 从早年生活开始
hk parse early_life.md -t general/biography_graph -o ./bio_kb/ -l zh

# 添加职业生涯
hk feed ./bio_kb/ career.md

# 添加晚年
hk feed ./bio_kb/ later_years.md

# 最终可视化
hk show ./bio_kb/
```

---

## 验证

检查 feed 是否成功：

```bash
hk info ./ka/
```

查看：
- 节点数增加
- 边数增加
- 时间戳更新

---

## 最佳实践

1. **使用相同模板** — Feed 应使用兼容的模板
2. **匹配语言** — 为获得最佳效果，使用一致的语言
3. **之后重建索引** — 搜索/聊天需要 `hk build-index ./ka/`
4. **可视化更改** — 使用 `hk show ./ka/` 查看更新

---

## 错误处理

### "不是有效的知识库目录"

目录不包含有效的知识库。检查：

```bash
ls ./ka/
# 应该包含：data.json, metadata.json
```

### "模板不匹配"

Feed 最适合使用相同类型的模板。如有需要可以覆盖：

```bash
hk feed ./ka/ doc.md -t general/biography_graph
```

---

## 另请参见

- [`hk parse`](parse.md) — 创建新知识库
- [`hk info`](info.md) — 查看知识库统计信息
- [`hk build-index`](build-index.md) — Feed 后重建搜索索引
